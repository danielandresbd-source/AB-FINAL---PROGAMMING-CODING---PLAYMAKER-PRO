# ============================================================
# tests/test_cobertura_adicional.py
# Tests adicionales para mejorar la cobertura al 80%+ en todos los modulos
# Cubre lineas faltantes en data_manager, analyzer, reporter y models
# Proyecto: AB Final - Programming & Coding - MSMK 2025-2026
# ============================================================

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import analyzer
import data_manager
import reporter
from exceptions import (
    PlaybookFullError,
    PlaybookNotFoundError,
    PlayNotFoundError,
    ValidationError,
)
from models import Play, Playbook


# --- Fixture para usar JSON temporal en todos los tests ---

@pytest.fixture(autouse=True)
def usar_json_temporal(tmp_path, monkeypatch):
    """Redirige el JSON de datos a un archivo temporal para no tocar datos reales."""

    directorio_data = tmp_path / "data"
    directorio_data.mkdir()
    ruta_temporal = str(directorio_data / "playbooks.json")
    monkeypatch.setattr(data_manager, "RUTA_JSON", ruta_temporal)


# --- Funcion de ayuda ---

def crear_jugada(nombre="Test", tipo="run", formacion="SHOTGUN",
                 yardas=5.0, tasa_exito=0.65,
                 down_distance="1st&10", hash_position="middle"):
    """Crea una jugada de prueba con valores por defecto."""

    return Play(
        nombre=nombre,
        tipo=tipo,
        formacion=formacion,
        yardas=yardas,
        tasa_exito=tasa_exito,
        down_distance=down_distance,
        hash_position=hash_position,
    )


# ============================================================
# TESTS PARA data_manager.py
# Lineas faltantes: 42-47, 195-226, 290, 334, 345-359, 398
# ============================================================

class TestCargarJsonCorrrupto:
    """Cubre las lineas 42-47: manejo de JSON corrupto."""

    def test_json_corrupto_devuelve_estructura_vacia(self, tmp_path, monkeypatch):
        """
        Si el archivo JSON esta corrupto, debe devolver estructura vacia
        en lugar de lanzar una excepcion al usuario.
        """

        # Escribir contenido invalido en el JSON
        ruta_json = str(tmp_path / "data" / "playbooks.json")
        os.makedirs(os.path.dirname(ruta_json), exist_ok=True)

        with open(ruta_json, "w") as f:
            f.write("esto no es json valido {{{")

        monkeypatch.setattr(data_manager, "RUTA_JSON", ruta_json)

        # No debe lanzar excepcion, debe devolver lista vacia
        playbooks = data_manager.listar_playbooks()
        assert playbooks == []


class TestActualizarPlaybook:
    """Cubre las lineas 195-226: funcion actualizar_playbook completa."""

    def test_actualizar_nombre_del_playbook(self):
        """Actualizar el nombre de un playbook debe guardarlo en JSON."""

        pb = data_manager.crear_playbook("Nombre Original")
        pb_actualizado = data_manager.actualizar_playbook(
            pb.id,
            nuevo_nombre="Nombre Nuevo"
        )

        assert pb_actualizado.nombre == "Nombre Nuevo"

    def test_actualizar_tipo_ofensa_del_playbook(self):
        """Actualizar el tipo de ofensa debe reflejarse en el JSON."""

        pb = data_manager.crear_playbook("Playbook Test", tipo_ofensa="spread")
        pb_actualizado = data_manager.actualizar_playbook(
            pb.id,
            nuevo_tipo_ofensa="power"
        )

        assert pb_actualizado.tipo_ofensa == "power"

    def test_actualizar_nombre_y_tipo_a_la_vez(self):
        """Actualizar nombre y tipo al mismo tiempo debe funcionar."""

        pb = data_manager.crear_playbook("Original", tipo_ofensa="spread")
        pb_actualizado = data_manager.actualizar_playbook(
            pb.id,
            nuevo_nombre="Actualizado",
            nuevo_tipo_ofensa="west_coast"
        )

        assert pb_actualizado.nombre == "Actualizado"
        assert pb_actualizado.tipo_ofensa == "west_coast"

    def test_actualizar_con_nombre_vacio_lanza_validation_error(self):
        """Intentar actualizar con nombre vacio debe lanzar ValidationError."""

        pb = data_manager.crear_playbook("Playbook")

        with pytest.raises(ValidationError):
            data_manager.actualizar_playbook(pb.id, nuevo_nombre="   ")

    def test_actualizar_playbook_inexistente_lanza_error(self):
        """Actualizar un playbook que no existe debe lanzar PlaybookNotFoundError."""

        with pytest.raises(PlaybookNotFoundError):
            data_manager.actualizar_playbook("id_que_no_existe", nuevo_nombre="Nombre")


class TestAnadirJugadaPlaybookInexistente:
    """Cubre la linea 290: PlaybookNotFoundError en anadir_jugada."""

    def test_anadir_jugada_a_playbook_inexistente_lanza_error(self):
        """Anadir jugada a un playbook que no existe debe lanzar PlaybookNotFoundError."""

        jugada = crear_jugada()

        with pytest.raises(PlaybookNotFoundError):
            data_manager.anadir_jugada("id_falso_12345", jugada)


class TestActualizarJugadaTodasLasPropiedades:
    """Cubre las lineas 334, 345-359: actualizar_jugada con todos los campos."""

    def _preparar_playbook_con_jugada(self):
        """Crea un playbook con una jugada y devuelve ambos."""

        pb = data_manager.crear_playbook("Playbook Actualizacion")
        jugada = crear_jugada(nombre="Jugada Original")
        data_manager.anadir_jugada(pb.id, jugada)
        return pb, jugada

    def test_actualizar_jugada_playbook_inexistente_lanza_error(self):
        """Actualizar jugada en playbook inexistente debe lanzar PlaybookNotFoundError."""

        with pytest.raises(PlaybookNotFoundError):
            data_manager.actualizar_jugada("id_falso", "play_falso", {"nombre": "X"})

    def test_actualizar_campo_tipo(self):
        """Actualizar el campo tipo de una jugada debe funcionar."""

        pb, jugada = self._preparar_playbook_con_jugada()
        resultado = data_manager.actualizar_jugada(
            pb.id, jugada.id, {"tipo": "pass"}
        )
        assert resultado.tipo == "pass"

    def test_actualizar_campo_formacion(self):
        """Actualizar la formacion de una jugada debe funcionar."""

        pb, jugada = self._preparar_playbook_con_jugada()
        resultado = data_manager.actualizar_jugada(
            pb.id, jugada.id, {"formacion": "PISTOL"}
        )
        assert resultado.formacion == "PISTOL"

    def test_actualizar_campo_descripcion(self):
        """Actualizar la descripcion de una jugada debe funcionar."""

        pb, jugada = self._preparar_playbook_con_jugada()
        resultado = data_manager.actualizar_jugada(
            pb.id, jugada.id, {"descripcion": "Nueva descripcion de la jugada"}
        )
        assert resultado.descripcion == "Nueva descripcion de la jugada"

    def test_actualizar_campo_tasa_exito(self):
        """Actualizar la tasa de exito de una jugada debe funcionar."""

        pb, jugada = self._preparar_playbook_con_jugada()
        resultado = data_manager.actualizar_jugada(
            pb.id, jugada.id, {"tasa_exito": 0.90}
        )
        assert resultado.tasa_exito == 0.90

    def test_actualizar_campo_down_distance(self):
        """Actualizar el down_distance de una jugada debe funcionar."""

        pb, jugada = self._preparar_playbook_con_jugada()
        resultado = data_manager.actualizar_jugada(
            pb.id, jugada.id, {"down_distance": "3rd&long"}
        )
        assert resultado.down_distance == "3rd&long"

    def test_actualizar_campo_hash_position(self):
        """Actualizar el hash_position de una jugada debe funcionar."""

        pb, jugada = self._preparar_playbook_con_jugada()
        resultado = data_manager.actualizar_jugada(
            pb.id, jugada.id, {"hash_position": "left"}
        )
        assert resultado.hash_position == "left"

    def test_actualizar_campo_etiquetas(self):
        """Actualizar las etiquetas de una jugada debe funcionar."""

        pb, jugada = self._preparar_playbook_con_jugada()
        resultado = data_manager.actualizar_jugada(
            pb.id, jugada.id, {"etiquetas": ["red_zone", "power_run"]}
        )
        assert "red_zone" in resultado.etiquetas


class TestEliminarJugadaPlaybookInexistente:
    """Cubre la linea 398: PlaybookNotFoundError en eliminar_jugada."""

    def test_eliminar_jugada_de_playbook_inexistente_lanza_error(self):
        """Eliminar jugada de playbook que no existe debe lanzar PlaybookNotFoundError."""

        with pytest.raises(PlaybookNotFoundError):
            data_manager.eliminar_jugada("id_falso_99999", "play_falso")


# ============================================================
# TESTS PARA analyzer.py
# Lineas faltantes: 147, 159, 166, 232, 238, 268-293
# ============================================================

class TestDetectarAnomaliasCasosFaltantes:
    """Cubre las lineas 147, 159, 166: tipos de anomalias no probadas aun."""

    def test_tasa_exito_invalida_se_detecta_como_anomalia(self):
        """
        Linea 147: jugada con tasa de exito fuera de [0.0, 1.0]
        debe ser detectada como anomalia.
        """

        jugadas = [
            crear_jugada(nombre=f"Normal {i}", yardas=5.0)
            for i in range(5)
        ]
        # Agregar jugada con tasa invalida directamente
        jugada_mala = Play(
            nombre="Tasa Imposible",
            tipo="run",
            formacion="SHOTGUN",
            yardas=5.0,
            tasa_exito=1.8,  # Fuera del rango valido
        )
        jugadas.append(jugada_mala)

        anomalias = analyzer.detectar_anomalias(jugadas)

        nombres = [a["jugada"].nombre for a in anomalias]
        assert "Tasa Imposible" in nombres

        for anomalia in anomalias:
            if anomalia["jugada"].nombre == "Tasa Imposible":
                razones = " ".join(anomalia["razones"])
                assert "tasa" in razones.lower() or "rango" in razones.lower()

    def test_down_distance_invalido_se_detecta_como_anomalia(self):
        """
        Linea 159: jugada con down_distance desconocido
        debe ser detectada como anomalia.
        """

        jugadas = [
            crear_jugada(nombre="Jugada Normal", yardas=5.0),
            Play(
                nombre="Down Invalido",
                tipo="run",
                formacion="SHOTGUN",
                yardas=5.0,
                tasa_exito=0.65,
                down_distance="99th&999",  # No existe esto
            ),
        ]

        anomalias = analyzer.detectar_anomalias(jugadas)
        nombres = [a["jugada"].nombre for a in anomalias]
        assert "Down Invalido" in nombres

    def test_hash_position_invalida_se_detecta_como_anomalia(self):
        """
        Linea 166: jugada con hash_position desconocida
        debe ser detectada como anomalia.
        """

        jugadas = [
            crear_jugada(nombre="Jugada Normal", yardas=5.0),
            Play(
                nombre="Hash Invalido",
                tipo="run",
                formacion="SHOTGUN",
                yardas=5.0,
                tasa_exito=0.65,
                hash_position="diagonal",  # No existe esto
            ),
        ]

        anomalias = analyzer.detectar_anomalias(jugadas)
        nombres = [a["jugada"].nombre for a in anomalias]
        assert "Hash Invalido" in nombres


class TestPredecirTendencias:
    """Cubre las lineas 232, 238: tendencias subiendo y sin datos suficientes."""

    def _crear_jugadas_con_tasas(self, tasas):
        """Crea jugadas con las tasas de exito indicadas, en orden cronologico."""

        from datetime import datetime, timedelta

        jugadas = []
        fecha_base = datetime(2025, 1, 1)

        for i, tasa in enumerate(tasas):
            jugada = Play(
                nombre=f"Jugada {i}",
                tipo="run",
                formacion="SHOTGUN",
                yardas=5.0,
                tasa_exito=tasa,
                creada_en=(fecha_base + timedelta(hours=i)).isoformat(),
            )
            jugadas.append(jugada)

        return jugadas

    def test_tendencia_subiendo_cuando_ultima_media_es_mayor(self):
        """
        Linea 232: cuando la ultima media movil es mayor que la anterior,
        la tendencia debe ser 'subiendo'.
        """

        # Tasas crecientes al final para forzar tendencia subiendo
        tasas = [0.30, 0.32, 0.33, 0.35, 0.50, 0.70, 0.85]
        jugadas = self._crear_jugadas_con_tasas(tasas)

        resultado = analyzer.predecir_efectividad(jugadas, ventana=3)

        assert resultado["tendencia"] == "subiendo"

    def test_tendencia_bajando_cuando_ultima_media_es_menor(self):
        """Cuando la ultima media movil es menor que la anterior, debe ser 'bajando'."""

        # Tasas decrecientes al final para forzar tendencia bajando
        tasas = [0.85, 0.80, 0.75, 0.60, 0.40, 0.30, 0.20]
        jugadas = self._crear_jugadas_con_tasas(tasas)

        resultado = analyzer.predecir_efectividad(jugadas, ventana=3)

        assert resultado["tendencia"] == "bajando"

    def test_tendencia_sin_datos_suficientes_cuando_solo_hay_una_media(self):
        """
        Linea 238: cuando solo se puede calcular una media movil
        (jugadas == ventana), la tendencia es 'sin datos suficientes'.
        """

        # Exactamente 5 jugadas con ventana 5 -> solo 1 media movil posible
        tasas = [0.60, 0.65, 0.70, 0.68, 0.72]
        jugadas = self._crear_jugadas_con_tasas(tasas)

        resultado = analyzer.predecir_efectividad(jugadas, ventana=5)

        assert resultado["tendencia"] == "sin datos suficientes"


class TestObtenerResumenTendencias:
    """Cubre las lineas 268-293: funcion obtener_resumen_tendencias."""

    def test_resumen_vacio_con_lista_vacia(self):
        """Lista vacia debe devolver diccionario vacio."""

        resultado = analyzer.obtener_resumen_tendencias([])
        assert resultado == {}

    def test_resumen_agrupa_por_tipo_correctamente(self):
        """El resumen debe agrupar las jugadas por tipo y calcular promedios."""

        jugadas = [
            crear_jugada(nombre="Run 1", tipo="run", tasa_exito=0.60),
            crear_jugada(nombre="Run 2", tipo="run", tasa_exito=0.80),
            crear_jugada(nombre="Pass 1", tipo="pass", tasa_exito=0.70),
            crear_jugada(nombre="Pass 2", tipo="pass", tasa_exito=0.90),
        ]

        resultado = analyzer.obtener_resumen_tendencias(jugadas)

        assert "run" in resultado
        assert "pass" in resultado
        assert resultado["run"]["total_jugadas"] == 2
        assert resultado["run"]["tasa_promedio"] == 0.70
        assert resultado["pass"]["tasa_promedio"] == 0.80

    def test_resumen_identifica_mejor_y_peor_jugada(self):
        """El resumen debe identificar la mejor y peor jugada por tasa de exito."""

        jugadas = [
            crear_jugada(nombre="La Mejor", tipo="run", tasa_exito=0.90),
            crear_jugada(nombre="La Peor", tipo="run", tasa_exito=0.30),
            crear_jugada(nombre="La Normal", tipo="run", tasa_exito=0.60),
        ]

        resultado = analyzer.obtener_resumen_tendencias(jugadas)

        assert resultado["run"]["mejor_jugada"] == "La Mejor"
        assert resultado["run"]["peor_jugada"] == "La Peor"

    def test_tipo_con_una_sola_jugada_no_aparece_en_resumen(self):
        """
        Un tipo con solo 1 jugada no debe aparecer en el resumen
        porque no hay suficientes datos para analizar tendencias.
        """

        jugadas = [
            crear_jugada(nombre="Unica Special", tipo="special_teams", tasa_exito=0.50),
            crear_jugada(nombre="Run 1", tipo="run", tasa_exito=0.60),
            crear_jugada(nombre="Run 2", tipo="run", tasa_exito=0.70),
        ]

        resultado = analyzer.obtener_resumen_tendencias(jugadas)

        # special_teams tiene solo 1 jugada, no debe aparecer
        assert "special_teams" not in resultado
        # run tiene 2 jugadas, si debe aparecer
        assert "run" in resultado


# ============================================================
# TESTS PARA reporter.py
# Lineas faltantes: 53, 95, 104, 181, 212, 248-270
# ============================================================

@pytest.fixture()
def directorio_exports_temporal(tmp_path, monkeypatch):
    """Redirige el directorio de exports a una carpeta temporal."""

    directorio = tmp_path / "exports"
    directorio.mkdir()
    monkeypatch.setattr(reporter, "DIRECTORIO_EXPORTACIONES", str(directorio))
    return str(directorio)


class TestExportarEstadisticasCsv:
    """Cubre las lineas 95, 104: exportar_estadisticas_csv."""

    def test_exportar_estadisticas_crea_archivo(self, directorio_exports_temporal):
        """exportar_estadisticas_csv debe crear un archivo CSV con las estadisticas."""

        jugadas = [
            crear_jugada(nombre=f"Jugada {i}", tipo="run" if i % 2 == 0 else "pass")
            for i in range(6)
        ]
        estadisticas = analyzer.calcular_estadisticas(jugadas)

        ruta = reporter.exportar_estadisticas_csv(estadisticas)

        assert os.path.exists(ruta)
        assert ruta.endswith(".csv")

    def test_exportar_estadisticas_vacias_lanza_error(self, directorio_exports_temporal):
        """Exportar estadisticas vacias debe lanzar ValueError."""

        with pytest.raises(ValueError):
            reporter.exportar_estadisticas_csv({})


class TestMostrarTopJugadas:
    """Cubre las lineas 212, 248-270: mostrar_top_jugadas."""

    def test_mostrar_top_jugadas_con_datos(self, capsys):
        """
        mostrar_top_jugadas debe imprimir en consola el top 5 sin lanzar errores.
        """

        jugadas = [
            crear_jugada(nombre=f"Jugada {i}", tasa_exito=0.50 + i * 0.05)
            for i in range(6)
        ]
        estadisticas = analyzer.calcular_estadisticas(jugadas)

        # No debe lanzar ninguna excepcion
        reporter.mostrar_top_jugadas(estadisticas)

        salida = capsys.readouterr().out
        assert "TOP" in salida or "Exito" in salida

    def test_mostrar_top_jugadas_sin_datos(self, capsys):
        """
        Linea 212: mostrar_top_jugadas con estadisticas sin jugadas
        debe mostrar mensaje de aviso.
        """

        reporter.mostrar_top_jugadas({})

        salida = capsys.readouterr().out
        assert "No hay" in salida


# ============================================================
# TESTS PARA models.py
# Lineas faltantes: 113, 117, 130, 137, 153-164, 203, 256, 280, 300, 337
# ============================================================

class TestPlaybookLleno:
    """Cubre las lineas 113, 117: PlaybookFullError cuando el playbook esta lleno."""

    def test_anadir_jugada_51_lanza_playbook_full_error(self):
        """
        Anadir la jugada 51 a un playbook ya lleno debe lanzar PlaybookFullError.
        """

        playbook = Playbook(nombre="Playbook Lleno")

        # Llenar el playbook hasta el limite
        for i in range(50):
            jugada = crear_jugada(nombre=f"Jugada {i + 1}")
            playbook.jugadas.append(jugada)

        # La jugada 51 debe lanzar error
        jugada_extra = crear_jugada(nombre="Jugada 51")

        with pytest.raises(PlaybookFullError):
            playbook.anadir_jugada(jugada_extra)


class TestEliminarJugadaDeModelo:
    """Cubre las lineas 130, 137: PlayNotFoundError en Playbook.eliminar_jugada."""

    def test_eliminar_jugada_inexistente_lanza_play_not_found(self):
        """Eliminar jugada que no existe en el playbook debe lanzar PlayNotFoundError."""

        playbook = Playbook(nombre="Playbook Test")

        with pytest.raises(PlayNotFoundError):
            playbook.eliminar_jugada("id_que_no_existe")


class TestObtenerJugadaDeModelo:
    """Cubre las lineas 153-164: PlayNotFoundError en Playbook.obtener_jugada."""

    def test_obtener_jugada_inexistente_lanza_play_not_found(self):
        """Obtener jugada que no existe en el playbook debe lanzar PlayNotFoundError."""

        playbook = Playbook(nombre="Playbook Test")

        with pytest.raises(PlayNotFoundError):
            playbook.obtener_jugada("id_inexistente")


class TestReprModelos:
    """Cubre las lineas 203, 337: metodos __repr__ de Play y Playbook."""

    def test_repr_play_devuelve_string_con_id_y_nombre(self):
        """El __repr__ de Play debe devolver un string con id, nombre y tipo."""

        jugada = crear_jugada(nombre="Mi Jugada")
        representacion = repr(jugada)

        assert "Mi Jugada" in representacion
        assert "Play" in representacion

    def test_repr_playbook_devuelve_string_con_nombre(self):
        """El __repr__ de Playbook debe devolver un string con el nombre."""

        playbook = Playbook(nombre="Mi Playbook")
        representacion = repr(playbook)

        assert "Mi Playbook" in representacion
        assert "Playbook" in representacion


class TestDesdeDiccionarioModelos:
    """Cubre las lineas 256, 280, 300: metodos desde_diccionario."""

    def test_play_desde_diccionario_crea_objeto_correcto(self):
        """Play.desde_diccionario debe crear un objeto Play con los datos correctos."""

        datos = {
            "id": "play_test_001",
            "nombre": "Jugada Desde Dict",
            "tipo": "pass",
            "formacion": "SHOTGUN",
            "yardas": 12.0,
            "tasa_exito": 0.75,
            "down_distance": "2nd&long",
            "hash_position": "left",
            "etiquetas": ["deep_ball"],
            "descripcion": "Jugada de pase profundo",
        }

        jugada = Play.desde_diccionario(datos)

        assert jugada.id == "play_test_001"
        assert jugada.nombre == "Jugada Desde Dict"
        assert jugada.tipo == "pass"
        assert jugada.yardas == 12.0

    def test_playbook_desde_diccionario_incluye_sus_jugadas(self):
        """Playbook.desde_diccionario debe crear el playbook con sus jugadas incluidas."""

        datos = {
            "id": "pb_test_001",
            "nombre": "Playbook Desde Dict",
            "tipo_ofensa": "spread",
            "creado_en": "2025-05-08T16:00:00",
            "actualizado_en": "2025-05-08T16:00:00",
            "jugadas": [
                {
                    "id": "play_001",
                    "nombre": "HB Dive",
                    "tipo": "run",
                    "formacion": "I_FORMATION",
                    "yardas": 4.5,
                    "tasa_exito": 0.68,
                    "down_distance": "1st&10",
                    "hash_position": "middle",
                    "etiquetas": [],
                }
            ],
        }

        playbook = Playbook.desde_diccionario(datos)

        assert playbook.id == "pb_test_001"
        assert playbook.nombre == "Playbook Desde Dict"
        assert len(playbook.jugadas) == 1
        assert playbook.jugadas[0].nombre == "HB Dive"
