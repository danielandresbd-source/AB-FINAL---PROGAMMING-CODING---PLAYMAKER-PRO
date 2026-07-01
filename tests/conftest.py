# ============================================================
# tests/conftest.py
# Configuracion global de pytest para todos los tests

# Proyecto: AB Final - Programming & Coding - MSMK 2025-2026
# ============================================================


import random
import sys
import os

import pytest

# Agregar el directorio raiz al path para que pytest encuentre los modulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(autouse=True)
def fijar_semilla_aleatoria():

    """
    Esto inicializa el generador aleatorio con una semilla fija para que todos los
    tests trabajen con los mismos datos en cada ejecución. Esto hace que los
    tests sean repetibles y evita fallos aleatorios.

    autouse=True permite que este fixture se ejecute automáticamente.
    """
    random.seed(42)
