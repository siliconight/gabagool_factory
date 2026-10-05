"""Roadmap item 179: manhole covers and sewer drain grates, filed for later.

The walker, 2026-10-04, with five photographs. Appended after item 178, the
status line directly above the heading (the `roadmap_status.py` convention);
the generated index is NOT touched here -- `roadmap_status.py --write`
regenerates it.

    python patch_roadmap_179_street_covers.py <roadmap path>
"""
import pathlib
import sys

ANCHOR = ("building anything new and is the difference between a pipeline that produces\n"
          "levels and one that produces levels somebody would ship.\n")

ITEM = r"""
*STATUS: OPEN 2026-10-04 -- FILED FOR LATER by the walker, with five photographs. Nothing places either today: no species, no placement rule, no skin.*

**179. Manhole covers and sewer drain grates: a street has them, and only so
many.** The walker, 2026-10-04: "in various locations, usually on sidewalks,
we should have manhole covers, sewer drain grates (should be like fire hydrants
where there is only so many in shared area)". Five photographs came with it.

**READ OFF THE PHOTOGRAPHS -- the format, never the marks.**

  * **Covers.** Round cast iron, flush in asphalt or in sidewalk concrete. A
    raised relief over the whole face -- a waffle of short bars in one, a
    field of diamond studs in another -- one cast word across the middle and
    foundry lettering around the rim. Dark iron and rust brown; one carries a
    smear of green marking paint; a tar seam where the asphalt meets the ring.
  * **Drain grates (curb inlets).** A rectangular cast grate in the gutter,
    tight against the kerb: a grid of rectangular slots. Above it, an open
    THROAT cut into the kerb face, dark inside. Rust, grit, a weed in the
    seam; the kerb over one painted yellow, over another red, both chipped.
  * **Where they stand.** A cover in the sidewalk a step behind an inlet; an
    inlet at a corner beside the ramp, with a round cover out in the
    crosswalk; inlets along a kerb between corners.

Invented marks only (`fake-delco-brands`): any foundry or municipal name on a
cover is ours, not a real foundry's.

**THE RULE IT ASKS FOR IS THE HYDRANT'S, AND THE HYDRANT'S IS SOURCED.**
`lot/site_furniture.py` stands hydrants by two rules:
  * `CORNER_ONE_EACH` -- one per corner, so two roads sharing a corner do not
    each stand one;
  * `HYDRANT_MIN_SPACING = HYDRANT_SPACING_DESIGN / 2` = 45.7 m site-wide,
    from the 91.4 m district average NFPA 1 and AWWA M17 state.
A cover and an inlet want the same shape: a design spacing read from a source,
a site-wide minimum, and a count that does not grow with the number of roads.

**WHAT A SOURCE WOULD SETTLE, NOT YET READ.** Sanitary manholes are spaced as
a maximum along a sewer run -- the Great Lakes "Ten States Standards" are the
usual citation for small sewers -- and storm inlets sit at low points and on
the upstream side of crosswalks, so water does not cross where people walk.
Both are to be read at source before a number is written down, as the hydrant
figure was. They are fill-ins: the walker's "usually on sidewalks" is the
look, and a reference answers only what it leaves open.

**WHO OWNS WHAT** (`USING_THE_FACTORY.md`):
  * **Zoo:** two species, a round cover and a rectangular grate, cast iron.
    The relief is geometry or a normal -- it is what reads at a glance.
  * **Pixelcoat:** cast iron and rust from the metal kinds that exist
    (`metal_bare`), the green paint as a decal at most.
  * **Lot:** placement, in `site_furniture`'s family, by the hydrant's shape
    of rule.

**ALREADY KNOWN, SO IT IS NOT RE-LEARNED.**
  * **Flush is a z-fight.** A cover coplanar with the sidewalk's top fights
    it, and the coplanar-faces gate counts exactly that (item 177). Stand it
    a few millimetres proud with a bevelled rim, or cut it in.
  * **A body walks over it.** No collision beyond the ground's own, and a few
    millimetres is far under any step limit (`site_steps`).
  * **The inlet's throat is the kerb.** An opening in the kerb face is Lot's
    kerb geometry, not a prop; a dark-faced piece standing against a solid
    kerb would read as the hole without being one, and costs nothing.
  * **Cost.** Few per site by construction -- the cap is the request. If they
    ride Patina's surface dressing they ride its MultiMesh: cold run 9146's
    export packed 4,241 dressing instances into 4 draw calls.
"""


def main():
    p = pathlib.Path(sys.argv[1])
    d = p.read_bytes()
    assert b"\r\n" not in d, "the roadmap is LF; a CRLF means something changed"
    s = d.decode("utf-8")
    assert s.count(ANCHOR) == 1, "anchor not found exactly once"
    assert s.endswith(ANCHOR), "item 178 is no longer the last thing in the file"
    assert "**179." not in s, "item 179 already exists"
    p.write_bytes((s + ITEM).encode("utf-8"))
    print("appended item 179 to", p)


if __name__ == "__main__":
    main()
