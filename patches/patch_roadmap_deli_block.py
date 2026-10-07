"""Roadmap: items 186 and 195 move on the deli block; items 196 and 197 are new.

    python patch_roadmap_deli_block.py

Anchored on the two status lines in full and on item 195's last line, as read
2026-10-07 (1,222,227 bytes, LF). Then run `tools/roadmap_status.py --write`
and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

S186_OLD = ("*STATUS: NARROWED 2026-10-06 -- the gas station and the convenience store are done and proven: "
            "Deli Counter 0.188.0, Zoo 1.75.0, Pixelcoat 0.58.0, Level Factory 0.146.0; cold runs 9181 (a "
            "never-seen one-building convenience store, generated) and 9182 (gas_block_001), both 0 "
            "interventions. The strip club's band no longer contradicts its neon (item 187's option D). "
            "FLAPPAHS is cream on green on every sign, the walker's call: Pixelcoat 0.60.0 draws the band in "
            "Zoo's colourway 0. No cold run has drawn a FLAPPAHS store since. Open: deli detail; the brief words "
            "still refused (`deli`, `night_deli`, `stop_n_go`, `corner_store`, `nightclub`).*\n")
S186_NEW = ("*STATUS: NARROWED 2026-10-07 -- the gas station and the convenience store are done and proven: "
            "Deli Counter 0.188.0, Zoo 1.75.0, Pixelcoat 0.58.0, Level Factory 0.146.0; cold runs 9181 (a "
            "never-seen one-building convenience store, generated) and 9182 (gas_block_001), both 0 "
            "interventions. The strip club's band no longer contradicts its neon (item 187's option D). "
            "FLAPPAHS is cream on green on every sign, the walker's call: Pixelcoat 0.60.0 draws the band in "
            "Zoo's colourway 0. THE DELI, done generated and drawn alike: its case stops at its wall (Deli "
            "Counter 0.199.0, item 195) and builds as Zoo 1.81.0's `deli_case` (curved glass, a lit deck of "
            "salads, cards and parsley, logs cut to the glass; Deli Counter 0.200.0 routes it), its front "
            "window hangs a beer neon over two taped posters (Deli Counter 0.201.0), and `deli`, `delicatessen`, "
            "`night_deli` and `stop_n_go` resolve (Level Factory 0.150.0). Cold run 9190 (restaurant_row_001, 0 "
            "interventions) stood the case in deli_a01 and priced it against the box it replaced: +1.0 draw a "
            "station, +0.017 ms median, under the controls' 0.084 ms spread. Cold run 9191 (deli_001, a "
            "never-seen one-building `deli` brief, generated, 0 interventions) built the case, the sign and the "
            "posters, framed from the street. Open: `corner_store` and `nightclub` stay refused by decision; "
            "furnish's wall pieces on open edges stand in front of the case (item 196); the generated deli's "
            "enemies jam at its rear door (item 197); the window neon reads faint behind its pane, the walker's "
            "to judge.*\n")

S195_OLD = ("*STATUS: NARROWED 2026-10-06 -- Deli Counter 0.199.0: layout_lint L25 (WARN) names every piece "
            "reaching past both faces of a wall the builder stands -- 19 pieces in 15 of 146 non-LF specs at "
            "0.198.0, 7 THROUGH a wall and 12 ALONG one; `presets.make` trims a recipe's piece through its own "
            "wall (the corner deli's case, the hospital's waiting seats) and `migrate_wall_crossing` trimmed the "
            "library's 7 (six deli cases to x -14.0..-8.185, warehouse's shelving run to x -4.0..7.84); both "
            "instruments read 12 in 8 specs after. Open: the twelve ALONG a wall, frozen in "
            "`wall_crossing_baseline.json`, each to be looked at; `casino_tower`'s generated basement vault "
            "block, centred on a partition; a level frame of the trimmed case.*\n")
S195_NEW = ("*STATUS: NARROWED 2026-10-07 -- Deli Counter 0.199.0: layout_lint L25 (WARN) names every piece "
            "reaching past both faces of a wall the builder stands -- 19 pieces in 15 of 146 non-LF specs at "
            "0.198.0, 7 THROUGH a wall and 12 ALONG one; `presets.make` trims a recipe's piece through its own "
            "wall (the corner deli's case, the hospital's waiting seats) and `migrate_wall_crossing` trimmed the "
            "library's 7 (six deli cases to x -14.0..-8.185, warehouse's shelving run to x -4.0..7.84); both "
            "instruments read 12 in 8 specs after. In a level: cold run 9190's composed deli_a01 stands the case "
            "at x -11.0925, the trimmed 5.815 m, and 9191's generated deli the same (`frame_9190_case_*.jpg`). "
            "Open: the twelve ALONG a wall, frozen in `wall_crossing_baseline.json`, each to be looked at; "
            "`casino_tower`'s generated basement vault block, centred on a partition.*\n")

TAIL = ("3. A level frame of the trimmed case, from the next cold run that draws a deli.\n")
TAIL_NEW = TAIL + '''
*STATUS: OPEN 2026-10-07 -- measured, not fixed: 155 of the library's 4,086 furnished wall pieces stand against a room edge with no built wall behind them, in 18 of 146 shells (`docs/findings/wall_pieces_without_walls/`); the generated deli does it too (cold run 9191's frame). The fix belongs in `level_design._wall_slots`.*

**196. Furnish stands wall pieces against walls that are not there.** Found 2026-10-07 framing the deli case in cold run 9190 (`docs/findings/wall_pieces_without_walls/`).

**WHAT WAS SEEN.** In deli_a01 an ATM and two paper lottery boards stood in front of the deli case's service front. The boards were hanging in mid-air. All three were wall pieces slotted against the customer floor's north edge, y -3.0, where no wall stands: the customer floor and the deli counter room meet across open floor.

**WHY.** `_wall_slots` offers a wall piece every edge of its room. It checks an exterior edge's openings and glazing; an interior edge it assumes is a wall and never asks whether a partition stands on it. Layout_lint L12 and L24 learned the open-floor rule in Deli Counter 0.197.0 (`tactical.shared_open_edge`); furnish never did.

**WHAT WAS MEASURED** (`wall_pieces_without_walls.py`, Deli Counter 0.201.0's specs). A wall piece is one `furnish` wrote whose stem `_PIECES` puts on a wall; a wall behind it is a built wall (`layout_lint.built_walls`) on its storey within 0.10 m of the edge it was slotted against, covering half its run.
- 155 of 4,086, in 18 shells, every one 0.18-0.19 m off its edge (`_wall_slots`' own spacing).
- The six delis 76 between them, apartment_walkup_a01 18, rowhouse_raid 17, office_stepped 8.
- Shelf runs 43, file cabinets 27, store poster boards 17, waiting chairs 10, service counters 10, vending 9, video poker 6.

**NOT ESTABLISHED.** How each reads in a frame (the deli's three are seen; the rest are counted), and whether every open edge in the list is meant to be open.

*STATUS: OPEN 2026-10-07 -- narrowed to one spot, not explained: in cold run 9191 every generated-deli candidate fails Laser Tag's ENEMY_PATHING_BROKEN, and 165 of seed_9191's 177 enemy-stuck events stand 1 m outside the recipe's 1.1 m rear staff door.*

**197. A generated deli's enemies jam at its rear door.** Found 2026-10-07 in cold run 9191, the first cold run of a generated corner deli (`docs/cold_runs/cold_9191/NOTES.md`).

**WHAT WAS MEASURED.**
- All three candidates fail `ENEMY_PATHING_BROKEN`: seed_9191 177 enemy-stuck events (1.18 per enemy per run, 19 timeouts in 25 runs), seed_9292 192 (20 timeouts).
- 165 of seed_9191's 177 stand at site (18-20, 0, -15): in the building's frame x 12-14, y +15, 1 m outside the north wall at and just east of `rear_staff_entry` (pos 0.32, x 12.0 as cut, 1.1 m wide). All six enemies jam there, the first at t 6.07 s. The site stands only the walk Lot lays to that door.
- The door is 1.1 m against the contract's 1.25 (`min_door_width`). Library deli_a01 has no rear door and 0 enemy-stuck events in 9190; deli_a03, whose rear door is 1.4 m, had 36.

**REFUTED, KEPT.** A floor safe flush against the north wall inside the door's span was the first suspect. It is the basement vault's (storey -1); the first filter took pieces by plan position without their storey.

**NEXT.** Bake 9191's walk-copy site and read the navmesh through the rear door, before any change to the recipe.
'''


def main():
    data = RM.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    for old in (S186_OLD, S195_OLD, TAIL):
        assert text.count(old) == 1, "anchor found %d times: %r" % (text.count(old), old[:70])
    assert text.endswith(TAIL), "item 195 is no longer the roadmap's last"
    assert "**196. " not in text and "**197. " not in text
    text = text.replace(S186_OLD, S186_NEW).replace(S195_OLD, S195_NEW)
    text = text[:-len(TAIL)] + TAIL_NEW
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 186 and 195 moved on; 196 and 197 appended; %d -> %d bytes"
          % (len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
