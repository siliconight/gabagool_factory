"""drywall_orangepeel_delco: the cheetah print comes out.

Anchored; refuses on any miss. Run only after `cold_run.py --end` has
printed -- Pixelcoat is hashed by a run in flight.

WHAT WAS WRONG, measured rather than described. The shipped albedo is 256 px
over 2.0 m, 7.8 mm a texel. Real orange peel is a 2-5 mm stipple, so it is
sub-texel at this density and the grammar cannot draw it; what it drew
instead was `worley_f1` at 24 cells -- 8.3 cm blobs -- carrying 42% of the
tile, over a 40-cell micro band that is itself blobs at this size. On a wall
that reads as a spotted animal hide, which is what the walker saw.

Luminance-variance share in the 40-150 mm wavelength band ("blob"), the
band an 8 cm Worley cell lives in, on the synthesized 256 px albedo at seed
1999:

    shipped         48.0%    contrast 0.046
    C_fineworley    13.5%    contrast 0.035
    drywall_delco   10.0%    contrast 0.039   (the flat sibling, for scale)

The change keeps Worley -- orange peel IS a cellular stipple -- and moves it
to 120 cells (1.7 cm, two texels, the finest the density can carry) at 0.22
weight under a 160-cell fbm micro at 0.40, with height_strength 0.15 to
match the siblings. Chosen by eye from a four-way contact sheet; the numbers
are what the eye agreed with, not what chose.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
PC = ROOT / "pixelcoat"
GRAMMAR = PC / "profiles" / "materials" / "drywall_orangepeel_delco.json"
VERSION = PC / "VERSION"
CHANGELOG = PC / "CHANGELOG.md"
TEST = PC / "tests" / "test_drywall_orangepeel.py"


def edit(path, pairs, label):
    raw = path.read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: %s has mixed endings" % path)
    eol = "\r\n" if crlf else "\n"
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for i, (old, new) in enumerate(pairs):
        if t.count(old) != 1:
            raise SystemExit("REFUSED: %s anchor %d matched %d times"
                             % (label, i, t.count(old)))
        t = t.replace(old, new, 1)
    out = (t.replace("\n", eol) if eol == "\r\n" else t).encode("utf-8")
    path.write_bytes(out)
    print("[patch] %s: %d blocks, %d -> %d bytes"
          % (path.name, len(pairs), len(raw), len(out)))


GRAMMAR_PAIRS = [
    ('''  "bands": {
    "macro": 0.18,
    "meso": 0.42,
    "micro": 0.3
  },''',
     '''  "bands": {
    "macro": 0.18,
    "meso": 0.42,
    "micro": 0.15
  },'''),
    ('''  "meso": {
    "generator": "worley_f1",
    "cells": 24
  },
  "micro": {
    "generator": "fbm",
    "cells": 40,
    "octaves": 2
  },''',
     '''  "meso": {
    "generator": "fbm",
    "cells": 16,
    "octaves": 2
  },
  "micro": {
    "generator": "fbm",
    "cells": 160,
    "octaves": 2
  },'''),
    ('''  "height_strength": 0.3,''',
     '''  "height_strength": 0.15,'''),
]

CHANGELOG_OLD = '''# Changelog

## [0.51.0]'''
CHANGELOG_NEW = '''# Changelog

## [0.52.0] - orange-peel drywall stops being a cheetah print

`drywall_orangepeel_delco` read as a spotted hide on every interior wall it
dressed, and the walker called it: "We need to change/fix this". Measured
before touched:

THE TEXEL CANNOT HOLD THE FINISH. The pack is 256 px over 2.0 m, 7.8 mm a
texel. Real orange peel is a 2-5 mm stipple -- sub-texel at this density, so
the grammar cannot draw it and never did. What it drew was `worley_f1` at
24 cells (8.3 cm blobs) carrying 42% of the tile over a 40-cell micro fbm
that is itself blobs at this size. Eight-centimetre cells at 0.42 weight are
spots, whatever the grammar's name says.

THE NUMBER THAT SEES IT. Share of luminance variance at 40-150 mm
wavelength -- the band an 8 cm cell lives in -- on the synthesized albedo,
beside the neighbour correlation `tests/test_theme_profiles.py` already
held this grammar to (ac1, 1.0 smooth, 0.0 static):

    shipped (0.51.0)       blob 48.0%   grain 14%   ac1 0.70   spots
    C, worley at 120       blob 13.5%   grain 33%   ac1 0.27   static
    this (D)               blob  9.2%   grain 18%   ac1 0.64
    drywall_delco          blob 10.0%   grain 26%   ac1 0.60   (the flat sibling)

A first attempt at a spectrum metric reported a "dominant wavelength" of
666.7 mm for all four candidates -- the macro band, the same for every one
-- and was thrown out for the band shares above, which move between rows. A
metric that cannot move is not evidence (CLAUDE.md, draw-call section).

THE FIRST PICK WAS RETRACTED BY AN OLDER INSTRUMENT. The walker chose C from
a four-way contact sheet: Worley kept, because orange peel IS a cellular
stipple, taken to 120 cells (1.7 cm, two texels). It passed the blob gate
and failed `test_delco_interior_finishes_read_as_surface_not_noise` at ac1
0.27 against a floor of 0.5 -- a floor written from the walker's own
earlier complaint, "too much digital noise". C had traded spots for static;
two instruments, two things the walker has objected to, and C satisfied
one. A sweep of 648 grammars found 139 that pass both; a second sheet put
four of them beside the shipped and C, and the walker chose this one.

THE CHANGE is fbm at 16 cells (12.5 cm, two octaves) at 0.42 in place of
the Worley -- the cheetah print is the cell structure, not the scale, and
Worley at ANY cell count this density can draw is either spots or static --
under a 160-cell fbm micro at 0.15; `height_strength` 0.30 -> 0.15, in line
with the other drywalls. It reads as a soft mottled plaster. It is NOT
orange peel: real orange peel is 2-5 mm, this pack's texel is 7.8 mm, and no
grammar at this density can draw the finish the id names. A wall that is
neither spots nor static is what can be had; the name is kept because the
theme keys on it.

A SECOND FAULT THE SAME MEASUREMENT TURNED UP. The 0.51.0 tile was blown
(L > 0.94) on 2.2% of its texels against the audit's 1% budget -- a light
base under a 0.42 blob band -- and no test had ever held this grammar to the
audit. 0.52.0 measures 0.18%. Not a goal of the change; recorded because it
moved.

Held by `tests/test_drywall_orangepeel.py`: blob share under 25% (the
0.51.0 grammar fails it at 48%, and the test rebuilds that grammar to prove
the metric can see it), grain share under 25% (C fails it at 33%), the
tile still tiles, and it meets the audit's budget. The ac1 floor stays
where it was, in `test_theme_profiles.py`. Interior walls carry this on
every level, so a cold run is the confirmation that matters and is the
next thing.

## [0.51.0]'''

TEST_SRC = '''"""drywall_orangepeel_delco: neither spots nor static.

The 0.51.0 grammar drew 8 cm Worley cells at 0.42 weight and read as a
spotted hide on every interior wall; the first replacement traded the
spots for texel-scale static and failed the ac1 floor in
`test_theme_profiles.py` (CHANGELOG 0.52.0). Real orange peel is 2-5 mm and
sub-texel at this pack's 7.8 mm/texel, so no grammar here can draw the
finish; what it CAN avoid is both failure modes, and this measures both.
The ac1 floor itself stays in `test_theme_profiles.py`.
"""
import os

import numpy as np

from pixelcoat.core import material_grammar as mg
from tools import art_standard_audit as audit

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_MATERIALS = os.path.join(_ROOT, "profiles", "materials")
_SEED = 1999
GID = "drywall_orangepeel_delco"

#: the wavelength band an 8 cm Worley cell lives in, mm
BLOB_MM = (40.0, 150.0)
#: shipped 0.51.0 measured 48.0%; 0.52.0 9.2%; the flat sibling 10.0%
BLOB_SHARE_MAX = 0.25
#: under 20 mm is two texels and below: the static band. The retracted
#: Worley-at-120 candidate measured 33%; 0.52.0 18%; the sibling 26%
GRAIN_MM = (0.0, 20.0)
GRAIN_SHARE_MAX = 0.25


def _load(gid):
    return mg.MaterialGrammar.load(os.path.join(_MATERIALS, gid + ".json"))


def _synth(gid):
    g = _load(gid)
    px = mg.pack_size_for(g.meters_per_tile)
    return g, px, mg.synthesize(g, size=px, seed=_SEED)


def _luma01(albedo_u8):
    a = albedo_u8[..., :3].astype(np.float64)
    return (0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]) / 255.0


def band_share(albedo_u8, meters_per_tile, lo_mm, hi_mm):
    """Share of the tile's luminance variance whose wavelength, in mm on
    the wall, falls in [lo_mm, hi_mm]. Radial power spectrum; DC excluded.
    The tile is square, so one axis sets the scale."""
    a = _luma01(albedo_u8)
    a = a - a.mean()
    px = a.shape[0]
    mm_per_px = meters_per_tile * 1000.0 / px
    f = np.abs(np.fft.fftshift(np.fft.fft2(a))) ** 2
    cy, cx = np.array(f.shape) // 2
    yy, xx = np.indices(f.shape)
    k = np.hypot(yy - cy, xx - cx)
    wl = np.where(k > 0, (px / np.maximum(k, 1e-9)) * mm_per_px, np.inf)
    tot = f[k > 0].sum()
    return float(f[(wl >= lo_mm) & (wl <= hi_mm)].sum() / tot)


def _wrap_no_worse_than_interior(arr):
    a = arr.astype(np.int32)
    if a.ndim == 2:
        a = a[..., None]
    rows = np.abs(np.diff(a, axis=0)).mean(axis=(1, 2))
    cols = np.abs(np.diff(a, axis=1)).mean(axis=(0, 2))
    wy = float(np.abs(a[0] - a[-1]).mean())
    wx = float(np.abs(a[:, 0] - a[:, -1]).mean())
    return (wy, float(rows.max())), (wx, float(cols.max()))


def test_orange_peel_is_not_a_blob_field():
    """The cheetah print, as a number. Fails against the 0.51.0 grammar
    (48%) and passes the 0.52.0 one (13.5%), with the flat `drywall_delco`
    at 10% as the floor a plain wall sits on."""
    g, _, s = _synth(GID)
    share = band_share(s["albedo"], g.meters_per_tile, *BLOB_MM)
    assert share <= BLOB_SHARE_MAX, share
    # ...and the metric can see a blob field: the grammar that was the
    # defect, rebuilt from the shipped numbers, sits well over the line.
    raw = dict(g.__dict__)
    raw["bands"] = {"macro": 0.18, "meso": 0.42, "micro": 0.3}
    raw["meso"] = {"generator": "worley_f1", "cells": 24}
    raw["micro"] = {"generator": "fbm", "cells": 40, "octaves": 2}
    old = mg.MaterialGrammar.from_dict(raw)
    px = mg.pack_size_for(old.meters_per_tile)
    was = band_share(mg.synthesize(old, size=px, seed=_SEED)["albedo"],
                     old.meters_per_tile, *BLOB_MM)
    assert was > 1.5 * BLOB_SHARE_MAX, was    # measured 0.480


def test_orange_peel_is_not_static_either():
    """The other failure mode, the one the first replacement had. Worley at
    120 cells passed the blob gate and put a third of the tile's variance
    under 20 mm -- ac1 0.27 -- which is the digital noise the theme test's
    floor exists for. Flatter than it was, not flat: some contrast stays."""
    g, _, s = _synth(GID)
    grain = band_share(s["albedo"], g.meters_per_tile, *GRAIN_MM)
    assert grain <= GRAIN_SHARE_MAX, grain
    lum = _luma01(s["albedo"])
    assert 0.02 <= lum.std() <= 0.06, lum.std()
    raw = dict(g.__dict__)
    raw["bands"] = {"macro": 0.18, "meso": 0.22, "micro": 0.4}
    raw["meso"] = {"generator": "worley_f1", "cells": 120}
    raw["micro"] = {"generator": "fbm", "cells": 160, "octaves": 2}
    c = mg.MaterialGrammar.from_dict(raw)
    px = mg.pack_size_for(c.meters_per_tile)
    was = band_share(mg.synthesize(c, size=px, seed=_SEED)["albedo"],
                     c.meters_per_tile, *GRAIN_MM)
    assert was > GRAIN_SHARE_MAX, was    # measured 0.333


def test_orange_peel_tiles_and_meets_the_art_standard():
    """Held to the audit's own budget rather than to zero, because the
    0.51.0 grammar was ALSO blown on 2.2% of its texels against a 1%
    budget -- a light base colour under an 0.42 blob band -- and nothing
    had ever measured it. 0.52.0 measures 0.18%."""
    g, _, s = _synth(GID)
    for key, arr in s.items():
        for wrap, worst in _wrap_no_worse_than_interior(arr):
            assert wrap <= worst + 1e-6, (key, wrap, worst)
    row = audit.measure(g, mg.synthesize(g, size=256, seed=_SEED))
    b = audit.ENV_BUDGET
    assert row["crushed_frac"] <= b["crushed_frac"], row["crushed_frac"]
    assert row["blown_frac"] <= b["blown_frac"], row["blown_frac"]
    assert row["value_range"] <= b["value_range"], row["value_range"]
    assert row["rough_mean"] >= b["rough_mean_min"], row["rough_mean"]
    assert not row["emissive"]
    assert set(s) == {"albedo", "roughness"}, sorted(s)
'''


def main() -> int:
    edit(GRAMMAR, GRAMMAR_PAIRS, "drywall_orangepeel_delco.json")
    edit(VERSION, [("Pixelcoat 0.51.0", "Pixelcoat 0.52.0")], "VERSION")
    edit(CHANGELOG, [(CHANGELOG_OLD, CHANGELOG_NEW)], "CHANGELOG.md")
    if TEST.exists():
        raise SystemExit("REFUSED: %s exists" % TEST)
    TEST.write_text(TEST_SRC, encoding="utf-8", newline="\n")
    print("[patch] wrote %s" % TEST.name)
    g = json.loads(GRAMMAR.read_text(encoding="utf-8"))
    assert g["meso"] == {"generator": "fbm", "cells": 16, "octaves": 2}, g
    assert g["bands"] == {"macro": 0.18, "meso": 0.42, "micro": 0.15}, g
    return 0


if __name__ == "__main__":
    sys.exit(main())
