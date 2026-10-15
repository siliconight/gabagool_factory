"""Roadmap 250 to 255, 2026-10-14 late: the walk's findings 5 and 7-9 fixed and proven (Deli Counter 0.221.0 and
0.222.0, cold runs 9311 and 9312), and three items filed -- the walker's two asks of the evening and the check that
generalises finding 5.

- 250: status rewritten (5 and 7-9 fixed); a FIXED paragraph before its Left; its Left rewritten for what remains.
  Both old lines are pinned by sha16 of the text read in this session, so nothing else can be replaced.
- 253, new, OPEN: flag assets as looking good or needing love (the walker's ask).
- 254, new, OPEN: a contract language for Level Factory's data (pinned for later by the walker).
- 255, new, OPEN: a partition that stops short of where its rooms meet.

The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_250_255.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import hashlib
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
OLD_STATUS_SHA = "fb06fd8268c6335b"
OLD_LEFT_SHA = "3a0101301c160166"

S250 = (
    "*STATUS: NARROWED 2026-10-14 -- THE WALKER'S WALK OF COLD RUNS 9305-9307, NINE FINDINGS BY EYE. 1-4 fixed in the "
    "tools and run fresh for the walker's demo, 0 interventions each: Zoo 1.111.0 (9176f8d) and 1.112.0 (8d1e2a4), "
    "Level Factory 0.211.0 (5c67868); cold runs 9308-9310. 5 and 7-9 fixed after it, each the walker's call: Deli "
    "Counter 0.221.0 (33e6866f) stands a cut switchback's second flight on the stair's lowest floor and closes the "
    "walkway's mouth with a back -- \"fill the stairs to the ground\", 14 shells; 0.222.0 (6c312336) runs the delis' "
    "basement divider wall to wall and gives the utility room a door from the corridor -- \"close the basement\", "
    "and the door, by the walker's 2026-10-06 rule for a room reached only by breaching. Cold runs 9311 "
    "(restaurant_row_001) and 9312 (urban_row_001), 0 interventions each, findings unchanged, every grade held; seen "
    "at the walker's spots in the inspection light. Open: 6, a `floor_hole` cut bare (144's residue); 8's storey-1 "
    "guard rail, still crossing the void seen from below; two taste calls (`docs/findings/walk_2026-10-14/`).*")

FIXED = (
    "**FIXED, 2026-10-14 late: 5 and 7-9** (`patches/patch_dc_fill_to_ground.py`, `patch_dc_basement_wall.py`, each "
    "with its folder; `docs/cold_runs/cold_9311/`, `cold_9312/`; `docs/findings/walk_2026-10-14/`: "
    "`core_9311_sheet.png` against `core_9310_sheet.png`, `basement_9312_sheet.png` against `basement_9308_sheet.png`). "
    "**Deli Counter 0.221.0** (33e6866f): `stairwell.flight_solid_base` stands a cut multi-storey switchback's filled "
    "second leg on the stair's lowest floor, unless something else opens that floor under its run; the builder "
    "stands each tread's column and collider there, every other leg's numbers 0.220.0's floats; `stair_guards` gives "
    "the second run a back from leg 1's foot to the arrival edge, closing the walkway 0.134.0 had kept open as a "
    "passage, and the two tests that pinned it changed with it. `build.py --all` moved exactly the 14 shells' GLBs. "
    "**Deli Counter 0.222.0** (6c312336): `presets.corner_deli` and `migrate_basement_wall.py` run the divider -19..19 "
    "in all six delis, the door and breach where they were built (-8.5, 7.0). Wall to wall it left the utility "
    "room's two breach panels -- solid, with colliders -- its only ways in, which `test_walk_reach` refused under "
    "layout_lint L24; asked again, the walker chose a door from the corridor, midway between that wall's breach and "
    "the divider, y -4.0, and the rooms reached only by breaching are then exactly the baseline's four server rooms. "
    "The refurnish moved deli_a03 alone, one chair set at the vault's count table. **The cold runs:** 9311 "
    "(restaurant_row_001, office and deli_a03) held every grade, its walked candidate's fields moving by hairs; 9312 "
    "(urban_row_001, deli_a01 and, unannounced in its own batch description, the office) held every grade, its "
    "walked candidate PASS 100 with 10 of 32 fields moved -- survival 52.40 -> 55.61 s, deaths 13 -> 12 -- the two "
    "changes together. **Seen:** the stair core one solid block where the walker saw a slot, the second flight's "
    "mass down to the floor; the basement divider unbroken to the outside wall, the vault walled off from the utility "
    "room, and the utility room's new door.")

LEFT = (
    "**Left:** 6, a design call -- dress the hole as deliberate, trim and a guard, or as damage, its gameplay role "
    "kept; 8's storey-1 guard rail across the hole's south edge, still read from below as a rail across the void, for "
    "the walker's eye now that the core is solid; and two taste calls for the walker -- whether the door's trade sign "
    "should wear the band's colours, yellow on black, rather than its own, and whether a corner shop's window wants "
    "depth, a redrawn pane or a shallow interior, priced first. The backdrop's ground went out unpriced (252); the "
    "check that would have caught finding 5 is 255.")

S253 = (
    "*STATUS: OPEN 2026-10-14 -- THE WALKER'S ASK: \"I want a way to flag assets that look good and assets that need "
    "more polish/love\". Proposed: two keys in every walk copy recording the asset under the crosshair, the verdict and "
    "a frame into a ledger the factory reads. Not started; the shape is the walker's to confirm.*")
H253 = (
    "**253. Flag assets as looking good or needing love.** The walker, 2026-10-14, after the demo: \"I want a way to "
    "flag assets that look good and assets that need more polish/love...\". It is roadmap 18's missing gate from the "
    "walker's side: today a look is judged in chat, frame by frame, and nothing keeps the verdicts. **PROPOSED, not "
    "started:** in every walk copy, debug builds only like F3 and the work light, G marks what the crosshair rests on "
    "as looking good and P as needing love. Each press resolves the asset the debug overlay's ray hit -- a Zoo "
    "species by its GLB's name, a Deli Counter building and slot, a Lux fixture, a Lot prop -- and writes the verdict, "
    "the asset, the level and cold run, the camera and a frame to a flags file beside the copy, a banner confirming "
    "it; `tools/asset_flags.py` gathers the walk copies' flags into one tracked ledger per asset. **What it feeds:** "
    "\"needs love\" a ranked queue for the asset work; \"looks good\" what a change must show the walker before and "
    "after it moves, the walker's taste overriding an art audit. **Known gaps:** the physics ray misses a visual-only "
    "mesh -- the fire escape has no collider -- so a render-side pick by bounds; and the keys see only what a walk "
    "passes, so a review board over every species would be the systematic sweep. **WHAT WOULD CLOSE IT:** the walker "
    "flags assets on a walk and the ledger names each rightly, its frames beside it.")

S254 = (
    "*STATUS: OPEN 2026-10-14 -- PINNED FOR LATER BY THE WALKER: \"we'll want a contract language like protobufs for "
    "level factory...a pin in it\". Not to be started without the walker's go.*")
H254 = (
    "**254. A contract language for Level Factory's data.** The walker, 2026-10-14, after asking whether Level "
    "Factory's configuration is all JSON: \"for later later....we'll want a contract language like protobufs for "
    "level factory...a pin in it\". **Measured that evening:** the data that drives a level is JSON -- briefs, batches, "
    "every job's manifests and reports, the approvals, Deli Counter's 446 building specs and `agent_contract.json`, "
    "Zoo's genomes -- with three JSON Schemas (`level_factory/schemas/mission.brief.schema.json`, "
    "`surface_dressing.v1.json`, Deli Counter's `schema/level.schema.json`) and versions as strings "
    "(`level_factory.batch.v0.1`, `level_factory.perf_stations.v1`); the tuning is about 330 module-level constants in "
    "58 Python files of Level Factory's packages; the workspace's job index is SQLite; scenes and resources are "
    "Godot's own text formats. **Why it would matter:** the deliverable is a pipeline strangers point at their own "
    "game, and typed, versioned contracts between the tools keep a reader from guessing a shape -- this repo's rule "
    "against writing a checker to a guessed schema is the same lesson. **WHAT WOULD CLOSE IT:** the walker's go, then "
    "a language chosen and a first contract, the brief, generated and checked on both sides.")

S255 = (
    "*STATUS: OPEN 2026-10-14 -- FOUND TRACING THE WALK'S FINDING 5. A partition that stops short of where the rooms "
    "it divides meet leaves an opening no spec names: 59 stretches over 1 m in 31 of 446 specs before Deli Counter "
    "0.222.0 closed the delis', 33 in 20 after, 24 in 14 in the library itself. Proposed: a layout_lint advisory "
    "naming each unless the spec names the gap, today's sorted by a person.*")
H255 = (
    "**255. A partition that stops short of where its rooms meet.** Found tracing 250's finding 5 "
    "(`docs/findings/walk_2026-10-14/partition_gaps.py`): two rooms on one storey MEET along a partition's line where "
    "one's bound is the line on one side and the other's on the other, and wherever such a meeting runs past the "
    "partition's ends by more than 1 m that stretch has no wall, and no spec names it as an opening. **Measured:** 59 "
    "such stretches in 31 of 446 specs (`partition_gaps.out.txt`); after Deli Counter 0.222.0 closed the delis' "
    "basements, 33 in 20 (`partition_gaps_after_0222.out.txt`), 24 of them in 14 library specs -- rowhouse_raid's and "
    "apartment_walkup_a01's basements and ground floors, the auto shops' upper storeys, the parking garages' decks, "
    "the warehouses' north aisles, office's executive lobby, and corner_deli_heist_01's subdivided cold storage. Some "
    "read as designed openness, some as 250's defect again; the census names no cause. **WHAT WOULD CLOSE IT:** a "
    "`layout_lint` advisory naming each stretch unless the spec names the gap -- an opening of its own kind, or the "
    "rooms declared one space -- with each of today's 24 sorted by a person and closed or named.")

NEW_ITEMS = "\n" + "\n\n".join([S253, H253, S254, H254, S255, H255]) + "\n"


def _sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def _span(text, number):
    h = text.find("\n\n**%d. " % number)
    assert h > 0, ("no item", number)
    s = text.rfind("\n\n*STATUS:", 0, h)
    e = text.find("\n\n*STATUS:", h)
    return s, h, (e if e > 0 else len(text))


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "\n\n**253. " not in text, "already applied"
    s, h, e = _span(text, 250)
    old_status = text[s + 2:h]
    assert _sha(old_status) == OLD_STATUS_SHA, ("250's status is not the text read", _sha(old_status))
    body = text[h:e]
    lefts = [ln for ln in body.split("\n") if ln.startswith("**Left:** 5, traced (")]
    assert len(lefts) == 1 and _sha(lefts[0]) == OLD_LEFT_SHA, ("250's Left is not the text read", len(lefts))
    for block in (S250, FIXED, LEFT, NEW_ITEMS):
        for line in block.splitlines():
            if line.startswith(("**253. ", "**254. ", "**255. ")):
                continue
            assert not re.match(r"\*\*\d+\.", line), ("a body line would parse as an item", line[:40])
    new_body = body.replace(lefts[0], FIXED + "\n\n" + LEFT, 1)
    text = text[:s + 2] + S250 + new_body + text[e:]
    assert text.endswith("\n")
    text = text + NEW_ITEMS
    for number, head in ((250, "*STATUS: NARROWED 2026-10-14 -- THE WALKER'S WALK"),
                         (253, "*STATUS: OPEN 2026-10-14 -- THE WALKER'S ASK"),
                         (254, "*STATUS: OPEN 2026-10-14 -- PINNED FOR LATER"),
                         (255, "*STATUS: OPEN 2026-10-14 -- FOUND TRACING THE WALK'S FINDING 5")):
        s, h, e = _span(text, number)
        assert text[s + 2:].startswith(head), (number, "status does not adjoin its heading", text[s + 2:s + 80])
        assert "\n\n" not in text[s + 2:h], (number, "a blank line inside the status")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 250 updated (5 and 7-9 fixed); 253, 254 and 255 filed; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
