"""Run `tests/test_cover_sides.py`'s Blender test inside Blender.

    C:\\blender\\blender.exe --background --python run_bpy_test.py

Blender's Python carries no pytest, so `pytest` is stubbed with the one call
the test makes (`importorskip`), and the test function is called with a
fresh temporary directory. Prints PASS or the assertion, and exits 0 or 1.
"""
import importlib
import pathlib
import sys
import tempfile
import traceback
import types

ZOO = pathlib.Path(__file__).resolve().parents[2] / "zoo"
sys.path.insert(0, str(ZOO))
sys.path.insert(0, str(ZOO / "tests"))
stub = types.ModuleType("pytest")
stub.importorskip = importlib.import_module
sys.modules.setdefault("pytest", stub)

import test_cover_sides as T  # noqa: E402

code = 0
for name in ("test_bpy_one_mesh_a_side_per_material",):
    try:
        with tempfile.TemporaryDirectory() as tmp:
            getattr(T, name)(pathlib.Path(tmp))
        print(f"PASS {name}")
    except Exception:
        traceback.print_exc()
        print(f"FAIL {name}")
        code = 1
sys.stdout.flush()
sys.exit(code)
