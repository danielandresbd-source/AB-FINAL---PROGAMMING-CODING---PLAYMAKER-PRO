# ============================================================
# tests/test_performance.py
# Tests de rendimiento (T25)
# Verifica que el sistema cumple el requisito NF1:
# procesar 10.000 jugadas en menos de 3 segundos
# Proyecto: AB Final - Programming & Coding - MSMK 2025-2026
# ============================================================

import time
import csv

import analyzer
import data_importer
import simulator

# --- Test T25: Rendimiento con 10.000 jugadas ---

class TestRendimiento:
    """
    Tests para verificar que el sistema cumple el requisito de rendimiento NF1.
    El sistema debe procesar 10.000 jugadas en menos de 3 segundos.
    """

    def test_T25_cargar_10000_jugadas_en_menos_de_3_segundos(self, tmp_path):
        """
        T25 - Rendimiento: Importar un CSV con 10.000 jugadas y calcular
        estadisticas debe completarse en menos de 3 segundos.
        """

        # Crear CSV con 10.000 jugadas
        ruta_csv = str(tmp_path / "jugadas_rendimiento.csv")

        formaciones = [
            "SHOTGUN", "I_FORMATION", "SINGLEBACK",
            "PISTOL", "EMPTY_SET", "GUN_TRIPS"
        ]
        tipos = ["run", "pass", "special_teams"]
        downs = ["1st&10", "2nd&long", "3rd&short", "4th&goal"]

        with open(ruta_csv, "w", encoding="utf-8", newline="") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow([
                "nombre", "tipo", "formacion", "yardas",
                "tasa_exito", "down_distance", "hash_position"
            ])

            for i in range(10000):
                escritor.writerow([
                    f"Jugada {i + 1}",
                    tipos[i % len(tipos)],
                    formaciones[i % len(formaciones)],
                    round(2.0 + (i % 20), 1),
                    round(0.30 + ((i % 7) * 0.1), 2),
                    downs[i % len(downs)],
                    "middle",
                ])

        # Medir el tiempo de carga + calculo de estadisticas
        tiempo_inicio = time.time()

        jugadas = data_importer.cargar_csv(ruta_csv)
        estadisticas = analyzer.calcular_estadisticas(jugadas)

        tiempo_total = time.time() - tiempo_inicio

        # Verificar que se cargaron todas las jugadas
        assert len(jugadas) == 10000

        # Verificar que las estadisticas se calcularon correctamente
        assert estadisticas["total_jugadas"] == 10000

        # Verificar que se completo en menos de 3 segundos (requisito NF1)
        assert tiempo_total < 3.0, (
            f"El procesamiento tardo {tiempo_total:.2f} segundos. "
            "El limite es de 3 segundos (requisito NF1)."
        )

    def test_T25_deteccion_anomalias_1000_jugadas_es_rapida(self):
        """
        T25 - Rendimiento: La deteccion de anomalias en 1.000 jugadas
        debe completarse en menos de 2 segundos.
        """

        # Generar 1.000 jugadas sinteticas
        jugadas = simulator.generar_jugadas(cantidad=1000)

        # Medir el tiempo de deteccion de anomalias
        tiempo_inicio = time.time()

        analyzer.detectar_anomalias(jugadas)

        tiempo_total = time.time() - tiempo_inicio

        # Debe completarse en menos de 2 segundos
        assert tiempo_total < 2.0, (
            f"La deteccion de anomalias tardo {tiempo_total:.2f} segundos. "
            "El limite es de 2 segundos."
        )

    def test_T25_prediccion_1000_registros_es_rapida(self):
        """
        T25 - Rendimiento: La prediccion con 1.000 registros debe
        completarse en menos de 1 segundo.
        """

        jugadas = simulator.generar_jugadas(cantidad=1000)

        tiempo_inicio = time.time()

        resultado = analyzer.predecir_efectividad(jugadas, ventana=10)

        tiempo_total = time.time() - tiempo_inicio

        assert resultado["prediccion"] is not None
        assert tiempo_total < 1.0, (
            f"La prediccion tardo {tiempo_total:.2f} segundos. "
            "El limite es de 1 segundo."
        )
