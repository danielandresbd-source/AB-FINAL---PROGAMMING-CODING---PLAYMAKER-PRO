# ============================================================
# data_importer.py
# RF1: Importacion y validacion de jugadas desde archivos CSV
# Proyecto: AB Final - Programming & Coding - MSMK 2025-2026
# ============================================================

import csv
import logging
import os

from exceptions import ArchivoCsvError, ValidationError
from models import Formation, Play, PlayType

# Configuracion del sistema de registro de eventos
logger = logging.getLogger(__name__)

# Columnas que deben existir en el CSV para que sea valido
COLUMNAS_REQUERIDAS = ["nombre", "tipo", "formacion", "yardas"]

# Valores validos para las columnas de tipo y formacion
TIPOS_VALIDOS = [t.value for t in PlayType]
FORMACIONES_VALIDAS = [f.value for f in Formation]


def cargar_csv(ruta_archivo):
    """
    Carga jugadas desde un archivo CSV y devuelve una lista de objetos Play.

    El archivo CSV debe tener al menos las columnas:
    nombre, tipo, formacion, yardas

    Columnas opcionales: descripcion, tasa_exito, down_distance,
                         hash_position, etiquetas

    Args:
        ruta_archivo: Ruta al archivo CSV que se va a importar.

    Returns:
        Lista de objetos Play con las jugadas cargadas correctamente.

    Raises:
        FileNotFoundError: Si el archivo no existe en la ruta indicada.
        ArchivoCsvError: Si el archivo no tiene el formato correcto.
    """

    # Verificar que el archivo existe
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(
            f"No se encontro el archivo: '{ruta_archivo}'. "
            "Verifica que la ruta sea correcta."
        )

    jugadas_cargadas = []
    jugadas_con_error = 0

    try:
        with open(ruta_archivo, encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)

            # Verificar que el archivo tiene las columnas necesarias
            if lector.fieldnames is None:
                return []

            _verificar_columnas(lector.fieldnames, ruta_archivo)

            # Procesar cada fila del CSV
            for numero_fila, fila in enumerate(lector, start=2):
                try:
                    jugada = _procesar_fila(fila, numero_fila)
                    jugadas_cargadas.append(jugada)
                except ValidationError as error:
                    # Si una fila tiene error, se omite pero se continua
                    logger.warning(f"Fila {numero_fila} omitida - {error}")
                    jugadas_con_error += 1

    except UnicodeDecodeError:
        raise ArchivoCsvError(
            f"El archivo '{ruta_archivo}' no esta en formato UTF-8. "
            "Guarda el archivo con codificacion UTF-8 e intentalo de nuevo."
        )

    # Registro del resultado de la importacion
    logger.info(
        f"Importacion completada: {len(jugadas_cargadas)} jugadas cargadas, "
        f"{jugadas_con_error} filas omitidas por errores."
    )

    return jugadas_cargadas


def _verificar_columnas(columnas_encontradas, ruta_archivo):
    """
    Verifica que el CSV tiene todas las columnas requeridas.

    Args:
        columnas_encontradas: Lista de columnas que tiene el archivo.
        ruta_archivo: Nombre del archivo (para el mensaje de error).

    Raises:
        ArchivoCsvError: Si falta alguna columna requerida.
    """

    # Convertir a minusculas para comparar sin importar mayusculas
    columnas_lower = [col.lower().strip() for col in columnas_encontradas]

    columnas_faltantes = []
    for columna in COLUMNAS_REQUERIDAS:
        if columna not in columnas_lower:
            columnas_faltantes.append(columna)

    if columnas_faltantes:
        raise ArchivoCsvError(
            f"El archivo '{ruta_archivo}' no tiene las columnas requeridas. "
            f"Columnas faltantes: {', '.join(columnas_faltantes)}. "
            f"Columnas requeridas: {', '.join(COLUMNAS_REQUERIDAS)}"
        )


def _procesar_fila(fila, numero_fila):
    """
    Procesa una fila del CSV y la convierte en un objeto Play.

    Args:
        fila: Diccionario con los datos de la fila del CSV.
        numero_fila: Numero de la fila en el archivo (para mensajes de error).

    Returns:
        Objeto Play con los datos de la fila.

    Raises:
        ValidationError: Si los datos de la fila son incorrectos.
    """

    # Limpiar espacios en blanco de todos los valores
    fila_limpia = {k.lower().strip(): str(v).strip() for k, v in fila.items()}

    # Validar y obtener el nombre (campo obligatorio)
    nombre = fila_limpia.get("nombre", "")
    if not nombre:
        raise ValidationError(
            f"Fila {numero_fila}: el campo 'nombre' esta vacio."
        )

    # Validar y obtener las yardas (campo obligatorio)
    try:
        yardas = float(fila_limpia.get("yardas", "0"))
    except ValueError:
        raise ValidationError(
            f"Fila {numero_fila}: las yardas '{fila_limpia.get('yardas')}' "
            "no son un numero valido."
        )

    # Validar el tipo de jugada
    tipo = fila_limpia.get("tipo", "run")
    if tipo not in TIPOS_VALIDOS:
        raise ValidationError(
            f"Fila {numero_fila}: el tipo '{tipo}' no es valido. "
            f"Opciones permitidas: {TIPOS_VALIDOS}"
        )

    # Validar la formacion
    formacion = fila_limpia.get("formacion", "SHOTGUN").upper()
    if formacion not in FORMACIONES_VALIDAS:
        raise ValidationError(
            f"Fila {numero_fila}: la formacion '{formacion}' no es valida. "
            f"Opciones permitidas: {FORMACIONES_VALIDAS}"
        )

    # Obtener tasa de exito (campo opcional)
    tasa_exito = 0.0
    valor_tasa = fila_limpia.get("tasa_exito", "")
    if valor_tasa:
        try:
            tasa_exito = float(valor_tasa)
            if tasa_exito < 0.0 or tasa_exito > 1.0:
                raise ValidationError(
                    f"Fila {numero_fila}: la tasa de exito '{tasa_exito}' "
                    "debe estar entre 0.0 y 1.0."
                )
        except ValueError:
            raise ValidationError(
                f"Fila {numero_fila}: la tasa de exito '{valor_tasa}' "
                "no es un numero valido."
            )

    # Obtener campos opcionales con valores por defecto
    descripcion = fila_limpia.get("descripcion", "")
    down_distance = fila_limpia.get("down_distance", "1st&10")
    hash_position = fila_limpia.get("hash_position", "middle")

    # Procesar etiquetas si existen (separadas por punto y coma)
    etiquetas_texto = fila_limpia.get("etiquetas", "")
    etiquetas = []
    if etiquetas_texto:
        etiquetas = [e.strip() for e in etiquetas_texto.split(";") if e.strip()]

    # Crear y devolver el objeto Play
    jugada = Play(
        nombre=nombre,
        tipo=tipo,
        formacion=formacion,
        descripcion=descripcion,
        yardas=yardas,
        tasa_exito=tasa_exito,
        down_distance=down_distance,
        hash_position=hash_position,
        etiquetas=etiquetas,
    )

    return jugada


def sanitizar_datos(jugadas):
    """
    Limpia y valida una lista de jugadas ya importadas.

    Elimina jugadas con datos claramente incorrectos y registra las omitidas.

    Args:
        jugadas: Lista de objetos Play a limpiar.

    Returns:
        Lista de jugadas validas.
    """

    jugadas_validas = []

    for jugada in jugadas:
        try:
            jugada.validar()
            jugadas_validas.append(jugada)
        except ValidationError as error:
            logger.warning(
                f"Jugada '{jugada.nombre}' eliminada durante sanitizacion: {error}"
            )

    logger.info(
        f"Sanitizacion completada: {len(jugadas_validas)} jugadas validas de {len(jugadas)} totales."
    )

    return jugadas_validas
