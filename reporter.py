# ============================================================
# reporter.py
# RF5: Exportacion de reportes a CSV
# RF9: Graficos de barras ASCII en consola
# Proyecto: AB Final - Programming & Coding
# ============================================================

import csv
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

# Directorio donde se guardan los reportes exportados
DIRECTORIO_EXPORTACIONES = os.path.join("data", "exports")


# --- RF5: Exportacion a CSV ---

def exportar_csv(jugadas, nombre_archivo=None):
    """
    Exporta una lista de jugadas a un archivo CSV.

    El archivo se guarda en la carpeta data/exports/ con la fecha y hora
    actual en el nombre para que no se sobreescriba.

    Args:
        jugadas: Lista de objetos Play a exportar.
        nombre_archivo: Nombre del archivo de salida (opcional).
                        Si no se proporciona, se genera uno automaticamente.

    Returns:
        Ruta completa del archivo CSV generado.

    Raises:
        ValueError: Si la lista de jugadas esta vacia.
    """

    if not jugadas:
        raise ValueError("No hay jugadas para exportar. La lista esta vacia.")

    # Crear el directorio de exportaciones si no existe
    os.makedirs(DIRECTORIO_EXPORTACIONES, exist_ok=True)

    # Generar el nombre del archivo si no se proporciono uno
    if not nombre_archivo:
        fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"reporte_jugadas_{fecha_hora}.csv"

    # Asegurarse de que el archivo tenga extension .csv
    if not nombre_archivo.endswith(".csv"):
        nombre_archivo += ".csv"

    ruta_completa = os.path.join(DIRECTORIO_EXPORTACIONES, nombre_archivo)

    # Columnas que se van a exportar
    columnas = [
        "id", "nombre", "tipo", "formacion", "descripcion",
        "yardas", "tasa_exito", "down_distance", "hash_position",
        "etiquetas", "creada_en",
    ]

    with open(ruta_completa, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)

        # Escribir la fila de cabeceras
        escritor.writeheader()

        # Escribir cada jugada como una fila
        for jugada in jugadas:
            fila = jugada.a_diccionario()
            # Las etiquetas se convierten a texto separado por punto y coma
            fila["etiquetas"] = ";".join(fila.get("etiquetas", []))
            escritor.writerow(fila)

    logger.info(f"Reporte exportado: '{ruta_completa}' con {len(jugadas)} jugadas.")

    return ruta_completa


def exportar_estadisticas_csv(estadisticas, nombre_archivo=None):
    """
    Exporta las estadisticas de jugadas a un archivo CSV.

    Args:
        estadisticas: Diccionario con las estadisticas calculadas por analyzer.py
        nombre_archivo: Nombre del archivo de salida (opcional).

    Returns:
        Ruta completa del archivo CSV generado.
    """

    if not estadisticas:
        raise ValueError("No hay estadisticas para exportar.")

    os.makedirs(DIRECTORIO_EXPORTACIONES, exist_ok=True)

    if not nombre_archivo:
        fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"estadisticas_{fecha_hora}.csv"

    if not nombre_archivo.endswith(".csv"):
        nombre_archivo += ".csv"

    ruta_completa = os.path.join(DIRECTORIO_EXPORTACIONES, nombre_archivo)

    with open(ruta_completa, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)

        # Escribir informacion general
        escritor.writerow(["Metrica", "Valor"])
        escritor.writerow(["Total de jugadas", estadisticas.get("total_jugadas", 0)])
        escritor.writerow(["Formacion mas usada", estadisticas.get("formacion_mas_usada", "")])
        escritor.writerow(["Yardas promedio", estadisticas.get("yardas_promedio", 0)])
        escritor.writerow(["Yardas minimas", estadisticas.get("yardas_minimas", 0)])
        escritor.writerow(["Yardas maximas", estadisticas.get("yardas_maximas", 0)])
        escritor.writerow([])

        # Escribir distribucion por tipo
        escritor.writerow(["Tipo de jugada", "Cantidad"])
        jugadas_por_tipo = estadisticas.get("jugadas_por_tipo", {})
        for tipo, cantidad in jugadas_por_tipo.items():
            escritor.writerow([tipo, cantidad])
        escritor.writerow([])

        # Escribir top 5 jugadas
        escritor.writerow(["Top 5 jugadas por tasa de exito"])
        escritor.writerow(["Posicion", "Nombre", "Tipo", "Tasa de exito", "Yardas"])
        top_5 = estadisticas.get("top_5_jugadas", [])
        for i, jugada in enumerate(top_5, start=1):
            escritor.writerow([
                i,
                jugada["nombre"],
                jugada["tipo"],
                jugada["tasa_exito"],
                jugada["yardas"],
            ])

    logger.info(f"Estadisticas exportadas: '{ruta_completa}'")

    return ruta_completa


# --- RF9: Graficos ASCII ---

def mostrar_grafico_ascii(estadisticas):
    """
    Genera y muestra en consola un grafico de barras ASCII.

    El grafico muestra la distribucion de jugadas por tipo y por formacion.

    Args:
        estadisticas: Diccionario con las estadisticas calculadas por analyzer.py

    Returns:
        El texto del grafico como string (tambien lo imprime en consola).
    """

    if not estadisticas:
        return "No hay estadisticas para mostrar."

    lineas_grafico = []

    # --- Grafico de distribucion por tipo de jugada ---
    lineas_grafico.append("")
    lineas_grafico.append("=" * 55)
    lineas_grafico.append("  DISTRIBUCION POR TIPO DE JUGADA")
    lineas_grafico.append("=" * 55)

    jugadas_por_tipo = estadisticas.get("jugadas_por_tipo", {})

    if jugadas_por_tipo:
        valor_maximo = max(jugadas_por_tipo.values())

        for tipo, cantidad in sorted(jugadas_por_tipo.items()):
            # Calcular la longitud de la barra proporcionalmente
            if valor_maximo > 0:
                longitud_barra = int((cantidad / valor_maximo) * 30)
            else:
                longitud_barra = 0

            barra = "#" * longitud_barra

            # Formatear el tipo para que ocupe 15 caracteres
            tipo_formateado = tipo.ljust(15)

            lineas_grafico.append(f"  {tipo_formateado} | {barra} {cantidad}")

    # --- Grafico de distribucion por formacion ---
    lineas_grafico.append("")
    lineas_grafico.append("=" * 55)
    lineas_grafico.append("  DISTRIBUCION POR FORMACION")
    lineas_grafico.append("=" * 55)

    jugadas_por_formacion = estadisticas.get("jugadas_por_formacion", {})

    if jugadas_por_formacion:
        valor_maximo_formacion = max(jugadas_por_formacion.values())

        # Ordenar por cantidad de mayor a menor
        formaciones_ordenadas = sorted(
            jugadas_por_formacion.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        for formacion, cantidad in formaciones_ordenadas:
            if valor_maximo_formacion > 0:
                longitud_barra = int((cantidad / valor_maximo_formacion) * 25)
            else:
                longitud_barra = 0

            barra = "#" * longitud_barra

            # Formatear el nombre de la formacion
            formacion_formateada = formacion.ljust(15)

            lineas_grafico.append(f"  {formacion_formateada} | {barra} {cantidad}")

    lineas_grafico.append("")
    lineas_grafico.append(
        f"  Total de jugadas analizadas: {estadisticas.get('total_jugadas', 0)}"
    )
    lineas_grafico.append(
        f"  Yardas promedio: {estadisticas.get('yardas_promedio', 0)}"
    )
    lineas_grafico.append("=" * 55)
    lineas_grafico.append("")

    # Unir todas las lineas en un solo texto
    texto_grafico = "\n".join(lineas_grafico)

    # Imprimir en consola
    print(texto_grafico)

    return texto_grafico


def mostrar_top_jugadas(estadisticas):
    """
    Muestra en consola el top 5 de jugadas por tasa de exito.

    Args:
        estadisticas: Diccionario con las estadisticas calculadas.
    """

    top_5 = estadisticas.get("top_5_jugadas", [])

    if not top_5:
        print("No hay jugadas para mostrar.")
        return

    print("")
    print("=" * 55)
    print("  TOP 5 JUGADAS POR TASA DE EXITO")
    print("=" * 55)

    for posicion, jugada in enumerate(top_5, start=1):
        tasa = jugada["tasa_exito"]
        porcentaje = int(tasa * 100)
        barra = "#" * int(tasa * 30)

        print(f"  {posicion}. {jugada['nombre']}")
        print(f"     Tipo: {jugada['tipo']}  |  Yardas: {jugada['yardas']}")
        print(f"     Exito: {barra} {porcentaje}%")
        print("")

    print("=" * 55)
    print("")
