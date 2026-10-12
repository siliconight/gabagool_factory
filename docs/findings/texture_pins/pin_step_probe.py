"""Which step of the export undoes the shared textures' import pins?

`pin_loss_probe.py` REFUTED the first suspicion: one `--import` on a stripped package leaves no
PNG under `_tex/` without a sidecar (0 of 415, three trials), so the pin step does find every
sidecar. This runs Level Factory's own `export._write_import_sidecars` -- pass one, the pins, the
GLB sidecars rewritten, the extracted PNGs dropped, the cache removed, pass two -- on a stripped
copy of a package, counts the pinned sidecars under `_tex/` after it, then runs one more `--import`
over the cache it left (as the light bake does twice) and counts again. Two trials. It measures
and prints.

    python docs/findings/texture_pins/pin_step_probe.py <package dir>
"""
import collections
import os
import shutil
import subprocess
import sys
import time

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "level_factory"))
from pathlib import Path  # noqa: E402

from packages.exporting import export as E  # noqa: E402

G = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
X = os.path.join(F, "_scratch", "texture_pins")


def census(root):
    """(pinned, defaulted, other) over the sidecars under `_tex/`, by the two pins that are always
    set: mipmaps generated and the alpha border left alone."""
    c = collections.Counter()
    for r, _, fs in os.walk(root):
        if os.path.basename(r) != "_tex":
            continue
        for f in fs:
            if not f.endswith(".png.import"):
                continue
            text = open(os.path.join(r, f), encoding="utf-8", errors="replace").read()
            mip = "mipmaps/generate=true" in text
            fab = "process/fix_alpha_border=false" in text
            c["pinned" if (mip and fab) else "defaulted" if (not mip and not fab) else "mixed"] += 1
    return dict(c)


def main():
    src = os.path.abspath(sys.argv[1])
    shutil.rmtree(X, ignore_errors=True)
    os.makedirs(X)
    for trial in (1, 2):
        p = os.path.join(X, "pkg_%d" % trial)
        shutil.copytree(src, p)
        shutil.rmtree(os.path.join(p, ".godot"), ignore_errors=True)
        for r, _, fs in os.walk(p):
            for f in fs:
                if f.endswith(".import"):
                    os.remove(os.path.join(r, f))
        t0 = time.time()
        n = E._write_import_sidecars(Path(p), G)
        print("trial %d: _write_import_sidecars %.1f s, %d sidecars; under _tex/: %s"
              % (trial, time.time() - t0, n, census(p)))
        t0 = time.time()
        subprocess.run([G, "--headless", "--path", p, "--import"], stdin=subprocess.DEVNULL,
                       capture_output=True, timeout=1200)
        print("          one more --import over its cache %.1f s; under _tex/: %s"
              % (time.time() - t0, census(p)))
        shutil.rmtree(p, ignore_errors=True)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
