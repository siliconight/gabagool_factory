"""Roadmap 148 NARROWED: every desk's screen is lit -- Zoo 1.115.0, Level Factory 0.224.0, cold run 9350.

Anchored: the item's status block and the end of its body with the next item's status, read verbatim from the roadmap
when this was written, must each be there exactly once; nothing is written otherwise. Every line LF. Then
`python tools/roadmap_status.py --write` and `--check` regenerate and verify the index.

    python patches/patch_roadmap_148_screens.py
"""
import pathlib
import sys

ROADMAP = pathlib.Path(__file__).resolve().parents[1] / "PIPELINE_ROADMAP.md"
HEADING = '**148. Nothing dresses the inside of a building: no posters, clocks, vents,'
EDITS = [("roadmap 148's status", '*STATUS: NARROWED 2026-10-19 -- THE WALKER\'S LOOK REVIEW: the rooms "Too sparse" -- "these are ultimately shooting galleries for a video game, but the rooms still feel sparse and boring....computer screens hsould be on...bring life to this dead world". Next: denser rooms from the kinds already made, and every desk\'s screen lit. Earlier status kept: NARROWED 2026-10-15 -- re-measured on cold run 9314\'s package and Zoo\'s recipes (`docs/findings/open_items_remeasure/`, `interior_dressing_148.py`). Of the ask\'s seven kinds, two exist as species -- posters (`poster`, `poster_wall`, on four wall kinds since 2026-10-02) and garbage (`litter_bin`, `litter_scrap`, `trash_bags`) -- and they reach rooms by Deli Counter\'s furnish recipes, a slot at a time: 9314\'s deli carries 22 prop species including three poster walls and two litter bins, the pharmacy three poster walls and a bin, the office its desks, cabinets and machines and none of the asked kinds. Left: no species for a clock, a ceiling vent (`vent_stack` and `exhaust_fan` are roof pieces), a smoke detector, a light switch or an exit sign; interior litter is a bin, not a scatter; and the no-collision interior dressing LAYER this item names -- one MultiMesh over a room\'s walls and ceiling, placed by a rule on room roles -- is not built. Whether a room reads as inhabited is the walker\'s eye.*\n\n', '*STATUS: NARROWED 2026-10-20 -- EVERY DESK\'S SCREEN IS LIT: Zoo 1.115.0 (9e8c9bc, `patches/patch_zoo_desk_screens.py`) puts a screen on every monitor `_surface_stock` stands on a desk or a cubicle bank\'s work surface -- six invented 1997 office screens (a word processor, a spreadsheet, a desktop, a terminal, an amber bulletin board, a starfield), painted in pure Python with the bar TV\'s tube, on a backlit `_Face` atlas Lux\'s power cut finds by name, the app named by where the monitor stands; a kit A/B against 1.114.1 found the screen\'s art moving the rest of a top\'s stock (a cubicle bank lost a workstation), fixed before it shipped: every 1.114.1 mesh now rebuilds unchanged to its positions\' hash. Level Factory 0.224.0 keeps each module\'s screens a mesh of their own where they stood and merges the rest of the desk. Cold run 9350 (restaurant_row_001, seed 9003, 0 interventions, findings 108 -> 108): 18 screen meshes, the office\'s 9 desks and 6 cubicle banks and deli_a03\'s 3 desks; frames from six stations at the desks and the cubicles against 9349\'s (`docs/cold_runs/cold_9350/office_9349_vs_9350.jpg`); priced at 53 headings against 9349 re-merged the same way, twice each: 1 to 14 more draws at the 18 headings that moved and none elsewhere, the frame time inside the controls\' 0.224 ms floor, 0.2 MiB, the meshes over the 8-light cap the control\'s 9. Left: denser rooms from the kinds already made; a clock, a ceiling vent, a smoke detector, a light switch and an exit sign, which no species draws; the no-collision dressing layer; and whether a room reads as inhabited, the walker\'s eye. Earlier status kept: NARROWED 2026-10-19 -- THE WALKER\'S LOOK REVIEW: the rooms "Too sparse" -- "these are ultimately shooting galleries for a video game, but the rooms still feel sparse and boring....computer screens hsould be on...bring life to this dead world". Next: denser rooms from the kinds already made, and every desk\'s screen lit. Earlier status kept: NARROWED 2026-10-15 -- re-measured on cold run 9314\'s package and Zoo\'s recipes (`docs/findings/open_items_remeasure/`, `interior_dressing_148.py`). Of the ask\'s seven kinds, two exist as species -- posters (`poster`, `poster_wall`, on four wall kinds since 2026-10-02) and garbage (`litter_bin`, `litter_scrap`, `trash_bags`) -- and they reach rooms by Deli Counter\'s furnish recipes, a slot at a time: 9314\'s deli carries 22 prop species including three poster walls and two litter bins, the pharmacy three poster walls and a bin, the office its desks, cabinets and machines and none of the asked kinds. Left: no species for a clock, a ceiling vent (`vent_stack` and `exhaust_fan` are roof pieces), a smoke detector, a light switch or an exit sign; interior litter is a bin, not a scatter; and the no-collision interior dressing LAYER this item names -- one MultiMesh over a room\'s walls and ceiling, placed by a rule on room roles -- is not built. Whether a room reads as inhabited is the walker\'s eye.*\n\n'), ("the end of roadmap 148's body", 'chain, one species placed by one rule, and a walk that finds a room\nreading as inhabited rather than modelled.\n\n*STATUS: CLOSED 2026-09-12 -- COLD RUN 9009 PLACED A BANK FIRST IN ALL\n', "chain, one species placed by one rule, and a walk that finds a room\nreading as inhabited rather than modelled.\n\n**THE SCREENS ARE ON, 2026-10-20** (Zoo 1.115.0; `patches/zoo_desk_screens/`, `docs/cold_runs/cold_9350/`). The look review's second ask, done in the species that already stood in every office: a monitor's dark glass carries an art quad 2.5 mm proud of it, painted from one atlas of six screens a kit, lit, and named `_Face` so the power cut takes it with the lights. Not this item's dressing layer: the screens are part of the desk's own module, one more mesh for each module with a monitor. Copies of one module show its one app; 9350's office stood 9 desks on 7 modules. The atlas packer stacks the six apps in one column and leaves half of its image empty.\n\n*STATUS: CLOSED 2026-09-12 -- COLD RUN 9009 PLACED A BANK FIRST IN ALL\n")]


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
    print("roadmap 148 updated; now tools/roadmap_status.py --write and --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
