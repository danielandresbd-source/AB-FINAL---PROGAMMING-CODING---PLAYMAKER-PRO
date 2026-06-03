# ============================================================
# tests/test_simulator.py
# Tests unitarios para simulator.py (RF10)
# Cubre los casos T20, T21 del plan de testing
# Proyecto: AB Final - Programming & Coding - MSMK 2025-2026
# ============================================================

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import simulator
from models import Formation, PlayType


# --- Tests T20: Generacion de jugadas sinteticas ---

class TestGenerarJugadas:
    """Tests para la funcion generar_jugadas del modulo simulator."""

    def test_T20_generar_100_jugadas_devuelve_lista_de_100(self):
        """
        T20 - Unitario: Generar 100 jugadas sinteticas debe devolver
        una lista con exactamente 100 objetos Play.
        """

        jugadas = simulator.generar_jugadas(cantidad=100)

        assert len(jugadas) == 100

    def test_T20_jugadas_generadas_tienen_datos_validos(self):
        """
        T20 - Los objetos Play generados deben tener datos coherentes.
        """

        tipos_validos = [t.value for t in PlayType]
        formaciones_validas = [f.value for f in Formation]

        jugadas = simulator.generar_jugadas(cantidad=50)

        for jugada in jugadas:
            # Verificar nombre
            assert jugada.nombre is not None
            assert len(jugada.nombre) > 0

            # Verificar tipo valido
            assert jugada.tipo in tipos_validos

            # Verificar formacion valida
            assert jugada.formacion in formaciones_validas

            # Verificar tasa de exito en rango valido
            assert 0.0 <= jugada.tasa_exito <= 1.0

    def test_T20_generar_solo_corridas(self):
        """
        T20 - Generar jugadas de tipo 'run' debe devolver solo corridas.
        """

        jugadas = simulator.generar_jugadas(cantidad=20, tipo_ofensa="run")

        for jugada in jugadas:
            assert jugada.tipo == "run"

    def test_T20_generar_solo_pases(self):
        """
        T20 - Generar jugadas de tipo 'pass' debe devolver solo pases.
        """

        jugadas = simulator.generar_jugadas(cantidad=20, tipo_ofensa="pass")

        for jugada in jugadas:
            assert jugada.tipo == "pass"

    def test_T20_jugadas_generadas_tienen_ids_unicos(self):
        """
        T20 - Cada jugada generada debe tener un ID unico.
        """

        jugadas = simulator.generar_jugadas(cantidad=30)

        ids = [j.id for j in jugadas]
        # Si los IDs son unicos, al convertirlos a set no pierde elementos
        assert len(set(ids)) == len(ids)


# --- Tests T21: Casos limite del simulador ---

class TestGenerarJugadasLimite:
    """Tests para casos limite de la generacion de datos sinteticos."""

    def test_T21_generar_cero_jugadas_devuelve_lista_vacia(self):
        """
        T21 - Limite: Generar 0 jugadas debe devolver una lista vacia.
        """

        jugadas = simulator.generar_jugadas(cantidad=0)

        assert jugadas == []

    def test_T21_generar_una_sola_jugada(self):
        """
        T21 - Generar exactamente 1 jugada debe devolver lista con 1 elemento.
        """

        jugadas = simulator.generar_jugadas(cantidad=1)

        assert len(jugadas) == 1

    def test_T21_generar_playbooks_crea_cantidad_correcta(self):
        """
        T21 - Generar playbooks sinteticos debe crear el numero indicado.
        """

        playbooks = simulator.generar_playbooks(num_playbooks=3, jugadas_por_playbook=5)

        assert len(playbooks) == 3
        for pb in playbooks:
            assert len(pb.jugadas) == 5

    def test_T21_guardar_dataset_csv_crea_archivo(self, tmp_path):
        """
        T21 - Guardar dataset como CSV debe crear el archivo en la ruta indicada.
        """

        jugadas = simulator.generar_jugadas(cantidad=10)
        ruta_salida = str(tmp_path / "test_dataset.csv")

        ruta_guardada = simulator.guardar_dataset_csv(jugadas, ruta_archivo=ruta_salida)

        assert os.path.exists(ruta_guardada)

    def test_T21_guardar_dataset_json_crea_archivo(self, tmp_path):
        """
        T21 - Guardar dataset como JSON debe crear el archivo en la ruta indicada.
        """

        playbooks = simulator.generar_playbooks(num_playbooks=2, jugadas_por_playbook=3)
        ruta_salida = str(tmp_path / "test_dataset.json")

        ruta_guardada = simulator.guardar_dataset_json(playbooks, ruta_archivo=ruta_salida)

        assert os.path.exists(ruta_guardada)
