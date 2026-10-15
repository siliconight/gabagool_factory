"""Switchback flights filled solid to a floor their own stair has cut away (the walk's finding 9, 2026-10-14).

    python docs/findings/walk_2026-10-14/floating_flights.py

`stairwell.flight_solid_under` fills a switchback's first two legs solid "to that storey's floor", on the premise
that "only the first leg of each run stands on a storey floor". With `cut_slabs`, the stair cuts the slab of every
storey it climbs into, across both runs (`stairwell.hole_span`), so the second leg's fill stands on a floor that
is not there. For every Deli Counter spec under `deli_counter/specs/`, and every switchback in it, this prints each
leg the rule fills whose storey is above the stair's lowest -- the fill's base z, and whether the stair's own hole
on that storey covers the leg's run (from `hole_span`, `flight_rect` and the builder's hole formula) -- and counts
them. Pure: reads specs through Deli Counter's own loader and rules, builds nothing. Names no cause.
"""
import pathlib
import sys

F = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(F / "deli_counter"))

import spec_loader  # noqa: E402
import stairwell  # noqa: E402


def main():
    specs = sorted((F / "deli_counter" / "specs").glob("*.json"))
    hits, stairs_seen, unreadable = [], 0, 0
    for path in specs:
        try:
            spec = spec_loader.load_spec(str(path))
        except Exception as exc:  # a spec the loader refuses is counted, not hidden
            unreadable += 1
            print("UNREADABLE %s: %s" % (path.name, str(exc)[:100]))
            continue
        H = spec.story_height
        for i, st in enumerate(spec.stairs or []):
            if st.style != "switchback":
                continue
            stairs_seen += 1
            lo = min(st.from_story, st.to_story)
            for s in range(lo + 1, max(st.from_story, st.to_story)):
                if not stairwell.flight_solid_under(spec, st, s):
                    continue
                # the hole the leg below cut in this storey's slab: hole_span wide, spanning the leg's run
                cx, w = stairwell.hole_span(st)
                x0, _y0, x1, _y1 = stairwell.flight_rect(st, s)
                covered = (st.cut_slabs and cx - w / 2.0 <= min(x0, x1) + 1e-6
                           and cx + w / 2.0 >= max(x0, x1) - 1e-6)
                hits.append((path.stem, stairwell.stair_ident(st, i), s, s * H, covered))
    for name, sid, s, z, covered in hits:
        print("%-34s %-28s leg on storey %d filled to z %.2f; its storey's slab cut across its run: %s"
              % (name, sid, s, z, covered))
    print("%d filled legs above a stair's lowest storey, %d of them over their own cut, in %d switchbacks across "
          "%d specs (%d unreadable)" % (len(hits), sum(1 for h in hits if h[4]), stairs_seen, len(specs),
                                         unreadable))


if __name__ == "__main__":
    main()
