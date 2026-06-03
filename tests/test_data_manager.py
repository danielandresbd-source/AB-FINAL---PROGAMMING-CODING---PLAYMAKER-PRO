# ============================================================
# tests/test_data_manager.py
# Tests unitarios para data_manager.py (RF2)
# Cubre los casos T06, T07, T08, T09, T10 del plan de testing
# Proyecto: AB Final - Programming & Coding - MSMK 2025-2026
# ============================================================

import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import data_manager
from exceptions import PlaybookNotFoundError, PlayNotFoundError, ValidationError
from models import Play, Playbook


# --- Configuracion de los tests ---

@pytest.fixture(autouse=True)
def usar_json_temporal(tmp_path, monkeypatch):
    """
    Configura cada test para usar un archivo JSON temporal.

    Esto evita que los tests modifiquen el archivo JSON real del proyecto.
    'autouse=True' significa que se aplica automaticamente a todos los tests.
    """

    # Crear el directorio data/ dentro del directorio temporal
    directorio_data = tmp_path / "data"
    directorio_data.mkdir()

    # Decirle a data_manager que use el archivo temporal
    ruta_temporal = str(directorio_data / "playbooks.json")
    monkeypatch.setattr(data_manager, "RUTA_JSON", ruta_temporal)


# --- Tests T06: Crear playbook ---

class TestCrearPlaybook:
    """Tests para la creacion de playbooks."""

    def test_T06_crear_playbook_con_datos_validos(self):
        """
        T06 - Unitario: Crear playbook con parametros validos debe guardarlo en JSON.
        """

        playbook = data_manager.crear_playbook(
            nombre="Red Zone Offense",
            tipo_ofensa="spread",
        )

        assert playbook.nombre == "Red Zone Offense"
        assert playbook.tipo_ofensa == "spread"
        assert playbook.id is not None
        assert playbook.id.startswith("pb_")

    def test_T06_playbook_creado_persiste_en_json(self):
        """
        T06 - El playbook creado debe poder recuperarse del JSON.
        """

        playbook_original = data_manager.crear_playbook("Test Playbook")
        playbook_recuperado = data_manager.obtener_playbook(playbook_original.id)

        assert playbook_recuperado.nombre == "Test Playbook"


# --- Tests T07: Crear playbook con datos invalidos ---

class TestCrearPlaybookInvalido:
    """Tests para validacion al crear playbooks."""

    def test_T07_nombre_vacio_lanza_validation_error(self):
        """
        T07 - Error: Nombre vacio debe lanzar ValidationError.
        """

        with pytest.raises(ValidationError):
            data_manager.crear_playbook(nombre="")

    def test_T07_nombre_solo_espacios_lanza_validation_error(self):
        """
        T07 - Error: Nombre con solo espacios debe lanzar ValidationError.
        """

        with pytest.raises(ValidationError):
            data_manager.crear_playbook(nombre="   ")


# --- Tests T08: Actualizar jugada ---

class TestActualizarJugada:
    """Tests para la actualizacion de jugadas."""

    def test_T08_actualizar_play_cambia_atributos_correctamente(self):
        """
        T08 - Unitario: Actualizar una jugada debe cambiar sus atributos en el JSON.
        """

        # Preparar: crear playbook y jugada
        playbook = data_manager.crear_playbook("Playbook Test")

        jugada = Play(
            nombre="Jugada Original",
            tipo="run",
            formacion="SHOTGUN",
            yardas=5.0,
        )
        data_manager.anadir_jugada(playbook.id, jugada)

        # Actualizar la jugada
        jugada_actualizada = data_manager.actualizar_jugada(
            playbook_id=playbook.id,
            play_id=jugada.id,
            datos_nuevos={"nombre": "Jugada Actualizada", "yardas": 8.0},
        )

        assert jugada_actualizada.nombre == "Jugada Actualizada"
        assert jugada_actualizada.yardas == 8.0

    def test_T08_actualizacion_persiste_en_json(self):
        """
        T08 - Los cambios de la actualizacion deben persistir en el JSON.
        """

        playbook = data_manager.crear_playbook("Playbook Persistencia")
        jugada = Play(nombre="Jugada A", tipo="run", formacion="SHOTGUN", yardas=3.0)
        data_manager.anadir_jugada(playbook.id, jugada)

        data_manager.actualizar_jugada(
            playbook.id,
            jugada.id,
            {"yardas": 10.0},
        )

        # Recuperar del JSON y verificar
        playbook_recuperado = data_manager.obtener_playbook(playbook.id)
        jugada_recuperada = playbook_recuperado.obtener_jugada(jugada.id)

        assert jugada_recuperada.yardas == 10.0


# --- Tests T09: Eliminar playbook con ID inexistente ---

class TestEliminarPlaybookInexistente:
    """Tests para eliminar playbooks que no existen."""

    def test_T09_eliminar_id_inexistente_lanza_playbook_not_found(self):
        """
        T09 - Limite: Eliminar playbook con ID que no existe debe lanzar
        PlaybookNotFoundError con un mensaje claro.
        """

        with pytest.raises(PlaybookNotFoundError) as info_error:
            data_manager.eliminar_playbook("id_que_no_existe")

        # Verificar que el mensaje es claro
        assert "id_que_no_existe" in str(info_error.value)

    def test_T09_obtener_playbook_inexistente_lanza_error(self):
        """
        T09 - Buscar un playbook que no existe debe lanzar PlaybookNotFoundError.
        """

        with pytest.raises(PlaybookNotFoundError):
            data_manager.obtener_playbook("pb_999999")


# --- Tests T10: Obtener jugada por ID ---

class TestObtenerJugada:
    """Tests para obtener jugadas especificas."""

    def test_T10_obtener_jugada_por_id_valido_devuelve_play_correcto(self):
        """
        T10 - Unitario: Buscar jugada por ID valido debe devolver el objeto Play correcto.
        """

        playbook = data_manager.crear_playbook("Playbook Busqueda")

        jugada = Play(
            nombre="Jugada Buscable",
            tipo="pass",
            formacion="SHOTGUN",
            yardas=12.0,
        )
        data_manager.anadir_jugada(playbook.id, jugada)

        # Buscar la jugada
        jugada_encontrada = data_manager.obtener_jugada(playbook.id, jugada.id)

        assert jugada_encontrada.id == jugada.id
        assert jugada_encontrada.nombre == "Jugada Buscable"

    def test_T10_listar_playbooks_devuelve_todos(self):
        """
        T10 - Listar playbooks debe devolver todos los que se hayan creado.
        """

        data_manager.crear_playbook("Playbook Uno")
        data_manager.crear_playbook("Playbook Dos")
        data_manager.crear_playbook("Playbook Tres")

        playbooks = data_manager.listar_playbooks()

        assert len(playbooks) == 3
