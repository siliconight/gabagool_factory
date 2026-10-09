"""What differs between two exported packages, file by file, and inside each
differing GLB, byte by byte (roadmap 214, trial 1).

    python pkg_diff.py <package A> <package B>

Run on cold run 9210's package (Zoo 1.86.0) and 9211's (Zoo 1.87.0), which
differ in Zoo alone. Prints:
- files only in A, only in B, and in both with different bytes, grouped by
  extension;
- for each GLB that differs: whether its JSON chunk is identical, and how many
  differing bytes of its binary chunk fall inside a NORMAL accessor's range
  and how many outside. Weighting moves normals and nothing else, so the
  claim to test is "all inside";
- the first few differing files of any other kind, by name.
Skips `.godot/` (an import cache, regenerated on open). Prints what it
measured and stops. A GLB it cannot parse is reported, not skipped.
"""
import collections
import hashlib
import json
import os
import struct
import sys

A, B = sys.argv[1], sys.argv[2]


def files(root):
    out = {}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d != ".godot"]
        for f in fn:
            p = os.path.join(dp, f)
            out[os.path.relpath(p, root).replace("\\", "/")] = p
    return out


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def chunks(p):
    data = open(p, "rb").read()
    jlen = struct.unpack_from("<I", data, 12)[0]
    js = data[20:20 + jlen]
    blen = struct.unpack_from("<I", data, 20 + jlen)[0]
    return json.loads(js), js, data[28 + jlen:28 + jlen + blen]


def normal_ranges(doc):
    spans = []
    for mesh in doc.get("meshes", []):
        for prim in mesh["primitives"]:
            i = prim["attributes"].get("NORMAL")
            if i is None:
                continue
            a = doc["accessors"][i]
            bv = doc["bufferViews"][a["bufferView"]]
            start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
            stride = bv.get("byteStride") or 12
            spans.append((start, start + stride * (a["count"] - 1) + 12))
    return spans


def owner(doc, k):
    """Which primitive attribute's accessor holds binary byte ``k``, by name
    (`indices` for an index buffer); None when no accessor covers it."""
    for mesh in doc.get("meshes", []):
        for prim in mesh["primitives"]:
            named = dict(prim["attributes"])
            if "indices" in prim:
                named["indices"] = prim["indices"]
            for name, i in named.items():
                a = doc["accessors"][i]
                bv = doc["bufferViews"][a["bufferView"]]
                start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
                if start <= k < start + bv["byteLength"] - a.get("byteOffset", 0):
                    return name
    return None


fa, fb = files(A), files(B)
only_a = sorted(set(fa) - set(fb))
only_b = sorted(set(fb) - set(fa))
both = sorted(set(fa) & set(fb))
diff = [r for r in both if os.path.getsize(fa[r]) != os.path.getsize(fb[r]) or sha(fa[r]) != sha(fb[r])]
print(f"files: A {len(fa)}, B {len(fb)}; only in A {len(only_a)}, only in B {len(only_b)}, "
      f"in both {len(both)}, differing {len(diff)}")
for label, rows in (("only in A", only_a), ("only in B", only_b)):
    for r in rows[:10]:
        print(f"  {label}: {r}")
by_ext = collections.Counter(os.path.splitext(r)[1].lower() or "(none)" for r in diff)
print("differing, by extension:", dict(sorted(by_ext.items())))

def _acc(doc, binary, i):
    a = doc["accessors"][i]
    bv = doc["bufferViews"][a["bufferView"]]
    off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    n = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}[a["type"]]
    fmt = {5126: "f", 5123: "H", 5125: "I", 5121: "B"}[a["componentType"]]
    stride = bv.get("byteStride") or struct.calcsize("<" + fmt * n)
    return [struct.unpack_from("<" + fmt * n, binary, off + k * stride)
            for k in range(a["count"])]


def _triangles(doc, binary):
    """Every triangle as its corners' (position, uv, colour), rotated to start
    at its smallest corner so the winding is kept and the start is not."""
    out = collections.Counter()
    for m, mesh in enumerate(doc.get("meshes", [])):
        for p, prim in enumerate(mesh["primitives"]):
            att = prim["attributes"]
            cols = [_acc(doc, binary, att[k]) for k in ("POSITION", "TEXCOORD_0", "COLOR_0")
                    if k in att]
            idx = [t[0] for t in _acc(doc, binary, prim["indices"])]
            for t in range(0, len(idx), 3):
                c = [tuple(col[i] for col in cols) for i in idx[t:t + 3]]
                k = c.index(min(c))
                out[(m, p, tuple(c[k:] + c[:k]))] += 1
    return out


def same_triangles(da, ba, db, bb):
    """True when both files hold the same triangles, ignoring vertex order."""
    return _triangles(da, ba) == _triangles(db, bb)


glbs = [r for r in diff if r.lower().endswith(".glb")]
inside = outside = js_differs = unparsed = reordered = 0
outside_by = collections.Counter()
for r in glbs:
    try:
        da, ja, ba = chunks(fa[r])
        db, jb, bb = chunks(fb[r])
    except Exception as exc:                          # reported, not skipped
        unparsed += 1
        print(f"  GLB not parsed: {r}: {type(exc).__name__}: {exc}")
        continue
    if ja != jb:
        js_differs += 1
        print(f"  GLB JSON chunk differs: {r}")
        continue
    spans = normal_ranges(da)
    n_in = n_out = 0
    where = collections.Counter()
    for k in range(min(len(ba), len(bb))):
        if ba[k] != bb[k]:
            if any(s <= k < e for s, e in spans):
                n_in += 1
            else:
                n_out += 1
                where[owner(da, k)] += 1
    n_out += abs(len(ba) - len(bb))
    inside += n_in
    outside += n_out
    outside_by.update(where)
    if n_out:
        same = same_triangles(da, ba, db, bb)
        reordered += same
        print(f"  GLB bytes differ OUTSIDE normals: {r}: {n_out} (inside {n_in}), "
              f"in {dict(where)}; triangles (position, uv, colour) the same as "
              f"multisets: {same}")
print(f"GLBs differing: {len(glbs)}; JSON chunk differs in {js_differs}; not parsed {unparsed}; "
      f"differing binary bytes inside NORMAL ranges {inside}, outside {outside}, "
      f"the outside ones by attribute {dict(outside_by)}; GLBs with bytes outside "
      f"whose triangles are the same multiset: {reordered}")
other = [r for r in diff if not r.lower().endswith(".glb")]
derived = [r for r in other if r.endswith((".import", ".unwrap_cache"))]
glb_names = set(glbs)
orphans = [r for r in derived if r.rsplit(".", 1)[0] not in glb_names]
print(f"other differing files: {len(other)}; Godot import sidecars and unwrap caches "
      f"{len(derived)}, of which {len(orphans)} belong to no differing GLB")
for r in orphans[:25]:
    print(f"  sidecar of an unchanged file: {r}")
for r in [r for r in other if r not in derived]:
    print(f"  {r}  ({os.path.getsize(fa[r])} -> {os.path.getsize(fb[r])} bytes)")
