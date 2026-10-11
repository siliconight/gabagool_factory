"""Roadmap 241: an urban level type -- mid-rise street walls, chosen by the brief (the walker's call,
2026-10-11). Appends the item after 240 (asserting the roadmap still ends with 240's body); nothing
written on a miss. Run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_241_urban_type.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

TAIL_240 = ("**WHAT WOULD CLOSE IT.** Each build lands as a generator rule proven in a cold run with "
            "frames beside the comps, and the walker's eye on them; never a placement in a workspace.\n")
STATUS_241 = (
    "*STATUS: OPEN 2026-10-11 -- decided, not started. The walker chose a NEW URBAN LEVEL TYPE: a "
    "brief asks for an urban block, mid-rise Empties (5-12 storeys) form continuous street walls at "
    "the sidewalk line with the enterable buildings among them, and the Delco strip levels stay as "
    "they are (`docs/reference/URBAN_MIDRISE_COMPS.md`). Order: Deli Counter's mid-rise Empty family, "
    "Lot's urban layout, Level Factory's brief field, Lux's dusk haze, each priced.*")
ITEM_241 = """

**241. An urban level type: mid-rise street walls.** The walker, 2026-10-11, with three screenshots of another studio's game: "more around potential lot layout city building height". Read for scale and layout only (`docs/reference/URBAN_MIDRISE_COMPS.md`, screenshots not stored): mid-rise brick blocks of five to twelve storeys standing at the sidewalk line and touching, block after block, the skyline stepping up with distance; corner buildings with a lit shop at grade and homes above; four-lane streets with tree pits and signals at every corner; dusk haze as the depth cue. Every level the factory has made is a one- to three-storey Delco strip, buildings set back behind pads and parking with plate between them -- right for that place, and the library stands 3.2 to 13 m at the roof (two of 133 shells reach 12 m). Asked how the mid-rise city should come in, **the walker chose a new level type**: a brief asks for it, and the Delco strip stays.

**THE BUILD, IN ORDER.**
1. **Deli Counter: a mid-rise Empty family.** Non-enterable like the rowhome Empties, so a street of them stays cheap -- covers merged per side per material, dark inside, lit windows as paint: a brick block of five to twelve storeys with regular windows, a parapet and a rooftop penthouse; a corner variant with a shop at grade (lit, an awning, the invented brands); a bay-window variant. Heights drawn by cause (taller away from the action), never by jitter.
2. **Lot: the urban layout.** Zero setback: buildings at the sidewalk line, continuous along the block, the mission's enterable buildings standing among the Empties; a gap is an event (a fenced lawn, a lot); street trees in pits (roadmap 216's species); signals at every corner (Lot already resolves junction control).
3. **Level Factory: the brief that asks for it.** A field the brief sets (a site shape or a density word), planning the urban layout and the mid-rise Empties; absent, today's strip, byte for byte.
4. **Lux: dusk haze.** Depth fog, which GL Compatibility supports, priced at the fixed stations; lit ground floors.
5. **Priced and seen.** A ten-storey facade merges to an Empty's draws, but its lightmap area, shadows and texture memory (roadmap 238) grow with it: price it the cover merge's way, frames beside the comps, the walker's eye.

**RELATED.** Roadmap 240's parts (the pole line, stoops, silver roofs) serve both level types; 228's edge recipes gain taller massing for the urban one; 199 and 230 (the walkable-city brief, the adjacency guide) say what an urban block's routes and neighbours should be."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "\n**241. " not in text, "already applied"
    assert text.endswith(TAIL_240), ("the roadmap does not end with 240's body", text[-160:])
    text = text.rstrip("\n") + "\n\n" + STATUS_241 + ITEM_241 + "\n"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 241 appended after 240; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
