import os
import sys

# Permite ejecutar `pytest` desde la raíz del proyecto y que los tests
# puedan hacer `from src.models... import ...` / `from config.db import ...`
# igual que lo hace app.py.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
