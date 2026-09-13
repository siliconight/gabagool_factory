"""Roadmap batch 61, 2026-09-13 (evening): item 155 appended -- the walker's
first in-game feedback rounds, every finding triaged with its owner and how
much of its cause is MEASURED versus SUSPECTED. Asserts the item is new.
"""
import io
import sys

P = "PIPELINE_ROADMAP.md"

APPEND = """

*STATUS: NARROWED 2026-09-13 (evening) -- THE WALKER PLAYED THE LEVEL, AND
SIX OF TWENTY-ONE FINDINGS ARE FIXED. The first two rounds of feedback from
walking a generated package in Godot (cold runs 9045, 9046, 9048). Fixed, each
measured and shipped: stairs a body can climb, solid stair undersides with a
toggle, chairs facing their table, ladders climbable in walk copies, and the
debug overlay in walk copies. The rest are triaged below with what is known
about each cause and what is only suspected. Nothing marked suspected has
been measured; do not build on it before it is.*

**155. The walker played a generated level, and the list of what a person
finds in five minutes is longer than anything a gate found in a week.** Two
rounds on 2026-09-13, from cold runs 9046 and 9048's walk copies. This item
is the ledger, so none of it is lost to a transcript; each entry names the
tool that owns it.

FIXED.

1. **"cant get up the steps"** (Deli Counter 0.124.0). 61 of 148 shipped
   flights were over the 45 degrees a CharacterBody3D stands on; the bake
   allows 55, so every nav gate passed. Flights are capped at 40 and
   lengthened to 38 (`stair_pitch`); 112 lengthened, 25 re-seated. The known
   contract tension CLAUDE.md names, found by a person on a screen.
2. **"stairs should have a solid bottom to the ground"** (DC 0.124.0). Treads
   are columns to the floor where nothing of the stair is below. Then the
   walker asked for it as a gameplay lever -- "a toggle we flip on and off if
   we want more sightlines" -- which is DC 0.125.0: per stair, per building,
   per build (`DC_STAIR_UNDERSIDES`), default solid, reported to gameplay.json
   as `stair_systems[].underside`.
3. **"chairs should face each the table"** (DC 0.124.0). `Volume.rot_z`, and
   `_fit_rotation` keeping a slot's own rotation on a tie -- a square chair
   always came out at 0 before.
4. **"I can't get up this ladder, we have made successful ladders in the
   past"** (factory `tools/walk_export.py` + `tools/walk_ladders.gd`). The
   package carries ladder MARKERS; the climb Area3D is the consumer's to build,
   Lot's walk scene builds it, and `walk_export` never did. Every ladder in
   every walk copy was scenery. Verified headless: 3 volumes built for the 3
   ladder anchors in 9048. The climb itself is Lot's existing code.
5. **"didnt we have a debug overlay that showed coordinates"** (same tool).
   Level Factory's `debug_overlay.gd` (position, building under the crosshair,
   surface and distance; F3) rode in `walk_themed.py` and not in
   `walk_export.py`. It does now, in the walk copy only. The walker's rule,
   recorded: F3 toggles it, it is for debug builds only, and player exports
   will never have it. STILL TO DO: an `OS.is_debug_build()` guard inside the
   overlay so a release export of a walk project drops it too.
6. **Film emulsion** -- a question, answered: off. The package runs Lux's
   Delco Summer Afternoon preset; film needs three keys and the preset's is
   false, as in every preset Lux ships.

DIAGNOSED BY READING THE CODE, NOT YET FIXED.

7. **Two stop signs at a crosswalk, facing across the sidewalk** (Lot).
   `site_furniture` gives any kerb cut `>= DRIVEWAY_WIDTH` (3.5 m) a stop sign
   as a parking-lot exit, and Level Factory's door-to-street spurs are
   `SPUR_WIDTH` 4.0 m -- so every footpath crossing is treated as a driveway
   and signed on both sides. The walker supplied the placement rule to build
   to (MUTCD): one sign per approach on the driver's RIGHT, at least 6 ft
   from the pavement edge, no more than 50 ft from the intersection, about
   4 ft before a marked crosswalk, a second sign on the left only for wide or
   multi-lane approaches.
8. **"Chairs shouldnt face walls like this where humans couldnt sit in them"**
   (DC `furnish`). Wall-placed seating (`chair_waiting`) gets no `rot_z`, so a
   waiting row stands against a wall with its seats toward the wall.
9. **"the metal pole of a stop sign goes behind the face of it"** (Zoo
   `stop_sign`). In the walker's frame the pole stands in front of the plate;
   the plate also carries no STOP lettering. Reference photo supplied.
10. **"NOthing in the cabinets"** (Zoo `shelving`). The recipe builds empty
    shelves; there are no contents.
10a. **"why the paint on the pavement has the look of identical blotches
    missing?"** (Pixelcoat `road_paint_delco`). The wear is a `cutout` mask
    (fbm, 3 cells, threshold 0.4) on a pack whose `meters_per_tile` is 0.5,
    so the same handful of holes repeats every half metre down every stripe
    of every crosswalk. The same lesson as the concrete cracks in item 45: a
    sparse feature in a tiling texture advertises the tile. The wear has to
    vary at a scale much larger than the paint's own tile.

SUSPECTED, NOT MEASURED -- the first thing to do with each is look.

11. **"these wheels jitter whn i walk past them"** (Zoo `simple_car`).
    Suspect coplanar faces (hub against tyre, tyre against body) z-fighting.
12. **"the safe details on the front are jittering"** (Zoo `drop_safe`).
    Suspect the dial and handle boxes are flush with the door face.
13. **"What are these boxes that are the same texture as the wall?"** (DC).
    Suspect cover or shelter pieces whose names route to no species
    (`crate_stack`, `planter_box`, `kiosk`) and so wear the building's
    `default_material` as a plain box.
14. **"Getting some fizziness from this texture"** (Pixelcoat / import).
    Suspect per-pixel `hash_grain` in the micro band shimmering under a
    nearest filter as the camera moves.
15. **"Interesting circular lighting on the corrugated steel"** -- the walker
    did not say whether it is wanted. Suspect specular rings from a
    posterized normal map under omni lights. Ask before changing.
16. **White boxes at the foot of the stop signs** in the same frame.
    Unidentified; the overlay now names what the crosshair is on.
17. **"you can see the seams here"** -- thin light and dark vertical lines
    where modular wall segments meet, beside a window (DC modular walls /
    import). Suspect either a real gap between tiles or the texture's edge
    sampled at each tile's UV border under a nearest filter.

A READABILITY RULE THE WALKER STATED, and the finding behind it.

18. **"the chairs being the same texture as the floor and walls almost make
    them invisible ... The collision is correct, but it should look like a 3d
    object that looks different from the ground and wall so I can see them
    from a distance"** (DC `furnish`, and a rule for every prop). `furnish`
    writes no `material`, so every piece takes the building's
    `default_material` -- the walls' own skin. The rule to hold: a solid a
    body can walk into must contrast with the floor and the wall behind it.
    That is measurable (a luminance or hue difference between a prop's skin
    and the surfaces around it) and nothing measures it yet.

DESIGN WORK.

19. **"this bank teller booth should connect and be locked to the public ...
    a section where only employees can be there and enter/exit, we only have
    the front of the teller windows"** (DC bank archetypes). The teller line is
    a free-standing counter front; a bank needs the staff side enclosed, with
    a locked employee door, so the public side and the staff side are two
    places.
20. **The "13" frame: a large opening to a lower level, stair placement that
    needs to be thicker, and a door opening that does not look right** (DC).
    A stair's slab hole reads as an unguarded pit, and the stair inside it
    reads thin against it. Locate it with the overlay before diagnosing.

**WHAT WOULD CLOSE THIS:** every entry above fixed or explicitly declined by
the walker, and a walk of a fresh cold package that raises none of them
again.
"""


def main() -> int:
    raw = io.open(P, "rb").read()
    if b"\r\n" in raw:
        print("roadmap has CRLF endings -- stop", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    if "**155. " in text:
        print("refusing: item 155 already exists", file=sys.stderr)
        return 1
    if "**154. " not in text:
        print("refusing: item 154 is not where this expects it", file=sys.stderr)
        return 1
    text = text.rstrip("\n") + "\n" + APPEND.rstrip("\n") + "\n"
    out = text.encode("utf-8")
    io.open(P, "wb").write(out)
    print(f"wrote {len(out)} bytes ({len(raw)} before); 155 appended")
    return 0


if __name__ == "__main__":
    sys.exit(main())
