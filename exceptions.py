# ============================================================
# exceptions.py
# Excepciones personalizadas del sistema PlayMaker Pro
# Proyecto: AB Final - Programming & Coding - MSMK 2025-2026
# ============================================================


class PlayMakerError(Exception):
    """Excepcion base de todos los errores del sistema PlayMaker Pro."""

    pass


class ValidationError(PlayMakerError):
    """
    Se lanza cuando los datos enviados por el usuario no son validos.

    Por ejemplo: un nombre vacio, yardas negativas, etc.
    """

    pass


class PlaybookNotFoundError(PlayMakerError):
    """
    Se lanza cuando se intenta acceder a un playbook que no existe.

    Por ejemplo: buscar un playbook con un ID que no esta guardado.
    """

    pass


class PlayNotFoundError(PlayMakerError):
    """
    Se lanza cuando se intenta acceder a una jugada que no existe.

    Por ejemplo: buscar una jugada dentro de un playbook y no encontrarla.
    """

    pass


class PlaybookFullError(PlayMakerError):
    """
    Se lanza cuando se intenta anadir una jugada a un playbook que esta lleno.

    El limite maximo de jugadas por playbook es de 50.
    """

    pass


class ArchivoCsvError(PlayMakerError):
    """
    Se lanza cuando hay un problema con el archivo CSV al importarlo.

    Por ejemplo: el archivo no existe, esta vacio, o tiene un formato incorrecto.
    """

    pass
