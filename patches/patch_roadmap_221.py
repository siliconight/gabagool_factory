"""Roadmap 221: the cause verified and fixed in Patina 0.30.0, not yet run cold.

The status line is rewritten from its unique opening; the item's last line, asserted unique, gets
the verified cause and the fix after it. Then:

    python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

S221 = "*STATUS: OPEN 2026-10-09 -- found while tracing 220: Patina's anchor-derived wall covers face INTO"
N221 = (
    "*STATUS: NARROWED 2026-10-10 -- the cause verified and fixed in Patina 0.30.0, not yet run "
    "cold. `_up_to_z` swaps two axes, a reflection, and the anchor pass took its wall normals from "
    "cross products in that view: all 10 of strip_club_a01's segments pointed into the building. "
    "The floor and roof slabs' edges on each wall's centre line were exterior-wall segments too. "
    "Replayed through Zoo's `plan_dressing`, the club's 51 base courses went from 0 facing out, 0 "
    "on their own side and 28 inside the wall to 45 of 45 out, on their side, on the face; its "
    "curbs from 52 of 57 inside to none; its 2 conduits onto the wall, facing out "
    "(`docs/findings/patina_cover_normals/`). Not yet: a cold run, and the merge's price.*"
)
LAST = "3. then price the merge before and after, at stations that face one side of a building."
ADD = (
    "\n\n**The cause, verified 2026-10-10** (`docs/findings/patina_cover_normals/`). Loaded the way "
    "`patina.cli.run` loads it, strip_club_a01's shell has 10 wall segments, and every derived "
    "normal points at the building's centre, dot -1.00; the same faces' normals with the winding "
    "taken before the permutation all point out. Nothing downstream compensates: Zoo's "
    "`_orient_matrix` turns a cover along the normal and `cover_side` files it by the normal. "
    "The 22 buried base courses (28 on the shell as built today) were a second defect: "
    "`surfaces.classify` accepts an outward face within `_BOUNDARY_TOL`, 0.25 m, of the bounds, "
    "and the floor slab under each wall and the roof slab over it end on the wall's centre line, "
    "0.15 m in. *RETRACTED, kept:* the probe's first run skipped `bake_visual_transforms` and "
    "measured one slab tile's frame, 7 x 3.3 x 4.8 m; and the fix's first draft dropped whole "
    "segments a face covered, which no centre-line segment was, since the slabs run 0.3 m below "
    "and above each face.\n\n"
    "**The fix, Patina 0.30.0:** `_exterior_wall_faces` negates its product in a mirrored view; "
    "`_buried` skips any point with a face of the same facing in front of it, within 0.5 m, "
    "across its run and height (asked per point, so a roofline on the roof slab's exposed edge "
    "stays); a conduit takes its wall's plane. `tests/test_anchor_normals.py`: four of its six "
    "fail on 0.29.2. Suite 393 passed, 1 skipped (0.29.2: 387 and 1).\n\n"
    "**Still to do:** a cold run, and step 3 above, the merge's price at stations that face one "
    "side of a building."
)


def main():
    data = ROADMAP.read_bytes()
    assert b"\r\n" not in data, "the roadmap is LF; found CRLF"
    text = data.decode("utf-8")
    lines = text.split("\n")
    hits = [i for i, ln in enumerate(lines) if ln.startswith(S221)]
    assert len(hits) == 1, ("221 status", len(hits))
    lines[hits[0]] = N221
    text = "\n".join(lines)
    assert text.count(LAST) == 1, "221's last line"
    text = text.replace(LAST, LAST + ADD)
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 221: cause verified, fixed in Patina 0.30.0")


if __name__ == "__main__":
    main()
