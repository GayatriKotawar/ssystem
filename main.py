import os
import sys
from importlib.util import module_from_spec, spec_from_file_location


BACKEND_DIR = os.path.join(os.path.dirname(__file__), "backend")
BACKEND_MAIN_PATH = os.path.join(BACKEND_DIR, "main.py")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


spec = spec_from_file_location("backend_main", BACKEND_MAIN_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("Unable to load backend/main.py")

backend_main = module_from_spec(spec)
spec.loader.exec_module(backend_main)
app = backend_main.app
