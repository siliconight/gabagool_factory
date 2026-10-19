"""Where the flood stops: on a copy of a package, Level Factory 0.219.0's drop-edge instrument at two lattice phases,
each made to dump every surface it found -- position, height, owner, free, reached -- and the cells one phase reaches
that the other does not, grouped into regions, with the frontier where the second phase's flood stopped beside them. A
probe: the dump is a variant of the instrument made here and never shipped; prints what it measured and stops.

    python reach_dump.py <package> <out dir> <label=dx,dz> <label=dx,dz>

The copy is made under the factory's _scratch/reach_dump/, imported once, and deleted. A cell of the first phase is
matched to the second's nearest cell within half a cell horizontally and LEVEL_TOL vertically. Regions are 4-connected
on the first phase's lattice. A frontier cell is a free surface the second phase found and did not reach, beside one
it did reach. Frame: Godot metres, site space.
"""
import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
FACTORY = HERE.parents[3]
sys.path.insert(0, str(FACTORY / "level_factory"))
from packages.exporting import drop_edges as D  # noqa: E402
from packages.exporting import occluders  # noqa: E402

GODOT = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
ANCHOR = '\treport["reachable_cells"] = reached\n'
DUMP = ANCHOR + (
    '\t# REACH DUMP (a probe variant of this instrument, never shipped): every surface\n'
    '\tvar dump: Array = []\n'
    '\tfor ix in range(nx):\n'
    '\t\tfor iz in range(nz):\n'
    '\t\t\tfor h in cols[ix * nz + iz]:\n'
    '\t\t\t\tdump.append([snappedf(box.position.x + float(ix) * cell, 0.0001),\n'
    '\t\t\t\t\tsnappedf(box.position.z + float(iz) * cell, 0.0001), snappedf(float(h[0]), 0.001),\n'
    '\t\t\t\t\tint(h[1]), 1 if h[2] else 0, 1 if h[3] else 0])\n'
    '\treport["surface_dump"] = dump\n')

pkg, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
arms = []
for a in sys.argv[3:5]:
    label, d = a.split("=", 1)
    arms.append((label,) + tuple(float(v) for v in d.split(",")))
assert len(arms) == 2, "name two arms"
out.mkdir(parents=True, exist_ok=True)
name = pkg.name.replace(".portable-godot", "")
src = D.EDGE_SCRIPT.read_bytes().decode("utf-8")
assert src.count(ANCHOR) == 1, "the instrument's reach line moved"
work = FACTORY / "_scratch" / "reach_dump"
copy = work / pkg.name
if copy.exists():
    shutil.rmtree(copy)
work.mkdir(parents=True, exist_ok=True)
lines = []


def say(s=""):
    print(s, flush=True)
    lines.append(s)


def variant(label, dx, dz):
    t = src.replace(ANCHOR, DUMP)
    for const, val in (("SEAM_NUDGE_X", dx), ("SEAM_NUDGE_Z", dz)):
        old = "const %s := " % const
        hit = [ln for ln in t.split("\n") if ln.startswith(old)]
        assert len(hit) == 1, (const, len(hit))
        t = t.replace(hit[0], "%s%r" % (old, val))
    p = work / ("walkable_edge_dump_%s.gd" % label)
    p.write_bytes(t.encode("utf-8"))
    return p


shutil.copytree(pkg, copy)
dumps = {}
try:
    occluders.ensure_imported(copy, GODOT)
    for label, dx, dz in arms:
        rep = D.measure(copy, GODOT, script=variant(label, dx, dz))
        dump = rep.get("surface_dump")
        assert isinstance(dump, list) and dump and len(dump[0]) == 6, "the dump is not the shape this reads"
        owners = rep.get("owners") or []
        dumps[label] = (dump, owners, rep)
        (out / ("%s_%s_surfaces.json" % (name, label))).write_text(
            json.dumps({"owners": owners, "cell_m": rep.get("cell_m"), "lattice_offset_m": rep.get("lattice_offset_m"),
                        "surfaces": dump}, separators=(",", ":")), encoding="utf-8")
        say("%s: %d surfaces, %d free, %d reached (the report says %s)" % (
            label, len(dump), sum(r[4] for r in dump), sum(r[5] for r in dump), rep.get("reachable_cells")))
finally:
    shutil.rmtree(copy, ignore_errors=True)
    say("copy deleted: %s" % (not copy.exists()))

(a_lab, a_dx, a_dz), (b_lab, b_dx, b_dz) = arms
a_dump, a_own, a_rep = dumps[a_lab]
b_dump, b_own, b_rep = dumps[b_lab]
cell = float(a_rep.get("cell_m"))
bucket = defaultdict(list)
for r in b_dump:
    bucket[(round((r[0] - b_dx) / cell), round((r[1] - b_dz) / cell))].append(r)


def match(r):
    """b's surface nearest r: within half a cell horizontally and LEVEL_TOL vertically, or None."""
    k = (round((r[0] - a_dx) / cell), round((r[1] - a_dz) / cell))
    best, bd = None, 1e9
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            for s in bucket.get((k[0] + di, k[1] + dj), ()):
                if abs(s[0] - r[0]) <= cell / 2 + 1e-6 and abs(s[1] - r[1]) <= cell / 2 + 1e-6 \
                        and abs(s[2] - r[2]) <= D.LEVEL_TOL:
                    d = abs(s[0] - r[0]) + abs(s[1] - r[1]) + abs(s[2] - r[2])
                    if d < bd:
                        best, bd = s, d
    return best


lost = [r for r in a_dump if r[5] and r[4] and not ((m := match(r)) and m[5])]
say("%s reaches and %s does not: %d surfaces" % (a_lab, b_lab, len(lost)))
key = {(round((r[0] - a_dx) / cell), round((r[1] - a_dz) / cell), round(r[2], 1)): r for r in lost}
seen, regions = set(), []
for k0 in key:
    if k0 in seen:
        continue
    stack, reg = [k0], []
    seen.add(k0)
    while stack:
        k = stack.pop()
        reg.append(key[k])
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for dy in (-0.1, 0.0, 0.1):
                n = (k[0] + di, k[1] + dj, round(k[2] + dy, 1))
                if n in key and n not in seen:
                    seen.add(n)
                    stack.append(n)
    regions.append(reg)
regions.sort(key=len, reverse=True)
b_free = {(round((s[0] - b_dx) / cell), round((s[1] - b_dz) / cell), round(s[2], 1)): s for s in b_dump if s[4]}
for reg in regions[:12]:
    xs, zs, ys = [r[0] for r in reg], [r[1] for r in reg], [r[2] for r in reg]
    by_owner = defaultdict(int)
    for r in reg:
        by_owner[D._tail(a_own, r[3])] += 1
    top = sorted(by_owner.items(), key=lambda kv: -kv[1])[:3]
    say("region of %d: x %.2f..%.2f, z %.2f..%.2f, y %.2f..%.2f; %s" % (
        len(reg), min(xs), max(xs), min(zs), max(zs), min(ys), max(ys), ", ".join("%s %d" % kv for kv in top)))
front = []
for k, s in b_free.items():
    if s[5]:
        continue
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        hit = False
        for dy in (-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
            n = b_free.get((k[0] + di, k[1] + dj, round(k[2] + dy, 1)))
            if n is not None and n[5]:
                hit = True
                break
        if hit:
            front.append(s)
            break
say("%s's free surfaces left unreached beside reached ones (its flood's frontier): %d" % (b_lab, len(front)))
for s in sorted(front, key=lambda s: (s[0], s[1]))[:40]:
    say("   frontier (%.4f, %.3f, %.4f) on %s" % (s[0], s[2], s[1], D._tail(b_own, s[3])))
(out / ("%s_reach.out.txt" % name)).write_text("\n".join(lines) + "\n", encoding="utf-8")
