# ============================================================
# tests/test_data_importer.py
# Tests unitarios para data_importer.py (RF1)
# Cubre los casos T01, T02, T03, T04, T05 del plan de testing
# Proyecto: AB Final - Programming & Coding 
# ============================================================

import tempfile

import os
import pytest

# Agregar el directorio raiz al path para importar modulos

import data_importer

# Funciones de ayuda para los tests

def crear_csv_temporal(contenido, encoding="utf-8"):
    """
    Crea un archivo CSV temporal con el contenido indicado.

    Devuelve la ruta del archivo temporal creado.
    """
    archivo_temporal = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        delete=False,
        encoding=encoding,
    )
    archivo_temporal.write(contenido)
    archivo_temporal.close()
    return archivo_temporal.name

def eliminar_archivo(ruta):
    """Elimina un archivo temporal si existe."""
    if os.path.exists(ruta):
        os.unlink(ruta)

# --- Tests T01: CSV valido ---

class TestCargarCsvValido:
    """Tests para cargar un CSV con datos correctos."""

    def test_T01_cargar_csv_valido_devuelve_lista_de_plays(self):
        """
        T01 - Unitario: CSV valido con 10 jugadas debe devolver lista de 10 objetos Play.
        """

        contenido_csv = (
            "nombre,tipo,formacion,yardas,tasa_exito,down_distance,hash_position\n"
            "HB Dive,run,I_FORMATION,4.5,0.65,1st&10,middle\n"
            "Slant Route,pass,SHOTGUN,8.0,0.72,2nd&long,left\n"
            "Counter Left,run,SINGLEBACK,3.0,0.55,3rd&short,right\n"
            "Post Route,pass,SHOTGUN,15.0,0.45,1st&10,middle\n"
            "HB Toss,run,PISTOL,5.5,0.60,2nd&medium,left\n"
            "Screen Pass,pass,EMPTY_SET,7.0,0.70,3rd&medium,right\n"
            "Power Run,run,I_FORMATION,3.5,0.68,4th&short,middle\n"
            "Go Route,pass,GUN_TRIPS,20.0,0.35,1st&10,left\n"
            "QB Sneak,run,SINGLEBACK,1.5,0.80,4th&short,middle\n"
            "Fade Route,pass,SHOTGUN,12.0,0.40,3rd&goal,right\n"
        )

        ruta = crear_csv_temporal(contenido_csv)

        try:
            jugadas = data_importer.cargar_csv(ruta)
            assert len(jugadas) == 10
            assert jugadas[0].nombre == "HB Dive"
            assert jugadas[0].tipo == "run"
            assert jugadas[0].yardas == 4.5
        finally:
            eliminar_archivo(ruta)

    def test_T01_tipos_correctos_en_objetos_play(self):
        """
        T01 - Los objetos Play cargados deben tener los tipos de datos correctos.
        """

        contenido_csv = (
            "nombre,tipo,formacion,yardas,tasa_exito\n"
            "HB Dive,run,SHOTGUN,4.5,0.65\n"
        )

        ruta = crear_csv_temporal(contenido_csv)

        try:
            jugadas = data_importer.cargar_csv(ruta)
            jugada = jugadas[0]

            assert isinstance(jugada.nombre, str)
            assert isinstance(jugada.yardas, float)
            assert isinstance(jugada.tasa_exito, float)
        finally:
            eliminar_archivo(ruta)

# --- Tests T02: CSV vacio ---

class TestCargarCsvVacio:
    """Tests para cargar un CSV que no tiene jugadas."""

    def test_T02_csv_solo_cabeceras_devuelve_lista_vacia(self):
        """
        T02 - Limite: CSV con solo cabeceras debe devolver lista vacia [].
        """

        contenido_csv = "nombre,tipo,formacion,yardas\n"

        ruta = crear_csv_temporal(contenido_csv)

        try:
            jugadas = data_importer.cargar_csv(ruta)
            assert jugadas == []
        finally:
            eliminar_archivo(ruta)

# --- Tests T03: Archivo no encontrado ---

class TestArchivoNoEncontrado:
    """Tests para cuando el archivo CSV no existe."""

    def test_T03_archivo_inexistente_lanza_file_not_found(self):
        """
        T03 - Error: Archivo no encontrado debe lanzar FileNotFoundError.
        """

        with pytest.raises(FileNotFoundError):
            data_importer.cargar_csv("/ruta/que/no/existe/archivo.csv")

    def test_T03_mensaje_error_incluye_la_ruta(self):
        """
        T03 - El mensaje de error debe incluir la ruta del archivo.
        """

        ruta_inexistente = "/ruta/falsa/jugadas.csv"

        with pytest.raises(FileNotFoundError) as info_error:
            data_importer.cargar_csv(ruta_inexistente)

        assert ruta_inexistente in str(info_error.value)

# --- Tests T04: Fila con datos invalidos ---

class TestValidarFilaConErrores:
    """Tests para filas con datos incorrectos en el CSV."""

    def test_T04_yardas_nan_omite_fila_sin_crashear(self):
        """
        T04 - Error: CSV con yardas invalidas debe omitir la fila pero continuar.
        """

        contenido_csv = (
            "nombre,tipo,formacion,yardas\n"
            "Jugada Buena,run,SHOTGUN,5.0\n"
            "Jugada Mala,run,SHOTGUN,no_es_un_numero\n"
        )

        ruta = crear_csv_temporal(contenido_csv)

        try:
            # No debe lanzar excepcion, solo omitir la fila mala
            jugadas = data_importer.cargar_csv(ruta)
            # Solo debe cargar la jugada buena
            assert len(jugadas) == 1
            assert jugadas[0].nombre == "Jugada Buena"
        finally:
            eliminar_archivo(ruta)

    def test_T04_tasa_exito_fuera_de_rango_omite_fila(self):
        """
        T04 - Error: Tasa de exito mayor que 1.0 debe omitir la fila.
        """

        contenido_csv = (
            "nombre,tipo,formacion,yardas,tasa_exito\n"
            "Jugada Valida,run,SHOTGUN,5.0,0.75\n"
            "Jugada Invalida,run,SHOTGUN,5.0,1.5\n"
        )

        ruta = crear_csv_temporal(contenido_csv)

        try:
            jugadas = data_importer.cargar_csv(ruta)
            assert len(jugadas) == 1
        finally:
            eliminar_archivo(ruta)

# --- Tests T05: Columnas extra ---

class TestSanitizarDatos:
    """Tests para la sanitizacion de datos importados."""

    def test_T05_csv_con_columnas_extra_ignora_columnas_sobrantes(self):
        """
        T05 - Limite: CSV con columnas extra debe cargar correctamente ignorando las extras.
        """

        contenido_csv = (
            "nombre,tipo,formacion,yardas,columna_extra,otra_columna_extra\n"
            "HB Dive,run,SHOTGUN,4.5,valor_ignorado,otro_valor_ignorado\n"
        )

        ruta = crear_csv_temporal(contenido_csv)

        try:
            jugadas = data_importer.cargar_csv(ruta)
            assert len(jugadas) == 1
            assert jugadas[0].nombre == "HB Dive"
        finally:
            eliminar_archivo(ruta)

    def test_T05_sanitizar_elimina_jugadas_invalidas(self):
        """
        T05 - La sanitizacion debe eliminar jugadas con datos imposibles.
        """

        from models import Play

        # Crear jugadas: una valida y una con datos invalidos
        jugada_valida = Play(
            nombre="Jugada Valida",
            tipo="run",
            formacion="SHOTGUN",
            yardas=5.0,
            tasa_exito=0.65,
        )

        jugada_invalida = Play(
            nombre="Jugada Invalida",
            tipo="run",
            formacion="SHOTGUN",
            yardas=5.0,
            tasa_exito=2.0,  # Esto esta fuera del rango valido
        )

        jugadas = [jugada_valida, jugada_invalida]
        jugadas_limpias = data_importer.sanitizar_datos(jugadas)

        # Solo debe quedar la jugada valida
        assert len(jugadas_limpias) == 1
        assert jugadas_limpias[0].nombre == "Jugada Valida"
