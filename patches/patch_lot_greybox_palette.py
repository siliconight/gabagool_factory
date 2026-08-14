r"""The site stops being one flat grey: ground, paths, courts, the perimeter
box and cover each get a value the eye can separate.

    python patch_lot_greybox_palette.py --palette   # the numbers, no files touched
    python patch_lot_greybox_palette.py --check
    python patch_lot_greybox_palette.py
    python patch_lot_greybox_palette.py --verify <site.tscn>
    python patch_lot_greybox_palette.py --revert

Run from the FACTORY ROOT (the directory holding `lot/`).

## The defect

`_box_node` and `_yaw_box_node` have taken a `color=` argument since they were
written, and emit a `StandardMaterial3D` override when they get one:

    mat_line = f'material_override = SubResource("Mat_{name}")' if color else ''

Three callers pass one -- `road_*`, `sidewalk_*`, `blocker_*`. Five do not:

    Ground / Ground_1 ... Ground_N     the plate the whole level stands on
    path_0 ... path_N                  every route between two buildings
    courtyard_0 ... courtyard_N        designed open space
    perim_N / perim_S / perim_E / perim_W   the box around the level
    cover_0 ... cover_N                the things you take cover behind

Counted in `lot-demo-ws/.level_factory/preview/lot_demo_001_walk/site.tscn`:
**49 uncoloured boxes -- 36 ground tiles, 4 paths, 4 perimeter walls, 5 cover
-- and not one road, sidewalk or blocker in the scene.** Every coloured caller
Lot has is a caller the generated spec never reaches. That is the whole of "the
level is a flat grey box": the three surfaces that carry colour are exactly the
three a generated site does not emit.

## The rule this palette follows, and where it broke

`patch_dc_greybox_palette.py` adopted "value separates function, hue names it",
with contrast checked only between surfaces that share a view, at a floor of
0.15 relative luminance.

Applied to the site that rule is **infeasible, and this was measured, not
guessed.** Solving the full co-read graph -- ground, path, courtyard, road,
sidewalk, perimeter, cover, blocker, against Deli Counter's fixed wall and
roof -- for the largest gap that satisfies every pair:

    max achievable min-gap over the full co-read graph: 0.140

and the assignment that reaches it is degenerate (path and courtyard land on
the same near-black, blockers on pure white). Relaxing to walkable-vs-blocking
only lifts it to 0.159. Value is a one-dimensional budget: at 0.15 it holds
about seven slots, and between Lot and Deli Counter there are seventeen
surfaces asking for one.

So value is spent where it answers the question a player actually asks --
**can I stand here, or is this in my way** -- and everything that answers a
different question is a marker carried by chroma, which is the convention Deli
Counter's palette already uses for stairs, ladders, doorways and breaches.

VALUE LADDER -- the surfaces that answer "can I stand here". These clear each
other by 0.15 in relative luminance, and `--palette` refuses if they do not:

    road         0.131   asphalt, unchanged
    ground       0.317   the plate: cool, mid-dark, the base for everything
    path         0.478   a walked surface, warm
    wall         0.710   Deli Counter's exterior, fixed here
    perimeter    0.879   the edge of the world

    gaps: 0.186  0.161  0.232  0.169     -- every one over 0.15

MARKERS -- these answer a different question, so chroma carries them and their
luminance is free. Each must clear the surface it sits on by 0.25 saturation:

    cover        0.448   saturated green: a thing you use, not a surface
    blocker      0.310   warm massing: a building you cannot enter

ONE BAND, TWO MEMBERS -- both walkable, so value has nothing to say. A visible
seam plus opposite hue casts:

    path / courtyard    seam 0.036   warmth +0.13 vs -0.07
    path / sidewalk     seam 0.073   warmth +0.13 vs -0.02

Three choices worth stating rather than leaving to be discovered:

  * **The perimeter is bright, not dark.** Dark was tried first and is
    arithmetically unavailable: it would have to clear road's 0.131 by 0.15,
    which puts it below zero. Bright also happens to be right -- a uniform
    chalky boundary reads as "outside the level" and never as floor.

  * **Cover is a marker.** It sits on ground, on paths and on courtyards, and
    no value clears all three plus the wall plus the perimeter.

  * **BLOCKER_COLOR moves.** It is an existing constant and this patch changes
    it, because the check refused the old one: a building-sized mass standing
    on the new plate was 0.03 apart in luminance and 0.09 in saturation from
    the plate itself. That is the flat-grey complaint in miniature, and
    leaving it because it was already written would have been the wrong kind
    of restraint. Same warm-massing intent, enough chroma to carry it.

## What this does NOT fix -- corrected

An earlier draft of this docstring claimed the walk preview was unlit, on a
grep of `site.tscn`. That was wrong: `site.tscn` is the CONTENT scene and the
dev light rig lives in the wrapper, `walk.tscn`, exactly where
`build_walk_preview` says it puts it. The preview IS lit. Retracted.

What is true is that the rig is badly balanced -- directionless ambient at 1.4
against a 0.6 sun with shadows off, so a wall and the floor it stands on render
at nearly the same value whatever their albedo. `patch_lf_preview_lighting.py`
is that fix. This palette makes surfaces distinguishable from each other; that
one makes their form read. They are complementary and neither substitutes for
the other.

Separately and still open: `lux_apply`'s output never reaches the preview at
all. `walk_content_dir` returns `themed_site_assemble/out` and never looks at
`lux_apply/out`; `_find_level_scene` prefers a file named `site_lux.tscn` while
lux writes `lux.applied.tscn`. Nothing in the tree writes `site_lux.tscn`, so
that branch has never fired.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

LOT = Path("lot") / "lot.py"
SIDECAR = ".pre_lotpalette"


# --------------------------------------------------------------------------
# the palette
# --------------------------------------------------------------------------

#: Relative luminance, Rec. 709. The same weighting `patch_dc_greybox_palette`
#: checks with, so the two palettes are comparable in one number.
def lum(c) -> float:
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


NEW = {
    "ground":    (0.30, 0.32, 0.34),
    "path":      (0.53, 0.47, 0.40),
    "courtyard": (0.48, 0.52, 0.55),
    "perimeter": (0.87, 0.88, 0.90),
    "cover":     (0.18, 0.55, 0.22),
    # MOVED, not new. The first draft of this patch kept the existing
    # (0.38, 0.34, 0.30) and the check below refused it: a building-sized mass
    # standing on the plate was 0.03 in luminance and 0.09 in saturation from
    # the plate itself, which is the flat-grey complaint in miniature. Same
    # warm-massing intent, enough chroma to be seen carrying it.
    "blocker":   (0.46, 0.28, 0.16),
}

#: Already in `lot.py`, and not moved by this patch.
KEPT = {
    "road":     (0.13, 0.13, 0.14),
    "sidewalk": (0.55, 0.55, 0.57),
}

#: Deli Counter's greybox palette. Not ours to move; the site is checked
#: against it because a building stands on the plate and is seen with it.
DC = {
    "wall":    (0.72, 0.71, 0.68),
    "roof":    (0.52, 0.56, 0.60),
    "doorway": (0.05, 0.42, 0.50),
    "stair":   (1.00, 0.78, 0.32),
    "ladder":  (1.00, 0.90, 0.55),
    "prop":    (0.28, 0.30, 0.26),
}

#: Surfaces whose read is "can I stand here or is this in my way". These must
#: clear each other on VALUE where they share a view -- hue is not allowed to
#: do this job, which is the mistake the Deli Counter palette was caught making
#: on its first draft (floor vs stair, gap 0.042).
LADDER = ("road", "ground", "path", "wall", "perimeter")
MIN_VALUE_GAP = 0.15

#: Markers. Chroma carries them, so their luminance is deliberately free. Each
#: is required instead to clear the surface it sits on by SATURATION, because
#: chroma against a near-neutral field is what makes them findable.
MARKERS = {
    "cover":   ("ground", "path", "courtyard"),
    "blocker": ("ground", "road", "sidewalk"),
}
MIN_SAT_GAP = 0.25

#: Two members of one band, distinguished from each other by hue direction
#: rather than by value: both are walkable, so value has nothing to say. A
#: seam still has to be visible, and the casts have to point opposite ways --
#: saturation cannot see this, which is why it is measured separately. The
#: first draft claimed "cool hue names it apart" for courtyard and the
#: saturation check called that bluff (gap 0.01); this is the metric that
#: actually holds the claim to account.
SAME_BAND = (("path", "courtyard"), ("path", "sidewalk"))
MIN_SEAM = 0.03
MIN_WARMTH_GAP = 0.10


def warmth(c) -> float:
    """Red minus blue: positive is a warm cast, negative a cool one."""
    return c[0] - c[2]


def sat(c) -> float:
    hi, lo = max(c), min(c)
    return 0.0 if hi <= 0 else (hi - lo) / hi


def _all():
    out = dict(KEPT)
    out.update(NEW)
    out.update(DC)
    return out


def _palette(verbose: bool = True) -> int:
    every = _all()
    bad = 0
    if verbose:
        print("  value ladder -- these answer 'can I stand here'")
    rungs = sorted(LADDER, key=lambda k: lum(every[k]))
    prev = None
    for k in rungs:
        v = lum(every[k])
        gap = "" if prev is None else f"   gap {v - prev:.3f}"
        if prev is not None and v - prev < MIN_VALUE_GAP - 1e-9:
            gap += "   <-- UNDER 0.15"
            bad = 1
        if verbose:
            print(f"    {k:<11} {v:.3f}{gap}")
        prev = v

    if verbose:
        print()
        print("  markers -- chroma carries these, luminance is free")
    for marker, against in MARKERS.items():
        ms, ml = sat(every[marker]), lum(every[marker])
        line = f"    {marker:<11} lum {ml:.3f}  sat {ms:.2f}   vs "
        parts = []
        for other in against:
            os_ = sat(every[other])
            d = abs(ms - os_)
            flag = "" if d >= MIN_SAT_GAP - 1e-9 else "  <-- UNDER 0.25"
            if flag:
                bad = 1
            parts.append(f"{other} {d:+.2f}{flag}")
        if verbose:
            print(line + ", ".join(parts))

    if verbose:
        print()
        print("  one band, two members -- hue direction, not value")
    for a, b in SAME_BAND:
        seam = abs(lum(every[a]) - lum(every[b]))
        cast = abs(warmth(every[a]) - warmth(every[b]))
        flags = ""
        if seam < MIN_SEAM - 1e-9:
            flags += "  <-- NO SEAM"
            bad = 1
        if cast < MIN_WARMTH_GAP - 1e-9:
            flags += "  <-- SAME CAST"
            bad = 1
        if verbose:
            print(f"    {a} / {b:<11} seam {seam:.3f}   warmth "
                  f"{warmth(every[a]):+.2f} vs {warmth(every[b]):+.2f}"
                  f"   d {cast:.2f}{flags}")

    if verbose:
        print()
        print("  every surface, by luminance")
        for k, v in sorted(every.items(), key=lambda kv: lum(kv[1])):
            src = ("lot" if k in NEW else
                   "lot/kept" if k in KEPT else "deli_counter")
            print(f"    {lum(v):.3f}  {k:<11} {src}")
    if verbose:
        print()
        print("  FAIL" if bad else "  palette holds")
    return bad


# --------------------------------------------------------------------------
# the edits
# --------------------------------------------------------------------------

CONST_OLD = """ROAD_COLOR = (0.13, 0.13, 0.14)        # asphalt
SIDEWALK_COLOR = (0.55, 0.55, 0.57)    # concrete, raised curb"""

CONST_NEW = '''#: The site's greybox palette. Everything below except the two street colours
#: was emitting NO material at all: a generated spec produces ground, paths, a
#: perimeter and cover, and not one of those was a coloured caller.
#:
#: Value carries the read that matters outdoors -- can I stand here, or is this
#: in my way -- and the surfaces answering it are held 0.15 apart in relative
#: luminance:
#:
#:     road 0.131 < ground 0.317 < path 0.478 < DC wall 0.710 < perimeter 0.879
#:
#: Anything answering a DIFFERENT question is a marker carried by chroma
#: instead, which is the convention Deli Counter's palette already uses for
#: stairs, ladders, doorways and breaches. Value is one-dimensional: solving the
#: full co-read graph for the largest gap that satisfies every pair returns
#: 0.140, below the floor, so not every surface can have one. Spending it on the
#: walk/block question and marking the rest is a choice, and this is where it is
#: written down. `patch_lot_greybox_palette.py --palette` re-checks these
#: numbers and refuses to write them if they stop holding.
#:
#: The perimeter is bright rather than dark for a reason that is arithmetic
#: before it is taste: dark would have to clear road's 0.131 by 0.15, which is
#: below zero. Bright is also the better read -- a uniform chalky boundary is
#: never mistaken for floor.
ROAD_COLOR = (0.13, 0.13, 0.14)        # 0.131 -- asphalt
SIDEWALK_COLOR = (0.55, 0.55, 0.57)    # 0.551 -- concrete, raised curb
GROUND_COLOR = (0.30, 0.32, 0.34)      # 0.317 -- the plate everything is read against
PATH_COLOR = (0.53, 0.47, 0.40)        # 0.478 -- a walked surface; warm cast names it
COURT_COLOR = (0.48, 0.52, 0.55)       # 0.514 -- path's band, cool cast names it apart
PERIM_COLOR = (0.87, 0.88, 0.90)       # 0.879 -- the edge of the world: bright, flat, dead
COVER_COLOR = (0.18, 0.55, 0.22)       # 0.448 -- a MARKER: chroma finds it, value is free

#: Warm massing -- reads as a building you can't enter. MOVED from
#: (0.38, 0.34, 0.30): against the new plate that was 0.03 apart in luminance
#: and 0.09 in saturation, which is the flat-grey complaint in miniature. Same
#: intent, enough chroma to carry it.
BLOCKER_COLOR = (0.46, 0.28, 0.16)     # 0.310'''


GROUND_OLD = """            bl, sr = _box_node("Ground" if j == 0 else f"Ground_{j}",
                               (x1 - x0, GROUND_THICK - GROUND_SINK, y1 - y0),
                               ((x0 + x1) / 2,
                                -(GROUND_THICK + GROUND_SINK) / 2,
                                -(y0 + y1) / 2))"""

GROUND_NEW = """            bl, sr = _box_node("Ground" if j == 0 else f"Ground_{j}",
                               (x1 - x0, GROUND_THICK - GROUND_SINK, y1 - y0),
                               ((x0 + x1) / 2,
                                -(GROUND_THICK + GROUND_SINK) / 2,
                                -(y0 + y1) / 2),
                               GROUND_COLOR)"""


PATH_OLD = """        bl, sr = _yaw_box_node(f"path_{i}",
                               (length, PATH_THICK + GROUND_SINK, w),
                               (cx, (PATH_THICK - GROUND_SINK) / 2, -cy), -ang)"""

PATH_NEW = """        bl, sr = _yaw_box_node(f"path_{i}",
                               (length, PATH_THICK + GROUND_SINK, w),
                               (cx, (PATH_THICK - GROUND_SINK) / 2, -cy), -ang,
                               PATH_COLOR)"""


COURT_OLD = """        bl, sr = _box_node(f"courtyard_{i}",
                           (sx, COURT_THICK + GROUND_SINK, sy),
                           (cx, (COURT_THICK - GROUND_SINK) / 2, -cy))"""

COURT_NEW = """        bl, sr = _box_node(f"courtyard_{i}",
                           (sx, COURT_THICK + GROUND_SINK, sy),
                           (cx, (COURT_THICK - GROUND_SINK) / 2, -cy),
                           COURT_COLOR)"""


PERIM_OLD = """        ]:
            bl, sr = _box_node(name, size, at_xyz)"""

PERIM_NEW = """        ]:
            bl, sr = _box_node(name, size, at_xyz, PERIM_COLOR)"""


COVER_OLD = """        bl, sr = _box_node(f"cover_{i}", (sx, sy, sz), (cx, sy / 2, -cy))"""

COVER_NEW = """        bl, sr = _box_node(f"cover_{i}", (sx, sy, sz), (cx, sy / 2, -cy),
                           COVER_COLOR)"""


BLOCKER_OLD = """BLOCKER_COLOR = (0.38, 0.34, 0.30)     # warm massing -- reads as a building you can't enter"""

BLOCKER_NEW = """# BLOCKER_COLOR moved up into the palette block above, where the numbers that
# constrain it are written down."""


EDITS = {
    LOT: ((CONST_OLD, CONST_NEW),
          (BLOCKER_OLD, BLOCKER_NEW),
          (GROUND_OLD, GROUND_NEW),
          (PATH_OLD, PATH_NEW),
          (COURT_OLD, COURT_NEW),
          (PERIM_OLD, PERIM_NEW),
          (COVER_OLD, COVER_NEW)),
}

_CRLF = "\r\n"


def _find(body: str, anchor: str):
    for candidate in (anchor, anchor.replace("\n", _CRLF)):
        count = body.count(candidate)
        if count:
            return candidate, count
    return anchor, 0


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(path: Path, edits, *, check: bool) -> int:
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR)

    done = sum(1 for _o, new in edits if _find(body, new)[1] == 1)
    if done == len(edits):
        print(f"  already applied  {path.name}")
        return 0
    if done:
        print(f"REFUSING: {path.name} has {done} of {len(edits)} edits already "
              f"present.")
        return 1

    out = body
    for old, new in edits:
        anchor, count = _find(out, old)
        if count != 1:
            print(f"REFUSING: {path.name} -- expected 1 occurrence of an "
                  f"anchor, found {count}.")
            print(f"  anchor starts: {old.splitlines()[0].strip()!r}")
            return 1
        out = out.replace(
            anchor, new.replace("\n", _CRLF) if _CRLF in anchor else new, 1)

    data = out.encode("utf-8")
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        return 0
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


# --------------------------------------------------------------------------
# --verify: read a built site.tscn and count what actually carries a material
# --------------------------------------------------------------------------

_NODE = re.compile(r'^\[node name="([^"]+)" type="([^"]+)" parent="([^"]*)"',
                   re.M)
_OVERRIDE = re.compile(r'^material_override = SubResource\("Mat_([^"]+)"\)',
                       re.M)
_ALBEDO = re.compile(
    r'^\[sub_resource type="StandardMaterial3D" id="Mat_([^"]+)"\]\s*\n'
    r'(?:transparency = 1\s*\n)?'
    r'albedo_color = Color\(([^)]*)\)', re.M)

#: Which node-name prefix belongs to which palette entry.
_OWNER = (("Ground", "ground"), ("path_", "path"), ("courtyard_", "courtyard"),
          ("perim_", "perimeter"), ("cover_", "cover"), ("road_", "road"),
          ("sidewalk_", "sidewalk"), ("kerbcut_", "road"),
          ("blocker_", "blocker"))


def _owner(name: str):
    for prefix, key in _OWNER:
        if name == prefix or name.startswith(prefix):
            return key
    return None


def _verify(scene: Path) -> int:
    text = scene.read_text(encoding="utf-8", errors="replace")
    overrides = set(_OVERRIDE.findall(text))
    colors = {}
    for name, body in _ALBEDO.findall(text):
        try:
            colors[name] = tuple(float(p) for p in body.split(","))[:3]
        except ValueError:
            pass

    owned, unpainted, wrong = {}, [], []
    for name, ntype, parent in _NODE.findall(text):
        if parent != "." or ntype != "StaticBody3D":
            continue
        key = _owner(name)
        if key is None:
            continue
        owned.setdefault(key, []).append(name)
        if name not in overrides:
            unpainted.append(name)
            continue
        got, want = colors.get(name), _all().get(key)
        if got and want and max(abs(a - b) for a, b in zip(got, want)) > 1e-6:
            wrong.append((name, got, want))

    print(f"  {scene}")
    for key in sorted(owned):
        names = owned[key]
        miss = sum(1 for n in names if n in unpainted)
        mark = "  UNPAINTED" if miss else ""
        print(f"    {key:<11} {len(names):>3} node(s)"
              f"   lum {lum(_all()[key]):.3f}"
              f"   missing {miss}{mark}")
    for name, got, want in wrong:
        print(f"    WRONG COLOUR  {name}  got {got}  want {want}")
    if not owned:
        print("    no site boxes found -- is this a composed scene rather "
              "than a lot scene?")
        return 1
    bad = 1 if (unpainted or wrong) else 0
    print("  FAIL" if bad else "  every site box carries its palette colour")

    # NOT a defect when it is zero, and an earlier version of this line said it
    # was. A content scene is not supposed to carry lighting: the walk preview's
    # dev rig lives in the WRAPPER, `walk.tscn`, and a Lux-applied scene owns its
    # own. Reporting "unlit" off this file was reading the wrong artefact. The
    # count is still worth printing -- a content scene that suddenly grows lights
    # means something upstream changed -- it just is not a verdict.
    lights = len(re.findall(r'type="(?:\w*Light3D|WorldEnvironment)"', text))
    print(f"  lights in this CONTENT scene: {lights}"
          + ("   (expected -- the rig is in walk.tscn; check it with "
             "patch_lf_preview_lighting.py --verify)" if lights == 0
             else "   <-- unexpected: content scenes do not carry lighting"))
    return bad


def main(argv: list[str]) -> int:
    if "--palette" in argv:
        return _palette()

    if "--verify" in argv:
        i = argv.index("--verify")
        if i + 1 >= len(argv):
            raise SystemExit("--verify needs a path to a built site.tscn")
        return _verify(Path(argv[i + 1]))

    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root (the directory holding lot/)")

    if "--revert" in argv:
        bad = 0
        for rel in EDITS:
            path = root / rel
            side = path.with_suffix(path.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {path.name}")
                bad = 1
                continue
            path.write_bytes(side.read_bytes())
            print(f"  reverted     {path.name}")
        return bad

    if _palette(verbose=False):
        print("REFUSING: the palette fails its own check -- fix the numbers "
              "before writing them into lot.py.")
        return 1

    check = "--check" in argv
    for rel, edits in EDITS.items():
        code = _apply(root / rel, edits, check=check)
        if code:
            return code
    if not check:
        print()
        print("  Palette: python patch_lot_greybox_palette.py --palette")
        print("  Then:    re-run the mission and verify the built scene --")
        print("           python patch_lot_greybox_palette.py --verify \\")
        print("             lot-demo-ws\\.level_factory\\preview\\"
              "lot_demo_001_walk\\site.tscn")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
