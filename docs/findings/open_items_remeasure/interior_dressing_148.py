"""Roadmap 148 re-measured: what dresses the inside of a building today.

148 (2026-09-11) asked for the interior half of Layer 3 -- posters, garbage, clocks, vents, smoke detectors, as a
no-collision dressing layer on interior walls, ceilings and floors -- and found nothing walked an interior surface.
This counts two things: the species Zoo has that answer the ask by name (its `zoo_keeper/recipes/`), and the props
each mission building of a package carries (the GLBs under `lot/<building>/art/zoo/`, species read off the file
stem; the Empties' are merged and not listed). It prints and stops; whether a room reads as inhabited is a walk.

    python docs/findings/open_items_remeasure/interior_dressing_148.py <package dir>
"""
import collections
import glob
import os
import pathlib
import re
import sys

ZOO_RECIPES = pathlib.Path(__file__).resolve().parents[3] / "zoo" / "zoo_keeper" / "recipes"
ASKED = {"poster": ("poster", "poster_wall"), "garbage": ("litter_bin", "litter_scrap", "trash_bags"),
         "clock": ("clock",), "vent": ("vent", "vent_grille", "ceiling_vent", "vent_stack", "exhaust_fan"),
         "smoke detector": ("smoke_detector",), "light switch": ("light_switch",), "exit sign": ("exit_sign",)}


def main():
    recipes = {p.stem for p in ZOO_RECIPES.glob("*.py") if not p.stem.startswith("_")}
    print("== Zoo species that answer the ask by name (%d recipes)" % len(recipes))
    for ask, names in ASKED.items():
        have = [n for n in names if n in recipes]
        print("  %-15s %s" % (ask, ", ".join(have) if have else "none"))
    pkg = pathlib.Path(sys.argv[1])
    print("== the props each mission building carries in %s" % pkg.name)
    for b in sorted(p for p in (pkg / "lot").iterdir() if (p / "art" / "zoo").is_dir()):
        tally = collections.Counter()
        for g in glob.glob(str(b / "art" / "zoo" / "*.glb")):
            stem = os.path.basename(g)[:-4]
            species = re.split(r"_delco_1997|_w\d+|_\d+$", stem)[0]
            tally[species] += 1
        props = {k: v for k, v in tally.items() if k.startswith("prop_")}
        asked = {k: v for k, v in props.items() if any(k == "prop_" + n for names in ASKED.values() for n in names)}
        print("  %-16s %3d GLBs, %2d species, %2d prop species; of the asked kinds: %s"
              % (b.name, sum(tally.values()), len(tally), len(props),
                 ", ".join("%s x%d" % (k[5:], v) for k, v in sorted(asked.items())) or "none"))


if __name__ == "__main__":
    main()
