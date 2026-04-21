import importlib
import os
import sys


BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


backend_main = importlib.import_module("main")
app = backend_main.app
