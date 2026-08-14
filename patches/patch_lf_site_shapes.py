r"""A site can be a shape other than a line.

    python patch_lf_site_shapes.py --check
    python patch_lf_site_shapes.py
    python patch_lf_site_shapes.py --verify
    python patch_lf_site_shapes.py --revert

Run from the FACTORY ROOT.

## Why

`site_variation` places every candidate as a ROW centred on the origin.
`row_offsets` returns X positions only; the whole lateral freedom is
`_ACROSS = (-10,-5,0,5,10)`. Its own comment names what that costs:

    "Across-row stagger. This is the one that changes sightlines: a staggered
     row breaks the single long firing lane a flush row creates."

Measured 2026-08-09 with `probe_sightlines`, on all three candidates of
`lot_demo_001`: longest open lane **287 / 299 / 247 m, every one at 0 degrees**
-- straight down the row, past every front door, five to six times the 45 m at
which Laser Tag's crew opens fire. The yaw, the nudge and the stagger move the
LENGTH of that lane and never its DIRECTION, because the row is the lane.
In-engine agrees: 48-50% of walkable positions visible to 3+ enemy spawns, and
Lot placing cover against a 140.3 m open sightline.

`MissionBrief.site_shape` has existed the whole time, is written into the spec
at `_write_site_spec`, and is read by nothing.

## What this adds

`layout_offsets(shape, footprints)` -> `[(x, y), ...]`, and three shapes:

    row         the line, unchanged
    L           two arms about one corner
    courtyard   a closed ring with open ground in the middle

Each step between consecutive buildings is sized by the two shells that share
it -- both reaches, the street, and the slack for the nudge each neighbour can
make toward the other -- which is `row_offsets`' rule, applied per step instead
of per row. The slack term is per AXIS, because the nudges are: `_ALONG` moves
x and `_ACROSS` moves y, and they are not the same size.

## Compatibility, which is the whole care here

**`shape="row"` delegates to `row_offsets`.** Not "reproduces" -- delegates, so
there is one implementation and it cannot drift. An unset or unrecognised
`site_shape` is a row.

**The random draw order is untouched.** `site_placements` still draws rot, then
along, then across, in that order, per building. A row mission's placements are
byte-identical and no already-graded candidate re-rolls. Only a brief that sets
`site_shape` to something else moves, which is the same opt-in shape as
`lot_library`.

## The safety gates come along for free

`overlapping()` and `uncovered()` were already 2-D and shape-agnostic -- they
compare axis-aligned rects in x and y and know nothing about rows. Only the
GENERATOR was one-dimensional. `ground_size` is generalised here to bound the
real placement on both axes.

And because a shape that turns can bring non-adjacent buildings together (a
courtyard's ends close on each other), the generator checks every pair against
the worst-case nudge and widens every gap until they clear. `_write_site_spec`
RAISES on `overlapping()`, so a generator that can emit an overlap is a
generator that can stop a build.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

SV = Path("level_factory") / "packages" / "pipeline" / "site_variation.py"
CMD = Path("level_factory") / "apps" / "cli" / "commands" / "__init__.py"
SIDECAR = ".pre_siteshapes"


SV_OLD = '''def row_spacing(footprint: tuple[float, float] | None = None,'''

SV_NEW = '''#: The shapes a site can be laid out in. `row` is the historical line and stays
#: the default for an unset or unrecognised `site_shape`, so a brief that says
#: nothing gets the placement it has always had.
SHAPES = ("row", "L", "courtyard")

#: What a brief may write for each. Case-insensitive; anything else is a row,
#: because refusing a spelling would stop a build over a label.
_SHAPE_ALIASES = {
    "": "row", "row": "row", "street_row": "row", "street": "row",
    "line": "row", "strip": "row",
    "l": "L", "ell": "L", "corner": "L", "l_shape": "L",
    "courtyard": "courtyard", "court": "courtyard", "ring": "courtyard",
    "block": "courtyard", "quad": "courtyard",
}


def shape_of(site_shape) -> str:
    """The layout a brief's ``site_shape`` names. Unknown spellings are rows."""
    return _SHAPE_ALIASES.get(str(site_shape or "").strip().lower(), "row")


def _steps(shape: str, count: int) -> list:
    """Unit steps between consecutive buildings, in site XY.

    A layout is a walk: each building is placed one gap along from the last, in
    a direction this decides. `row` never turns, `L` turns once, `courtyard`
    turns three times and closes. Expressing them this way means the gap
    arithmetic below is written once and every shape gets the same rule.
    """
    n = max(1, int(count)) - 1
    if n <= 0:
        return []
    if shape == "L":
        first = (n + 1) // 2
        return [(1.0, 0.0)] * first + [(0.0, 1.0)] * (n - first)
    if shape == "courtyard":
        # THREE sides, not four. A closed ring walks the last building back
        # onto the first: measured on five shells, b4 landed within a metre of
        # b0, and the pairwise widening below then inflated every gap trying to
        # separate two points that scale together -- ending at a 280 x 292 m
        # plate, wider than the row it exists to shorten.
        #
        # Three sides leave a mouth, and the mouth is the way in. That is what
        # a courtyard is; a sealed one is a building.
        per = [n // 3] * 3
        for i in range(n % 3):
            per[i] += 1
        out = []
        for direction, k in zip(((1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)), per):
            out += [direction] * k
        return out
    return [(1.0, 0.0)] * n


#: Worst case each nudge table can close a gap on its own axis. `_ALONG` moves
#: a building in x and `_ACROSS` moves it in y, and they are different sizes --
#: so the slack a gap needs depends on which way the gap runs. Getting this
#: wrong in the x direction would change every existing row.
def _slack(axis: int) -> float:
    return max(abs(v) for v in (_ALONG if axis == 0 else _ACROSS))


def _pairs_clear(points, reaches) -> bool:
    """Can any two shells touch, for ANY combination of their nudges?

    The separating-axis test `overlapping()` will apply, made worst-case: two
    buildings clear if their gap on either axis survives both of them being
    nudged toward each other. Yaw is already absorbed by `_reach`, which takes
    the longer axis on both.
    """
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            need = reaches[i] + reaches[j]
            dx = abs(points[i][0] - points[j][0]) - 2.0 * _slack(0)
            dy = abs(points[i][1] - points[j][1]) - 2.0 * _slack(1)
            if dx < need and dy < need:
                return False
    return True


def _walk(steps, reaches, street: float, spread: float) -> list:
    points = [(0.0, 0.0)]
    for i, direction in enumerate(steps, start=1):
        axis = 0 if direction[0] else 1
        gap = math.ceil((reaches[i - 1] + reaches[i] + float(street)
                         + 2.0 * _slack(axis)) * spread)
        points.append((points[-1][0] + direction[0] * gap,
                       points[-1][1] + direction[1] * gap))
    return points


def layout_offsets(shape, footprints, *, street: float = STREET) -> list:
    """``(x, y)`` per building for a site laid out as ``shape``, centred on 0.

    ``row`` DELEGATES to :func:`row_offsets` rather than reproducing it. One
    implementation, so the line a thousand existing candidates stand on cannot
    drift away from the line this function draws.

    Every other shape walks the same gap rule step by step, then widens every
    gap uniformly until no two shells can touch under any nudge. Widening
    rather than refusing because `_write_site_spec` RAISES on `overlapping()`:
    a generator that can emit an overlap is a generator that can stop a build,
    and a slightly wider street is not a defect.

    Whole metres, for the reason `site_placements` gives: a spec full of
    x = -67.5 reads as arithmetic having happened to it rather than as a
    placement someone chose.
    """
    reaches = [_reach(f) for f in (footprints or [])]
    if not reaches:
        return []
    shape = shape_of(shape)
    if shape == "row":
        return [(x, 0) for x in row_offsets(footprints, street=street)]

    steps = _steps(shape, len(reaches))
    spread = 1.0
    points = _walk(steps, reaches, street, spread)
    # Bounded, and it converges: every gap grows with `spread`, so the pairwise
    # distances do too. Thirty tries is a 20x street before it gives up, which
    # is past any site anyone has built.
    tries = 0
    while not _pairs_clear(points, reaches) and tries < 30:
        spread += 0.1
        tries += 1
        points = _walk(steps, reaches, street, spread)

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    cx = (min(xs) + max(xs)) / 2.0
    cy = (min(ys) + max(ys)) / 2.0
    return [(int(round(x - cx)), int(round(y - cy))) for x, y in points]


def row_spacing(footprint: tuple[float, float] | None = None,'''


SV_PLACE_OLD = '''def site_placements(seed: int, count: int, *, spacing: int = 45,
                    footprints=None) -> dict:'''

SV_PLACE_NEW = '''def site_placements(seed: int, count: int, *, spacing: int = 45,
                    footprints=None, shape=None) -> dict:'''

SV_OFFSETS_OLD = '''    offsets = row_offsets(footprints) if footprints else None'''

SV_OFFSETS_NEW = '''    offsets = layout_offsets(shape, footprints) if footprints else None'''

SV_BASE_OLD = '''        base = offsets[i] if offsets else (i * spacing - origin)
        buildings.append({"at": [base + along, across], "rot": rot})'''

SV_BASE_NEW = '''        # The nudges stay world-axis-aligned whatever the shape: `_ALONG` in x,
        # `_ACROSS` in y, drawn in that order, per building. Keeping the DRAW
        # ORDER is what makes this opt-in -- a brief that names no shape gets
        # the row it always had, from the same three numbers, and no candidate
        # anyone has already graded re-rolls.
        base = offsets[i] if offsets else (i * spacing - origin, 0)
        buildings.append({"at": [base[0] + along, base[1] + across],
                          "rot": rot})'''

SV_GROUND_OLD = '''def ground_size(count: int, *, spacing: int = 45,
                footprint: tuple[float, float] | None = None,
                footprints=None) -> tuple[int, int]:'''

SV_GROUND_NEW = '''def ground_size(count: int, *, spacing: int = 45,
                footprint: tuple[float, float] | None = None,
                footprints=None, shape=None) -> tuple[int, int]:'''

SV_GROUND_BODY_OLD = '''        offs = row_offsets(footprints)
        reaches = [_reach(f) for f in footprints]
        half_x = max(abs(o) + slack + r for o, r in zip(offs, reaches))
        half_y = max(abs(v) for v in _ACROSS) + max(reaches)'''

SV_GROUND_BODY_NEW = '''        # Bound the placement this module actually makes, on BOTH axes. The row
        # version could take its y from the stagger table alone because every
        # building sat on y = 0; a shape that turns puts them somewhere else,
        # and a plate sized for a row under an L is the defect this module's
        # header is about, wearing the other hat.
        offs = layout_offsets(shape, footprints)
        reaches = [_reach(f) for f in footprints]
        half_x = max(abs(o[0]) + _slack(0) + r for o, r in zip(offs, reaches))
        half_y = max(abs(o[1]) + _slack(1) + r for o, r in zip(offs, reaches))'''


CMD_PLACE_OLD = '''        placed = site_placements(seed, len(lot), footprints=footprints)'''

CMD_PLACE_NEW = '''        placed = site_placements(seed, len(lot), footprints=footprints,
                                 shape=model.site_shape)'''

CMD_GROUND_OLD = '''        span_x, span_y = ground_size(len(lot), footprints=footprints)'''

CMD_GROUND_NEW = '''        span_x, span_y = ground_size(len(lot), footprints=footprints,
                                     shape=model.site_shape)'''


EDITS = {
    SV: ((SV_OLD, SV_NEW),
         (SV_PLACE_OLD, SV_PLACE_NEW),
         (SV_OFFSETS_OLD, SV_OFFSETS_NEW),
         (SV_BASE_OLD, SV_BASE_NEW),
         (SV_GROUND_OLD, SV_GROUND_NEW),
         (SV_GROUND_BODY_OLD, SV_GROUND_BODY_NEW)),
    CMD: ((CMD_PLACE_OLD, CMD_PLACE_NEW),
          (CMD_GROUND_OLD, CMD_GROUND_NEW)),
}

_CRLF = "\r\n"


def _find(body: str, anchor: str) -> tuple[str, int]:
    for candidate in (anchor, anchor.replace("\n", _CRLF)):
        count = body.count(candidate)
        if count:
            return candidate, count
    return anchor, 0


def _apply(path: Path, edits, *, check: bool) -> int:
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR)
    done = sum(1 for _o, new in edits if _find(body, new)[1] == 1)
    if done == len(edits):
        print(f"  already applied  {path.name}")
        return 0
    if done:
        print(f"REFUSING: {path.name} has {done} of {len(edits)} edits present")
        return 1
    out = body
    for old, new in edits:
        anchor, count = _find(out, old)
        if count != 1:
            print(f"REFUSING: {path.name} -- expected 1 occurrence, found "
                  f"{count}: {old.splitlines()[0].strip()!r}")
            return 1
        out = out.replace(
            anchor, new.replace("\n", _CRLF) if _CRLF in anchor else new, 1)
    data = out.encode("utf-8")
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"({len(data) - len(raw):+,})")
        return 0
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha {hashlib.sha256(data).hexdigest()[:12]}")
    return 0


def _verify(root: Path) -> int:
    sys.path.insert(0, str(root / "level_factory"))
    from packages.pipeline import site_variation as sv

    if not hasattr(sv, "layout_offsets"):
        print("[verify] FAIL: layout_offsets is not there -- apply first")
        return 1

    # Five shells about the size Deli Counter ships.
    fps = [(36.4, 28.4), (20.3, 14.3), (38.3, 28.3), (44.0, 30.0), (26.0, 20.0)]
    bad = 0

    # 1. The row is not merely reproduced, it is the same function.
    row = sv.layout_offsets("street_row", fps)
    if [x for x, _y in row] != sv.row_offsets(fps) or any(y for _x, y in row):
        print(f"[verify] FAIL: row layout {row} is not row_offsets "
              f"{sv.row_offsets(fps)}")
        bad = 1
    else:
        print(f"[verify] row delegates to row_offsets: {sv.row_offsets(fps)}")

    # 2. Placements are byte-identical for an unset shape, over many seeds.
    for seed in range(0, 400):
        a = sv.site_placements(seed, len(fps), footprints=fps)
        b = sv.site_placements(seed, len(fps), footprints=fps, shape="")
        c = sv.site_placements(seed, len(fps), footprints=fps,
                               shape="street_row")
        if a != b or a != c:
            print(f"[verify] FAIL: seed {seed} moved when a shape was named")
            bad = 1
            break
    else:
        print("[verify] 400 seeds: an unset or row shape places identically")

    # 3. Every shape, every seed: the two gates the spec writer raises on.
    for shape in sv.SHAPES:
        faults = 0
        for seed in range(0, 250):
            placed = sv.site_placements(seed, len(fps), footprints=fps,
                                        shape=shape)
            gx, gy = sv.ground_size(len(fps), footprints=fps, shape=shape)
            spec = {"buildings": [dict(b, id=f"b{i}")
                                  for i, b in enumerate(placed["buildings"])],
                    "ground": {"size_x": gx, "size_y": gy}}
            faults += len(sv.overlapping(spec, footprints=fps))
            faults += len(sv.uncovered(spec, footprints=fps))
        gx, gy = sv.ground_size(len(fps), footprints=fps, shape=shape)
        print(f"[verify] {shape:<10} 250 seeds  faults {faults:<4} "
              f"plate {gx} x {gy} m")
        if faults:
            print(f"[verify] FAIL: {shape} can place a row its own plate and "
                  f"spacing cannot carry -- _write_site_spec RAISES on this")
            bad = 1

    # 4. The shapes are actually different sites.
    spans = {}
    for shape in sv.SHAPES:
        offs = sv.layout_offsets(shape, fps)
        spans[shape] = (max(x for x, _ in offs) - min(x for x, _ in offs),
                        max(y for _, y in offs) - min(y for _, y in offs))
    print(f"[verify] spans (x, y): "
          + "  ".join(f"{k} {v[0]}x{v[1]}" for k, v in spans.items()))
    if spans["row"][1] != 0:
        print("[verify] FAIL: the row is not flat")
        bad = 1
    for shape in ("L", "courtyard"):
        if spans[shape][1] == 0 or spans[shape][0] >= spans["row"][0]:
            print(f"[verify] FAIL: {shape} is not shorter and taller than the "
                  f"row -- it would not break the lane this exists for")
            bad = 1

    print("[verify] " + ("shapes place, clear their own gates, and differ"
                         if not bad else "FAILED"))
    return bad


def main(argv: list[str]) -> int:
    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} -- run from the factory root")
    if "--verify" in argv:
        return _verify(root)
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
    check = "--check" in argv
    for rel, edits in EDITS.items():
        if _apply(root / rel, edits, check=check):
            return 1
    if not check:
        print()
        print("  Verify:  python patch_lf_site_shapes.py --verify")
        print("           cd level_factory && python -m pytest tests\\unit")
        print("  Then set site_shape on the brief (L / courtyard) and re-run;")
        print("  measure with probe_sightlines --workspace lot-demo-ws.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
