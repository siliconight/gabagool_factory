"""What textures a package ships, and what they would cost: a census of every image under a
Level Factory package with the import mode its sidecar asks for (the package ships `.import`
sidecars, not the cache), the pixels, the bytes on disk, and two estimates of texture memory --
raw (RGBA8 plus a mip chain, what `VRAM Uncompressed` or `Lossless` costs) and block-compressed
(BC1 for opaque, BC3 for alpha, plus mips, what `VRAM Compressed` costs on a desktop GL
Compatibility target). It counts and prints; the engine's own number is `texture_mem_probe.gd`.

    python docs/findings/texture_memory/texture_census.py <package dir> [--top 12]
"""
import collections
import os
import re
import sys

from PIL import Image

MODES = {"0": "lossless", "1": "lossy", "2": "vram_compressed", "3": "vram_uncompressed", "4": "basis_universal"}
EXTS = (".png", ".webp", ".jpg", ".jpeg", ".tga", ".exr", ".ktx2", ".hdr")
MIPS = 4.0 / 3.0


def sidecar_mode(path):
    """The `compress/mode` the image's `.import` sidecar asks for, or None without one."""
    imp = path + ".import"
    if not os.path.isfile(imp):
        return None, False
    text = open(imp, encoding="utf-8", errors="replace").read()
    m = re.search(r"^compress/mode=(\d+)", text, re.M)
    mips = re.search(r"^mipmaps/generate=(true|false)", text, re.M)
    return (MODES.get(m.group(1), m.group(1)) if m else "default"), (mips.group(1) == "true" if mips else None)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    pkg = sys.argv[1]
    top = int(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 12
    rows = []
    for dirpath, _dirs, files in os.walk(pkg):
        if "/.godot" in dirpath.replace("\\", "/"):
            continue
        for f in files:
            if not f.lower().endswith(EXTS):
                continue
            p = os.path.join(dirpath, f)
            size = os.path.getsize(p)
            try:
                with Image.open(p) as im:
                    w, h, mode = im.width, im.height, im.mode
            except Exception as ex:  # noqa: BLE001 -- an unreadable image is a row, not a crash
                w, h, mode = 0, 0, "unreadable:%s" % type(ex).__name__
            alpha = "A" in mode
            cmode, mips = sidecar_mode(p)
            rows.append((os.path.relpath(p, pkg), w, h, mode, size, cmode, mips, alpha))
    if not rows:
        sys.exit("no images under %s" % pkg)
    n = len(rows)
    disk = sum(r[4] for r in rows)
    px = sum(r[1] * r[2] for r in rows)
    raw = sum(r[1] * r[2] * 4 * MIPS for r in rows)
    bc = sum(r[1] * r[2] * (1.0 if r[7] else 0.5) * MIPS for r in rows)
    by_mode = collections.Counter(r[5] for r in rows)
    by_dir = collections.Counter(r[0].replace("\\", "/").split("/")[0] for r in rows)
    by_dim = collections.Counter("%dx%d" % (r[1], r[2]) for r in rows)
    print("package: %s" % pkg)
    print("images %d, on disk %.1f MiB, %.1f Mpx" % (n, disk / 2**20, px / 1e6))
    print("sidecar compress/mode: %s" % dict(by_mode))
    print("by top folder: %s" % dict(by_dir.most_common(8)))
    print("by size: %s" % dict(by_dim.most_common(10)))
    print("texture memory, estimated with a mip chain (x4/3):")
    print("  raw RGBA8 (lossless / vram_uncompressed)  %.1f MiB" % (raw / 2**20))
    print("  block-compressed (BC1 opaque, BC3 alpha)  %.1f MiB" % (bc / 2**20))
    print("the %d largest:" % top)
    for r in sorted(rows, key=lambda r: -r[1] * r[2])[:top]:
        print("  %7dx%-6d %-5s %7.2f MiB  %-16s mips=%s  %s" % (r[1], r[2], r[3], r[4] / 2**20, r[5], r[6], r[0]))


if __name__ == "__main__":
    main()
