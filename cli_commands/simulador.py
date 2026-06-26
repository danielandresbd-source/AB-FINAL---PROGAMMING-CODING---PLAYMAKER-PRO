"""Comandos CLI para generar datasets sinteticos."""

import simulator
from cli_commands.common import imprimir_error, imprimir_separador


def generar(args):
    """Genera un dataset sintetico de jugadas para testing."""

    try:
        cantidad = int(args.jugadas) if args.jugadas else 20
        tipo = args.tipo if args.tipo else None

        jugadas = simulator.generar_jugadas(cantidad=cantidad, tipo_ofensa=tipo)
        ruta_csv = simulator.guardar_dataset_csv(jugadas)

        imprimir_separador()
        print("  SIMULADOR - DATASET GENERADO")
        imprimir_separador()
        print(f"  Jugadas generadas: {len(jugadas)}")
        print(f"  Archivo CSV: {ruta_csv}")
        imprimir_separador()

    except Exception as error:
        imprimir_error(f"Error al generar datos sinteticos: {error}")
