"""Run Level Factory 0.216.0's drop-edge gate -- measure, classify, write, assert -- on a copy of a package,
the way export_mission does at step 4.88, and print what it decided. A probe: prints and stops.

    python gate_probe.py <package copy> <out.txt>
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "level_factory"))
from packages.exporting import drop_edges as D  # noqa: E402

GODOT = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
pkg = Path(sys.argv[1])
lines = []


def say(s):
    print(s)
    lines.append(s)


say("package: %s" % pkg)
say("cache before: %s" % (pkg / ".godot").exists())
say("extent the gate passes: %r" % D.extent_from_hints(pkg))
say("seed: %r" % (D.seed_from_anchors(pkg),))
t = time.time()
rep = D.measure(pkg, GODOT)
say("measure: %.1f s, schema %s, extent %s, standable %s, reachable %s, unguarded %s, links used %s unresolved %s"
    % (time.time() - t, rep["schema"], rep.get("extent"), rep["standable_cells"], rep["reachable_cells"],
       rep["unguarded"], rep.get("links_used"), rep.get("links_unresolved")))
say("cache after: %s; instrument left behind: %s" % ((pkg / ".godot").exists(), (pkg / "walkable_edge.gd").exists()))
scan = D.classify(rep, pkg)
D.write_scan(pkg, scan)
say("summary: " + D.summary(scan))
say("links read: %r" % (scan["links"],))
for r in scan["undeclared"]:
    say("  undeclared (%.2f, %.2f, %.2f) drop %.2f on %s to %s" % (r["x"], r["y"], r["z"], r["drop_m"], r["on"], r["to"]))
try:
    D.assert_declared(pkg, scan)
    say("assert_declared: PASSES")
except D.UndeclaredDropError as exc:
    say("assert_declared: REFUSES -- " + str(exc).splitlines()[0])
Path(sys.argv[2]).write_text("\n".join(lines) + "\n", encoding="utf-8")
