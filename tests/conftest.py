# ============================================================
# tests/conftest.py
# Configuracion global de pytest para todos los tests
# Agrega el directorio raiz al path de Python una sola vez aqui,
# para que cada archivo de test no tenga que hacerlo individualmente.
# Proyecto: AB Final - Programming & Coding - MSMK 2025-2026
# ============================================================

import os
import sys

# Agregar el directorio raiz del proyecto al path de Python
# Esto permite importar los modulos del proyecto desde cualquier test
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
