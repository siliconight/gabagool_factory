"""Report which UV channels a built .glb actually carries.

WHAT THIS IS FOR. Every Godot GI technique except ReflectionProbe asks something
of the geometry, and LightmapGI asks the most: a second UV set, per mesh, laid
out so no two faces share a texel. It is also the only technique that runs on
the Mobile and Compatibility renderers -- SDFGI and VoxelGI are Forward+ only --
so on a package we ship to a consumer whose renderer we do not choose, "is there
a UV2" decides whether baked GI is a decision still open or a thing that cannot
be done. That is a fact about files already on disk, and until this tool existed
nothing in the repo read it.

    python tools\\glb_uv_census.py <file-or-dir> [<file-or-dir> ...]

WHAT IT MEASURES, AND IN WHAT FRAME. Counts are per PRIMITIVE, not per mesh: a
mesh with three primitives counts three, because a primitive is what carries an
attribute dict and what Godot turns into one surface. `TEXCOORD_n` is read from
the glTF JSON chunk only -- no accessor data is decoded except for the two
refutations below, which need it.

TWO REFUTATIONS, BECAUSE "HAS TEXCOORD_1" IS NOT "HAS A LIGHTMAP UNWRAP".

  identical_to_uv0 -- the TEXCOORD_1 accessor resolves to the same bytes as
      TEXCOORD_0. Exporters emit this when a material asked for a second channel
      and nothing generated one. A duplicate of the tiling UV is not an unwrap.

  outside_unit_square -- some u or v falls outside [0, 1]. A lightmap atlas
      coordinate cannot; a tiling wall UV routinely does. This is one-directional
      evidence: inside the square does not prove non-overlapping, which is the
      property a bake actually needs and which this tool does not check. It is
      reported so a "we have UV2" claim can be refuted cheaply, not so one can
      be confirmed.

WHAT A NONZERO EXIT MEANS. Only that the measurement did not happen -- a path
that is not there, a container this parser does not understand. It never reports
a file it could not read as a file with no UV2.
"""
import argparse
import base64
import json
import os
import struct
import sys

GLB_MAGIC = 0x46546C67
CHUNK_JSON = 0x4E4F534A
CHUNK_BIN = 0x004E4942

#: glTF componentType -> (struct code, byte size). Only what a TEXCOORD can be.
COMPONENT = {
    5120: ("b", 1), 5121: ("B", 1), 5122: ("h", 2),
    5123: ("H", 2), 5125: ("I", 4), 5126: ("f", 4),
}
NCOMP = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


class UnreadableGLB(Exception):
    """The file could not be parsed. Not a finding about its UVs."""


def read_glb(path):
    """(gltf_json, bin_chunk_or_None) from a binary .glb container."""
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) < 12:
        raise UnreadableGLB(path + ": shorter than a GLB header")
    magic, version, total = struct.unpack_from("<III", data, 0)
    if magic != GLB_MAGIC:
        raise UnreadableGLB(
            path + ": not a binary GLB (magic 0x%08x). A .gltf+.bin pair "
            "is a different container and this parser does not read it."
            % magic)
    if version != 2:
        raise UnreadableGLB(path + ": glTF version %d, expected 2" % version)
    if total != len(data):
        # Reported, not fatal: the JSON chunk is usually still intact, and a
        # truncated tail would surface as an accessor read failure below.
        sys.stderr.write(
            "warning: %s declares %d bytes, file is %d\n"
            % (path, total, len(data)))
    gltf = None
    binc = None
    off = 12
    while off + 8 <= len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        body = data[off + 8:off + 8 + clen]
        if ctype == CHUNK_JSON and gltf is None:
            gltf = json.loads(body.decode("utf-8"))
        elif ctype == CHUNK_BIN and binc is None:
            binc = body
        off += 8 + clen + ((4 - clen % 4) % 4)
    if gltf is None:
        raise UnreadableGLB(path + ": no JSON chunk")
    return gltf, binc


def buffer_bytes(gltf, binc, index):
    """The bytes of one buffer: the BIN chunk, or an embedded data: URI."""
    buf = gltf.get("buffers", [])[index]
    uri = buf.get("uri")
    if uri is None:
        if binc is None:
            raise UnreadableGLB("buffer %d wants the BIN chunk, none present"
                                % index)
        return binc
    if uri.startswith("data:"):
        return base64.b64decode(uri.split(",", 1)[1])
    raise UnreadableGLB(
        "buffer %d is external (%s); this tool reads self-contained files only"
        % (index, uri[:40]))


def accessor_values(gltf, binc, index):
    """Decoded values of one accessor as a flat tuple, or None if unreadable.

    Handles byteStride, because an interleaved vertex buffer is the normal
    shape out of a real exporter and reading it as tight would compare noise.
    """
    acc = gltf["accessors"][index]
    if "bufferView" not in acc:
        return None                      # sparse or zero-filled; not our case
    view = gltf["bufferViews"][acc["bufferView"]]
    code, size = COMPONENT[acc["componentType"]]
    n = NCOMP[acc["type"]]
    count = acc["count"]
    raw = buffer_bytes(gltf, binc, view.get("buffer", 0))
    base = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
    stride = view.get("byteStride") or (size * n)
    out = []
    for i in range(count):
        at = base + i * stride
        if at + size * n > len(raw):
            raise UnreadableGLB("accessor %d runs past its buffer" % index)
        out.extend(struct.unpack_from("<" + code * n, raw, at))
    return tuple(out)


def census_file(path):
    gltf, binc = read_glb(path)
    meshes = gltf.get("meshes", [])
    prims = 0
    channels = {}
    attributes = {}
    uv1_same = 0
    uv1_outside = 0
    uv1_checked = 0
    uv1_unreadable = 0
    for mesh in meshes:
        for prim in mesh.get("primitives", []):
            prims += 1
            attrs = prim.get("attributes", {})
            for key in attrs:
                attributes[key] = attributes.get(key, 0) + 1
                if key.startswith("TEXCOORD_"):
                    channels[key] = channels.get(key, 0) + 1
            if "TEXCOORD_1" not in attrs:
                continue
            try:
                a = accessor_values(gltf, binc, attrs["TEXCOORD_0"]) \
                    if "TEXCOORD_0" in attrs else None
                b = accessor_values(gltf, binc, attrs["TEXCOORD_1"])
            except (UnreadableGLB, KeyError, struct.error):
                uv1_unreadable += 1
                continue
            if b is None:
                uv1_unreadable += 1
                continue
            uv1_checked += 1
            if a is not None and a == b:
                uv1_same += 1
            if any(v < 0.0 or v > 1.0 for v in b):
                uv1_outside += 1
    return {
        "file": os.path.basename(path),
        "path": path,
        "meshes": len(meshes),
        "primitives": prims,
        # Every vertex attribute present, not only the UVs. A shell that turns
        # out to carry POSITION and NORMAL and nothing else is a different
        # situation from one with UVs in the wrong channel, and the count that
        # distinguishes them costs nothing to collect.
        "attributes": dict(sorted(attributes.items())),
        "materials": len(gltf.get("materials", [])),
        "textures": len(gltf.get("textures", [])),
        "images": len(gltf.get("images", [])),
        "generator": str(gltf.get("asset", {}).get("generator", "")),
        "texcoord_channels": dict(sorted(channels.items())),
        "primitives_with_uv0": channels.get("TEXCOORD_0", 0),
        "primitives_with_uv1": channels.get("TEXCOORD_1", 0),
        "uv1_accessors_read": uv1_checked,
        "uv1_identical_to_uv0": uv1_same,
        "uv1_outside_unit_square": uv1_outside,
        "uv1_unreadable": uv1_unreadable,
    }


def collect(targets):
    out = []
    for t in targets:
        if os.path.isdir(t):
            for name in sorted(os.listdir(t)):
                if name.lower().endswith(".glb"):
                    out.append(os.path.join(t, name))
        else:
            out.append(t)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("targets", nargs="+",
                    help=".glb files, or directories to scan for them")
    ap.add_argument("--json", action="store_true",
                    help="emit the full report as JSON instead of a table")
    args = ap.parse_args(argv)

    paths = collect(args.targets)
    if not paths:
        sys.stderr.write("no .glb found under: " + ", ".join(args.targets)
                         + "\n")
        return 2

    rows = []
    failed = []
    for p in paths:
        try:
            rows.append(census_file(p))
        except (UnreadableGLB, OSError, KeyError, ValueError,
                struct.error) as exc:
            failed.append((p, str(exc)))

    if args.json:
        print(json.dumps({"files": rows, "unreadable": [
            {"path": p, "error": e} for p, e in failed]}, indent=2))
    else:
        width = max([len(r["file"]) for r in rows] + [4])
        print("%-*s  %5s  %5s  %5s  %4s  %s"
              % (width, "file", "prims", "uv0", "uv1", "mats", "attributes"))
        for r in rows:
            print("%-*s  %5d  %5d  %5d  %4d  %s"
                  % (width, r["file"], r["primitives"],
                     r["primitives_with_uv0"], r["primitives_with_uv1"],
                     r["materials"], ",".join(r["attributes"]) or "-"))
        tot_p = sum(r["primitives"] for r in rows)
        tot_1 = sum(r["primitives_with_uv1"] for r in rows)
        same = sum(r["uv1_identical_to_uv0"] for r in rows)
        outside = sum(r["uv1_outside_unit_square"] for r in rows)
        read = sum(r["uv1_accessors_read"] for r in rows)
        print()
        print("%d files, %d primitives, %d with TEXCOORD_1"
              % (len(rows), tot_p, tot_1))
        if tot_1:
            print("  of %d TEXCOORD_1 accessors read: %d identical to "
                  "TEXCOORD_0, %d with a coordinate outside [0,1]"
                  % (read, same, outside))
            print("  neither figure confirms a usable lightmap unwrap; "
                  "non-overlap is not checked here")
        else:
            print("  no TEXCOORD_1 anywhere: LightmapGI cannot bake these "
                  "meshes as they are")
        for p, e in failed:
            sys.stderr.write("unreadable: " + e + "\n")

    return 1 if failed and not rows else 0


if __name__ == "__main__":
    sys.exit(main())
