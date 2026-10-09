"""Weighted normals across every species Zoo builds (roadmap 214, trial 1).

Run inside Blender, background, against a Zoo tree that has 1.87.0's
`weighted_normals` keyword:

    C:\\blender\\blender.exe -b --factory-startup --python census.py -- <zoo root> <out dir> [species ...]

Each species is planned and built ONCE, at its genome's default corner, the
way `tools/coplanar_census.py` builds it (`kit.plan_kit`, then
`build.build_module`; its role map and corner dims are imported from that
tool, not copied). The one built scene is then exported twice, with
`share_textures=False` both times:
- ON: `export_glb(...)`, Zoo 1.87.0's default, which weighs the normals;
- OFF: every part's custom normals removed, then
  `export_glb(..., weighted_normals=False)` -- what 1.86.0 shipped
  (`export_probe.py`: 28.89 degrees on the crate either way).
So the two files differ in their normals and in nothing a build decided.

Per species, from the two GLBs: meshes, vertices, triangles and bytes, ON
against OFF; on triangles over 0.01 m2, the corners and their splay (degrees
between a corner's normal and its face's), mean and the count over 10
degrees, OFF and ON; and the largest normal change and how many triangle
corners moved more than 1 degree, paired by TRIANGLE CORNER.

RETRACTED, kept above the pairing that replaced it. Run 1 paired the two
files' VERTICES by index, guarded by "the position lists are identical". It
reported normals moved up to 177.5 degrees on weed_tuft, 178.4 on
litter_scrap and 177.6 on london_plane, where `fan_probe.py`, reading the
meshes themselves, found 7.7, 18.6 and 26.5 at most. The guard could not
catch it: a thin card's front and back vertices share a position, so the
position lists match whichever order the exporter writes the two in, and its
order follows the normals, which is the thing that changed. A front vertex
paired with a back one reads as a flip. Triangle corners come in the faces'
order, which weighting does not touch, and each pair's two positions are
checked equal before any is compared.

Prints what it measured and stops. JSON: <out dir>/census.json.
"""
import json
import math
import os
import struct
import sys
import traceback

argv = sys.argv[sys.argv.index("--") + 1:]
ZOO, OUT = argv[0], os.path.abspath(argv[1])
sys.path.insert(0, ZOO)
sys.path.insert(0, os.path.join(ZOO, "tools"))
os.makedirs(OUT, exist_ok=True)

import bpy  # noqa: E402
import coplanar_census as cc  # noqa: E402
from zoo_keeper.bpylayer import build, export  # noqa: E402
from zoo_keeper.core import kit  # noqa: E402

THEME, STYLE = "delco_1997", 1
BIG = 0.01          # m2
DOMED = 10.0        # degrees


def read_glb(path):
    with open(path, "rb") as f:
        data = f.read()
    jlen = struct.unpack_from("<I", data, 12)[0]
    doc = json.loads(data[20:20 + jlen])
    binary = data[20 + jlen + 8:]

    def acc(i):
        a = doc["accessors"][i]
        bv = doc["bufferViews"][a["bufferView"]]
        off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        n = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[a["type"]]
        fmt = {5126: "f", 5123: "H", 5125: "I", 5121: "B"}[a["componentType"]]
        stride = bv.get("byteStride") or struct.calcsize("<" + fmt * n)
        return [struct.unpack_from("<" + fmt * n, binary, off + k * stride)
                for k in range(a["count"])]

    pos, nor, idx, prims = [], [], [], 0
    for mesh in doc.get("meshes", []):
        for prim in mesh["primitives"]:
            prims += 1
            if "NORMAL" not in prim["attributes"]:
                continue
            base = len(pos)
            pos += acc(prim["attributes"]["POSITION"])
            nor += acc(prim["attributes"]["NORMAL"])
            idx += [base + t[0] for t in acc(prim["indices"])]
    return {"prims": prims, "pos": pos, "nor": nor, "idx": idx,
            "bytes": len(data)}


def _deg(a, b):
    d = sum(x * y for x, y in zip(a, b))
    return math.degrees(math.acos(max(-1.0, min(1.0, d))))


def splay(g):
    pos, nor, idx = g["pos"], g["nor"], g["idx"]
    angles = []
    for t in range(0, len(idx), 3):
        a, b, c = (pos[i] for i in idx[t:t + 3])
        u = [b[i] - a[i] for i in range(3)]
        w = [c[i] - a[i] for i in range(3)]
        fn = [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2],
              u[0] * w[1] - u[1] * w[0]]
        ln = math.sqrt(sum(x * x for x in fn))
        if ln / 2.0 < BIG:
            continue
        fn = [x / ln for x in fn]
        angles += [_deg(fn, nor[i]) for i in idx[t:t + 3]]
    return angles


def strip_custom_normals(coll):
    n = 0
    for obj in coll.objects:
        me = obj.data if obj.type == "MESH" else None
        if me is not None and me.has_custom_normals:
            me.attributes.remove(me.attributes["custom_normal"])
            n += 1
    return n


def one(sp, roles):
    gpath = os.path.join(ZOO, "zoo_keeper", "genome", "species", sp + ".json")
    with open(gpath, encoding="utf-8") as f:
        g = json.load(f)
    dims = cc._corner_dims(g, "default")
    rec = {"species": sp, "dims": [round(v, 4) for v in dims]}
    cc._clear(bpy)
    role, size_mod = roles.get(sp, ("prop", "full"))
    slot = {"slot_id": f"{sp}_0", "role": role, "size_mod": size_mod,
            "style": STYLE, "fit": {"dims": dims, "pivot": "center"}}
    if role == "prop":
        slot["species"] = sp
    plan = kit.plan_kit({"building_id": "wn_census", "slots": [slot]},
                        theme=THEME, style=STYLE)
    if not plan["modules"]:
        rec["error"] = "plan_kit returned no module"
        return rec
    res = build.build_module(plan["modules"][0], OUT, theme=THEME, style=STYLE,
                             options={"save_blend": False})
    stem = res["stem"]
    rec["stem"], rec["status"] = stem, res["report"]["status"]
    coll = bpy.data.collections[stem]
    on_p, off_p = (os.path.join(OUT, stem + s) for s in (".on.glb", ".off.glb"))
    export.export_glb(on_p, coll, share_textures=False)
    rec["parts_stripped"] = strip_custom_normals(coll)
    export.export_glb(off_p, coll, share_textures=False, weighted_normals=False)
    on, off = read_glb(on_p), read_glb(off_p)
    for k in ("prims", "bytes"):
        rec[k] = [off[k], on[k]]
    rec["verts"] = [len(off["pos"]), len(on["pos"])]
    rec["tris"] = [len(off["idx"]) // 3, len(on["idx"]) // 3]
    s_off, s_on = splay(off), splay(on)
    rec["big_corners"] = len(s_on)
    if s_on:
        rec["splay_mean"] = [round(sum(s_off) / len(s_off), 2),
                             round(sum(s_on) / len(s_on), 2)]
        rec["domed"] = [sum(a > DOMED for a in s_off), sum(a > DOMED for a in s_on)]
    pairs = list(zip(off["idx"], on["idx"]))
    if (len(off["idx"]) == len(on["idx"])
            and all(off["pos"][a] == on["pos"][b] for a, b in pairs)):
        moved = [_deg(off["nor"][a], on["nor"][b]) for a, b in pairs]
        rec["corners"] = len(moved)
        rec["moved_max"] = round(max(moved), 2) if moved else 0.0
        rec["moved_over_1"] = sum(m > 1.0 for m in moved)
    else:
        rec["moved_max"] = None          # triangle corners differ: not compared
    return rec


def main():
    gdir = os.path.join(ZOO, "zoo_keeper", "genome", "species")
    species = argv[2:] or sorted(f[:-5] for f in os.listdir(gdir) if f.endswith(".json"))
    roles = cc._role_map(kit)
    rows = []
    for sp in species:
        try:
            rec = one(sp, roles)
        except Exception as exc:                       # recorded, not hidden
            rec = {"species": sp, "error": f"{type(exc).__name__}: {exc}",
                   "traceback": traceback.format_exc()[-1200:]}
        rows.append(rec)
        if "error" in rec:
            print(f"[wn] {sp}: ERROR {rec['error']}")
        else:
            print(f"[wn] {sp}: verts {rec['verts']} tris {rec['tris']} prims {rec['prims']} "
                  f"bytes {rec['bytes']} big {rec['big_corners']} "
                  f"splay {rec.get('splay_mean')} domed {rec.get('domed')} "
                  f"moved max {rec.get('moved_max')} over1 {rec.get('moved_over_1')}")
    with open(os.path.join(OUT, "census.json"), "w", encoding="utf-8") as f:
        json.dump({"theme": THEME, "style": STYLE, "big_m2": BIG, "domed_deg": DOMED,
                   "rows": rows}, f, indent=1)
    ok = [r for r in rows if "error" not in r]
    same = lambda k: sum(r[k][0] == r[k][1] for r in ok)  # noqa: E731
    print(f"[wn] {len(rows)} species, {len(rows) - len(ok)} did not build")
    for k in ("verts", "tris", "prims", "bytes"):
        print(f"[wn] {k} identical ON and OFF: {same(k)} of {len(ok)}")
    changed = [r for r in ok if (r.get("moved_over_1") or 0) > 0]
    unpaired = [r["species"] for r in ok if r.get("moved_max") is None]
    print(f"[wn] species with a triangle corner's normal moved over 1 deg: "
          f"{len(changed)} of {len(ok)}; not paired: {unpaired or 'none'}")
    worst = max((r for r in ok if r.get("moved_max") is not None),
                key=lambda r: r["moved_max"], default=None)
    if worst:
        print(f"[wn] largest move: {worst['moved_max']} deg, {worst['species']}")
    d_off = sum(r.get("domed", [0, 0])[0] for r in ok)
    d_on = sum(r.get("domed", [0, 0])[1] for r in ok)
    print(f"[wn] big-face corners over {DOMED:g} deg, all species: OFF {d_off}, ON {d_on}")


main()
