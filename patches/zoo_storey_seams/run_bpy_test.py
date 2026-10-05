"""Run `tests/test_butt_joints.py`'s Blender tests inside Blender.

    C:\\blender\\blender.exe --background --python run_bpy_test.py

Blender's Python carries no pytest, so `pytest` is stubbed with the calls the
test module makes: `importorskip`, `mark.parametrize` (a no-op decorator --
only the bpy tests are called here) and `approx` (relative 1e-6, absolute
1e-12, pytest's own defaults). Each test is called with a fresh temporary
directory. Prints PASS or the assertion, and exits 0 or 1.
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


class _Approx:
    def __init__(self, expected, rel=1e-6, abs=1e-12):
        self.expected, self.rel, self.abs = expected, rel, abs

    def __eq__(self, other):
        return abs(other - self.expected) <= max(self.rel * abs(self.expected), self.abs)

    def __repr__(self):
        return "approx(%r)" % (self.expected,)


stub = types.ModuleType("pytest")
stub.importorskip = importlib.import_module
stub.approx = _Approx
stub.mark = types.SimpleNamespace(parametrize=lambda *a, **k: (lambda fn: fn))
sys.modules.setdefault("pytest", stub)

import test_butt_joints as T  # noqa: E402

code = 0
for name in ("test_bpy_a_wall_has_no_chamfer_at_its_ends_top_or_bottom",
             "test_bpy_a_doorway_keeps_its_reveal_and_loses_its_ends"):
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
