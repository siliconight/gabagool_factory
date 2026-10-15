"""The office's stair core as Deli Counter derives it (the walk's findings 7-9, 2026-10-14).

    python docs/findings/walk_2026-10-14/stair_core.py [spec name, default office]

Reads `deli_counter/specs/<name>.json` with Deli Counter's own loader and prints, for each switchback, what the
builder's own rules produce, in spec metres, the building's frame (x, y plan; z up from the lowest storey's floor):
- each leg's storey, run (sign), whether `stairwell.flight_solid_under` fills it, and the z its fill stands on;
- the slab holes the stair cuts, by storey;
- whether the floor under each filled leg's run is cut at the storey the fill stands on;
- every piece `stairwell.stair_guards` derives for it (kind, storey, axis, line, span).

Pure: builds nothing, reads no built file. Prints what it measured and stops; names no cause.
"""
import pathlib
import sys

F = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(F / "deli_counter"))

import spec_loader  # noqa: E402
import stairwell  # noqa: E402


def _overlaps(r, h):
    """Do plan rectangles (x0, y0, x1, y1) overlap by more than a hair?"""
    return min(r[2], h[2]) - max(r[0], h[0]) > 1e-6 and min(r[3], h[3]) - max(r[1], h[1]) > 1e-6


def main(name):
    spec = spec_loader.load_spec(str(F / "deli_counter" / "specs" / ("%s.json" % name)))
    H = spec.story_height
    print("%s: %s x %s m, %d storeys of %.2f m, wall %.2f, floor %.2f"
          % (name, spec.footprint_x, spec.footprint_y, spec.n_stories, H, spec.wall_thick, spec.floor_thick))
    for i, st in enumerate(spec.stairs):
        if st.style != "switchback":
            continue
        print("\nstair %d (%s): at (%.2f, %.2f), stories %d..%d, run %.2f, width %.2f, facing %s, cut_slabs %s, "
              "underside %s" % (i, stairwell.stair_ident(st, i), st.x, st.y, st.from_story, st.to_story, st.run,
                                st.width, getattr(st, "facing", "N"), st.cut_slabs,
                                stairwell.stair_underside(spec, st)))
        cx, w = stairwell.hole_span(st)
        print("  hole_span: centre x %.3f, width %.3f" % (cx, w))
        lo = min(st.from_story, st.to_story)
        for s in range(lo, max(st.from_story, st.to_story)):
            leg = s - lo
            sign = 1 if leg % 2 == 0 else -1
            rect = stairwell.flight_rect(st, s)
            solid = stairwell.flight_solid_under(spec, st, s)
            print("  leg %d, storey %d, run sign %+d: flight_rect x %.3f..%.3f y %.3f..%.3f; solid fill %s, "
                  "standing on z %.2f (storey %d's floor)" % (leg, s, sign, rect[0], rect[2], rect[1], rect[3],
                                                             solid, s * H, s))
    holes = [h for h in spec.slab_holes]
    print("\nslab holes in the spec as loaded (the builder appends a stair's own cuts as it builds):")
    for h in holes:
        print("  storey %d: centre (%.3f, %.3f), %.3f x %.3f" % (h.story, h.x, h.y, h.size_x, h.size_y))
    print("\nstair_guards:")
    for g in stairwell.stair_guards(spec):
        print("  %-5s storey %d  along %s at %8.3f  %8.3f..%8.3f  (%.3f m)%s"
              % (g["kind"], g["story"], g["axis"], g["pos"], g["lo"], g["hi"], g["hi"] - g["lo"],
                 ("  thick %.3f" % g["thick"]) if "thick" in g else ""))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "office")
