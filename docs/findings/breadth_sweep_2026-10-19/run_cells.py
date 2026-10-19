"""Run edge_cells.gd on a copy of a package: copy it under the factory's _scratch/gate_ab/, import it once as the gate's
census would find it, ask the named cell pairs in both arms, keep the [cells] lines, delete the copy. A driver: it
prints what the probe printed and stops.

    python run_cells.py <package> <pairs.txt> <out.txt>
"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FACTORY = HERE.parents[2]
sys.path.insert(0, str(FACTORY / "level_factory"))
from packages.exporting import occluders  # noqa: E402

GODOT = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
pkg, pairs, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
copy = FACTORY / "_scratch" / "gate_ab" / pkg.name
if copy.exists():
    shutil.rmtree(copy)
shutil.copytree(pkg, copy)
try:
    occluders.ensure_imported(copy, GODOT)
    shutil.copy2(HERE / "edge_cells.gd", copy / "edge_cells.gd")
    shutil.copy2(pairs, copy / "pairs.txt")
    run = subprocess.run([GODOT, "--headless", "--path", str(copy), "--script", "res://edge_cells.gd", "--",
                          "res://pairs.txt"], capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL)
    lines = [ln for ln in run.stdout.splitlines() if ln.startswith("[cells]")]
    if not lines:
        lines = ["[cells] NO OUTPUT; godot exit %s" % run.returncode] + run.stdout.splitlines()[-20:] \
            + run.stderr.splitlines()[-20:]
finally:
    shutil.rmtree(copy, ignore_errors=True)
out.write_text("package: %s\n" % pkg + "\n".join(lines) + "\n", encoding="utf-8")
print("%s: %d lines -> %s; copy deleted: %s" % (pkg.name, len(lines), out.name, not copy.exists()))
