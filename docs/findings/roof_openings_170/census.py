"""Roadmap 170: the split the item asked for first -- a bulkhead where a STAIR reaches the roof, a lid where a
LADDER does -- counted over Deli Counter's authored specs rather than assumed.

For every `deli_counter/specs/*.json`: the storeys, the stairs whose `to_story` reaches the roof level
(`n_stories`), the ladders whose role is `roof_access` (or whose `upper_surface` is `roof` / whose `transition`
is `roof_hatch_exit`), and the `vertical_links` of kind `hatch` on the roof slab. Each roof opening is then
sorted by what reaches it: a stair (bulkhead), a ladder only (lid), or a hatch link with neither (a hole in the
contract). It prints the counts and the per-spec rows for the buildings with a roof opening, and stops.

    python census.py [specs_dir]
"""
import collections
import glob
import json
import os
import sys


def main(argv):
    specs = argv[1] if len(argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                        "..", "..", "..", "deli_counter", "specs")
    specs = os.path.abspath(specs)
    files = sorted(glob.glob(os.path.join(specs, "*.json")))
    totals = collections.Counter()
    rows = []
    unreadable = 0
    for f in files:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            unreadable += 1
            continue
        if not isinstance(d, dict) or "n_stories" not in d:
            unreadable += 1
            continue
        n = int(d.get("n_stories") or 0)
        stairs = [s for s in (d.get("stairs") or []) if isinstance(s, dict)]
        ladders = [l for l in (d.get("ladders") or []) if isinstance(l, dict)]
        links = [v for v in (d.get("vertical_links") or []) if isinstance(v, dict)]
        stair_to_roof = [s for s in stairs if int(s.get("to_story", -1)) >= n]
        roof_ladders = [l for l in ladders
                        if l.get("role") == "roof_access" or l.get("upper_surface") == "roof"
                        or l.get("transition") == "roof_hatch_exit" or int(l.get("to_story", -1)) >= n]
        roof_hatches = [v for v in links if v.get("kind") == "hatch" and int(v.get("story", -1)) >= n]
        other_hatches = [v for v in links if v.get("kind") == "hatch" and int(v.get("story", -1)) < n]
        totals["specs"] += 1
        totals["stairs"] += len(stairs)
        totals["stairs to the roof"] += len(stair_to_roof)
        totals["ladders"] += len(ladders)
        totals["roof_access ladders"] += len(roof_ladders)
        totals["hatch links on the roof slab"] += len(roof_hatches)
        totals["hatch links below the roof"] += len(other_hatches)
        if roof_ladders or roof_hatches or stair_to_roof:
            totals["specs with a roof opening or a stair to the roof"] += 1
            kind = ("stair" if stair_to_roof else "ladder" if roof_ladders else "hatch link only")
            totals[f"  reached by: {kind}"] += 1
            rows.append((os.path.basename(f)[:-5], n, len(stair_to_roof), len(roof_ladders), len(roof_hatches),
                         kind))
    print(f"specs dir: {specs}")
    print(f"read {totals['specs']} specs ({unreadable} skipped: not a building spec)")
    for k in ("stairs", "stairs to the roof", "ladders", "roof_access ladders", "hatch links on the roof slab",
              "hatch links below the roof", "specs with a roof opening or a stair to the roof",
              "  reached by: stair", "  reached by: ladder", "  reached by: hatch link only"):
        print(f"  {k:48s} {totals[k]:5d}")
    print()
    print(f"{'spec':40s} {'storeys':>7s} {'stairs->roof':>12s} {'roof ladders':>12s} {'roof hatches':>12s}  reached by")
    for r in rows:
        print(f"{r[0]:40s} {r[1]:7d} {r[2]:12d} {r[3]:12d} {r[4]:12d}  {r[5]}")
    # THE TWO POPULATIONS, by what cuts the roof slab. A stair that reaches the roof with `cut_slabs` leaves
    # the hole at its head (the bulkhead case); a roof ladder leaves one only where a `hatch` link sits at its
    # own (x, y) -- an exterior or parapet ladder cuts nothing and needs no lid.
    stair_rows = []
    ladder_kinds = collections.Counter()
    ladder_holes = collections.Counter()
    for f in files:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(d, dict) or "n_stories" not in d:
            continue
        n = int(d.get("n_stories") or 0)
        links = [v for v in (d.get("vertical_links") or []) if isinstance(v, dict)]
        roof_hatches = [v for v in links if v.get("kind") == "hatch" and int(v.get("story", -1)) >= n]
        for s in (d.get("stairs") or []):
            if isinstance(s, dict) and int(s.get("to_story", -1)) >= n:
                stair_rows.append((os.path.basename(f)[:-5], n, s.get("style"), bool(s.get("cut_slabs")),
                                   s.get("role"), len(roof_hatches)))
        for l in (d.get("ladders") or []):
            if not isinstance(l, dict):
                continue
            if not (l.get("role") == "roof_access" or l.get("upper_surface") == "roof"
                    or l.get("transition") == "roof_hatch_exit" or int(l.get("to_story", -1)) >= n):
                continue
            ladder_kinds[(l.get("placement_mode"), l.get("transition"))] += 1
            at_foot = [v for v in roof_hatches
                       if abs(float(v.get("x", 1e9)) - float(l.get("x", 0))) < 0.01
                       and abs(float(v.get("y", 1e9)) - float(l.get("y", 0))) < 0.01]
            ladder_holes["hatch link at the ladder's (x, y): the slab is cut" if at_foot
                         else "no hatch link at the ladder: nothing cut"] += 1
    print()
    print("stairs that reach the roof (spec, storeys, style, cut_slabs, role, roof hatch links in the spec):")
    for r in stair_rows:
        print(f"  {r[0]:36s} {r[1]:2d}  {r[2]:10s} cut_slabs={r[3]!s:5s} {r[4]:20s} hatches={r[5]}")
    print(f"  {len(stair_rows)} stairs, {sum(1 for r in stair_rows if r[3])} of them cutting the slab they reach")
    print("roof ladders by (placement_mode, transition):", ladder_kinds.most_common())
    print("roof ladders by whether the slab is cut:", ladder_holes.most_common())


if __name__ == "__main__":
    sys.exit(main(sys.argv))
