"""Roadmap: item 198 (night interiors, closed) and item 199 (the walkable-city
brief, open).

    python patch_roadmap_night_and_brief.py

Appends both after item 197, anchored on the file's last line in full, as
read 2026-10-07 (1,228,143 bytes, LF). Then run `tools/roadmap_status.py
--write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

TAIL = ("**NEXT.** Bake 9191's walk-copy site and read the navmesh through the rear door, before any change "
        "to the recipe.\n")

ADD = """
*STATUS: CLOSED 2026-10-07 -- cold run 9193 (0 interventions, findings 64 -> 64, Laser Tag identical): restaurant_row_001's 16 fluorescent rooms 15.5 -> 39.2 mean luma and its 8 bulb-lit rooms 3.8 -> 23.4 against 9190's shipped bake of the same draw, rooms with half the frame under 10 from 14 and 8 to 1 and 1. Lux 0.67.0 hangs a bare bulb's lamp under its glass (33 rigs); Lux 0.68.1 and Level Factory 0.151.0 bake room fills (267) and ship none; Lux 0.68.2 keeps a den of sin's whole building unfilled (club_block_014: strip_club_a02 back to its shipped dark room for room).*

**198. Baked interiors are darker than their lamps say.** Found 2026-10-07 from the walker: "a lot of our interiors are quite dark when the sun isn't up ... this can be intentional in dive bars, strip clubs, and other 'dens of sin' but otherwise we should aim to give the humans enough light to signify the surroundings" (`docs/findings/night_interiors/`).

**WHAT WAS MEASURED.** One station a room (`night_interior_census.py`), cold run 9190's restaurant row at Blue Hour: baked 15.5 / 3.8 mean luma (16 fluorescent / 8 bulb-lit rooms) against 24.3 / 17.5 for the same level lit live. The light bake (Level Factory 0.131.0, on by default since 0.144.0) had been priced and compared outdoors only.

**THE TWO CAUSES.**
- A lightmapped surface takes its light from the lightmap alone, so the room probes' ambient floor (Lux 0.38.0) reached no wall or floor: raised five-fold on all 24 probes, it moved no room.
- Every steady bare bulb sat inside its own glass: Zoo's `pendant_fixture` reaches 0.15 of a radius below its anchor and Lux hung the lamp at the anchor. The floor under the deli counter's bulb read 0.9 baked against 40.4 live. That is the defect the street poles had (Lux 0.65.0).

**WHAT SHIPPED.**
- Lux 0.67.0: `BULB_LAMP_DROP_M` (0.022, derived).
- Lux 0.68.x and Level Factory 0.151.0: `add_bake_fills` lays static omnis over every untinted room probe, one per 6 m cell at 1.7 m, 0.025 each (`LuxPreset.bake_room_fill`), reaching 1.5 cells flat, half in a bulb-lit room. The bake lays them before it presses Bake and frees them before it saves, so nothing ships.

**REFUTED, KEPT.**
- Three earlier layouts (in the loader): one centre fill a room sat on the centre bulb's anchor, inside its glass; a room's energy split across cells left big rooms dark.
- 0.68.0's unowned fill: LightmapGI skips a child with no owner, and the first real bake baked none of 267.
- A first fixture control read 0.00: its cameras stood at x 0, from `global_position` read before the tree ran.

**NOT ESTABLISHED.**
- The office lobby (14.0) and the rail concourse (16.6) are dark floors: in the lobby the fill lifted the ceiling 16 codes and the carpet 2.4.
- The derived spawn shot reads 0.8 in every variant (camera 3 cm inside the lobby's west edge).
- Lamps that hang AT their anchor on other hardware (club neon, back bar, stage, canopy wash, sign) are unchecked.
- Window spots ship at 3.0 at every hour; at midnight they moved club_block_014's rooms 0-0.9.
- Per time of day: the walker set five slots (morning, high noon, afternoon, evening, midnight) whose preset should carry each one's floor.

*STATUS: OPEN 2026-10-07 -- filed, not compared: the walker's Dynamic Walkable City brief (`docs/reference/DYNAMIC_WALKABLE_CITY_LEVEL_DESIGN_BRIEF.md`), the companion of the land-use guide Lot already builds to, "should be placed and inform future Lot layout". Nothing has been measured against it yet.*

**199. Lot's layout against the walkable-city brief.** Filed 2026-10-07 at the walker's word, during the night-lighting block: "I know we are focused on lighting right now, please continue, but this should be placed and inform future Lot layout".

**WHAT IT ASKS.**
- A hub central in movement, not geometry.
- At least three approaches that differ in exposure, distance, height or access.
- Loops: a short loop near the hub, a long route around its most exposed ground, a shortcut with a readable cost, and recovery from a blocked edge.
- Dead ends only with a purpose, and edges explained rather than clipped.
- Height changes that join real route nodes at both ends.
- Neighbours with a shared reason, and a landmark hierarchy revealed in sequence.
- Validation in three tiers: hard failures, design warnings, and a traversal review per entry point (fastest, safest, elevated, service, and one blocked edge).

**WHAT IT TOUCHES THAT EXISTS.**
- `MissionBrief.road_grammar` and `route_shape` (a T or a crossroads).
- Laser Tag's route findings and route completion.
- `tools/landuse_census.py`, and the land-use guide's parcel and open-space accounting.

**NEXT.** Map the brief's hard failures and design warnings onto those gates one by one, and measure the gap on a few briefs before any layout changes.
"""


def main():
    data = RM.read_bytes()
    assert len(data) == 1228143, "roadmap is %d bytes, read at 1,228,143" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.endswith(TAIL) and text.count(TAIL) == 1, "the tail anchor is not the file's end"
    text = text + ADD
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 198 and 199 appended; %d -> %d bytes" % (len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
