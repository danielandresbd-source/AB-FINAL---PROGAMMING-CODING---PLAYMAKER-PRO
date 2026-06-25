# ============================================================
# tests/test_alerts.py
# Tests unitarios para alerts.py (RF6)
# Cubre los casos T18, T19 del plan de testing
# Proyecto: AB Final - Programming & Coding
# ============================================================

import os
import sys


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from alerts import MotorAlertas
from models import Play, Playbook


# Funcion de ayuda

def crear_jugada_valida(nombre="Jugada Valida"):
    """Crea una jugada con todos los datos correctos."""

    return Play(
        nombre=nombre,
        tipo="run",
        formacion="SHOTGUN",
        yardas=5.0,
        tasa_exito=0.65,
        down_distance="1st&10",
        hash_position="middle",
    )


# Tests T18: Alerta por formacion invalida

class TestEvaluarJugada:
    """Tests para el metodo evaluar_jugada del MotorAlertas."""

    def test_T18_formacion_invalida_dispara_alerta(self):
        """
        T18 - Unitario: Jugada con formacion no reconocida debe disparar
        una alerta en el motor.
        """

        motor = MotorAlertas()

        jugada_invalida = Play(
            nombre="Jugada Formacion Mala",
            tipo="run",
            formacion="FORMACION_INVENTADA",  # No existe en el sistema
            yardas=5.0,
            tasa_exito=0.65,
        )

        alertas = motor.evaluar_jugada(jugada_invalida)

        assert len(alertas) > 0
        # Verificar que la alerta menciona la formacion
        alerta_texto = " ".join(alertas)
        assert "FORMACION_INVENTADA" in alerta_texto or "formacion" in alerta_texto.lower()

    def test_T18_jugada_valida_no_genera_alertas(self):
        """
        T18 - Una jugada con todos los datos correctos no debe generar alertas.
        """

        motor = MotorAlertas()
        jugada = crear_jugada_valida()

        alertas = motor.evaluar_jugada(jugada)

        assert alertas == []

    def test_T18_yardas_extremas_generan_alerta(self):
        """
        T18 - Jugada con yardas de mas de 99 debe generar una alerta.
        """

        motor = MotorAlertas()

        jugada = Play(
            nombre="Jugada Yardas Extremas",
            tipo="run",
            formacion="SHOTGUN",
            yardas=150.0,  # Valor extremo
            tasa_exito=0.65,
        )

        alertas = motor.evaluar_jugada(jugada)

        assert len(alertas) > 0

    def test_T18_tasa_exito_invalida_genera_alerta(self):
        """
        T18 - Jugada con tasa de exito mayor que 1.0 debe generar una alerta.
        """

        motor = MotorAlertas()

        jugada = Play(
            nombre="Jugada Tasa Invalida",
            tipo="run",
            formacion="SHOTGUN",
            yardas=5.0,
            tasa_exito=1.5,  # Imposible
        )

        alertas = motor.evaluar_jugada(jugada)

        assert len(alertas) > 0


# Tests T19: Alerta por capacidad del playbook

class TestVerificarPlaybook:
    """Tests para el metodo verificar_playbook del MotorAlertas."""

    def test_T19_playbook_con_51_jugadas_genera_alerta_de_capacidad(self):
        """
        T19 - Limite: Playbook con 51 jugadas debe generar alerta de
        capacidad excedida (limite es 50).
        """

        motor = MotorAlertas()

        playbook = Playbook(nombre="Playbook Lleno", tipo_ofensa="spread")

        # Agregar 51 jugadas directamente a la lista (sin pasar por anadir_jugada
        # para evitar que se lance PlaybookFullError durante el test)
        for i in range(51):
            jugada = crear_jugada_valida(nombre=f"Jugada {i + 1}")
            playbook.jugadas.append(jugada)

        alertas = motor.verificar_playbook(playbook)

        # Debe haber al menos una alerta de capacidad
        assert len(alertas) > 0
        alerta_texto = " ".join(alertas)
        assert (
            "50" in alerta_texto
            or "limite" in alerta_texto.lower()
            or "lleno" in alerta_texto.lower()
        )

    def test_T19_playbook_con_nombres_duplicados_genera_alerta(self):
        """
        T19 - Playbook con jugadas de mismo nombre debe generar alerta de duplicados.
        """

        motor = MotorAlertas()

        playbook = Playbook(nombre="Playbook Duplicados")

        # Agregar dos jugadas con el mismo nombre
        playbook.jugadas.append(crear_jugada_valida(nombre="Jugada Repetida"))
        playbook.jugadas.append(crear_jugada_valida(nombre="Jugada Repetida"))
        playbook.jugadas.append(crear_jugada_valida(nombre="Jugada Unica"))

        alertas = motor.verificar_playbook(playbook)

        alerta_texto = " ".join(alertas)
        assert "duplicado" in alerta_texto.lower() or "repetida" in alerta_texto.lower()

    def test_T19_registro_guarda_todas_las_alertas(self):
        """
        T19 - El registro interno del motor debe guardar todas las alertas generadas.
        """

        motor = MotorAlertas()

        # Evaluar una jugada con problemas
        jugada_mala = Play(
            nombre="Jugada Con Problemas",
            tipo="run",
            formacion="FORMACION_FALSA",
            yardas=5.0,
            tasa_exito=1.5,
        )

        motor.evaluar_jugada(jugada_mala)

        alertas_guardadas = motor.obtener_alertas()
        assert len(alertas_guardadas) > 0

    def test_T19_limpiar_registro_vacia_las_alertas(self):
        """
        T19 - Limpiar el registro debe dejar la lista de alertas vacia.
        """

        motor = MotorAlertas()

        # Generar algunas alertas
        jugada_mala = Play(
            nombre="Jugada Mala",
            tipo="run",
            formacion="FORMACION_FALSA",
            yardas=5.0,
            tasa_exito=0.5,
        )
        motor.evaluar_jugada(jugada_mala)

        # Limpiar y verificar
        motor.limpiar_registro()

        assert motor.obtener_alertas() == []
