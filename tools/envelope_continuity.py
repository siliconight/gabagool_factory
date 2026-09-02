r"""Does the exterior envelope close -- along each run, and around each corner?

    python envelope_continuity.py <id>.slots.json ...        # the request
    python envelope_continuity.py --dir deli_counter/build   # the whole library
    python envelope_continuity.py --scene <preview>/lot/<id> --slots <id>.slots.json
    python envelope_continuity.py --selftest                 # prove the ruler

Read-only. Pure standard library. No Blender, no Godot, no rebuild.

## What this exists to measure

Roadmap item 58: a facade corner walked as visibly OPEN on `lot_demo_001`, and
no automated check had ever mentioned it. Item 57 classes a gap between pieces
as Critical -- it exposes modular construction instantly -- and asks for "an
envelope-continuity check over adjacent exterior wall slots' themed extents, so
an open corner fails a build instead of waiting for a walker with a
screenshot". This is that check.

Measured 2026-08-24 across the five buildings of `lot_demo_001`: every
exterior run is contiguous, and every run terminates EXACTLY on the
perpendicular wall's CENTRELINE -- 0.000 m past it, one distinct value over 40
corners -- leaving a re-entrant notch of half the wall thickness on each side,
full storey height, at every outside corner. `wallEnd` fills straight-run
remainders; nothing in the vocabulary turns.

So the two findings are deliberately separate. A run gap and a corner notch
look alike from a screenshot and have nothing else in common: one is a
remainder that was not filled, the other is a corner that was never anybody's
job.

## THE RULER, which is the part to read before trusting a number here

A dimension stored BY AXIS was twice read BY ROLE while this was being
written, and each time it printed a confident, wrong answer.

1. The filename token `_w<cm>` is the module's own X extent. On an N/S run
   that is the run width (`wall_rockay_03_w200`, 2.00 m). On an E/W run the
   SAME token is the THICKNESS (`wall_rockay_01_w30`, 0.30 m) and the 2.00 m
   length lives on Z, where no filename records it at all.
2. `fit.dims` is `[x, y, z]` in whichever frame the slot was written in, and
   the manifest does not say which. Wall segments are in BUILDING space, so
   the run extent is `dims[0]` on N/S and `dims[1]` on E/W. Openings are in
   CANONICAL-X space, so it is `dims[0]` on both. Zoo's `plan_kit` documents
   the field as `[w, d, h]` and reads it positionally, which is the openings'
   convention; the segments depart from it and get away with it because they
   are also placed unrotated.

Either mistake prints a comb of gaps of exactly `pitch - thickness` on every
E/W run and nothing on N/S. The first pass over `lot_demo_001` reported 222
gaps and every one of them was 1.700 m or half of it -- 2.000 minus 0.300.
That signature is the tell: ONE value, repeated, equal to the pitch minus the
thickness, on one pair of walls only.

**So this file never parses a module stem, and never indexes `fit.dims` by a
fixed position.** The run axis comes from the slot's `facing`, and both the
width and the thickness are then read off that axis. A gate that parsed
filenames would pass the real corner and fail 222 sound joints.

## What it reads, and what that licenses it to say

`<id>.slots.json` is the REQUEST -- what Deli Counter asked the kit for. That
is the right artefact for this question, because item 58's defect is authored
there: the slot spans already stop at the centreline, so the composed scene is
faithful and the corner is missing upstream of Zoo. It is also available
before any geometry exists, which is the whole point of a gate.

It is NOT the built geometry, and this file does not claim to have measured
any. `--scene` adds that half by joining the composed `site.tscn` on
`slot_id == node name` and reporting where placement disagrees with the slot
it was placed into -- placement from the scene, dimensions from the slot,
neither from a filename.

## What it does NOT decide

Whether a corner notch is a defect. It is a measurement: the run reaches this
far past the perpendicular centreline, and that leaves this much uncovered.
Whether the envelope should close with a corner species, with a lapped run, or
not at all is a decision for the reply and for the owning repo -- per
`USING_THE_FACTORY.md` the slot layout is `deli_counter`'s and a new module
family is `zoo`'s, which makes it the gap protocol rather than a patch.

## Refusing rather than passing

A slots file whose shape is not recognised is reported and skipped, never
counted as clean. That is roadmap item 62's convention and this repo's own
scar: a `--verify` once read `export_closure_scan.json` for keys it does not
have, turned the absence into an empty problem list with `or []`, and printed
"closure verdict clean" three lines under `EXPORT_CLOSURE_BROKEN: 21
unresolved`. A checker that cannot find the field it wants has learned
nothing and must say so.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TOL = 1e-6                      # geometry here is authored on exact 0.05 m steps

# Pinned, not assumed. Both are uniform across all 137 manifests in
# `deli_counter/build` as of 2026-08-24, and both decide how every number
# below is read: the version fixes the field names, the space fixes which two
# of the three axes are the plan. If either moves, this file has to be re-read
# against the new shape rather than quietly keep measuring against the old one.
KNOWN_VERSIONS = ("1.2.0",)
KNOWN_SPACE = "spec/Blender Z-up raw coords; rot_y = degrees about up"
SIDES = ("N", "S", "E", "W")
_WALL = re.compile(r"^ext_(-?\d+)_([NSEW])$")

#: WHAT BLOCKS A BUILD, and the rule for changing it.
#:
#: A code graduates WARN -> FAIL when the shipped library reads ZERO for it,
#: never before -- the path `layout_lint`'s L18 took (Deli Counter 0.101.0
#: WARN, 0.101.2 FAIL, on the day the library lint came back clean). A gate
#: switched on over a red library is a gate everyone learns to pass with a
#: flag.
#:
#: Measured on the rebuilt library, 2026-08-25, 124 buildings:
#:     ENV_CORNER_OPEN            0   -> FAIL (graduated; was 988 on 2026-08-24)
#:     ENV_PLACEMENT_DRIFT        0   -> FAIL
#:     ENV_SHAPE_UNRECOGNISED     0   -> FAIL
#:     ENV_RUN_GAP                1   -> WARN (auto_shop_a02, pre-existing)
#:     ENV_DIMS_FRAME_CANONICAL 349   -> WARN (roadmap item 63)
#:
#: `--strict` promotes every WARN to FAIL, which is how you measure what a
#: graduation would cost before committing to it.
SEVERITY = {
    "ENV_CORNER_OPEN": "FAIL",
    "ENV_PLACEMENT_DRIFT": "FAIL",
    "ENV_SHAPE_UNRECOGNISED": "FAIL",
    "ENV_RUN_GAP": "WARN",
    "ENV_DIMS_FRAME_CANONICAL": "WARN",
}

RUN_GAP = "ENV_RUN_GAP"
CORNER_OPEN = "ENV_CORNER_OPEN"
DRIFT = "ENV_PLACEMENT_DRIFT"
DIMS_FRAME = "ENV_DIMS_FRAME_CANONICAL"
UNREADABLE = "ENV_SHAPE_UNRECOGNISED"


class NotABuilding(Exception):
    """A well-formed manifest that simply has no exterior envelope."""


# ------------------------------------------------------------------ the ruler
def run_axis(facing: str) -> int:
    """Index into a slot translation/dims of the axis a run travels along.

    N and S walls run along x; E and W walls run along y. This is the ONLY
    place the mapping lives, and every width, thickness and centreline below
    is taken through it -- see THE RULER in the module docstring for the two
    readings that got this wrong by assuming a fixed position instead.
    """
    if facing in ("N", "S"):
        return 0
    if facing in ("E", "W"):
        return 1
    raise ValueError(f"unknown facing {facing!r}")


def _span(slot: dict, thickness: float | None = None):
    """(axis, lo, hi, perpendicular offset, thickness, swapped) for one slot.

    TWO FRAMES LIVE IN ONE MANIFEST, and nothing in a slot says which it is
    in. Measured 2026-08-24 over 281 E/W exterior slots in five buildings:
    266 carry dims in BUILDING space (thickness on x, run extent on y) and 15
    carry them CANONICAL-X (run extent on x, the frame a module is authored
    in before `rot_y` brings it onto its wall). The split is exact: wall
    SEGMENTS are building-space, OPENINGS are canonical-X.

    NEITHER IS WRONG, and the first reading of this file said openings were
    "transposed", which was a defect report about a convention. Both produce
    correct geometry because composition rotates them differently -- measured
    on the same five buildings, 698 exterior modules: `rot_y` is honoured for
    8 of them (E-wall openings, 90 deg) and ignored for the other 690, and
    each combination lands the module correctly in world space. `deli_counter
    ._slot_orient` states the openings' half outright -- "brings a
    canonically-authored module (along X) onto this wall" -- and the segment
    writer `_record_wall_slot` simply passes the box size straight through,
    already in building space.

    What IS a defect is that a reader cannot tell them apart from the slot.
    So the frame is decided per slot against the run's own thickness rather
    than assumed: whichever axis carries the thickness is the perpendicular
    one, and the other is the run. `thickness` comes from the run's segments,
    which is why `load_slots` reads a run twice. See roadmap item 63.
    """
    ax = run_axis(slot["facing"])
    t = slot["transform"]["translation"]
    dims = slot["fit"]["dims"]
    swapped = False
    if thickness is not None and abs(dims[1 - ax] - thickness) > TOL:
        if abs(dims[ax] - thickness) <= TOL:
            ax_dims, swapped = 1 - ax, True
        else:
            raise ValueError(
                f'{slot["slot_id"]}: neither dims axis is the run thickness '
                f'{thickness} (dims {dims[0]}, {dims[1]})')
    else:
        ax_dims = ax
    c, w = t[ax], dims[ax_dims]
    return ax, c - w / 2.0, c + w / 2.0, t[1 - ax], dims[1 - ax_dims], swapped


# ------------------------------------------------------------------- readers
def load_slots(path: Path) -> dict:
    """Every exterior wall slot, grouped (storey, facing). Raises on a shape
    this file does not recognise, rather than returning an empty result that
    would read as a clean building."""
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or "slots" not in doc:
        raise ValueError("no `slots` key -- not a slot manifest")
    ver = doc.get("slot_manifest_version")
    if ver not in KNOWN_VERSIONS:
        raise ValueError(f"slot_manifest_version {ver!r} is not one of "
                         f"{KNOWN_VERSIONS} -- re-read the schema before trusting "
                         f"any measurement from it")
    if doc.get("space") != KNOWN_SPACE:
        raise ValueError(f"space {doc.get('space')!r} is not the frame this "
                         f"file measures in ({KNOWN_SPACE!r})")
    runs: dict[tuple[str, str], dict] = {}
    for s in doc["slots"]:
        wall = s.get("wall") or ""
        m = _WALL.match(wall)
        if not m:
            continue                     # interior partitions and everything else
        for key in ("slot_id", "facing", "transform", "fit"):
            if key not in s:
                raise ValueError(f"slot in {wall} has no `{key}`")
        if "dims" not in s["fit"] or len(s["fit"]["dims"]) != 3:
            raise ValueError(f'{s["slot_id"]}: fit.dims is not three numbers')
        runs.setdefault((m.group(1), m.group(2)), []).append(s)
    if not runs:
        # NOT a failure to check, and the difference matters at the top level.
        # 13 of the 137 manifests carry 1-5 slots and no `wall` field at all --
        # mission and site stubs, not buildings. Folding them into "could not
        # check" would make `check_all.py` report NOT CHECKED forever, and a
        # permanent amber is one nobody reads. A manifest this cannot MEASURE
        # (bad version, unknown frame, malformed slot) still raises.
        raise NotABuilding("no `ext_<storey>_<side>` wall slots -- not a building")
    return {k: _measure(v) for k, v in runs.items()}


def _measure(slots: list[dict]) -> dict:
    """One run, measured twice: the segments fix the thickness, then every
    slot is resolved against it. A run whose segments do not agree on one
    thickness is refused rather than guessed at."""
    ax = run_axis(slots[0]["facing"])
    segs_only = [s for s in slots if "_open" not in s["slot_id"]] or slots
    th_counts: dict[float, int] = {}
    for s in segs_only:
        t = round(s["fit"]["dims"][1 - ax], 6)
        th_counts[t] = th_counts.get(t, 0) + 1
    ranked = sorted(th_counts.items(), key=lambda kv: -kv[1])
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        raise ValueError(f'{slots[0]["wall"]}: segments disagree on thickness '
                         f'{sorted(th_counts)}')
    thickness = ranked[0][0]
    out = {"axis": ax, "segs": [], "perp": set(), "th": set(), "swapped": []}
    for s in slots:
        _, lo, hi, perp, th, swapped = _span(s, thickness)
        out["segs"].append((lo, hi, s["slot_id"]))
        out["perp"].add(round(perp, 6))
        out["th"].add(round(th, 6))
        if swapped:
            out["swapped"].append((s["slot_id"], tuple(s["fit"]["dims"][:2])))
    return out


def load_scene(scene: Path) -> dict:
    """`node name -> origin` for every instanced node in a composed building
    scene. Node names are slot ids, which is the join key; dimensions are NOT
    taken from here, because the only dimension a scene carries is in a
    filename and the filename is the trap."""
    txt = scene.read_text(encoding="utf-8", errors="replace")
    out, cur = {}, None
    for line in txt.splitlines():
        if line.startswith("[node "):
            nm = re.search(r'name="([^"]+)"', line)
            cur = nm.group(1) if nm else None
        elif cur and line.startswith("transform = Transform3D("):
            nums = [float(v) for v in line[len("transform = Transform3D("):-1].split(",")]
            if len(nums) == 12:
                out[cur] = (nums[9], nums[10], nums[11])
            cur = None
    if not out:
        raise ValueError(f"{scene}: no node transforms found")
    return out


# ------------------------------------------------------------------ findings
def check(runs: dict, scene: dict | None = None) -> list[dict]:
    out = []
    for (storey, side), r in sorted(runs.items()):
        for sid, dims in r.get("swapped", []):
            out.append(dict(code=DIMS_FRAME, storey=storey, side=side, a=sid,
                            note=f"fit.dims {dims} is canonical-X (width on x) "
                                 f"while this run's segments are building-space; "
                                 f"the run extent was read off the thickness"))
        segs = sorted(r["segs"])
        for a, b in zip(segs, segs[1:]):
            if b[0] - a[1] > TOL:
                out.append(dict(code=RUN_GAP, storey=storey, side=side,
                                size=round(b[0] - a[1], 4), a=a[2], b=b[2]))
    for storey in sorted({k[0] for k in runs}):
        have = {k[1]: v for k, v in runs.items() if k[0] == storey}
        if set(have) != set(SIDES):
            out.append(dict(code=UNREADABLE, storey=storey, side="-",
                            note=f"storey has runs {sorted(have)}, not N/S/E/W;"
                                 f" the corner test does not apply"))
            continue
        for run_side, perp_side in (("N", "W"), ("N", "E"), ("S", "W"), ("S", "E")):
            run, perp = have[run_side], have[perp_side]
            if len(perp["perp"]) != 1 or len(perp["th"]) != 1:
                out.append(dict(code=UNREADABLE, storey=storey, side=perp_side,
                                note="run is not a single straight line"))
                continue
            centre = next(iter(perp["perp"]))
            half = next(iter(perp["th"])) / 2.0
            segs = sorted(run["segs"])
            end = segs[0][0] if centre < 0 else segs[-1][1]
            reach = abs(end) - abs(centre)      # + means it passes the centreline
            if half - reach > TOL:
                out.append(dict(code=CORNER_OPEN, storey=storey,
                                side=run_side + perp_side,
                                size=round(half - reach, 4),
                                note=f"{run_side} run ends {end:+.3f}, {perp_side}"
                                     f" wall centreline {centre:+.3f},"
                                     f" reaches {reach:+.3f} past it"))
    if scene is not None:
        for (storey, side), r in sorted(runs.items()):
            ax = r["axis"]
            for lo, hi, sid in sorted(r["segs"]):
                if sid not in scene:
                    continue
                # slot space is (x, y, z-up); scene space is (x, y-up, z) with
                # the plan axis negated -- so only the RUN axis is compared,
                # which is the one this gate is about.
                placed = scene[sid][0 if ax == 0 else 2]
                want = (lo + hi) / 2.0
                if abs(abs(placed) - abs(want)) > 1e-3:
                    out.append(dict(code=DRIFT, storey=storey, side=side,
                                    size=round(abs(placed) - abs(want), 4), a=sid,
                                    note=f"slot centre {want:+.3f}, placed {placed:+.3f}"))
    return out


# ------------------------------------------------------------------ selftest
def selftest() -> int:
    """Two buildings built by hand: one that closes, one that does not.

    The closing one is the case a name-parsing ruler gets WRONG -- its E/W
    modules are 2.00 m along the run and 0.30 m thick, the exact shape that
    produced 222 phantom 1.700 m gaps. A gate that passes only the broken
    building has not been tested.
    """
    def wall(sid, facing, c, perp, w, th, storey="0"):
        ax = run_axis(facing)
        t = [0.0, 0.0, 1.75]; t[ax] = c; t[1 - ax] = perp
        d = [0.0, 0.0, 3.5]; d[ax] = w; d[1 - ax] = th
        return dict(slot_id=sid, wall=f"ext_{storey}_{facing}", facing=facing,
                    transform=dict(translation=t, rot_y=0, scale=[1, 1, 1]),
                    fit=dict(dims=d))

    def building(reach):
        """Runs 10 m each way; `reach` is how far past the perpendicular
        centreline each run is extended."""
        slots = []
        for facing, perp in (("N", 5.0), ("S", -5.0)):
            for k in range(-5, 5):
                slots.append(wall(f"ext_0_{facing}_seg{k+5}", facing, k + 0.5, perp, 1.0, 0.3))
            slots.append(wall(f"ext_0_{facing}_end0", facing, -5.0 - reach / 2, perp, reach, 0.3))
            slots.append(wall(f"ext_0_{facing}_end1", facing, 5.0 + reach / 2, perp, reach, 0.3))
        for facing, perp in (("E", 5.0), ("W", -5.0)):
            for k in range(-5, 5):
                slots.append(wall(f"ext_0_{facing}_seg{k+5}", facing, k + 0.5, perp, 1.0, 0.3))
        return [s for s in slots if s["fit"]["dims"][run_axis(s["facing"])] > 0]

    fails = []
    # 1. corners left on the centreline -- item 58's shape
    f = check(_group(building(0.0)))
    corners = [x for x in f if x["code"] == CORNER_OPEN]
    if len(corners) != 4 or {c["size"] for c in corners} != {0.15}:
        fails.append(f"open corners: got {[(c['side'], c.get('size')) for c in corners]}")
    if any(x["code"] == RUN_GAP for x in f):
        fails.append("a closed run reported a gap -- the ruler is reading by role")
    # 2. corners lapped to the perpendicular outer face
    f = check(_group(building(0.3)))
    if [x for x in f if x["code"] in (CORNER_OPEN, RUN_GAP)]:
        fails.append(f"a lapped envelope reported findings: {f}")
    # 3. a real gap is found
    b = building(0.3)
    b = [s for s in b if s["slot_id"] != "ext_0_N_seg3"]
    gaps = [x for x in check(_group(b)) if x["code"] == RUN_GAP]
    if len(gaps) != 1 or abs(gaps[0]["size"] - 1.0) > 1e-9:
        fails.append(f"a 1.0 m hole read as {gaps}")
    # 4. an unrecognised shape refuses
    try:
        load_slots(_tmp_json({"slots": [{"wall": "ext_0_N", "slot_id": "x"}]}))
    except ValueError:
        pass
    else:
        fails.append("a slot with no transform/fit was accepted")
    for line in fails:
        print("  " + line)
    if fails:
        print(f"  selftest FAILED: {len(fails)} case(s)")
        return 1
    print("  selftest ok: 4 cases -- open corner, lapped corner, real gap, bad shape")
    return 0


def _group(slots: list[dict]) -> dict:
    runs: dict[tuple[str, str], list] = {}
    for s in slots:
        m = _WALL.match(s["wall"])
        runs.setdefault((m.group(1), m.group(2)), []).append(s)
    return {k: _measure(v) for k, v in runs.items()}


def _tmp_json(doc) -> Path:
    import tempfile
    p = Path(tempfile.mkstemp(suffix=".json")[1])
    p.write_text(json.dumps(doc), encoding="utf-8")
    return p


# ----------------------------------------------------------------------- CLI
def main(argv: list[str]) -> int:
    """Three states, per `check_all.py`'s contract:

        0   checked, nothing that blocks
        1   checked, found something that blocks
        2   COULD NOT check

    The third is the one that matters. A manifest whose shape this does not
    recognise is exit 2, never a quiet 0 -- this repo has already paid for a
    `--verify` that read a file for keys it does not have, turned the absence
    into an empty problem list, and printed "closure verdict clean" three
    lines under `EXPORT_CLOSURE_BROKEN: 21 unresolved`.
    """
    if "--selftest" in argv:
        return selftest()
    strict = "--strict" in argv
    show_all = "--all" in argv
    scene_dir = None
    if "--scene" in argv:
        i = argv.index("--scene")
        scene_dir = Path(argv[i + 1]); del argv[i:i + 2]
    if "--slots" in argv:
        argv.remove("--slots")
    paths: list[Path] = []
    if "--dir" in argv:
        i = argv.index("--dir")
        d = Path(argv[i + 1]); del argv[i:i + 2]
        if not d.is_dir():
            print(f"  cannot check: {d} is not a directory")
            return 2
        paths = sorted(d.glob("*.slots.json"))
        if not paths:
            print(f"  cannot check: no *.slots.json under {d}")
            return 2
    paths += [Path(a) for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__.strip().splitlines()[0])
        print("  give one or more <id>.slots.json, or --dir <build dir>")
        return 2

    def sev(code):
        base = SEVERITY.get(code, "FAIL")
        return "FAIL" if (strict and base == "WARN") else base

    tot = {c: 0 for c in SEVERITY}
    unreadable, not_buildings, seen, clean = [], [], 0, 0
    for p in paths:
        try:
            runs = load_slots(p)
        except NotABuilding as exc:
            not_buildings.append((p.name, str(exc)))
            continue
        except (ValueError, json.JSONDecodeError, OSError) as exc:
            unreadable.append((p.name, str(exc)))
            continue
        seen += 1
        scene = None
        if scene_dir is not None:
            sc = scene_dir / p.name.replace(".slots.json", "") / "site.tscn"
            sc = sc if sc.is_file() else scene_dir / "site.tscn"
            if sc.is_file():
                scene = load_scene(sc)
        found = check(runs, scene)
        for f in found:
            tot[f["code"]] = tot.get(f["code"], 0) + 1
        blocking = [f for f in found if sev(f["code"]) == "FAIL"]
        if not blocking:
            clean += 1
        shown = found if show_all else blocking
        if not shown:
            continue
        print(f"{p.name}")
        for f in shown:
            head = f"  {sev(f['code']):<4} {f['code']:<24} storey {f['storey']:>2} {f['side']:<3}"
            if f["code"] == RUN_GAP:
                print(f"{head} {f['size']:.3f} m  {f['a']} -> {f['b']}")
            elif f["code"] == CORNER_OPEN:
                print(f"{head} {f['size']:.3f} m uncovered   {f['note']}")
            elif f["code"] in (DIMS_FRAME, DRIFT):
                print(f"{head} {f['a']}: {f['note']}")
            else:
                print(f"{head} {f['note']}")

    print()
    if not_buildings:
        print(f"  {len(not_buildings)} manifest(s) carry no exterior envelope "
              f"and were not measured (not buildings):")
        for name, _why in not_buildings:
            print(f"       {name}")
    if unreadable:
        print(f"  COULD NOT CHECK {len(unreadable)} manifest(s):")
        for name, why in unreadable:
            print(f"       {name}: {why}")
        print("       A manifest that could not be read is not one that passed.")
        return 2
    # The counts go LAST on purpose: `check_all.py` surfaces one line per check
    # by scanning its output in REVERSE for a summary-shaped line, so anything
    # printed after this would be the line a reader sees instead of the verdict.
    for code in sorted(tot, key=lambda c: (sev(c) != "FAIL", c)):
        note = ""
        if sev(code) == "WARN":
            note = ("   graduates to FAIL at 0"
                    if tot[code] else "   reads 0 -- ready to graduate")
        print(f"  {sev(code):<4} {code:<24} {tot[code]:>4}{note}")
    print(f"  {seen} building(s) read, {clean} with no blocking finding")
    if seen == 0:
        print("  cannot check: nothing measurable in the paths given")
        return 2
    return 1 if any(tot[c] for c in tot if sev(c) == "FAIL") else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
