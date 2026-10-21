"""Run `merge_drop_census.gd` over an unmerged package's placed buildings (the factory's install test 11's walk).

    python docs/findings/merge_ladders_227/run_census.py <unmerged package> <godot> [--out FILE]

Lists the buildings the site places as Level Factory's building merge does (`placed_buildings`), imports the package
as the merge does (`ensure_imported`), copies the census into the package for the run and removes it after. Prints
what the census printed and stops. `--out` defaults to `census.json` beside this file.
"""
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
FACTORY = HERE.parents[2]
sys.path.insert(0, str(FACTORY / "level_factory"))

from packages.exporting.merge_buildings import placed_buildings  # noqa: E402
from packages.exporting.occluders import ensure_imported  # noqa: E402

args = [a for a in sys.argv[1:] if not a.startswith("--out")]
out = HERE / "census.json"
for a in sys.argv[1:]:
    if a.startswith("--out="):
        out = pathlib.Path(a.split("=", 1)[1]).resolve()
package, godot = pathlib.Path(args[0]).resolve(), args[1]
scenes = list(placed_buildings(package))
print("placed buildings:", len(scenes))
ensure_imported(package, godot)
census = package / "merge_drop_census.gd"
census.write_bytes((HERE / "merge_drop_census.gd").read_bytes())
try:
    r = subprocess.run([godot, "--headless", "--path", str(package), "--script", "res://merge_drop_census.gd",
                        "--", str(out), *scenes], capture_output=True, text=True, timeout=1800)
finally:
    census.unlink(missing_ok=True)
for line in r.stdout.splitlines():
    if line.startswith("[census]"):
        print(line)
print("godot exit", r.returncode, "->", out)
