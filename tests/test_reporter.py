# ============================================================
# tests/test_reporter.py
# Tests unitarios para reporter.py (RF5, RF9)
# Cubre los casos T16, T17 del plan de testing
# Proyecto: AB Final - Programming & Coding
# ============================================================

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import reporter
from models import Play


# Configuracion de fixtures

@pytest.fixture(autouse=True)
def usar_directorio_temporal(tmp_path, monkeypatch):
    """
    Redirige las exportaciones a un directorio temporal para no
    contaminar la carpeta real de exports del proyecto.
    """

    directorio_exports = tmp_path / "exports"
    directorio_exports.mkdir()
    monkeypatch.setattr(reporter, "DIRECTORIO_EXPORTACIONES", str(directorio_exports))


# Funcion de ayuda

def crear_jugadas_prueba(cantidad=5):
    """Crea una lista de jugadas de prueba para los tests."""

    jugadas = []
    for i in range(cantidad):
        jugada = Play(
            nombre=f"Jugada Test {i + 1}",
            tipo="run" if i % 2 == 0 else "pass",
            formacion="SHOTGUN",
            yardas=float(5 + i),
            tasa_exito=0.5 + (i * 0.05),
            down_distance="1st&10",
            hash_position="middle",
        )
        jugadas.append(jugada)

    return jugadas


# Tests T16: Exportacion a CSV

class TestExportarCsv:
    """Tests para la exportacion de jugadas a CSV."""

    def test_T16_exportar_jugadas_crea_archivo_csv(self):
        """
        T16 - Unitario: Exportar lista de jugadas valida debe crear un archivo CSV
        en el directorio de exports.
        """

        jugadas = crear_jugadas_prueba(5)
        ruta = reporter.exportar_csv(jugadas)

        assert os.path.exists(ruta)
        assert ruta.endswith(".csv")

    def test_T16_csv_contiene_cabeceras_correctas(self):
        """
        T16 - El CSV exportado debe contener las columnas correctas.
        """

        import csv

        jugadas = crear_jugadas_prueba(3)
        ruta = reporter.exportar_csv(jugadas)

        with open(ruta, encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            columnas = lector.fieldnames

        assert "nombre" in columnas
        assert "tipo" in columnas
        assert "formacion" in columnas
        assert "yardas" in columnas

    def test_T16_csv_contiene_el_numero_correcto_de_filas(self):
        """
        T16 - El CSV exportado debe tener una fila por cada jugada mas la cabecera.
        """

        import csv

        jugadas = crear_jugadas_prueba(7)
        ruta = reporter.exportar_csv(jugadas)

        with open(ruta, encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            filas = list(lector)

        assert len(filas) == 7

    def test_T16_exportar_lista_vacia_lanza_value_error(self):
        """
        T16 - Exportar lista vacia debe lanzar ValueError.
        """

        with pytest.raises(ValueError):
            reporter.exportar_csv([])

    def test_T16_nombre_personalizado_usa_nombre_indicado(self):
        """
        T16 - Exportar con nombre personalizado debe usar ese nombre para el archivo.
        """

        jugadas = crear_jugadas_prueba(2)
        ruta = reporter.exportar_csv(jugadas, nombre_archivo="mi_reporte_test.csv")

        assert "mi_reporte_test.csv" in ruta


# Tests T17: Grafico ASCII

class TestGraficoAscii:
    """Tests para la generacion de graficos ASCII."""

    def test_T17_grafico_ascii_devuelve_string_no_vacio(self):
        """
        T17 - Unitario: mostrar_grafico_ascii con estadisticas validas debe
        devolver un string con barras ASCII.
        """

        import analyzer

        jugadas = crear_jugadas_prueba(10)
        estadisticas = analyzer.calcular_estadisticas(jugadas)
        grafico = reporter.mostrar_grafico_ascii(estadisticas)

        assert isinstance(grafico, str)
        assert len(grafico) > 0

    def test_T17_grafico_contiene_caracteres_de_barra(self):
        """
        T17 - El grafico ASCII debe contener el caracter '#' que representa las barras.
        """

        import analyzer

        jugadas = crear_jugadas_prueba(5)
        estadisticas = analyzer.calcular_estadisticas(jugadas)
        grafico = reporter.mostrar_grafico_ascii(estadisticas)

        assert "#" in grafico

    def test_T17_grafico_con_estadisticas_vacias_devuelve_mensaje(self):
        """
        T17 - Grafico con estadisticas vacias debe devolver un mensaje de aviso.
        """

        resultado = reporter.mostrar_grafico_ascii({})
        assert "No hay" in resultado

    def test_T17_grafico_contiene_tipos_de_jugada(self):
        """
        T17 - El grafico debe contener los tipos de jugadas del dataset.
        """

        import analyzer

        jugadas = crear_jugadas_prueba(6)
        estadisticas = analyzer.calcular_estadisticas(jugadas)
        grafico = reporter.mostrar_grafico_ascii(estadisticas)

        # El dataset tiene jugadas de tipo 'run' y 'pass'
        assert "run" in grafico or "pass" in grafico
