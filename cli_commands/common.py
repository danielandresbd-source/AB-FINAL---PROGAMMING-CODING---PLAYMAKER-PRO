"""Funciones compartidas para presentar mensajes en la CLI."""


def imprimir_separador():
    """Imprime una linea separadora en consola."""
    print("=" * 55)


def imprimir_titulo():
    """Muestra el titulo de la aplicacion al iniciarla."""
    imprimir_separador()
    print("  PLAYMAKER PRO")
    print("  Football Playbook Creator and Analyzer")
    print("  Madrid Bulldogs - MSMK University 2025-2026")
    imprimir_separador()
    print("")


def imprimir_error(mensaje):
    """Muestra un mensaje de error de forma clara."""
    print(f"\n[ERROR] {mensaje}\n")


def imprimir_exito(mensaje):
    """Muestra un mensaje de exito."""
    print(f"\n[OK] {mensaje}\n")
