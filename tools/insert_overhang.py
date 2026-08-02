"""Measure how far each themed insert sticks out of the shape it was fitted to.

WHAT THIS IS FOR. The swap contract says a Zoo insert substitutes the VISUAL at
a Deli Counter slot and leaves the shell's shape and collision alone
(`deli_counter/docs/ASSET_SWAP_CONTRACT.md`). Art may wrap the shell; it must
not reinterpret it. Nothing measured whether it does. The composed building's
placement gate reports how many modules SIT ON the greybox collision, which is
a different question from how far past the slot they extend -- a module can sit
correctly and still project three metres of pole into the sky.

    python tools\\insert_overhang.py <composed>\\site.tscn [--slots <name>.slots.json]

WHAT IT MEASURES, AND IN WHAT FRAME. Godot space, Y up -- and TWO SPACES ARE
INVOLVED, which the first version of this file got wrong and reported as a
finding. `COORDINATE_CONTRACT.md` is ratified: everything Deli Counter authors,
`slots.json` included, is Blender Z-up, and the glTF importer converts to Godot
Y-up exactly once at import. So a slot's `(dx, dy, dz)` is a module's
`(dx, dz, dy)`, and its translation `(x, y, z)` is `(x, z, -y)`. Comparing them
unconverted reported a 44 x 32 roof as 31.70 m short in y and 31.70 m long in z
-- equal and opposite, the swap's own signature, and no defect at all.

For every instanced module:

  * its local AABB, straight from the glTF POSITION accessor's `min`/`max`
    (mandatory in the spec, so no vertex data is decoded);
  * that AABB carried through the node transform, re-hulled axis-aligned --
    conservative for a rotated module, in the direction that OVER-reports
    overhang rather than under-reporting it;
  * its extents against the slot's `fit.dims`, converted, when the node name
    matches a `slot_id`;
  * how far it reaches outside the DECLARED ENVELOPE -- the union of every slot
    box. Not `site_base.glb`: that is the ground plate (measured x -22..22,
    y -2..2, z -16..16, four metres tall under a two-storey building), and
    comparing walls against it reported 320 of 321 modules as offenders. A
    reference that makes almost everything an offender is the wrong reference;
  * whether it answers a declared slot at all. A module with no slot is art
    occupying space nothing asked for, and that is a different question from
    overhang.

WHAT IT DOES NOT MEASURE. Whether an insert intrudes INWARD into playable
space. That needs the shell's interior surfaces rather than its bounding box,
and a bounding box cannot answer it. Reported as absent rather than
approximated -- an inward intrusion is the half of the contract that actually
breaks gameplay, and a number that looked like an answer would stop anyone
writing the real one.

WHAT A NONZERO EXIT MEANS. Only that the measurement did not happen. Overhang
is reported, never judged: this file has no opinion about how many centimetres
are acceptable, because that number belongs in the slot manifest
(`allowed_outward_overhang_m`) where a person can set it.
"""
import argparse
import json
import os
import re
import struct
import sys

GLB_MAGIC = 0x46546C67
CHUNK_JSON = 0x4E4F534A

_NODE = re.compile(r'^\[node\s+(.*)\]\s*$')
_ATTR = re.compile(r'(\w+)="([^"]*)"')
_INSTANCE = re.compile(r'instance=ExtResource\(\s*"?([^")]+)"?\s*\)')
_TRANSFORM = re.compile(r'^transform\s*=\s*Transform3D\(([^)]*)\)')
_EXT = re.compile(r'\[ext_resource[^\]]*?\bpath="([^"]+)"[^\]]*?\bid="([^"]+)"')
_EXT_ALT = re.compile(r'\[ext_resource[^\]]*?\bid="([^"]+)"[^\]]*?\bpath="([^"]+)"')

_IDENTITY = ((1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0))


class Unreadable(Exception):
    """A file that could not be read. Not a finding about its geometry."""


def gltf_json(path):
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) < 12:
        raise Unreadable(f"{path}: shorter than a GLB header")
    magic, _version, _total = struct.unpack_from("<III", data, 0)
    if magic != GLB_MAGIC:
        raise Unreadable(f"{path}: not a binary GLB")
    off = 12
    while off + 8 <= len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        if ctype == CHUNK_JSON:
            return json.loads(data[off + 8:off + 8 + clen].decode("utf-8"))
        off += 8 + clen + ((4 - clen % 4) % 4)
    raise Unreadable(f"{path}: no JSON chunk")


def glb_aabb(path):
    """(lo, hi) over every POSITION accessor, in the glTF's own space.

    The accessors' `min`/`max` are required for POSITION, so this is the
    bounding box the exporter itself declared -- not one recomputed here, which
    keeps this measurement independent of how the vertices are encoded.
    """
    doc = gltf_json(path)
    lo = [float("inf")] * 3
    hi = [float("-inf")] * 3
    seen = False
    for mesh in doc.get("meshes", []):
        for prim in mesh.get("primitives", []):
            idx = prim.get("attributes", {}).get("POSITION")
            if idx is None:
                continue
            acc = doc.get("accessors", [])[idx]
            amin, amax = acc.get("min"), acc.get("max")
            if not amin or not amax or len(amin) < 3:
                continue
            seen = True
            for a in range(3):
                lo[a] = min(lo[a], float(amin[a]))
                hi[a] = max(hi[a], float(amax[a]))
    if not seen:
        raise Unreadable(f"{path}: no POSITION accessor declared min/max")
    return tuple(lo), tuple(hi)


def godot_transform(numbers):
    """Godot writes Transform3D as basis COLUMNS then origin."""
    v = [float(n) for n in numbers]
    if len(v) < 12:
        return _IDENTITY
    return ((v[0], v[3], v[6], v[9]),
            (v[1], v[4], v[7], v[10]),
            (v[2], v[5], v[8], v[11]))


def hull(matrix, lo, hi):
    """The transformed box, re-hulled axis-aligned. Conservative by design."""
    out_lo = [float("inf")] * 3
    out_hi = [float("-inf")] * 3
    for sx in (lo[0], hi[0]):
        for sy in (lo[1], hi[1]):
            for sz in (lo[2], hi[2]):
                for a in range(3):
                    r = matrix[a]
                    v = r[0] * sx + r[1] * sy + r[2] * sz + r[3]
                    out_lo[a] = min(out_lo[a], v)
                    out_hi[a] = max(out_hi[a], v)
    return tuple(out_lo), tuple(out_hi)


def scene_instances(path):
    """(node_name, resource_path, transform) for every instanced scene."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    ext = {}
    for p, rid in _EXT.findall(text):
        ext[rid] = p
    for rid, p in _EXT_ALT.findall(text):
        ext.setdefault(rid, p)
    out = []
    pending = None
    for raw in text.splitlines():
        line = raw.strip()
        head = _NODE.match(line)
        if head:
            attrs = dict(_ATTR.findall(head.group(1)))
            ref = _INSTANCE.search(head.group(1))
            pending = None
            if ref and ref.group(1) in ext:
                pending = [attrs.get("name", "?"), ext[ref.group(1)], _IDENTITY]
                out.append(pending)
            continue
        if pending is not None:
            m = _TRANSFORM.match(line)
            if m:
                pending[2] = godot_transform(m.group(1).split(","))
                pending = None
    return [tuple(x) for x in out]


def resolve(ref, base_dir):
    rel = ref[6:] if ref.startswith("res://") else ref
    probe = base_dir
    for _ in range(4):
        cand = os.path.join(probe, rel.replace("/", os.sep))
        if os.path.exists(cand):
            return cand
        probe = os.path.dirname(probe)
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("scene", help="the composed themed scene (.tscn)")
    ap.add_argument("--slots", default=None,
                    help="the Deli Counter <name>.slots.json the scene was fitted to")
    ap.add_argument("--base", default="site_base.glb",
                    help="the greybox base resource name (default site_base.glb)")
    ap.add_argument("--top", type=int, default=15,
                    help="how many worst offenders to print (default 15)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    base_dir = os.path.dirname(os.path.abspath(args.scene))
    try:
        instances = scene_instances(args.scene)
    except OSError as exc:
        sys.stderr.write(f"cannot read scene: {exc}\n")
        return 2
    if not instances:
        sys.stderr.write("no instanced modules in this scene\n")
        return 2

    slots = {}
    if args.slots:
        try:
            with open(args.slots, encoding="utf-8") as fh:
                for s in json.load(fh).get("slots", []):
                    slots[str(s.get("slot_id"))] = s
        except (OSError, json.JSONDecodeError) as exc:
            sys.stderr.write(f"cannot read slots: {exc}\n")
            return 2

    boxes = {}
    unreadable = []
    rows = []
    shell = None
    for name, ref, matrix in instances:
        path = resolve(ref, base_dir)
        if path is None:
            unreadable.append(f"{name}: {ref} did not resolve")
            continue
        if ref not in boxes:
            try:
                boxes[ref] = glb_aabb(path)
            except (Unreadable, OSError, KeyError, IndexError, ValueError) as exc:
                unreadable.append(str(exc))
                boxes[ref] = None
        if boxes[ref] is None:
            continue
        lo, hi = hull(matrix, *boxes[ref])
        row = {"node": name, "module": os.path.basename(ref),
               "lo": lo, "hi": hi,
               "size": tuple(hi[a] - lo[a] for a in range(3))}
        if os.path.basename(ref) == args.base:
            shell = (lo, hi)
        rows.append(row)

        slot = slots.get(name)
        row["has_slot"] = slot is not None
        if slot:
            dims = (slot.get("fit") or {}).get("dims")
            if dims and len(dims) >= 3:
                # AXIS CONVERSION, and it is the whole correctness of this
                # comparison. COORDINATE_CONTRACT.md is ratified: slots.json is
                # authored Z-up (Blender) and the glTF importer converts to
                # Godot Y-up exactly once, at import. So a slot's (dx, dy, dz)
                # is a module's (dx, dz, dy) -- extents, so the sign the axis
                # swap carries does not survive into a size.
                #
                # Comparing them unconverted is not a small error: it reported a
                # 44 x 32 roof as 31.70 m too short in y and 31.70 m too long in
                # z, equal and opposite, which is the swap's own signature and
                # not a defect in the art.
                d = [float(x) for x in dims[:3]]
                godot_dims = (d[0], d[2], d[1])
                row["slot_dims"] = list(godot_dims)
                # YAW IS NOT SIZE, and conflating them was this file's second
                # frame error. A module's AABB is taken AFTER its node
                # transform, so a slot turned 90 degrees about up puts the
                # module's width on z where the slot declares it on x. The
                # first version compared them positionally and reported every
                # opening as "-1.25 on x, +1.25 on z" -- equal and opposite,
                # which is a rotation's signature and not a size at all.
                #
                # Slot rotation is `rot_y`/`rot_z`, about the UP axis only
                # (COORDINATE_CONTRACT.md), so height cannot swap and the
                # footprint pair can. Compare y directly and {x, z} as an
                # unordered pair: that is exactly the freedom the contract
                # grants and no more.
                got = sorted((row["size"][0], row["size"][2]))
                want = sorted((godot_dims[0], godot_dims[2]))
                row["slot_excess"] = [round(got[1] - want[1], 3),
                                      round(row["size"][1] - godot_dims[1], 3),
                                      round(got[0] - want[0], 3)]
                row["slot_excess_axes"] = "footprint_long / height / footprint_short"
                # ABSOLUTE, not signed, and this is a correction. Ranking by
                # `max(excess)` reported only modules BIGGER than their slot,
                # and the failure standing in this level is a wall lying on its
                # side: same box, tipped onto a horizontal axis, so it is
                # SHORTER than its slot and never appeared. "No module is
                # bigger than its slot" was true and answered nothing.
                #
                # Yaw is still forgiven above -- a wall turned about up is a
                # correct placement -- so a height that does not match is a
                # rotation about a HORIZONTAL axis, which the slot never
                # granted. That is the signal, and it is a mismatch in either
                # direction.
                row["height_mismatch"] = round(
                    abs(row["size"][1] - godot_dims[1]), 3)
                row["worst_slot_excess"] = round(
                    max(abs(v) for v in row["slot_excess"]), 3)

    # RETRACTED: this used to compare every module against site_base.glb and
    # call the difference "past the greybox base". site_base.glb is the GROUND
    # PLATE -- measured x -22..22, y -2..2, z -16..16, four metres tall under a
    # two-storey building -- so every wall in the level "extended past" it and
    # the tool reported 320 of 321 modules as offenders. A reference that makes
    # almost everything an offender is the wrong reference, not a catastrophe.
    #
    # The envelope a module must stay inside is the one Deli Counter DECLARED:
    # the union of its slot boxes. Anything outside that is art occupying space
    # no slot asked for, which is the actual contract question.
    if slots:
        env_lo = [float("inf")] * 3
        env_hi = [float("-inf")] * 3
        for s in slots.values():
            dims = (s.get("fit") or {}).get("dims")
            t = (s.get("transform") or {}).get("translation")
            if not dims or not t or len(dims) < 3 or len(t) < 3:
                continue
            d = [float(x) for x in dims[:3]]
            # Z-up -> Y-up for both the centre and the extents.
            c = (float(t[0]), float(t[2]), -float(t[1]))
            h = (d[0] / 2.0, d[2] / 2.0, d[1] / 2.0)
            for a in range(3):
                env_lo[a] = min(env_lo[a], c[a] - h[a])
                env_hi[a] = max(env_hi[a], c[a] + h[a])
        if env_lo[0] != float("inf"):
            envelope = (tuple(env_lo), tuple(env_hi))
            for row in rows:
                out = []
                for a in range(3):
                    out.append(round(max(envelope[0][a] - row["lo"][a],
                                         row["hi"][a] - envelope[1][a], 0.0), 3))
                row["outside_shell"] = out
                row["worst_outside"] = round(max(out), 3)
            shell = envelope

    if args.json:
        print(json.dumps({"scene": args.scene, "modules": rows,
                          "unreadable": unreadable}, indent=2, default=list))
        return 0

    if shell:
        print("declared envelope (union of slot boxes, Godot space): "
              "x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f"
              % (shell[0][0], shell[1][0], shell[0][1], shell[1][1],
                 shell[0][2], shell[1][2]))
    else:
        print("no slots manifest given; envelope comparison skipped "
              "(pass --slots)")
    print()

    ranked = sorted((r for r in rows if r.get("worst_outside")),
                    key=lambda r: -r["worst_outside"])
    if ranked:
        print("OUTSIDE THE DECLARED ENVELOPE, worst first (metres, Godot space, Y up)")
        print("%-26s %-30s %8s  %s" % ("node", "module", "worst", "x / y / z"))
        for r in ranked[:args.top]:
            print("%-26s %-30s %8.2f  %s"
                  % (r["node"][:26], r["module"][:30], r["worst_outside"],
                     " / ".join("%.2f" % v for v in r["outside_shell"])))
        print()
        print("%d of %d modules reach outside it; %d by more than 1 m"
              % (len(ranked), len(rows),
                 sum(1 for r in ranked if r["worst_outside"] > 1.0)))
    else:
        print("no module reaches outside the declared envelope")

    orphans = [r for r in rows if slots and not r.get("has_slot")]
    if orphans:
        print()
        print("ANSWERING NO DECLARED SLOT (%d) -- art occupying space nothing "
              "asked for" % len(orphans))
        for r in orphans[:args.top]:
            print("%-26s %-30s  y %.2f..%.2f"
                  % (r["node"][:26], r["module"][:30], r["lo"][1], r["hi"][1]))

    tipped = sorted((r for r in rows if r.get("height_mismatch")),
                    key=lambda r: -r["height_mismatch"])
    tipped = [r for r in tipped if r["height_mismatch"] > 0.01]
    if tipped:
        print()
        print("HEIGHT DOES NOT MATCH THE SLOT (%d) -- rotated about a "
              "horizontal axis, which no slot grants" % len(tipped))
        print("%-26s %-30s %8s  %s"
              % ("node", "module", "off_by", "module h / slot h"))
        for r in tipped[:args.top]:
            print("%-26s %-30s %8.2f  %.2f / %.2f"
                  % (r["node"][:26], r["module"][:30], r["height_mismatch"],
                     r["size"][1], r["slot_dims"][1]))

    excess = sorted((r for r in rows if r.get("worst_slot_excess")),
                    key=lambda r: -r["worst_slot_excess"])
    if excess:
        print()
        print("DIMENSIONS OFF THE SLOT, worst first (metres, absolute)")
        print("%-26s %-30s %8s  %s"
              % ("node", "module", "worst",
                 "long / height / short (footprint pair unordered: yaw is allowed)"))
        for r in excess[:args.top]:
            print("%-26s %-30s %8.2f  %s"
                  % (r["node"][:26], r["module"][:30], r["worst_slot_excess"],
                     " / ".join("%.2f" % v for v in r["slot_excess"])))
    elif slots:
        print()
        print("no module is bigger than its slot")

    print()
    print("inward intrusion is NOT measured: a bounding box cannot answer it, "
          "and it is the half of the contract that breaks gameplay.")
    for u in unreadable:
        sys.stderr.write("unreadable: " + u + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
