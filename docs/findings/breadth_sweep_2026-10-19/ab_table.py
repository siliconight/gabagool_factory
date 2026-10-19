"""The three-arm A/B as one table: each package's gate verdict and counts under Level Factory 0.218.2 ("old"), the
first build of 0.219.0 ("columns") and the final ("lattice"), read off gate_ab/<name>_<arm>_scan.json and
gate_ab/<name>_<arm>_rows.json, with the rows each arm has that the old one does not. A reader: it prints what the
files say and stops; a file missing or of another shape is named, never read as a zero.

    python ab_table.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent / "gate_ab"
RUNS = (("9328", "LF_precinct_yard_001"), ("9330", "LF_deli_001"), ("9331", "LF_convenience_001"),
        ("9332", "LF_gas_block_001"), ("9333", "LF_restaurant_row_001"), ("9334", "LF_county_hospital_001"))
ARMS = ("old", "columns", "lattice")
CLASSES = ("top", "outdoors", "stair_side", "declared_drop", "ladder_hole", "undeclared")


def load(name, arm, kind):
    p = HERE / ("%s_%s_%s.json" % (name, arm, kind))
    if not p.is_file():
        raise SystemExit("MISSING %s" % p.name)
    return json.loads(p.read_text(encoding="utf-8"))


def rows(name, arm):
    data = load(name, arm, "rows")
    if not isinstance(data, list) or (data and len(data[0]) != 8):
        raise SystemExit("UNEXPECTED SHAPE %s_%s_rows.json" % (name, arm))
    return Counter({tuple(r[:7]): r[7] for r in data})


print("| run | mission | arm | verdict | reached / standable | unguarded | " + " | ".join(CLASSES)
      + " | rows not in old | rows only in old |")
print("|---" * (8 + len(CLASSES)) + "|")
for run, name in RUNS:
    base = rows(name, "old")
    for arm in ARMS:
        s = load(name, arm, "scan")
        c = s.get("counts")
        if not isinstance(c, dict) or any(k not in c for k in CLASSES):
            raise SystemExit("UNEXPECTED SHAPE %s_%s_scan.json counts %r" % (name, arm, c))
        r = rows(name, arm)
        verdict = "REFUSES" if c["undeclared"] else "passes"
        print("| %s | %s | %s | %s | %s / %s | %s | %s | %d | %d |" % (
            run, name.replace("LF_", ""), arm, verdict, s.get("reachable_cells"), s.get("standable_cells"),
            s.get("unguarded"), " | ".join(str(c[k]) for k in CLASSES),
            sum((r - base).values()), sum((base - r).values())))
sys.exit(0)
