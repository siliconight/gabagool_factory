r"""How long a firing lane does this site's layout leave? Measured off the spec.

    python probe_sightlines.py --selftest
    python probe_sightlines.py --workspace lot-demo-ws
    python probe_sightlines.py --spec <...>\candidate_seed_5017\site.json

## Why this exists

`site_variation` places every candidate as a ROW centred on the origin: X from
`row_offsets`, and the only lateral freedom is `_ACROSS = (-10,-5,0,5,10)`. Its
own comment names the cost and the cure:

    "Across-row stagger. This is the one that changes sightlines: a staggered
     row breaks the single long firing lane a flush row creates."

A LANE is the thing that sentence is about: a straight run of open ground that
nothing stands in. It is a property of the layout and the plate, and it needs
no markers, no engine and no bake to measure. This is the baseline instrument
for changing placement -- run it before, keep the numbers, run it after.

## What it measures

Open ground only: the plate minus every building's footprint. Lines are swept
across the plate at `--angles` directions, and for each line the OPEN RUNS are
computed exactly (interval arithmetic against each footprint, the same slab
clip `sightlines._crossings` uses) rather than sampled, so there is no step
size to tune and no run that falls between two samples.

Reported: the longest lane, how many exceed `--limit`, and their total metres.
The limit defaults to `lasertag_contract.MEASURED.opening_range` -- the range
the crew's bot opens fire at. A lane shorter than that is a fight. A lane
longer than that is being shot at from somewhere you cannot answer.

## What it does NOT measure, and one thing it used to

It does not say whether a level is good. `sightlines.describe` says the same of
itself -- "Advisory: this is a design note, not a gate" -- and this keeps that.

An earlier version measured lines between the spawn / objective / extraction
buildings instead. That was wrong twice, and it is recorded here because the
numbers were plausible. The mission points were placed at building ORIGINS,
which are inside the shells' own collision volumes, so every line began and
ended inside a solid; and on a row the intervening shells blocked every long
pair, so a flush row scored zero open ground. The row's real lane is the street
running ALONGSIDE the buildings, which a centre-to-centre line never touches.
The probe's own selftest caught it. Points came out; lanes went in.

Perimeter walls are ignored: they close the plate rim and cannot stand in a
lane that runs parallel to them.

## The calibration case

`--selftest` asserts three things, in both directions:

    an empty plate            -> one lane the full width of the plate
    a plate under one shell   -> no lane at all
    a flush row vs an L       -> the row's longest lane is strictly longer

A probe that only proves it can find a lane cannot tell you it would not also
find one in solid ground.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

#: Fallback for `lasertag_contract.MEASURED.opening_range`, checked against the
#: real one in `--selftest` rather than trusted.
DEFAULT_LIMIT = 45.0

#: Sweep directions over a half-turn (a lane has no direction). 12 gives 15
#: degree steps and includes both cardinals, which is where streets run.
DEFAULT_ANGLES = 12

#: Perpendicular spacing between swept lines, metres. Two lanes closer together
#: than this are one lane for reporting purposes.
DEFAULT_SPACING = 2.0

_EPS = 1e-9


def _lf_root(start: Path) -> Path | None:
    for base in (start, *start.parents):
        if (base / "level_factory" / "packages").is_dir():
            return base / "level_factory"
        if (base / "packages" / "validation").is_dir():
            return base
    return None


ROOT = _lf_root(Path(__file__).resolve().parent)
if ROOT is None:
    raise SystemExit("cannot find level_factory/packages from this file -- run "
                     "this from the factory root")
sys.path.insert(0, str(ROOT))


def _opening_range() -> float:
    try:
        from packages.validation import lasertag_contract
        return float(lasertag_contract.MEASURED.opening_range)
    except Exception:                                    # pragma: no cover
        return DEFAULT_LIMIT


# ------------------------------------------------------------------ geometry
def shell_extent(glb: Path):
    """(x, z) footprint about the shell's own origin, in metres, or None.

    Same rule as `site_variation.shell_footprint`, which this defers to when it
    is importable: the extent ABOUT THE ORIGIN (twice the furthest face), not
    the collider bounding box, because Lot places a building by its origin and a
    shell modelled off-centre reaches further from `at` than its width.

    None when the geometry cannot be read. A shell that could not be measured is
    not a shell of size zero, and the caller has to tell those apart.
    """
    try:
        from packages.pipeline.site_variation import shell_footprint
    except ImportError:                                  # pragma: no cover
        return None
    return shell_footprint(Path(glb))


def _glb_for(entry: dict) -> Path | None:
    """The shell `.glb` beside the `gameplay` manifest the spec names.

    `gameplay` is ABSOLUTE and documented to stay so ("build inputs, not
    deliverables"), while `glb`/`scene` are site-relative and resolve only
    inside a staged Godot project. So the manifest is the one followable here.
    """
    gp = entry.get("gameplay")
    if not gp:
        return None
    p = Path(str(gp))
    for suffix in (".gameplay.json", ".json"):
        if p.name.endswith(suffix):
            cand = p.with_name(p.name[: -len(suffix)] + ".glb")
            if cand.is_file():
                return cand
    return None


def footprint_rects(spec: dict) -> tuple[list, list[str]]:
    """One axis-aligned rect per building, and what had to be substituted.

    Yaw is cardinal, so a quarter turn swaps the two horizontal extents and the
    rect stays axis-aligned -- exact, not the pessimistic longer-axis-on-both
    that `site_variation.overlapping` uses. A probe that is deliberately
    pessimistic reports fewer lanes than the site has and flatters every layout
    equally.
    """
    notes: list[str] = []
    rects = []
    for entry in spec.get("buildings") or []:
        bid = str(entry.get("id", "?"))
        at = entry.get("at") or [0.0, 0.0]
        x, y = float(at[0]), float(at[1])
        rot = int(entry.get("rot", 0) or 0) % 360

        glb = _glb_for(entry)
        fp = shell_extent(glb) if glb else None
        if fp is None:
            from packages.pipeline.site_variation import DEFAULT_FOOTPRINT
            fp = DEFAULT_FOOTPRINT
            notes.append(
                f"{bid}: geometry not measured "
                f"({glb or entry.get('gameplay') or 'no gameplay path'}) -- "
                f"assumed {fp[0]:g} x {fp[1]:g} m")
        fx, fy = float(fp[0]), float(fp[1])
        if rot in (90, 270):
            fx, fy = fy, fx
        rects.append((bid, (x - fx / 2.0, y - fy / 2.0,
                            x + fx / 2.0, y + fy / 2.0)))
    return rects, notes


def _slab(p0, d, rect):
    """The ``t`` interval of the infinite line ``p0 + t*d`` inside ``rect``.

    None when the line misses. The slab method, which is what
    ``sightlines._crossings`` does for a segment -- restated here for an
    unbounded line rather than imported, because clipping to the segment is
    exactly the part that does not apply.
    """
    x0, y0, x1, y1 = rect
    lo, hi = -math.inf, math.inf
    for p, dd, a, b in ((p0[0], d[0], x0, x1), (p0[1], d[1], y0, y1)):
        if abs(dd) < _EPS:
            if p < a or p > b:
                return None
            continue
        t_a, t_b = (a - p) / dd, (b - p) / dd
        if t_a > t_b:
            t_a, t_b = t_b, t_a
        lo, hi = max(lo, t_a), min(hi, t_b)
        if lo > hi:
            return None
    return (lo, hi)


def _open_runs(p0, d, plate, blockers) -> list[tuple[float, float]]:
    """The clear ``t`` intervals of one line across the plate.

    Intervals rather than lengths, because a lane nobody can locate is a number
    rather than a place -- the caller turns ``t`` back into a midpoint so the
    longest one can be looked at.
    """
    span = _slab(p0, d, plate)
    if span is None:
        return []
    t0, t1 = span
    if t1 - t0 <= _EPS:
        return []
    blocked = []
    for rect in blockers:
        hit = _slab(p0, d, rect)
        if hit is None:
            continue
        a, b = max(hit[0], t0), min(hit[1], t1)
        if b - a > _EPS:
            blocked.append((a, b))
    blocked.sort()
    runs = []
    cursor = t0
    for a, b in blocked:
        if a > cursor + _EPS:
            runs.append((cursor, a))
        cursor = max(cursor, b)
    if t1 > cursor + _EPS:
        runs.append((cursor, t1))
    return runs


def lanes(spec: dict, *, angles: int, spacing: float):
    """Every clear run across the site's open ground, longest first.

    Returns ``[(length, angle_deg, (mid_x, mid_y)), ...]`` so the longest lane
    can be looked at rather than only counted.
    """
    rects, notes = footprint_rects(spec)
    ground = spec.get("ground") or {}
    try:
        hx = float(ground["size_x"]) / 2.0
        hy = float(ground["size_y"]) / 2.0
    except (KeyError, TypeError, ValueError):
        return [], notes + ["the spec declares no readable ground size -- "
                            "there is no plate to sweep"]
    plate = (-hx, -hy, hx, hy)
    blockers = [r for _bid, r in rects]
    reach = math.hypot(hx, hy)

    out = []
    for i in range(max(1, int(angles))):
        theta = math.pi * i / max(1, int(angles))
        d = (math.cos(theta), math.sin(theta))
        n = (-d[1], d[0])
        steps = int(math.ceil(2.0 * reach / max(0.1, spacing)))
        for k in range(steps + 1):
            off = -reach + k * spacing
            p0 = (n[0] * off, n[1] * off)
            for a, b in _open_runs(p0, d, plate, blockers):
                mid = (a + b) / 2.0
                out.append((b - a, math.degrees(theta),
                            (p0[0] + d[0] * mid, p0[1] + d[1] * mid)))
    out.sort(key=lambda r: -r[0])
    return out, notes


# -------------------------------------------------------------------- report
def measure(spec: dict, *, limit: float, angles: int, spacing: float) -> dict:
    found, notes = lanes(spec, angles=angles, spacing=spacing)
    over = [r for r in found if r[0] > limit]
    return {
        "buildings": len(spec.get("buildings") or []),
        "shape": spec.get("site_shape") or "(unset)",
        "seed": spec.get("candidate_seed"),
        "paths": len(spec.get("paths") or []),
        "longest": round(found[0][0], 1) if found else 0.0,
        "longest_at": found[0][1:] if found else None,
        "over": len(over),
        "over_metres": round(sum(r[0] for r in over), 1),
        "top": found[:5],
        "notes": notes,
    }


def report(label: str, m: dict, *, limit: float) -> None:
    print(f"  {label}")
    print(f"    buildings {m['buildings']}   paths {m['paths']}   "
          f"site_shape {m['shape']}   seed {m['seed']}")
    for note in m["notes"]:
        print(f"    NOTE  {note}")
    if not m["top"]:
        print("    no open ground measured")
        return
    for length, angle, (mx, my) in m["top"]:
        print(f"    {length:8.1f} m   at {angle:5.1f} deg   "
              f"through ({mx:7.1f}, {my:7.1f})")
    print(f"    longest {m['longest']:g} m   lanes over {limit:g} m: "
          f"{m['over']}   totalling {m['over_metres']:g} m")
    # LONGEST is the comparable number. The count and the total scale with how
    # much plate there is, and `ground_size` sizes the plate from the placement
    # -- so a layout that spreads out reports more lane metres for having more
    # ground, not for being more exposed. Within one mission the plate is fixed
    # (bounded over every seed, so candidates stay comparable) and all three
    # numbers can be read against each other; across shapes, only `longest`.


# ------------------------------------------------------------------ selftest
def _synthetic(offsets, *, size=(48.0, 48.0), pad=8.0) -> dict:
    fx, fy = size
    buildings = [{"id": f"b{i}", "at": [float(x), float(y)], "rot": 0}
                 for i, (x, y) in enumerate(offsets)]
    hx = (max(abs(x) for x, _ in offsets) if offsets else 0.0) + fx / 2 + pad
    hy = (max(abs(y) for _, y in offsets) if offsets else 0.0) + fy / 2 + pad
    return {"buildings": buildings,
            "ground": {"size_x": 2 * hx, "size_y": 2 * hy},
            "site_shape": "(synthetic)", "candidate_seed": 0, "paths": []}


def _selftest(limit: float, angles: int, spacing: float) -> int:
    print(f"[selftest] limit {limit:g} m "
          f"(lasertag opening range {_opening_range():g} m), "
          f"{angles} directions, {spacing:g} m spacing\n")

    # A 40 m plate under a 48 m shell: the footprint covers the whole plate, so
    # there is nowhere a lane can be. The earlier version of this case put the
    # shell on a LARGER plate and asserted a short lane, which was wrong -- a
    # 26 m rim still carries a line the full length of the plate, and the probe
    # was right to print 103.5 m. Cover the plate and the answer is unarguable.
    buried = {"buildings": [{"id": "b0", "at": [0, 0], "rot": 0}],
              "ground": {"size_x": 40.0, "size_y": 40.0},
              "site_shape": "(buried)", "candidate_seed": 0}
    # Same corridor with and without one shell across it. A -> B, so nothing
    # about plate size or sweep density can explain the difference away.
    corridor = {"ground": {"size_x": 200.0, "size_y": 40.0},
                "site_shape": "(corridor)", "candidate_seed": 0}
    corridor_open = dict(corridor, buildings=[])
    corridor_blocked = dict(
        corridor, buildings=[{"id": "b0", "at": [0, 0], "rot": 0}])
    row = _synthetic([(-120, 0), (-60, 0), (0, 0), (60, 0), (120, 0)])
    ell = _synthetic([(-60, -60), (-60, 0), (-60, 60), (0, 60), (60, 60)])

    def m(spec):
        return measure(spec, limit=limit, angles=angles, spacing=spacing)

    m_buried, m_open = m(buried), m(corridor_open)
    m_blocked, m_row, m_ell = m(corridor_blocked), m(row), m(ell)

    report("buried       (40 m plate under a 48 m shell -- no open ground)",
           m_buried, limit=limit)
    print()
    report("corridor     (200 x 40 m, nothing on it)", m_open, limit=limit)
    print()
    report("corridor + 1 (the same plate, one 48 m shell across it)",
           m_blocked, limit=limit)
    print()
    report("flush row    (five shells, one axis)", m_row, limit=limit)
    print()
    report("L layout     (same five shells, two axes)", m_ell, limit=limit)
    print()

    bad = 0
    if m_open["longest"] < 199.0:
        print(f"[selftest] FAIL: an empty 200 m corridor reads "
              f"{m_open['longest']:g} m. The sweep is not finding open ground "
              f"that is unambiguously there, so every number is a floor of "
              f"unknown depth.")
        bad = 1
    if m_buried["longest"] > _EPS:
        print(f"[selftest] FAIL: a plate entirely under a shell reads "
              f"{m_buried['longest']:g} m of lane. The sweep is not seeing the "
              f"footprint at all, which is the expensive direction -- it would "
              f"report every layout as wide open.")
        bad = 1
    if m_blocked["longest"] >= m_open["longest"]:
        print(f"[selftest] FAIL: one shell laid across the corridor changed "
              f"the longest lane from {m_open['longest']:g} m to "
              f"{m_blocked['longest']:g} m. A building that does not shorten "
              f"the lane it stands in is not being measured.")
        bad = 1
    if m_row["longest"] <= m_ell["longest"]:
        print(f"[selftest] FAIL: the row reads {m_row['longest']:g} m and the "
              f"L reads {m_ell['longest']:g} m. The probe does not respond to "
              f"the property this work exists to change, so it cannot measure "
              f"whether the change helped.")
        bad = 1
    if not bad:
        print(f"[selftest] buried {m_buried['longest']:g} m, corridor "
              f"{m_open['longest']:g} -> {m_blocked['longest']:g} m with a "
              f"shell in it, row {m_row['longest']:g} m vs L "
              f"{m_ell['longest']:g} m -- finds the lane that is there, not "
              f"the one that is not, and responds to layout")
    return bad


# ---------------------------------------------------------------------- main
def _find_specs(ws: Path, mission: str | None) -> list[Path]:
    """`_write_site_spec` writes
    `<ws>/.level_factory/temp/<mission>/candidate_seed_<n>/[themed/]site.json`."""
    temp = ws / ".level_factory" / "temp"
    if not temp.is_dir():
        return []
    root = (temp / mission) if mission else temp
    return sorted(p for p in root.rglob("site.json") if p.is_file())


def _flag(argv, name, cast, default):
    return cast(argv[argv.index(name) + 1]) if name in argv else default


def main(argv: list[str]) -> int:
    limit = _flag(argv, "--limit", float, _opening_range())
    angles = _flag(argv, "--angles", int, DEFAULT_ANGLES)
    spacing = _flag(argv, "--spacing", float, DEFAULT_SPACING)

    if "--selftest" in argv:
        return _selftest(limit, angles, spacing)

    if "--spec" in argv:
        specs = [Path(argv[argv.index("--spec") + 1])]
    elif "--workspace" in argv:
        ws = Path(argv[argv.index("--workspace") + 1])
        mission = _flag(argv, "--mission", str, None)
        specs = _find_specs(ws, mission)
        if not specs:
            print(f"no candidate specs under {ws / '.level_factory' / 'temp'}"
                  + (f" for mission {mission}" if mission else "")
                  + " -- plan a run first")
            return 2
    else:
        for line in __doc__.splitlines()[2:5]:
            print(line.strip())
        return 2

    print(f"\n  limit {limit:g} m (lasertag opening range), {angles} "
          f"directions, {spacing:g} m spacing\n")
    totals = []
    for spec_path in specs:
        if not spec_path.is_file():
            print(f"  not a file: {spec_path}")
            return 2
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        m = measure(spec, limit=limit, angles=angles, spacing=spacing)
        report(f"{spec_path.parent.name}  ({spec_path})", m, limit=limit)
        print()
        totals.append((str(spec_path.parent), m))

    if len(totals) > 1:
        print("  across candidates")
        for name, m in totals:
            print(f"    {Path(name).name:<24} {m['buildings']:>2} bldg   "
                  f"longest {m['longest']:>7.1f} m   over-limit {m['over']:>4}"
                  f"   {m['over_metres']:>9.1f} m")
        comparable = [m for _n, m in totals if m["buildings"] > 1]
        if comparable and len({m["longest"] for m in comparable}) == 1:
            print("    every multi-building candidate reports the SAME longest "
                  "lane -- either the placements are not varying, or this "
                  "measurement cannot see the way they vary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
