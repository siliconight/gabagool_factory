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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("glb")
    ap.add_argument("--below", type=float, default=None,
                    help="list nodes whose translation Y is under this (Y-up)")
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
    print("(glTF space -- Y-UP, so up is the second component)")
    print()
    print("%6s  %-34s %9s %9s" % ("count", "family", "y_min", "y_max"))
    for f, c in fams.most_common(args.top):
        if zs.get(f):
            print("%6d  %-34s %9.2f %9.2f" % (c, f[:34], min(zs[f]), max(zs[f])))
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
