# ============================================================
# tests/test_integration.py
# Tests de integracion entre modulos (T22, T23, T24)
# Verifica que los modulos funcionan correctamente en conjunto
# Proyecto: AB Final - Programming & Coding - MSMK 2025-2026
# ============================================================

import csv
import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import analyzer
import data_importer
import data_manager
import reporter
import simulator
from models import Play


# --- Configuracion de los tests de integracion ---

@pytest.fixture(autouse=True)
def usar_archivos_temporales(tmp_path, monkeypatch):
    """
    Redirige todos los archivos de datos a rutas temporales para que
    los tests de integracion no modifiquen los archivos reales.
    """

    # Directorio de datos temporal
    directorio_data = tmp_path / "data"
    directorio_data.mkdir()

    directorio_exports = directorio_data / "exports"
    directorio_exports.mkdir()

    # Redirigir data_manager al JSON temporal
    ruta_json_temporal = str(directorio_data / "playbooks.json")
    monkeypatch.setattr(data_manager, "RUTA_JSON", ruta_json_temporal)

    # Redirigir reporter al directorio de exports temporal
    monkeypatch.setattr(reporter, "DIRECTORIO_EXPORTACIONES", str(directorio_exports))


# --- Funcion de ayuda para crear CSV temporal ---

def crear_csv_con_jugadas(tmp_path, cantidad=10):
    """Crea un archivo CSV temporal con jugadas de muestra."""

    ruta_csv = str(tmp_path / "jugadas_test.csv")

    with open(ruta_csv, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow([
            "nombre", "tipo", "formacion", "yardas",
            "tasa_exito", "down_distance", "hash_position"
        ])

        formaciones = ["SHOTGUN", "I_FORMATION", "SINGLEBACK", "PISTOL", "EMPTY_SET"]
        tipos = ["run", "pass"]

        for i in range(cantidad):
            escritor.writerow([
                f"Jugada Integracion {i + 1}",
                tipos[i % 2],
                formaciones[i % len(formaciones)],
                round(3.0 + i * 0.5, 1),
                round(0.40 + (i * 0.04), 2),
                "1st&10",
                "middle",
            ])

    return ruta_csv


# --- Test T22: Pipeline completo CSV -> Analisis -> Exportar ---

class TestPipelineImportarAnalizarExportar:
    """
    T22 - Integracion: Verifica el pipeline completo de importacion,
    analisis y exportacion.
    """

    def test_T22_pipeline_carga_analiza_y_exporta_correctamente(self, tmp_path):
        """
        T22 - Pipeline completo: cargar CSV, calcular estadisticas y
        exportar a CSV debe funcionar de principio a fin sin errores.
        """

        # Paso 1: Crear archivo CSV de entrada
        ruta_csv = crear_csv_con_jugadas(tmp_path, cantidad=10)

        # Paso 2: Importar las jugadas desde el CSV
        jugadas_importadas = data_importer.cargar_csv(ruta_csv)
        assert len(jugadas_importadas) == 10

        # Paso 3: Calcular estadisticas
        estadisticas = analyzer.calcular_estadisticas(jugadas_importadas)
        assert estadisticas["total_jugadas"] == 10
        assert "yardas_promedio" in estadisticas

        # Paso 4: Exportar las estadisticas a CSV
        ruta_exportada = reporter.exportar_estadisticas_csv(estadisticas)
        assert os.path.exists(ruta_exportada)

        # Paso 5: Verificar que el CSV exportado tiene contenido
        with open(ruta_exportada, encoding="utf-8") as archivo:
            contenido = archivo.read()

        assert len(contenido) > 0
        assert "total_jugadas" in contenido.lower() or "Total de jugadas" in contenido

    def test_T22_pipeline_detecta_anomalias_en_datos_importados(self, tmp_path):
        """
        T22 - Pipeline: Datos importados con outliers deben ser detectados
        como anomalias en el paso de analisis.
        """

        # Crear CSV con una jugada anómala
        ruta_csv = str(tmp_path / "jugadas_con_anomalia.csv")

        with open(ruta_csv, "w", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["nombre", "tipo", "formacion", "yardas", "tasa_exito"])

            # Jugadas normales
            for i in range(8):
                escritor.writerow([f"Jugada Normal {i}", "run", "SHOTGUN", 5.0, 0.65])

            # Jugada con yardas extremas (outlier)
            escritor.writerow(["Jugada Outlier", "run", "SHOTGUN", 999.0, 0.65])

        jugadas = data_importer.cargar_csv(ruta_csv)
        anomalias = analyzer.detectar_anomalias(jugadas)

        # El outlier debe ser detectado
        assert len(anomalias) > 0
        nombres = [a["jugada"].nombre for a in anomalias]
        assert "Jugada Outlier" in nombres


# --- Test T23: Crear playbook -> Añadir jugada -> Detectar anomalias ---

class TestPipelinePlaybookAnomalias:
    """
    T23 - Integracion: Verifica que crear un playbook, añadir una jugada
    anomala y detectarla funciona correctamente.
    """

    def test_T23_playbook_nuevo_jugada_anomala_es_detectada(self):
        """
        T23 - Pipeline: Crear playbook con varias jugadas normales mas una
        anomala extrema y verificar que la anomalia es detectada.
        """

        # Paso 1: Crear un nuevo playbook
        playbook = data_manager.crear_playbook("Playbook Integracion T23")
        assert playbook.id is not None

        # Paso 2: Añadir varias jugadas con yardas normales (alrededor de 5)
        # Se necesitan suficientes jugadas para que el Z-score funcione bien
        for i in range(8):
            jugada = Play(
                nombre=f"Jugada Normal {i + 1}",
                tipo="run",
                formacion="SHOTGUN",
                yardas=5.0 + (i * 0.1),  # Yardas entre 5.0 y 5.7
                tasa_exito=0.65,
            )
            data_manager.anadir_jugada(playbook.id, jugada)

        # Paso 3: Recuperar el playbook y añadir una jugada con yardas extremas
        playbook_recuperado = data_manager.obtener_playbook(playbook.id)

        jugada_anomala = Play(
            nombre="Jugada Anomala T23",
            tipo="run",
            formacion="SHOTGUN",
            yardas=500.0,  # Valor extremo que es un outlier claro
            tasa_exito=0.65,
        )
        playbook_recuperado.jugadas.append(jugada_anomala)

        # Paso 4: Detectar anomalias en las jugadas del playbook
        anomalias = analyzer.detectar_anomalias(playbook_recuperado.jugadas)

        # La jugada con 500 yardas debe ser detectada como outlier
        assert len(anomalias) > 0
        nombres_anomalos = [a["jugada"].nombre for a in anomalias]
        assert "Jugada Anomala T23" in nombres_anomalos

    def test_T23_crud_completo_funciona_encadenado(self):
        """
        T23 - Pipeline CRUD: Crear, leer, actualizar y eliminar debe
        funcionar correctamente en secuencia.
        """

        # Crear playbook
        pb = data_manager.crear_playbook("CRUD Test")

        # Añadir jugada
        jugada = Play(nombre="Jugada CRUD", tipo="run", formacion="SHOTGUN", yardas=5.0)
        data_manager.anadir_jugada(pb.id, jugada)

        # Actualizar jugada
        data_manager.actualizar_jugada(pb.id, jugada.id, {"yardas": 10.0})

        # Verificar actualizacion
        pb_actualizado = data_manager.obtener_playbook(pb.id)
        jugada_actualizada = pb_actualizado.obtener_jugada(jugada.id)
        assert jugada_actualizada.yardas == 10.0

        # Eliminar jugada
        data_manager.eliminar_jugada(pb.id, jugada.id)

        # Verificar eliminacion
        pb_final = data_manager.obtener_playbook(pb.id)
        assert len(pb_final.jugadas) == 0

        # Eliminar playbook
        data_manager.eliminar_playbook(pb.id)

        # Verificar que ya no existe
        from exceptions import PlaybookNotFoundError
        with pytest.raises(PlaybookNotFoundError):
            data_manager.obtener_playbook(pb.id)


# --- Test T24: Simular -> Importar -> Predecir ---

class TestPipelineSimularPredecir:
    """
    T24 - Integracion: Verifica que generar datos sinteticos y usarlos
    para una prediccion funciona de extremo a extremo.
    """

    def test_T24_datos_sinteticos_permiten_calcular_prediccion(self, tmp_path):
        """
        T24 - Pipeline: Generar datos sinteticos, guardarlos en CSV,
        importarlos y calcular una prediccion debe funcionar sin errores.
        """

        # Paso 1: Generar dataset sintetico con suficientes jugadas
        jugadas_sinteticas = simulator.generar_jugadas(cantidad=20)
        assert len(jugadas_sinteticas) == 20

        # Paso 2: Guardar como CSV
        ruta_csv = str(tmp_path / "sintetico.csv")
        simulator.guardar_dataset_csv(jugadas_sinteticas, ruta_archivo=ruta_csv)

        # Paso 3: Importar desde CSV
        jugadas_importadas = data_importer.cargar_csv(ruta_csv)
        assert len(jugadas_importadas) > 0

        # Paso 4: Calcular prediccion con los datos importados
        resultado = analyzer.predecir_efectividad(jugadas_importadas, ventana=5)

        # Verificar que la prediccion es valida
        assert 0.0 <= resultado["prediccion"] <= 1.0
        assert resultado["total_registros"] == len(jugadas_importadas)

    def test_T24_pipeline_estadisticas_completo(self, tmp_path):
        """
        T24 - Pipeline estadisticas: Simular, analizar y generar grafico
        ASCII debe funcionar sin errores.
        """

        # Generar jugadas
        jugadas = simulator.generar_jugadas(cantidad=15)

        # Calcular estadisticas
        estadisticas = analyzer.calcular_estadisticas(jugadas)

        # Generar grafico ASCII (no debe lanzar excepcion)
        grafico = reporter.mostrar_grafico_ascii(estadisticas)

        assert isinstance(grafico, str)
        assert len(grafico) > 0
