"""Which unreachable markers are real defects, and which are out of scope.

    python marker_scope_census.py deli_counter\\build
    python marker_scope_census.py deli_counter\\build --list

Pure: `<id>.gameplay.json` and `<id>.navgate.json`, both already on disk. No
Blender, no Godot, no rebuild. Runs over 135 shells in about a second.

## The question

`nav_gate` reports 107 of 135 shells with an unreachable marker. Read as a
per-building quality signal that says four fifths of the library is broken,
and any rule keyed on it keeps six shells.

docs/NAV_GATE_FINDINGS.md (2026-08-05) already said most of those are benign:

    "snap > SNAP_MAX -- 94 occurrences, benign. Almost all extraction_*:
     STREET, EXIT, YARD, LOT, DRIVE. Exterior markers outside the single
     building whose navmesh was baked. Nothing to fix."
    "Distinguishing the two in the gate's own output is a real improvement
     and is NOT yet implemented."

This script implements the distinction, and measures the discriminator that
paragraph proposes rather than adopting it.

## Why snap distance is the wrong discriminator

Snap distance is how far the marker moved to land on a navmesh polygon. It
CORRELATES with being outside the building, because an exterior marker is
further from interior navmesh -- but it is not the same fact, and the two come
apart in both directions on this library:

    corner_deli_heist_01  objective_SAFE   snap 2.6 m   INSIDE the footprint
    cr_deli               loot_VAULT_CASH  snap 2.4 m   INSIDE the footprint
    gas_station           extraction_FORECOURT snap 1.2 m  OUTSIDE the footprint

Ten markers are classified differently by the two rules -- six real defects
the snap rule would drop as benign, four benign ones it would report as real.
Six dropped defects is the expensive direction: a check that silently declines
to look is the failure mode this repo has already paid for three times.

## The discriminator that is not a proxy

`gameplay.json` carries the building's `footprint` and every marker's `x, y`.
Whether a marker is inside the building is therefore arithmetic on data both
manifests already hold -- not an inference from how far something moved.

    exterior  ==  |x| > footprint[0]/2  or  |y| > footprint[1]/2

Measured over all 135 shells:

    extraction OUTSIDE the footprint x UNREACHABLE                    99
    extraction OUTSIDE the footprint x reachable                       8
    extraction INSIDE  the footprint x reachable                      11
    extraction INSIDE  the footprint x UNREACHABLE                     1
    NO extraction marker at all                                       16

An extraction point is where the crew leaves with the loot. It stands on the
street. The street is laid by Lot when it assembles the site, so a per-building
navmesh cannot contain it, and asking a building-scope bake whether it is
reachable is asking a question at a scope where its subject does not exist.
The answer is no 99 times, and it is not about the building.

The 8 that pass are not better buildings -- they are buildings whose extraction
sits closer to the wall than the bake's inset:

    1.0 m outside the footprint:  0 unreachable,  4 reachable
    2.0 m outside the footprint: 89 unreachable,  2 reachable

## What this changes

Excluding exterior markers from the building-scope verdict and keeping
UNJUDGED as its own state:

    interior markers all reachable  103 shells   43 families
    an interior marker unreachable   15 shells   14 families
    no interior marker judged        17 shells   17 families

`final_stand` -- the shell walked on 2026-08-07 with a stair into a wall and
an objective nobody can reach -- is still refused, on both conditions.
`pharmacy_a02`, which stood up in the same walk, is still admitted. The
corrected rule keeps the true positive and drops 92 false ones.

## What it deliberately does not do

It does not filter a library, edit a manifest or promote a warning. It reports.
Which of these should BLOCK is a decision about the game.
"""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

def _factory_root() -> Path:
    """The directory holding `factory.manifest.json`, found by walking up.

    Was `Path(__file__).resolve().parent`, which required this file to sit AT
    the factory root and kept eleven scripts pinned there. Walking up means it
    works from `tools/`, `patches/` or anywhere else, and still returns the
    root when it IS the root -- the first candidate tested is its own
    directory.

    The manifest is the marker because it is the one file that defines this
    place and exists in no tool repo. `.git` would match every tool repo.
    """
    here = Path(__file__).resolve()
    for base in (here.parent, *here.parents):
        if (base / "factory.manifest.json").is_file():
            return base
    return here.parent


ROOT = _factory_root()
sys.path.insert(0, str(ROOT / "level_factory"))

SNAP_MAX = 2.0          # agent_contract.qa.snap_max_m, for the comparison only
_VARIANT = re.compile(r"_a\d+$")


def _load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _family(aid: str) -> str:
    return _VARIANT.sub("", aid)


def _outside(marker, half_x: float, half_y: float) -> bool:
    try:
        return (abs(float(marker.get("x", 0))) > half_x + 1e-6
                or abs(float(marker.get("y", 0))) > half_y + 1e-6)
    except (TypeError, ValueError):
        return False


def _coverage(root: Path, aid: str) -> dict:
    data = _load(root / f"{aid}.slots.json")
    cov = (data or {}).get("coverage")
    return dict(cov) if isinstance(cov, dict) else {}


def _rule():
    """`building_library.source_exclusion`, or ``None`` — never a local copy.

    THIS SCRIPT GLOBS THE DIRECTORY and does not go through
    `building_library.index`; the 2026-08-09 handoff said it did. That matters
    because "103 navigable, 15 with a holed interior, 17 unjudged" was printed
    by THIS file, and a fix applied only at `index` would have left those three
    numbers counted over a library that includes nine composed Level Factory
    sites and two facades — while `library_themed_fit.py`, which does go
    through `index`, reported a different denominator for the same directory.
    Two instruments disagreeing about what is in a folder is the state this
    repo has a hard rule about.

    Imported rather than restated, for the reason `library_themed_fit.py`
    gives at length: a second copy of the rule reports what the report thinks.
    """
    try:
        from packages.pipeline import building_library as bl
        return bl.source_exclusion
    except Exception:                           # noqa: BLE001 -- reported above
        return None


def source_ids(root: Path, argv: list[str]):
    """``(ids, excluded)`` for a build dir — or ``None`` when it cannot judge.

    REFUSES rather than printing an unfiltered census, because an unfiltered
    census here is not a rougher number, it is the defect: every count in this
    file's docstring was taken with the pipeline's own output in the
    denominator. `--unfiltered` prints it anyway, and says so, for comparing
    against a figure taken before this landed.
    """
    ids = sorted(p.name[: -len(".glb")] for p in root.glob("*.glb"))
    if "--unfiltered" in argv:
        print("!! --unfiltered: this census includes the pipeline's own "
              "composed output and Deli Counter's facades")
        return ids, []
    rule = _rule()
    if rule is None:
        print("could not import building_library.source_exclusion")
        print(f"  expected it under {ROOT / 'level_factory'}")
        print("  this file must SIT in the factory root next to level_factory/")
        print("  re-run with --unfiltered to census the raw directory anyway")
        return None
    keep, excluded = [], []
    for aid in ids:
        why = rule(root, aid)
        if why:
            excluded.append((aid, why))
        else:
            keep.append(aid)
    return keep, excluded


# ------------------------------------------------------------------- selftest
def _selftest() -> int:
    """Prove the discriminator before trusting a census built on it.

    `_outside` IS the finding of 2026-08-08: it is what replaced snap distance
    and moved the library from 6 themeable families to 37, and from "99
    unreachable extractions" to "99 questions asked at the wrong scope". Every
    number this file prints rests on it, and nothing had ever put it wrong on
    purpose.

    THE ASYMMETRIC CASE IS THE ONE THAT MATTERS. `_outside(marker, hx, hy)`
    takes the half-extents in x, y order and `main` passes
    `fp[0]/2, fp[1]/2`. On a square footprint a swap is invisible; on a
    46 x 26 building it misclassifies a whole band of markers in both
    directions. That is the same shape as the `.glb` Y-up bug that made a
    correct kit read as broken, and the same shape as `module_stem` keying a
    plate on width alone -- an axis assumed rather than stated.

    A marker exactly on the wall is INSIDE. A footprint edge belongs to the
    building; `_outside` uses a 1e-6 epsilon so a coordinate that lands on the
    line does not flip on floating-point noise.
    """
    hx, hy = 23.0, 13.0        # depot_a01: a 46 x 26 footprint, deliberately not square
    cases = [
        ("centre",              {"x": 0.0,   "y": 0.0},   False),
        ("just inside +x",      {"x": 22.9,  "y": 0.0},   False),
        ("just outside +x",     {"x": 23.1,  "y": 0.0},   True),
        ("just inside -x",      {"x": -22.9, "y": 0.0},   False),
        ("just outside -x",     {"x": -23.1, "y": 0.0},   True),
        ("just inside +y",      {"x": 0.0,   "y": 12.9},  False),
        ("just outside +y",     {"x": 0.0,   "y": 13.1},  True),
        ("on the +x wall",      {"x": 23.0,  "y": 0.0},   False),
        ("on the -y wall",      {"x": 0.0,   "y": -13.0}, False),
        # THE SWAP DETECTOR. Inside on the long axis, outside on the short one.
        # Reading the half-extents in the wrong order calls this one inside.
        ("x-ok, y-out (swap)",  {"x": 20.0,  "y": 20.0},  True),
        # ...and its mirror: outside on x, inside on y.
        ("x-out, y-ok (swap)",  {"x": 30.0,  "y": 5.0},   True),
        # A marker with no usable coordinates is not a claim about geometry.
        ("no coordinates",      {},                       False),
        ("unparseable",         {"x": "n/a", "y": 0.0},   False),
    ]
    bad = 0
    for label, marker, want in cases:
        got = _outside(marker, hx, hy)
        ok = got is want
        bad += not ok
        print(f"[selftest] {label:22} -> {str(got):5} want {str(want):5} "
              f"{'ok' if ok else 'FAIL'}")

    fam = [("depot_a01", "depot"), ("pharmacy_a02", "pharmacy"),
           ("final_stand", "final_stand"), ("lf_lot_demo_001_5017",
                                            "lf_lot_demo_001_5017")]
    for aid, want_f in fam:
        got_f = _family(aid)
        ok = got_f == want_f
        bad += not ok
        print(f"[selftest] family {aid:22} -> {got_f:22} "
              f"{'ok' if ok else 'FAIL want ' + want_f}")

    # THE SECOND THING EVERY COUNT NOW RESTS ON. `_outside` decides which
    # markers are in scope; `source_exclusion` decides which BUILDINGS are.
    # A wrong answer here is the same class of error one level up -- 135
    # consistent numbers over the wrong set of shells -- so it is proved
    # before the census the same way, and put wrong on purpose in both
    # directions rather than only checked on a known offender.
    rule = _rule()
    if rule is None:
        print("[selftest] source_exclusion UNAVAILABLE -- the census will "
              "refuse rather than count the pipeline's own output as buildings")
    else:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            (tmp / "quiet_row_a01.validation.json").write_text(
                '{"facade": true}', encoding="utf-8")
            (tmp / "gs_facade_but_real.validation.json").write_text(
                '{"facade": false}', encoding="utf-8")
            src_cases = [
                # the two real kinds
                ("lf_lot_demo_001_5017", tmp, True),
                ("quiet_row_a01", tmp, True),
                # ...and the two ways a name rule would get it wrong. The
                # facade test reads Deli Counter's flag, not the id, so a
                # building merely NAMED like a facade stays in.
                ("gs_facade_but_real", tmp, False),
                ("depot_a01", tmp, False),
            ]
            for aid, d, want in src_cases:
                got = bool(rule(d, aid))
                ok = got is want
                bad += not ok
                print(f"[selftest] source  {aid:24} -> excluded={str(got):5} "
                      f"want {str(want):5} {'ok' if ok else 'FAIL'}")

    if bad:
        print("[selftest] the discriminator is wrong; every count below it is "
              "a number, not a measurement")
        return 1
    print("[selftest] footprint arithmetic, family grouping and the "
          "source/output split all handled")
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return _selftest()
    if not argv:
        print("usage: python marker_scope_census.py <deli_counter/build> "
              "[--list] [--selftest]")
        return 2
    root = Path(argv[0])
    show = "--list" in argv
    if not root.is_dir():
        print(f"not a directory: {root}")
        return 2
    # Proved before it is trusted, every run. The census is one number per
    # shell over 135 shells; a wrong discriminator is 135 wrong numbers that
    # all look consistent with each other.
    if _selftest():
        return 1
    print()

    got = source_ids(root, argv)
    if got is None:
        return 2
    ids, excluded = got
    if excluded:
        # Printed, not merely subtracted. Every figure in this file's own
        # docstring was measured with these in the denominator, so the
        # difference has to be visible to compare an old number to a new one.
        print(f"NOT SOURCE ARCHETYPES -- excluded from every count below "
              f"({len(excluded)}):")
        for aid, why in excluded:
            print(f"    {aid:34} {why}")
        print()

    rows = []
    skipped = []
    for aid in ids:
        glb = root / f"{aid}.glb"
        game = _load(root / f"{aid}.gameplay.json")
        nav = _load(root / f"{aid}.navgate.json")
        if game is None or nav is None:
            skipped.append(aid)
            continue
        fp = game.get("footprint") or []
        if len(fp) < 2:
            # No footprint means no inside/outside. Reported, not assumed --
            # guessing a bounding box here would put the whole census on an
            # invented number.
            skipped.append(aid)
            continue
        hx, hy = float(fp[0]) / 2.0, float(fp[1]) / 2.0
        by_name = {str(m.get("name", "")).upper(): m
                   for m in (game.get("markers") or [])}
        markers = nav.get("markers") or {}
        unreach = [str(u) for u in (markers.get("unreachable") or [])]
        exterior_count = sum(1 for m in (game.get("markers") or [])
                             if m.get("type") == "extraction")

        judged = []
        for raw in unreach:
            name = re.sub(r"\s*\(.*\)$", "", raw).strip()
            snap_m = re.search(r"snap ([\d.]+)m", raw)
            snap = float(snap_m.group(1)) if snap_m else None
            key = name.split("_", 1)[1].upper() if "_" in name else name.upper()
            marker = by_name.get(key) or by_name.get(name.upper())
            # None means the navgate named a marker the gameplay manifest does
            # not. Kept as None rather than defaulted to interior, because
            # "unknown" and "inside" are different answers.
            outside = None if marker is None else _outside(marker, hx, hy)
            judged.append(dict(name=name, snap=snap, outside=outside))

        rows.append(dict(
            aid=aid, family=_family(aid), fp=(fp[0], fp[1]),
            checked=int(markers.get("checked") or 0),
            reachable=int(markers.get("reachable") or 0),
            unreachable=judged, exterior_markers=exterior_count,
            coverage=_coverage(root, aid)))

    if not rows:
        print("no shell had both a gameplay and a navgate manifest")
        return 1
    print(f"library: {root}")
    print(f"  {len(rows)} shells with both manifests and a footprint"
          + (f"; {len(skipped)} skipped ({', '.join(skipped[:6])})"
             if skipped else ""))
    print()

    # ---------------------------------------------------------------- scope
    tab = collections.Counter()
    for r in rows:
        has_ext = r["exterior_markers"] > 0
        fails_ext = any(j["outside"] for j in r["unreachable"])
        inside_ext = has_ext and not any(
            j["outside"] for j in r["unreachable"]) and not fails_ext
        key = ("has an extraction marker" if has_ext
               else "NO extraction marker at all")
        tab[(key, "its extraction is UNREACHABLE" if fails_ext
             else "nothing exterior failed")] += 1
    print("EXTRACTION MARKERS, WHICH THE BUILDING BAKE CANNOT REACH:")
    for k, v in sorted(tab.items()):
        print(f"    {k[0]:30} x {k[1]:32} {v:>4}")
    print()

    # --------------------------------------------- the two classifiers agree?
    dis = []
    for r in rows:
        for j in r["unreachable"]:
            if j["outside"] is None or j["snap"] is None:
                continue
            if j["outside"] != (j["snap"] > SNAP_MAX):
                dis.append((r["aid"], j))
    print(f"SNAP-DISTANCE RULE vs FOOTPRINT GEOMETRY: {len(dis)} "
          f"disagreement(s) over every unreachable marker")
    for aid, j in dis:
        why = ("INTERIOR, but snap > SNAP_MAX -- the snap rule drops a real "
               "defect" if not j["outside"] else
               "EXTERIOR, but snap <= SNAP_MAX -- the snap rule reports a "
               "benign one")
        print(f"    {aid:30} {j['name']:26} snap={j['snap']:>4}  {why}")
    print()

    # ------------------------------------------------------ corrected verdict
    clean, dirty, unjudged = [], [], []
    for r in rows:
        interior_checked = r["checked"] - r["exterior_markers"]
        bad = [j for j in r["unreachable"] if j["outside"] is not True]
        if interior_checked <= 0:
            unjudged.append(r)
        elif bad:
            dirty.append((r, bad))
        else:
            clean.append(r)

    def fams(entries):
        return sorted({e["family"] for e in entries})

    print("BUILDING-SCOPE VERDICT WITH EXTERIOR MARKERS EXCLUDED:")
    for label, sel in (("interior markers all reachable", clean),
                       ("an interior marker unreachable",
                        [r for r, _ in dirty]),
                       ("no interior marker judged -- NOT passing", unjudged)):
        print(f"    {label:44} {len(sel):>4} shells  "
              f"{len(fams(sel)):>3} families")
    print()

    themed = [r for r in clean if r["coverage"]]
    tf = fams(themed)
    print(f"THEMED-FIT UNDER THE CORRECTED RULE (coverage + interior "
          f"reachability): {len(themed)} shells, {len(tf)} families")
    for i in range(0, len(tf), 4):
        print("      " + "  ".join(f"{x:22}" for x in tf[i:i + 4]))
    print()

    print("THE REAL SIGNAL -- shells with an interior marker nothing can "
          f"reach ({len(dirty)}):")
    for r, bad in dirty:
        print(f"    {r['aid']:32} "
              + ", ".join(f"{j['name']} ({j['snap']}m)" for j in bad[:4]))
    if show:
        print()
        print(f"NEVER JUDGED ({len(unjudged)}) -- nothing asked, so nothing "
              f"passed:")
        print("    " + ", ".join(r["aid"] for r in unjudged))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
