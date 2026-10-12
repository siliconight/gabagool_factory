"""Two or more lightmaps, texel by texel: how far apart are they?

Each `name=path/to/bake.exr` is read by Godot itself (`exr_dump.gd`, headless) and written out as
raw half-float RGBA; then every pair is compared over the colour channels: how many texels are
bit for bit the same, and the absolute difference's mean, 99.9th percentile and maximum, beside
each lightmap's own mean so the numbers have a scale. Alpha is reported apart. Values are the
lightmap's own linear light, before any tonemapping. It measures and prints; it names no cause.

    python docs/findings/grader_speed/lightmap_compare.py ref=<exr> change=<exr> control=<exr>

LAYOUT (`--layout a=<package> b=<package>`): two bakes whose atlases were packed differently
cannot be compared texel by texel -- the same light lands somewhere else. This reads each bake's
layout (`lightmap_layout.gd`: every user's slice and rectangle, from `bake.lmbake`) in a small
project holding only the bake's data and its lightmap, the lightmap imported lossless there so
the import takes seconds; matches the users by node path and sub-instance; counts those placed
the same, moved, and resized; and, for every user whose rectangle has the same size in texels in
both, compares the texels inside it -- that user's own light, wherever the atlas put it.

    python docs/findings/grader_speed/lightmap_compare.py --layout r9256=<package> r9257=<package>

The dumps and the small projects go to _scratch/lightmap_compare/ and are deleted when the
comparison is printed.
"""
import itertools
import json
import os
import re
import shutil
import subprocess
import sys

import numpy as np

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
X = os.path.join(F, "_scratch", "lightmap_compare")
HERE = os.path.dirname(os.path.abspath(__file__))
DUMP = os.path.join(HERE, "exr_dump.gd")
LAYOUT = os.path.join(HERE, "lightmap_layout.gd")


def godot():
    local = json.load(open(os.path.join(F, "factory.local.json"), encoding="utf-8"))
    return local["godot_executable"]


def dump_exrs(named):
    """{name: (h, w, 4) float32 array} of each `(name, exr path)`, read by Godot."""
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
    return maps


def pairs(named):
    maps = dump_exrs(named)
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


def read_layout(name, pkg):
    """{(node path, sub-instance): (slice, x, y, w, h)} of a package's bake, in the slice's
    normalised coordinates, read by Godot from a small project holding only the bake."""
    proj = os.path.join(X, "proj_" + name)
    if os.path.isdir(proj):
        shutil.rmtree(proj)
    os.makedirs(proj)
    try:
        for f in ("bake.lmbake", "bake.exr"):
            shutil.copy(os.path.join(pkg, f), os.path.join(proj, f))
        imp = open(os.path.join(pkg, "bake.exr.import"), encoding="utf-8").read()
        assert imp.count("compress/mode=2") == 1, "the lightmap's import is not what this was written against"
        with open(os.path.join(proj, "bake.exr.import"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(imp.replace("compress/mode=2", "compress/mode=0"))
        with open(os.path.join(proj, "project.godot"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write('config_version=5\n\n[application]\n\nconfig/name="lightmap_layout"\n')
        subprocess.run([godot(), "--headless", "--path", proj, "--import"], capture_output=True, timeout=600)
        run = subprocess.run([godot(), "--headless", "--path", proj, "-s", LAYOUT, "--", "res://bake.lmbake"],
                             capture_output=True, text=True, timeout=600)
    finally:
        shutil.rmtree(proj, ignore_errors=True)
    users = {}
    total = None
    for line in run.stdout.splitlines():
        if line.startswith("LM_USER\t"):
            _tag, path, sub, sl, x, y, w, h = line.split("\t")
            key = (path, int(sub))
            assert key not in users, ("a user twice", key)
            users[key] = (int(sl), float(x), float(y), float(w), float(h))
        elif line.startswith("LM_USERS "):
            total = line
    assert total and "unreadable" not in total, (name, total, run.stdout[-300:], run.stderr[-300:])
    assert int(total.split()[1]) == len(users), (name, total, len(users))
    return users


def texel_rect(entry, size):
    sl, x, y, w, h = entry
    return sl, int(round(x * size)), int(round(y * size)), int(round(w * size)), int(round(h * size))


def layout(named):
    assert len(named) == 2, "--layout compares two packages"
    (na, pa), (nb, pb) = named
    la, lb = read_layout(na, pa), read_layout(nb, pb)
    maps = dump_exrs([(na, os.path.join(pa, "bake.exr")), (nb, os.path.join(pb, "bake.exr"))])
    ma, mb = maps[na], maps[nb]
    size = ma.shape[1]
    assert ma.shape == mb.shape and ma.shape[0] % size == 0, (ma.shape, mb.shape)
    keys_a, keys_b = set(la), set(lb)
    common = sorted(keys_a & keys_b)
    placed_same = moved = resized = 0
    diffs, worst = [], []
    groups = {"placed the same": [], "moved": []}
    for k in common:
        ra, rb = texel_rect(la[k], size), texel_rect(lb[k], size)
        if ra == rb:
            placed_same += 1
            group = "placed the same"
        elif ra[3:] == rb[3:]:
            moved += 1
            group = "moved"
        else:
            resized += 1
            continue
        pa_ = ma[ra[0] * size + ra[2]: ra[0] * size + ra[2] + ra[4], ra[1]: ra[1] + ra[3], :3]
        pb_ = mb[rb[0] * size + rb[2]: rb[0] * size + rb[2] + rb[4], rb[1]: rb[1] + rb[3], :3]
        assert pa_.shape == pb_.shape and pa_.size, (k, ra, rb, pa_.shape, pb_.shape)
        d = np.abs(pa_ - pb_)
        diffs.append(d.reshape(-1, 3))
        groups[group].append(((pa_ - pb_).reshape(-1, 3), pa_.reshape(-1, 3)))
        worst.append((float(d.max(axis=-1).mean()), k, float(pa_.mean())))
    print("[lm] layout %s: %d users; %s: %d users; in both %d, only in %s %d, only in %s %d"
          % (na, len(la), nb, len(lb), len(common), na, len(keys_a - keys_b), nb, len(keys_b - keys_a)), flush=True)
    print("[lm] layout: of the %d in both, %d placed the same, %d moved with the same size, %d resized"
          % (len(common), placed_same, moved, resized), flush=True)
    if diffs:
        d = np.concatenate(diffs)
        per = d.max(axis=-1)
        print("[lm] the light inside the %d same-size rectangles, each against its own: %d texels; |diff| over RGB "
              "mean %.6f, 99.9th percentile %.5f, max %.4f; apart by more than 0.01: %d, by more than 0.1: %d"
              % (len(diffs), d.shape[0], float(d.mean()), float(np.percentile(per, 99.9)), float(d.max()),
                 int((per > 0.01).sum()), int((per > 0.1).sum())), flush=True)
        # apart by group, and SIGNED: a bake's noise falls either way, a change of light one way
        for group, rows in groups.items():
            if not rows:
                continue
            sd = np.concatenate([r[0] for r in rows])
            own = np.concatenate([r[1] for r in rows])
            ad = np.abs(sd).max(axis=-1)
            print("[lm]   %s: %d users, %d texels; |diff| mean %.6f, apart by more than 0.01: %d (%.2f %%); "
                  "signed mean %s - %s %+.6f against their mean %.5f"
                  % (group, len(rows), sd.shape[0], float(np.abs(sd).mean()), int((ad > 0.01).sum()),
                     100.0 * float((ad > 0.01).mean()), na, nb, float(sd.mean()), float(own.mean())), flush=True)
        worst.sort(reverse=True)
        for mean_diff, k, own in worst[:8]:
            print("[lm]   the most apart: %s [%d]: mean |diff| %.5f, its own mean %.5f" % (k[0], k[1], mean_diff, own),
                  flush=True)
    for k in sorted(k for k in common if texel_rect(la[k], size)[3:] != texel_rect(lb[k], size)[3:])[:12]:
        print("[lm]   resized: %s [%d]: %s -> %s texels" % (k[0], k[1], texel_rect(la[k], size)[3:],
                                                           texel_rect(lb[k], size)[3:]), flush=True)


def main():
    args = [a for a in sys.argv[1:] if a != "--layout"]
    named = [a.split("=", 1) for a in args]
    assert named and all(len(n) == 2 for n in named), "give name=path pairs"
    if "--layout" in sys.argv:
        layout(named)
    else:
        pairs(named)


if __name__ == "__main__":
    main()
