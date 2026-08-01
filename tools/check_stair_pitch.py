"""How steep are the stairs, and which of the two limits do they fall between?

REPORTED FROM PLAY: you can get onto a flight, you cannot climb it, and you slide
back down. That is the signature of a surface the ENGINE classifies as a wall --
not a missing ramp foot, which would stop you at the bottom with solid ground
under you and no upward motion at all.

THE SUSPECT. Two numbers describe "how steep can you stand on this", and nothing
ties them together:

    nav_bake.agent_max_slope_deg = 55       what the navmesh will route a body up
    CharacterBody3D.floor_max_angle = 45    the engine default; lot_player.gd
                                            never sets it

Anything pitched between them is navigable on paper and a wall in play. The QA
walkers follow the navmesh and climb it; a person slides off. A stair ramp is the
only surface in this stack steep enough to land in that band, which is why stairs
specifically fail while everything outdoors works.

That is a HYPOTHESIS. This measures it, off the geometry that shipped, by reading
the collision ramp meshes out of each building's .glb and computing the pitch of
each one's top surface. No Blender, no Godot, no re-derivation from the constants
that produced the geometry -- the same discipline site_steps uses on the .tscn.

THE ANSWER DECIDES THE FIX, and the two are not close in cost:

  * pitches between 45 and 55  -> raise the controller's floor_max_angle to the
    contract's agent_max_slope_deg. One line, no geometry moves. Note it also
    moves the step thresholds, since both derive from floor_max_angle: the walk
    ceiling goes 0.1025 -> 0.149 and the step-up's lower bound follows it, so the
    two still meet exactly.
  * pitches above 55 -> neither limit permits them and the navmesh is also lying.
    The stairs need a longer run or a landing, which is a deli_counter geometry
    change across every building that has one.
  * pitches below 45 -> the hypothesis is wrong, stairs are walkable by both
    limits, and the cause is something else. Say so and stop.

    python check_stair_pitch.py
    python check_stair_pitch.py --glb lot\\specs\\walkup_siege\\buildings
"""
import argparse
import json
import math
import os
import pathlib
import struct

ROOT = pathlib.Path(__file__).resolve().parent
SITES = ROOT / "lot" / "specs"
CONTRACT = ROOT / "deli_counter" / "agent_contract.json"

#: Collision meshes deli_counter emits for a flight. The ramp is the smooth
#: surface under the visual steps; it is what a body actually stands on.
RAMP_HINTS = ("ramp",)
STAIR_HINTS = ("stair",)


def read_glb(path):
    """(json chunk, binary chunk) from a binary glTF."""
    with open(path, "rb") as f:
        magic, _ver, _len = struct.unpack("<III", f.read(12))
        if magic != 0x46546C67:
            raise ValueError("not a .glb")
        js, bin_ = None, b""
        while True:
            head = f.read(8)
            if len(head) < 8:
                break
            clen, ctype = struct.unpack("<II", head)
            data = f.read(clen)
            if ctype == 0x4E4F534A:
                js = json.loads(data.decode("utf-8"))
            elif ctype == 0x004E4942:
                bin_ = data
        return js, bin_


def node_world(gltf, idx, cache):
    """World matrix of a node, walking the parent chain once and memoising."""
    if idx in cache:
        return cache[idx]
    parent = None
    for i, n in enumerate(gltf.get("nodes", [])):
        if idx in (n.get("children") or []):
            parent = i
            break
    m = local_matrix(gltf["nodes"][idx])
    if parent is not None:
        m = mat_mul(node_world(gltf, parent, cache), m)
    cache[idx] = m
    return m


def local_matrix(node):
    if "matrix" in node:                       # column-major in glTF
        m = node["matrix"]
        return [[m[0], m[4], m[8], m[12]], [m[1], m[5], m[9], m[13]],
                [m[2], m[6], m[10], m[14]], [m[3], m[7], m[11], m[15]]]
    t = node.get("translation", [0.0, 0.0, 0.0])
    r = node.get("rotation", [0.0, 0.0, 0.0, 1.0])
    s = node.get("scale", [1.0, 1.0, 1.0])
    x, y, z, w = r
    rot = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w), 0.0],
           [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w), 0.0],
           [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y), 0.0],
           [0.0, 0.0, 0.0, 1.0]]
    for c in range(3):
        for rw in range(3):
            rot[rw][c] *= s[c]
    rot[0][3], rot[1][3], rot[2][3] = t
    return rot


def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)]
            for i in range(4)]


def apply(m, p):
    return [m[i][0] * p[0] + m[i][1] * p[1] + m[i][2] * p[2] + m[i][3]
            for i in range(3)]


def positions(gltf, bin_, mesh_idx):
    """Every vertex position of a mesh, in mesh space."""
    out = []
    for prim in gltf["meshes"][mesh_idx].get("primitives", []):
        acc_i = prim.get("attributes", {}).get("POSITION")
        if acc_i is None:
            continue
        acc = gltf["accessors"][acc_i]
        if acc.get("componentType") != 5126 or acc.get("type") != "VEC3":
            continue
        bv = gltf["bufferViews"][acc["bufferView"]]
        off = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
        stride = bv.get("byteStride") or 12
        for i in range(acc["count"]):
            s = off + i * stride
            out.append(struct.unpack_from("<fff", bin_, s))
    return out


def pitch_of(pts):
    """AABB estimate of pitch. RETAINED, AND WRONG -- see pitch_exact.

    This takes the world-space bounding box of the ramp and returns
    atan2(dy, max(dx, dz)). A stair ramp is a tilted SLAB, and the box around a
    tilted slab is both taller and shorter than the slab: for length L, thickness
    t and pitch p, dy = L*sin(p) + t*cos(p) and dx = L*cos(p) + t*sin(p), so the
    ratio always reads STEEPER than the surface is. Worse, max(dx, dz) picks the
    larger horizontal extent, which is the stair's WIDTH rather than its run
    whenever a flight is wider than it is long -- which a half-height basement
    flight is, and every steep reading was a storey -1 flight.

    It reported 45-51 degrees where stair_place.stair_dims generates about 33 for
    a 3.2 m storey. Kept beside the exact figure so the correction travels with
    the claim instead of the claim being remembered alone.
    """
    if len(pts) < 4:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    zs = [p[2] for p in pts]
    dx, dy, dz = max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)
    run = max(dx, dz)
    if run < 1e-6:
        return None
    return math.degrees(math.atan2(dy, run))


def pitch_exact(m, local_pts):
    """Pitch of a ramp from its own world matrix, in degrees.

    Identify the slab's axes by its LOCAL EXTENTS, not by their inclination. A
    first version sorted the three axes by how steep they were and took the
    middle one as the run -- which is right below 45 degrees and silently returns
    the COMPLEMENT above it, because past 45 the long axis is steeper than the
    normal and the sort swaps them. It read a true 55 as 35, in exactly the range
    the stairs were being judged in, and its own agreement check reported perfect
    agreement because both readings came from the same swapped pair.

    The slab's thinnest local axis is its normal, unambiguously and at any pitch.
    The surface pitch is then the angle between that normal and vertical. The
    longest local axis is the run, and its inclination should equal the same
    pitch -- two genuinely independent readings, so their disagreement means
    something.

    Returns (pitch_deg, disagreement_deg) or None.
    """
    if len(local_pts) < 4:
        return None
    ext = []
    for ax in range(3):
        vals = [p[ax] for p in local_pts]
        ext.append(max(vals) - min(vals))
    thin = ext.index(min(ext))
    long_ = ext.index(max(ext))
    if thin == long_:
        return None

    def world_axis(c):
        v = (m[0][c], m[1][c], m[2][c])
        n = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
        return None if n < 1e-9 else (v[0] / n, v[1] / n, v[2] / n)

    nv = world_axis(thin)
    rv = world_axis(long_)
    if nv is None or rv is None:
        return None
    # pitch from the NORMAL: a flat floor's normal is vertical, so the angle
    # between the normal and up IS the surface's tilt.
    from_normal = math.degrees(math.acos(min(1.0, abs(nv[1]))))
    # pitch from the RUN: how far the long axis rises out of horizontal.
    horiz = math.sqrt(rv[0] * rv[0] + rv[2] * rv[2])
    from_run = math.degrees(math.atan2(abs(rv[1]), horiz))
    return from_normal, abs(from_normal - from_run)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--glb", default=None,
                    help="a directory of .glb (default: every building the "
                         "library uses)")
    ap.add_argument("--all-meshes", action="store_true",
                    help="report every stair mesh, not just the ramps")
    args = ap.parse_args()

    with open(CONTRACT, encoding="utf-8") as f:
        c = json.load(f)
    nav_slope = float(c["nav_bake"]["agent_max_slope_deg"])
    floor_angle = 45.0          # CharacterBody3D default; lot_player never sets it

    if args.glb:
        files = sorted(pathlib.Path(args.glb).glob("*.glb"))
    else:
        files = sorted(SITES.glob("*/buildings/*.glb"))
    seen = {}
    for f in files:
        seen.setdefault(f.stem, f)
    if not seen:
        print("no .glb found")
        return 1

    print(f"  navmesh routes bodies up to   {nav_slope:.1f} deg "
          f"(nav_bake.agent_max_slope_deg)")
    print(f"  a body STANDS on up to        {floor_angle:.1f} deg "
          f"(CharacterBody3D.floor_max_angle, never set)")
    print(f"  so anything between them is navigable on paper and a wall in "
          f"play\n")

    rows = []
    for stem, path in sorted(seen.items()):
        try:
            gltf, bin_ = read_glb(path)
        except (OSError, ValueError, struct.error) as e:
            print(f"  {stem}: unreadable ({type(e).__name__})")
            continue
        cache = {}
        for i, node in enumerate(gltf.get("nodes", [])):
            nm = (node.get("name") or "").lower()
            if "mesh" not in node:
                continue
            if not any(h in nm for h in STAIR_HINTS):
                continue
            is_ramp = any(h in nm for h in RAMP_HINTS)
            if not is_ramp and not args.all_meshes:
                continue
            pts = positions(gltf, bin_, node["mesh"])
            if not pts:
                continue
            m = node_world(gltf, i, cache)
            world = [apply(m, p) for p in pts]
            p = pitch_of(world)
            ex = pitch_exact(m, pts)
            if ex is None:
                continue
            exact, agree = ex
            if exact < 1.0:
                continue
            rows.append((stem, node.get("name"), exact, p, agree))

    if not rows:
        print("  no stair ramp meshes found. Either these buildings have no "
              "stairs,\n  or the naming convention has changed -- check a .glb "
              "before concluding\n  anything from this silence.")
        return 2

    worst = {}
    for stem, nm, exact, aabb, agree in rows:
        if stem not in worst or exact > worst[stem][1]:
            worst[stem] = (nm, exact, aabb, agree)

    print(f"  {'building':<24}{'steepest ramp':<30}{'pitch':>7}{'aabb':>7}"
          f"   verdict")
    print("  " + "-" * 88)
    band = walls = fine = 0
    disagree = 0
    for stem, (nm, p, aabb, agree) in sorted(worst.items(),
                                             key=lambda kv: -kv[1][1]):
        if agree > 1.0:
            disagree += 1
        if p > nav_slope:
            v = "TOO STEEP FOR EITHER -- navmesh is lying too"
            walls += 1
        elif p > floor_angle:
            v = f"navigable, NOT STANDABLE -- wall in play"
            band += 1
        else:
            v = "walkable"
            fine += 1
        print(f"  {stem:<24}{(nm or '')[:28]:<30}{p:6.1f}d{aabb:6.1f}d   {v}")

    print(f"\n  {fine} building(s) walkable, {band} in the 45-55 band, "
          f"{walls} above both")
    print(f"  `pitch` is the ramp's own tilt, from its world matrix. `aabb` is "
          f"the old\n  bounding-box estimate, kept visible because it read "
          f"steeper than the\n  surface actually is and that number has already "
          f"been quoted.")
    if disagree:
        print(f"  {disagree} row(s) where the two axis readings disagree by more "
              f"than a degree --\n  those rows are not trustworthy; the ramp may "
              f"not be a simple tilted slab.")
    if band and not walls:
        print(f"\n  Every failing flight is between {floor_angle:.0f} and "
              f"{nav_slope:.0f} degrees, so the geometry is\n  consistent with "
              f"the contract and the CONTROLLER is the odd one out. Setting\n  "
              f"floor_max_angle to nav_bake.agent_max_slope_deg would make them "
              f"standable.\n  Note it also moves every threshold derived from "
              f"floor_max_angle: the walk\n  ceiling goes "
              f"{0.35 * (1 - math.cos(math.radians(floor_angle))):.4f} -> "
              f"{0.35 * (1 - math.cos(math.radians(nav_slope))):.4f} m for the "
              f"0.35 m body, and the step-up's\n  lower bound follows it, so "
              f"the two still meet exactly.")
    elif walls:
        print("\n  Some flights are steeper than the navmesh's own limit, so "
              "raising the\n  controller would not be enough and the bake is "
              "promising a climb no body\n  can make. Those need a longer run "
              "or a landing -- a deli_counter change.")
    else:
        print("\n  Nothing is above the floor angle, so the slope hypothesis is "
              "REFUTED and\n  stairs fail for some other reason. Do not patch "
              "floor_max_angle.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
