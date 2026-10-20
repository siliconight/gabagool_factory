"""Roadmap 210 NARROWED: every street phone faces the sidewalk and wears its own booth -- Lot 0.126.0, Zoo 1.116.0,
cold run 9351.

Anchored: the item's status block and the end of its body with the next item's status, read verbatim from the roadmap
when this was written, must each be there exactly once; nothing is written otherwise. Every line LF. Then
`python tools/roadmap_status.py --write` and `--check` regenerate and verify the index.

    python patches/patch_roadmap_210_facing.py
"""
import pathlib
import sys

ROADMAP = pathlib.Path(__file__).resolve().parents[1] / "PIPELINE_ROADMAP.md"
HEADING = '**210. Payphones: quarters and a steel cord.**'
EDITS = [("roadmap 210's status", '*STATUS: NARROWED 2026-10-19 -- THE WALKER\'S LOOK REVIEW: a street phone should "Always face the sidewalk" -- "the same same graffiti and drawing int he phone booth is too similar/uniform"; the lit booth at night "Looks right"; which level themes get phones: "you decide...we should have city, rural, special". Next: every street phone turned to the sidewalk (restaurant_row_001\'s faces the storefront behind it), the booth\'s graffiti seeded per phone, and a city / rural / special rule for where phones stand -- the factory\'s call, recorded when made. Earlier status kept: NARROWED 2026-10-09 -- the Zoo half, the light and the indoor form shipped. Zoo 1.88.0 redrew the payphone (cold run 9212). Zoo 1.89.0 lights it -- the header\'s face and a hood lamp\'s diffuser on a backlit atlas, `LuxEmit_payphone_hood` under the diffuser carrying its height above the ground -- Lux 0.70.0 spawns that lamp (`payphone_hood`, `REFERENCE_POOL` x 0.75 on the ground under it, set from frames of a lamp stood live in 9212\'s package), and Deli Counter 0.204.0 makes an indoor payphone a wall unit (39 payphones in 38 specs refurnished and rebuilt). Cold run 9213 (club_block_014, 0 interventions): three lamps spawned and baked; the booth\'s caller view at midnight 20.5 to 81.8 mean luma; priced against 9212 at 53 headings with no measurable frame cost, one draw per payphone in view, 0 over the paired 8-light cap. Open: Lot\'s placement by theme (the walker\'s call on which are city and urban), and the walker\'s eye on the lit booth.*\n\n', '*STATUS: NARROWED 2026-10-20 -- EVERY STREET PHONE FACES THE SIDEWALK AND WEARS ITS OWN BOOTH: Lot 0.126.0 (49dcf8d, `patches/patch_lot_stop_facing.py`) turns every piece at a bus stop toward the road from either kerb by the hydrant\'s rule -- `_stop_corner` had turned the payphone round on both kerbs and the mailbox and news racks on neither, so an L-kerb phone faced the wall behind it and an R-kerb mailbox and racks did -- and gives each payphone one of Zoo 1.116.0\'s four looks (3e811ec, `patches/patch_zoo_payphone_marks.py`: the tags inside the enclosure, their place and ink, and the stickers, drawn per variant; variant 0 the old booth byte for byte), picked by where it stands. Cold run 9351 (restaurant_row_001, seed 9003, 0 interventions, findings 108 -> 108): payphone_0L3 180 -> 0 and _1L3 270 -> 90, the road-2 mailbox and racks 90 -> 270, two booths in look 1; frames from the road side against 9350\'s (`docs/cold_runs/cold_9351/phones_9350_vs_9351.jpg`), the lit booths facing the street where 9350 showed their backs; priced against 9350 twice each, nothing this machine can see but 0.3 MiB. Left: the city / rural / special rule for where phones stand (the walker: "you decide"), the indoor wall units\' marks (Deli Counter\'s slots carry no variant), and the walker\'s eye. Earlier status kept: NARROWED 2026-10-19 -- THE WALKER\'S LOOK REVIEW: a street phone should "Always face the sidewalk" -- "the same same graffiti and drawing int he phone booth is too similar/uniform"; the lit booth at night "Looks right"; which level themes get phones: "you decide...we should have city, rural, special". Next: every street phone turned to the sidewalk (restaurant_row_001\'s faces the storefront behind it), the booth\'s graffiti seeded per phone, and a city / rural / special rule for where phones stand -- the factory\'s call, recorded when made. Earlier status kept: NARROWED 2026-10-09 -- the Zoo half, the light and the indoor form shipped. Zoo 1.88.0 redrew the payphone (cold run 9212). Zoo 1.89.0 lights it -- the header\'s face and a hood lamp\'s diffuser on a backlit atlas, `LuxEmit_payphone_hood` under the diffuser carrying its height above the ground -- Lux 0.70.0 spawns that lamp (`payphone_hood`, `REFERENCE_POOL` x 0.75 on the ground under it, set from frames of a lamp stood live in 9212\'s package), and Deli Counter 0.204.0 makes an indoor payphone a wall unit (39 payphones in 38 specs refurnished and rebuilt). Cold run 9213 (club_block_014, 0 interventions): three lamps spawned and baked; the booth\'s caller view at midnight 20.5 to 81.8 mean luma; priced against 9212 at 53 headings with no measurable frame cost, one draw per payphone in view, 0 over the paired 8-light cap. Open: Lot\'s placement by theme (the walker\'s call on which are city and urban), and the walker\'s eye on the lit booth.*\n\n'), ("the end of roadmap 210's body", "- **The walker's eye** on the lit booth and the wall units at midnight (`docs/cold_runs/cold_9213/payphone_*.png`).\n\n*STATUS: CLOSED 2026-10-08 -- Lot 0.98.2 reads", "- **The walker's eye** on the lit booth and the wall units at midnight (`docs/cold_runs/cold_9213/payphone_*.png`).\n\n**THE STREET PHONES FACE THE SIDEWALK, 2026-10-20** (Lot 0.126.0, Zoo 1.116.0; `patches/lot_stop_facing/`, `patches/zoo_payphone_marks/`, `docs/cold_runs/cold_9351/`). The walker's two notes from the look review. Each stop-corner piece stands 0.45 m in from the band's back edge, the sidewalk between it and the road, and each one's face is Zoo's -Y, which at the road's angle points at the road only from the L kerb; the hydrant had been turned by kerb since Lot 0.72.2 and the stop corner never was. A half turn keeps every footprint, so nothing else on a site moves. The booths' marks ride the kit's `variant`, as a box truck's fleet does: a level that uses a second look carries one more paint atlas (0.3 MiB measured on 9351), and draws do not change. Over three phones two drew the same look; a hash of place can repeat.\n\n*STATUS: CLOSED 2026-10-08 -- Lot 0.98.2 reads")]


def main():
    raw = ROADMAP.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("REFUSED: the roadmap has CRLF lines; nothing written")
    text = raw.decode("utf-8")
    for what, old, new in EDITS:
        if text.count(old) != 1:
            raise SystemExit("REFUSED: %s is there %d times, not once; nothing written" % (what, text.count(old)))
    for what, old, new in EDITS:
        text = text.replace(old, new)
    i = text.index(HEADING)
    if not text[:i].endswith(EDITS[0][2]):
        raise SystemExit("REFUSED: the status no longer adjoins its heading; nothing written")
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 210 updated; now tools/roadmap_status.py --write and --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
