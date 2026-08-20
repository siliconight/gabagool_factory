#!/usr/bin/env python3
"""shape_metrics.py -- measure the SHAPE of a built asset, not just its size.

WHY THIS EXISTS.  Everything else in this pipeline is measured against
something: the capsule against `unassisted_step_max`, the lights against a
count, traversal against the functional lock.  Shape had no target and no
instrument, so every judgement about whether a pebble looked like a pebble was
a person squinting at a render.  That is the one place in the stack where we
were still asserting instead of measuring.

WHAT IT MEASURES.  Two units, because they fail differently.

  SPECIMEN metrics answer "is this one object the right kind of solid".
  They are computed from triangles alone -- no Blender, no scene, no
  materials -- so they can run on a shipped GLB in CI.

  PATCH metrics answer "does a scatter of them read as placed or as
  procedural noise".  `docs/SURFACE_DRESSING.md`'s definition of done says
  "no obvious uniform scatter pattern from primary views"; the Clark-Evans
  nearest-neighbour ratio below is that sentence as a number.

WHAT IT DOES NOT DO.  It has no opinion about whether a number is good.  It
reports; the genome (or a future gate) decides.  Thresholds live with the
species that has to meet them, not in the ruler.

UP AXIS.  glTF on disk is Y-UP, so `up=1` is the default here.  Blender-side
callers building in Z-up must pass `up=2`.  This has bitten this repo before
(`glb_nodes.py`, the dressing height check that measured nothing), so the axis
is an explicit argument everywhere rather than a convention.

USAGE
    python tools/shape_metrics.py <file.glb> [more.glb ...] [--json] [--up N]
    python tools/shape_metrics.py --dir <folder>            # every *.glb under it
    python tools/shape_metrics.py --selftest
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import struct
import sys

VERSION = "0.3.1"

# Faces whose normals differ by less than this are treated as one flat region.
# 5 degrees is tight enough that a bevel does not merge with the face it
# bevels, loose enough that float noise on a nominally planar quad does not
# split it in two.
COPLANAR_DEG = 5.0

# Facets whose normals differ by less than this are one "region" of the
# silhouette -- the scale at which an eye reads a face rather than a facet.
REGION_DEG = 20.0

# "Up-facing" for the flat-top tell.  20 degrees, because a rock top that
# slopes 15 degrees still reads as a flat top from a standing eye height.
UPFACE_DEG = 20.0

# Angular bins for the plan-view radial profile.
RADIAL_BINS = 36


# --------------------------------------------------------------------------
# GLB reading.  Deliberately dependency-free: struct + json.  numpy would be
# faster and is probably present, but this tool has to run in CI and in
# Blender's bundled interpreter without an install step.
# --------------------------------------------------------------------------

_COMPONENT = {5120: ("b", 1), 5121: ("B", 1), 5122: ("h", 2),
              5123: ("H", 2), 5125: ("I", 4), 5126: ("f", 4)}
_NCOMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4,
          "MAT2": 4, "MAT3": 9, "MAT4": 16}


def read_glb(path):
    """Return (gltf_json_dict, binary_chunk_bytes) for a .glb file."""
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:4] != b"glTF":
        raise ValueError(f"{path}: not a GLB (magic is {data[:4]!r})")
    _ver, _length = struct.unpack_from("<II", data, 4)
    off, js, bin_chunk = 12, None, b""
    while off + 8 <= len(data):
        clen, ctype = struct.unpack_from("<I4s", data, off)
        payload = data[off + 8: off + 8 + clen]
        if ctype == b"JSON":
            js = json.loads(payload.decode("utf-8"))
        elif ctype == b"BIN\x00":
            bin_chunk = payload
        off += 8 + clen + ((4 - clen % 4) % 4 if clen % 4 else 0)
    if js is None:
        raise ValueError(f"{path}: no JSON chunk")
    return js, bin_chunk


def _accessor(gltf, blob, index):
    """Decode one accessor into a flat list of tuples (or scalars)."""
    acc = gltf["accessors"][index]
    n = acc["count"]
    ncomp = _NCOMP[acc["type"]]
    fmt, size = _COMPONENT[acc["componentType"]]
    if "bufferView" not in acc:                    # sparse-only / zero-filled
        return [(0.0,) * ncomp if ncomp > 1 else 0 for _ in range(n)]
    bv = gltf["bufferViews"][acc["bufferView"]]
    base = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    stride = bv.get("byteStride") or (size * ncomp)
    out = []
    for i in range(n):
        vals = struct.unpack_from("<" + fmt * ncomp, blob, base + i * stride)
        out.append(vals if ncomp > 1 else vals[0])
    return out


def glb_primitives(gltf, blob):
    """Yield (positions, triangles) per primitive, in FILE space.

    Node transforms are applied when a node names a matrix or TRS; Zoo builds
    everything at world scale in place, so in practice this is identity, but
    the tool is also pointed at level GLBs where it is not.
    """
    node_xform = {}
    for ni, node in enumerate(gltf.get("nodes", [])):
        m = node.get("matrix")
        if m:
            # glTF matrices are column-major.
            node_xform[ni] = [[m[0], m[4], m[8], m[12]],
                              [m[1], m[5], m[9], m[13]],
                              [m[2], m[6], m[10], m[14]]]
        else:
            t = node.get("translation", [0.0, 0.0, 0.0])
            s = node.get("scale", [1.0, 1.0, 1.0])
            node_xform[ni] = [[s[0], 0.0, 0.0, t[0]],
                              [0.0, s[1], 0.0, t[1]],
                              [0.0, 0.0, s[2], t[2]]]
    mesh_nodes = {}
    for ni, node in enumerate(gltf.get("nodes", [])):
        if "mesh" in node:
            mesh_nodes.setdefault(node["mesh"], []).append(ni)

    for mi, mesh in enumerate(gltf.get("meshes", [])):
        for prim in mesh.get("primitives", []):
            if prim.get("mode", 4) != 4:           # TRIANGLES only
                continue
            pos_idx = prim.get("attributes", {}).get("POSITION")
            if pos_idx is None:
                continue
            pos = _accessor(gltf, blob, pos_idx)
            if "indices" in prim:
                idx = _accessor(gltf, blob, prim["indices"])
            else:
                idx = list(range(len(pos)))
            tris = [(idx[i], idx[i + 1], idx[i + 2])
                    for i in range(0, len(idx) - 2, 3)]
            for ni in mesh_nodes.get(mi, [None]):
                if ni is None:
                    yield [tuple(p) for p in pos], tris
                    continue
                M = node_xform[ni]
                yield [tuple(M[r][0] * p[0] + M[r][1] * p[1]
                             + M[r][2] * p[2] + M[r][3] for r in range(3))
                       for p in pos], tris


def glb_bounds(gltf):
    """Bounds straight from the POSITION accessors' declared min/max.

    This is the number the old height check was reaching for and never got:
    `glb_nodes.py` reads NODE translations, and a Zoo dressing GLB has exactly
    one node at the origin, so it reported "0 with an explicit translation" and
    measured nothing.  Accessor min/max is mandatory on POSITION in glTF 2.0,
    so this always exists and costs no decoding.
    """
    lo = [float("inf")] * 3
    hi = [float("-inf")] * 3
    seen = False
    for mesh in gltf.get("meshes", []):
        for prim in mesh.get("primitives", []):
            pi = prim.get("attributes", {}).get("POSITION")
            if pi is None:
                continue
            acc = gltf["accessors"][pi]
            if "min" not in acc or "max" not in acc:
                continue
            seen = True
            for i in range(3):
                lo[i] = min(lo[i], acc["min"][i])
                hi[i] = max(hi[i], acc["max"][i])
    return (tuple(lo), tuple(hi)) if seen else None


# --------------------------------------------------------------------------
# Small geometry helpers (no numpy, no scipy).
# --------------------------------------------------------------------------

def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def hull_2d(points):
    """Andrew's monotone chain.  Returns the hull in CCW order."""
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def half(seq):
        out = []
        for p in seq:
            while len(out) >= 2:
                (x1, y1), (x2, y2) = out[-2], out[-1]
                if (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1) > 0:
                    break
                out.pop()
            out.append(p)
        return out

    return half(pts)[:-1] + half(reversed(pts))[:-1]


def poly_area(poly):
    if len(poly) < 3:
        return 0.0
    s = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        s += x1 * y2 - x2 * y1
    return abs(s) * 0.5


def _hull_radial_cv(hull, bins=None):
    """Coefficient of variation of the radius of a convex polygon, sampled at
    evenly spaced angles from its interior centroid.

    Anchors, so a threshold means something:  circle 0.00, square 0.086,
    3:1 rectangle 0.44.  Higher means a less regular plan outline.
    """
    bins = bins or RADIAL_BINS
    if len(hull) < 3:
        return 0.0
    cx = sum(p[0] for p in hull) / len(hull)      # inside, hull is convex
    cy = sum(p[1] for p in hull) / len(hull)
    radii = []
    for b in range(bins):
        th = 2 * math.pi * b / bins
        dx, dy = math.cos(th), math.sin(th)
        best = None
        for i in range(len(hull)):
            x1, y1 = hull[i]
            x2, y2 = hull[(i + 1) % len(hull)]
            ex, ey = x2 - x1, y2 - y1
            den = dx * ey - dy * ex
            if abs(den) < 1e-15:
                continue
            t = ((x1 - cx) * ey - (y1 - cy) * ex) / den
            sseg = ((x1 - cx) * dy - (y1 - cy) * dx) / den
            if t >= 0 and -1e-9 <= sseg <= 1 + 1e-9:
                best = t if best is None else min(best, t)
        if best is not None:
            radii.append(best)
    if len(radii) < 3:
        return 0.0
    mean_r = sum(radii) / len(radii)
    if mean_r <= 0:
        return 0.0
    var = sum((r - mean_r) ** 2 for r in radii) / len(radii)
    return math.sqrt(var) / mean_r


# Position quantisation for welding.  1e-6 m = one micron; Zoo builds in
# metres at centimetre scale, so nothing legitimate is closer than this.
WELD_DIGITS = 6


def weld(verts, tris, digits=WELD_DIGITS):
    """Merge vertices that share a position, and remap the triangles.

    WHY THIS IS NOT OPTIONAL ON A GLB.  glTF has one index buffer for every
    attribute, so the exporter must SPLIT a vertex wherever two triangles
    disagree about its UV, normal or colour.  A closed Blender mesh therefore
    arrives with more vertices than it had, and any topology computed from the
    file's indices is computed on a shredded surface.

    Measured on the shipped pebble: 424 vertices and 192 triangles in the file,
    102 vertices after welding -- exactly the count Blender reported.  Before
    welding, index-based edge pairing called 424 edges "open"; after welding it
    calls zero.  The first number was measuring UV seams and reporting them as
    holes, which is a metric that fires on every correct asset.
    """
    lut, remap = {}, []
    out = []
    for p in verts:
        k = (round(p[0], digits), round(p[1], digits), round(p[2], digits))
        i = lut.get(k)
        if i is None:
            i = lut[k] = len(out)
            out.append(p)
        remap.append(i)
    wt = [(remap[a], remap[b], remap[c]) for (a, b, c) in tris]
    wt = [t for t in wt if t[0] != t[1] and t[1] != t[2] and t[0] != t[2]]
    return out, wt


def components(verts, tris):
    """Index lists of the connected islands, on ALREADY-WELDED topology.

    WHY THE ISLAND IS THE UNIT.  A `pebble` specimen is three stones merged
    into one mesh, and the aggregate bounding box of three scattered stones
    tends toward square as the scatter randomises -- measured, the shipped
    pebble reports b/a = 0.943 for the clump while its individual stones are
    0.60.  Read as a Zingg class, the aggregate is describing the SCATTER
    FOOTPRINT and not the clast, which is a different thing wearing the same
    name.  Proportion metrics belong per island; coverage metrics belong to
    the clump.
    """
    adj = {}
    for (a, b, c) in tris:
        for u, v in ((a, b), (b, c), (c, a)):
            adj.setdefault(u, set()).add(v)
            adj.setdefault(v, set()).add(u)
    seen, out = set(), []
    for start in range(len(verts)):
        if start in seen or start not in adj:
            continue
        stack, group = [start], []
        seen.add(start)
        while stack:
            n = stack.pop()
            group.append(n)
            for w in adj[n]:
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        out.append(group)
    return out


def _proportion(verts, idx, up):
    """Cheap per-island proportion: sorted extents, b/a, c/b, Zingg class."""
    lo = [min(verts[i][k] for i in idx) for k in range(3)]
    hi = [max(verts[i][k] for i in idx) for k in range(3)]
    ext = [hi[k] - lo[k] for k in range(3)]
    a, b, c = sorted(ext, reverse=True)
    ba = (b / a) if a > 0 else 0.0
    cb = (c / b) if b > 0 else 0.0
    zg = (("equant" if cb > 2 / 3 else "disc") if ba > 2 / 3
          else ("rod" if cb > 2 / 3 else "blade"))
    return {"elongation_ba": ba, "flatness_cb": cb, "zingg": zg,
            "extent_up": ext[up]}


def _median(xs):
    xs = sorted(xs)
    n = len(xs)
    if not n:
        return 0.0
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


# --------------------------------------------------------------------------
# SPECIMEN metrics
# --------------------------------------------------------------------------

def mesh_metrics(verts, tris, up=1):
    """Shape metrics for one triangle soup.

    `verts` is a sequence of (x, y, z); `tris` a sequence of index triples;
    `up` the index of the vertical axis (1 for glTF Y-up, 2 for Blender Z-up).
    """
    if not verts or not tris:
        return {"error": "empty mesh", "tris": 0, "verts": len(verts)}

    raw_verts = len(verts)
    verts, tris = weld(verts, tris)                # see weld() for why
    if not tris:
        return {"error": "no non-degenerate triangles", "tris": 0,
                "verts": raw_verts}

    ax = [i for i in range(3) if i != up]          # the two ground axes
    lo = [min(v[i] for v in verts) for i in range(3)]
    hi = [max(v[i] for v in verts) for i in range(3)]
    ext = [hi[i] - lo[i] for i in range(3)]

    # --- per-face area, normal, signed volume ------------------------------
    total_area = 0.0
    vol6 = 0.0
    faces = []                                     # (area, unit normal)
    largest = 0.0
    for (i, j, k) in tris:
        p, q, r = verts[i], verts[j], verts[k]
        n = _cross(_sub(q, p), _sub(r, p))
        mag = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
        area = mag * 0.5
        if mag <= 1e-18:
            continue                               # degenerate sliver
        total_area += area
        largest = max(largest, area)
        faces.append((area, (n[0] / mag, n[1] / mag, n[2] / mag)))
        vol6 += (p[0] * (q[1] * r[2] - q[2] * r[1])
                 - p[1] * (q[0] * r[2] - q[2] * r[0])
                 + p[2] * (q[0] * r[1] - q[1] * r[0]))
    volume = abs(vol6) / 6.0

    # Closedness.  The signed-volume sum above is only meaningful on a closed
    # surface, and an open one is a real defect in a shipped asset besides:
    # you see through it from one side and its lighting is wrong.  An edge
    # used by exactly one triangle is a hole.
    edge_use = {}
    for (i, j, k) in tris:
        for u, v in ((i, j), (j, k), (k, i)):
            edge_use[(u, v) if u < v else (v, u)] = \
                edge_use.get((u, v) if u < v else (v, u), 0) + 1
    open_edges = sum(1 for n in edge_use.values() if n == 1)
    nonmanifold = sum(1 for n in edge_use.values() if n > 2)

    # --- proportion: sorted extents, Zingg class ---------------------------
    a, b, c = sorted(ext, reverse=True)            # a >= b >= c
    elong = (b / a) if a > 0 else 0.0              # b/a
    flat = (c / b) if b > 0 else 0.0               # c/b
    # Zingg (1935) splits gravel shape on b/a and c/b at 2/3.  Real gravel
    # populations sit mostly in blade+disc; a procedural generator that only
    # ever emits `equant` is emitting balls, and that is the single most
    # "procedural" silhouette there is.
    zingg = (("equant" if flat > 2 / 3 else "disc") if elong > 2 / 3
             else ("rod" if flat > 2 / 3 else "blade"))

    bbox_vol = ext[0] * ext[1] * ext[2]
    occupancy = (volume / bbox_vol) if bbox_vol > 1e-18 else 0.0

    # --- flatness tells ----------------------------------------------------
    # dominant_face_share: the biggest coplanar region as a fraction of surface
    # area.  This is the metric that catches "you jittered a cube's 8 corners,
    # so all six faces are still single planes".
    cos_co = math.cos(math.radians(COPLANAR_DEG))
    dominant = 0.0
    probe = faces if len(faces) <= 3000 else faces[::max(1, len(faces) // 3000)]
    for _, n0 in probe:
        s = 0.0
        for area, n in faces:
            if n0[0] * n[0] + n0[1] * n[1] + n0[2] * n[2] >= cos_co:
                s += area
        dominant = max(dominant, s)
    dominant_share = dominant / total_area if total_area > 0 else 0.0

    # normal_regions_80: how many distinct facing directions it takes to
    # account for 80% of the surface.  THIS is the number that catches
    # "you jittered a cube's 8 corners".  Jittering moves vertices but not
    # face count, so a jittered box still has 6 facing directions and reads as
    # a box no matter how far the corners travel; irregularity is bounded
    # above by face count, and this measures the bound rather than the intent.
    # Anchors: cube 5, uv-sphere(24x12) ~50+.
    cos_reg = math.cos(math.radians(REGION_DEG))
    remaining = list(faces)
    regions, covered = 0, 0.0
    target = total_area * 0.80
    while remaining and covered < target:
        best_n, best_s = None, -1.0
        for _, n0 in remaining:
            acc = sum(area for area, n in remaining
                      if n0[0] * n[0] + n0[1] * n[1] + n0[2] * n[2] >= cos_reg)
            if acc > best_s:
                best_s, best_n = acc, n0
        covered += best_s
        regions += 1
        remaining = [(area, n) for area, n in remaining
                     if (best_n[0] * n[0] + best_n[1] * n[1]
                         + best_n[2] * n[2]) < cos_reg]
        if regions > 400:                          # runaway guard
            break

    cos_up = math.cos(math.radians(UPFACE_DEG))
    up_area = sum(area for area, n in faces if n[up] >= cos_up)
    up_share = up_area / total_area if total_area > 0 else 0.0
    largest_share = largest / total_area if total_area > 0 else 0.0

    # --- plan-view silhouette ---------------------------------------------
    # Measured on the plan-view convex HULL, sampled by ray-cast at fixed
    # angles -- not by binning the raw point cloud.  Binning the cloud makes
    # the number depend on how many segments the primitive happened to have
    # (a 24-column sphere leaves a third of the bins empty and invents
    # variation that is not in the shape), and a metric whose value moves when
    # the tessellation moves is not measuring the silhouette.
    plan = [(v[ax[0]], v[ax[1]]) for v in verts]
    ph = hull_2d(plan)
    hull_area = poly_area(ph)
    radial_cv = _hull_radial_cv(ph)
    # `plan_hull_area_m2` below is reported in absolute m2, not only as the
    # `plan_hull_fill` ratio. A dressing planner needs "how much floor does one
    # of these hide"; without the absolute figure it has to reconstruct the
    # area from the ratio and the bbox, and to do THAT it has to know which two
    # of the three bbox axes are the ground plane -- the up-axis question,
    # asked again in a consumer that had no reason to ask it. The measurement
    # belongs with the measurer.
    foot_bbox = ext[ax[0]] * ext[ax[1]]
    hull_fill = hull_area / foot_bbox if foot_bbox > 1e-18 else 0.0

    # --- ground contact ----------------------------------------------------
    eps = max(1e-6, ext[up] * 0.02)
    base_pts = [(v[ax[0]], v[ax[1]]) for v in verts if v[up] - lo[up] <= eps]
    base_area = poly_area(hull_2d(base_pts)) if len(base_pts) >= 3 else 0.0
    base_ratio = base_area / hull_area if hull_area > 1e-18 else 0.0

    # --- per-island proportion -------------------------------------------
    isl = components(verts, tris)
    props = [_proportion(verts, g, up) for g in isl]
    zcount = {}
    for pr in props:
        zcount[pr["zingg"]] = zcount.get(pr["zingg"], 0) + 1

    return {
        "tris": len(tris),
        "verts": len(verts),
        "verts_in_file": raw_verts,
        "components": len(isl),
        "part_elongation_ba": round(_median([p["elongation_ba"] for p in props]), 3),
        "part_flatness_cb": round(_median([p["flatness_cb"] for p in props]), 3),
        "part_extent_up_max": round(max([p["extent_up"] for p in props] or [0.0]), 5),
        "part_zingg": ",".join(f"{k}:{v}" for k, v in sorted(zcount.items())),
        "bbox": [round(e, 5) for e in ext],
        "extent_up": round(ext[up], 5),
        "base_at": round(lo[up], 5),
        "axis_abc": [round(a, 5), round(b, 5), round(c, 5)],
        "elongation_ba": round(elong, 3),
        "flatness_cb": round(flat, 3),
        "zingg": zingg,
        "volume": round(volume, 8),
        "open_edges": open_edges,
        "nonmanifold_edges": nonmanifold,
        "closed": open_edges == 0 and nonmanifold == 0,
        "surface_area": round(total_area, 6),
        "bbox_occupancy": round(occupancy, 3),
        "dominant_face_share": round(dominant_share, 3),
        "normal_regions_80": regions,
        "up_facing_share": round(up_share, 3),
        "largest_face_share": round(largest_share, 3),
        "plan_radial_cv": round(radial_cv, 3),
        "plan_hull_fill": round(hull_fill, 3),
        "plan_hull_area_m2": round(hull_area, 6),
        "base_contact_ratio": round(base_ratio, 3),
    }


def glb_metrics(path, up=1):
    """Metrics for a GLB, merging every triangle primitive into one soup.

    Merging is correct for these species: a `pebble` specimen is three stones
    that ship as one mesh and are seen as one clump.  For a multi-part asset
    the caller wants per-primitive numbers instead -- use `glb_primitives`.
    """
    gltf, blob = read_glb(path)
    verts, tris = [], []
    for pos, idx in glb_primitives(gltf, blob):
        off = len(verts)
        verts.extend(pos)
        tris.extend([(i + off, j + off, k + off) for (i, j, k) in idx])
    m = mesh_metrics(verts, tris, up=up)
    m["file"] = os.path.basename(path)
    b = glb_bounds(gltf)
    if b:
        m["accessor_extent_up"] = round(b[1][up] - b[0][up], 5)
    return m


# --------------------------------------------------------------------------
# PATCH metrics -- the unit that actually reads on screen
# --------------------------------------------------------------------------

def patch_metrics(points, area=None):
    """Distribution statistics for a scatter of placements.

    `points` is a sequence of (x, y) ground positions.  `area` is the region
    they were scattered over; when omitted the convex hull of the points is
    used, which UNDERSTATES area for a clustered set and therefore biases R
    upward -- pass the real region area when the caller knows it.

    Clark & Evans (1954) R = observed mean nearest-neighbour distance divided
    by the mean expected under complete spatial randomness (0.5 / sqrt(density)).

        R  < 1   clustered      <- what real debris does
        R == 1   random
        R  > 1   dispersed      <- what a naive even scatter does; R = 2.0 for
                                   a perfect square lattice

    This is `docs/SURFACE_DRESSING.md`'s "no obvious uniform scatter pattern"
    expressed as something a test can assert on.
    """
    n = len(points)
    if n < 3:
        return {"n": n, "error": "need at least 3 points"}
    nn = []
    for i, (x1, y1) in enumerate(points):
        best = float("inf")
        for j, (x2, y2) in enumerate(points):
            if i == j:
                continue
            d = (x1 - x2) ** 2 + (y1 - y2) ** 2
            if d < best:
                best = d
        nn.append(math.sqrt(best))
    mean_nn = sum(nn) / n
    var = sum((d - mean_nn) ** 2 for d in nn) / n
    cv = math.sqrt(var) / mean_nn if mean_nn > 0 else 0.0

    if area is None:
        area = poly_area(hull_2d(list(points)))
    density = (n / area) if area and area > 0 else 0.0
    expected = 0.5 / math.sqrt(density) if density > 0 else 0.0
    R = (mean_nn / expected) if expected > 0 else 0.0
    reading = ("clustered" if R < 0.85
               else ("random" if R < 1.15 else "dispersed"))
    return {
        "n": n,
        "mean_nn": round(mean_nn, 5),
        "nn_cv": round(cv, 3),
        "density": round(density, 4),
        "clark_evans_R": round(R, 3),
        "reading": reading,
    }


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------

def _unit_cube():
    v = [(x, y, z) for z in (0.0, 1.0) for y in (0.0, 1.0) for x in (0.0, 1.0)]
    # 0:(0,0,0) 1:(1,0,0) 2:(0,1,0) 3:(1,1,0) 4:(0,0,1) 5:(1,0,1) 6:(0,1,1) 7:(1,1,1)
    q = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4),
         (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    t = []
    for a, b, c, d in q:
        t += [(a, b, c), (a, c, d)]
    return v, t


def _slab(h):
    v, t = _unit_cube()
    return [(x, y, z * h) for (x, y, z) in v], t


def _uv_sphere(u=24, vseg=12, r=0.5):
    verts, tris = [], []
    for i in range(vseg + 1):
        phi = math.pi * i / vseg
        for j in range(u):
            th = 2 * math.pi * j / u
            verts.append((r * math.sin(phi) * math.cos(th),
                          r * math.sin(phi) * math.sin(th),
                          r * math.cos(phi) + r))
    for i in range(vseg):
        for j in range(u):
            a = i * u + j
            b = i * u + (j + 1) % u
            c = (i + 1) * u + j
            d = (i + 1) * u + (j + 1) % u
            tris += [(a, c, d), (a, d, b)]
    return verts, tris


def _fail(msg, got):
    print(f"  FAIL  {msg}  (got {got})")
    return 1


def selftest():
    bad = 0
    print(f"shape_metrics {VERSION} selftest (up=2, Z-up, for these fixtures)")

    cube = mesh_metrics(*_unit_cube(), up=2)
    print("  cube          ", {k: cube[k] for k in
                               ("bbox_occupancy", "normal_regions_80",
                                "dominant_face_share",
                                "plan_hull_fill", "zingg", "base_contact_ratio")})
    if abs(cube["bbox_occupancy"] - 1.0) > 0.01:
        bad += _fail("cube occupancy should be 1.0", cube["bbox_occupancy"])
    if abs(cube["plan_hull_fill"] - 1.0) > 0.01:
        bad += _fail("cube plan hull fill should be 1.0", cube["plan_hull_fill"])
    if cube["zingg"] != "equant":
        bad += _fail("cube should be equant", cube["zingg"])
    if abs(cube["dominant_face_share"] - 1 / 6) > 0.01:
        bad += _fail("cube dominant face share should be 1/6",
                     cube["dominant_face_share"])
    if abs(cube["base_contact_ratio"] - 1.0) > 0.01:
        bad += _fail("cube sits flat, base contact should be 1.0",
                     cube["base_contact_ratio"])
    if not cube["closed"] or cube["open_edges"]:
        bad += _fail("a cube is a closed surface",
                     (cube["open_edges"], cube["nonmanifold_edges"]))
    # FALSIFICATION: a hole must be detected. Drop one triangle and the
    # closedness test has to fail; if it still passes it is testing nothing.
    cv, ct = _unit_cube()
    holed = mesh_metrics(cv, ct[:-1], up=2)
    if holed["closed"] or holed["open_edges"] != 3:
        bad += _fail("removing a triangle must open exactly 3 edges",
                     (holed["closed"], holed["open_edges"]))
    if cube["normal_regions_80"] != 5:
        bad += _fail("a cube needs 5 of its 6 faces to cover 80% of area",
                     cube["normal_regions_80"])

    sph = mesh_metrics(*_uv_sphere(), up=2)
    print("  sphere        ", {k: sph[k] for k in
                               ("bbox_occupancy", "normal_regions_80",
                                "dominant_face_share",
                                "plan_hull_fill", "plan_radial_cv",
                                "base_contact_ratio")})
    if abs(sph["bbox_occupancy"] - math.pi / 6) > 0.03:
        bad += _fail("sphere occupancy should be pi/6 = 0.524",
                     sph["bbox_occupancy"])
    if abs(sph["plan_hull_area_m2"] - math.pi * 0.25) > 0.03:
        bad += _fail("a unit-diameter sphere's plan hull is pi/4 m2",
                     sph["plan_hull_area_m2"])
    if abs(cube["plan_hull_area_m2"] - 1.0) > 0.01:
        bad += _fail("a unit cube's plan hull is 1 m2",
                     cube["plan_hull_area_m2"])
    if abs(sph["plan_hull_fill"] - math.pi / 4) > 0.03:
        bad += _fail("sphere plan hull fill should be pi/4 = 0.785",
                     sph["plan_hull_fill"])
    if sph["plan_radial_cv"] > 0.02:
        bad += _fail("a circle has no radial variation", sph["plan_radial_cv"])
    if sph["normal_regions_80"] < 20:
        bad += _fail("a sphere has many facing directions",
                     sph["normal_regions_80"])
    # FALSIFICATION: normal_regions_80 is the criterion-3 instrument; if it
    # cannot separate a 6-faced solid from a tessellated one it is measuring
    # nothing.
    if sph["normal_regions_80"] <= cube["normal_regions_80"] * 2:
        bad += _fail("normal_regions_80 fails to separate sphere from cube",
                     (sph["normal_regions_80"], cube["normal_regions_80"]))
    # FALSIFICATION: a ball must not look like a box on the metric that is
    # supposed to tell them apart.  If this ever passes, occupancy is broken.
    if abs(sph["bbox_occupancy"] - cube["bbox_occupancy"]) < 0.3:
        bad += _fail("occupancy fails to separate sphere from cube",
                     (sph["bbox_occupancy"], cube["bbox_occupancy"]))
    if sph["base_contact_ratio"] > 0.15:
        bad += _fail("a sphere touches the ground at a point, not a face",
                     sph["base_contact_ratio"])
    # FALSIFICATION: contact must separate "sits flat" from "rests on a point".
    if sph["base_contact_ratio"] >= cube["base_contact_ratio"] * 0.5:
        bad += _fail("base_contact_ratio fails to separate sphere from cube",
                     (sph["base_contact_ratio"], cube["base_contact_ratio"]))
    if cube["plan_radial_cv"] <= sph["plan_radial_cv"]:
        bad += _fail("a square plan must be less round than a circular one",
                     (cube["plan_radial_cv"], sph["plan_radial_cv"]))

    slab = mesh_metrics(*_slab(0.1), up=2)
    print("  slab 1x1x0.1  ", {k: slab[k] for k in
                               ("up_facing_share", "dominant_face_share",
                                "zingg", "flatness_cb")})
    if abs(slab["up_facing_share"] - 1 / 2.4) > 0.02:
        bad += _fail("slab up-facing share should be 1/2.4 = 0.417",
                     slab["up_facing_share"])
    if slab["zingg"] != "disc":
        bad += _fail("a 1x1x0.1 slab is a disc in Zingg terms", slab["zingg"])
    # FALSIFICATION: the flat-top tell must fire on the slab and not on the cube.
    if slab["up_facing_share"] <= cube["up_facing_share"]:
        bad += _fail("up_facing_share fails to separate slab from cube",
                     (slab["up_facing_share"], cube["up_facing_share"]))

    # --- welding and islands ----------------------------------------------
    cv, ct = _unit_cube()
    # Simulate what a glTF exporter does: give every triangle its own copy of
    # its three vertices, exactly as a UV/normal split would.
    split_v, split_t = [], []
    for (i, j, k) in ct:
        n = len(split_v)
        split_v += [cv[i], cv[j], cv[k]]
        split_t.append((n, n + 1, n + 2))
    split = mesh_metrics(split_v, split_t, up=2)
    print("  split cube    ", {k: split[k] for k in
                               ("verts_in_file", "verts", "open_edges",
                                "closed", "components")})
    if split["verts_in_file"] != 36 or split["verts"] != 8:
        bad += _fail("welding must take 36 split vertices back to 8",
                     (split["verts_in_file"], split["verts"]))
    # FALSIFICATION: this is the exact bug welding exists to kill. Without it
    # a fully split cube reports every edge open. If this ever regresses, the
    # tool calls every correct exported asset broken.
    if not split["closed"] or split["open_edges"]:
        bad += _fail("a split-vertex cube must weld back to a closed surface",
                     (split["closed"], split["open_edges"]))
    if split["components"] != 1:
        bad += _fail("a welded cube is one island", split["components"])

    # two cubes side by side: the clump is elongated, each part is not.
    two_v = list(cv) + [(x + 4.0, y, z) for (x, y, z) in cv]
    two_t = list(ct) + [(i + 8, j + 8, k + 8) for (i, j, k) in ct]
    two = mesh_metrics(two_v, two_t, up=2)
    print("  two cubes     ", {k: two[k] for k in
                               ("components", "elongation_ba",
                                "part_elongation_ba", "part_zingg")})
    if two["components"] != 2:
        bad += _fail("two separated cubes are two islands", two["components"])
    # FALSIFICATION: the whole reason part_* exists. The clump reads as a rod
    # (b/a = 0.2); each cube is equant. If these ever agree, the per-island
    # split is not happening and the Zingg class is describing the scatter.
    if abs(two["part_elongation_ba"] - 1.0) > 0.01:
        bad += _fail("each cube is equant in isolation",
                     two["part_elongation_ba"])
    if two["elongation_ba"] > 0.5:
        bad += _fail("the clump of two spaced cubes should read elongated",
                     two["elongation_ba"])
    if two["part_zingg"] != "equant:2":
        bad += _fail("both islands should classify equant", two["part_zingg"])

    # --- patch statistics --------------------------------------------------
    lattice = [(i * 1.0, j * 1.0) for i in range(12) for j in range(12)]
    # Area is 12x12, not 11x11: each of the 144 points owns a 1x1 cell.
    # Using the hull area (11x11) undercounts the region and inflates R --
    # which is exactly the bias the docstring warns about, demonstrated.
    lat = patch_metrics(lattice, area=12.0 * 12.0)
    print("  lattice 12x12 ", {k: lat[k] for k in ("clark_evans_R", "nn_cv",
                                                   "reading")})
    if abs(lat["clark_evans_R"] - 2.0) > 0.06:
        bad += _fail("square lattice R should be 2.0", lat["clark_evans_R"])
    if lat["reading"] != "dispersed":
        bad += _fail("a lattice must read as dispersed", lat["reading"])

    import random as _r
    rnd = _r.Random(1999)
    poisson = [(rnd.uniform(0, 11), rnd.uniform(0, 11)) for _ in range(144)]
    poi = patch_metrics(poisson, area=11.0 * 11.0)
    print("  poisson n=144 ", {k: poi[k] for k in ("clark_evans_R", "nn_cv",
                                                   "reading")})
    if not 0.85 <= poi["clark_evans_R"] <= 1.15:
        bad += _fail("Poisson R should sit near 1.0", poi["clark_evans_R"])

    clustered = []
    for _ in range(12):
        cx, cy = rnd.uniform(0, 11), rnd.uniform(0, 11)
        for _ in range(12):
            clustered.append((cx + rnd.gauss(0, 0.18), cy + rnd.gauss(0, 0.18)))
    clu = patch_metrics(clustered, area=11.0 * 11.0)
    print("  clustered     ", {k: clu[k] for k in ("clark_evans_R", "nn_cv",
                                                   "reading")})
    if clu["clark_evans_R"] >= 0.6:
        bad += _fail("tight clusters should give R well under 1",
                     clu["clark_evans_R"])
    # FALSIFICATION: the three regimes must be ORDERED, not merely computed.
    if not (clu["clark_evans_R"] < poi["clark_evans_R"] < lat["clark_evans_R"]):
        bad += _fail("R fails to order clustered < random < dispersed",
                     (clu["clark_evans_R"], poi["clark_evans_R"],
                      lat["clark_evans_R"]))
    if clu["nn_cv"] <= poi["nn_cv"]:
        bad += _fail("clustered spacing must vary more than Poisson",
                     (clu["nn_cv"], poi["nn_cv"]))

    print("SELFTEST", "PASSED" if bad == 0 else f"FAILED ({bad})")
    return 1 if bad else 0


# --------------------------------------------------------------------------

# Aggregate columns describe the CLUMP; `part_*` columns describe the
# individual islands inside it.  On a single-island asset they agree.
#
# Short headers with a legend, not full metric names.  0.2.0 printed fifteen
# 19-character columns, which is a 330-character line: on a normal console the
# rightmost columns -- including `open_edges`, the one the release was about --
# fell off the edge and were reported as missing. A table wider than the
# terminal is a table nobody reads.
_TABLE = [
    ("tris", "tris"),
    ("components", "parts"),
    ("extent_up", "up_m"),
    ("part_extent_up_max", "part_up"),
    ("part_zingg", "zingg"),
    ("part_elongation_ba", "b/a"),
    ("part_flatness_cb", "c/b"),
    ("bbox_occupancy", "occ"),
    ("normal_regions_80", "regs"),
    ("up_facing_share", "upface"),
    ("plan_radial_cv", "radcv"),
    ("plan_hull_fill", "hullfil"),
    ("base_contact_ratio", "contact"),
    ("open_edges", "open"),
    ("nonmanifold_edges", "nonman"),
    ("base_at", "base_at"),
]

_LEGEND = [
    "parts   = connected islands in the mesh (proportion is measured per island)",
    "up_m    = height of the whole clump; part_up = tallest single island",
    "zingg   = Zingg class per island (equant/disc/rod/blade), 2/3 thresholds",
    "b/a,c/b = median island elongation and flatness",
    "occ     = volume / bbox volume;  regs = facing directions covering 80% of area",
    "upface  = area facing up within 20 deg;  radcv/hullfil = plan-view silhouette",
    "contact = footprint touching the base plane, as a share of the plan hull",
    "open    = unpaired edges after welding (holes);  nonman = edges on >2 faces",
]


def _fmt(v):
    return "-" if v is None else str(v)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--dir", help="measure every *.glb under this folder")
    ap.add_argument("--up", type=int, default=1,
                    help="index of the up axis (1 = glTF Y-up, default)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", help="write the report here instead of stdout. "
                                  "A level_factory PlannedCommand is argv "
                                  "without a shell, so `> file` is not "
                                  "available to it and a tool that only "
                                  "writes to stdout cannot be a pipeline step.")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--version", action="store_true")
    args = ap.parse_args(argv)

    if args.version:
        print(VERSION)
        return 0
    if args.selftest:
        return selftest()

    paths = list(args.files)
    if args.dir:
        paths += sorted(glob.glob(os.path.join(args.dir, "**", "*.glb"),
                                  recursive=True))
    if not paths:
        ap.print_help()
        return 2

    rows = []
    for p in paths:
        try:
            rows.append(glb_metrics(p, up=args.up))
        except Exception as exc:                   # noqa: BLE001 - report, continue
            rows.append({"file": os.path.basename(p), "error": str(exc)})

    if args.json:
        text = json.dumps(rows, indent=1)
        if args.out:
            with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
        else:
            print(text)
        return 0

    w = max([len(r.get("file", "?")) for r in rows] + [4])
    widths = []
    for key, label in _TABLE:
        widths.append(max([len(label)]
                          + [len(_fmt(r.get(key))) for r in rows if "error" not in r]))
    print(f"{'file':<{w}}  "
          + "  ".join(f"{lab:>{wd}}" for (_, lab), wd in zip(_TABLE, widths)))
    for r in rows:
        if "error" in r:
            print(f"{r['file']:<{w}}  ERROR: {r['error']}")
            continue
        print(f"{r['file']:<{w}}  "
              + "  ".join(f"{_fmt(r.get(k)):>{wd}}"
                          for (k, _), wd in zip(_TABLE, widths)))
    print()
    for line in _LEGEND:
        print("  " + line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
