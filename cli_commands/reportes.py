"""Comandos CLI para generar reportes."""

import analyzer
import data_manager
import reporter
from cli_commands.common import imprimir_error, imprimir_exito
from exceptions import PlaybookNotFoundError


def csv(args):
    """Exporta las estadisticas de un playbook a un archivo CSV."""

    try:
        playbook = data_manager.obtener_playbook(args.playbook)

        if not playbook.jugadas:
            imprimir_error("El playbook no tiene jugadas para exportar.")
            return

        estadisticas = analyzer.calcular_estadisticas(playbook.jugadas)
        ruta = reporter.exportar_estadisticas_csv(estadisticas)

        imprimir_exito(f"Estadisticas exportadas a: {ruta}")

    except PlaybookNotFoundError as error:
        imprimir_error(str(error))
    except Exception as error:
        imprimir_error(f"Error al exportar: {error}")
