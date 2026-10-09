"""Roadmap 217 and 218 after cold runs 9215 and 9216, and 219 appended: the walker's
twelve walk notes of 2026-10-09.

217: the sky in the bake proven cold; the moon trial refused on look.
218: CLOSED -- Level Factory 0.163.1's import pass ran cold twice.
219: the walk of 2026-10-09, each note with its owner and the cause found.

A status line is replaced whole: the one line that starts with its unique opening, asserted to
be exactly one. Item 219 is appended after the file's last line, asserted to be 218's. Then:

    python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

S217_START = "*STATUS: NARROWED 2026-10-09 -- the instruments exist, the street lamps are dark by day, and the sky is in the bake."
S217_NEW = (
    "*STATUS: NARROWED 2026-10-09 -- the instruments exist, the street lamps are dark by day, and the sky "
    "is in the bake, proven cold. Root tools `light_breakdown.py`, `light_check.py` and `lux_rebake.py` "
    "measure a level by source, by room and street against named floors, and at any slot by an exact "
    "re-bake. Lux 0.71.0 darkens poles and wall packs under the four day presets, proven in cold run 9214 "
    "(0 interventions): a hidden lamp is not baked (wall pack 002's wall 32.5, against 48.0 with the lamps "
    "forced on), and the lamps move the check's 23 stations by 0.2 or less. Level Factory 0.164.0 bakes the "
    "sky at the walker's word (\"yes bake the sky in\"), proven in cold runs 9215 (bank_block_001, Heavy "
    "Rain, within 0.1 of the re-bake trial) and 9216 (card_block_001, a clear afternoon), 0 interventions "
    "each: against 9216's own sky-off control the extraction rose 65.6 to 79.9 and the elevations +1.9 to "
    "+6.4, every room 1.2 or less, and shade lost its bounce-only orange. Heavy Rain's shadowless sun still "
    "lights rooms through their roofs (12 of 16 interior stations outshine its street; 7 with the shadow "
    "on), a trade Lux 0.38.0 made on a price that predates the bake and the merges. A baked moon (\"bake the "
    "moon, see how it looks\") stopped the night seep into distant rooms but took a third off the street "
    "and the trees' shadows (trees are kept dynamic and cast none into a bake): refused on look, and the "
    "cull-mask split is the fix proposed for both leaks. "
    "Open: the walker's calls on Heavy Rain's sun and the moon, where the night boost lives, and morning and "
    "noon presets.*\n"
)
S218_START = "*STATUS: NARROWED 2026-10-09 -- shipped, not yet run cold. Level Factory 0.163.1"
S218_NEW = (
    "*STATUS: CLOSED 2026-10-09 -- the import pass checks its own work, proven cold. Level Factory 0.163.1 "
    "counts a model imported once its sidecar's `dest_files` are there, repeats a short pass up to 3 times, "
    "keeps every pass's exit code and output in `<package>.import.log` beside the package, and stops the "
    "export on a pass that never completes. Cold runs 9215 (bank_block_001) and 9216 (card_block_001), 0 "
    "interventions and 0 retries each, carry the log with both passes complete (`import pass 1: exit 0`, "
    "`import pass 2: exit 0`); the repeat itself is covered by `test_a_pass_that_imports_no_model_is_run_again` "
    "(8 of the 9 tests fail on 0.163.0). Why cold run 9214's first pass imported 0 of 425 models is not "
    "established; the next short pass will leave its output.*\n"
)

LAST = ("- **The occluder bake still says `ok` on a scene with no modules.** The import check now stops the "
        "export before it can, but the bake cannot tell an empty site from an unloadable one.\n")

ITEM_219 = r"""
*STATUS: OPEN 2026-10-09 -- twelve notes from the walker's walk of club_block_014 (cold run 9213, midnight), each filed with its owner and the cause found by reading the code; one decided (Blue Highway for the shop signs), none fixed yet. The quick ones go first, each with a test that fails without it: the news racks, the meters, the antennas, the sign face, the signals and the den windows; then the club's light, the moon, the two placeholders and the bags; then the perimeter and the backdrop, as a menu with frames.*

**219. The walk of 2026-10-09: twelve notes.** The walker walked club_block_014 (cold run 9213, midnight) and sent notes with screenshots, closing with "i think that's enough for this round, thank you". Two more came after. Owners and causes were found by reading the code; nothing is changed yet. The notes' own record is the memory note `walk-feedback-2026-10-09`.

| # | the note | owner | the cause |
|---|---|---|---|
| 1 | "strip club is still a tad too dark ... dark and moody, but lit enough for a player to see and experience it" (comps: VtMB, KOTOR 2) | Lux | Dens of sin get no bake fills (Lux 0.68.2); the club is lit by washes in pools. Measured, luma after the grade: our club frame mean 1.8, median 1, 98% under 10; the comps mean 36 to 43, median 15 to 39, 19 to 40% under 10. |
| 2 | den windows get curtains, drapes or blinds: "people outside can't see in, and you keep the streetlight light out" | Deli Counter (Zoo paints the states) | No rule covers a den's windows; strip_club_a01's are clear glass. `empty_panes.py` already chooses curtain, blind and shade states for the Empties. |
| 3 | "far too many" rowhome antennas and dishes, "perhaps 30% as many" | Deli Counter specs | Authored per house: 10 fixtures on 9 of the 12 `gs_empty_rowhome_*`, and every copy of an archetype repeats its roof. |
| 4 | parking meters face the sidewalk | Lot | `site_furniture.plan_meters` turns every meter +90 degrees on both kerbs, so its face looks along the street. |
| 5 | "i dont know what this giant grey box is" | Zoo | `box_truck` is still a placeholder silhouette, one solid box; `litter_bin` is the only other one. Both ship in club_block_014. |
| 6 | newspaper boxes through a pole and the bus shelter | Lot | `plan_furniture` adds the bus stop's pieces to `out` but not to `placed`, so `_stop_corner`'s `_free` cannot see them. A nudge stood one rack 0.11 m from the flag post and another over the shelter's end. |
| 7 | moonlight seeps into distant rooms and goes as you approach | Lux (Deli Counter and Level Factory for a layer split) | Delco Night's `sun_shadow_max_distance = 30.0`. Past it the moon is unshadowed and lights rooms through their roofs, seen down the airport terminal's 38 m corridor. A baked moon was tried and refused on look (item 217). |
| 8 | a diegetic perimeter that keeps the collision and the signal | Lot, Zoo | The `perim_*` edges are bare walls. A menu with frames is owed. |
| 9 | traffic signals light every lens; two heads on a pole must match | Zoo (a small cycle at run time) | `traffic_signal` lights all three lenses. One lit lens a head, synced per approach, the cross street opposite. |
| 10 | "need better looking fonts on these signs" | Pixelcoat | `core/signage.py` sets every sign in Pixel Operator on a 16 px grid, thresholded for the nearest filter. DECIDED, the walker: "use Blue Highway for the shop signs". |
| 11 | filled black garbage bags stacked by the bins | Zoo, Lot | A new species and its placement beside the dumpsters (one a building) and the cans. |
| 12 | something past the sky's horizon, "to make the level not look like it's literally floating in space" | Lot, Zoo | Nothing stands beyond the perimeter. `docs/reference/PENNSYLVANIA_BACKDROP_WORLDS_GUIDE.md` was filed for this. Goes with 8. |
"""


def _replace_line(text, start, new):
    lines = text.split("\n")
    hits = [i for i, ln in enumerate(lines) if ln.startswith(start)]
    assert len(hits) == 1, (start[:60], len(hits))
    lines[hits[0]] = new.rstrip("\n")
    return "\n".join(lines)


def main():
    data = ROADMAP.read_bytes()
    assert b"\r\n" not in data, "the roadmap is LF; found CRLF"
    text = data.decode("utf-8")
    assert "**219. " not in text, "already applied"
    assert text.endswith(LAST) and text.count(LAST) == 1, "the roadmap no longer ends with item 218's last line"
    text = _replace_line(text, S217_START, S217_NEW)
    text = _replace_line(text, S218_START, S218_NEW)
    text = text + ITEM_219
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap: 217 updated, 218 closed, 219 appended")


if __name__ == "__main__":
    main()
