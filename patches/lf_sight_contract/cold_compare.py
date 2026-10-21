"""Cold run 9373 (Level Factory 0.230.0) against cold run 9372 (0.229.0), on what 0.230.0 touched.

`run` now asks `_run_scenario` for the scenario keys it writes, and the advisory sights from the heights the run's
scenario carries -- the contract's body, read from the run's Deli Counter checkout. With the contract's stock body
both should leave a cold run exactly as it was:

- each Laser Tag candidate's staged `mission_scenario.tres`, byte for byte;
- the validation record (`.level_factory/validation/<mission>.json`), finding for finding by code, candidate and
  message, and the advisory's own codes counted on each side.

Prints what it compared; writes `cold_compare.out.txt` beside this file. A file missing on either side is a refusal,
not a match.

    python patches/lf_sight_contract/cold_compare.py
"""
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
F = HERE.parents[1]
OLD, NEW, MISSION = "9372", "9373", "restaurant_row_001"
lines = ["== cold run %s (Level Factory 0.230.0) against %s (0.229.0), %s" % (NEW, OLD, MISSION)]


def ws(run):
    return F / "workspaces" / ("cold-%s-ws" % run) / ".level_factory"


old_tres = sorted(ws(OLD).glob("staging/%s.laser_tag_evaluate.*/mission_scenario.tres" % MISSION))
new_tres = sorted(ws(NEW).glob("staging/%s.laser_tag_evaluate.*/mission_scenario.tres" % MISSION))
if not old_tres or [p.parent.name for p in old_tres] != [p.parent.name for p in new_tres]:
    sys.exit("REFUSED: the two runs do not stage the same Laser Tag candidates: %s against %s"
             % ([p.parent.name for p in old_tres], [p.parent.name for p in new_tres]))
for a, b in zip(old_tres, new_tres):
    same = a.read_bytes() == b.read_bytes()
    lines.append("mission_scenario.tres %s: %d bytes against %d, %s" % (a.parent.name.rsplit(".", 1)[-1],
                                                                       a.stat().st_size, b.stat().st_size,
                                                                       "identical" if same else "DIFFERENT"))
    if not same:
        diff = [(x, y) for x, y in zip(a.read_text(encoding="utf-8").splitlines(),
                                       b.read_text(encoding="utf-8").splitlines()) if x != y]
        lines += ["    %s  ->  %s" % d for d in diff[:10]]

records = {}
for run in (OLD, NEW):
    p = ws(run) / "validation" / ("%s.json" % MISSION)
    if not p.is_file():
        sys.exit("REFUSED: no validation record at %s" % p)
    issues = json.loads(p.read_text(encoding="utf-8")).get("issues")
    if not isinstance(issues, list):
        sys.exit("REFUSED: %s has no issues list" % p)
    records[run] = issues
key = lambda i: (i.get("code"), i.get("candidate_id"), i.get("message"))  # noqa: E731
for run in (OLD, NEW):
    lt = collections.Counter(i.get("code") for i in records[run] if i.get("source_tool") == "laser_tag"
                             and not str(i.get("code", "")).startswith("LT_MAP_"))
    lines.append("cold %s: %d findings; the Laser Tag advisory's: %s" % (run, len(records[run]), sorted(lt.items())))
a, b = collections.Counter(map(key, records[OLD])), collections.Counter(map(key, records[NEW]))
lines.append("findings identical by code, candidate and message: %s (only %s: %d, only %s: %d)"
             % (a == b, OLD, sum((a - b).values()), NEW, sum((b - a).values())))
for k in list((b - a).elements())[:10]:
    lines.append("  only %s: %s %s %s" % (NEW, k[0], k[1], str(k[2])[:120]))
txt = "\n".join(lines) + "\n"
(HERE / "cold_compare.out.txt").write_text(txt, encoding="utf-8", newline="\n")
print(txt)
