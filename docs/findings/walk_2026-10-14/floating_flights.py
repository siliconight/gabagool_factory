"""Switchback flights filled solid to a floor their own stair has cut away (the walk's finding 9, 2026-10-14).

    python docs/findings/walk_2026-10-14/floating_flights.py

`stairwell.flight_solid_under` fills a switchback's first two legs solid "to that storey's floor", on the premise
that "only the first leg of each run stands on a storey floor". With `cut_slabs`, the stair cuts the slab of every
storey it climbs into, across both runs (`stairwell.hole_span`), so the second leg's fill stands on a floor that
is not there. For every Deli Counter spec under `deli_counter/specs/`, and every switchback in it, this prints each
leg the rule fills whose storey is above the stair's lowest -- its storey, whether that storey's slab is open under
the leg's solid (`stairwell.slab_openings` against `stairwell.flight_solid_rect`, both in world metres), and,
where Deli Counter has it (0.221.0 on), the storey `stairwell.flight_solid_base` now stands the fill on -- and
counts them. Pure: reads specs through Deli Counter's own loader and rules, builds nothing. Names no cause.

REFUTED AND KEPT: the first run of this file read "204 of them over their own cut" and, in the library, 15 of 17.
It compared `hole_span`'s width, which is in the stair's own unrotated frame, against `flight_rect`'s world x, so
the two east-facing stairs (bank, rowhouse_raid) read as uncut. Asked in one frame, every one is over its cut.
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
                # is this storey's slab open under the leg's solid? both rects in world metres
                a0, b0, a1, b1 = stairwell.flight_solid_rect(st, H, s)
                covered = any(o[0] <= a0 + 1e-6 and o[1] <= b0 + 1e-6 and o[2] >= a1 - 1e-6 and o[3] >= b1 - 1e-6
                              for o in stairwell.slab_openings(spec).get(s, ()))
                base = (stairwell.flight_solid_base(spec, st, s) if hasattr(stairwell, "flight_solid_base")
                        else s)
                hits.append((path.stem, stairwell.stair_ident(st, i), s, base, covered))
    for name, sid, s, base, covered in hits:
        print("%-34s %-28s leg on storey %d; its storey's slab open under its solid: %-5s; fill stands on storey %d"
              % (name, sid, s, covered, base))
    lib = [h for h in hits if not h[0].startswith("lf_")]
    print("%d filled legs above a stair's lowest storey, %d of them over a cut, %d standing on their own storey, in %d "
          "switchbacks across %d specs (%d unreadable); in the library apart from Level Factory's lf_ copies, %d legs in "
          "%d specs, %d over a cut, %d standing on their own storey"
          % (len(hits), sum(1 for h in hits if h[4]), sum(1 for h in hits if h[3] == h[2]), stairs_seen, len(specs),
             unreadable, len(lib), len({h[0] for h in lib}), sum(1 for h in lib if h[4]),
             sum(1 for h in lib if h[3] == h[2])))


if __name__ == "__main__":
    main()
