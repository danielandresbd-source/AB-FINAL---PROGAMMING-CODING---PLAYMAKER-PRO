# ============================================================
# models.py
# Clases de datos del dominio: Play, Playbook, Formation, PlayType
# Proyecto: AB Final - Programming & Coding
# ============================================================

import uuid
from datetime import datetime
from enum import Enum

from exceptions import ValidationError


# --- Enumeraciones del dominio de futbol americano ---

class Formation(str, Enum):
    """Formaciones ofensivas y defensivas validas en el sistema."""

    # Formaciones ofensivas
    SHOTGUN = "SHOTGUN"
    I_FORMATION = "I_FORMATION"
    SINGLEBACK = "SINGLEBACK"
    GUN_TRIPS = "GUN_TRIPS"
    EMPTY_SET = "EMPTY_SET"
    PISTOL = "PISTOL"
    WILDCAT = "WILDCAT"

    # Formaciones defensivas
    FOUR_THREE = "FOUR_THREE"
    THREE_FOUR = "THREE_FOUR"
    NICKEL = "NICKEL"
    DIME = "DIME"


class PlayType(str, Enum):
    """Tipos de jugada disponibles en el sistema."""

    CORRIDA = "run"
    PASE = "pass"
    ESPECIALES = "special_teams"


# --- Clases de dominio principales ---

class Play:
    """
    Representa una jugada individual de futbol americano.

    Atributos:
        id: Identificador unico de la jugada (generado automaticamente)
        nombre: Nombre de la jugada (ej: "HB Dive Left")
        tipo: Tipo de jugada (run, pass, special_teams)
        formacion: Formacion desde la que se ejecuta la jugada
        descripcion: Descripcion detallada de la jugada
        yardas: Yardas promedio que gana esta jugada
        tasa_exito: Porcentaje de exito entre 0.0 y 1.0
        down_distance: Situacion de down-and-distance (ej: "2nd&short")
        hash_position: Posicion en el campo (left, middle, right)
        etiquetas: Lista de etiquetas para categorizar la jugada
        creada_en: Fecha y hora en que se creo la jugada
    """

    # Situaciones de down-and-distance validas
    DOWNS_VALIDOS = [
        "1st&10", "1st&goal",
        "2nd&long", "2nd&medium", "2nd&short", "2nd&goal",
        "3rd&long", "3rd&medium", "3rd&short", "3rd&goal",
        "4th&short", "4th&goal", "4th&long",
    ]

    # Posiciones en el campo validas
    POSICIONES_HASH_VALIDAS = ["left", "middle", "right"]

    def __init__(
        self,
        nombre,
        tipo,
        formacion,
        descripcion="",
        yardas=0.0,
        tasa_exito=0.0,
        down_distance="1st&10",
        hash_position="middle",
        etiquetas=None,
        play_id=None,
        creada_en=None,
    ):
        """Inicializa una nueva jugada y valida sus datos."""

        # Si no se pasa un ID, se genera uno automaticamente
        self.id = play_id if play_id else "play_" + str(uuid.uuid4())[:8]

        self.nombre = nombre
        self.tipo = tipo
        self.formacion = formacion
        self.descripcion = descripcion
        self.yardas = yardas
        self.tasa_exito = tasa_exito
        self.down_distance = down_distance
        self.hash_position = hash_position
        self.etiquetas = etiquetas if etiquetas else []
        self.creada_en = creada_en if creada_en else datetime.now().isoformat()

    def validar(self):
        """
        Valida que todos los datos de la jugada son correctos.

        Lanza ValidationError si hay algun dato invalido.
        """

        # El nombre no puede estar vacio
        if not self.nombre or not self.nombre.strip():
            raise ValidationError("El nombre de la jugada no puede estar vacio.")

        # Las yardas no pueden ser un numero imposible
        if self.yardas < -99 or self.yardas > 999:
            raise ValidationError(
                f"Las yardas '{self.yardas}' estan fuera del rango permitido (-99 a 999)."
            )

        # La tasa de exito debe estar entre 0.0 y 1.0
        if self.tasa_exito < 0.0 or self.tasa_exito > 1.0:
            raise ValidationError(
                f"La tasa de exito '{self.tasa_exito}' debe estar entre 0.0 y 1.0."
            )

        # El tipo debe ser uno de los permitidos
        tipos_validos = [t.value for t in PlayType]
        if self.tipo not in tipos_validos:
            raise ValidationError(
                f"El tipo '{self.tipo}' no es valido. Opciones: {tipos_validos}"
            )

        # La formacion debe ser una de las permitidas
        formaciones_validas = [f.value for f in Formation]
        if self.formacion not in formaciones_validas:
            raise ValidationError(
                f"La formacion '{self.formacion}' no es valida. Opciones: {formaciones_validas}"
            )

        return True

    def es_anomala(self):
        """
        Comprueba si la jugada tiene datos inusuales.

        Devuelve True si la jugada parece tener datos incorrectos.
        Este metodo hace una comprobacion basica. El analisis completo
        se hace en analyzer.py con el contexto del dataset completo.
        """

        # Tasa de exito imposible
        if self.tasa_exito < 0.0 or self.tasa_exito > 1.0:
            return True

        # Down-distance desconocido
        if self.down_distance not in self.DOWNS_VALIDOS:
            return True

        # Hash position desconocida
        if self.hash_position not in self.POSICIONES_HASH_VALIDAS:
            return True

        return False

    def a_diccionario(self):
        """Convierte la jugada a un diccionario para guardarlo en JSON."""

        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "formacion": self.formacion,
            "descripcion": self.descripcion,
            "yardas": self.yardas,
            "tasa_exito": self.tasa_exito,
            "down_distance": self.down_distance,
            "hash_position": self.hash_position,
            "etiquetas": self.etiquetas,
            "creada_en": self.creada_en,
        }

    @classmethod
    def desde_diccionario(cls, datos):
        """Crea un objeto Play a partir de un diccionario (leido del JSON)."""

        return cls(
            play_id=datos.get("id"),
            nombre=datos.get("nombre", ""),
            tipo=datos.get("tipo", "run"),
            formacion=datos.get("formacion", "SHOTGUN"),
            descripcion=datos.get("descripcion", ""),
            yardas=float(datos.get("yardas", 0.0)),
            tasa_exito=float(datos.get("tasa_exito", 0.0)),
            down_distance=datos.get("down_distance", "1st&10"),
            hash_position=datos.get("hash_position", "middle"),
            etiquetas=datos.get("etiquetas", []),
            creada_en=datos.get("creada_en"),
        )

    def __repr__(self):
        """Representacion de la jugada como texto para depuracion."""
        return f"Play(id={self.id}, nombre={self.nombre}, tipo={self.tipo})"


class Playbook:
    """
    Representa un playbook (libro de jugadas) del equipo.

    Un playbook agrupa varias jugadas relacionadas. Por ejemplo:
    'Red Zone Offense' puede tener jugadas de corrida y pase
    especificamente disenadas para la zona roja del campo.

    Atributos:
        id: Identificador unico del playbook
        nombre: Nombre del playbook
        tipo_ofensa: Estilo de juego (spread, power, west_coast, etc.)
        jugadas: Lista de objetos Play que contiene este playbook
        creado_en: Fecha y hora de creacion
        actualizado_en: Fecha y hora de la ultima modificacion
    """

    # Limite maximo de jugadas por playbook (segun RF6)
    LIMITE_JUGADAS = 50

    def __init__(
        self,
        nombre,
        tipo_ofensa="spread",
        playbook_id=None,
        creado_en=None,
        actualizado_en=None,
    ):
        """Inicializa un nuevo playbook."""

        # Si no se pasa un ID, se genera uno automaticamente
        self.id = playbook_id if playbook_id else "pb_" + str(uuid.uuid4())[:8]

        self.nombre = nombre
        self.tipo_ofensa = tipo_ofensa
        self.jugadas = []
        self.creado_en = creado_en if creado_en else datetime.now().isoformat()
        self.actualizado_en = actualizado_en if actualizado_en else datetime.now().isoformat()

    def anadir_jugada(self, jugada):
        """
        Anade una jugada al playbook.

        Lanza PlaybookFullError si ya hay 50 jugadas.
        """

        # Importacion local para evitar importaciones circulares
        from exceptions import PlaybookFullError

        if len(self.jugadas) >= self.LIMITE_JUGADAS:
            raise PlaybookFullError(
                f"El playbook '{self.nombre}' ya tiene {self.LIMITE_JUGADAS} jugadas. "
                "No se pueden agregar mas."
            )

        self.jugadas.append(jugada)
        self.actualizado_en = datetime.now().isoformat()

    def eliminar_jugada(self, play_id):
        """
        Elimina una jugada del playbook por su ID.

        Lanza PlayNotFoundError si no se encuentra la jugada.
        """

        from exceptions import PlayNotFoundError

        jugada_encontrada = None
        for jugada in self.jugadas:
            if jugada.id == play_id:
                jugada_encontrada = jugada
                break

        if jugada_encontrada is None:
            raise PlayNotFoundError(
                f"No se encontro la jugada con ID '{play_id}' en el playbook '{self.nombre}'."
            )

        self.jugadas.remove(jugada_encontrada)
        self.actualizado_en = datetime.now().isoformat()

    def obtener_jugada(self, play_id):
        """
        Busca y devuelve una jugada del playbook por su ID.

        Lanza PlayNotFoundError si no se encuentra.
        """

        from exceptions import PlayNotFoundError

        for jugada in self.jugadas:
            if jugada.id == play_id:
                return jugada

        raise PlayNotFoundError(
            f"No se encontro la jugada con ID '{play_id}' en el playbook '{self.nombre}'."
        )

    def a_diccionario(self):
        """Convierte el playbook a un diccionario para guardarlo en JSON."""

        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo_ofensa": self.tipo_ofensa,
            "creado_en": self.creado_en,
            "actualizado_en": self.actualizado_en,
            "jugadas": [jugada.a_diccionario() for jugada in self.jugadas],
        }

    @classmethod
    def desde_diccionario(cls, datos):
        """Crea un objeto Playbook a partir de un diccionario (leido del JSON)."""

        playbook = cls(
            playbook_id=datos.get("id"),
            nombre=datos.get("nombre", "Sin nombre"),
            tipo_ofensa=datos.get("tipo_ofensa", "spread"),
            creado_en=datos.get("creado_en"),
            actualizado_en=datos.get("actualizado_en"),
        )

        # Cargar las jugadas del playbook
        for datos_jugada in datos.get("jugadas", []):
            jugada = Play.desde_diccionario(datos_jugada)
            playbook.jugadas.append(jugada)

        return playbook

    def __repr__(self):
        """Representacion del playbook como texto para depuracion."""
        return (
            f"Playbook(id={self.id}, nombre={self.nombre}, "
            f"jugadas={len(self.jugadas)})"
        )
