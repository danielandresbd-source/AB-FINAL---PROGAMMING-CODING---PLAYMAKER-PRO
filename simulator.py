# ============================================================
# simulator.py
# RF10: Generador de datos sinteticos de jugadas para testing y demos
# Proyecto: AB Final - Programming & Coding
# ============================================================

"""
Este modulo genera datos sinteticos (falsos pero realistas) de jugadas
y playbooks de futbol americano.

Por que existe este modulo?
Porque para probar el resto de la aplicacion (analisis, alertas, reportes)
se necesitan muchos datos de ejemplo, y escribirlos a mano uno por uno
seria muy lento. Este modulo los genera automaticamente en cualquier
cantidad, con valores realistas (yardas, formaciones, tasas de exito, etc.)
en lugar de numeros aleatorios sin sentido.
"""

import csv
import json
import logging
import os
import random
from datetime import datetime, timedelta

from models import Formation, Play, Playbook

logger = logging.getLogger(__name__)

# --- Datos de ejemplo para generar jugadas realistas ---
# Estas listas son los "ingredientes" que combinamos al azar para crear
# cada jugada sintetica. Estan basadas en terminologia real de futbol
# americano para que los datos generados parezcan jugadas de verdad.

# Nombres base para jugadas ofensivas de corrida
NOMBRES_CORRIDA = [
    "HB Dive", "FB Blast", "HB Toss", "HB Sweep", "Power Run",
    "Counter Left", "Counter Right", "Draw Play", "QB Sneak",
    "Option Left", "Option Right", "Inside Zone", "Outside Zone",
]

# Nombres base para jugadas de pase
NOMBRES_PASE = [
    "Slant Route", "Curl Route", "Post Route", "Corner Route",
    "Go Route", "Screen Pass", "Quick Hitch", "Out Route",
    "Cross Route", "Fade Route", "Comeback Route", "Flat Route",
    "Seam Route", "Wagon Wheel", "Four Verticals",
]

# Nombres base para jugadas especiales
NOMBRES_ESPECIALES = [
    "Kickoff", "Punt Formation", "Field Goal", "Extra Point",
    "Onside Kick", "Fake Punt", "Fake Field Goal",
]

# Etiquetas posibles para las jugadas
ETIQUETAS_POSIBLES = [
    "short_yardage", "red_zone", "two_minute_drill", "third_down",
    "power_run", "quick_pass", "deep_ball", "goal_line", "screen",
    "trick_play", "formation_motion", "play_action",
]

# Situaciones de down-and-distance
DOWNS_DISPONIBLES = [
    "1st&10", "1st&goal",
    "2nd&long", "2nd&medium", "2nd&short",
    "3rd&long", "3rd&medium", "3rd&short",
    "4th&short", "4th&goal",
]

# Posiciones en el campo
POSICIONES_HASH = ["left", "middle", "right"]


def generar_jugadas(cantidad=10, tipo_ofensa=None):
    """
    Genera una lista de jugadas sinteticas con datos realistas.

    Args:
        cantidad: Numero de jugadas a generar (por defecto: 10).
        tipo_ofensa: Tipo de ofensa preferido. Si es None, mezcla tipos.
                     Puede ser 'run', 'pass', o 'special_teams'.

    Returns:
        Lista de objetos Play generados aleatoriamente.
    """

    # Caso limite: si piden 0 o menos jugadas, no tiene sentido generar nada.
    # Devolvemos lista vacia en vez de lanzar un error, porque pedir 0
    # jugadas no es realmente un error del usuario.
    if cantidad <= 0:
        logger.info("Se solicito generar 0 jugadas. Devolviendo lista vacia.")
        return []

    jugadas_generadas = []

    # Definir que tipos de jugada se van a generar.
    # Si el usuario pide un tipo especifico, generamos solo ese tipo.
    # Si no especifica nada, mezclamos los tres tipos con una proporcion
    # realista: en un partido real hay mas pases que corridas, y muy
    # pocas jugadas especiales (patadas, punts).
    if tipo_ofensa == "run":
        tipos_disponibles = ["run"]
    elif tipo_ofensa == "pass":
        tipos_disponibles = ["pass"]
    elif tipo_ofensa == "special_teams":
        tipos_disponibles = ["special_teams"]
    else:
        # Por defecto: 50% pase, 40% corrida, 10% especiales.
        # Truco simple para pesos de probabilidad sin usar random.choices():
        # repetimos cada tipo segun su peso y luego elegimos al azar
        # de la lista resultante (5 "pass" + 4 "run" + 1 "special_teams").
        tipos_disponibles = (
            ["pass"] * 5 + ["run"] * 4 + ["special_teams"] * 1
        )

    # Lista de todas las formaciones validas que existen en el sistema
    # (la sacamos del Enum Formation para no tener que escribirlas a mano)
    todas_las_formaciones = [f.value for f in Formation]

    # Fecha base para los timestamps. Restamos 'cantidad' dias para que,
    # al ir sumando horas mas adelante, las jugadas queden ordenadas
    # cronologicamente desde el pasado hasta el presente. Esto es
    # importante para RF7 (prediccion), que necesita datos en orden.
    fecha_base = datetime.now() - timedelta(days=cantidad)

    for i in range(cantidad):
        # Seleccionar un tipo de jugada aleatoriamente de los disponibles
        tipo = random.choice(tipos_disponibles)

        # Seleccionar el nombre base segun el tipo de jugada.
        # Tambien definimos que formaciones tienen mas sentido para
        # cada tipo: las corridas suelen usar formaciones con mas
        # corredores (I_FORMATION), los pases formaciones abiertas
        # (SHOTGUN, EMPTY_SET).
        if tipo == "run":
            nombre_base = random.choice(NOMBRES_CORRIDA)
            formaciones_preferidas = [
                "I_FORMATION", "SINGLEBACK", "PISTOL", "WILDCAT"
            ]
        elif tipo == "pass":
            nombre_base = random.choice(NOMBRES_PASE)
            formaciones_preferidas = [
                "SHOTGUN", "GUN_TRIPS", "EMPTY_SET", "SINGLEBACK"
            ]
        else:
            nombre_base = random.choice(NOMBRES_ESPECIALES)
            formaciones_preferidas = todas_las_formaciones

        # Agregar un numero al nombre para que cada jugada generada
        # tenga un nombre unico (evita duplicados exactos en el dataset)
        nombre = f"{nombre_base} {i + 1}"

        # Elegir formacion: el 70% de las veces usamos una formacion
        # "logica" para el tipo de jugada, y el 30% restante una
        # formacion completamente aleatoria. Esto simula que en la
        # realidad a veces los equipos usan formaciones poco comunes
        # para sorprender al rival.
        if random.random() < 0.7 and formaciones_preferidas:
            formacion = random.choice(formaciones_preferidas)
        else:
            formacion = random.choice(todas_las_formaciones)

        # Generar yardas realistas segun el tipo de jugada.
        # random.gauss(media, desviacion) genera una distribucion de
        # campana (la mayoria de valores cerca de la media, pocos
        # valores extremos), que se parece mas a estadisticas reales
        # de futbol que random.uniform() (que da igual probabilidad
        # a cualquier valor del rango).
        if tipo == "run":
            yardas = round(random.gauss(4.5, 3.0), 1)
        elif tipo == "pass":
            yardas = round(random.gauss(8.0, 6.0), 1)
        else:
            yardas = round(random.uniform(0, 50), 1)

        # Generar tasa de exito aleatoria entre 30% y 85%
        # (fuera de ese rango seria una jugada o demasiado mala o
        # sospechosamente perfecta para ser realista)
        tasa_exito = round(random.uniform(0.3, 0.85), 2)

        # Elegir down-distance aleatoriamente de las situaciones posibles
        down_distance = random.choice(DOWNS_DISPONIBLES)

        # Elegir en que parte del campo (hash) se ejecuta la jugada
        hash_position = random.choice(POSICIONES_HASH)

        # Seleccionar entre 0 y 2 etiquetas aleatorias sin repetir.
        # random.sample() nunca repite elementos, a diferencia de
        # random.choices(). El min() evita pedir mas etiquetas de
        # las que existen en la lista (proteccion defensiva).
        num_etiquetas = random.randint(0, 2)
        etiquetas = random.sample(ETIQUETAS_POSIBLES, min(num_etiquetas, len(ETIQUETAS_POSIBLES)))

        # Calcular la fecha de esta jugada en concreto, sumando horas
        # a la fecha base para mantener el orden cronologico
        fecha_jugada = fecha_base + timedelta(hours=i)

        # Crear el objeto Play con todos los datos generados
        jugada = Play(
            nombre=nombre,
            tipo=tipo,
            formacion=formacion,
            descripcion=f"Jugada sintetica de tipo {tipo} desde formacion {formacion}.",
            yardas=yardas,
            tasa_exito=tasa_exito,
            down_distance=down_distance,
            hash_position=hash_position,
            etiquetas=etiquetas,
            creada_en=fecha_jugada.isoformat(),
        )

        jugadas_generadas.append(jugada)

    logger.info(f"Se generaron {len(jugadas_generadas)} jugadas sinteticas.")

    return jugadas_generadas


def generar_playbooks(num_playbooks=2, jugadas_por_playbook=10):
    """
    Genera una lista de playbooks sinteticos con jugadas incluidas.

    Args:
        num_playbooks: Numero de playbooks a generar (por defecto: 2).
        jugadas_por_playbook: Jugadas por cada playbook (por defecto: 10).

    Returns:
        Lista de objetos Playbook generados con sus jugadas.
    """

    # Nombres tematicos que suenan a playbooks reales de futbol americano,
    # en vez de nombres genericos tipo "Playbook 1", "Playbook 2"
    nombres_playbooks = [
        "Red Zone Offense", "Two Minute Drill", "Short Yardage",
        "Third Down Package", "Opening Drive", "Goal Line Defense",
        "Spread Offense", "Power Running Game", "Quick Pass Attack",
    ]

    tipos_ofensa = ["spread", "power", "west_coast", "air_raid", "option"]

    playbooks_generados = []

    for i in range(num_playbooks):
        # Si pedimos mas playbooks que nombres tematicos disponibles,
        # usamos los nombres de la lista mientras alcancen, y a partir
        # de ahi generamos nombres genericos numerados para no repetir
        if i < len(nombres_playbooks):
            nombre = nombres_playbooks[i]
        else:
            nombre = f"Playbook Sintetico {i + 1}"

        tipo_ofensa = random.choice(tipos_ofensa)

        # Crear el playbook vacio primero
        playbook = Playbook(nombre=nombre, tipo_ofensa=tipo_ofensa)

        # Reutilizamos generar_jugadas() para llenar el playbook.
        # Esto evita duplicar logica: la generacion de jugadas
        # individuales ya esta resuelta arriba, aqui solo la usamos.
        jugadas = generar_jugadas(cantidad=jugadas_por_playbook)
        for jugada in jugadas:
            playbook.jugadas.append(jugada)

        playbooks_generados.append(playbook)

    logger.info(
        f"Se generaron {len(playbooks_generados)} playbooks sinteticos."
    )

    return playbooks_generados


def guardar_dataset_json(playbooks, ruta_archivo=None):
    """
    Guarda un conjunto de playbooks sinteticos en un archivo JSON.

    Args:
        playbooks: Lista de objetos Playbook a guardar.
        ruta_archivo: Ruta del archivo de salida (opcional).

    Returns:
        Ruta del archivo JSON guardado.
    """

    # Si no se especifica una ruta, generamos un nombre automatico
    # con la fecha y hora actual para que cada exportacion tenga
    # un nombre unico y no se sobreescriban entre si
    if not ruta_archivo:
        fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_archivo = os.path.join(
            "data", "exports", f"dataset_sintetico_{fecha_hora}.json"
        )

    # Crear la carpeta de destino si no existe todavia
    # (evita error si data/exports/ no se ha creado antes)
    os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)

    # Empaquetamos los playbooks junto con metadatos de cuando se generaron
    datos = {
        "generado_en": datetime.now().isoformat(),
        "playbooks": [pb.a_diccionario() for pb in playbooks],
    }

    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
        # indent=2 hace el JSON legible por humanos para depuracion
        json.dump(datos, archivo, indent=2, ensure_ascii=False)

    logger.info(f"Dataset sintetico guardado en: '{ruta_archivo}'")

    return ruta_archivo


def guardar_dataset_csv(jugadas, ruta_archivo=None):
    """
    Guarda una lista de jugadas sinteticas en un archivo CSV.

    Args:
        jugadas: Lista de objetos Play a guardar.
        ruta_archivo: Ruta del archivo de salida (opcional).

    Returns:
        Ruta del archivo CSV guardado.
    """

    if not ruta_archivo:
        fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_archivo = os.path.join(
            "data", "exports", f"jugadas_sinteticas_{fecha_hora}.csv"
        )

    os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)

    # Columnas en el orden en que queremos que aparezcan en el CSV
    columnas = [
        "nombre", "tipo", "formacion", "descripcion",
        "yardas", "tasa_exito", "down_distance", "hash_position", "etiquetas",
    ]

    with open(ruta_archivo, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()

        for jugada in jugadas:
            datos = jugada.a_diccionario()
            # Solo escribimos las columnas que definimos arriba,
            # ignorando cualquier campo extra que tenga el diccionario
            fila = {col: datos.get(col, "") for col in columnas}
            # Las etiquetas son una lista en Python, pero CSV no soporta
            # listas como valor de celda, asi que las unimos con ";"
            # Ejemplo: ["red_zone", "power_run"] -> "red_zone;power_run"
            fila["etiquetas"] = ";".join(datos.get("etiquetas", []))
            escritor.writerow(fila)

    logger.info(f"Dataset CSV guardado en: '{ruta_archivo}'")

    return ruta_archivo
