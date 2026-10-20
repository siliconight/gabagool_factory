"""Level Factory's drop-edge gate -- measure, classify, assert, as export step 4.88 runs them -- on a copy of one
package through several instruments, and every edge row one has that another does not. A probe: prints what it
measured and stops. The breadth sweep's `gate_ab.py` (docs/findings/breadth_sweep_2026-10-19/), copied here with the
probe-body instrument's two new report keys printed (`too_narrow`, `stand_lift_m`) and each arm's whole report kept.

    python gate_ab.py <package> <out dir> <label>=<walkable_edge.gd> [<label>=<walkable_edge.gd> ...]

The first arm is the reference: each other arm's rows are compared with it, and with the arm before. The first
version of this script took two instruments as `<old> <new> <out dir>` and wrote gate_ab_columns_only/; its "new"
arm was the columns-only build of Level Factory 0.219.0 (sha256 ea549226f34d577c).

The gate writes its report and scan into the package it measures, so this measures a copy: made under the factory's
_scratch/gate_ab/, imported once (the cache both arms then share, as the export's census has the bake's), measured
by each instrument in turn, and deleted. The package's own scan -- the record its export wrote -- is printed first:
the old arm reproducing it is the control that this harness runs what the export ran.

Frame: edge rows are the instrument's (Godot metres, site space; x, z the midpoint of two cells; y the cell's
surface). Rows are compared by (x, y, z, drop_m, indoors, on, to), owners by their path's last two parts.
"""
import json
import shutil
import sys
import time
from collections import Counter
from pathlib import Path

FACTORY = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(FACTORY / "level_factory"))
from packages.exporting import drop_edges as D  # noqa: E402
from packages.exporting import occluders  # noqa: E402

GODOT = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
#: Left out of the report kept per arm: the rows (kept apart, in `_rows.json`) and the per-owner tables, which are
#: most of a report's bytes and which `table.py` does not read. Applied to the files of 2026-10-20's run after it.
SLIM_OUT = ("edges", "owners", "standable_by_owner", "reachable_by_owner")
REPORT_KEYS = ("standable_cells", "reachable_cells", "occupied_surfaces", "steep_surfaces", "occupied_next",
               "drop_edges", "guarded", "blocked", "too_narrow", "unguarded", "unguarded_indoors", "links_used",
               "links_unresolved", "stand_lift_m")

pkg = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
arms = [(a.split("=", 1)[0], Path(a.split("=", 1)[1]).resolve()) for a in sys.argv[3:]]
assert len(arms) >= 2 and all("=" in a for a in sys.argv[3:]), "arms are <label>=<walkable_edge.gd>, two or more"
out.mkdir(parents=True, exist_ok=True)
name = pkg.name.replace(".portable-godot", "")
lines = []


def say(s=""):
    print(s, flush=True)
    lines.append(s)


def rows(rep):
    owners = rep.get("owners") or []
    return Counter((float(e["x"]), float(e["y"]), float(e["z"]), float(e["drop_m"]), bool(e.get("indoors")),
                    D._tail(owners, e.get("on")), D._tail(owners, e.get("to"))) for e in rep["edges"])


say("package: %s" % pkg)
rec = pkg / D.SCAN_NAME
if rec.is_file():
    r = json.loads(rec.read_text(encoding="utf-8"))
    say("the export's own scan: reachable %s of %s standable, unguarded %s, counts %s"
        % (r.get("reachable_cells"), r.get("standable_cells"), r.get("unguarded"), r.get("counts")))
else:
    say("the export's own scan: NONE at %s" % rec)
copy = FACTORY / "_scratch" / "gate_ab" / pkg.name
if copy.exists():
    shutil.rmtree(copy)
t = time.time()
shutil.copytree(pkg, copy)
say("copied in %.0f s; cache in the copy: %s" % (time.time() - t, (copy / occluders.CACHE_DIR).is_dir()))
t = time.time()
ran = occluders.ensure_imported(copy, GODOT)
say("import: %s, %.0f s" % ("ran" if ran else "not needed", time.time() - t))
got = {}
try:
    for label, script in arms:
        t = time.time()
        rep = D.measure(copy, GODOT, script=script)
        scan = D.classify(rep, copy)
        try:
            D.assert_declared(copy, scan)
            verdict = "PASSES"
        except D.UndeclaredDropError as exc:
            verdict = "REFUSES -- " + str(exc).splitlines()[0]
        got[label] = (rep, scan)
        (out / ("%s_%s_scan.json" % (name, label))).write_text(json.dumps(scan, indent=2, sort_keys=True),
                                                               encoding="utf-8")
        (out / ("%s_%s_report.json" % (name, label))).write_text(
            json.dumps({k: v for k, v in rep.items() if k not in SLIM_OUT}, indent=1, sort_keys=True), encoding="utf-8")
        (out / ("%s_%s_rows.json" % (name, label))).write_text(
            json.dumps(sorted(list(k) + [n] for k, n in rows(rep).items()), indent=0), encoding="utf-8")
        say("%s arm (%s): %.0f s" % (label, script.name, time.time() - t))
        say("   " + ", ".join("%s %s" % (k, rep.get(k)) for k in REPORT_KEYS))
        say("   counts %s" % scan["counts"])
        say("   verdict: " + verdict)
        for u in scan["undeclared"][:8]:
            say("   undeclared (%.2f, %.2f, %.2f) drop %.2f on %s to %s"
                % (u["x"], u["y"], u["z"], u["drop_m"], u["on"], u["to"]))
finally:
    shutil.rmtree(copy, ignore_errors=True)
    say("copy deleted: %s" % (not copy.exists()))
labels = [lb for lb, _ in arms if lb in got]
pairs = [(labels[0], lb) for lb in labels[1:]] + [(labels[i - 1], labels[i]) for i in range(2, len(labels))]
for la, lb in pairs:
    a, b = rows(got[la][0]), rows(got[lb][0])
    gone, came = a - b, b - a
    say("edge rows %s -> %s: %d -> %d; only in %s %d, only in %s %d"
        % (la, lb, sum(a.values()), sum(b.values()), la, sum(gone.values()), lb, sum(came.values())))
    for tag, c in (("only in " + la, gone), ("only in " + lb, came)):
        for k in sorted(c)[:60]:
            say("   %s: (%.2f, %.2f, %.2f) drop %.2f indoors %s on %s to %s x%d" % ((tag,) + k + (c[k],)))
        if len(c) > 60:
            say("   %s: ... %d more" % (tag, len(c) - 60))
(out / ("%s_ab.out.txt" % name)).write_text("\n".join(lines) + "\n", encoding="utf-8")
