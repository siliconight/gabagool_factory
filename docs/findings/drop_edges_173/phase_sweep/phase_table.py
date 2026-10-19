"""The phase sweep as one table: each package's gate verdict and counts at each lattice phase, read off
gate_ab/<name>_<phase>_scan.json, and every undeclared row a phase finds. A reader: it prints what the files say and
stops; a file missing or of another shape is named, never read as a zero.

    python phase_table.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent / "gate_ab"
RUNS = (("9335", "LF_restaurant_row_001"), ("9332", "LF_gas_block_001"), ("9334", "LF_county_hospital_001"))
PHASES = (("p00", "0.0031, 0.0023"), ("p11", "0.1281, 0.1273"), ("p22", "0.2531, 0.2523"),
          ("p33", "0.3781, 0.3773"), ("p20", "0.2531, 0.0023"), ("p02", "0.0031, 0.2523"))
CLASSES = ("top", "outdoors", "stair_side", "declared_drop", "ladder_hole", "undeclared")


def scan(name, phase):
    p = HERE / ("%s_%s_scan.json" % (name, phase))
    if not p.is_file():
        raise SystemExit("MISSING %s" % p.name)
    s = json.loads(p.read_text(encoding="utf-8"))
    c = s.get("counts")
    if not isinstance(c, dict) or any(k not in c for k in CLASSES):
        raise SystemExit("UNEXPECTED SHAPE %s counts %r" % (p.name, c))
    return s


print("| run | mission | phase (dx, dz) m | verdict | reached / standable | unguarded | " + " | ".join(CLASSES) + " |")
print("|---" * (6 + len(CLASSES)) + "|")
found = []
for run, name in RUNS:
    for ph, off in PHASES:
        s = scan(name, ph)
        c = s["counts"]
        print("| %s | %s | %s | %s | %s / %s | %s | %s |" % (
            run, name.replace("LF_", ""), off, "REFUSES" if c["undeclared"] else "passes",
            s.get("reachable_cells"), s.get("standable_cells"), s.get("unguarded"),
            " | ".join(str(c[k]) for k in CLASSES)))
        for u in s.get("undeclared") or []:
            found.append((run, ph, u))
print()
print("undeclared rows at any phase: %d" % len(found))
for run, ph, u in found:
    print("  %s %s (%.2f, %.2f, %.2f) drop %.2f on %s to %s" % (run, ph, u["x"], u["y"], u["z"], u["drop_m"],
                                                               u["on"], u["to"]))
