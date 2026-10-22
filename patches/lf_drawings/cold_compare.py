"""Cold run 9377 (Deli Counter 0.257.0, Level Factory 0.232.0) against cold run 9376, on what it touched: the
factory's roadmap 296.

The two tools draw each building into its package and index a level's buildings at its package's root -- files a
game reads, never scene content -- so the run should be 9376's in everything else:

- each Laser Tag candidate's staged `mission_scenario.tres`, byte for byte;
- the validation record (`.level_factory/validation/<mission>.json`), finding by finding by code, candidate and
  message;
- the export's light bake, its models and users.

9376's scenarios and record are read from copies taken before this run (argv[1], a folder holding
`validation_9376.json` and `seed_<n>.mission_scenario.tres`). Prints what it compared; writes `cold_compare.out.txt`
beside this file. A file missing on either side is a refusal, not a match. Copied from
`patches/dc_desk_move/cold_compare.py`, its runs, versions and docstring changed. What the package carries is
`package_check.py`'s.

    python patches/lf_drawings/cold_compare.py <copies of 9376's>
"""
import collections
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
F = HERE.parents[1]
OLD, NEW, MISSION = "9376", "9377", "restaurant_row_001"
KEPT = pathlib.Path(sys.argv[1])
lines = ["== cold run %s (Deli Counter 0.257.0, Level Factory 0.232.0) against %s, %s" % (NEW, OLD, MISSION)]
ws_new = F / "workspaces" / ("cold-%s-ws" % NEW) / ".level_factory"

new_tres = sorted(ws_new.glob("staging/%s.laser_tag_evaluate.*/mission_scenario.tres" % MISSION))
old_tres = sorted(KEPT.glob("seed_*.mission_scenario.tres"))
if not old_tres or [p.parent.name.rsplit(".", 1)[-1] for p in new_tres] != [p.name.split(".")[0] for p in old_tres]:
    sys.exit("REFUSED: the two runs do not stage the same Laser Tag candidates: %s against %s"
             % ([p.parent.name for p in new_tres], [p.name for p in old_tres]))
for a, b in zip(old_tres, new_tres):
    same = a.read_bytes() == b.read_bytes()
    lines.append("mission_scenario.tres %s: %d bytes against %d, %s" % (a.name.split(".")[0], a.stat().st_size,
                                                                       b.stat().st_size,
                                                                       "identical" if same else "DIFFERENT"))
    eyes = [l for l in b.read_text(encoding="utf-8").splitlines() if "eye_height_m" in l or "aim_height_m" in l]
    lines.append("    %s: %s" % (NEW, "; ".join(eyes)))

records = {}
for run, p in ((OLD, KEPT / "validation_9376.json"), (NEW, ws_new / "validation" / ("%s.json" % MISSION))):
    if not p.is_file():
        sys.exit("REFUSED: no validation record for cold run %s at %s" % (run, p))
    issues = json.loads(p.read_text(encoding="utf-8")).get("issues")
    if not isinstance(issues, list):
        sys.exit("REFUSED: %s has no issues list" % p)
    records[run] = issues
key = lambda i: (i.get("code"), i.get("candidate_id"), i.get("message"))  # noqa: E731
for run in (OLD, NEW):
    lines.append("cold %s: %d findings" % (run, len(records[run])))
a, b = collections.Counter(map(key, records[OLD])), collections.Counter(map(key, records[NEW]))
lines.append("findings identical by code, candidate and message: %s (only %s: %d, only %s: %d)"
             % (a == b, OLD, sum((a - b).values()), NEW, sum((b - a).values())))
for run, only in ((OLD, a - b), (NEW, b - a)):
    for k in list(only.elements())[:12]:
        lines.append("  only %s: %s %s %s" % (run, k[0], k[1], str(k[2])[:140]))
BAKE = re.compile(r"light bake: (\d+) model\(s\) and (\d+) primitive mesh\(es\) lightmapped.*?; (\d+) users")
for run in (OLD, NEW):
    p = F / "docs" / "cold_runs" / ("cold_%s" % run) / "export.log"
    m = BAKE.search(p.read_text(encoding="utf-8", errors="replace")) if p.is_file() else None
    if not m:
        sys.exit("REFUSED: no light-bake line in %s" % p)
    lines.append("cold %s's bake: %s models and %s primitive meshes lightmapped, %s users" % ((run,) + m.groups()))
txt = "\n".join(lines) + "\n"
(HERE / "cold_compare.out.txt").write_text(txt, encoding="utf-8", newline="\n")
print(txt)
