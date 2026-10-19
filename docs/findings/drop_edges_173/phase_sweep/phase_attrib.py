"""Attribute the phase sweep's one false refusal and its reach loss: on a copy of a package, the drop-edge instrument
at named lattice phases (Level Factory 0.219.0's walkable_edge.gd with its two SEAM_NUDGE constants set), each full
report kept, the reached cells compared surface owner by owner, and edge_cells_at.gd asked the named cell pairs at
the same phases. A probe: prints what it measured and stops.

    python phase_attrib.py <package> <out dir> <pairs.txt> <label=dx,dz> [<label=dx,dz> ...]

The copy is made under the factory's _scratch/phase_attrib/, imported once, and deleted. Owners are compared by the
last two parts of their node path; a row prints when an owner's reached cells differ between the first arm and
another by more than 20. Frame: Godot metres, site space.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FACTORY = HERE.parents[3]
sys.path.insert(0, str(FACTORY / "level_factory"))
from packages.exporting import drop_edges as D  # noqa: E402
from packages.exporting import occluders  # noqa: E402

GODOT = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
pkg, out, pairs = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
arms = []
for a in sys.argv[4:]:
    label, d = a.split("=", 1)
    dx, dz = (float(v) for v in d.split(","))
    arms.append((label, dx, dz))
assert arms, "name at least one arm"
out.mkdir(parents=True, exist_ok=True)
name = pkg.name.replace(".portable-godot", "")
src = D.EDGE_SCRIPT.read_bytes().decode("utf-8")
work = FACTORY / "_scratch" / "phase_attrib"
copy = work / pkg.name
if copy.exists():
    shutil.rmtree(copy)
work.mkdir(parents=True, exist_ok=True)
lines = []


def say(s=""):
    print(s, flush=True)
    lines.append(s)


def variant(label, dx, dz):
    t = src
    for const, val in (("SEAM_NUDGE_X", dx), ("SEAM_NUDGE_Z", dz)):
        old = "const %s := " % const
        hit = [ln for ln in t.split("\n") if ln.startswith(old)]
        assert len(hit) == 1, (const, len(hit))
        t = t.replace(hit[0], "%s%r" % (old, val))
    p = work / ("walkable_edge_%s.gd" % label)
    p.write_bytes(t.encode("utf-8"))
    return p


def tails(rep):
    owners = rep.get("owners") or []
    return {D._tail(owners, int(k)): int(v) for k, v in (rep.get("reachable_by_owner") or {}).items()}


shutil.copytree(pkg, copy)
reports = {}
try:
    occluders.ensure_imported(copy, GODOT)
    for label, dx, dz in arms:
        rep = D.measure(copy, GODOT, script=variant(label, dx, dz))
        reports[label] = rep
        (out / ("%s_%s_report.json" % (name, label))).write_text(json.dumps(rep, indent=1, sort_keys=True),
                                                                 encoding="utf-8")
        say("%s (%r, %r): lattice_offset_m %s, reached %s of %s, unguarded %s" % (
            label, dx, dz, rep.get("lattice_offset_m"), rep.get("reachable_cells"), rep.get("standable_cells"),
            rep.get("unguarded")))
    shutil.copy2(HERE / "edge_cells_at.gd", copy / "edge_cells_at.gd")
    shutil.copy2(pairs, copy / "pairs.txt")
    run = subprocess.run([GODOT, "--headless", "--path", str(copy), "--script", "res://edge_cells_at.gd", "--",
                          "res://pairs.txt"] + ["%s=%r,%r" % a for a in arms],
                         capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL)
    cells = [ln for ln in run.stdout.splitlines() if ln.startswith("[cells]")]
    (out / ("%s_cells.out.txt" % name)).write_text("\n".join(cells) + "\n", encoding="utf-8")
    say("edge_cells_at.gd: %d lines -> %s_cells.out.txt (godot exit %s)" % (len(cells), name, run.returncode))
finally:
    shutil.rmtree(copy, ignore_errors=True)
    say("copy deleted: %s" % (not copy.exists()))
first = arms[0][0]
base = tails(reports[first])
for label, _, _ in arms[1:]:
    other = tails(reports[label])
    say("reached by owner, %s -> %s (owners differing by more than 20 cells):" % (first, label))
    for own in sorted(set(base) | set(other), key=lambda o: -abs(other.get(o, 0) - base.get(o, 0))):
        d = other.get(own, 0) - base.get(own, 0)
        if abs(d) > 20:
            say("   %-48s %7d -> %7d   %+d" % (own, base.get(own, 0), other.get(own, 0), d))
(out / ("%s_attrib.out.txt" % name)).write_text("\n".join(lines) + "\n", encoding="utf-8")
