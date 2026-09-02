"""Count how many times the same texture payload is stored across a kit's GLBs.

WHAT THIS MEASURES, precisely. Every `.glb` under the given directory is
opened as a glTF container and its `images[]` are resolved to the bytes they
actually occupy. Those byte ranges are hashed. The census then reports how
many DISTINCT payloads exist against how many COPIES of them are stored.

WHY THE QUESTION EXISTS. Deli Counter's whole VRAM discipline is that one
mesh is built once and instanced N times, so Godot loads one Mesh resource no
matter how many placements a wall run has. That discipline operates on
MESHES. Pixelcoat writes one texture per material -- a single
`concrete_delco_albedo.png` for the level -- but Zoo exports each module as a
self-contained GLB, and a self-contained GLB embeds the image bytes it
references. Two facts that are individually correct can still combine into N
copies of one texture, and nothing in the pipeline was counting.

WHAT IT DOES NOT MEASURE, and do not let anyone quote it as if it did:

  * It is not a VRAM number. Bytes in a GLB are COMPRESSED PNG; the GPU holds
    decompressed (or block-compressed) texels plus mips. The `vram_estimate`
    column is width*height*4 bytes for the base level only, labelled as an
    estimate, and it moves by a large factor depending on the importer's
    compression mode. Use it to compare against itself, never as a budget.
  * It does not know what the engine did. Godot may or may not deduplicate
    identical embedded images across separate imported scenes. `--imported`
    counts the `.ctex` files a project's import cache actually contains, which
    is the observation that settles it -- but that is a separate section with
    a separate number, not folded into this one.
  * It says nothing about whether duplication is WRONG. A self-contained GLB
    is a legitimate design with real benefits. This reports a count.

USAGE
    python tools/texture_census.py <dir-of-glbs> [--json] [--imported PROJECT]
"""

import argparse
import hashlib
import json
import os
import struct
import sys
from collections import defaultdict

GLTF_MAGIC = b"glTF"
CHUNK_JSON = 0x4E4F534A
CHUNK_BIN = 0x004E4942


def read_glb(path):
    """Return (gltf_json, bin_bytes). Raises ValueError on anything unexpected.

    Deliberately strict. A silently-skipped file becomes an undercount, and an
    undercount here reads as 'no duplication problem'.
    """
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:4] != GLTF_MAGIC:
        raise ValueError("not a GLB (bad magic)")
    version, _length = struct.unpack_from("<II", data, 4)
    if version != 2:
        raise ValueError("glTF version %d, expected 2" % version)
    off = 12
    js = None
    binary = b""
    while off + 8 <= len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        body = data[off + 8:off + 8 + clen]
        if ctype == CHUNK_JSON:
            js = json.loads(body)
        elif ctype == CHUNK_BIN:
            binary = body
        off += 8 + clen
    if js is None:
        raise ValueError("no JSON chunk")
    return js, binary


def png_dims(blob):
    """(width, height) from a PNG IHDR, or None. Stdlib only, on purpose --
    this tool has to run wherever the pipeline runs."""
    if len(blob) < 24 or blob[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    if blob[12:16] != b"IHDR":
        return None
    w, h = struct.unpack_from(">II", blob, 16)
    return (w, h)


def image_payloads(gltf, binary):
    """Yield (name, mime, bytes) for every image the file stores inline."""
    views = gltf.get("bufferViews", [])
    for img in gltf.get("images", []):
        if "bufferView" not in img:
            # A URI image is a shared file on disk, which is the opposite of
            # the case this tool exists to count. Report it as such.
            yield (img.get("name") or img.get("uri") or "?",
                   img.get("mimeType", ""), None)
            continue
        bv = views[img["bufferView"]]
        start = bv.get("byteOffset", 0)
        blob = binary[start:start + bv["byteLength"]]
        yield (img.get("name") or "?", img.get("mimeType", ""), blob)


def census(root):
    files = []
    for dirpath, _dirs, names in os.walk(root):
        for n in sorted(names):
            if n.lower().endswith(".glb"):
                files.append(os.path.join(dirpath, n))
    payloads = defaultdict(lambda: {"bytes": 0, "dims": None, "names": set(),
                                    "carriers": []})
    external = []
    errors = []
    for path in sorted(files):
        try:
            gltf, binary = read_glb(path)
        except Exception as exc:                       # noqa: BLE001
            errors.append((path, str(exc)))
            continue
        for name, mime, blob in image_payloads(gltf, binary):
            if blob is None:
                external.append((path, name))
                continue
            key = hashlib.sha256(blob).hexdigest()
            rec = payloads[key]
            rec["bytes"] = len(blob)
            rec["dims"] = rec["dims"] or png_dims(blob)
            rec["names"].add(name)
            rec["carriers"].append(os.path.relpath(path, root))
    return files, payloads, external, errors


def imported_ctex(project, known):
    """Count the .ctex files Godot's import cache holds, grouped by which of
    the KNOWN texture names (taken from the GLBs this run just read) appears
    in each filename. This is the engine's own behaviour, observed.

    The names come from the data, never from a pattern guessed off the
    filenames. Two earlier groupings both produced confident nonsense: the
    first keyed on the whole stem (every file unique -- "no duplication"),
    the second on a trailing `<word>_albedo` (concrete, drywall and carpet
    all collapsing into one "delco_albedo" bucket). Longest known name wins,
    because `tile_delco_albedo` is a substring of `ceiling_tile_delco_albedo`.
    """
    cache = os.path.join(project, ".godot", "imported")
    if not os.path.isdir(cache):
        return None
    names = sorted(known, key=len, reverse=True)
    groups = defaultdict(list)
    for n in sorted(os.listdir(cache)):
        if not n.endswith(".ctex"):
            continue
        hit = next((k for k in names if k in n), None)
        groups[hit or "(unmatched) " + n].append(n)
    return groups


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", help="directory to walk for .glb files")
    ap.add_argument("--imported", default=None,
                    help="a Godot project folder; also count the .ctex files "
                         "its .godot/imported cache actually contains")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    files, payloads, external, errors = census(a.root)
    copies = sum(len(r["carriers"]) for r in payloads.values())
    stored = sum(r["bytes"] * len(r["carriers"]) for r in payloads.values())
    unique = sum(r["bytes"] for r in payloads.values())
    vram = 0
    for r in payloads.values():
        if r["dims"]:
            vram += r["dims"][0] * r["dims"][1] * 4 * len(r["carriers"])

    rows = []
    for key, r in sorted(payloads.items(),
                         key=lambda kv: -len(kv[1]["carriers"])):
        rows.append({
            "sha256": key[:12],
            "name": sorted(r["names"])[0],
            "bytes": r["bytes"],
            "dims": list(r["dims"]) if r["dims"] else None,
            "copies": len(r["carriers"]),
            "carriers": sorted(r["carriers"]),
        })

    imported = None
    if a.imported:
        known = set()
        for r in payloads.values():
            known |= r["names"]
        groups = imported_ctex(a.imported, known)
        if groups is None:
            imported = {"error": "no .godot/imported under %s" % a.imported}
        else:
            imported = {k: len(v) for k, v in sorted(
                groups.items(), key=lambda kv: -len(kv[1]))}

    if a.json:
        json.dump({"glb_files": len(files), "distinct_payloads": len(payloads),
                   "stored_copies": copies, "stored_bytes": stored,
                   "unique_bytes": unique, "vram_estimate_bytes": vram,
                   "images": rows, "external_uri_images": external,
                   "unreadable": errors, "imported_ctex": imported},
                  sys.stdout, indent=1)
        print()
        return 0

    print("[texture_census] %s" % os.path.abspath(a.root))
    print("  %d GLB file(s)" % len(files))
    if errors:
        print("  %d UNREADABLE:" % len(errors))
        for p, e in errors:
            print("     %s -- %s" % (p, e))
    print("  %d distinct image payload(s) stored %d time(s)"
          % (len(payloads), copies))
    print("  %.2f MB stored   %.2f MB unique   duplication factor %.2fx"
          % (stored / 1e6, unique / 1e6,
             (stored / unique) if unique else 0.0))
    print("  base-level VRAM estimate if nothing is shared: %.1f MB"
          % (vram / 1e6))
    print("     (width*height*4, no mips, no block compression -- an estimate)")
    if external:
        print("  %d image(s) referenced by URI instead of embedded" %
              len(external))
    print()
    print("  %-14s %-30s %9s %11s %7s" %
          ("sha256", "name", "bytes", "dims", "copies"))
    for r in rows:
        d = "%dx%d" % tuple(r["dims"]) if r["dims"] else "-"
        print("  %-14s %-30s %9d %11s %7d"
              % (r["sha256"], r["name"][:30], r["bytes"], d, r["copies"]))

    if imported is not None:
        print()
        if "error" in imported:
            print("  [imported] %s" % imported["error"])
        else:
            print("  [imported] .ctex files in the project's import cache,")
            print("             grouped by the source texture they end with:")
            for k, v in imported.items():
                print("     %-40s %4d" % (k[:40], v))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
