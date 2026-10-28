"""Price Zoo 1.143.0 + Deli Counter 0.287.0-0.287.1 (a vault rack blue painted steel and open-backed, its bricks pale;
a bank vault's money racks in rows): draw calls and frame time at fixed stations.

    python docs/findings/bank_interior/price_rows.py

ARMS, all in one session with nothing else running (`docs/COMMANDS.md`, "Nothing else runs beside a price"):
  control_a, control_b  `bank_block_001` at seed 9082 on Zoo 1.142.0, Deli Counter 0.286.1, Lot 0.135.0 and Level Factory 0.262.0
                        (`workspaces/bank-rack-ws`), twice: the same bytes, so their difference is the
                        instrument's floor
  subject               the same mission and seed made on Zoo 1.143.0 and Deli Counter 0.287.1, Level Factory
                        0.263.0, every other tool the same (`workspaces/bank-rows-ws`)

Each arm is a fresh copy of the package with its import cache removed, imported headless, then run through Level
Factory's fixed-station harness (`level_factory/tools/perf_stations_run.py`, the stations the package's own anchors
give). Each copy is deleted once measured (about 250 MB each). Reports land beside this file as
`perf_rows_<arm>.json`; prints each arm's summary and draws no conclusion. Copied from `price_rack.py` beside it; the
arms and the reports' names changed.
"""
import pathlib
import shutil
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
F = HERE.parents[2]
GODOT = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
WORK = F / "_scratch" / "price_bank_rows" / "perf"
PKG = "LF_bank_block_001.portable-godot"
CONTROL = F / "workspaces" / "bank-rack-ws" / ".level_factory" / "exports" / PKG
SUBJECT = F / "workspaces" / "bank-rows-ws" / ".level_factory" / "exports" / PKG
ARMS = [("control_a", CONTROL), ("subject", SUBJECT), ("control_b", CONTROL)]

for tag, pkg in ARMS:
    assert pkg.is_dir(), pkg
    dst = WORK / tag
    t0 = time.monotonic()
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(pkg, dst)
    t1 = time.monotonic()
    shutil.rmtree(dst / ".godot", ignore_errors=True)
    r = subprocess.run([GODOT, "--headless", "--path", str(dst), "--import"], capture_output=True, text=True,
                       timeout=1800)
    t2 = time.monotonic()
    print(tag, "import", r.returncode, flush=True)
    r = subprocess.run([sys.executable, str(F / "level_factory" / "tools" / "perf_stations_run.py"), str(dst),
                        "--json", str(HERE / ("perf_rows_%s.json" % tag))],
                       capture_output=True, text=True, timeout=3600, cwd=str(F / "level_factory"))
    t3 = time.monotonic()
    print(tag, "perf", r.returncode, "-- copy %.0f s, import %.0f s, harness %.0f s" % (t1 - t0, t2 - t1, t3 - t2), flush=True)
    print(r.stdout[-1800:], flush=True)
    if r.returncode not in (0, 1):
        print(r.stderr[-800:], flush=True)
    shutil.rmtree(dst, ignore_errors=True)
