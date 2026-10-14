"""Inside Blender: a Zoo build run as its job runs it, with a digest of the matching parts' meshes printed after each
step (roadmap 247). Driven by `stage_runs.py`; by hand:

    blender --background --python docs/findings/roofprops_bytes/stage_digest.py -- <zoo_cli.py's own arguments>

Wraps, in memory only, Zoo's `geometry.bm_to_object` and the steps it calls by module name (`bevel_edges`,
`shade_by_angle`, `cube_project_uv`, `wear_colors`), `geometry.weight_normals` and `merge.pack_by_material`, then
runs `tools/zoo_cli.py` as `__main__` with the arguments after `--`. For every part whose object name starts with
`STAGE_MATCH` (default `SatelliteDish`), each line reads

    STAGE <part>#<n> <step> ov=.. of=.. fi=.. fr=.. v=.. f=.. c=.. u=.. n=.. nv=<count> nf=<count>

(`_fields` says what each digest covers: the order as stored, the faces' corner tuples blind to order and then to
their starting corner, and the content -- coordinates, faces as coordinate cycles, wear colours, UVs, normals.) Coordinates rounded to 1e-5 m, colours, UVs and
normals to 1e-4. `<n>` counts the parts of one name in build order. Prints; names no cause.
"""
import hashlib
import os
import runpy
import sys

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ZOO = os.environ.get("ZOO_ROOT") or os.path.join(F, "zoo")
MATCH = os.environ.get("STAGE_MATCH", "SatelliteDish")
sys.path.insert(0, ZOO)

import bmesh  # noqa: E402

from zoo_keeper.bpylayer import geometry, merge  # noqa: E402

SEEN = {}
CURRENT = [None]


def _h(x):
    return hashlib.sha256(repr(x).encode()).hexdigest()[:10]


def _r(seq, nd):
    return tuple(round(float(c), nd) for c in seq)


def _canon(cycle):
    k = cycle.index(min(cycle))
    return tuple(cycle[k:] + cycle[:k])


def _fields(co, faces, cols, uvs, nors):
    """`key=digest` pairs: ov, of -- the vertices and the faces' corner indices as stored; fi -- those corner
    tuples sorted (blind to the faces' order, not to where each starts); fr -- each rotated to its lowest index,
    then sorted (blind to both); v, f -- coordinates sorted, and faces as coordinate cycles from their least
    corner; c, u, n -- colours, UVs and normals keyed to their corner's coordinates."""
    rot = [tuple(f[f.index(min(f)):] + f[:f.index(min(f))]) for f in faces]
    return "ov=%s of=%s fi=%s fr=%s v=%s f=%s c=%s u=%s n=%s nv=%d nf=%d" % (
        _h(co), _h(faces), _h(sorted(faces)), _h(sorted(rot)), _h(sorted(co)),
        _h(sorted(_canon([co[i] for i in f]) for f in faces)), _h(sorted(cols)),
        "-" if uvs is None else _h(sorted(uvs)), _h(sorted(nors)), len(co), len(faces))


def bm_line(bm):
    bm.verts.index_update()
    co = [_r(v.co, 5) for v in bm.verts]
    faces = [tuple(v.index for v in f.verts) for f in bm.faces]
    # `geometry.wear_colors` writes a BYTE colour layer named `Wear` (`geometry.WEAR_LAYER`), and draws one
    # random number a vertex in storage order
    col = bm.loops.layers.color.get(geometry.WEAR_LAYER)
    uv = bm.loops.layers.uv.active if bm.loops.layers.uv else None
    cols, uvs, nors = [], [], []
    for f in bm.faces:
        for lp in f.loops:
            key = co[lp.vert.index]
            if col is not None:
                cols.append((key, _r(lp[col], 4)))
            if uv is not None:
                uvs.append((key, _r(lp[uv].uv, 4)))
            nors.append((key, _r(lp.vert.normal, 4), f.smooth))
    return _fields(co, faces, cols, uvs, nors)


def mesh_line(me):
    co = [_r(v.co, 5) for v in me.vertices]
    faces = [tuple(p.vertices) for p in me.polygons]
    cn = getattr(me, "corner_normals", None)
    nors = []
    if cn is not None:
        for p in me.polygons:
            for li in p.loop_indices:
                nors.append((co[me.loops[li].vertex_index], _r(cn[li].vector, 4)))
    col = me.color_attributes.active_color if me.color_attributes else None
    cols = []
    if col is not None and col.domain == "CORNER":
        for p in me.polygons:
            for li in p.loop_indices:
                cols.append((co[me.loops[li].vertex_index], _r(col.data[li].color, 4)))
    return _fields(co, faces, cols, None, nors)


def say(step, text):
    if CURRENT[0]:
        print("STAGE %s %s %s" % (CURRENT[0], step, text), flush=True)


def wrap_bm(name):
    orig = getattr(geometry, name)

    def inner(bm, *a, **k):
        say(name + ":in", bm_line(bm))
        out = orig(bm, *a, **k)
        say(name + ":out", bm_line(bm))
        return out
    setattr(geometry, name, inner)


for _step in ("bevel_edges", "shade_by_angle", "cube_project_uv", "wear_colors"):
    wrap_bm(_step)

_bm_to_object = geometry.bm_to_object


def bm_to_object(bm, name, *a, **k):
    if name.startswith(MATCH):
        SEEN[name] = SEEN.get(name, 0) + 1
        CURRENT[0] = "%s#%d" % (name, SEEN[name])
    try:
        obj = _bm_to_object(bm, name, *a, **k)
        say("to_mesh", mesh_line(obj.data))
        return obj
    finally:
        CURRENT[0] = None


geometry.bm_to_object = bm_to_object

_weight = geometry.weight_normals


def weight_normals(me):
    out = _weight(me)
    if me.name.startswith(MATCH):
        print("STAGE %s weight_normals %s" % (me.name, mesh_line(me)), flush=True)
    return out


geometry.weight_normals = weight_normals

_pack = merge.pack_by_material


def pack_by_material(collection, *a, **k):
    packed = _pack(collection, *a, **k)
    if packed is not None:
        for o in packed.objects:
            if o.name.startswith(MATCH) and getattr(o, "type", "") == "MESH":
                print("STAGE %s merged %s" % (o.name, mesh_line(o.data)), flush=True)
    return packed


merge.pack_by_material = pack_by_material

sys.argv = [os.path.join(ZOO, "tools", "zoo_cli.py")] + sys.argv[sys.argv.index("--"):]
try:
    runpy.run_path(os.path.join(ZOO, "tools", "zoo_cli.py"), run_name="__main__")
except SystemExit as exc:
    print("STAGE_EXIT %s" % exc.code, flush=True)
