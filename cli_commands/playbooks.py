"""Comandos CLI para gestionar playbooks."""

import data_manager
import reporter
from cli_commands.common import imprimir_error, imprimir_exito, imprimir_separador
from exceptions import PlaybookNotFoundError, ValidationError


def listar(args):
    """Muestra en consola todos los playbooks guardados."""

    try:
        playbooks = data_manager.listar_playbooks()
    except Exception as error:
        imprimir_error(f"No se pudieron cargar los playbooks: {error}")
        return

    imprimir_separador()
    print("  PLAYBOOKS GUARDADOS")
    imprimir_separador()

    if not playbooks:
        print("  No hay playbooks guardados todavia.")
        print("  Usa: python cli.py playbooks crear --nombre 'Mi Playbook'")
    else:
        for pb in playbooks:
            print(f"  ID: {pb.id}")
            print(f"  Nombre: {pb.nombre}")
            print(f"  Tipo de ofensa: {pb.tipo_ofensa}")
            print(f"  Jugadas: {len(pb.jugadas)}")
            print(f"  Creado: {pb.creado_en[:10]}")
            print("")

    imprimir_separador()


def crear(args):
    """Crea un nuevo playbook con el nombre y tipo de ofensa indicados."""

    try:
        nuevo_pb = data_manager.crear_playbook(
            nombre=args.nombre,
            tipo_ofensa=args.tipo if args.tipo else "spread",
        )
        imprimir_exito(
            f"Playbook '{nuevo_pb.nombre}' creado correctamente. "
            f"ID: {nuevo_pb.id}"
        )
    except ValidationError as error:
        imprimir_error(str(error))
    except Exception as error:
        imprimir_error(f"Error inesperado al crear playbook: {error}")


def eliminar(args):
    """Elimina un playbook por su ID."""

    try:
        data_manager.eliminar_playbook(args.id)
        imprimir_exito(f"Playbook con ID '{args.id}' eliminado correctamente.")
    except PlaybookNotFoundError as error:
        imprimir_error(str(error))
    except Exception as error:
        imprimir_error(f"Error inesperado: {error}")


def exportar(args):
    """Exporta todas las jugadas de un playbook a un archivo CSV."""

    try:
        playbook = data_manager.obtener_playbook(args.id)

        if not playbook.jugadas:
            imprimir_error(
                f"El playbook '{playbook.nombre}' no tiene jugadas para exportar."
            )
            return

        ruta_exportada = reporter.exportar_csv(
            jugadas=playbook.jugadas,
            nombre_archivo=args.archivo if args.archivo else None,
        )
        imprimir_exito(f"Playbook exportado a: {ruta_exportada}")

    except PlaybookNotFoundError as error:
        imprimir_error(str(error))
    except Exception as error:
        imprimir_error(f"Error al exportar: {error}")
