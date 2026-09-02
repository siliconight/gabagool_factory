"""Lift embedded images out of a kit's GLBs and reference them instead.

WHAT THIS IS FOR. Roadmap 87: Pixelcoat writes ONE texture per material, Zoo
exports each module as a self-contained GLB, and a self-contained GLB embeds
the image bytes it references -- so 18 modules that share `concrete_delco`
ship 18 copies, and Godot's importer makes 18 `.ctex` resources out of them.
Measured 3.82x duplication across the shipped kit by `texture_census.py`.

WHY REFERENCING IS THE FIX, and it was PROVEN before this file was written
rather than assumed. Two GLBs whose `images[]` carry a `uri` instead of a
`bufferView`, importing into one Godot project, produce exactly ONE
`stone.png-<hash>.ctex`. The probe lives in `_scratch/texshare_probe`. Had it
produced two, this tool would be the wrong shape and a shared material library
would be the right one.

WHY NOT `export_format="GLTF_SEPARATE"`. Blender will happily write .gltf +
.bin + loose textures, and it renames the payload. Every contract downstream
is spelled `.glb` -- Deli Counter's resolver, `walk_themed`, `look_shots`,
`texture_census`, the `art/zoo/*.glb` layout, the provenance sidecars. A
container change to fix a duplication problem is a large blast radius for a
small defect. A GLB may carry external URIs perfectly legally, so the
extension and every contract stay exactly as they are.

WHAT IT DOES NOT DO. It does not decide where the textures should live in the
shipped payload, and it does not carry them through assembly -- today
`_runs/<walk>/art/` contains GLBs and nothing else, so whoever stages art has
to learn about the texture folder too. That is the other half of 87 and it is
deliberately not in this file.

    python tools/detach_textures.py <dir-of-glbs> --tex-dir tex [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import struct
import sys

CHUNK_JSON = 0x4E4F534A
CHUNK_BIN = 0x004E4942
_EXT = {"image/png": ".png", "image/jpeg": ".jpg"}


def read_glb(path):
    with open(path, "rb") as fh:
        data = fh.read()
    if data[:4] != b"glTF":
        raise ValueError("not a GLB")
    version = struct.unpack_from("<I", data, 4)[0]
    if version != 2:
        raise ValueError("glTF version %d" % version)
    off, js, binary = 12, None, b""
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


def write_glb(path, gltf, binary):
    js = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    js += b" " * ((4 - len(js) % 4) % 4)
    binary += b"\x00" * ((4 - len(binary) % 4) % 4)
    total = 12 + 8 + len(js) + (8 + len(binary) if binary else 0)
    out = b"glTF" + struct.pack("<II", 2, total)
    out += struct.pack("<II", len(js), CHUNK_JSON) + js
    if binary:
        out += struct.pack("<II", len(binary), CHUNK_BIN) + binary
    with open(path, "wb") as fh:
        fh.write(out)


def _view_bytes(gltf, binary, i):
    bv = gltf["bufferViews"][i]
    start = bv.get("byteOffset", 0)
    return binary[start:start + bv["byteLength"]]


def detach(gltf, binary, name_for):
    """Rewrite `images[]` to URIs and REBUILD the buffer without their bytes.

    The rebuild is the part that has to be right. Dropping a bufferView
    renumbers every one after it, so accessors that still point at the old
    index would silently read the wrong attribute -- a mesh that loads, draws,
    and is wrong. Every surviving view is copied into a fresh blob and every
    accessor is remapped through an explicit old->new table.
    """
    images = gltf.get("images", [])
    if not images:
        return None
    written = []
    image_views = set()
    for img in images:
        if "bufferView" not in img:
            continue
        idx = img["bufferView"]
        blob = _view_bytes(gltf, binary, idx)
        uri = name_for(img.get("name") or "image", img.get("mimeType", ""),
                       blob)
        image_views.add(idx)
        img.pop("bufferView", None)
        img.pop("mimeType", None)
        img["uri"] = uri
        written.append((uri, blob))
    if not written:
        return None

    keep = [i for i in range(len(gltf.get("bufferViews", [])))
            if i not in image_views]
    remap = {old: new for new, old in enumerate(keep)}
    new_blob = bytearray()
    new_views = []
    for old in keep:
        bv = dict(gltf["bufferViews"][old])
        payload = _view_bytes(gltf, binary, old)
        while len(new_blob) % 4:
            new_blob.append(0)
        bv["byteOffset"] = len(new_blob)
        bv["byteLength"] = len(payload)
        new_blob.extend(payload)
        new_views.append(bv)
    for acc in gltf.get("accessors", []):
        if "bufferView" in acc:
            acc["bufferView"] = remap[acc["bufferView"]]
        sp = acc.get("sparse")
        if sp:
            for key in ("indices", "values"):
                if key in sp and "bufferView" in sp[key]:
                    sp[key]["bufferView"] = remap[sp[key]["bufferView"]]
    gltf["bufferViews"] = new_views
    gltf["buffers"] = [{"byteLength": len(new_blob)}]
    return bytes(new_blob), written


def _rel(root_relative, glb_dir, root):
    """`root_relative` expressed from the directory the GLB sits in."""
    target = os.path.normpath(os.path.join(root, root_relative))
    return os.path.relpath(target, glb_dir).replace(os.sep, "/")


def detach_tree(root, tex_dir="tex", dry_run=False):
    """Rewrite every GLB under `root` in place; return a summary dict.

    Split out from `main` so `walk_themed.py` can call it during assembly
    without shelling out. Same code path either way -- a second
    implementation of this would be a second set of bugs, and the buffer
    rebuild is the part that must not have two versions.
    """
    class _A:
        pass
    a = _A()
    a.root, a.tex_dir, a.dry_run = root, tex_dir, dry_run
    return _run(a)


def _run(a):
    texroot = os.path.join(a.root, a.tex_dir)
    by_hash = {}
    used = {}

    # A glTF image `uri` resolves RELATIVE TO THE FILE THAT CARRIES IT, not to
    # the kit root. The first cut of this tool wrote a root-relative path and
    # all 80 references pointed at a directory that does not exist next to the
    # GLB -- the meshes were perfect and every texture was missing. `here` is
    # rebound per file so `art/zoo/wall.glb` gets `../tex/stone.png`.
    here = {"dir": a.root}

    def name_for(name, mime, blob):
        digest = hashlib.sha256(blob).hexdigest()
        if digest in by_hash:
            return _rel(by_hash[digest], here["dir"], a.root)
        ext = _EXT.get(mime) or ".png"
        stem = "".join(c if c.isalnum() or c in "._-" else "_" for c in name)
        cand = stem + ext
        # Two DIFFERENT payloads under one name is the failure that would make
        # this tool silently swap one material's texture for another's. Keep
        # the name, disambiguate with the hash, never overwrite.
        if used.get(cand, digest) != digest:
            cand = "%s.%s%s" % (stem, digest[:8], ext)
        used[cand] = digest
        by_hash[digest] = posixpath.join(a.tex_dir, cand)
        return _rel(by_hash[digest], here["dir"], a.root)

    files = []
    for dirpath, _d, names in os.walk(a.root):
        if os.path.abspath(dirpath).startswith(os.path.abspath(texroot)):
            continue
        files += [os.path.join(dirpath, n) for n in sorted(names)
                  if n.lower().endswith(".glb")]

    if not a.dry_run:
        os.makedirs(texroot, exist_ok=True)
    before = after = 0
    touched = 0
    payloads = {}
    for path in sorted(files):
        before += os.path.getsize(path)
        here["dir"] = os.path.dirname(path)
        gltf, binary = read_glb(path)
        res = detach(gltf, binary, name_for)
        if res is None:
            after += os.path.getsize(path)
            continue
        new_blob, written = res
        for uri, blob in written:
            payloads[os.path.normpath(os.path.join(here["dir"], uri))] = blob
        if not a.dry_run:
            write_glb(path, gltf, new_blob)
            for uri, blob in written:
                dest = os.path.normpath(os.path.join(here["dir"], uri))
                if not os.path.exists(dest):
                    with open(dest, "wb") as fh:
                        fh.write(blob)
        after += 12 + 8 + len(json.dumps(gltf, separators=(",", ":"))) \
            + 8 + len(new_blob)
        touched += 1

    tex_bytes = sum(len(b) for b in payloads.values())
    return {"glbs": len(files), "rewritten": touched,
            "payloads": len(payloads), "glb_bytes_before": before,
            "glb_bytes_after": after, "texture_bytes": tex_bytes,
            "tex_dir": a.tex_dir, "root": a.root}


def report(r):
    """Print a summary dict from `_run`/`detach_tree`."""
    print("[detach_textures] %s%s"
          % (os.path.abspath(r["root"]), "  (DRY RUN)" if r.get("dry_run") else ""))
    print("  %d GLB(s), %d rewritten" % (r["glbs"], r["rewritten"]))
    print("  %d distinct texture payload(s) -> %s/"
          % (r["payloads"], r["tex_dir"]))
    before = r["glb_bytes_before"]
    after = r["glb_bytes_after"]
    tex = r["texture_bytes"]
    print("  glb bytes  %.2f MB -> %.2f MB" % (before / 1e6, after / 1e6))
    print("  textures   %.2f MB written once" % (tex / 1e6))
    print("  total      %.2f MB -> %.2f MB"
          % (before / 1e6, (after + tex) / 1e6))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root", help="directory of .glb files to rewrite in place")
    ap.add_argument("--tex-dir", default="tex",
                    help="folder for the shared textures, relative to root "
                         "(default: %(default)s)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    r = detach_tree(a.root, a.tex_dir, a.dry_run)
    r["dry_run"] = a.dry_run
    report(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
