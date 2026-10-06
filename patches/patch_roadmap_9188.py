"""PIPELINE_ROADMAP.md after cold run 9188, Lot 0.97.3, Deli Counter 0.191.0 and
0.192.0, and Level Factory 0.149.0:
- 177 NARROWED: the gates are read now, item 192.
- 191 CLOSED: 9188 measured Lot 0.97.3 for regressions, and found none.
- 192 new: the presentation gates were read for one building in sixteen, and
  the circulation gate could not pass.
- 193 new: pieces over openings and on stair walks, and nothing asks again.

Run `tools/roadmap_status.py --write` then `--check` after.

    python patch_roadmap_9188.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ROADMAP = ROOT / "PIPELINE_ROADMAP.md"

OLD_177 = '''*STATUS: OPEN 2026-09-23 -- THE GATE HAS FAILED ON EVERY COLD RUN REPORTED AS
CLEAN. `presentation_compose` exits 3 with "z-fight gate [FAIL]" and the word
ERROR on 9072 (107 coplanar pairs / 363 solids), 9073 (72/283), 9075 (44/300),
9076 (130/594) and 9077 (79/525). All five were reported as zero-intervention
runs. Nothing blocks, nothing is read, and no item tracked it until now.*
'''
NEW_177 = '''*STATUS: NARROWED 2026-10-06 -- the gates are read now, and one could not pass (item 192). The z-fight gate became a finding for ONE building (roadmap 133), and since Level Factory 0.149.0 for every building a level places: cold run 9188 recorded deli_a01 200 pairs, office 121 and rail_station_a02 117, where 9187 recorded deli_a01's alone. The circulation gate failed on every building of every run from 9164 to 9187, on merged cover boxes, and reached no finding; with Deli Counter 0.191.0, 9188's compose exited 0 for the first time. Open: the z-fight pairs themselves, on three of 9188's fifteen buildings.*
'''

OLD_191 = "*STATUS: NARROWED 2026-10-06 -- fixed at the source in Lot 0.97.3, not yet run in a level. Every `UNREACHABLE_SPAWN` refusal in cold runs 9164 to 9186 -- four, on two candidates -- was an enemy Lot's spawn placer pushed inside an Empty, which it could not see. 0.97.3 keeps every spawn out of the blockers and every enemy out of the band behind an Empty row's front line, the ground its fences shut off. With the collision reading Lot passes, 0.97.2 reproduces every shipped enemy on six candidates; 0.97.3 moves 9186's Enemy_5 out of e9 to 1.33 m clear of the row, moves 9174's two out of e15 and the band to open ground (pushed 50.0 and 45.0 m), and moves no enemy on any candidate of 9178 or 9187. A fixture test on 9186's site as drawn fails four of five on 0.97.2. Open: a cold run on 0.97.3.*\n"
NEW_191 = "*STATUS: CLOSED 2026-10-06 -- Lot 0.97.3 keeps every spawn out of the blockers and every enemy out of the band behind an Empty row's front line, the ground its fences shut off. Every `UNREACHABLE_SPAWN` refusal in cold runs 9164 to 9186 -- four, on two candidates -- was an enemy Lot's spawn placer pushed inside an Empty, which it could not see. With the collision reading Lot passes, 0.97.2 reproduces every shipped enemy on six candidates; 0.97.3 moves 9186's Enemy_5 out of e9 to 1.33 m clear of the row and 9174's two out of e15 and the band (pushed 50.0 and 45.0 m). A fixture test on 9186's site as drawn fails four of five on 0.97.2. Cold run 9188 (restaurant_row_001, 0 interventions) measured it for regressions: every enemy of its three candidates stands where 9187's did, as the measurement before the run said.*\n"

OLD_191_OPEN = "**OPEN.** A cold run on Lot 0.97.3. It will move no enemy on restaurant_row_001's current candidates, so that run measures for regressions; it is not a proof of the fix.\n"
NEW_191_OPEN = "**MEASURED IN A LEVEL, cold run 9188** (`docs/cold_runs/cold_9188/NOTES.md`). 0 interventions. Every enemy of the three candidates stands where 9187's did. Laser Tag reads identically on seed_9003 and seed_9104; seed_9205 went 0.88 -> 0.84 completion, WARN either way, its deli_a03 refurnished by item 193. No current draw puts an enemy where 0.97.3 would move it, so the proof of the fix stays the fixture test.\n"

ITEMS = """
*STATUS: NARROWED 2026-10-06 -- read, honest, and proven in a level. Level Factory 0.149.0 reads every placed building's compose package, names the building in each finding, and turns the circulation gate into one (`PRESENTATION_CIRCULATION`); Deli Counter 0.191.0 boxes a dressing's parts, not its merged nodes, and excuses a stair's own guards. Cold run 9188 (0 interventions): compose exited 0 where every run from 9164 to 9187 exited 6; `PRESENTATION_ZFIGHT` 1 -> 3 (office and rail_station_a02 had been failing unread); no circulation finding -- the gate's one real finding on 9187's buildings, deli_a01's counter island over its stairwell, moved with item 193. Open: a walkable piece at a door reads as a conflict, and the z-fight pairs themselves (item 177).*

**192. The presentation gates were read for one building in sixteen, and the circulation gate could not pass.** Found 2026-10-06 checking item 177 against the runs since (`docs/findings/presentation_gates/`).

**WHAT WAS MEASURED.**
- `presentation_compose` composes the mission's own shell and every building of a varied lot, and `job.log` keeps only the last command's lines: gs_empty_rowhome_l's "63 solids" on every run that draws it.
- Level Factory's adapter read `next(...)` of 16 sorted manifests, which is lot/deli_a01's. In 9187 z-fight failed on deli_a01 (203 pairs), office (121) and rail_station_a02 (117); one was recorded.
- No branch read `circulation_check`. The driver printed "0 prop conflict(s) across ? circulation volume(s)" from the top of Deli Counter's two-arm schema: a FAIL with nothing in it, exit 6 on every run from 9164 to 9187, each counted clean.
- **The dressing arm could not pass.** It boxed each node, and since Zoo 1.68.0 merged covers per side per material a node's box is the building's (6.7 x 7.1 x 12 m on gs_empty_rowhome_l). Every doorway lay inside one: 9, 48, 28 and 27 conflicts on four buildings. The dressing layer is non-collision by construction.
- The shell arm read a stair's own fall guards as props in its column (office's `stair_guard_back_10`, 0.26 m), and found one real defect: deli_a01's counter island 0.8 m inside its up-stair (item 193).

**REFUTED, KEPT.** Index connectivity without welding returns one component per FACE (1,452 planes on gs_empty_rowhome_l). A plane has zero thickness, and `_pen` can never flag it: 0 conflicts for the wrong reason.

**WHAT SHIPPED.**
- Deli Counter 0.191.0: `dressing_part_boxes`, position-welded index-connected parts, 123 to 249 a building; a 1 m crate planted in a doorway is still caught, at 0.95 m. `GUARD_PREFIX` is excused from stair volumes only, and listed.
- Level Factory 0.149.0: `_placed_manifests` reads each lot building's package, and the root only when there is no lot (a lot's root is the mission shell, not placed); every finding names its building; `PRESENTATION_CIRCULATION` (moderate) and `PRESENTATION_MANIFEST_UNREADABLE`; the driver prints each arm.

**PROVEN, cold run 9188** (`docs/cold_runs/cold_9188/NOTES.md`): compose exit 0; the circulation line reads its arms; `PRESENTATION_ZFIGHT` 1 -> 3, each named; no circulation finding.

**OPEN.**
- A walkable piece at a door: twin_a01's porch deck and stoop read 0.2 m into its front doorways' volumes, and the shell arm fails it. The gate has no notion of a piece being walked on.
- The z-fight pairs on deli_a01, office and rail_station_a02 (item 177).

*STATUS: NARROWED 2026-10-06 -- the rule exists and 17 pieces moved; 47 are frozen, 30 of them over AUTHORED openings that furnish cannot see. Layout lint L23 (Deli Counter 0.192.0) asks every piece whether it stands over a slab opening or in a stair's walk on its own storey: 64 pieces in 18 of 146 shells. `migrate_stale_pieces.py` moved 17 in 10 shells by each piece's own placement rule and refurnished each spec -- deli_a01-a03's counter islands and crate stacks, twin_a01's wardrobes (0.190.0's wider flights had put them over the hole) and five small ones; every nav-gate verdict is as before, themed fitness unchanged at 102 of 127, and in cold run 9188 deli_a01's circulation conflict is gone. `stale_pieces_baseline.json` freezes 47 in 8 shells and fails a new one. Open: furnish and seed_cover check stairs, not authored `slab_holes`; cbp_town_finale's and final_stand's tables stand inside 28 x 22 m and 10 x 8 m openings with nothing declared under them.*

**193. Pieces stand over openings and on stair walks, and nothing asks again.** Found 2026-10-06 by item 192's restored circulation gate (`docs/findings/presentation_gates/`, `stale_pieces.py`).

**WHAT WAS MEASURED.**
- 64 pieces in 18 of 146 shells over a slab opening or in a stair's walk on their own storey: 55 over a hole, 17 in a walk.
- Two causes the census cannot tell apart:
  - STALE. The presets, `seed_cover` and `furnish` clear a piece of the stairs when they place it, and each is idempotent by name, so a piece placed before a stair changed is never asked again. deli_a01-a03's counter islands date from 0.80.0, and the stair's default run has lengthened since. **0.190.0's wider flights put twin_a01's two wardrobes 0.12 m2 each over its hole**: measured on 0.189.0's spec and on 0.190.0's. Its swept gate passed it, because walking is unaffected and nothing checked pieces against openings.
  - UNSEEN. `furnish` and `seed_cover` clear the stairs (`_stair_reserved_rects`), not an authored `slab_holes` opening. apartment_walkup_a01's dining set over a 2 x 2 m authored hole comes back on every refurnish.
- 12 shells have authored `slab_holes`, and 30 of the 47 frozen pieces stand over one. In cbp_town_finale and final_stand they stand at their storey's floor height with nothing declared under them.

**REFUTED, KEPT.**
- Moving apartment_walkup_a01's dining set: it is furnish's, and the refurnish puts it back.
- A migration that did not refurnish: moving deli_a01's islands changes where furnish lays its hall, and `test_club_fixtures`' fixed point failed on deli_a01.
- A 6 m reach left four pieces unplaced; 12 m placed them all.
- Two storey rules: the census's round put a hung sign on the storey above, and a floor put final_stand's `boss_desk`, 5 cm under storey 2's floor line, on storey 1. `piece_story` takes the nearest floor within a slab (0.25 m) and floors anything else.
- The census's first run filed every landing rect under the stair's lowest storey: `stair_endpoints` carries no storey.

**WHAT SHIPPED, Deli Counter 0.192.0.** L23 (WARN); `level_design.reseat_piece`; `_seed_clear_doors`, the seeder's door rule in one spelling; `migrate_stale_pieces.py`, which moves and then refurnishes; `stale_pieces_baseline.json`, 47 in 8 shells, each with why; `test_stale_pieces.py` (11).

**MEASURED.** The nav gate on all 11 shells rebuilt reads as 0.191.0's did; the circulation gate's shell arm is clean on the delis; themed fitness 102 of 127; cold run 9188, 0 interventions.

**OPEN, IN ORDER.**
1. `furnish` and `seed_cover` keep off an authored `slab_holes` opening on the room's storey (`_seed_clear`), then the four shells are refurnished. Look at cbp_town_finale's storey-1 tables in a frame first.
2. A furnish SET -- a table and its chairs -- moves together, not a piece at a time.
3. The rest of the frozen list, case by case: foundry's skylight box and roof AC, the garages' columns, final_stand's statue and covers.
"""


def main():
    text = ROADMAP.read_bytes().decode("utf-8")
    assert "\r\n" not in text, "the roadmap is LF; CRLF here means it changed under us"
    assert "**192." not in text and "**193." not in text, "an item already exists"
    for old, new in ((OLD_177, NEW_177), (OLD_191, NEW_191), (OLD_191_OPEN, NEW_191_OPEN)):
        n = text.count(old)
        assert n == 1, ("anchor matched %d times" % n, old[:80])
        text = text.replace(old, new)
    assert text.endswith(NEW_191_OPEN), "the roadmap no longer ends with item 191"
    ROADMAP.write_bytes((text + ITEMS).encode("utf-8"))
    print("PIPELINE_ROADMAP.md: 177 NARROWED, 191 CLOSED, 192 and 193 added")


if __name__ == "__main__":
    main()
