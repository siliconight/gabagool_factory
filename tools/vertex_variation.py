"""Do identical-looking meshes actually differ? COLOR_0 variation in a GLB.

WHAT THIS IS FOR. A modular pipeline instances one mesh many times, and the
single loudest tell that a level was generated is that every copy is the same.
Zoo computes per-vertex wear (concavity darkening plus seeded grime) for every
cover it builds, and Patina computes a deterministic per-slot colour factor in
`instances.json`. Neither had ever been checked against a shipped file.

The first run of this measurement, on a dressing GLB of 2098 covers:

    family                 n     mean   BETWEEN sd   WITHIN sd
    Cover_panel_field   1315   1.0000      0.00000     0.00000
    Cover_gutter_run     299   1.0000      0.00000     0.00000
    ... all eight families ...  1.0000      0.00000     0.00000

Pure white on every vertex of every cover, while the `rockay` style declared
`wear: 0.29`. The wear was computed, written into a colour layer named "Wear",
and dropped at the export boundary because `export_glb` exports
`export_vertex_color="ACTIVE"` and nothing ever made that layer active.

    python tools\\vertex_variation.py <file.glb> [--json]

WHAT THE TWO NUMBERS MEAN, because they fail for different reasons.

  * BETWEEN sd -- spread of the per-mesh mean across every instance of a
    family. Zero means every copy is identical: no per-instance variation,
    which is the "1374 panels stamped from one die" failure.
  * WITHIN sd -- the average spread INSIDE a single mesh. Zero means the mesh
    is flat-coloured: no wear, no ambient occlusion, no grime, which is a
    different failure with the same symptom.

Both zero is what a missing export looks like. BETWEEN zero with WITHIN
nonzero is wear working and instancing not. Reporting them apart is the point.

WHAT IT CANNOT TELL YOU. Whether the variation is any good, or whether Godot
uses it -- a material has to be set to read vertex colour as albedo. This
measures that the DATA is in the file, which is the half that kept being
absent.

WHAT A NONZERO EXIT MEANS. The file could not be read, or carried no COLOR_0
at all. An absence of variation is a finding and exits 0; an absence of
measurement is not, and exits 2.
"""
import argparse
import json
import struct
import sys

#: glTF componentType -> (numpy dtype string, value that means 1.0)
_COMPONENT = {5121: ("u1", 255.0), 5123: ("u2", 65535.0), 5126: ("f4", 1.0)}
_COUNT = {"VEC3": 3, "VEC4": 4, "SCALAR": 1}


class Unreadable(Exception):
    """The file could not be parsed. Not a finding about its contents."""


def chunks(path):
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) < 12 or struct.unpack_from("<I", data, 0)[0] != 0x46546C67:
        raise Unreadable("%s: not a binary GLB" % path)
    doc = blob = None
    off = 12
    while off + 8 <= len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        body = data[off + 8:off + 8 + clen]
        if ctype == 0x4E4F534A:
            doc = json.loads(body.decode("utf-8"))
        elif ctype == 0x004E4942:
            blob = body
        off += 8 + clen + ((4 - clen % 4) % 4)
    if doc is None:
        raise Unreadable("%s: no JSON chunk" % path)
    return doc, blob


def read_accessor(doc, blob, index):
    """Normalised float view of an accessor. Integer colours are 0..1 scaled
    by their own type's maximum -- a uint8 255 read as 1/65535 is how a white
    mesh reads as black, which happened on the first draft of this."""
    import numpy as np
    a = doc["accessors"][index]
    bv = doc["bufferViews"][a["bufferView"]]
    dt, norm = _COMPONENT[a["componentType"]]
    n = _COUNT[a["type"]]
    off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    raw = np.frombuffer(blob, np.dtype(dt), count=a["count"] * n, offset=off)
    return raw.reshape(-1, n).astype(np.float32) / norm


def family(name):
    """The stem shared by every instance of one thing. Blender dedupes with
    `.001` and Godot turns the dot into an underscore, so neither survives."""
    return (name or "").split(".")[0].rstrip("0123456789_-") or "(unnamed)"


def measure(path):
    import numpy as np
    doc, blob = chunks(path)
    fams = {}
    no_colour = 0
    for node in doc.get("nodes", []):
        if "mesh" not in node:
            continue
        prim = doc["meshes"][node["mesh"]]["primitives"][0]
        ci = prim.get("attributes", {}).get("COLOR_0")
        if ci is None:
            no_colour += 1
            continue
        c = read_accessor(doc, blob, ci)[:, :3]
        fams.setdefault(family(node.get("name", "")), []).append(
            (float(c.mean()), float(c.std())))
    rows = []
    for fam, vals in fams.items():
        means = np.array([v[0] for v in vals])
        withins = np.array([v[1] for v in vals])
        rows.append({"family": fam, "n": len(vals),
                     "mean": round(float(means.mean()), 4),
                     "between_sd": round(float(means.std()), 5),
                     "within_sd": round(float(withins.mean()), 5)})
    rows.sort(key=lambda r: -r["n"])
    return rows, no_colour


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("glb", nargs="+")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    measured = 0
    out = {}
    for path in args.glb:
        try:
            rows, no_colour = measure(path)
        except (Unreadable, OSError, ValueError, KeyError) as exc:
            sys.stderr.write("unreadable: %s\n" % exc)
            continue
        except ImportError:
            sys.stderr.write("numpy is required\n")
            return 2
        if not rows:
            sys.stderr.write("%s: no mesh carries COLOR_0 -- nothing measured, "
                             "which is not the same as no variation\n" % path)
            continue
        measured += 1
        out[path] = rows
        if args.json:
            continue
        print("=" * 66)
        print(path.replace("\\", "/").split("/")[-1])
        if no_colour:
            print("  %d meshed node(s) carry no COLOR_0 at all" % no_colour)
        print()
        print("%-22s %6s %9s %12s %12s"
              % ("family", "n", "mean", "BETWEEN sd", "WITHIN sd"))
        for r in rows:
            print("%-22s %6d %9.4f %12.5f %12.5f"
                  % (r["family"], r["n"], r["mean"],
                     r["between_sd"], r["within_sd"]))
        flat_between = [r["family"] for r in rows if r["between_sd"] == 0.0]
        flat_within = [r["family"] for r in rows if r["within_sd"] == 0.0]
        print()
        if flat_between:
            print("NO PER-INSTANCE VARIATION (%d famil(ies)): every copy is the "
                  "same colour" % len(flat_between))
        if flat_within:
            print("FLAT-COLOURED (%d famil(ies)): no wear, occlusion or grime "
                  "inside the mesh" % len(flat_within))
        if not flat_between and not flat_within:
            print("every family varies both between instances and within one")
        print()

    if args.json:
        print(json.dumps(out, indent=2))
    return 0 if measured else 2


if __name__ == "__main__":
    sys.exit(main())
