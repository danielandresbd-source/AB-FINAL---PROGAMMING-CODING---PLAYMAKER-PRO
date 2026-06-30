# ============================================================
# tests/test_cli_commands.py
# Tests unitarios para los modulos de cli_commands/
# Cubre: common.py, playbooks.py, jugadas.py, analisis.py,
#        reportes.py, simulador.py
# Objetivo: cerrar el hueco de cobertura detectado en revision
# de pares (cli_commands/* estaba excluido de coverage y sin tests)
# Proyecto: AB Final - Programming & Coding - MSMK 2025-2026
# ============================================================

from argparse import Namespace

import pytest

import data_manager
from cli_commands import analisis, common, jugadas, playbooks, reportes, simulador
from models import Play


# ============================================================
# Fixture de aislamiento
# ============================================================
# Igual que en test_data_manager.py, redirigimos RUTA_JSON a un
# archivo temporal para no tocar el JSON real del proyecto.
# Ademas hacemos chdir a una carpeta temporal porque reporter.py
# y simulator.py escriben en rutas relativas "data/exports/..."
# directamente, sin pasar por una variable que se pueda monkeypatchear.
# Al cambiar el directorio de trabajo, esas rutas relativas terminan
# dentro de la carpeta temporal de pytest en vez de en el proyecto real.

@pytest.fixture(autouse=True)
def entorno_aislado(tmp_path, monkeypatch):
    """Aisla cada test en un directorio temporal con su propio JSON."""

    monkeypatch.chdir(tmp_path)

    directorio_data = tmp_path / "data"
    directorio_data.mkdir()

    ruta_temporal = str(directorio_data / "playbooks.json")
    monkeypatch.setattr(data_manager, "RUTA_JSON", ruta_temporal)


# ============================================================
# common.py
# ============================================================

class TestCommon:
    """Tests para las funciones de presentacion compartidas."""

    def test_imprimir_separador_muestra_linea_de_55_caracteres(self, capsys):
        common.imprimir_separador()
        salida = capsys.readouterr().out
        assert "=" * 55 in salida

    def test_imprimir_titulo_muestra_nombre_de_la_app(self, capsys):
        common.imprimir_titulo()
        salida = capsys.readouterr().out
        assert "PLAYMAKER PRO" in salida
        assert "Madrid Bulldogs" in salida

    def test_imprimir_error_incluye_etiqueta_error(self, capsys):
        common.imprimir_error("algo salio mal")
        salida = capsys.readouterr().out
        assert "[ERROR]" in salida
        assert "algo salio mal" in salida

    def test_imprimir_exito_incluye_etiqueta_ok(self, capsys):
        common.imprimir_exito("todo bien")
        salida = capsys.readouterr().out
        assert "[OK]" in salida
        assert "todo bien" in salida


# ============================================================
# playbooks.py
# ============================================================

class TestPlaybooksListar:
    """Tests para el comando 'playbooks listar'."""

    def test_listar_sin_playbooks_muestra_mensaje_vacio(self, capsys):
        playbooks.listar(Namespace())
        salida = capsys.readouterr().out
        assert "No hay playbooks guardados todavia" in salida

    def test_listar_con_playbooks_muestra_sus_datos(self, capsys):
        data_manager.crear_playbook("Red Zone Offense", tipo_ofensa="spread")

        playbooks.listar(Namespace())
        salida = capsys.readouterr().out

        assert "Red Zone Offense" in salida
        assert "spread" in salida


class TestPlaybooksCrear:
    """Tests para el comando 'playbooks crear'."""

    def test_crear_con_nombre_valido_lo_guarda(self, capsys):
        args = Namespace(nombre="Two Minute Drill", tipo="power")

        playbooks.crear(args)
        salida = capsys.readouterr().out

        assert "[OK]" in salida
        assert "Two Minute Drill" in salida

        guardados = data_manager.listar_playbooks()
        assert len(guardados) == 1
        assert guardados[0].nombre == "Two Minute Drill"

    def test_crear_sin_tipo_usa_spread_por_defecto(self):
        args = Namespace(nombre="Sin Tipo", tipo=None)

        playbooks.crear(args)

        guardado = data_manager.listar_playbooks()[0]
        assert guardado.tipo_ofensa == "spread"

    def test_crear_con_nombre_vacio_muestra_error(self, capsys):
        args = Namespace(nombre="", tipo=None)

        playbooks.crear(args)
        salida = capsys.readouterr().out

        assert "[ERROR]" in salida
        assert data_manager.listar_playbooks() == []


class TestPlaybooksEliminar:
    """Tests para el comando 'playbooks eliminar'."""

    def test_eliminar_id_existente_lo_borra(self, capsys):
        playbook = data_manager.crear_playbook("Playbook a Borrar")

        playbooks.eliminar(Namespace(id=playbook.id))
        salida = capsys.readouterr().out

        assert "[OK]" in salida
        assert data_manager.listar_playbooks() == []

    def test_eliminar_id_inexistente_muestra_error(self, capsys):
        playbooks.eliminar(Namespace(id="pb_no_existe"))
        salida = capsys.readouterr().out

        assert "[ERROR]" in salida


class TestPlaybooksExportar:
    """Tests para el comando 'playbooks exportar'."""

    def test_exportar_playbook_sin_jugadas_muestra_error(self, capsys):
        playbook = data_manager.crear_playbook("Playbook Vacio")

        playbooks.exportar(Namespace(id=playbook.id, archivo=None))
        salida = capsys.readouterr().out

        assert "[ERROR]" in salida
        assert "no tiene jugadas" in salida

    def test_exportar_playbook_con_jugadas_genera_archivo(self, capsys):
        playbook = data_manager.crear_playbook("Playbook Con Jugadas")
        jugada = Play(nombre="HB Dive", tipo="run", formacion="SHOTGUN", yardas=5.0)
        data_manager.anadir_jugada(playbook.id, jugada)

        playbooks.exportar(Namespace(id=playbook.id, archivo=None))
        salida = capsys.readouterr().out

        assert "[OK]" in salida
        assert "exportado" in salida.lower()

    def test_exportar_playbook_inexistente_muestra_error(self, capsys):
        playbooks.exportar(Namespace(id="pb_fantasma", archivo=None))
        salida = capsys.readouterr().out

        assert "[ERROR]" in salida


# ============================================================
# jugadas.py
# ============================================================

class TestJugadasListar:
    """Tests para el comando 'jugadas listar'."""

    def test_listar_playbook_inexistente_muestra_error(self, capsys):
        jugadas.listar(Namespace(playbook_id="pb_no_existe"))
        salida = capsys.readouterr().out

        assert "[ERROR]" in salida

    def test_listar_playbook_sin_jugadas_muestra_aviso(self, capsys):
        playbook = data_manager.crear_playbook("Playbook Vacio")

        jugadas.listar(Namespace(playbook_id=playbook.id))
        salida = capsys.readouterr().out

        assert "no tiene jugadas todavia" in salida

    def test_listar_playbook_con_jugadas_las_muestra(self, capsys):
        playbook = data_manager.crear_playbook("Playbook Con Datos")
        jugada = Play(nombre="Slant Route", tipo="pass", formacion="SHOTGUN", yardas=8.0)
        data_manager.anadir_jugada(playbook.id, jugada)

        jugadas.listar(Namespace(playbook_id=playbook.id))
        salida = capsys.readouterr().out

        assert "Slant Route" in salida


class TestJugadasAnadir:
    """Tests para el comando 'jugadas anadir'."""

    def _args_validos(self, playbook_id):
        return Namespace(
            playbook=playbook_id,
            nombre="HB Dive Left",
            tipo="run",
            formacion="SHOTGUN",
            descripcion=None,
            yardas="4.5",
            tasa_exito="0.7",
            down=None,
            hash=None,
        )

    def test_anadir_jugada_valida_la_guarda(self, capsys):
        playbook = data_manager.crear_playbook("Playbook Jugadas")

        jugadas.anadir(self._args_validos(playbook.id))
        salida = capsys.readouterr().out

        assert "[OK]" in salida
        playbook_actualizado = data_manager.obtener_playbook(playbook.id)
        assert len(playbook_actualizado.jugadas) == 1
        assert playbook_actualizado.jugadas[0].nombre == "HB Dive Left"

    def test_anadir_jugada_a_playbook_inexistente_muestra_error(self, capsys):
        jugadas.anadir(self._args_validos("pb_no_existe"))
        salida = capsys.readouterr().out

        assert "[ERROR]" in salida

    def test_anadir_jugada_con_tipo_invalido_muestra_error(self, capsys):
        playbook = data_manager.crear_playbook("Playbook Tipo Invalido")
        args = self._args_validos(playbook.id)
        args.tipo = "kickflip"

        jugadas.anadir(args)
        salida = capsys.readouterr().out

        assert "[ERROR]" in salida


class TestJugadasEliminar:
    """Tests para el comando 'jugadas eliminar'."""

    def test_eliminar_jugada_existente_la_borra(self, capsys):
        playbook = data_manager.crear_playbook("Playbook Eliminar")
        jugada = Play(nombre="Power Run", tipo="run", formacion="I_FORMATION", yardas=3.0)
        data_manager.anadir_jugada(playbook.id, jugada)

        jugadas.eliminar(Namespace(playbook=playbook.id, id=jugada.id))
        salida = capsys.readouterr().out

        assert "[OK]" in salida
        playbook_actualizado = data_manager.obtener_playbook(playbook.id)
        assert playbook_actualizado.jugadas == []

    def test_eliminar_jugada_inexistente_muestra_error(self, capsys):
        playbook = data_manager.crear_playbook("Playbook Sin Jugada")

        jugadas.eliminar(Namespace(playbook=playbook.id, id="play_no_existe"))
        salida = capsys.readouterr().out

        assert "[ERROR]" in salida


class TestJugadasImportar:
    """Tests para el comando 'jugadas importar'."""

    def _crear_csv_valido(self, tmp_path):
        contenido = (
            "nombre,tipo,formacion,yardas,tasa_exito,down_distance,"
            "hash_position,etiquetas,descripcion\n"
            "HB Dive,run,SHOTGUN,4.5,0.7,1st&10,middle,power_run,Jugada de prueba\n"
            "Slant Route,pass,SHOTGUN,8.0,0.65,2nd&long,left,blitz_beater,Pase rapido\n"
        )
        ruta = tmp_path / "jugadas_validas.csv"
        ruta.write_text(contenido, encoding="utf-8")
        return str(ruta)

    def test_importar_csv_valido_anade_jugadas(self, tmp_path, capsys):
        playbook = data_manager.crear_playbook("Playbook Importacion")
        ruta_csv = self._crear_csv_valido(tmp_path)

        jugadas.importar(Namespace(archivo=ruta_csv, playbook=playbook.id))
        salida = capsys.readouterr().out

        assert "[OK]" in salida
        playbook_actualizado = data_manager.obtener_playbook(playbook.id)
        assert len(playbook_actualizado.jugadas) == 2

    def test_importar_archivo_inexistente_muestra_error(self, capsys):
        playbook = data_manager.crear_playbook("Playbook Importacion Fallida")

        jugadas.importar(
            Namespace(archivo="no_existe.csv", playbook=playbook.id)
        )
        salida = capsys.readouterr().out

        assert "[ERROR]" in salida

    def test_importar_a_playbook_inexistente_muestra_error(self, tmp_path, capsys):
        ruta_csv = self._crear_csv_valido(tmp_path)

        jugadas.importar(Namespace(archivo=ruta_csv, playbook="pb_fantasma"))
        salida = capsys.readouterr().out

        assert "[ERROR]" in salida


# ============================================================
# analisis.py
# ============================================================

class TestAnalisisEstadisticas:
    """Tests para el comando 'analisis estadisticas'."""

    def test_estadisticas_playbook_inexistente_muestra_error(self, capsys):
        analisis.estadisticas(Namespace(playbook="pb_fantasma"))
        salida = capsys.readouterr().out

        assert "[ERROR]" in salida

    def test_estadisticas_playbook_sin_jugadas_muestra_error(self, capsys):
        playbook = data_manager.crear_playbook("Playbook Sin Datos")

        analisis.estadisticas(Namespace(playbook=playbook.id))
        salida = capsys.readouterr().out

        assert "[ERROR]" in salida
        assert "no tiene jugadas" in salida

    def test_estadisticas_con_jugadas_muestra_resumen(self, capsys):
        playbook = data_manager.crear_playbook("Playbook Estadisticas")
        for i in range(3):
            jugada = Play(
                nombre=f"Jugada {i}", tipo="run",
                formacion="SHOTGUN", yardas=4.0 + i,
            )
            data_manager.anadir_jugada(playbook.id, jugada)

        analisis.estadisticas(Namespace(playbook=playbook.id))
        salida = capsys.readouterr().out

        assert "ESTADISTICAS" in salida
        assert "Total de jugadas: 3" in salida


class TestAnalisisAnomalias:
    """Tests para el comando 'analisis anomalias'."""

    def test_anomalias_sin_jugadas_muestra_error(self, capsys):
        playbook = data_manager.crear_playbook("Playbook Sin Jugadas")

        analisis.anomalias(Namespace(playbook=playbook.id))
        salida = capsys.readouterr().out

        assert "[ERROR]" in salida

    def test_anomalias_sin_anomalias_muestra_mensaje_correcto(self, capsys):
        playbook = data_manager.crear_playbook("Playbook Normal")
        for i in range(3):
            jugada = Play(
                nombre=f"Jugada Normal {i}", tipo="run",
                formacion="SHOTGUN", yardas=4.0, tasa_exito=0.6,
            )
            data_manager.anadir_jugada(playbook.id, jugada)

        analisis.anomalias(Namespace(playbook=playbook.id))
        salida = capsys.readouterr().out

        assert "No se encontraron anomalias" in salida

    def test_anomalias_con_nombre_duplicado_las_detecta(self, capsys):
        playbook = data_manager.crear_playbook("Playbook Duplicados")
        for _ in range(2):
            jugada = Play(
                nombre="Jugada Repetida", tipo="run",
                formacion="SHOTGUN", yardas=4.0, tasa_exito=0.6,
            )
            data_manager.anadir_jugada(playbook.id, jugada)

        analisis.anomalias(Namespace(playbook=playbook.id))
        salida = capsys.readouterr().out

        assert "Se encontraron" in salida


class TestAnalisisPrediccion:
    """Tests para el comando 'analisis prediccion'."""

    def test_prediccion_con_pocos_registros_muestra_error(self, capsys):
        playbook = data_manager.crear_playbook("Playbook Pocos Datos")
        jugada = Play(nombre="Unica Jugada", tipo="run", formacion="SHOTGUN", yardas=4.0)
        data_manager.anadir_jugada(playbook.id, jugada)

        analisis.prediccion(Namespace(playbook=playbook.id, ventana=None))
        salida = capsys.readouterr().out

        assert "[ERROR]" in salida

    def test_prediccion_con_registros_suficientes_muestra_resultado(self, capsys):
        playbook = data_manager.crear_playbook("Playbook Prediccion")
        for i in range(6):
            jugada = Play(
                nombre=f"Jugada {i}", tipo="run",
                formacion="SHOTGUN", yardas=4.0, tasa_exito=0.5 + (i * 0.02),
            )
            data_manager.anadir_jugada(playbook.id, jugada)

        analisis.prediccion(Namespace(playbook=playbook.id, ventana=None))
        salida = capsys.readouterr().out

        assert "PREDICCION" in salida
        assert "Tendencia actual" in salida


class TestAnalisisAlertas:
    """Tests para el comando 'analisis alertas_playbook'."""

    def test_alertas_playbook_sin_problemas_muestra_mensaje_ok(self, capsys):
        playbook = data_manager.crear_playbook("Playbook Sano")
        jugada = Play(
            nombre="Jugada Correcta", tipo="run",
            formacion="SHOTGUN", yardas=4.0, tasa_exito=0.6,
            down_distance="1st&10", hash_position="middle",
        )
        data_manager.anadir_jugada(playbook.id, jugada)

        analisis.alertas_playbook(Namespace(playbook=playbook.id))
        salida = capsys.readouterr().out

        assert "VERIFICACION DE ALERTAS" in salida

    def test_alertas_playbook_inexistente_muestra_error(self, capsys):
        analisis.alertas_playbook(Namespace(playbook="pb_fantasma"))
        salida = capsys.readouterr().out

        assert "[ERROR]" in salida


# ============================================================
# reportes.py
# ============================================================

class TestReportesCsv:
    """Tests para el comando 'reportes csv'."""

    def test_csv_sin_jugadas_muestra_error(self, capsys):
        playbook = data_manager.crear_playbook("Playbook Sin Jugadas Reporte")

        reportes.csv(Namespace(playbook=playbook.id))
        salida = capsys.readouterr().out

        assert "[ERROR]" in salida

    def test_csv_con_jugadas_genera_archivo(self, capsys):
        playbook = data_manager.crear_playbook("Playbook Con Jugadas Reporte")
        jugada = Play(nombre="HB Dive", tipo="run", formacion="SHOTGUN", yardas=5.0)
        data_manager.anadir_jugada(playbook.id, jugada)

        reportes.csv(Namespace(playbook=playbook.id))
        salida = capsys.readouterr().out

        assert "[OK]" in salida
        assert "exportadas" in salida.lower()

    def test_csv_playbook_inexistente_muestra_error(self, capsys):
        reportes.csv(Namespace(playbook="pb_fantasma"))
        salida = capsys.readouterr().out

        assert "[ERROR]" in salida


# ============================================================
# simulador.py
# ============================================================

class TestSimuladorGenerar:
    """Tests para el comando 'simulador generar'."""

    def test_generar_con_cantidad_por_defecto_crea_20_jugadas(self, capsys):
        simulador.generar(Namespace(jugadas=None, tipo=None))
        salida = capsys.readouterr().out

        assert "SIMULADOR" in salida
        assert "Jugadas generadas: 20" in salida

    def test_generar_con_cantidad_especifica_la_respeta(self, capsys):
        simulador.generar(Namespace(jugadas="7", tipo=None))
        salida = capsys.readouterr().out

        assert "Jugadas generadas: 7" in salida

    def test_generar_con_tipo_especifico_no_lanza_error(self, capsys):
        simulador.generar(Namespace(jugadas="5", tipo="run"))
        salida = capsys.readouterr().out

        assert "[ERROR]" not in salida
        assert "Jugadas generadas: 5" in salida
