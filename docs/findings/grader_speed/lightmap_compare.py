"""Two or more lightmaps, texel by texel: how far apart are they?

Each `name=path/to/bake.exr` is read by Godot itself (`exr_dump.gd`, headless) and written out as
raw half-float RGBA; then every pair is compared over the colour channels: how many texels are
bit for bit the same, and the absolute difference's mean, 99.9th percentile and maximum, beside
each lightmap's own mean so the numbers have a scale. Alpha is reported apart. Values are the
lightmap's own linear light, before any tonemapping. It measures and prints; it names no cause.

    python docs/findings/grader_speed/lightmap_compare.py ref=<exr> change=<exr> control=<exr>

The dumps go to _scratch/lightmap_compare/ and are deleted when the comparison is printed.
"""
import itertools
import json
import os
import subprocess
import sys

import numpy as np

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
X = os.path.join(F, "_scratch", "lightmap_compare")
DUMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exr_dump.gd")


def godot():
    local = json.load(open(os.path.join(F, "factory.local.json"), encoding="utf-8"))
    return local["godot_executable"]


def main():
    named = [a.split("=", 1) for a in sys.argv[1:]]
    assert named and all(len(n) == 2 for n in named), "give name=path pairs"
    os.makedirs(X, exist_ok=True)
    cmd = [godot(), "--headless", "--script", DUMP, "--"]
    outs = {}
    for name, path in named:
        outs[name] = os.path.join(X, name + ".rgbah")
        cmd += [os.path.abspath(path), outs[name]]
    run = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    sizes = {}
    for line in run.stdout.splitlines():
        if line.startswith("EXR_DUMP "):
            parts = line.split()
            if parts[1] == "unreadable":
                sys.exit("unreadable: %s" % parts[2])
            sizes[os.path.normcase(os.path.abspath(parts[1]))] = (int(parts[-3]), int(parts[-2]), int(parts[-1]))
    maps = {}
    try:
        for name, path in named:
            key = os.path.normcase(os.path.abspath(path))
            assert key in sizes, ("Godot printed no size for", path, run.stdout[-400:], run.stderr[-400:])
            w, h, fmt = sizes[key]
            data = np.fromfile(outs[name], dtype=np.float16)
            assert data.size == w * h * 4, (name, data.size, w, h)
            maps[name] = data.reshape(h, w, 4).astype(np.float32)
            rgb = maps[name][..., :3]
            print("[lm] %-8s %s: %d x %d, read as format %d; mean RGB %.5f, max %.3f; alpha min %.3f max %.3f"
                  % (name, path, w, h, fmt, float(rgb.mean()), float(rgb.max()),
                     float(maps[name][..., 3].min()), float(maps[name][..., 3].max())), flush=True)
    finally:
        for p in outs.values():
            if os.path.exists(p):
                os.remove(p)
    for a, b in itertools.combinations(maps, 2):
        ma, mb = maps[a], maps[b]
        if ma.shape != mb.shape:
            print("[lm] %s against %s: different sizes %s and %s" % (a, b, ma.shape, mb.shape), flush=True)
            continue
        d = np.abs(ma[..., :3] - mb[..., :3])
        same = int(np.all(ma == mb, axis=-1).sum())
        texels = ma.shape[0] * ma.shape[1]
        per_texel = d.max(axis=-1)
        print("[lm] %s against %s: %d of %d texels the same (%.2f %%); |diff| over RGB mean %.6f, 99.9th "
              "percentile %.5f, max %.4f; texels apart by more than 0.01: %d, by more than 0.1: %d; alpha "
              "apart at %d texels"
              % (a, b, same, texels, 100.0 * same / texels, float(d.mean()),
                 float(np.percentile(per_texel, 99.9)), float(d.max()),
                 int((per_texel > 0.01).sum()), int((per_texel > 0.1).sum()),
                 int((ma[..., 3] != mb[..., 3]).sum())), flush=True)


if __name__ == "__main__":
    main()
