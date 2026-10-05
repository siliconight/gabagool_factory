"""Run a Zoo test module's Blender tests inside Blender.

    C:\\blender\\blender.exe --background --python run_bpy_test.py -- <zoo dir> <test module>

Every function in the module named `test_bpy_*` is called with a fresh
temporary directory. Blender's Python carries no pytest, so `pytest` is
stubbed with what the tests call: `importorskip`, `mark.parametrize` (a no-op)
and `approx` (pytest's own default tolerances). Prints PASS or the traceback
per test and exits 0 or 1 -- and 1 when the module has no Blender test at
all, since a run that tested nothing has not passed.

`zoo dir` is any Zoo checkout, so a patch can be tried on a scratch copy
before it is applied to the repo.
"""
import importlib
import pathlib
import sys
import tempfile
import traceback
import types

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ZOO = pathlib.Path(argv[0]).resolve()
MODULE = argv[1]
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

T = importlib.import_module(MODULE)
assert pathlib.Path(T.__file__).resolve().is_relative_to(ZOO), (T.__file__, ZOO)
names = sorted(n for n in dir(T) if n.startswith("test_bpy"))
code = 0 if names else 1
if not names:
    print(f"NO BLENDER TESTS in {MODULE}")
for name in names:
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
