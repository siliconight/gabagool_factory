"""How many families can carry a theme, using the pipeline's OWN predicate.

Run from the factory root (the file must SIT there -- it locates
`level_factory/packages` relative to itself, so cwd does not matter):

    python library_themed_fit.py deli_counter\\build
    python library_themed_fit.py deli_counter\\build --list

Read-only. Imports `building_library` and calls the same `index` and
`themed_report` that selection calls. No Blender, no Godot, no writes.

## Why it imports rather than reimplements

The first version of this script carried its own copy of the fitness rule, and
that was a mistake of exactly the kind it was written to find. A report that
computes the answer a second way tells you what the report thinks, not what the
pipeline will do; when the two drift, the number on screen is the one nobody
ships. Now the only thing here is presentation.

It also means this script CHANGES when the rule changes, which is the point.

## What the rule is, as of 2026-08-08

A shell can carry a theme when its slot manifest has a non-empty `coverage`
(the themed kit fills its walls) and its navgate manifest says
`navigable: true` (a body can reach what the mission needs INSIDE it).

That second half is read, never recomputed. Deli Counter's `nav_gate` owns the
inside/outside classification because it holds the marker positions and the
footprint. A manifest written before the 2026-08-08 scope split has no
`markers.interior_checked`, and is reported UNSCOPED rather than trusted --
its `navigable` counted extraction points standing on streets Lot has not laid
yet, and 99 of 135 shells read `false` for that reason alone.

## Two numbers, and only one of them decides

`pick_lot` draws one shell per FAMILY. Six fit shells spread over three
families cannot fill a five-building lot: the shell count looks sufficient and
selection fails anyway. Families are what this prints in bold.
"""
from __future__ import annotations

import collections
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "level_factory"))


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: python library_themed_fit.py <deli_counter/build> "
              "[--list] [--count N]")
        return 2
    library = Path(argv[0])
    show = "--list" in argv
    want = int(argv[argv.index("--count") + 1]) if "--count" in argv else 5
    if not library.is_dir():
        print(f"not a directory: {library}")
        return 2

    try:
        from packages.pipeline import building_library as bl
    except Exception as exc:                    # noqa: BLE001 -- reported
        print(f"could not import building_library: {exc}")
        print(f"  expected it under {ROOT / 'level_factory'}")
        print("  this file must SIT in the factory root next to level_factory/")
        return 2
    if not hasattr(bl, "themed_report"):
        print("building_library has no `themed_report` -- this tree predates "
              "themed selection, so there is no rule here to report on")
        return 2

    if not hasattr(bl, "source_exclusion"):
        print("building_library has no `source_exclusion` -- this tree predates "
              "the source/output split, so every number below would be counted "
              "against a library containing the pipeline's own composed output")
        return 2

    complete, incomplete, non_source = bl.index(str(library))
    fit, unfit = bl.themed_report(complete)

    def fams(rows):
        return sorted({r.get("family", "") for r in rows})

    fit_fams = fams(fit)
    print(f"library: {library}")
    print(f"  index(): {len(complete)} complete, {len(incomplete)} incomplete "
          f"(dropped for a missing REQUIRED manifest)")
    print(f"  not source archetypes: {len(non_source)} "
          f"(the pipeline's own composed output and Deli Counter's facades, "
          f"which sit in this directory because it is both source and sink)")
    for e in sorted(non_source, key=lambda x: x["id"]):
        print(f"      {e['id']:34} {e['reason']}")
    print(f"  themed_report(): {len(fit)} fit, {len(unfit)} unfit")
    print()
    print(f"THE NUMBER THAT DECIDES: {len(fit_fams)} fit famil"
          f"{'y' if len(fit_fams) == 1 else 'ies'} against a lot of {want}")
    if len(fit_fams) >= want:
        print(f"  >= {want}: a themed lot of {want} can be drawn.")
    else:
        print(f"  <  {want}: every themed run of {want} refuses. The work is "
              f"in Deli Counter -- build or judge the missing shells.")
    print()

    if show and fit:
        by = collections.defaultdict(list)
        for r in fit:
            by[r.get("family", "")].append(r.get("id", "?"))
        for f in fit_fams:
            print(f"      {f:26} {', '.join(sorted(by[f]))}")
        print()

    tally = collections.Counter()
    for r in unfit:
        for reason in r.get("reasons") or ():
            tally[str(reason).split(":", 1)[0]] += 1
    print(f"WHY THE OTHER {len(unfit)} ARE OUT (a shell can fail more than "
          f"one condition):")
    for reason, n in tally.most_common():
        print(f"    {reason:34} {n:>4}")
    print()

    # The cheapest route to a wider library: shells short by ONE condition
    # whose family the fit set does not already hold. Fixing a shell whose
    # family is already covered widens nothing, because `pick_lot` draws one
    # per family -- so the two are worth separating.
    have = set(fit_fams)
    near = collections.defaultdict(list)
    for r in unfit:
        reasons = r.get("reasons") or []
        if len(reasons) == 1 and r.get("family") not in have:
            near[r["family"]].append((r.get("id", "?"),
                                      str(reasons[0]).split(":", 1)[0]))
    print(f"ONE CONDITION SHORT, in a family the fit set lacks: "
          f"{sum(len(v) for v in near.values())} shell(s) across "
          f"{len(near)} famil{'y' if len(near) == 1 else 'ies'}")
    for f in sorted(near)[:20]:
        print(f"      {f:26} "
              + ", ".join(f"{i} ({why})" for i, why in sorted(near[f])[:3]))
    if len(near) > 20:
        print(f"      ... and {len(near) - 20} more families")

    if show and unfit:
        print()
        print("--- every unfit shell ---")
        for r in sorted(unfit, key=lambda x: x.get("id", "")):
            print(f"    {r.get('id', '?'):32} "
                  + "; ".join(str(x).split(":", 1)[0]
                              for x in (r.get("reasons") or [])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
