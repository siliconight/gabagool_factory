"""The control for pricing cold run 9263's wires: a COPY of its package with every wire node hidden.

    python docs/cold_runs/cold_9263/wires_off.py <package copy under _scratch/>

Lot 0.119.0 stands one MeshInstance3D a 32 m cell, `site_wires_c<x>_<y>`, each with its OBJ beside
the scene. This writes `visible = false` under each node's header: a hidden node is never submitted,
so the copy draws everything the package draws except the wires, from the same files and the same
bake. A package carries the nodes in TWO scenes: the content scene `site.tscn` that Lot wrote, and
`presentation/lux.applied.tscn`, Lux's re-save of it -- the one `mission.tscn` loads, through
`bake.tscn`. Every scene holding a wire node must hold exactly one for each `site_wires_*.obj`, and the
scene `bake.tscn` instances must be one of them; nothing is written until all of that holds. It
refuses a path that is not under `_scratch/` -- the run's own package is the record.

FIRST VERSION, KEPT: it checked one node per OBJ over all scenes together, found 14 for 7 (the two
scenes above) and refused -- after it had already written both scenes of the copy. The copy was
scratch and is re-made by `wires_price.sh`; this one checks every scene before it writes any.
"""
import pathlib
import re
import sys

HEAD = re.compile(r'^\[node name="(site_wires_c\d{3}_\d{3})" type="MeshInstance3D"[^\]]*\]$')
LOADED = re.compile(r'^\[ext_resource type="PackedScene" path="res://([^"]+)" id="site"\]$', re.M)


def main():
    copy = pathlib.Path(sys.argv[1]).resolve()
    if "_scratch" not in copy.parts:
        sys.exit("refusing: %s is not a copy under _scratch/" % copy)
    objs = sorted(p.stem for p in copy.rglob("site_wires_*.obj"))
    if not objs:
        sys.exit("NOTHING TO HIDE: no site_wires_*.obj under %s" % copy)
    loaded = LOADED.findall((copy / "bake.tscn").read_text(encoding="utf-8"))
    if len(loaded) != 1:
        sys.exit("UNKNOWN SHAPE: bake.tscn instances %d site scene(s): %r" % (len(loaded), loaded))
    loaded = loaded[0]
    plans = {}
    for scene in sorted(copy.rglob("*.tscn")):
        raw = scene.read_bytes()
        if b"site_wires_c" not in raw:
            continue
        eol = b"\r\n" if b"\r\n" in raw else b"\n"
        lines = raw.decode("utf-8").replace("\r\n", "\n").split("\n")
        out, here = [], []
        for i, line in enumerate(lines):
            out.append(line)
            m = HEAD.match(line)
            if m:
                if i + 1 < len(lines) and lines[i + 1].strip() == "visible = false":
                    sys.exit("ALREADY HIDDEN: %s in %s" % (m.group(1), scene))
                out.append("visible = false")
                here.append(m.group(1))
        rel = scene.relative_to(copy).as_posix()
        if sorted(here) != objs:
            sys.exit("MISMATCH in %s: %d wire OBJs, %d nodes %s" % (rel, len(objs), len(here), sorted(here)))
        plans[rel] = (scene, "\n".join(out).encode("utf-8").replace(b"\n", eol), here)
    if loaded not in plans:
        sys.exit("THE LOADED SCENE HOLDS NO WIRES: bake.tscn instances %s; wires in %s" % (loaded, sorted(plans)))
    # every check passed: now write
    for rel, (scene, data, here) in sorted(plans.items()):
        scene.write_bytes(data)
        print("hidden %d wire node(s) in %s%s" % (len(here), rel, "  <- the scene bake.tscn instances"
                                                     if rel == loaded else ""))
    print("%d scene(s), one hidden node for each of %d site_wires_*.obj in each" % (len(plans), len(objs)))


if __name__ == "__main__":
    main()
