"""Roadmap 28: how many of a package's embedded GLB images are the same bytes.

Item 28 (2026-08-12) read Zoo's `export_format="GLB"` and said each module file carries its own copy of the
pack it wears, so the texture side of the kit's reuse is "14x, not 1x" -- an inference from the exporter, never
counted. This counts it: every image in every GLB under a package, keyed by the SHA-256 of its bytes, and says
how many distinct images there are against how many are embedded. It reports a measurement and stops; what the
engine makes resident of them is `docs/findings/texture_memory/`'s question, not this script's.

    python embedded_textures_28.py <package_dir>
"""
import collections
import hashlib
import json
import pathlib
import struct
import sys


def glb_images(path: pathlib.Path):
    """Yield (mime, name, bytes) for each image embedded in a GLB; nothing for a GLB with none."""
    data = path.read_bytes()
    if data[:4] != b"glTF":
        return
    length = struct.unpack_from("<I", data, 8)[0]
    off = 12
    chunks = {}
    while off < length:
        clen, ctype = struct.unpack_from("<II", data, off)
        chunks[ctype] = data[off + 8:off + 8 + clen]
        off += 8 + clen
    doc = json.loads(chunks[0x4E4F534A].decode("utf-8"))
    bin_ = chunks.get(0x004E4942, b"")
    views = doc.get("bufferViews", [])
    for im in doc.get("images", []):
        if "bufferView" not in im:
            # An image the GLB points at rather than carries: the glTF `uri`, relative to the file.
            yield im.get("mimeType", "?"), im.get("name", ""), None, im.get("uri", "")
            continue
        v = views[im["bufferView"]]
        start = v.get("byteOffset", 0)
        yield im.get("mimeType", "?"), im.get("name", ""), bin_[start:start + v["byteLength"]], None


def main(argv):
    pkg = pathlib.Path(argv[1])
    glbs = sorted(pkg.rglob("*.glb"))
    by_hash = collections.defaultdict(list)
    by_uri = collections.defaultdict(list)
    embedded = 0
    files_with = 0
    files_with_uri = 0
    bytes_embedded = 0
    for g in glbs:
        n = 0
        m = 0
        for mime, name, blob, uri in glb_images(g):
            rel = g.relative_to(pkg).as_posix()
            if blob is None:
                target = (g.parent / uri).resolve()
                key = target.relative_to(pkg.resolve()).as_posix() if target.exists() else f"MISSING:{uri}"
                by_uri[key].append((rel, name))
                m += 1
                continue
            h = hashlib.sha256(blob).hexdigest()[:16]
            by_hash[h].append((rel, name, len(blob)))
            embedded += 1
            bytes_embedded += len(blob)
            n += 1
        files_with += 1 if n else 0
        files_with_uri += 1 if m else 0
    distinct_bytes = sum(v[0][2] for v in by_hash.values())
    print(f"package: {pkg.name}")
    print(f"glb files: {len(glbs)}  with embedded images: {files_with}  with uri images: {files_with_uri}")
    print(f"embedded images: {embedded}  ({bytes_embedded / 2**20:.1f} MiB)")
    print(f"distinct by bytes: {len(by_hash)}  ({distinct_bytes / 2**20:.1f} MiB)")
    if by_hash:
        print(f"copies per distinct image: mean {embedded / len(by_hash):.2f}")
    top = sorted(by_hash.items(), key=lambda kv: -len(kv[1]))[:12]
    print("most-copied images (copies, bytes, first file, name):")
    for h, v in top:
        print(f"  {len(v):4d}  {v[0][2]:9d}  {v[0][0]}  {v[0][1]}")
    by_dir = collections.Counter()
    for v in by_hash.values():
        for f, _, _ in v:
            by_dir[f.split("/")[0]] += 1
    print("embedded images by top-level folder:", dict(by_dir.most_common()))
    refs = sum(len(v) for v in by_uri.values())
    missing = [k for k in by_uri if k.startswith("MISSING:")]
    size = sum((pkg / k).stat().st_size for k in by_uri if not k.startswith("MISSING:"))
    print(f"uri image references: {refs}  distinct files: {len(by_uri)}  ({size / 2**20:.1f} MiB on disk)"
          f"  missing: {len(missing)}")
    if by_uri:
        print(f"references per distinct file: mean {refs / len(by_uri):.2f}")
    print("most-referenced files (refs, path):")
    for k, v in sorted(by_uri.items(), key=lambda kv: -len(kv[1]))[:12]:
        print(f"  {len(v):4d}  {k}")
    folders = collections.Counter(k.split("/")[0] for k in by_uri if not k.startswith("MISSING:"))
    print("distinct files by top-level folder:", dict(folders.most_common()))
    # Zoo names a shared texture by its content hash, so one basename in two building folders is the same
    # bytes written twice: once per `lot/<id>/art/zoo/_tex/`. Distinct basenames is the count of distinct images.
    names = collections.Counter(k.rsplit("/", 1)[-1] for k in by_uri if not k.startswith("MISSING:"))
    print(f"distinct basenames (content-hashed): {len(names)}  "
          f"written in more than one folder: {sum(1 for n, c in names.items() if c > 1)}  "
          f"max folders for one image: {max(names.values()) if names else 0}")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
