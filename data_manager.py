# ============================================================
# data_manager.py
# RF2: CRUD de Playbooks y Jugadas con persistencia en JSON
# Proyecto: AB Final - Programming & Coding
# ============================================================

"""
Este modulo implementa el CRUD (Create, Read, Update, Delete) del sistema.

CRUD significa:
- Create: crear nuevos playbooks y jugadas
- Read: leer y listar playbooks y jugadas existentes
- Update: modificar datos de un playbook o jugada
- Delete: eliminar un playbook o jugada

Todos los datos se guardan en un archivo JSON (playbooks.json). Esto
significa que los datos persisten en disco y siguen ahi aunque
cerremos y volvamos a abrir el programa, a diferencia de guardarlos
solo en variables de Python que se pierden al terminar la ejecucion.
"""

import json
import logging
import os
from datetime import datetime

from exceptions import PlaybookNotFoundError, ValidationError
from models import Playbook

# Configuracion del sistema de registro de eventos
logger = logging.getLogger(__name__)

# Ruta del archivo JSON donde se guardan todos los datos
RUTA_JSON = os.path.join("data", "playbooks.json")


# --- Funciones de lectura y escritura del archivo JSON ---
# Estas funciones empiezan con guion bajo (_cargar_datos_json) porque
# son funciones "privadas": solo las usan las demas funciones de este
# mismo modulo internamente, no estan pensadas para llamarse desde
# fuera (cli.py, tests, etc.)

def _cargar_datos_json():
    """
    Lee el archivo JSON y devuelve los datos guardados.

    Si el archivo no existe, devuelve una estructura vacia.

    Returns:
        Diccionario con la lista de playbooks guardados.
    """

    # Si el archivo todavia no existe (por ejemplo, primera vez que
    # se ejecuta la app), no hay nada que leer: devolvemos una
    # estructura vacia en lugar de lanzar un error
    if not os.path.exists(RUTA_JSON):
        return {"playbooks": []}

    try:
        with open(RUTA_JSON, encoding="utf-8") as archivo:
            datos = json.load(archivo)
            return datos
    except json.JSONDecodeError:
        # Si el archivo existe pero su contenido no es JSON valido
        # (por ejemplo, se corrompio o alguien lo edito mal a mano),
        # en vez de crashear toda la app, avisamos en el log y
        # continuamos con datos vacios
        logger.error(
            f"El archivo '{RUTA_JSON}' esta corrupto o no es JSON valido. "
            "Se iniciara con datos vacios."
        )
        return {"playbooks": []}


def _guardar_datos_json(datos):
    """
    Guarda los datos en el archivo JSON.

    Crea el directorio 'data/' si no existe.

    Args:
        datos: Diccionario con los datos a guardar.
    """

    # Crear el directorio data/ si no existe todavia
    # (exist_ok=True evita que lance error si ya existe)
    os.makedirs(os.path.dirname(RUTA_JSON), exist_ok=True)

    with open(RUTA_JSON, "w", encoding="utf-8") as archivo:
        # indent=2 hace el JSON legible por humanos (util para depurar)
        # ensure_ascii=False permite guardar acentos y caracteres especiales
        json.dump(datos, archivo, indent=2, ensure_ascii=False)

    logger.info(f"Datos guardados correctamente en '{RUTA_JSON}'.")


def _obtener_todos_playbooks():
    """
    Lee el JSON y devuelve todos los playbooks como objetos Playbook.

    Returns:
        Lista de objetos Playbook.
    """

    datos = _cargar_datos_json()
    playbooks = []

    # El JSON guarda los playbooks como diccionarios planos, asi que
    # los convertimos de vuelta a objetos Playbook para poder usar
    # sus metodos (anadir_jugada, obtener_jugada, etc.)
    for datos_pb in datos.get("playbooks", []):
        playbook = Playbook.desde_diccionario(datos_pb)
        playbooks.append(playbook)

    return playbooks


def _guardar_todos_playbooks(playbooks):
    """
    Guarda una lista de playbooks en el archivo JSON.

    Args:
        playbooks: Lista de objetos Playbook a guardar.
    """

    # Convertimos cada objeto Playbook de vuelta a diccionario antes
    # de guardarlo, porque json.dump() no sabe serializar objetos
    # propios de Python directamente, solo tipos basicos (dict, list,
    # str, int, etc.)
    datos = {
        "playbooks": [pb.a_diccionario() for pb in playbooks]
    }
    _guardar_datos_json(datos)


# --- Operaciones CRUD para Playbooks ---

def crear_playbook(nombre, tipo_ofensa="spread"):
    """
    Crea un nuevo playbook y lo guarda en el archivo JSON.

    Args:
        nombre: Nombre del playbook (obligatorio, no puede estar vacio).
        tipo_ofensa: Estilo de juego del playbook (por defecto: 'spread').

    Returns:
        El objeto Playbook creado.

    Raises:
        ValidationError: Si el nombre esta vacio.
    """

    # Validar que el nombre no este vacio antes de crear nada.
    # .strip() elimina espacios en blanco, asi que un nombre de
    # solo espacios ("   ") tambien se considera vacio
    if not nombre or not nombre.strip():
        raise ValidationError("El nombre del playbook no puede estar vacio.")

    # Crear el nuevo playbook con los datos ya limpios (sin espacios
    # sobrantes al principio o final)
    nuevo_playbook = Playbook(
        nombre=nombre.strip(),
        tipo_ofensa=tipo_ofensa.strip() if tipo_ofensa else "spread",
    )

    # Cargar todos los playbooks existentes desde el JSON y anadir
    # el nuevo a la lista en memoria
    playbooks = _obtener_todos_playbooks()
    playbooks.append(nuevo_playbook)

    # Guardar la lista completa (con el nuevo incluido) de vuelta al JSON.
    # Como no hay base de datos, cada operacion de escritura reescribe
    # el archivo entero con todos los playbooks.
    _guardar_todos_playbooks(playbooks)

    logger.info(f"Playbook creado: '{nuevo_playbook.nombre}' (ID: {nuevo_playbook.id})")

    return nuevo_playbook


def listar_playbooks():
    """
    Devuelve todos los playbooks guardados en el sistema.

    Returns:
        Lista de objetos Playbook. Lista vacia si no hay ninguno.
    """

    playbooks = _obtener_todos_playbooks()
    logger.info(f"Se encontraron {len(playbooks)} playbooks.")
    return playbooks


def obtener_playbook(playbook_id):
    """
    Busca y devuelve un playbook por su ID.

    Args:
        playbook_id: ID del playbook que se quiere obtener.

    Returns:
        El objeto Playbook encontrado.

    Raises:
        PlaybookNotFoundError: Si no existe ningun playbook con ese ID.
    """

    playbooks = _obtener_todos_playbooks()

    # Recorremos todos los playbooks buscando el que tenga el ID exacto.
    # En cuanto lo encontramos, devolvemos directamente sin seguir
    # recorriendo el resto de la lista (mas eficiente que recorrer todo)
    for playbook in playbooks:
        if playbook.id == playbook_id:
            return playbook

    # Si llegamos aqui, recorrimos toda la lista sin encontrar el ID
    raise PlaybookNotFoundError(
        f"No se encontro ningun playbook con el ID '{playbook_id}'."
    )


def actualizar_playbook(playbook_id, nuevo_nombre=None, nuevo_tipo_ofensa=None):
    """
    Actualiza el nombre o tipo de ofensa de un playbook existente.

    Args:
        playbook_id: ID del playbook a modificar.
        nuevo_nombre: Nuevo nombre para el playbook (opcional).
        nuevo_tipo_ofensa: Nuevo tipo de ofensa (opcional).

    Returns:
        El objeto Playbook con los cambios aplicados.

    Raises:
        PlaybookNotFoundError: Si no existe el playbook.
        ValidationError: Si el nuevo nombre esta vacio.
    """

    playbooks = _obtener_todos_playbooks()
    playbook_a_actualizar = None

    # Buscar el playbook en la lista por su ID
    for playbook in playbooks:
        if playbook.id == playbook_id:
            playbook_a_actualizar = playbook
            break

    if playbook_a_actualizar is None:
        raise PlaybookNotFoundError(
            f"No se encontro el playbook con ID '{playbook_id}'."
        )

    # Actualizacion parcial: solo modificamos los campos que el
    # usuario realmente proporciono. Si nuevo_nombre es None, significa
    # que no se quiere cambiar el nombre, asi que lo dejamos como esta.
    if nuevo_nombre is not None:
        if not nuevo_nombre.strip():
            raise ValidationError("El nuevo nombre del playbook no puede estar vacio.")
        playbook_a_actualizar.nombre = nuevo_nombre.strip()

    if nuevo_tipo_ofensa is not None:
        playbook_a_actualizar.tipo_ofensa = nuevo_tipo_ofensa.strip()

    # Actualizar la fecha de modificacion para saber cuando fue
    # la ultima vez que se toco este playbook
    playbook_a_actualizar.actualizado_en = datetime.now().isoformat()

    # Guardar todos los playbooks (incluyendo el que acabamos de
    # modificar) de vuelta al archivo JSON
    _guardar_todos_playbooks(playbooks)

    logger.info(f"Playbook actualizado: ID '{playbook_id}'")

    return playbook_a_actualizar


def eliminar_playbook(playbook_id):
    """
    Elimina un playbook del sistema por su ID.

    Args:
        playbook_id: ID del playbook a eliminar.

    Raises:
        PlaybookNotFoundError: Si no existe el playbook con ese ID.
    """

    playbooks = _obtener_todos_playbooks()

    # Construimos una nueva lista con todos los playbooks EXCEPTO el
    # que queremos eliminar (list comprehension con filtro)
    playbooks_filtrados = [pb for pb in playbooks if pb.id != playbook_id]

    # Si la lista filtrada tiene el mismo tamano que la original,
    # significa que ningun playbook coincidio con el ID buscado,
    # es decir, el playbook no existia
    if len(playbooks_filtrados) == len(playbooks):
        raise PlaybookNotFoundError(
            f"No se encontro el playbook con ID '{playbook_id}'. "
            "Verifica el ID e intentalo de nuevo."
        )

    # Guardar la lista ya sin el playbook eliminado
    _guardar_todos_playbooks(playbooks_filtrados)

    logger.info(f"Playbook eliminado: ID '{playbook_id}'")


# --- Operaciones CRUD para Jugadas ---

def anadir_jugada(playbook_id, jugada):
    """
    Anade una jugada a un playbook existente.

    Args:
        playbook_id: ID del playbook donde se va a anadir la jugada.
        jugada: Objeto Play con los datos de la jugada.

    Returns:
        El objeto Play anadido.

    Raises:
        PlaybookNotFoundError: Si no existe el playbook.
        PlaybookFullError: Si el playbook ya tiene 50 jugadas.
        ValidationError: Si los datos de la jugada son incorrectos.
    """

    # Validar la jugada ANTES de tocar el archivo JSON. Asi, si la
    # jugada tiene datos invalidos, fallamos rapido sin haber hecho
    # ninguna operacion de lectura/escritura innecesaria.
    jugada.validar()

    playbooks = _obtener_todos_playbooks()
    playbook_objetivo = None

    # Buscar el playbook donde se anadira la jugada
    for playbook in playbooks:
        if playbook.id == playbook_id:
            playbook_objetivo = playbook
            break

    if playbook_objetivo is None:
        raise PlaybookNotFoundError(
            f"No se encontro el playbook con ID '{playbook_id}'."
        )

    # Anadir la jugada al playbook. Este metodo puede lanzar
    # PlaybookFullError si el playbook ya tiene 50 jugadas (limite
    # definido en la clase Playbook)
    playbook_objetivo.anadir_jugada(jugada)

    # Guardar todos los playbooks con la jugada ya anadida
    _guardar_todos_playbooks(playbooks)

    logger.info(
        f"Jugada '{jugada.nombre}' anadida al playbook '{playbook_objetivo.nombre}'"
    )

    return jugada


def actualizar_jugada(playbook_id, play_id, datos_nuevos):
    """
    Actualiza los datos de una jugada dentro de un playbook.

    Args:
        playbook_id: ID del playbook que contiene la jugada.
        play_id: ID de la jugada a modificar.
        datos_nuevos: Diccionario con los campos a actualizar.

    Returns:
        El objeto Play con los cambios aplicados.

    Raises:
        PlaybookNotFoundError: Si no existe el playbook.
        PlayNotFoundError: Si no existe la jugada.
    """

    playbooks = _obtener_todos_playbooks()
    playbook_objetivo = None

    # Buscar el playbook que contiene la jugada a actualizar
    for playbook in playbooks:
        if playbook.id == playbook_id:
            playbook_objetivo = playbook
            break

    if playbook_objetivo is None:
        raise PlaybookNotFoundError(
            f"No se encontro el playbook con ID '{playbook_id}'."
        )

    # Buscar la jugada dentro del playbook (este metodo ya lanza
    # PlayNotFoundError internamente si no la encuentra)
    jugada_objetivo = playbook_objetivo.obtener_jugada(play_id)

    # Actualizacion parcial: solo cambiamos los campos que el usuario
    # incluyo en el diccionario datos_nuevos. Si un campo no esta en
    # el diccionario, la jugada conserva su valor anterior para ese campo.
    if "nombre" in datos_nuevos:
        jugada_objetivo.nombre = datos_nuevos["nombre"]
    if "tipo" in datos_nuevos:
        jugada_objetivo.tipo = datos_nuevos["tipo"]
    if "formacion" in datos_nuevos:
        jugada_objetivo.formacion = datos_nuevos["formacion"]
    if "descripcion" in datos_nuevos:
        jugada_objetivo.descripcion = datos_nuevos["descripcion"]
    if "yardas" in datos_nuevos:
        jugada_objetivo.yardas = float(datos_nuevos["yardas"])
    if "tasa_exito" in datos_nuevos:
        jugada_objetivo.tasa_exito = float(datos_nuevos["tasa_exito"])
    if "down_distance" in datos_nuevos:
        jugada_objetivo.down_distance = datos_nuevos["down_distance"]
    if "hash_position" in datos_nuevos:
        jugada_objetivo.hash_position = datos_nuevos["hash_position"]
    if "etiquetas" in datos_nuevos:
        jugada_objetivo.etiquetas = datos_nuevos["etiquetas"]

    # Validar la jugada despues de aplicar los cambios, para asegurarnos
    # de que los nuevos valores tambien cumplen las reglas de negocio
    # (por ejemplo, que tasa_exito siga estando entre 0.0 y 1.0)
    jugada_objetivo.validar()

    # Actualizar la fecha de modificacion del playbook, ya que una de
    # sus jugadas cambio
    playbook_objetivo.actualizado_en = datetime.now().isoformat()

    # Guardar todos los playbooks con la jugada ya actualizada
    _guardar_todos_playbooks(playbooks)

    logger.info(f"Jugada '{play_id}' actualizada en playbook '{playbook_id}'")

    return jugada_objetivo


def eliminar_jugada(playbook_id, play_id):
    """
    Elimina una jugada de un playbook.

    Args:
        playbook_id: ID del playbook que contiene la jugada.
        play_id: ID de la jugada a eliminar.

    Raises:
        PlaybookNotFoundError: Si no existe el playbook.
        PlayNotFoundError: Si no existe la jugada.
    """

    playbooks = _obtener_todos_playbooks()
    playbook_objetivo = None

    # Buscar el playbook que contiene la jugada a eliminar
    for playbook in playbooks:
        if playbook.id == playbook_id:
            playbook_objetivo = playbook
            break

    if playbook_objetivo is None:
        raise PlaybookNotFoundError(
            f"No se encontro el playbook con ID '{playbook_id}'."
        )

    # Eliminar la jugada del playbook (este metodo ya lanza
    # PlayNotFoundError internamente si la jugada no existe)
    playbook_objetivo.eliminar_jugada(play_id)

    # Guardar todos los playbooks ya sin la jugada eliminada
    _guardar_todos_playbooks(playbooks)

    logger.info(f"Jugada '{play_id}' eliminada del playbook '{playbook_id}'")


def obtener_jugada(playbook_id, play_id):
    """
    Busca y devuelve una jugada especifica de un playbook.

    Args:
        playbook_id: ID del playbook donde buscar.
        play_id: ID de la jugada a obtener.

    Returns:
        El objeto Play encontrado.

    Raises:
        PlaybookNotFoundError: Si no existe el playbook.
        PlayNotFoundError: Si no existe la jugada.
    """

    # Reutilizamos obtener_playbook() para encontrar el playbook
    # (ya maneja el caso de que no exista) y luego delegamos en el
    # propio objeto Playbook para buscar la jugada dentro de el
    playbook = obtener_playbook(playbook_id)
    return playbook.obtener_jugada(play_id)
