"""Count coplanar-surface fights across every built building in the factory.

WHY A SWEEP RATHER THAN ANOTHER SINGLE-BUILDING PROBE. cr_deli went 363 -> 23
across four fixes, but cr_deli is one spec. The claim the fixes are supposed to
support is about the EMITTER: that a building made by these tools does not ship
with surfaces fighting. One building cannot carry that claim, and the earlier
baseline -- "103 of 103 buildings affected, 410 in the worst" -- was measured
across the library, so the follow-up has to be measured the same way or the two
numbers are not comparable.

WHAT IT REPORTS, in two columns that answer different questions.

  visible    what zfight_gate.visible_fights returns: every same-facing
             coplanar overlapping face pair that is not entombed in a third
             solid. This is the gate's own verdict and it is deliberately
             conservative.

  exposed    of those, the ones with NOTHING covering the outward side of the
             shared plane -- the direction a camera must look from to see the
             fight. A wall top under a floor slab is `visible` and not
             `exposed`; a parapet corner against the sky is both.

They are printed side by side rather than one replacing the other. `exposed` is
the number that corresponds to what you see when you walk the level; `visible`
is the number a gate should hold the line on, because "a slab happens to be in
front of it today" is a property of the current composition, not of the
building. Where they disagree, that gap is the finding, not a rounding error.

WHAT IT SCANS, and why that is not "every .glb under the root". The first
version of this script globbed `deli_counter/build/*.glb` alongside the site
libraries, and reported `deli_a01 410 exposed` straight after a successful
rebuild. That 410 was a 19 July export sitting in the scratch dir; the rebuilt
copy in `lot/specs/*/buildings/` was a different file. Worse, the dedup key was
`(stem, size)` -- chosen so a building copied into several sites counts once --
which let the stale and fresh copies of the SAME building through as two
buildings. An instrument that mixes a graveyard into a library and prints one
average is the exact defect this toolchain keeps finding elsewhere.

So the library is `lot/specs/<site>/buildings/*.glb`: what `library_walk.py`
stages, and what `rebuild_buildings.py` re-exports. `deli_counter/build/` is a
scratch dir and `_runs/` is throwaway project output; neither is the library.
`--also-build` opts the scratch dir back in when that is what you want to look
at.

STALENESS IS REPORTED, NOT DEDUPED. Copies of one building are collapsed only
when they are byte-identical in size. When they differ, every copy is listed
with its write date and marked DIVERGED, because two sites walking different
geometry for the same building is a finding in itself.

KNOWN INSTRUMENT LIMIT, stated here rather than discovered later. Box extents
come from each node's glTF POSITION accessor min/max, so a slab with a stairwell
hole booleaned through it still reports its full footprint as solid. Stair parts
correctly sitting inside that hole are therefore counted as interpenetrating it.
In cr_deli that is 6 of 23. The fix is a real mesh test, not a bounding box; the
count is honest about being an upper bound until then.

    python sweep_fights.py                 # the built library
    python sweep_fights.py --top 20        # worst 20 only
    python sweep_fights.py --exposed-only  # hide buildings with 0 exposed
    python sweep_fights.py --also-build    # include deli_counter/build scratch

Reads .glb files and prints. Writes nothing.
"""
import argparse
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from factory_paths import factory_root  # noqa: E402


def _load_gate(root):
    """zfight_gate lives in deli_counter, which is where the definition of a
    fight belongs -- beside the emitter it judges. Imported rather than
    reimplemented, because a second copy of this rule would drift from the one
    that has unit tests."""
    dc = root / "deli_counter"
    if not (dc / "zfight_gate.py").is_file():
        raise SystemExit(f"no zfight_gate.py in {dc}. Nothing checked -- and a "
                         f"check that did not run is not a check that passed.")
    sys.path.insert(0, str(dc))
    import zfight_gate
    return zfight_gate


def _exposed(zg, boxes, findings):
    """Findings with nothing covering the OUTWARD side of the shared plane."""
    index = {nm: k for k, (nm, _) in enumerate(boxes)}
    out = []
    for f in findings:
        ia, ib = index[f["a"]], index[f["b"]]
        alo, ahi = boxes[ia][1]
        blo, bhi = boxes[ib][1]
        ax, side, plane = f["axis"], f["side"], f["plane"]
        rlo = [max(alo[k], blo[k]) for k in range(3)]
        rhi = [min(ahi[k], bhi[k]) for k in range(3)]
        o = [k for k in range(3) if k != ax]
        covered = False
        for k, (nm, (slo, shi)) in enumerate(boxes):
            if k in (ia, ib):
                continue
            if side == "max":
                if not (slo[ax] <= plane + zg.TOL
                        and shi[ax] >= plane + zg.OCCLUDE_MARGIN):
                    continue
            else:
                if not (shi[ax] >= plane - zg.TOL
                        and slo[ax] <= plane - zg.OCCLUDE_MARGIN):
                    continue
            if all(slo[q] <= rlo[q] + zg.TOL and shi[q] >= rhi[q] - zg.TOL
                   for q in o):
                covered = True
                break
        if not covered:
            out.append(f)
    return out


def _targets(root, also_build=False):
    """The built library: one entry per distinct build of each building.

    Described by rule so a new site is picked up without editing a list.
    Byte-identical copies of a building across sites collapse to one entry;
    copies that DIFFER are all kept, so divergence surfaces instead of being
    averaged away.
    """
    pats = ["lot/specs/*/buildings/*.glb"]
    if also_build:
        pats.append("deli_counter/build/*.glb")
    by_key = {}
    for pat in pats:
        for p in sorted(root.glob(pat)):
            st = p.stat()
            by_key.setdefault((p.stem, st.st_size), []).append((p, st.st_mtime))
    stems = {}
    for (stem, size) in by_key:
        stems.setdefault(stem, set()).add(size)
    out = []
    for (stem, size), copies in sorted(by_key.items()):
        p, mt = copies[0]
        out.append((p, mt, len(copies), len(stems[stem]) > 1))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--top", type=int, default=0,
                    help="show only the N worst (0 = all)")
    ap.add_argument("--exposed-only", action="store_true",
                    help="hide buildings whose exposed count is 0")
    ap.add_argument("--also-build", action="store_true",
                    help="include deli_counter/build, the scratch dir")
    args = ap.parse_args()

    root = factory_root()
    zg = _load_gate(root)
    files = _targets(root, also_build=args.also_build)
    if not files:
        raise SystemExit(f"no built .glb under {root}. Nothing checked.")

    scanned = ["lot/specs/*/buildings"]
    if args.also_build:
        scanned.append("deli_counter/build")
    print(f"root     {root}")
    print(f"scanned  {', '.join(scanned)}")
    print(f"builds   {len(files)} distinct, "
          f"{sum(c for _, _, c, _ in files)} file(s)\n")

    rows = []
    for p, mt, ncopies, diverged in files:
        try:
            boxes = zg._node_world_boxes(str(p))
            vis, buried = zg.visible_fights(boxes)
            rows.append((p, mt, ncopies, diverged, len(boxes), len(vis),
                         len(_exposed(zg, boxes, vis)), len(buried), None))
        except Exception as e:                     # noqa: BLE001
            rows.append((p, mt, ncopies, diverged, 0, 0, 0, 0,
                         f"{type(e).__name__}: {e}"))

    rows.sort(key=lambda r: (-r[6], -r[5], r[0].name))
    shown = [r for r in rows if not (args.exposed_only and r[6] == 0)]
    if args.top:
        shown = shown[:args.top]

    print(f"{'building':<30} {'built':<11} {'solids':>7} {'visible':>8} "
          f"{'exposed':>8} {'entombed':>9}")
    print("-" * 80)
    for p, mt, ncopies, diverged, n, v, e, b, err in shown:
        day = time.strftime("%Y-%m-%d", time.localtime(mt))
        mark = "  DIVERGED" if diverged else ("" if ncopies == 1
                                              else f"  x{ncopies}")
        if err:
            print(f"{p.stem:<30} {day:<11} {'--':>7} {'--':>8} {'--':>8} "
                  f"{'--':>9}{mark}  {err}")
        else:
            print(f"{p.stem:<30} {day:<11} {n:>7} {v:>8} {e:>8} {b:>9}{mark}")

    ok = [r for r in rows if r[8] is None]
    bad = [r for r in rows if r[8] is not None]
    div = [r for r in rows if r[3]]
    tv = sum(r[5] for r in ok)
    te = sum(r[6] for r in ok)
    clean_v = sum(1 for r in ok if r[5] == 0)
    clean_e = sum(1 for r in ok if r[6] == 0)
    print("-" * 80)
    if args.top and len(shown) < len(rows):
        print(f"  showing {len(shown)} of {len(rows)}")
    print(f"  {len(ok)} build(s) read, {len(bad)} unreadable")
    print(f"  visible  {tv:>6} total   {clean_v}/{len(ok)} clean")
    print(f"  exposed  {te:>6} total   {clean_e}/{len(ok)} clean")
    if div:
        print(f"\n  {len(div)} build(s) DIVERGED -- one building exists at more "
              f"than one\n  size, so some site is walking geometry another site "
              f"is not. Rebuild\n  before reading anything else here:")
        for r in sorted(div, key=lambda r: r[0].stem)[:10]:
            print(f"    {r[0].stem:<28} {r[0].parent.parent.name}")
    if bad:
        print(f"\n  {len(bad)} could not be read. Those are not passes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
