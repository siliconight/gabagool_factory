"""Minimal read-only decoder for Godot 4 binary resources (RSRC, uncompressed).

Follows core/io/resource_format_binary.cpp's loader: header, string table,
external and internal resource tables, then each internal resource's
properties (name = string-table index, value = tagged variant).

Usage: python -B rsrc_read.py <root> [--dump N]
Reports, over every .res under <root>:
  * StandardMaterial3D sub-resources: cull_mode, transparency,
    vertex_color_use_as_albedo values (absent = not stored);
  * ArrayMesh: surface count, whether any surface dict has a 'lods' key,
    lightmap_size_hint, shadow_mesh, custom_aabb, blend shapes.
An unrecognised variant tag raises, so an unknown shape FAILS loudly.
"""
import os
import struct
import sys
from collections import Counter, defaultdict

V_NIL, V_BOOL, V_INT, V_FLOAT, V_STRING = 1, 2, 3, 4, 5
V_VEC2, V_RECT2, V_VEC3, V_PLANE, V_QUAT, V_AABB, V_BASIS, V_XF3, V_XF2 = 10, 11, 12, 13, 14, 15, 16, 17, 18
V_COLOR, V_NODEPATH, V_RID, V_OBJECT, V_INPUTEVENT, V_DICT = 20, 22, 23, 24, 25, 26
V_ARRAY, V_PBYTE, V_PI32, V_PF32, V_PSTR, V_PV3, V_PCOL, V_PV2 = 30, 31, 32, 33, 34, 35, 36, 37
V_INT64, V_DOUBLE, V_CALLABLE, V_SIGNAL, V_SNAME = 40, 41, 42, 43, 44
V_VEC2I, V_RECT2I, V_VEC3I, V_PI64, V_PF64, V_VEC4, V_VEC4I, V_PROJ, V_PV4 = 45, 46, 47, 48, 49, 50, 51, 52, 53


class Ref:
    def __init__(self, kind, idx):
        self.kind, self.idx = kind, idx

    def __repr__(self):
        return "Ref(%s,%s)" % (self.kind, self.idx)


class R:
    def __init__(self, data):
        self.d = data
        self.p = 0
        self.real64 = False

    def u32(self):
        v = struct.unpack_from("<I", self.d, self.p)[0]
        self.p += 4
        return v

    def i32(self):
        v = struct.unpack_from("<i", self.d, self.p)[0]
        self.p += 4
        return v

    def u64(self):
        v = struct.unpack_from("<Q", self.d, self.p)[0]
        self.p += 8
        return v

    def i64(self):
        v = struct.unpack_from("<q", self.d, self.p)[0]
        self.p += 8
        return v

    def f32(self):
        v = struct.unpack_from("<f", self.d, self.p)[0]
        self.p += 4
        return v

    def f64(self):
        v = struct.unpack_from("<d", self.d, self.p)[0]
        self.p += 8
        return v

    def real(self):
        return self.f64() if self.real64 else self.f32()

    def ustr(self):
        n = self.u32()
        b = self.d[self.p:self.p + n]
        self.p += n
        return b.rstrip(b"\x00").decode("utf-8", "replace")

    def skip(self, n):
        self.p += n


def load(path):
    data = open(path, "rb").read()
    r = R(data)
    magic = data[:4]
    if magic != b"RSRC":
        raise ValueError("not an uncompressed RSRC: %r" % magic)
    r.p = 4
    big = r.u32()
    if big:
        raise ValueError("big-endian resource")
    r.real64 = bool(r.u32())
    ver_major, ver_minor, ver_format = r.u32(), r.u32(), r.u32()
    rtype = r.ustr()
    r.u64()  # importmd_ofs
    flags = r.u32()
    r.u64()  # uid (always present)
    if flags & 4:
        r.real64 = True
    if flags & 8:
        r.ustr()  # script class
    for _ in range(11):
        r.u32()
    nstr = r.u32()
    if nstr > 100000:
        raise ValueError("implausible string table size %d" % nstr)
    strings = [r.ustr() for _ in range(nstr)]
    next_ = r.u32()
    ext = []
    for _ in range(next_):
        t = r.ustr()
        pth = r.ustr()
        if flags & 2:
            r.u64()
        ext.append((t, pth))
    nint = r.u32()
    ints = []
    for _ in range(nint):
        pth = r.ustr()
        off = r.u64()
        ints.append((pth, off))

    def gstr():
        i = r.u32()
        if i & 0x80000000:
            n = i & 0x7FFFFFFF
            b = r.d[r.p:r.p + n]
            r.p += n
            return b.rstrip(b"\x00").decode("utf-8", "replace")
        return strings[i]

    def pad(n):
        e = 4 - (n % 4)
        if e < 4:
            r.p += e

    def var():
        t = r.u32()
        if t == V_NIL:
            return None
        if t == V_BOOL:
            return bool(r.u32())
        if t == V_INT:
            return r.i32()
        if t == V_INT64:
            return r.i64()
        if t == V_FLOAT:
            return r.f32()
        if t == V_DOUBLE:
            return r.f64()
        if t in (V_STRING, V_SNAME):
            return r.ustr()
        if t == V_VEC2:
            return (r.real(), r.real())
        if t in (V_VEC2I,):
            return (r.i32(), r.i32())
        if t in (V_RECT2, V_PLANE, V_QUAT, V_VEC4):
            return tuple(r.real() for _ in range(4))
        if t in (V_RECT2I, V_VEC4I):
            return tuple(r.i32() for _ in range(4))
        if t == V_VEC3:
            return tuple(r.real() for _ in range(3))
        if t == V_VEC3I:
            return tuple(r.i32() for _ in range(3))
        if t == V_AABB:
            return tuple(r.real() for _ in range(6))
        if t == V_XF2:
            return tuple(r.real() for _ in range(6))
        if t == V_BASIS:
            return tuple(r.real() for _ in range(9))
        if t == V_XF3:
            return tuple(r.real() for _ in range(12))
        if t == V_PROJ:
            return tuple(r.real() for _ in range(16))
        if t == V_COLOR:
            return tuple(r.f32() for _ in range(4))
        if t == V_NODEPATH:
            nn = struct.unpack_from("<H", r.d, r.p)[0]
            ns = struct.unpack_from("<H", r.d, r.p + 2)[0]
            r.p += 4
            ns &= 0x7FFF
            parts = [gstr() for _ in range(nn + ns)]
            return "NodePath(" + "/".join(parts) + ")"
        if t == V_RID:
            return ("RID", r.u32())
        if t == V_OBJECT:
            ot = r.u32()
            if ot == 0:
                return None
            if ot == 2:
                return Ref("int", r.u32())
            if ot == 3:
                return Ref("ext", r.u32())
            if ot == 1:
                return Ref("extpath", (r.ustr(), r.ustr()))
            raise ValueError("object type %d" % ot)
        if t in (V_CALLABLE, V_SIGNAL):
            return None
        if t == V_DICT:
            n = r.u32() & 0x7FFFFFFF
            out = {}
            for _ in range(n):
                k = var()
                v = var()
                try:
                    out[k] = v
                except TypeError:
                    out[repr(k)] = v
            return out
        if t == V_ARRAY:
            n = r.u32() & 0x7FFFFFFF
            return [var() for _ in range(n)]
        if t == V_PBYTE:
            n = r.u32()
            b = r.d[r.p:r.p + n]
            r.p += n
            pad(n)
            return ("bytes", n)
        if t in (V_PI32, V_PF32):
            n = r.u32()
            r.p += 4 * n
            return ("arr4", n)
        if t in (V_PI64, V_PF64):
            n = r.u32()
            r.p += 8 * n
            return ("arr8", n)
        if t == V_PSTR:
            n = r.u32()
            return [r.ustr() for _ in range(n)]
        if t == V_PV2:
            n = r.u32()
            r.p += n * 2 * (8 if r.real64 else 4)
            return ("v2", n)
        if t == V_PV3:
            n = r.u32()
            r.p += n * 3 * (8 if r.real64 else 4)
            return ("v3", n)
        if t == V_PCOL:
            n = r.u32()
            r.p += n * 16
            return ("col", n)
        if t == V_PV4:
            n = r.u32()
            r.p += n * 4 * (8 if r.real64 else 4)
            return ("v4", n)
        raise ValueError("unknown variant tag %d at %d" % (t, r.p - 4))

    res = []
    for pth, off in ints:
        r.p = off
        t = r.ustr()
        pc = r.u32()
        props = {}
        for _ in range(pc):
            nm = gstr()
            props[nm] = var()
        res.append((t, pth, props))
    return {"type": rtype, "ver": (ver_major, ver_minor, ver_format), "ext": ext, "res": res}


def main():
    root = sys.argv[1]
    dump = int(sys.argv[sys.argv.index("--dump") + 1]) if "--dump" in sys.argv else 0
    mat_cull = Counter()
    mat_transp = Counter()
    mat_vcol = Counter()
    mat_names_by_cull = defaultdict(Counter)
    surf_hist = Counter()
    lods_meshes = 0
    meshes = 0
    shadow_set = 0
    lm_hint_set = 0
    caabb_set = 0
    blend = 0
    by_group = defaultdict(Counter)
    errors = []
    dumped = 0
    for dp, dn, fns in os.walk(root):
        dn[:] = [d for d in dn if d != ".godot"]
        for fn in fns:
            if not fn.endswith(".res"):
                continue
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, root).replace("\\", "/")
            grp = rel.split("/")[0] if not rel.startswith("lot/") else "lot/*/" + rel.split("/")[2]
            try:
                info = load(p)
            except Exception as e:  # noqa
                errors.append((rel, str(e)))
                continue
            if dump and dumped < dump:
                dumped += 1
                print("DUMP", rel, info["type"], info["ver"], "ext:", info["ext"][:4])
                for t, pth, props in info["res"]:
                    short = {}
                    for k, v in props.items():
                        if k == "_surfaces":
                            short[k] = [{kk: (vv if not isinstance(vv, (list, dict)) else "...") for kk, vv in s.items()} for s in v]
                        else:
                            short[k] = v
                    print("   ", t, pth, short)
            for t, pth, props in info["res"]:
                if t in ("StandardMaterial3D", "ORMMaterial3D"):
                    c = props.get("cull_mode", "absent(default 0 = BACK)")
                    mat_cull[c] += 1
                    by_group[grp]["cull=%s" % c] += 1
                    mat_names_by_cull[c][props.get("resource_name", "?")] += 1
                    mat_transp[props.get("transparency", "absent(0)")] += 1
                    mat_vcol[props.get("vertex_color_use_as_albedo", "absent(False)")] += 1
                if t == "ArrayMesh":
                    meshes += 1
                    surfs = props.get("_surfaces", [])
                    surf_hist[len(surfs)] += 1
                    if any(isinstance(s, dict) and "lods" in s for s in surfs):
                        lods_meshes += 1
                    if props.get("shadow_mesh") is not None:
                        shadow_set += 1
                    if props.get("lightmap_size_hint") not in (None, (0, 0)):
                        lm_hint_set += 1
                    ca = props.get("custom_aabb")
                    if ca is not None and any(abs(x) > 0 for x in ca):
                        caabb_set += 1
                    if props.get("blend_shape_names") or props.get("_blend_shape_names"):
                        blend += 1
    print("errors:", len(errors), errors[:5])
    print("StandardMaterial3D cull_mode values:", dict(mat_cull))
    for c, names in mat_names_by_cull.items():
        print("  cull", c, "top names:", names.most_common(8))
    print("transparency values:", dict(mat_transp))
    print("vertex_color_use_as_albedo values:", dict(mat_vcol))
    print("ArrayMesh:", meshes, "surfaces-per-mesh hist:", dict(sorted(surf_hist.items())))
    print("  meshes with a 'lods' surface key:", lods_meshes)
    print("  shadow_mesh set:", shadow_set, " lightmap_size_hint set:", lm_hint_set,
          " custom_aabb nonzero:", caabb_set, " blend shapes:", blend)
    print("by group:")
    for g in sorted(by_group):
        print("  ", g, dict(by_group[g]))


if __name__ == "__main__":
    main()
