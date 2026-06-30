# ============================================================
# reporter.py
# RF5: Exportacion de reportes a CSV
# RF9: Graficos de barras ASCII en consola
# Proyecto: AB Final - Programming & Coding
# ============================================================

"""
Este modulo se encarga de dos cosas distintas:

1. Exportar datos a archivos CSV (RF5), para que el usuario pueda
   abrirlos en Excel o Google Sheets fuera de la aplicacion.

2. Generar graficos de barras en texto plano (RF9), porque la app
   es de linea de comandos (CLI) y no hay ventana grafica donde
   dibujar un grafico de verdad. Los graficos ASCII son la forma
   estandar de visualizar datos dentro de una terminal.
"""

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

    # No tiene sentido generar un CSV vacio, asi que avisamos antes
    # de crear un archivo que no serviria para nada
    if not jugadas:
        raise ValueError("No hay jugadas para exportar. La lista esta vacia.")

    # Crear el directorio de exportaciones si no existe todavia
    # (evita error si data/exports/ no se ha creado antes)
    os.makedirs(DIRECTORIO_EXPORTACIONES, exist_ok=True)

    # Generar el nombre del archivo si no se proporciono uno.
    # Usamos la fecha y hora actual para que cada exportacion tenga
    # un nombre unico y no se sobreescriba la anterior por accidente
    if not nombre_archivo:
        fecha_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"reporte_jugadas_{fecha_hora}.csv"

    # Asegurarse de que el archivo tenga extension .csv, por si el
    # usuario proporciono un nombre sin extension
    if not nombre_archivo.endswith(".csv"):
        nombre_archivo += ".csv"

    ruta_completa = os.path.join(DIRECTORIO_EXPORTACIONES, nombre_archivo)

    # Columnas que se van a exportar, en el orden que queremos
    # que aparezcan en el CSV final
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
            # Las etiquetas son una lista en Python, pero CSV no soporta
            # listas como valor de celda. Las convertimos a texto
            # separado por punto y coma para que quepan en una columna.
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

    # A diferencia de exportar_csv(), aqui usamos csv.writer normal en
    # vez de DictWriter, porque el formato de salida no es una tabla
    # uniforme de filas iguales: es un reporte con varias secciones
    # distintas (resumen general, distribucion por tipo, top 5), cada
    # una con sus propias columnas.
    with open(ruta_completa, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)

        # Seccion 1: Escribir informacion general del dataset
        escritor.writerow(["Metrica", "Valor"])
        escritor.writerow(["Total de jugadas", estadisticas.get("total_jugadas", 0)])
        escritor.writerow(["Formacion mas usada", estadisticas.get("formacion_mas_usada", "")])
        escritor.writerow(["Yardas promedio", estadisticas.get("yardas_promedio", 0)])
        escritor.writerow(["Yardas minimas", estadisticas.get("yardas_minimas", 0)])
        escritor.writerow(["Yardas maximas", estadisticas.get("yardas_maximas", 0)])
        # Fila vacia para separar visualmente esta seccion de la siguiente
        escritor.writerow([])

        # Seccion 2: Escribir distribucion de jugadas por tipo
        escritor.writerow(["Tipo de jugada", "Cantidad"])
        jugadas_por_tipo = estadisticas.get("jugadas_por_tipo", {})
        for tipo, cantidad in jugadas_por_tipo.items():
            escritor.writerow([tipo, cantidad])
        escritor.writerow([])

        # Seccion 3: Escribir el top 5 de jugadas por tasa de exito
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

    # Construimos el grafico como una lista de lineas de texto y al
    # final las unimos todas con saltos de linea. Es mas eficiente
    # que ir concatenando strings uno por uno dentro del bucle.
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
            # Calcular la longitud de la barra proporcionalmente al
            # valor mas alto, para que la barra mas larga siempre
            # mida 30 caracteres y las demas se escalen respecto a ella
            if valor_maximo > 0:
                longitud_barra = int((cantidad / valor_maximo) * 30)
            else:
                longitud_barra = 0

            barra = "#" * longitud_barra

            # Formatear el tipo para que todas las etiquetas ocupen
            # el mismo ancho (15 caracteres) y las barras queden alineadas
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

        # Ordenar de mayor a menor cantidad, para que las formaciones
        # mas usadas aparezcan primero en el grafico
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

            # Formatear el nombre de la formacion con el mismo ancho fijo
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

    # Unir todas las lineas en un solo texto separado por saltos de linea
    texto_grafico = "\n".join(lineas_grafico)

    # Imprimir en consola para que el usuario lo vea inmediatamente
    print(texto_grafico)

    # Tambien devolvemos el texto como string, util para tests
    # (verificar el contenido sin tener que capturar la salida de print)
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
        # Convertir la tasa decimal (0.0-1.0) a porcentaje entero (0-100)
        # para que sea mas facil de leer de un vistazo
        porcentaje = int(tasa * 100)
        # La barra visual tambien se escala segun la tasa de exito,
        # asi una jugada con mas exito muestra una barra mas larga
        barra = "#" * int(tasa * 30)

        print(f"  {posicion}. {jugada['nombre']}")
        print(f"     Tipo: {jugada['tipo']}  |  Yardas: {jugada['yardas']}")
        print(f"     Exito: {barra} {porcentaje}%")
        print("")

    print("=" * 55)
    print("")
