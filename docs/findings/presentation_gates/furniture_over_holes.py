"""Every library shell: which volumes stand over a slab opening on their own
storey (`stairwell.slab_openings`, the holes the builder cuts). Stair guards
are reported apart: they stand at a hole's edge by design. Measures; names no
cause.

    python furniture_over_holes.py
"""
import glob
import json
import os
import sys

DC = r"C:\Projects\gabagool_studios\gabagool_factory\deli_counter"
sys.path.insert(0, DC)
import stairwell  # noqa: E402
from spec_loader import load_spec  # noqa: E402

GUARD = "stair_guard_"


def main():
    shells = sorted(os.path.basename(p)[:-len(".manifest.json")]
                    for p in glob.glob(os.path.join(DC, "build", "*.manifest.json")))
    hits, guard_hits, checked, skipped = [], 0, 0, []
    for name in shells:
        path = os.path.join(DC, "specs", name + ".json")
        if not os.path.exists(path):
            skipped.append(name)
            continue
        try:
            s = load_spec(path)
        except Exception as ex:  # report, do not guess
            skipped.append("%s (%s)" % (name, ex))
            continue
        checked += 1
        holes = stairwell.slab_openings(s)
        H = s.story_height
        for v in s.volumes:
            storey = int(round((v.z - v.size_z / 2.0) / H))
            r = (v.x - v.size_x / 2.0, v.y - v.size_y / 2.0,
                 v.x + v.size_x / 2.0, v.y + v.size_y / 2.0)
            for h in holes.get(storey, []):
                ox = min(r[2], h[2]) - max(r[0], h[0])
                oy = min(r[3], h[3]) - max(r[1], h[1])
                if ox > 0.02 and oy > 0.02:
                    if v.name.startswith(GUARD):
                        guard_hits += 1
                    else:
                        hits.append((name, v.name, storey, round(ox * oy, 2),
                                     round(ox * oy / (v.size_x * v.size_y), 2)))
    print("shells checked %d, skipped %d" % (checked, len(skipped)))
    print("stair guards over a hole edge (by design): %d" % guard_hits)
    print("other volumes over a slab opening: %d in %d shells" % (
        len(hits), len({h[0] for h in hits})))
    for h in sorted(hits, key=lambda h: -h[4]):
        print("  %-28s %-38s storey %d  %.2f m2  (%.0f%% of its plan)" % (h[0], h[1], h[2], h[3], 100 * h[4]))
    if skipped:
        print("skipped:", skipped[:10])


if __name__ == "__main__":
    main()
