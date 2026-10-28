"""Price Deli Counter 0.282.0 + Zoo 1.136.0 (a bank's walls plastered inside, its cameras, plants and clock): draw calls
and frame time at fixed stations.

    python docs/findings/bank_interior/price_0282.py

ARMS, all in one session with nothing else running (`docs/COMMANDS.md`, "Nothing else runs beside a price"):
  control_a, control_b  `bank_block_001` at seed 9082 on Deli Counter 0.281.0 and Zoo 1.135.0
                        (`workspaces/bank-look-0281-ws`), twice: the same bytes, so their difference is the
                        instrument's floor
  subject               the same mission and seed made on Deli Counter 0.282.0 and Zoo 1.136.0, every other tool
                        the same (`workspaces/bank-look-0282-ws`)

Each arm is a fresh copy of the package with its import cache removed, imported headless, then run through Level
Factory's fixed-station harness (`level_factory/tools/perf_stations_run.py`, the stations the package's own anchors
give). Each copy is deleted once measured (about 250 MB each). Reports land beside this file as
`perf_0282_<arm>.json`; prints each arm's summary and draws no conclusion. Copied from `price.py` beside it; the arms
and the reports' names changed.
"""
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
F = HERE.parents[2]
GODOT = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
WORK = F / "_scratch" / "price_bank_0282" / "perf"
PKG = "LF_bank_block_001.portable-godot"
CONTROL = F / "workspaces" / "bank-look-0281-ws" / ".level_factory" / "exports" / PKG
SUBJECT = F / "workspaces" / "bank-look-0282-ws" / ".level_factory" / "exports" / PKG
ARMS = [("control_a", CONTROL), ("subject", SUBJECT), ("control_b", CONTROL)]

for tag, pkg in ARMS:
    assert pkg.is_dir(), pkg
    dst = WORK / tag
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(pkg, dst)
    shutil.rmtree(dst / ".godot", ignore_errors=True)
    r = subprocess.run([GODOT, "--headless", "--path", str(dst), "--import"], capture_output=True, text=True,
                       timeout=1800)
    print(tag, "import", r.returncode, flush=True)
    r = subprocess.run([sys.executable, str(F / "level_factory" / "tools" / "perf_stations_run.py"), str(dst),
                        "--json", str(HERE / ("perf_0282_%s.json" % tag))],
                       capture_output=True, text=True, timeout=3600, cwd=str(F / "level_factory"))
    print(tag, "perf", r.returncode, flush=True)
    print(r.stdout[-1800:], flush=True)
    if r.returncode not in (0, 1):
        print(r.stderr[-800:], flush=True)
    shutil.rmtree(dst, ignore_errors=True)
