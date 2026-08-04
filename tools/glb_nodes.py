"""Name what is inside a GLB: node families, counts, and where they sit.

WHAT THIS IS FOR. A baked layer arrives as ONE node in the scene -- `Dressing`,
`Fixtures` -- so every tool that reads scenes sees one box and every question
about what is actually in there ("what are these rods?", "why is this 2.85 m
below the floor?") has no instrument. This reads the glTF node list directly.

    python tools\\glb_nodes.py <file.glb> [--below Y] [--top N]

WHAT IT MEASURES, AND IN WHAT FRAME. The glTF's own space, which is **Y-UP** --
up is the SECOND component. Measured, not assumed, because the first draft of
this file assumed otherwise and would have tested a horizontal axis:

    cr_deli.glb   index[0]  -22.00 .. 19.00   span 41.00
                  index[1]   -3.45 ..  7.10   span 10.55   <- basement to roof
                  index[2]  -17.50 .. 18.00   span 35.50

`COORDINATE_CONTRACT.md` says the authoring space is Blender Z-up and that
conversion to Y-up happens "at the Godot import boundary". The first half is
true of the MANIFESTS -- `slots.json`, `gameplay.json`, `lights.json` are Z-up.
The second half is loose: the Blender glTF exporter converts on the way OUT, so
a GLB on disk is already Y-up and Godot converts nothing. Read a manifest as
Z-up and a GLB as Y-up, and do not trust one sentence to cover both.

Node translations are taken as authored -- local to each node's parent, not
composed down the hierarchy. For a baked prop layer the props are siblings under
one root and the two are the same.

`--below Y` lists every node whose translation is under Y, which is the "props
under the floor" question asked directly.

`--flat` lists every mesh node whose bounding box is DEGENERATE on one axis --
a plane rather than a solid. This is the "what is that white square I can only
see from one side?" question asked directly, and the reasoning is that a plane
answers it by construction: every box this pipeline builds is closed, so a
single-sided surface that vanishes when you walk around it cannot be a box. It
also flags OVERSIZE nodes, because the same accessor read is already done and a
mesh larger than the building it sits in is the other shape this bug takes.

WHAT A NONZERO EXIT MEANS. The file could not be read. It never reports an empty
node list as "nothing in there".
"""
import argparse
import collections
import json
import os
import re
import struct
import sys

GLB_MAGIC = 0x46546C67
CHUNK_JSON = 0x4E4F534A


class Unreadable(Exception):
    """The file could not be parsed. Not a finding about its contents."""


def gltf_json(path):
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) < 12:
        raise Unreadable(f"{path}: shorter than a GLB header")
    magic, _v, _t = struct.unpack_from("<III", data, 0)
    if magic != GLB_MAGIC:
        raise Unreadable(f"{path}: not a binary GLB")
    off = 12
    while off + 8 <= len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        if ctype == CHUNK_JSON:
            return json.loads(data[off + 8:off + 8 + clen].decode("utf-8"))
        off += 8 + clen + ((4 - clen % 4) % 4)
    raise Unreadable(f"{path}: no JSON chunk")


def family(name):
    """The stem of a node name, with trailing indices and dedup suffixes off.

    Blender dedupes repeats as `.001` and Godot's importer turns the dot into an
    underscore, so neither survives as a distinguishing part of a name.
    """
    stem = re.split(r"[.]", name or "")[0]
    return re.sub(r"[_-]?\d+$", "", stem) or "(unnamed)"


def node_boxes(doc):
    """[(name, (lo, hi))] per MESH node, in the node's own parent space.

    From the accessors' own ``min``/``max``, which the exporter is required to
    write for POSITION, so this needs no buffer decode and no mesh library.
    Node translation is added; rotation and scale are not composed -- a baked
    layer parents its parts as siblings with translation only, and a wrong
    answer under an unexpected hierarchy is better caught by the caller seeing
    an implausible number than by this pretending to a full transform stack.
    """
    acc = doc.get("accessors", [])
    meshes = doc.get("meshes", [])
    out = []
    for n in doc.get("nodes", []):
        mi = n.get("mesh")
        if mi is None or mi >= len(meshes):
            continue
        t = n.get("translation") or [0.0, 0.0, 0.0]
        lo = [float("inf")] * 3
        hi = [float("-inf")] * 3
        seen = False
        for prim in meshes[mi].get("primitives", []):
            ai = (prim.get("attributes") or {}).get("POSITION")
            if ai is None or ai >= len(acc):
                continue
            a = acc[ai]
            if not a.get("min") or not a.get("max"):
                continue
            seen = True
            for i in range(3):
                lo[i] = min(lo[i], float(a["min"][i]) + float(t[i]))
                hi[i] = max(hi[i], float(a["max"][i]) + float(t[i]))
        if seen:
            out.append((n.get("name") or "(unnamed)", (tuple(lo), tuple(hi))))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("glb")
    ap.add_argument("--below", type=float, default=None,
                    help="list nodes whose translation Y is under this (Y-up)")
    ap.add_argument("--flat", action="store_true",
                    help="list mesh nodes whose bbox is degenerate on one axis "
                         "(a plane, not a solid) or larger than --max-span. A "
                         "plane is the shape that is visible from one side and "
                         "gone from the other; no box this pipeline builds can "
                         "do that.")
    ap.add_argument("--flat-eps", type=float, default=0.002, metavar="M",
                    help="an axis span at or under this reads as degenerate "
                         "(default 0.002 -- thinner than any authored cover, "
                         "which bottoms out at 0.012)")
    ap.add_argument("--max-span", type=float, default=60.0, metavar="M",
                    help="report a mesh whose bbox exceeds this on any axis "
                         "(default 60, comfortably past a 44 x 32 m building)")
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    try:
        doc = gltf_json(args.glb)
    except (Unreadable, OSError, ValueError) as exc:
        sys.stderr.write(str(exc) + "\n")
        return 2

    nodes = doc.get("nodes", [])
    fams = collections.Counter()
    zs = collections.defaultdict(list)
    placed = 0
    for n in nodes:
        f = family(n.get("name", ""))
        fams[f] += 1
        t = n.get("translation")
        if t and len(t) >= 3:
            placed += 1
            zs[f].append(float(t[1]))

    if args.json:
        print(json.dumps({
            "file": os.path.basename(args.glb),
            "nodes": len(nodes),
            "families": {k: {"count": c,
                             "y_min": min(zs[k]) if zs.get(k) else None,
                             "y_max": max(zs[k]) if zs.get(k) else None}
                         for k, c in fams.items()},
        }, indent=2))
        return 0

    print("%s: %d nodes, %d with an explicit translation"
          % (os.path.basename(args.glb), len(nodes), placed))
    # --flat is a targeted question and is usually asked of every GLB in a
    # project at once, so it does not also dump the census -- 474 families
    # per file buries the two lines you came for.
    if not args.flat:
        print("(glTF space -- Y-UP, so up is the second component)")
        print()
        print("%6s  %-34s %9s %9s" % ("count", "family", "y_min", "y_max"))
        for f, c in fams.most_common(args.top):
            if zs.get(f):
                print("%6d  %-34s %9.2f %9.2f"
                      % (c, f[:34], min(zs[f]), max(zs[f])))
            else:
                print("%6d  %-34s %9s %9s" % (c, f[:34], "-", "-"))
        if len(fams) > args.top:
            print("  ... %d more famil(ies)" % (len(fams) - args.top))

    if args.below is not None:
        under = [(n.get("name", "?"), float(n["translation"][1]))
                 for n in nodes
                 if n.get("translation") and len(n["translation"]) >= 3
                 and float(n["translation"][1]) < args.below]
        print()
        print("BELOW y = %.2f: %d node(s)" % (args.below, len(under)))
        for name, z in sorted(under, key=lambda p: p[1])[:args.top]:
            print("   %8.2f  %s" % (z, name))

    if args.flat:
        boxes = node_boxes(doc)
        flat, big = [], []
        for name, (lo, hi) in boxes:
            span = [hi[i] - lo[i] for i in range(3)]
            thin = [i for i in range(3) if span[i] <= args.flat_eps]
            # a plane is thin on ONE axis and real on the others; thin on two
            # is an edge and on three a point, and neither draws a white square
            if len(thin) == 1 and max(span) > args.flat_eps * 10:
                flat.append((name, span, thin[0]))
            if max(span) > args.max_span:
                big.append((name, span))
        print()
        print("mesh nodes measured: %d" % len(boxes))
        print("DEGENERATE (a plane, single-sided by construction): %d"
              % len(flat))
        for name, span, ax in sorted(flat, key=lambda r: -max(r[1]))[:args.top]:
            print("   %-38s %7.2f x %7.2f x %7.2f   flat on %s"
                  % (name[:38], span[0], span[1], span[2], "XYZ"[ax]))
        if not flat:
            print("   every mesh node is a solid. Whatever you saw is not in")
            print("   this file -- try the site, or the dressing layer.")
        print("OVERSIZE (any axis over %.1f m): %d" % (args.max_span, len(big)))
        for name, span in sorted(big, key=lambda r: -max(r[1]))[:args.top]:
            print("   %-38s %7.2f x %7.2f x %7.2f"
                  % (name[:38], span[0], span[1], span[2]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
