"""Do Blender jobs build the same models three at a time as one at a time?

Level Factory's `blender` cap is 1 (TDD 19.2, never measured) and cold run 9250's art leg ran about
102 s of Blender jobs one after another. Cold run 9251 ran with `LF_CONCURRENCY=blender=3`. The
control is two runs at one: 9249 and 9250, the same inputs, already differ in seven GLBs -- and in
the one read closely (the clutter's pebble) only in the ORDER of its triangles: the same JSON, the
same vertex data, the same 192 triangles with the same winding. So each Blender job's outputs are
compared file by file and a GLB that differs is classed:

    identical    the same bytes
    equivalent   the same JSON chunk, the same bytes in every buffer view but the index views,
                 and each primitive's triangles the same set with the same winding
    DIFFERENT    anything else -- the class that would refuse the wider width

It prints the classes for the control (9249 against 9250) and for the change (9250 against 9251)
side by side, per job kind. It measures and prints.

    python docs/findings/grader_speed/blender_width_compare.py 9249 9250 9251

That run read workspaces/cold-9249-ws, workspaces/cold-9250-ws and workspaces/cold-9251-ws, named in
full here so tools/factory_retire.py sees them. On 2026-10-13 only cold-9251-ws is on disk.
"""
import collections
import glob
import json
import os
import struct
import sys

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
KINDS = ("zoo_clutter_build", "zoo_fixtures_build", "zoo_kit_build", "zoo_roof_props_build",
         "zoo_dressing_build", "deli_generate")


def _glb(path):
    b = open(path, "rb").read()
    off, chunks = 12, []
    while off < len(b):
        clen, _ = struct.unpack_from("<II", b, off)
        chunks.append(b[off + 8: off + 8 + clen])
        off += 8 + clen
    return json.loads(chunks[0].decode("utf-8").rstrip(" \x00")), (chunks[1] if len(chunks) > 1 else b"")


def _views(js, bin_):
    return [bin_[v.get("byteOffset", 0): v.get("byteOffset", 0) + v["byteLength"]]
            for v in js.get("bufferViews", [])]


def _triangles(js, bin_, acc_i):
    a = js["accessors"][acc_i]
    bv = js["bufferViews"][a["bufferView"]]
    fmt = {5121: "B", 5123: "H", 5125: "I"}[a["componentType"]]
    idx = struct.unpack_from("<%d%s" % (a["count"], fmt), bin_, bv.get("byteOffset", 0) + a.get("byteOffset", 0))
    canon = lambda t: min(t[i:] + t[:i] for i in range(3))
    return sorted(canon(tuple(idx[i:i + 3])) for i in range(0, len(idx), 3))


#: How far two normals' components may sit apart and still be the same normal: float32 sums taken
#: in another order (the control's water tower and trash bags differ in their normals and nothing
#: else but triangle order) move the last bits, which is 1e-7 at unit length.
NORMAL_EPS = 1e-4
_WS = __import__("re").compile(rb"cold-\d+-ws")


def classify(pa, pb):
    """See the module docstring; `.blend` files are Blender's own scenes, which carry per-save data
    and never match byte for byte, so they are set aside rather than compared."""
    if pa.endswith(".blend"):
        return "blend, not compared"
    a, b = open(pa, "rb").read(), open(pb, "rb").read()
    if a == b:
        return "identical"
    if not pa.endswith(".glb"):
        # a workspace's own name in a text file is not a difference in what was built
        return "identical but the workspace's name" if _WS.sub(b"ws", a) == _WS.sub(b"ws", b) else "DIFFERENT"
    try:
        ja, ba = _glb(pa)
        jb, bb = _glb(pb)
    except Exception:
        return "DIFFERENT"
    if ja != jb:
        return "DIFFERENT"
    index_views = {ja["accessors"][p["indices"]]["bufferView"]
                   for m in ja.get("meshes", []) for p in m["primitives"] if "indices" in p}
    normal_views = {ja["accessors"][ai]["bufferView"]
                    for m in ja.get("meshes", []) for p in m["primitives"]
                    for name, ai in p.get("attributes", {}).items() if name in ("NORMAL", "TANGENT")}
    va, vb = _views(ja, ba), _views(jb, bb)
    if len(va) != len(vb):
        return "DIFFERENT"
    for i in range(len(va)):
        if va[i] == vb[i] or i in index_views:
            continue
        if i in normal_views and len(va[i]) == len(vb[i]) and len(va[i]) % 4 == 0:
            fa = struct.unpack("<%df" % (len(va[i]) // 4), va[i])
            fb = struct.unpack("<%df" % (len(vb[i]) // 4), vb[i])
            if all(abs(x - y) <= NORMAL_EPS for x, y in zip(fa, fb)):
                continue
        return "DIFFERENT"
    for m in ja.get("meshes", []):
        for p in m["primitives"]:
            if "indices" in p and _triangles(ja, ba, p["indices"]) != _triangles(jb, bb, p["indices"]):
                return "DIFFERENT"
    return "equivalent"


def outputs(run, kind):
    root = os.path.join(F, "workspaces", "cold-%s-ws" % run, ".level_factory", "jobs")
    out = {}
    for job in glob.glob(os.path.join(root, "restaurant_row_001.%s*" % kind)):
        attempts = sorted(glob.glob(os.path.join(job, "*", "out")))
        if not attempts:
            continue
        base = attempts[-1]
        for r, _, fs in os.walk(base):
            for f in fs:
                if f.endswith(".provenance.json"):
                    continue
                p = os.path.join(r, f)
                out[os.path.basename(job) + "/" + os.path.relpath(p, base).replace("\\", "/")] = p
    return out


def compare(x, y):
    """``({kind: Counter of classes}, {names DIFFERENT or on one side only})``."""
    table, bad = {}, set()
    for kind in KINDS:
        ox, oy = outputs(x, kind), outputs(y, kind)
        c = collections.Counter()
        for k in sorted(set(ox) & set(oy)):
            cls = classify(ox[k], oy[k])
            c[cls] += 1
            if cls == "DIFFERENT":
                bad.add(k)
        c["only one side"] = len(set(ox) ^ set(oy))
        bad |= set(ox) ^ set(oy)
        table[kind] = c
    return table, bad


def main():
    """``<control runs at the old width...> <the run at the new width>``: every adjacent pair of
    control runs is a control, and the last control against the new run is the change. The
    verdict: no file differs in the change that does not differ in some control -- the controls
    already vary (the module docstring), so a wider width may not add a file to that set."""
    runs = sys.argv[1:]
    assert len(runs) >= 3, "two control runs at the old width at least, then the new run"
    controls, union = [], set()
    for x, y in zip(runs[:-2], runs[1:-1]):
        table, bad = compare(x, y)
        controls.append(("control %s against %s" % (x, y), table))
        union |= bad
    change, change_bad = compare(runs[-2], runs[-1])
    fmt = lambda t: ", ".join("%s %d" % (k, v) for k, v in sorted(t.items()) if v)
    for label, table in controls + [("CHANGE %s against %s" % (runs[-2], runs[-1]), change)]:
        print(label)
        for kind in KINDS:
            print("    %-22s %s" % (kind, fmt(table[kind])))
    new = sorted(change_bad - union)
    print("\nfiles different in some control: %d; different in the change: %d; in the change and in no control: %d"
          % (len(union), len(change_bad), len(new)))
    for k in new[:20]:
        print("    NEW: " + k)


if __name__ == "__main__":
    main()
