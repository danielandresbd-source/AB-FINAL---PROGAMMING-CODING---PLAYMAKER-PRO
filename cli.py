# ============================================================
# cli.py
# RF8: Punto de entrada principal de PlayMaker Pro
# Interfaz de linea de comandos (CLI) con argparse multi-nivel
# Proyecto: AB Final - Programming & Coding - MSMK 2025-2026
# ============================================================

import argparse
import logging
import sys

from cli_commands import analisis, jugadas, playbooks, reportes, simulador
from cli_commands.common import imprimir_error, imprimir_titulo

# Configurar el sistema de registro de eventos.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

# Desactivar los logs en la salida normal del CLI para no mezclarlos con la UI.
logging.disable(logging.CRITICAL)


def construir_parser():
    """
    Construye y configura el parser de argumentos de la CLI.

    Returns:
        Parser de argparse configurado con todos los subcomandos.
    """

    parser = argparse.ArgumentParser(
        prog="playmaker",
        description="PlayMaker Pro - Football Playbook Creator and Analyzer",
        epilog="Usa 'python cli.py <comando> --help' para ver ayuda de cada comando.",
    )

    subparsers = parser.add_subparsers(title="Modulos disponibles", dest="modulo")

    _configurar_playbooks(subparsers)
    _configurar_jugadas(subparsers)
    _configurar_analisis(subparsers)
    _configurar_reportes(subparsers)
    _configurar_simulador(subparsers)

    return parser


def _configurar_playbooks(subparsers):
    """Configura los subcomandos del modulo de playbooks."""

    parser_pb = subparsers.add_parser(
        "playbooks",
        help="Gestionar playbooks (crear, listar, eliminar, exportar)",
    )
    sub_pb = parser_pb.add_subparsers(dest="accion")

    sub_pb.add_parser("listar", help="Listar todos los playbooks guardados")

    p_crear_pb = sub_pb.add_parser("crear", help="Crear un nuevo playbook")
    p_crear_pb.add_argument("--nombre", required=True, help="Nombre del playbook")
    p_crear_pb.add_argument(
        "--tipo", help="Tipo de ofensa (spread, power, west_coast...)"
    )

    p_eliminar_pb = sub_pb.add_parser("eliminar", help="Eliminar un playbook por ID")
    p_eliminar_pb.add_argument("--id", required=True, help="ID del playbook a eliminar")

    p_exportar_pb = sub_pb.add_parser(
        "exportar", help="Exportar jugadas de un playbook a CSV"
    )
    p_exportar_pb.add_argument("--id", required=True, help="ID del playbook a exportar")
    p_exportar_pb.add_argument("--archivo", help="Nombre del archivo de salida")


def _configurar_jugadas(subparsers):
    """Configura los subcomandos del modulo de jugadas."""

    parser_j = subparsers.add_parser(
        "jugadas",
        help="Gestionar jugadas (anadir, listar, eliminar, importar)",
    )
    sub_j = parser_j.add_subparsers(dest="accion")

    p_listar_j = sub_j.add_parser("listar", help="Listar jugadas de un playbook")
    p_listar_j.add_argument(
        "--playbook-id",
        required=True,
        dest="playbook_id",
        help="ID del playbook",
    )

    p_anadir_j = sub_j.add_parser("anadir", help="Anadir una jugada a un playbook")
    p_anadir_j.add_argument("--playbook", required=True, help="ID del playbook")
    p_anadir_j.add_argument("--nombre", required=True, help="Nombre de la jugada")
    p_anadir_j.add_argument(
        "--tipo",
        required=True,
        choices=["run", "pass", "special_teams"],
        help="Tipo de jugada",
    )
    p_anadir_j.add_argument("--formacion", required=True, help="Formacion de la jugada")
    p_anadir_j.add_argument("--yardas", help="Yardas promedio de la jugada")
    p_anadir_j.add_argument("--descripcion", help="Descripcion de la jugada")
    p_anadir_j.add_argument(
        "--tasa-exito",
        dest="tasa_exito",
        help="Tasa de exito entre 0.0 y 1.0",
    )
    p_anadir_j.add_argument("--down", help="Situacion de down-and-distance")
    p_anadir_j.add_argument("--hash", help="Posicion en el campo (left/middle/right)")

    p_eliminar_j = sub_j.add_parser("eliminar", help="Eliminar una jugada")
    p_eliminar_j.add_argument("--playbook", required=True, help="ID del playbook")
    p_eliminar_j.add_argument("--id", required=True, help="ID de la jugada a eliminar")

    p_importar_j = sub_j.add_parser("importar", help="Importar jugadas desde un CSV")
    p_importar_j.add_argument("--archivo", required=True, help="Ruta del archivo CSV")
    p_importar_j.add_argument("--playbook", required=True, help="ID del playbook destino")


def _configurar_analisis(subparsers):
    """Configura los subcomandos del modulo de analisis."""

    parser_an = subparsers.add_parser(
        "analisis",
        help="Analizar jugadas (estadisticas, anomalias, prediccion, alertas)",
    )
    sub_an = parser_an.add_subparsers(dest="accion")

    p_stats = sub_an.add_parser("estadisticas", help="Ver estadisticas del playbook")
    p_stats.add_argument("--playbook", required=True, help="ID del playbook")

    p_anom = sub_an.add_parser("anomalias", help="Detectar jugadas con datos inusuales")
    p_anom.add_argument("--playbook", required=True, help="ID del playbook")

    p_pred = sub_an.add_parser("prediccion", help="Predecir efectividad de jugadas")
    p_pred.add_argument("--playbook", required=True, help="ID del playbook")
    p_pred.add_argument(
        "--ventana", default="5", help="Tamano de la ventana (default: 5)"
    )

    p_alert = sub_an.add_parser("alertas", help="Verificar conflictos en el playbook")
    p_alert.add_argument("--playbook", required=True, help="ID del playbook")


def _configurar_reportes(subparsers):
    """Configura los subcomandos del modulo de reportes."""

    parser_rep = subparsers.add_parser(
        "reportes",
        help="Generar reportes (CSV, grafico ASCII)",
    )
    sub_rep = parser_rep.add_subparsers(dest="accion")

    p_rep_csv = sub_rep.add_parser("csv", help="Exportar estadisticas a CSV")
    p_rep_csv.add_argument("--playbook", required=True, help="ID del playbook")


def _configurar_simulador(subparsers):
    """Configura los subcomandos del modulo simulador."""

    parser_sim = subparsers.add_parser(
        "simulador",
        help="Generar datos sinteticos de jugadas para testing",
    )
    sub_sim = parser_sim.add_subparsers(dest="accion")

    p_gen = sub_sim.add_parser("generar", help="Generar dataset sintetico de jugadas")
    p_gen.add_argument("--jugadas", default="20", help="Cantidad de jugadas a generar")
    p_gen.add_argument(
        "--tipo",
        choices=["run", "pass", "special_teams"],
        help="Tipo de jugadas a generar",
    )


# Tabla unica de enrutamiento: el parser se mantiene en cli.py y la logica
# de cada comando vive en su modulo correspondiente dentro de cli_commands/.
TABLA_COMANDOS = {
    ("playbooks", "listar"): playbooks.listar,
    ("playbooks", "crear"): playbooks.crear,
    ("playbooks", "eliminar"): playbooks.eliminar,
    ("playbooks", "exportar"): playbooks.exportar,
    ("jugadas", "listar"): jugadas.listar,
    ("jugadas", "anadir"): jugadas.anadir,
    ("jugadas", "eliminar"): jugadas.eliminar,
    ("jugadas", "importar"): jugadas.importar,
    ("analisis", "estadisticas"): analisis.estadisticas,
    ("analisis", "anomalias"): analisis.anomalias,
    ("analisis", "prediccion"): analisis.prediccion,
    ("analisis", "alertas"): analisis.alertas_playbook,
    ("reportes", "csv"): reportes.csv,
    ("simulador", "generar"): simulador.generar,
}


def main():
    """Funcion principal que inicia la aplicacion CLI."""

    imprimir_titulo()

    parser = construir_parser()
    args = parser.parse_args()

    if not args.modulo:
        parser.print_help()
        print("")
        print("Ejemplos rapidos:")
        print("  python cli.py playbooks listar")
        print("  python cli.py playbooks crear --nombre 'Red Zone'")
        print("  python cli.py simulador generar --jugadas 30")
        return

    accion = getattr(args, "accion", None)

    if not accion:
        parser.parse_args([args.modulo, "--help"])
        return

    clave = (args.modulo, accion)
    funcion_comando = TABLA_COMANDOS.get(clave)

    if funcion_comando:
        funcion_comando(args)
    else:
        imprimir_error(
            f"Comando no reconocido: '{args.modulo} {accion}'. "
            "Usa --help para ver los comandos disponibles."
        )


if __name__ == "__main__":
    main()
