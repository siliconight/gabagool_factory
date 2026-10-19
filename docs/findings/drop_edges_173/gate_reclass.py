"""Re-class the gate probe's own report (the instrument's run inside the gate, on 9318's package) with Level
Factory's drop-edge module (0.216.0, the shaft rule): (a) the package as it is, (b) with deli_a01's floor-hole drop link added as Deli
Counter 0.226.0 records it and Lot 0.125.0 moves it (building -> site: a translation by (-51, +2.51), read off
the package's two ladder links against the building's own ladders). A probe: prints and stops.

    python gate_reclass.py <package> <out.txt> [report.json]
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "level_factory"))
from packages.exporting import drop_edges as D  # noqa: E402

pkg = Path(sys.argv[1])
out = Path(sys.argv[2])
# the report: the package's own `drop_edges.json` by default, or one kept beside this file
# (`gate_9318_drop_edges.json` is the gate probe's, from a copy of 9318's package since deleted)
rep_path = Path(sys.argv[3]) if len(sys.argv) > 3 else pkg / "drop_edges.json"
rep = json.loads(rep_path.read_text(encoding="utf-8"))
lines = []


def say(s):
    print(s)
    lines.append(s)


scan = D.classify(rep, pkg)
say("(a) 9318's package as shipped: " + D.summary(scan))
say("    links read: %r" % (scan["links"],))
xs = sorted({(r["x"], r["z"]) for r in scan["undeclared"]})
say("    undeclared at x %.2f..%.2f, z %.2f..%.2f, y %s" % (min(p[0] for p in xs), max(p[0] for p in xs),
    min(p[1] for p in xs), max(p[1] for p in xs), sorted({r["y"] for r in scan["undeclared"]})))

# deli_a01's floor hole, building frame (deli_counter/build/deli_a01.gameplay.json, Deli Counter 0.226.0):
# start [8.0, -4.0, 3.3], hole [[6.9, -5.1], [9.1, -2.9]]; site = building + (-51, +2.51); Godot = (x, z, -y).
DX, DY = -51.0, 2.51
link = {"id": "lot:deli_a01_floor_hole_1_8_-4_navlink", "required_capability": "drop", "bidirectional": False,
        "start_position": [8.0 + DX, 3.3, -(-4.0 + DY)], "end_position": [8.0 + DX, 0.0, -(-4.0 + DY)],
        "hole": [[6.9 + DX, -5.1 + DY], [9.1 + DX, -2.9 + DY]]}
tmp = Path(tempfile.mkdtemp())
try:
    hints = json.loads((pkg / "navigation_hints.json").read_text(encoding="utf-8"))
    hints["links"] = list(hints.get("links") or []) + [link]
    (tmp / "navigation_hints.json").write_text(json.dumps(hints), encoding="utf-8")
    scan_b = D.classify(rep, tmp)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
say("(b) with the floor hole's drop link (start %r, hole %r): %s" % (link["start_position"], link["hole"],
                                                                     D.summary(scan_b)))
say("    links read: %r" % (scan_b["links"],))
try:
    D.assert_declared(pkg, scan_b)
    say("    assert_declared: PASSES")
except D.UndeclaredDropError as exc:
    say("    assert_declared: REFUSES -- " + str(exc).splitlines()[0])
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
