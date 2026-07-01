# ============================================================
# analyzer.py
# RF3: Estadisticas descriptivas de jugadas
# RF4: Deteccion de anomalias en jugadas
# RF7: Prediccion de efectividad con media movil simple
# Proyecto: AB Final - Programming & Coding - MSMK 2025-2026
# ============================================================

import logging
import math
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)


# --- RF3: Estadisticas descriptivas ---

def calcular_estadisticas(jugadas):
    """
    Calcula estadisticas descriptivas de una lista de jugadas.

    Calcula: jugadas por tipo, formacion mas usada, yardas promedio,
    yardas minimas, yardas maximas, y las 5 mejores jugadas.

    Args:
        jugadas: Lista de objetos Play con los datos de las jugadas.

    Returns:
        Diccionario con todas las estadisticas calculadas.
        Devuelve diccionario vacio si la lista de jugadas esta vacia.
    """

    if not jugadas:
        logger.warning("No hay jugadas para calcular estadisticas.")
        return {}

    # Counter cuenta cuantas jugadas hay de cada tipo y formacion.
    # Es mucho mas limpio que hacer un bucle manual con un dict vacio.
    # Ejemplo: Counter(['run', 'pass', 'run']) -> {'run': 2, 'pass': 1}
    jugadas_por_tipo = dict(Counter(jugada.tipo for jugada in jugadas))
    jugadas_por_formacion = dict(Counter(jugada.formacion for jugada in jugadas))

    # Encontrar la formacion mas usada usando el maximo del conteo
    formacion_mas_usada = max(
        jugadas_por_formacion, key=lambda f: jugadas_por_formacion[f]
    )

    # Calcular estadisticas basicas de yardas
    lista_yardas = [j.yardas for j in jugadas]
    yardas_promedio = sum(lista_yardas) / len(lista_yardas)
    yardas_minimas = min(lista_yardas)
    yardas_maximas = max(lista_yardas)

    # Top 5 jugadas ordenadas de mayor a menor tasa de exito
    jugadas_ordenadas = sorted(jugadas, key=lambda j: j.tasa_exito, reverse=True)
    top_5_jugadas = [
        {
            "nombre": j.nombre,
            "tipo": j.tipo,
            "tasa_exito": j.tasa_exito,
            "yardas": j.yardas,
        }
        for j in jugadas_ordenadas[:5]
    ]

    estadisticas = {
        "total_jugadas": len(jugadas),
        "jugadas_por_tipo": jugadas_por_tipo,
        "jugadas_por_formacion": jugadas_por_formacion,
        "formacion_mas_usada": formacion_mas_usada,
        "yardas_promedio": round(yardas_promedio, 2),
        "yardas_minimas": yardas_minimas,
        "yardas_maximas": yardas_maximas,
        "top_5_jugadas": top_5_jugadas,
    }

    logger.info(f"Estadisticas calculadas para {len(jugadas)} jugadas.")

    return estadisticas


# --- RF4: Deteccion de anomalias ---

def detectar_anomalias(jugadas):
    """
    Detecta jugadas con datos inusuales o incorrectos en el dataset.

    Una jugada se considera anomala si cumple alguna de estas condiciones:
    - Sus yardas tienen un Z-score mayor a 2.5 (outlier estadistico)
    - Su nombre esta duplicado en el dataset
    - Su tasa de exito esta fuera del rango [0.0, 1.0]
    - Su situacion de down-and-distance no es reconocida
    - Su hash_position no es valida

    Args:
        jugadas: Lista de objetos Play a analizar.

    Returns:
        Lista de diccionarios con las jugadas anomalas y sus razones.
        Cada elemento tiene: 'jugada' y 'razones' (lista de strings).
    """

    if not jugadas:
        logger.warning("No hay jugadas para analizar anomalias.")
        return []

    anomalias_encontradas = []

    # Calcular media y desviacion estandar de yardas para el Z-score.
    # El Z-score nos dice cuantas desviaciones estandar se aleja un valor
    # de la media. Si es mayor a 2.5 lo consideramos un outlier.
    lista_yardas = [j.yardas for j in jugadas]
    media_yardas = sum(lista_yardas) / len(lista_yardas)
    varianza = sum((y - media_yardas) ** 2 for y in lista_yardas) / len(lista_yardas)
    desviacion_estandar = math.sqrt(varianza) if varianza > 0 else 0

    # Usamos Counter para contar cuantas veces aparece cada nombre.
    # Es mas eficiente que llamar a list.count() dentro del bucle principal
    # porque Counter recorre la lista una sola vez (O(n)) mientras que
    # list.count() la recorreria una vez por cada jugada (O(n^2)).
    nombres_counter = Counter(j.nombre.lower() for j in jugadas)

    # Situaciones de down-and-distance que reconoce el sistema
    downs_validos = [
        "1st&10", "1st&goal",
        "2nd&long", "2nd&medium", "2nd&short", "2nd&goal",
        "3rd&long", "3rd&medium", "3rd&short", "3rd&goal",
        "4th&short", "4th&goal", "4th&long",
    ]

    # Posiciones validas en el campo
    posiciones_validas = ["left", "middle", "right"]

    for jugada in jugadas:
        razones_anomalia = []

        # Verificar si las yardas son un outlier estadistico
        if desviacion_estandar > 0:
            z_score = (jugada.yardas - media_yardas) / desviacion_estandar
            if abs(z_score) > 2.5:
                razones_anomalia.append(
                    f"Yardas fuera del rango estadistico (Z-score = "
                    f"{round(z_score, 2)})"
                )

        # Verificar nombre duplicado usando el Counter precalculado
        # Esto evita recorrer toda la lista de nuevo por cada jugada
        if nombres_counter[jugada.nombre.lower()] > 1:
            razones_anomalia.append("Nombre de jugada duplicado en el dataset")

        # Verificar tasa de exito imposible (debe estar entre 0 y 1)
        if jugada.tasa_exito < 0.0 or jugada.tasa_exito > 1.0:
            razones_anomalia.append(
                f"Tasa de exito fuera del rango valido: {jugada.tasa_exito}"
            )

        # Verificar down-and-distance desconocido
        if jugada.down_distance not in downs_validos:
            razones_anomalia.append(
                f"Situacion de down-and-distance desconocida: "
                f"'{jugada.down_distance}'"
            )

        # Verificar hash_position desconocida
        if jugada.hash_position not in posiciones_validas:
            razones_anomalia.append(
                f"Posicion en el campo no reconocida: '{jugada.hash_position}'"
            )
        if razones_anomalia:
            anomalias_encontradas.append({
                "jugada": jugada,
                "razones": razones_anomalia,
            })

    logger.info(
        f"Deteccion de anomalias completada: "
        f"{len(anomalias_encontradas)} jugadas anomalas de {len(jugadas)} totales."
    )

    return anomalias_encontradas


# --- RF7: Prediccion de efectividad ---

def predecir_efectividad(jugadas, ventana=5):
    """
    Predice la efectividad de las proximas jugadas usando media movil simple.

    La media movil simple (SMA) calcula el promedio de los ultimos N registros
    (donde N es el tamano de la ventana) y usa ese promedio como prediccion.
    Es el metodo mas basico de prediccion de tendencias temporales.

    Args:
        jugadas: Lista de objetos Play ordenados cronologicamente.
                 Se necesitan al menos 'ventana' registros.
        ventana: Tamano de la ventana de la media movil (por defecto: 5).

    Returns:
        Diccionario con la prediccion y el resumen del calculo.

    Raises:
        ValueError: Si hay menos registros que el tamano de la ventana.
    """

    if len(jugadas) < ventana:
        raise ValueError(
            f"Se necesitan al menos {ventana} registros para calcular "
            f"la prediccion. Solo hay {len(jugadas)} jugadas."
        )

    # Ordenar por fecha de creacion para respetar el orden cronologico
    jugadas_ordenadas = sorted(jugadas, key=lambda j: j.creada_en)
    tasas_de_exito = [j.tasa_exito for j in jugadas_ordenadas]

    # Calcular la media movil deslizante.
    # Para cada posicion i, tomamos los 'ventana' valores anteriores
    # y calculamos su promedio. La ultima media es la prediccion.
    medias_moviles = []
    for i in range(ventana, len(tasas_de_exito) + 1):
        ventana_actual = tasas_de_exito[i - ventana:i]
        media = sum(ventana_actual) / ventana
        medias_moviles.append(round(media, 4))

    # La prediccion es la ultima media movil calculada
    prediccion = medias_moviles[-1]

    # Calcular la tendencia comparando las dos ultimas medias moviles
    if len(medias_moviles) >= 2:
        diferencia = medias_moviles[-1] - medias_moviles[-2]
        if diferencia > 0.01:
            tendencia = "subiendo"
        elif diferencia < -0.01:
            tendencia = "bajando"
        else:
            tendencia = "estable"
    else:
        tendencia = "sin datos suficientes"

    resultado = {
        "prediccion": prediccion,
        "tendencia": tendencia,
        "ventana_usada": ventana,
        "total_registros": len(jugadas),
        "medias_moviles": medias_moviles,
        "ultimo_valor_real": tasas_de_exito[-1],
    }

    logger.info(
        f"Prediccion calculada con ventana={ventana}: {prediccion} "
        f"(tendencia: {tendencia})"
    )

    return resultado


def obtener_resumen_tendencias(jugadas):
    """
    Genera un resumen de tendencias agrupando jugadas por tipo.

    Args:
        jugadas: Lista de objetos Play para analizar.

    Returns:
        Diccionario con estadisticas de tendencia por tipo de jugada.
        Solo incluye tipos con al menos 2 jugadas (necesario para comparar).
    """

    if not jugadas:
        return {}

    # defaultdict(list) agrupa las jugadas por tipo automaticamente.
    # Es equivalente a hacer un if/else manual para inicializar la lista,
    # pero mucho mas limpio de leer.
    jugadas_por_tipo = defaultdict(list)
    for jugada in jugadas:
        jugadas_por_tipo[jugada.tipo].append(jugada)

    resumen = {}

    for tipo, jugadas_tipo in jugadas_por_tipo.items():
        # Necesitamos al menos 2 jugadas del mismo tipo para comparar
        if len(jugadas_tipo) >= 2:
            tasas = [j.tasa_exito for j in jugadas_tipo]
            promedio = sum(tasas) / len(tasas)
            resumen[tipo] = {
                "total_jugadas": len(jugadas_tipo),
                "tasa_promedio": round(promedio, 4),
                "mejor_jugada": max(
                    jugadas_tipo, key=lambda j: j.tasa_exito
                ).nombre,
                "peor_jugada": min(
                    jugadas_tipo, key=lambda j: j.tasa_exito
                ).nombre,
            }

    return resumen
