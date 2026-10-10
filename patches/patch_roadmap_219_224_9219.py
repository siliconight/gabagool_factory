"""Roadmap 219 and 224: cold run 9219 proves note 5 (Zoo 1.92.0, Lot 0.103.0), and files 224, the
blotches the bake's bounce leaves on a large pale face.

The 219 status line and note 5's row are each replaced whole: the one line that starts with its
unique opening, asserted to be exactly one. Item 224 is appended after 223, the last item. Then:

    python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

S219 = "*STATUS: NARROWED 2026-10-10 -- eight of the twelve notes fixed, seven PROVEN on the walked level"
N219 = (
    "*STATUS: NARROWED 2026-10-10 -- eight of the twelve notes fixed and PROVEN on the walked level, "
    "club_block_014 at seed 9181 by night. Six were proven together in cold run 9217 (0 "
    "interventions, 0 retries, findings 72 to 71 against 9213): notes 6 and 4 (Lot 0.102.1 and "
    "0.102.2), 3 (Deli Counter 0.204.1), 10 (Zoo 1.90.0), 9 (Level Factory 0.165.0) and 2 (Zoo "
    "1.91.0's drape, hung by Deli Counter 0.205.0). Note 1, the club's light, was proven in cold "
    "run 9218 (0 interventions, 0 retries, findings 71 to 71): Lux 0.72.0's wall washers and "
    "tinted fill. Mean and median luma at the room stations: the main floor 3.7 and 1 to 14.5 and "
    "8, the VIP wing 2.2 and 0 to 12.9 and 7, the bar 3.1 and 1 to 17.1 and 9 "
    "(`docs/cold_runs/cold_9218/`). Note 5 was proven in cold run 9219 (0 interventions, 0 "
    "retries, findings 71 to 71): the site's one truck ships as Zoo 1.92.0's cab-over in fleet 2, "
    "the variant Lot 0.103.0 picked where it stands, and its litter bin as the drawn street bin "
    "(`docs/cold_runs/cold_9219/truck_and_bin.png`). At midnight the truck reads by its shape and "
    "lamps; its livery is lost in the moon's shadow, where the bake's bounce lies in blotches "
    "(item 224). Still the walker's: the brighter fill, and the club's office-tile ceiling. Next: "
    "note 11, the bags; then the perimeter and the backdrop as a menu with frames. The moon waits "
    "on the walker.*"
)

S5 = "| 5 | \"i dont know what this giant grey box is\" |"
R5_OLD = "FIXED in Zoo 1.92.0, not yet run cold: the box truck is"
R5_NEW = "FIXED in Zoo 1.92.0 and PROVEN in cold run 9219: the box truck is"
R5_END_OLD = "so a lot's trucks differ. |"
R5_END_NEW = ("so a lot's trucks differ. In 9219 the site's one truck shipped as fleet 2, NANA'S "
              "BASEMENT SELF STORAGE, and at midnight it reads as a truck by its shape and lamps; "
              "its livery is lost in the moon's shadow (item 224). |")

LAST_223 = "It is a one-word fix with the next Pixelcoat release.\n"
ITEM_224 = """
*STATUS: OPEN 2026-10-10 -- found in cold run 9219: a large pale face lit only by the bake's bounce carries blotches. The box truck's side at midnight, in the moon's shadow, runs from luma 1 to 6 (p5 to p95 after an 8 px blur, median 2), and with the lightmap switched off it is black all over, so the blotches are the bake's. Not yet measured: the bake at a higher quality.*

**224. Blotches in the bake's bounce on a large pale face.** `docs/cold_runs/cold_9219/box_side_bake.png`. Cold run 9219's box truck (Zoo 1.92.0, fleet 2) stands with its box's sides away from the moon. In its shadow the sides are lit by the bake's bounce alone, and the bounce lies on them in light and dark blotches about half a metre across.
- **Measured** on `look_shots`' frame from 8 m, the walk copy at midnight: over the box's face, after an 8 px blur, luma p5 1, p50 2, p95 6 of 255.
- **The control:** `look_shots --switch-off lightmap` at the same station. The face is black all over, so the blotches are in the lightmap.
- **Not the art:** Blender's render of the same fleet from the same code shows a clean white box with faint grime (`box_truck_v2_blender.png` beside the notes).

**Why it is small today.** At midnight the face is near black anyway, median 2, and the blotches show only in a brightened frame. It would matter on a face lit by bounce alone in a level by day, or at a brighter night. The old box truck was one grey box, and its sides were never framed close.

**The first suspect is the bake's own setting.** Level Factory's `light_bake.py` bakes at `QUALITY = 0`, Low, with 2 bounces and the denoiser on: "quality Low (0) baked the lot in 22 s and is what was priced". A low sample count, denoised over a weak bounce, leaves blotches of this kind. Not yet looked at, in this order:
1. **Re-bake 9219's walk copy at Medium and High,** with the box face's p5 to p95 and the bake's time at each. The time is the price: the bake runs once per export, not per frame, so it costs the pipeline, not the player.
2. **A prop's lightmap texel density,** which sets how many texels a 6 m face gets.
3. **Whether every pale face in shadow does it:** a white wall in the moon's shadow would show the same, and a census by surface would say.

Owner: Level Factory for the bake's settings and the import. Nothing changes until one of these has been measured.
"""


def main():
    data = ROADMAP.read_bytes()
    assert b"\r\n" not in data, "the roadmap is LF; found CRLF"
    text = data.decode("utf-8")
    assert "**224." not in text, "224 is already filed"
    assert text.endswith(LAST_223) and text.count(LAST_223) == 1, repr(text[-80:])
    lines = text.split("\n")
    hits = [i for i, ln in enumerate(lines) if ln.startswith(S219)]
    assert len(hits) == 1, ("219 status", len(hits))
    lines[hits[0]] = N219
    rows = [i for i, ln in enumerate(lines) if ln.startswith(S5)]
    assert len(rows) == 1, ("note 5's row", len(rows))
    row = lines[rows[0]]
    assert row.count(R5_OLD) == 1 and row.endswith(R5_END_OLD), row[-120:]
    lines[rows[0]] = row.replace(R5_OLD, R5_NEW)[: -len(R5_END_OLD)] + R5_END_NEW
    out = "\n".join(lines) + ITEM_224
    ROADMAP.write_bytes(out.encode("utf-8"))
    print("roadmap 219: note 5 proven in 9219; 224 filed")


if __name__ == "__main__":
    main()
