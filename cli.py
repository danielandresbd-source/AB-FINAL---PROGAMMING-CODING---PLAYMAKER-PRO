# ============================================================
# cli.py
# RF8: Punto de entrada principal de PlayMaker Pro
# Interfaz de linea de comandos (CLI) con argparse multi-nivel
# Proyecto: AB Final - Programming & Coding - MSMK 2025-2026
# ============================================================

# Importaciones de la libreria estandar de Python
import argparse
import logging
import sys

# Importaciones de los modulos del proyecto
import alerts
import analyzer
import data_importer
import data_manager
import reporter
import simulator
from exceptions import (
    ArchivoCsvError,
    PlaybookFullError,
    PlaybookNotFoundError,
    PlayNotFoundError,
    ValidationError,
)
from models import Play

# Configurar el sistema de registro de eventos
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

# Desactivar los logs en la salida normal del CLI para no mezclarlos con la UI
logging.disable(logging.CRITICAL)


# --- Funciones de presentacion visual ---

def _imprimir_separador():
    """Imprime una linea separadora en consola."""
    print("=" * 55)


def _imprimir_titulo():
    """Muestra el titulo de la aplicacion al iniciarla."""
    _imprimir_separador()
    print("  PLAYMAKER PRO")
    print("  Football Playbook Creator and Analyzer")
    print("  Madrid Bulldogs - MSMK University 2025-2026")
    _imprimir_separador()
    print("")


def _imprimir_error(mensaje):
    """Muestra un mensaje de error de forma clara."""
    print(f"\n[ERROR] {mensaje}\n")


def _imprimir_exito(mensaje):
    """Muestra un mensaje de exito."""
    print(f"\n[OK] {mensaje}\n")


# --- Funciones del menu de Playbooks ---

def cmd_playbooks_listar(args):
    """Muestra en consola todos los playbooks guardados."""

    try:
        playbooks = data_manager.listar_playbooks()
    except Exception as error:
        _imprimir_error(f"No se pudieron cargar los playbooks: {error}")
        return

    _imprimir_separador()
    print("  PLAYBOOKS GUARDADOS")
    _imprimir_separador()

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

    _imprimir_separador()


def cmd_playbooks_crear(args):
    """Crea un nuevo playbook con el nombre y tipo de ofensa indicados."""

    try:
        nuevo_pb = data_manager.crear_playbook(
            nombre=args.nombre,
            tipo_ofensa=args.tipo if args.tipo else "spread",
        )
        _imprimir_exito(
            f"Playbook '{nuevo_pb.nombre}' creado correctamente. "
            f"ID: {nuevo_pb.id}"
        )
    except ValidationError as error:
        _imprimir_error(str(error))
    except Exception as error:
        _imprimir_error(f"Error inesperado al crear playbook: {error}")


def cmd_playbooks_eliminar(args):
    """Elimina un playbook por su ID."""

    try:
        data_manager.eliminar_playbook(args.id)
        _imprimir_exito(f"Playbook con ID '{args.id}' eliminado correctamente.")
    except PlaybookNotFoundError as error:
        _imprimir_error(str(error))
    except Exception as error:
        _imprimir_error(f"Error inesperado: {error}")


def cmd_playbooks_exportar(args):
    """Exporta todas las jugadas de un playbook a un archivo CSV."""

    try:
        playbook = data_manager.obtener_playbook(args.id)

        if not playbook.jugadas:
            _imprimir_error(
                f"El playbook '{playbook.nombre}' no tiene jugadas para exportar."
            )
            return

        ruta_exportada = reporter.exportar_csv(
            jugadas=playbook.jugadas,
            nombre_archivo=args.archivo if args.archivo else None,
        )
        _imprimir_exito(f"Playbook exportado a: {ruta_exportada}")

    except PlaybookNotFoundError as error:
        _imprimir_error(str(error))
    except Exception as error:
        _imprimir_error(f"Error al exportar: {error}")


# --- Funciones del menu de Jugadas ---

def cmd_jugadas_listar(args):
    """Lista todas las jugadas de un playbook especifico."""

    try:
        playbook = data_manager.obtener_playbook(args.playbook_id)
    except PlaybookNotFoundError as error:
        _imprimir_error(str(error))
        return

    _imprimir_separador()
    print(f"  JUGADAS DE: {playbook.nombre}")
    _imprimir_separador()

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

    _imprimir_separador()


def cmd_jugadas_anadir(args):
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

        _imprimir_exito(
            f"Jugada '{jugada_guardada.nombre}' anadida correctamente. "
            f"ID: {jugada_guardada.id}"
        )

    except (ValidationError, PlaybookNotFoundError, PlaybookFullError) as error:
        _imprimir_error(str(error))
    except Exception as error:
        _imprimir_error(f"Error inesperado: {error}")


def cmd_jugadas_eliminar(args):
    """Elimina una jugada de un playbook."""

    try:
        data_manager.eliminar_jugada(
            playbook_id=args.playbook,
            play_id=args.id,
        )
        _imprimir_exito(f"Jugada '{args.id}' eliminada correctamente.")
    except (PlaybookNotFoundError, PlayNotFoundError) as error:
        _imprimir_error(str(error))
    except Exception as error:
        _imprimir_error(f"Error inesperado: {error}")


def cmd_jugadas_importar(args):
    """Importa jugadas desde un archivo CSV a un playbook."""

    try:
        jugadas = data_importer.cargar_csv(args.archivo)

        if not jugadas:
            _imprimir_error("El archivo CSV esta vacio o no tiene jugadas validas.")
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

        _imprimir_exito(
            f"Se importaron {jugadas_anadidas} jugadas al playbook '{playbook.nombre}'."
        )

    except FileNotFoundError as error:
        _imprimir_error(str(error))
    except (ArchivoCsvError, PlaybookNotFoundError) as error:
        _imprimir_error(str(error))
    except Exception as error:
        _imprimir_error(f"Error inesperado: {error}")


# --- Funciones del menu de Analisis ---

def cmd_analisis_estadisticas(args):
    """Muestra estadisticas descriptivas de las jugadas de un playbook."""

    try:
        playbook = data_manager.obtener_playbook(args.playbook)

        if not playbook.jugadas:
            _imprimir_error(
                f"El playbook '{playbook.nombre}' no tiene jugadas para analizar."
            )
            return

        estadisticas = analyzer.calcular_estadisticas(playbook.jugadas)

        _imprimir_separador()
        print(f"  ESTADISTICAS: {playbook.nombre}")
        _imprimir_separador()
        print(f"  Total de jugadas: {estadisticas['total_jugadas']}")
        print(f"  Formacion mas usada: {estadisticas['formacion_mas_usada']}")
        print(f"  Yardas promedio: {estadisticas['yardas_promedio']}")
        print(f"  Yardas minimas: {estadisticas['yardas_minimas']}")
        print(f"  Yardas maximas: {estadisticas['yardas_maximas']}")
        print("")

        # Mostrar el grafico ASCII
        reporter.mostrar_grafico_ascii(estadisticas)

        # Mostrar top 5 jugadas
        reporter.mostrar_top_jugadas(estadisticas)

    except PlaybookNotFoundError as error:
        _imprimir_error(str(error))
    except Exception as error:
        _imprimir_error(f"Error inesperado: {error}")


def cmd_analisis_anomalias(args):
    """Detecta jugadas con datos inusuales en un playbook."""

    try:
        playbook = data_manager.obtener_playbook(args.playbook)

        if not playbook.jugadas:
            _imprimir_error("El playbook no tiene jugadas para analizar.")
            return

        anomalias = analyzer.detectar_anomalias(playbook.jugadas)

        _imprimir_separador()
        print(f"  ANOMALIAS EN: {playbook.nombre}")
        _imprimir_separador()

        if not anomalias:
            print("  No se encontraron anomalias. Todos los datos parecen correctos.")
        else:
            print(f"  Se encontraron {len(anomalias)} jugadas con datos inusuales:\n")
            for item in anomalias:
                jugada = item["jugada"]
                razones = item["razones"]
                print(f"  Jugada: {jugada.nombre} (ID: {jugada.id})")
                for razon in razones:
                    print(f"    - {razon}")
                print("")

        _imprimir_separador()

    except PlaybookNotFoundError as error:
        _imprimir_error(str(error))
    except Exception as error:
        _imprimir_error(f"Error inesperado: {error}")


def cmd_analisis_prediccion(args):
    """Predice la efectividad de las proximas jugadas usando media movil."""

    try:
        playbook = data_manager.obtener_playbook(args.playbook)

        ventana = int(args.ventana) if args.ventana else 5

        resultado = analyzer.predecir_efectividad(playbook.jugadas, ventana=ventana)

        _imprimir_separador()
        print(f"  PREDICCION DE EFECTIVIDAD: {playbook.nombre}")
        _imprimir_separador()
        print(f"  Prediccion: {int(resultado['prediccion'] * 100)}% de exito")
        print(f"  Tendencia actual: {resultado['tendencia']}")
        print(f"  Ventana de calculo: {resultado['ventana_usada']} jugadas")
        print(f"  Total de registros analizados: {resultado['total_registros']}")
        _imprimir_separador()

    except ValueError as error:
        _imprimir_error(str(error))
    except PlaybookNotFoundError as error:
        _imprimir_error(str(error))
    except Exception as error:
        _imprimir_error(f"Error inesperado: {error}")


def cmd_analisis_alertas(args):
    """Verifica si un playbook tiene conflictos o datos incorrectos."""

    try:
        playbook = data_manager.obtener_playbook(args.playbook)

        motor = alerts.MotorAlertas()

        _imprimir_separador()
        print(f"  VERIFICACION DE ALERTAS: {playbook.nombre}")
        _imprimir_separador()

        alertas_encontradas = motor.verificar_playbook(playbook)

        if not alertas_encontradas:
            print("  No se encontraron problemas en el playbook.")

        _imprimir_separador()

    except PlaybookNotFoundError as error:
        _imprimir_error(str(error))
    except Exception as error:
        _imprimir_error(f"Error inesperado: {error}")


# --- Funciones del menu de Reportes ---

def cmd_reportes_csv(args):
    """Exporta las estadisticas de un playbook a un archivo CSV."""

    try:
        playbook = data_manager.obtener_playbook(args.playbook)

        if not playbook.jugadas:
            _imprimir_error("El playbook no tiene jugadas para exportar.")
            return

        estadisticas = analyzer.calcular_estadisticas(playbook.jugadas)
        ruta = reporter.exportar_estadisticas_csv(estadisticas)

        _imprimir_exito(f"Estadisticas exportadas a: {ruta}")

    except PlaybookNotFoundError as error:
        _imprimir_error(str(error))
    except Exception as error:
        _imprimir_error(f"Error al exportar: {error}")


# --- Funciones del menu del Simulador ---

def cmd_simulador_generar(args):
    """Genera un dataset sintetico de jugadas para testing."""

    try:
        cantidad = int(args.jugadas) if args.jugadas else 20
        tipo = args.tipo if args.tipo else None

        jugadas = simulator.generar_jugadas(cantidad=cantidad, tipo_ofensa=tipo)

        # Guardar en CSV
        ruta_csv = simulator.guardar_dataset_csv(jugadas)

        _imprimir_separador()
        print("  SIMULADOR - DATASET GENERADO")
        _imprimir_separador()
        print(f"  Jugadas generadas: {len(jugadas)}")
        print(f"  Archivo CSV: {ruta_csv}")
        _imprimir_separador()

    except Exception as error:
        _imprimir_error(f"Error al generar datos sinteticos: {error}")


# --- Construccion del parser de argumentos ---

def construir_parser():
    """
    Construye y configura el parser de argumentos de la CLI.

    Returns:
        Parser de argparse configurado con todos los subcomandos.
    """

    # Parser principal
    parser = argparse.ArgumentParser(
        prog="playmaker",
        description="PlayMaker Pro - Football Playbook Creator and Analyzer",
        epilog="Usa 'python cli.py <comando> --help' para ver ayuda de cada comando.",
    )

    subparsers = parser.add_subparsers(title="Modulos disponibles", dest="modulo")

    # ==========================================
    # Modulo: playbooks
    # ==========================================
    parser_pb = subparsers.add_parser(
        "playbooks",
        help="Gestionar playbooks (crear, listar, eliminar, exportar)",
    )
    sub_pb = parser_pb.add_subparsers(dest="accion")

    # playbooks listar
    sub_pb.add_parser("listar", help="Listar todos los playbooks guardados")

    # playbooks crear
    p_crear_pb = sub_pb.add_parser("crear", help="Crear un nuevo playbook")
    p_crear_pb.add_argument("--nombre", required=True, help="Nombre del playbook")
    p_crear_pb.add_argument("--tipo", help="Tipo de ofensa (spread, power, west_coast...)")

    # playbooks eliminar
    p_eliminar_pb = sub_pb.add_parser("eliminar", help="Eliminar un playbook por ID")
    p_eliminar_pb.add_argument("--id", required=True, help="ID del playbook a eliminar")

    # playbooks exportar
    p_exportar_pb = sub_pb.add_parser("exportar", help="Exportar jugadas de un playbook a CSV")
    p_exportar_pb.add_argument("--id", required=True, help="ID del playbook a exportar")
    p_exportar_pb.add_argument("--archivo", help="Nombre del archivo de salida (opcional)")

    # ==========================================
    # Modulo: jugadas
    # ==========================================
    parser_j = subparsers.add_parser(
        "jugadas",
        help="Gestionar jugadas (anadir, listar, eliminar, importar)",
    )
    sub_j = parser_j.add_subparsers(dest="accion")

    # jugadas listar
    p_listar_j = sub_j.add_parser("listar", help="Listar jugadas de un playbook")
    p_listar_j.add_argument("--playbook-id", required=True, dest="playbook_id",
                            help="ID del playbook")

    # jugadas anadir
    p_anadir_j = sub_j.add_parser("anadir", help="Anadir una jugada a un playbook")
    p_anadir_j.add_argument("--playbook", required=True, help="ID del playbook")
    p_anadir_j.add_argument("--nombre", required=True, help="Nombre de la jugada")
    p_anadir_j.add_argument("--tipo", required=True,
                            choices=["run", "pass", "special_teams"],
                            help="Tipo de jugada")
    p_anadir_j.add_argument("--formacion", required=True, help="Formacion de la jugada")
    p_anadir_j.add_argument("--yardas", help="Yardas promedio de la jugada")
    p_anadir_j.add_argument("--descripcion", help="Descripcion de la jugada")
    p_anadir_j.add_argument("--tasa-exito", dest="tasa_exito",
                            help="Tasa de exito entre 0.0 y 1.0")
    p_anadir_j.add_argument("--down", help="Situacion de down-and-distance")
    p_anadir_j.add_argument("--hash", help="Posicion en el campo (left/middle/right)")

    # jugadas eliminar
    p_eliminar_j = sub_j.add_parser("eliminar", help="Eliminar una jugada")
    p_eliminar_j.add_argument("--playbook", required=True, help="ID del playbook")
    p_eliminar_j.add_argument("--id", required=True, help="ID de la jugada a eliminar")

    # jugadas importar (RF1)
    p_importar_j = sub_j.add_parser("importar", help="Importar jugadas desde un CSV")
    p_importar_j.add_argument("--archivo", required=True, help="Ruta del archivo CSV")
    p_importar_j.add_argument("--playbook", required=True, help="ID del playbook destino")

    # ==========================================
    # Modulo: analisis
    # ==========================================
    parser_an = subparsers.add_parser(
        "analisis",
        help="Analizar jugadas (estadisticas, anomalias, prediccion, alertas)",
    )
    sub_an = parser_an.add_subparsers(dest="accion")

    # analisis estadisticas (RF3)
    p_stats = sub_an.add_parser("estadisticas", help="Ver estadisticas del playbook")
    p_stats.add_argument("--playbook", required=True, help="ID del playbook")

    # analisis anomalias (RF4)
    p_anom = sub_an.add_parser("anomalias", help="Detectar jugadas con datos inusuales")
    p_anom.add_argument("--playbook", required=True, help="ID del playbook")

    # analisis prediccion (RF7)
    p_pred = sub_an.add_parser("prediccion", help="Predecir efectividad de jugadas")
    p_pred.add_argument("--playbook", required=True, help="ID del playbook")
    p_pred.add_argument("--ventana", default="5", help="Tamano de la ventana (default: 5)")

    # analisis alertas (RF6)
    p_alert = sub_an.add_parser("alertas", help="Verificar conflictos en el playbook")
    p_alert.add_argument("--playbook", required=True, help="ID del playbook")

    # ==========================================
    # Modulo: reportes
    # ==========================================
    parser_rep = subparsers.add_parser(
        "reportes",
        help="Generar reportes (CSV, grafico ASCII)",
    )
    sub_rep = parser_rep.add_subparsers(dest="accion")

    # reportes csv (RF5)
    p_rep_csv = sub_rep.add_parser("csv", help="Exportar estadisticas a CSV")
    p_rep_csv.add_argument("--playbook", required=True, help="ID del playbook")

    # ==========================================
    # Modulo: simulador
    # ==========================================
    parser_sim = subparsers.add_parser(
        "simulador",
        help="Generar datos sinteticos de jugadas para testing",
    )
    sub_sim = parser_sim.add_subparsers(dest="accion")

    # simulador generar (RF10)
    p_gen = sub_sim.add_parser("generar", help="Generar dataset sintetico de jugadas")
    p_gen.add_argument("--jugadas", default="20", help="Cantidad de jugadas a generar")
    p_gen.add_argument("--tipo", choices=["run", "pass", "special_teams"],
                       help="Tipo de jugadas a generar")

    return parser


# --- Tabla de enrutamiento de comandos ---

# Relaciona cada (modulo, accion) con la funcion que lo ejecuta
TABLA_COMANDOS = {
    ("playbooks", "listar"): cmd_playbooks_listar,
    ("playbooks", "crear"): cmd_playbooks_crear,
    ("playbooks", "eliminar"): cmd_playbooks_eliminar,
    ("playbooks", "exportar"): cmd_playbooks_exportar,
    ("jugadas", "listar"): cmd_jugadas_listar,
    ("jugadas", "anadir"): cmd_jugadas_anadir,
    ("jugadas", "eliminar"): cmd_jugadas_eliminar,
    ("jugadas", "importar"): cmd_jugadas_importar,
    ("analisis", "estadisticas"): cmd_analisis_estadisticas,
    ("analisis", "anomalias"): cmd_analisis_anomalias,
    ("analisis", "prediccion"): cmd_analisis_prediccion,
    ("analisis", "alertas"): cmd_analisis_alertas,
    ("reportes", "csv"): cmd_reportes_csv,
    ("simulador", "generar"): cmd_simulador_generar,
}


def main():
    """Funcion principal que inicia la aplicacion CLI."""

    _imprimir_titulo()

    parser = construir_parser()
    args = parser.parse_args()

    # Si no se paso ningun comando, mostrar la ayuda
    if not args.modulo:
        parser.print_help()
        print("")
        print("Ejemplos rapidos:")
        print("  python cli.py playbooks listar")
        print("  python cli.py playbooks crear --nombre 'Red Zone'")
        print("  python cli.py simulador generar --jugadas 30")
        return

    # Obtener la accion del subcomando
    accion = getattr(args, "accion", None)

    if not accion:
        # Si se paso el modulo pero no la accion, mostrar ayuda del modulo
        parser.parse_args([args.modulo, "--help"])
        return

    # Buscar la funcion correspondiente en la tabla de comandos
    clave = (args.modulo, accion)
    funcion_comando = TABLA_COMANDOS.get(clave)

    if funcion_comando:
        funcion_comando(args)
    else:
        _imprimir_error(
            f"Comando no reconocido: '{args.modulo} {accion}'. "
            "Usa --help para ver los comandos disponibles."
        )


# Punto de entrada cuando se ejecuta el archivo directamente
if __name__ == "__main__":
    main()
