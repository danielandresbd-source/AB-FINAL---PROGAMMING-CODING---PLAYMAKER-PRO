# ============================================================
# simulator.py
# RF10: Generador de datos sinteticos de jugadas para testing y demos
# Proyecto: AB Final - Programming & Coding
# ============================================================

import csv
import json
import logging
import os
import random
from datetime import datetime, timedelta

from models import Formation, Play, Playbook

logger = logging.getLogger(__name__)

# --- Datos de ejemplo para generar jugadas realistas ---

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

    if cantidad <= 0:
        logger.info("Se solicito generar 0 jugadas. Devolviendo lista vacia.")
        return []

    jugadas_generadas = []

    # Definir que tipos de jugada se van a generar
    if tipo_ofensa == "run":
        tipos_disponibles = ["run"]
    elif tipo_ofensa == "pass":
        tipos_disponibles = ["pass"]
    elif tipo_ofensa == "special_teams":
        tipos_disponibles = ["special_teams"]
    else:
        # Por defecto: 50% pase, 40% corrida, 10% especiales
        tipos_disponibles = (
            ["pass"] * 5 + ["run"] * 4 + ["special_teams"] * 1
        )

    # Lista de formaciones disponibles
    todas_las_formaciones = [f.value for f in Formation]

    # Fecha base para los timestamps (para que esten en orden cronologico)
    fecha_base = datetime.now() - timedelta(days=cantidad)

    for i in range(cantidad):
        # Seleccionar un tipo de jugada aleatoriamente
        tipo = random.choice(tipos_disponibles)

        # Seleccionar el nombre segun el tipo
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

        # Agregar un numero al nombre para que sea unico
        nombre = f"{nombre_base} {i + 1}"

        # Elegir formacion con preferencia segun el tipo de jugada
        if random.random() < 0.7 and formaciones_preferidas:
            formacion = random.choice(formaciones_preferidas)
        else:
            formacion = random.choice(todas_las_formaciones)

        # Generar yardas realistas segun el tipo
        if tipo == "run":
            yardas = round(random.gauss(4.5, 3.0), 1)
        elif tipo == "pass":
            yardas = round(random.gauss(8.0, 6.0), 1)
        else:
            yardas = round(random.uniform(0, 50), 1)

        # Generar tasa de exito aleatoria
        tasa_exito = round(random.uniform(0.3, 0.85), 2)

        # Elegir down-distance aleatoriamente
        down_distance = random.choice(DOWNS_DISPONIBLES)

        # Elegir hash position aleatoriamente
        hash_position = random.choice(POSICIONES_HASH)

        # Seleccionar 1 o 2 etiquetas aleatorias
        num_etiquetas = random.randint(0, 2)
        etiquetas = random.sample(ETIQUETAS_POSIBLES, min(num_etiquetas, len(ETIQUETAS_POSIBLES)))

        # Calcular la fecha de esta jugada (en orden cronologico)
        fecha_jugada = fecha_base + timedelta(hours=i)

        # Crear el objeto Play
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

    nombres_playbooks = [
        "Red Zone Offense", "Two Minute Drill", "Short Yardage",
        "Third Down Package", "Opening Drive", "Goal Line Defense",
        "Spread Offense", "Power Running Game", "Quick Pass Attack",
    ]

    tipos_ofensa = ["spread", "power", "west_coast", "air_raid", "option"]

    playbooks_generados = []

    for i in range(num_playbooks):
        # Elegir nombre del playbook
        if i < len(nombres_playbooks):
            nombre = nombres_playbooks[i]
        else:
            nombre = f"Playbook Sintetico {i + 1}"

        tipo_ofensa = random.choice(tipos_ofensa)

        # Crear el playbook
        playbook = Playbook(nombre=nombre, tipo_ofensa=tipo_ofensa)

        # Generar y agregar jugadas al playbook
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

    if not ruta_archivo:
        fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_archivo = os.path.join(
            "data", "exports", f"dataset_sintetico_{fecha_hora}.json"
        )

    os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)

    datos = {
        "generado_en": datetime.now().isoformat(),
        "playbooks": [pb.a_diccionario() for pb in playbooks],
    }

    with open(ruta_archivo, "w", encoding="utf-8") as archivo:
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

    columnas = [
        "nombre", "tipo", "formacion", "descripcion",
        "yardas", "tasa_exito", "down_distance", "hash_position", "etiquetas",
    ]

    with open(ruta_archivo, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()

        for jugada in jugadas:
            datos = jugada.a_diccionario()
            fila = {col: datos.get(col, "") for col in columnas}
            fila["etiquetas"] = ";".join(datos.get("etiquetas", []))
            escritor.writerow(fila)

    logger.info(f"Dataset CSV guardado en: '{ruta_archivo}'")

    return ruta_archivo
