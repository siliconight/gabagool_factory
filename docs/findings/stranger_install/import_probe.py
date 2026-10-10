"""Roadmap 202: which of a level's Python entry points import under a given interpreter.

    <interpreter> -B docs/findings/stranger_install/import_probe.py [--json]

Run it BY the interpreter under test (Blender's bundled one is
`<blender dir>/<version>/python/bin/python.exe`). For each entry point Level Factory's adapters
launch with `python_executable`, it loads that module in a fresh child of the same interpreter,
isolated (`-I`: no PYTHONPATH, no user site, no script directory) and writing no bytecode (`-B`),
with only that tool's own checkout on `sys.path`. A script entry point is loaded under a name
that is not `__main__`, so its main guard does not fire and nothing runs.

It measures TOP-LEVEL imports only. An import inside a function is reached only when that
function runs, and this does not run anything; those sites are listed separately in the
README from a search, not from this probe. A module that fails to load is reported with the
missing module's name when the failure is a missing module, and with the exception's type and
first line otherwise. It prints what it measured and stops.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

FACTORY = Path(__file__).resolve().parents[3]

# (tool, sys.path entry relative to the factory root, how it is loaded, target).
# "module" targets are imported by dotted name; "file" targets are loaded from a path.
ENTRY_POINTS = [
    ("level_factory", "level_factory", "module", "apps.cli.main"),
    ("level_factory", "level_factory", "file", "assets/scripts/run_presentation_compose.py"),
    ("deli_counter", "deli_counter", "file", "new_level.py"),
    ("deli_counter", "deli_counter", "file", "build.py"),
    ("deli_counter", "deli_counter", "file", "deli_counter.py"),
    ("deli_counter", "deli_counter", "file", "portable_building.py"),
    ("deli_counter", "deli_counter", "file", "themed_tscn.py"),
    ("deli_counter", "deli_counter", "file", "circulation.py"),
    ("deli_counter", "deli_counter", "file", "zfight_gate.py"),
    ("lot", "lot", "file", "lot.py"),
    ("lot", "lot", "file", "walktest.py"),
    ("pixelcoat", "pixelcoat", "module", "pixelcoat.cli.main"),
    ("patina", "patina", "module", "patina.cli"),
    ("patina", "patina", "module", "patina.surface_dressing"),
    ("dispatch", "dispatch", "module", "dispatch.__main__"),
    ("zoo", "zoo", "file", "tools/zoo_cli.py"),
]

LOADER = r"""
import importlib, importlib.util, sys, traceback
sys.dont_write_bytecode = True
root, how, target = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, root)
try:
    if how == "module":
        importlib.import_module(target)
    else:
        import os
        path = os.path.join(root, target)
        spec = importlib.util.spec_from_file_location("_probe_target", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["_probe_target"] = mod
        spec.loader.exec_module(mod)
    print("OK")
except ModuleNotFoundError as e:
    print("MISSING " + str(e.name))
except BaseException as e:
    first = (str(e).splitlines() or [""])[0]
    print("ERROR " + type(e).__name__ + ": " + first[:160])
"""


def probe():
    rows = []
    for tool, rel, how, target in ENTRY_POINTS:
        root = FACTORY / rel
        out = subprocess.run([sys.executable, "-B", "-I", "-c", LOADER, str(root), how, target],
                             capture_output=True, text=True, timeout=120, cwd=str(FACTORY),
                             stdin=subprocess.DEVNULL)
        lines = [ln for ln in (out.stdout or "").splitlines() if ln.strip()]
        verdict = lines[-1] if lines else ("NO OUTPUT, exit %d: %s" % (
            out.returncode, (out.stderr or "").strip().splitlines()[-1:]))
        rows.append({"tool": tool, "target": target, "result": verdict})
    return rows


def main():
    rows = probe()
    head = {"interpreter": sys.executable, "version": sys.version.split()[0]}
    if "--json" in sys.argv:
        print(json.dumps({**head, "entry_points": rows}, indent=2))
        return
    print("interpreter %s (%s)" % (head["interpreter"], head["version"]))
    for r in rows:
        print("  %-14s %-46s %s" % (r["tool"], r["target"], r["result"]))


if __name__ == "__main__":
    main()
