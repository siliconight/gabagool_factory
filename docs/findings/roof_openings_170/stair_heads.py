"""Roadmap 170, step 2: how big the bulkhead over each roof-reaching stair has to be, read off the specs.

For every authored spec whose stair reaches the roof (`to_story >= n_stories`, the census's 16), the hole
`_stairs` cuts in the roof slab -- `stairwell.hole_span` for its width and centre across the runs, and along the
travel direction `run / 2 + 0.3` behind the bottom step to `run / 2 + WALKOFF_CLEAR` past the top landing -- is
the bulkhead's inner footprint; the stair's `footprint_rect` against the building's footprint says how much roof
is left around it for walls and a parapet. Prints a row per stair and the ranges, and stops.

    python stair_heads.py            (from anywhere; reads ../../../deli_counter)
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DC = os.path.normpath(os.path.join(HERE, "..", "..", "..", "deli_counter"))
sys.path.insert(0, DC)

import stairwell  # noqa: E402
from spec_loader import load_spec  # noqa: E402


def main():
    rows = []
    for f in sorted(glob.glob(os.path.join(DC, "specs", "*.json"))):
        try:
            sp = load_spec(f)
        except Exception as exc:  # a spec the loader refuses is not a building here
            continue
        for st in sp.stairs:
            if int(st.to_story) < int(sp.n_stories):
                continue
            cx, w = stairwell.hole_span(st)
            near = st.run / 2 + 0.3
            far = st.run / 2 + stairwell.WALKOFF_CLEAR
            rect = stairwell.footprint_rect(st)
            fx, fy = sp.footprint_x / 2, sp.footprint_y / 2
            edge = min(fx - abs(rect[0]), fx - abs(rect[2]), fy - abs(rect[1]), fy - abs(rect[3]))
            par = [(p.height, p.thick) for p in sp.parapets if p.story >= sp.n_stories]
            rows.append((os.path.basename(f)[:-5], sp.n_stories, sp.story_height, w, near + far, st.run, st.width,
                         st.facing, st.x, st.y, sp.footprint_x, sp.footprint_y, edge, par))
    print(f"{'spec':30s} st   H   hole w x L      run  w   face  at            footprint   edge  parapet")
    for r in rows:
        print(f"{r[0]:30s} {r[1]:2d} {r[2]:4.2f} {r[3]:4.2f} x {r[4]:4.2f}  {r[5]:4.1f} {r[6]:3.1f}  {r[7]:1s}  "
              f"({r[8]:6.1f},{r[9]:6.1f})  {r[10]:4.1f}x{r[11]:4.1f}  {r[12]:4.2f}  {r[13]}")
    if rows:
        ws = [r[3] for r in rows]
        ls = [r[4] for r in rows]
        es = [r[12] for r in rows]
        print(f"{len(rows)} stairs: hole width {min(ws):.2f}..{max(ws):.2f}, length {min(ls):.2f}..{max(ls):.2f}, "
              f"roof left to the edge {min(es):.2f}..{max(es):.2f} m; storey {min(r[2] for r in rows):.2f}.."
              f"{max(r[2] for r in rows):.2f} m")


if __name__ == "__main__":
    sys.exit(main())
