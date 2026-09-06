"""Does the scene have equal contrast everywhere? The figure-ground number.

    python tools\\shot_contrast.py _runs/shots_exp_texel
    python tools\\shot_contrast.py A B          # two shot dirs, side by side
    python tools\\shot_contrast.py --selftest   # the calibration cases

WHY THIS EXISTS. `pixelcoat/docs/CONTRAST_DIRECTION.md` 3.4 specifies it, from
the review tests in the art standard's 22:

    Blur -- heavy blur, then measure what fraction of total luminance variance
    falls in the top decile of screen area. Uniform contrast lands near 0.10;
    a scene with a real focal point lands far above it. This is the single
    number that answers "does the scene have equal contrast everywhere".

It is the piece that "makes the standard visible in the level rather than in
the material library", and it is the one measurement that speaks to the
constraint every other instrument here is blind to: a moving body has to READ
against the wall behind it. 11 of the same standard: "Environment surfaces
near combat spaces should avoid ... repeated panel lines ... Busy edge
patterns behind enemies create visual camouflage." Nothing in this repo could
see that, so nothing checked it -- and the busiest materials measured are the
ones with the largest screen area.

WHAT IT DOES NOT MEASURE, said plainly because a partial number that looks
total is the recurring defect in this toolchain. This is the BLUR test only.
3.4 lists two others -- thumbnail and grayscale -- and both ask whether a
FOCAL MARKER separates from its local background. There are no enemies in a
Level Factory build (they belong to the consuming game), so there is no marker
to test, and inventing one would be measuring a thing this repo does not
place. When enemies exist, those two tests are the other half.

HOW THE NUMBER IS BUILT. The prose admits more than one reading, so the three
plausible ones were measured against the calibration it states -- uniform near
0.10, a focal point far above -- and only one reproduces both ends:

    frame              global-dev+blur   local-var+blur   local-var, no blur
    uniform noise                0.373            0.415                0.105
    even grating                 0.169            0.201                0.198
    one focal blob               0.959            0.998                0.999

So the number is: Rec.709 luminance on the 8-bit sRGB that reached the swap
chain -- the same frame and transfer `look_shots` reports, so the two agree
about what a pixel is -- then the VARIANCE WITHIN each cell of a 32-wide grid,
then the share of summed cell variance held by the top decile of cells.

THE DIVERGENCE FROM THE SPEC IS DELIBERATE AND IS RECORDED RATHER THAN TIDIED.
3.4 says "heavy blur", and heavy blur is what fails: blurred noise keeps
large-scale random blobs, so cell variances spread out and a flat frame reads
0.415 instead of the 0.10 the same sentence calibrates against. Fitting the
synthetic to the code until it passed would have been the easy move and the
wrong one. If the blur was meant to stop fine texture counting as contrast,
this metric does not need it: texture that is even across the frame gives every
cell a similar variance and therefore reads LOW, which is the answer wanted --
an evenly busy wall is exactly the camouflage 11 warns about.

`--selftest` pins both ends, and it is the first thing to run if this number
ever starts looking implausible.

THE FRAME BIASES THE NUMBER, SO STATE IT. `look_shots --interiors` puts a
station 3 m off a wall precisely so the wall fills the frame -- which drives
this number toward its floor by construction. Measured on the shipped
`precinct_yard_001`: `in_concrete_delco` 0.140 against `spawn` 0.854. That is
mostly the camera, not the level. The comparison this instrument supports is
THE SAME SHOT BETWEEN TWO BUILDS; comparing one camera against another is the
`site.tscn` mistake in a new costume.

READS THE FRAME, NAMES NO CAUSE. A low number means contrast is spread evenly.
Whether that is a flat level or a deliberately even one is a judgement, and it
belongs in the reply.
"""
from __future__ import annotations

import os
import sys

CELLS_X = 32          # 16:9 -> 32 x 18 cells, ~50 px per cell at 1600x900
TOP_DECILE = 0.10


def _luma(img):
    import numpy as np
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    return a @ np.array([0.2126, 0.7152, 0.0722], np.float32)


def concentration(img, cells_x=CELLS_X):
    """Share of local-contrast energy held by the top decile of screen cells.

    Cells are square-ish by construction: the vertical count is derived from
    the frame's aspect, so a cell is the same patch of screen on any render
    size and two resolutions stay comparable.
    """
    import numpy as np
    L = _luma(img)
    h, w = L.shape
    cy = max(1, int(round(cells_x * h / float(w))))
    ch, cw = h // cy, w // cells_x
    if ch < 1 or cw < 1:
        return None
    core = L[:ch * cy, :cw * cells_x]
    # Variance WITHIN each cell -- local contrast. Even contrast everywhere
    # gives every cell the same figure and a top decile of exactly 0.10; a
    # frame with somewhere to look concentrates it. See the header for the
    # three readings this was chosen from.
    grid = core.reshape(cy, ch, cells_x, cw).var(axis=(1, 3))
    flat = np.sort(grid.ravel())[::-1]
    total = flat.sum()
    if total <= 0.0:
        return 0.0
    n = max(1, int(round(flat.size * TOP_DECILE)))
    return float(flat[:n].sum() / total)


def _selftest():
    """Both ends of the calibration the docstring quotes."""
    import numpy as np
    from PIL import Image
    rng = np.random.default_rng(1999)
    h, w = 900, 1600

    flat = rng.normal(128, 18, (h, w)).clip(0, 255).astype(np.uint8)
    a = concentration(Image.fromarray(np.dstack([flat] * 3)))

    focal = np.full((h, w), 60, np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    focal += 180.0 * np.exp(-(((xx - 900) ** 2 + (yy - 400) ** 2) / (2 * 70.0 ** 2)))
    b = concentration(Image.fromarray(
        np.dstack([focal.clip(0, 255).astype(np.uint8)] * 3)))

    print("  uniform noise, no focal point : %.3f   (document says ~0.10)" % a)
    print("  one bright focal blob         : %.3f   (document says far above)" % b)
    ok = 0.06 <= a <= 0.16 and b > 0.5
    print("  SELFTEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def _shots(d):
    return sorted(f for f in os.listdir(d) if f.lower().endswith(".png"))


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return _selftest()
    if not argv:
        print(__doc__.strip().splitlines()[2].strip())
        return 2
    try:
        from PIL import Image
    except ImportError:
        print("[shot_contrast] NOT MEASURED: Pillow is not installed")
        return 1

    dirs = [a for a in argv if not a.startswith("-")]
    for d in dirs:
        if not os.path.isdir(d):
            print("[shot_contrast] NOT MEASURED: no such directory %s" % d)
            return 1

    names = _shots(dirs[0])
    if not names:
        print("[shot_contrast] NOT MEASURED: no PNGs in %s" % dirs[0])
        return 1

    head = "%-24s" % "shot" + "".join("%12s" % os.path.basename(d.rstrip("/\\"))[-11:]
                                      for d in dirs)
    print(head)
    print("-" * len(head))
    totals = [[] for _ in dirs]
    for n in names:
        row = "%-24s" % n[:-4]
        for i, d in enumerate(dirs):
            p = os.path.join(d, n)
            if not os.path.isfile(p):
                row += "%12s" % "-"
                continue
            v = concentration(Image.open(p))
            if v is None:
                row += "%12s" % "too small"
                continue
            totals[i].append(v)
            row += "%11.3f " % v
        print(row)
    print("-" * len(head))
    row = "%-24s" % "mean"
    for t in totals:
        row += "%11.3f " % (sum(t) / len(t)) if t else "%12s" % "-"
    print(row)
    print()
    print("share of LOCAL-CONTRAST energy in the top decile of screen cells.")
    print("~0.10 is contrast spread evenly -- nowhere for a moving body to")
    print("separate from; higher means the frame has somewhere to look.")
    print()
    print("COMPARE THE SAME CAMERA BETWEEN BUILDS, not one camera against")
    print("another. An `in_*` station stands 3 m off a wall so the wall FILLS")
    print("the frame, which floors this number by construction -- that is the")
    print("rig framing a material, not the level lacking a focal point.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
