# ============================================================
# tests/test_cli.py
# Tests unitarios para cli.py (RF8)
# Cubre: construccion del parser de argparse y la funcion main()
#        que enruta cada comando a su modulo en cli_commands/
# Objetivo: cerrar el ultimo hueco de cobertura detectado en
# revision de pares (cli.py estaba en 0% de cobertura)
# Proyecto: AB Final - Programming & Coding - MSMK 2025-2026
# ============================================================

import sys

import pytest

import cli
import data_manager


# ============================================================
# Fixture de aislamiento
# ============================================================
# Mismo patron que en test_cli_commands.py: aislamos cada test en
# un directorio temporal y redirigimos el JSON de persistencia,
# para que correr estos tests no toque el proyecto real.

@pytest.fixture(autouse=True)
def entorno_aislado(tmp_path, monkeypatch):
    """Aisla cada test en un directorio temporal con su propio JSON."""

    monkeypatch.chdir(tmp_path)

    directorio_data = tmp_path / "data"
    directorio_data.mkdir()

    ruta_temporal = str(directorio_data / "playbooks.json")
    monkeypatch.setattr(data_manager, "RUTA_JSON", ruta_temporal)


# ============================================================
# construir_parser()
# ============================================================
# Estos tests no ejecutan ningun comando, solo verifican que
# argparse reconoce correctamente cada modulo, accion y argumento,
# incluyendo los 'dest' personalizados (--playbook-id -> playbook_id,
# --tasa-exito -> tasa_exito, etc.)

class TestConstruirParser:
    """Tests para la estructura del parser de argparse."""

    def test_parser_playbooks_listar(self):
        parser = cli.construir_parser()
        args = parser.parse_args(["playbooks", "listar"])

        assert args.modulo == "playbooks"
        assert args.accion == "listar"

    def test_parser_playbooks_crear_con_argumentos(self):
        parser = cli.construir_parser()
        args = parser.parse_args(
            ["playbooks", "crear", "--nombre", "Red Zone", "--tipo", "spread"]
        )

        assert args.modulo == "playbooks"
        assert args.accion == "crear"
        assert args.nombre == "Red Zone"
        assert args.tipo == "spread"

    def test_parser_jugadas_listar_usa_dest_playbook_id(self):
        parser = cli.construir_parser()
        args = parser.parse_args(["jugadas", "listar", "--playbook-id", "pb_001"])

        # El argumento se escribe con guion (--playbook-id) pero el
        # dest se configuro explicitamente como playbook_id con guion bajo
        assert args.playbook_id == "pb_001"

    def test_parser_jugadas_anadir_argumentos_completos(self):
        parser = cli.construir_parser()
        args = parser.parse_args([
            "jugadas", "anadir",
            "--playbook", "pb_001",
            "--nombre", "HB Dive",
            "--tipo", "run",
            "--formacion", "SHOTGUN",
            "--yardas", "4.5",
            "--tasa-exito", "0.7",
            "--down", "1st&10",
            "--hash", "middle",
        ])

        assert args.playbook == "pb_001"
        assert args.nombre == "HB Dive"
        assert args.tipo == "run"
        assert args.formacion == "SHOTGUN"
        assert args.yardas == "4.5"
        # --tasa-exito se guarda en dest=tasa_exito (con guion bajo)
        assert args.tasa_exito == "0.7"
        assert args.down == "1st&10"
        assert args.hash == "middle"

    def test_parser_jugadas_anadir_tipo_invalido_falla(self):
        # El argparse define choices=["run","pass","special_teams"]
        # para --tipo, asi que un valor fuera de esa lista debe
        # provocar que argparse termine el programa con SystemExit
        parser = cli.construir_parser()

        with pytest.raises(SystemExit):
            parser.parse_args([
                "jugadas", "anadir",
                "--playbook", "pb_001",
                "--nombre", "Jugada Rara",
                "--tipo", "kickflip",
                "--formacion", "SHOTGUN",
            ])

    def test_parser_analisis_prediccion_ventana_por_defecto(self):
        parser = cli.construir_parser()
        args = parser.parse_args(["analisis", "prediccion", "--playbook", "pb_001"])

        # --ventana tiene default="5" definido en cli.py
        assert args.ventana == "5"

    def test_parser_simulador_generar_valores_por_defecto(self):
        parser = cli.construir_parser()
        args = parser.parse_args(["simulador", "generar"])

        # --jugadas tiene default="20" definido en cli.py
        assert args.jugadas == "20"
        assert args.tipo is None

    def test_parser_sin_argumentos_no_falla(self):
        # Llamar al programa sin ningun modulo es valido a nivel de
        # argparse (modulo queda en None); el manejo de ese caso lo
        # hace main(), no el parser
        parser = cli.construir_parser()
        args = parser.parse_args([])

        assert args.modulo is None


# ============================================================
# main()
# ============================================================
# Estos tests simulan ejecutar "python cli.py <argumentos>"
# sobreescribiendo sys.argv, igual que hace argparse normalmente
# al leer la linea de comandos real.

class TestMainSinModulo:
    """Tests para cuando se ejecuta el CLI sin ningun modulo."""

    def test_main_sin_argumentos_muestra_ayuda_y_ejemplos(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["cli.py"])

        cli.main()
        salida = capsys.readouterr().out

        assert "PLAYMAKER PRO" in salida
        assert "Ejemplos rapidos" in salida
        assert "python cli.py playbooks listar" in salida


class TestMainModuloSinAccion:
    """Tests para cuando se indica un modulo pero ninguna accion."""

    def test_main_modulo_sin_accion_redirige_a_ayuda_del_modulo(
        self, monkeypatch, capsys
    ):
        # Cuando se ejecuta "python cli.py playbooks" sin accion,
        # main() vuelve a llamar a parser.parse_args() con ["playbooks","--help"],
        # lo cual hace que argparse imprima la ayuda y termine el programa
        # con SystemExit (comportamiento estandar de argparse con --help)
        monkeypatch.setattr(sys, "argv", ["cli.py", "playbooks"])

        with pytest.raises(SystemExit) as info_salida:
            cli.main()

        # --help termina con codigo 0 (no es un error, es ayuda pedida)
        assert info_salida.value.code == 0

        salida = capsys.readouterr().out
        assert "playbooks" in salida.lower()


class TestMainEjecutaComandos:
    """Tests para la ejecucion real de comandos a traves de main()."""

    def test_main_playbooks_crear_persiste_el_playbook(self, monkeypatch, capsys):
        monkeypatch.setattr(
            sys, "argv",
            ["cli.py", "playbooks", "crear", "--nombre", "Equipo Test"],
        )

        cli.main()
        salida = capsys.readouterr().out

        assert "[OK]" in salida
        guardados = data_manager.listar_playbooks()
        assert len(guardados) == 1
        assert guardados[0].nombre == "Equipo Test"

    def test_main_playbooks_listar_sin_datos_muestra_aviso(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["cli.py", "playbooks", "listar"])

        cli.main()
        salida = capsys.readouterr().out

        assert "No hay playbooks guardados todavia" in salida

    def test_main_simulador_generar_ejecuta_correctamente(self, monkeypatch, capsys):
        monkeypatch.setattr(
            sys, "argv",
            ["cli.py", "simulador", "generar", "--jugadas", "5"],
        )

        cli.main()
        salida = capsys.readouterr().out

        assert "SIMULADOR" in salida
        assert "Jugadas generadas: 5" in salida

    def test_main_comando_no_mapeado_en_tabla_muestra_error(
        self, monkeypatch, capsys
    ):
        # Este es un caso defensivo: en condiciones normales argparse
        # nunca deja pasar una combinacion modulo+accion que no exista
        # en TABLA_COMANDOS, porque las acciones validas se definen como
        # subparsers (argparse las rechaza antes de llegar a main()).
        # Para probar esta rama de seguridad igualmente, simulamos el
        # escenario quitando temporalmente una entrada de la tabla.
        monkeypatch.setattr(sys, "argv", ["cli.py", "playbooks", "listar"])

        tabla_reducida = dict(cli.TABLA_COMANDOS)
        del tabla_reducida[("playbooks", "listar")]
        monkeypatch.setattr(cli, "TABLA_COMANDOS", tabla_reducida)

        cli.main()
        salida = capsys.readouterr().out

        assert "Comando no reconocido" in salida

