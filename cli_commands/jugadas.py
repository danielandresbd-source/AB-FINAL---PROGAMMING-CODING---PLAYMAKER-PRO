"""Comandos CLI para gestionar jugadas."""

import data_importer
import data_manager
from cli_commands.common import imprimir_error, imprimir_exito, imprimir_separador
from exceptions import (
    ArchivoCsvError,
    PlaybookFullError,
    PlaybookNotFoundError,
    PlayNotFoundError,
    ValidationError,
)
from models import Play


def listar(args):
    """Lista todas las jugadas de un playbook especifico."""

    try:
        playbook = data_manager.obtener_playbook(args.playbook_id)
    except PlaybookNotFoundError as error:
        imprimir_error(str(error))
        return

    imprimir_separador()
    print(f"  JUGADAS DE: {playbook.nombre}")
    imprimir_separador()

    if not playbook.jugadas:
        print("  Este playbook no tiene jugadas todavia.")
        print(
            f"  Usa: python cli.py jugadas anadir --playbook {args.playbook_id} "
            "--nombre 'Mi Jugada' --tipo run --formacion SHOTGUN --yardas 5"
        )
    else:
        for jugada in playbook.jugadas:
            print(f"  ID: {jugada.id}")
            print(f"  Nombre: {jugada.nombre}")
            print(f"  Tipo: {jugada.tipo}  |  Formacion: {jugada.formacion}")
            print(f"  Yardas: {jugada.yardas}  |  Exito: {int(jugada.tasa_exito * 100)}%")
            print(f"  Situacion: {jugada.down_distance}")
            print("")

    imprimir_separador()


def anadir(args):
    """Anade una nueva jugada a un playbook existente."""

    try:
        nueva_jugada = Play(
            nombre=args.nombre,
            tipo=args.tipo,
            formacion=args.formacion,
            descripcion=args.descripcion if args.descripcion else "",
            yardas=float(args.yardas) if args.yardas else 0.0,
            tasa_exito=float(args.tasa_exito) if args.tasa_exito else 0.0,
            down_distance=args.down if args.down else "1st&10",
            hash_position=args.hash if args.hash else "middle",
        )

        jugada_guardada = data_manager.anadir_jugada(
            playbook_id=args.playbook,
            jugada=nueva_jugada,
        )

        imprimir_exito(
            f"Jugada '{jugada_guardada.nombre}' anadida correctamente. "
            f"ID: {jugada_guardada.id}"
        )

    except (ValidationError, PlaybookNotFoundError, PlaybookFullError) as error:
        imprimir_error(str(error))
    except Exception as error:
        imprimir_error(f"Error inesperado: {error}")


def eliminar(args):
    """Elimina una jugada de un playbook."""

    try:
        data_manager.eliminar_jugada(
            playbook_id=args.playbook,
            play_id=args.id,
        )
        imprimir_exito(f"Jugada '{args.id}' eliminada correctamente.")
    except (PlaybookNotFoundError, PlayNotFoundError) as error:
        imprimir_error(str(error))
    except Exception as error:
        imprimir_error(f"Error inesperado: {error}")


def importar(args):
    """Importa jugadas desde un archivo CSV a un playbook."""

    try:
        jugadas = data_importer.cargar_csv(args.archivo)

        if not jugadas:
            imprimir_error("El archivo CSV esta vacio o no tiene jugadas validas.")
            return

        playbook = data_manager.obtener_playbook(args.playbook)
        jugadas_anadidas = 0

        for jugada in jugadas:
            try:
                data_manager.anadir_jugada(
                    playbook_id=args.playbook,
                    jugada=jugada,
                )
                jugadas_anadidas += 1
            except PlaybookFullError:
                print(
                    f"[AVISO] El playbook esta lleno. "
                    f"Se anadieron {jugadas_anadidas} de {len(jugadas)} jugadas."
                )
                break
            except Exception:
                continue

        imprimir_exito(
            f"Se importaron {jugadas_anadidas} jugadas al playbook '{playbook.nombre}'."
        )

    except FileNotFoundError as error:
        imprimir_error(str(error))
    except (ArchivoCsvError, PlaybookNotFoundError) as error:
        imprimir_error(str(error))
    except Exception as error:
        imprimir_error(f"Error inesperado: {error}")
