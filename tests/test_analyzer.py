# ============================================================
# tests/test_analyzer.py
# Tests unitarios para analyzer.py (RF3, RF4, RF7)
# Cubre los casos T11, T12, T13, T14, T15 del plan de testing
# Proyecto: AB Final - Programming & Coding - MSMK 2025-2026
# ============================================================

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import analyzer
from models import Play


# --- Funcion de ayuda para crear jugadas de prueba ---

def crear_jugada(nombre="Test Play", tipo="run", formacion="SHOTGUN",
                 yardas=5.0, tasa_exito=0.65, down_distance="1st&10",
                 hash_position="middle"):
    """Crea una jugada de prueba con los valores indicados."""

    return Play(
        nombre=nombre,
        tipo=tipo,
        formacion=formacion,
        yardas=yardas,
        tasa_exito=tasa_exito,
        down_distance=down_distance,
        hash_position=hash_position,
    )


def crear_dataset_10_jugadas():
    """
    Crea un dataset de 10 jugadas con valores variados para testing.
    """

    jugadas = [
        crear_jugada("HB Dive", "run", "I_FORMATION", 4.0, 0.65),
        crear_jugada("Slant Route", "pass", "SHOTGUN", 8.0, 0.72),
        crear_jugada("Counter Left", "run", "SINGLEBACK", 3.0, 0.55),
        crear_jugada("Post Route", "pass", "SHOTGUN", 15.0, 0.45),
        crear_jugada("HB Toss", "run", "PISTOL", 5.5, 0.60),
        crear_jugada("Screen Pass", "pass", "EMPTY_SET", 7.0, 0.70),
        crear_jugada("Power Run", "run", "I_FORMATION", 3.5, 0.68),
        crear_jugada("Go Route", "pass", "GUN_TRIPS", 20.0, 0.35),
        crear_jugada("QB Sneak", "run", "SINGLEBACK", 1.5, 0.80),
        crear_jugada("Fade Route", "pass", "SHOTGUN", 12.0, 0.40),
    ]

    return jugadas


# --- Tests T11: Estadisticas descriptivas ---

class TestCalcularEstadisticas:
    """Tests para la funcion calcular_estadisticas del modulo analyzer."""

    def test_T11_estadisticas_con_10_jugadas_calcula_correctamente(self):
        """
        T11 - Unitario: 10 jugadas con yardas distintas debe calcular
        media, minimo, maximo y top-5 correctamente.
        """

        jugadas = crear_dataset_10_jugadas()
        estadisticas = analyzer.calcular_estadisticas(jugadas)

        assert estadisticas["total_jugadas"] == 10
        assert estadisticas["yardas_minimas"] == 1.5
        assert estadisticas["yardas_maximas"] == 20.0
        assert estadisticas["yardas_promedio"] == 7.95

    def test_T11_top_5_jugadas_ordenadas_por_tasa_exito(self):
        """
        T11 - El top 5 debe estar ordenado de mayor a menor tasa de exito.
        """

        jugadas = crear_dataset_10_jugadas()
        estadisticas = analyzer.calcular_estadisticas(jugadas)
        top_5 = estadisticas["top_5_jugadas"]

        assert len(top_5) == 5
        # Verificar que estan ordenados de mayor a menor
        for i in range(len(top_5) - 1):
            assert top_5[i]["tasa_exito"] >= top_5[i + 1]["tasa_exito"]

    def test_T11_jugadas_por_tipo_cuenta_correctamente(self):
        """
        T11 - La distribucion por tipo debe contar correctamente.
        """

        jugadas = crear_dataset_10_jugadas()
        estadisticas = analyzer.calcular_estadisticas(jugadas)
        por_tipo = estadisticas["jugadas_por_tipo"]

        # El dataset tiene 5 runs y 5 passes
        assert por_tipo.get("run") == 5
        assert por_tipo.get("pass") == 5

    def test_T11_lista_vacia_devuelve_diccionario_vacio(self):
        """
        T11 - Lista de jugadas vacia debe devolver diccionario vacio.
        """

        resultado = analyzer.calcular_estadisticas([])
        assert resultado == {}


# --- Tests T12: Deteccion de anomalias ---

class TestDetectarAnomalias:
    """Tests para la funcion detectar_anomalias del modulo analyzer."""

    def test_T12_dataset_con_outlier_detecta_la_jugada_extrema(self):
        """
        T12 - Unitario: Dataset con una jugada de yardas extremas debe
        detectarla como anomalia por Z-score.
        """

        jugadas = crear_dataset_10_jugadas()

        # Agregar una jugada con yardas extremas (outlier claro)
        jugada_outlier = crear_jugada(
            nombre="Jugada Extrema",
            yardas=999.0,  # Valor extremo que definitivamente es outlier
        )
        jugadas.append(jugada_outlier)

        anomalias = analyzer.detectar_anomalias(jugadas)

        # Verificar que se detectaron anomalias
        assert len(anomalias) > 0

        # Verificar que la jugada extrema fue detectada
        nombres_anomalos = [a["jugada"].nombre for a in anomalias]
        assert "Jugada Extrema" in nombres_anomalos

    def test_T12_anomalia_incluye_razon_z_score(self):
        """
        T12 - La anomalia por outlier debe tener la razon del Z-score en sus razones.
        """

        jugadas = crear_dataset_10_jugadas()
        jugada_outlier = crear_jugada(nombre="Outlier Test", yardas=999.0)
        jugadas.append(jugada_outlier)

        anomalias = analyzer.detectar_anomalias(jugadas)

        # Buscar la anomalia del outlier
        for anomalia in anomalias:
            if anomalia["jugada"].nombre == "Outlier Test":
                razones = " ".join(anomalia["razones"])
                assert "Z-score" in razones or "rango" in razones.lower()
                break

    def test_T12_nombre_duplicado_detectado_como_anomalia(self):
        """
        T12 - Dos jugadas con el mismo nombre deben ser detectadas como anomalias.
        """

        jugadas = [
            crear_jugada(nombre="HB Dive", yardas=5.0),
            crear_jugada(nombre="HB Dive", yardas=5.5),  # Nombre duplicado
            crear_jugada(nombre="Slant Route", yardas=8.0),
        ]

        anomalias = analyzer.detectar_anomalias(jugadas)

        # Ambas jugadas con nombre "HB Dive" deben ser detectadas
        nombres_anomalos = [a["jugada"].nombre for a in anomalias]
        assert nombres_anomalos.count("HB Dive") == 2


# --- Tests T13: Anomalias con un solo registro ---

class TestDetectarAnomaliasDatosInsuficientes:
    """Tests para deteccion de anomalias con pocos datos."""

    def test_T13_una_sola_jugada_no_genera_anomalias_de_zscore(self):
        """
        T13 - Limite: Lista con 1 sola jugada no debe generar anomalias de Z-score
        porque no hay suficientes datos para calcular una distribucion.
        """

        jugadas = [crear_jugada(nombre="Unica Jugada", yardas=5.0)]

        anomalias = analyzer.detectar_anomalias(jugadas)

        # No debe haber anomalias de Z-score con solo una jugada
        for anomalia in anomalias:
            for razon in anomalia["razones"]:
                assert "Z-score" not in razon

    def test_T13_lista_vacia_devuelve_lista_vacia(self):
        """
        T13 - Lista vacia debe devolver lista vacia de anomalias.
        """

        anomalias = analyzer.detectar_anomalias([])
        assert anomalias == []


# --- Tests T14: Prediccion de efectividad ---

class TestPredecirEfectividad:
    """Tests para la funcion predecir_efectividad del modulo analyzer."""

    def test_T14_prediccion_con_10_registros_devuelve_float_valido(self):
        """
        T14 - Unitario: 10 registros validos con ventana=5 debe devolver
        un float en el rango [0.0, 1.0].
        """

        jugadas = crear_dataset_10_jugadas()
        resultado = analyzer.predecir_efectividad(jugadas, ventana=5)

        prediccion = resultado["prediccion"]

        assert isinstance(prediccion, float)
        assert 0.0 <= prediccion <= 1.0

    def test_T14_resultado_contiene_todos_los_campos_esperados(self):
        """
        T14 - El resultado debe contener: prediccion, tendencia,
        ventana_usada, total_registros, medias_moviles, ultimo_valor_real.
        """

        jugadas = crear_dataset_10_jugadas()
        resultado = analyzer.predecir_efectividad(jugadas, ventana=5)

        assert "prediccion" in resultado
        assert "tendencia" in resultado
        assert "ventana_usada" in resultado
        assert "total_registros" in resultado
        assert "medias_moviles" in resultado
        assert "ultimo_valor_real" in resultado

    def test_T14_tendencia_tiene_valor_valido(self):
        """
        T14 - El campo tendencia debe ser 'subiendo', 'bajando' o 'estable'.
        """

        jugadas = crear_dataset_10_jugadas()
        resultado = analyzer.predecir_efectividad(jugadas, ventana=5)

        tendencias_validas = {"subiendo", "bajando", "estable", "sin datos suficientes"}
        assert resultado["tendencia"] in tendencias_validas


# --- Tests T15: Prediccion con pocos registros ---

class TestPredecirEfectividadError:
    """Tests para errores en la prediccion por falta de datos."""

    def test_T15_menos_registros_que_ventana_lanza_value_error(self):
        """
        T15 - Error: Menos registros que el tamano de la ventana debe
        lanzar ValueError con un mensaje claro.
        """

        # Solo 3 jugadas con ventana de 5
        jugadas = [
            crear_jugada(nombre=f"Jugada {i}", yardas=float(i))
            for i in range(3)
        ]

        with pytest.raises(ValueError) as info_error:
            analyzer.predecir_efectividad(jugadas, ventana=5)

        # El mensaje debe ser claro sobre cuantos registros se necesitan
        assert "5" in str(info_error.value)

    def test_T15_lista_vacia_lanza_value_error(self):
        """
        T15 - Lista de jugadas vacia debe lanzar ValueError.
        """

        with pytest.raises(ValueError):
            analyzer.predecir_efectividad([], ventana=5)
