"""Comandos CLI para analizar playbooks."""

import alerts
import analyzer
import data_manager
import reporter
from cli_commands.common import imprimir_error, imprimir_separador
from exceptions import PlaybookNotFoundError


def estadisticas(args):
    """Muestra estadisticas descriptivas de las jugadas de un playbook."""

    try:
        playbook = data_manager.obtener_playbook(args.playbook)

        if not playbook.jugadas:
            imprimir_error(
                f"El playbook '{playbook.nombre}' no tiene jugadas para analizar."
            )
            return

        estadisticas_calculadas = analyzer.calcular_estadisticas(playbook.jugadas)

        imprimir_separador()
        print(f"  ESTADISTICAS: {playbook.nombre}")
        imprimir_separador()
        print(f"  Total de jugadas: {estadisticas_calculadas['total_jugadas']}")
        print(f"  Formacion mas usada: {estadisticas_calculadas['formacion_mas_usada']}")
        print(f"  Yardas promedio: {estadisticas_calculadas['yardas_promedio']}")
        print(f"  Yardas minimas: {estadisticas_calculadas['yardas_minimas']}")
        print(f"  Yardas maximas: {estadisticas_calculadas['yardas_maximas']}")
        print("")

        reporter.mostrar_grafico_ascii(estadisticas_calculadas)
        reporter.mostrar_top_jugadas(estadisticas_calculadas)

    except PlaybookNotFoundError as error:
        imprimir_error(str(error))
    except Exception as error:
        imprimir_error(f"Error inesperado: {error}")


def anomalias(args):
    """Detecta jugadas con datos inusuales en un playbook."""

    try:
        playbook = data_manager.obtener_playbook(args.playbook)

        if not playbook.jugadas:
            imprimir_error("El playbook no tiene jugadas para analizar.")
            return

        anomalias_detectadas = analyzer.detectar_anomalias(playbook.jugadas)

        imprimir_separador()
        print(f"  ANOMALIAS EN: {playbook.nombre}")
        imprimir_separador()

        if not anomalias_detectadas:
            print("  No se encontraron anomalias. Todos los datos parecen correctos.")
        else:
            print(f"  Se encontraron {len(anomalias_detectadas)} jugadas con datos inusuales:\n")
            for item in anomalias_detectadas:
                jugada = item["jugada"]
                razones = item["razones"]
                print(f"  Jugada: {jugada.nombre} (ID: {jugada.id})")
                for razon in razones:
                    print(f"    - {razon}")
                print("")

        imprimir_separador()

    except PlaybookNotFoundError as error:
        imprimir_error(str(error))
    except Exception as error:
        imprimir_error(f"Error inesperado: {error}")


def prediccion(args):
    """Predice la efectividad de las proximas jugadas usando media movil."""

    try:
        playbook = data_manager.obtener_playbook(args.playbook)
        ventana = int(args.ventana) if args.ventana else 5

        resultado = analyzer.predecir_efectividad(playbook.jugadas, ventana=ventana)

        imprimir_separador()
        print(f"  PREDICCION DE EFECTIVIDAD: {playbook.nombre}")
        imprimir_separador()
        print(f"  Prediccion: {int(resultado['prediccion'] * 100)}% de exito")
        print(f"  Tendencia actual: {resultado['tendencia']}")
        print(f"  Ventana de calculo: {resultado['ventana_usada']} jugadas")
        print(f"  Total de registros analizados: {resultado['total_registros']}")
        imprimir_separador()

    except ValueError as error:
        imprimir_error(str(error))
    except PlaybookNotFoundError as error:
        imprimir_error(str(error))
    except Exception as error:
        imprimir_error(f"Error inesperado: {error}")


def alertas_playbook(args):
    """Verifica si un playbook tiene conflictos o datos incorrectos."""

    try:
        playbook = data_manager.obtener_playbook(args.playbook)
        motor = alerts.MotorAlertas()

        imprimir_separador()
        print(f"  VERIFICACION DE ALERTAS: {playbook.nombre}")
        imprimir_separador()

        alertas_encontradas = motor.verificar_playbook(playbook)

        if not alertas_encontradas:
            print("  No se encontraron problemas en el playbook.")

        imprimir_separador()

    except PlaybookNotFoundError as error:
        imprimir_error(str(error))
    except Exception as error:
        imprimir_error(f"Error inesperado: {error}")
