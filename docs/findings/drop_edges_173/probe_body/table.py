"""The probe-body A/B as one table: each package, each lattice phase, the instrument before (Level Factory 0.221.0) and
after (the probe that models the body), off the scans and reports `gate_ab.py` kept in `gate_ab/`. A probe: prints and
stops. An arm whose scan or report is missing, or whose shape is not the gate's, FAILS rather than reading as empty.

    python table.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
AB = HERE / "gate_ab"
PHASES = ("p00", "p11", "p22", "p33", "p20", "p02")
PACKAGES = ("LF_precinct_yard_001", "LF_urban_row_001", "LF_deli_001")


def load(name, label):
    scan_p = AB / ("%s_%s_scan.json" % (name, label))
    rep_p = AB / ("%s_%s_report.json" % (name, label))
    scan, rep = json.loads(scan_p.read_text(encoding="utf-8")), json.loads(rep_p.read_text(encoding="utf-8"))
    if "counts" not in scan or "reachable_cells" not in rep:
        raise SystemExit("UNKNOWN SHAPE: %s / %s" % (scan_p.name, rep_p.name))
    return scan, rep


found = sorted({p.name.split("_old_")[0] for p in AB.glob("*_old_p00_scan.json")})
if not found:
    raise SystemExit("no scans under %s" % AB)
print("%-22s %-5s %-4s %-17s %-8s %-8s %-6s %-10s %s" % ("package", "phase", "arm", "reached/standable", "unguard",
                                                           "narrow", "undecl", "verdict", "counts"))
totals = {"old": [0, 0], "new": [0, 0]}
for name in found:
    for ph in PHASES:
        for arm in ("old", "new"):
            label = "%s_%s" % (arm, ph)
            try:
                scan, rep = load(name, label)
            except FileNotFoundError as exc:
                raise SystemExit("MISSING: %s" % exc)
            und = int(scan["counts"].get("undeclared", 0))
            totals[arm][0] += 1
            totals[arm][1] += und > 0
            print("%-22s %-5s %-4s %-17s %-8s %-8s %-6s %-10s %s" % (
                name.replace(".portable-godot", ""), ph, arm,
                "%s/%s" % (rep["reachable_cells"], rep["standable_cells"]), rep.get("unguarded"),
                rep.get("too_narrow", "-"), und, "REFUSES" if und else "passes",
                {k: v for k, v in scan["counts"].items() if v}))
print("[table] refusing arms: old %d of %d, new %d of %d" % (totals["old"][1], totals["old"][0],
                                                              totals["new"][1], totals["new"][0]))
