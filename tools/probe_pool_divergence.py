r"""How far apart are the greybox lot and the themed lot? Measure it.

    python probe_pool_divergence.py                       # lot_demo_001's seeds
    python probe_pool_divergence.py --library <build_dir> --count 5 \
        --seeds 5017 5118 5219

Run from the FACTORY ROOT (the directory holding `level_factory/`).

Roadmap addendum item J, unresolved since 2026-08-09:

    `require_themed_shells` narrows 134 -> 97 on the themed path only. Same
    seed, four of five archetypes differ and all five positions differ. Laser
    Tag grades the greybox; the themed site ships. The comment on the branch
    chose grade STABILITY over grade VALIDITY and said so; nothing had measured
    which side it landed on.

Nothing has measured it since either, and on 2026-08-12 a candidate was
RE-SELECTED on Laser Tag numbers -- `seed_5219` over `seed_5118`, on 60% route
completion against 0%. If the graded arrangement is not the shipped one, that
decision was made about a level nobody is going to walk.

WHAT IT MEASURES, precisely: the gap between the two POOLS, read straight off
the library. It calls `index`, `require_themed_shells` and `pick_lot` itself --
it does NOT execute the pipeline, and it cannot see which pool a run chose. So
it reports the same divergence before and after `patch_lf_grade_what_ships.py`,
because the pools are still two pools; what that patch changes is which one the
GREYBOX pass draws from.

    verify the PATCH from the run, not from here:
      an --art run prints `[site] graded lot (art run): N of M shell(s) ...`
      on the greybox pass. Before the patch that line did not exist -- only
      the themed pass printed `[site] themed lot: ...`.

This stays useful for the question it was built for: how much does the themed
narrowing cost, on this library, for these seeds. It reads the same two
functions the pipeline calls and prints the difference:

  * the archetypes each pool selects, in order
  * how many differ, and how many hold their position
  * whether the shipped set is a subset of the graded one or a different draw

WHAT IT CANNOT SAY. `pick_lot` returns an ordered selection; world positions
come from Lot's placement, downstream. Order is reported because position
follows it, but "all five positions differ" is a claim about the assembled
site and this probe does not assemble one. Where the addendum says positions,
read this as the selection that determines them.

A DIVERGENCE IS NOT AUTOMATICALLY A DEFECT. The branch comment chose stability
deliberately: re-selecting on the themed pool would change which levels an
already-graded seed draws, and grades already recorded would describe levels
that no longer exist. The question is how large the cost is, which is the one
thing nobody has written down.
"""
from __future__ import annotations

import argparse
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

DEFAULT_LIBRARY = ROOT / "deli_counter" / "build"
DEFAULT_SEEDS = (5017, 5118, 5219)
DEFAULT_COUNT = 5


def _ids(entries) -> list[str]:
    return [e.get("id", "?") for e in entries]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--library", default=str(DEFAULT_LIBRARY),
                    help="Deli Counter build dir (default: deli_counter/build)")
    ap.add_argument("--count", type=int, default=DEFAULT_COUNT,
                    help="buildings per lot (default 5)")
    ap.add_argument("--seeds", type=int, nargs="+", default=list(DEFAULT_SEEDS),
                    help="candidate seeds (default 5017 5118 5219)")
    args = ap.parse_args(argv)

    from packages.pipeline import building_library as BL

    lib = Path(args.library)
    if not lib.is_dir():
        print(f"not a directory: {lib}")
        return 2

    complete, incomplete, non_source = BL.index(lib)
    themed_pool = BL.require_themed_shells(list(complete), args.count)

    print(f"library {lib}")
    print(f"  {len(complete)} complete, {len(incomplete)} incomplete, "
          f"{len(non_source)} non-source")
    print(f"  greybox pool {len(complete)}  ->  themed pool "
          f"{len(themed_pool)}   ({len(complete) - len(themed_pool)} removed)")
    print()

    if not complete:
        print("  nothing to draw from")
        return 1

    tot_diff = tot_pos = 0
    for seed in args.seeds:
        grey = _ids(BL.pick_lot(list(complete), seed, args.count))
        them = _ids(BL.pick_lot(list(themed_pool), seed, args.count))
        same_slot = sum(1 for a, b in zip(grey, them) if a == b)
        differ = len(set(grey) ^ set(them)) // 2 if len(grey) == len(them) \
            else len(set(grey) ^ set(them))
        tot_diff += len(set(grey) - set(them))
        tot_pos += args.count - same_slot

        print(f"seed {seed}")
        print(f"  graded (greybox): {', '.join(grey) or '-'}")
        print(f"  shipped (themed): {', '.join(them) or '-'}")
        print(f"  {same_slot}/{len(grey)} hold their slot; "
              f"{len(set(grey) - set(them))} graded archetype(s) do not ship; "
              f"{len(set(them) - set(grey))} shipped archetype(s) were never "
              f"graded")
        only_grey = sorted(set(grey) - set(them))
        only_them = sorted(set(them) - set(grey))
        if only_grey:
            print(f"    graded, not shipped : {', '.join(only_grey)}")
        if only_them:
            print(f"    shipped, not graded : {', '.join(only_them)}")
        print()

    n = len(args.seeds) * args.count
    print("=" * 62)
    print(f"across {len(args.seeds)} seed(s), {n} building slot(s):")
    print(f"  {tot_diff} graded archetype(s) never ship")
    print(f"  {tot_pos} slot(s) hold a different archetype than the one graded")
    if tot_diff == 0 and tot_pos == 0:
        print("  the two pools draw the same lot -- the themed narrowing costs")
        print("  nothing on this library at these seeds")
    else:
        print("  the two pools draw different lots, and this is the size of it.")
        print("  That is a fact about the LIBRARY, not about the pipeline:")
        print("  after patch_lf_grade_what_ships.py an --art run draws BOTH")
        print("  passes from the themed pool, and this probe cannot see that.")
        print("  Confirm the patch from a real run instead -- the greybox pass")
        print("  prints `[site] graded lot (art run): ...`, a line that did")
        print("  not exist before it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
