"""PIPELINE_ROADMAP.md after cold run 9186 and Deli Counter 0.190.0:
- 189 stays NARROWED. 9186 proved its gate and walk test. twin_a01 is fixed
  by the flight width, and the fridge that was blamed is refuted and kept.
- 190 is new: the ledge at the head of every stair, trimmed at the source in
  0.190.0. The sink that came first is refuted and kept, and a level run is
  still owed.

Run `tools/roadmap_status.py --write` then `--check` after.

    python patch_roadmap_190.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ROADMAP = ROOT / "PIPELINE_ROADMAP.md"

OLD_189 = "*STATUS: NARROWED 2026-10-06 -- the gate and the walk test shipped. Deli Counter 0.189.0's nav gate bakes each shell again at eight grid origins and calls a shell not navigable when a stair, or an interior marker the base bake reached, connects at only some -- and Level Factory's themed-lot selection reads `navigable`, so such a shell leaves the draw (fit 102 -> 101: twin_a01, the twin family's only shell; no brief names that family). deli_a03's stair door widens to 2.4 m and connects at 8 of 8, gate and census agreeing; seven shells are frozen in `navgate_baseline.json` `grid_fragile`. Lot 0.97.2's walk test decides ladder access from the anchor's column, not from Godot's fallback, and passes 9185's seed_9003 as 9179 did. Located: five real floor necks (stair discharges against walls, a fridge at a stair top, a door half inside a wall, a cover pocket); in nine shells the floor holds and only the marker's snap moves. Open: fix the five, twin_a01's fridge first; have the gate test the base bake's standing point rather than re-snap; the register markers inside their counters.*"
NEW_189 = "*STATUS: NARROWED 2026-10-06 -- the gate and the walk test shipped and are proven, and twin_a01 is fixed. Deli Counter 0.189.0's nav gate bakes each shell again at eight grid origins and calls a shell not navigable when a stair, or an interior marker the base bake reached, connects at only some -- and Level Factory's themed-lot selection reads `navigable`, so such a shell leaves the draw. deli_a03's stair door widens to 2.4 m and connects at 8 of 8, gate and census agreeing. Lot 0.97.2's walk test decides ladder access from the anchor's column, not from Godot's fallback. Cold run 9186 (restaurant_row_001, 0 interventions) passed both deli_a03 candidates that 9185 dropped, with Godot's path error 0 times in their logs against 10 and 9, and `WALKTEST_ANCHOR_ISOLATED` 2 -> 0 -- and exposed item 190. Deli Counter 0.190.0 draws no flight narrower than a corridor (`presets.STAIR_FLIGHT_WIDTH`, 1.2 m: the contract's 1.1 m corridor and a bake cell): twin_a01's 0.9 m flights tore at one origin in eight, not its fridge, and at 1.2 m it connects at 8 of 8. Fit 102 -> 101 -> 102 of 127; six shells frozen in `navgate_baseline.json` `grid_fragile`. Open: four located floor necks (foundry_heist_vertical's and primos_pizza's stair discharges, a door half inside a wall, a cover pocket); have the gate test the base bake's standing point rather than re-snap; the register markers inside their counters.*"

LINE_REFUTED_LAST = "  - Lot's first fix asked for the single point closest to the anchor's column, which is always the floor under its own foot: it failed a drop off the deli's upstairs edge, 2.7 m out, that the old rule passed. The shipped one samples the column height by height inside the old window."
ADD_REFUTED = "- **That twin_a01's fridge pinched its stair**, this item's first OPEN entry. `fridge_right_0` stood nearest where the route tore, at the top of `stair1` beside its guard rail. Built in scratch with all four tall pieces against the end walls (`twin_exp`), the shell still connected at 7 of 8. The flight itself was 0.9 m, which leaves one cell after the bake's erosion; at 1.2 m with the furniture untouched it connects at 8 of 8, gate and census."

LINE_SHIPPED_LAST = "- **Lot 0.97.2, the walk test.** `_vertical_access` samples the anchor's column, nearest height first, inside the old concession's window (1.5 x SNAP_MAX across, more than 1 m up or down), and accepts a surface a strict route reaches. On a copy of 9185's seed_9003 the walk test passes as 9179's did; `home` and `proxy_1` now agree."
ADD_SHIPPED = (
    "- **Cold run 9186 proved both** (restaurant_row_001, 0 interventions; `docs/cold_runs/cold_9186/NOTES.md`). Both deli_a03 candidates passed the walk test, the objective on the main network by its stairs rather than passed as VERTICAL access. Godot's path error fired 0 times in their logs, against 10 and 9 in 9185, and `WALKTEST_ANCHOR_ISOLATED` went 2 -> 0. Laser Tag then dropped seed_9003 at the head of the deli's up-stair: item 190.\n"
    "- **Deli Counter 0.190.0, the flight width.** `presets.STAIR_FLIGHT_WIDTH` is the contract's corridor minimum (`min_corridor_width_m`, 1.1: twice the bake radius and 0.3) and one bake cell, 1.2 m. `twin` and `rowhome` drew 0.9 m flights, `pawn_shop` and `suburban_safehouse` 1.0 m; all four draw it now. twin_a01's frozen spec stands on it, with the reason on each stair's `meta` as `width_why`. The library's 1.0 and 1.1 m flights (cr_pawn, night_pawn, card_shop_a01) connect at 8 of 8 as built and keep their specs. Baseline `grid_fragile` 7 -> 6: twin_a01 leaves, and primos_pizza's list gains `patrol_point_PAT_CLUB`, which its base bake reaches through the trimmed ramps, at 6 of 8 like its stair. Fit 101 -> 102 of 127."
)

OLD_OPEN_1 = "1. **Fix the five located floor necks.** twin_a01 first: `fridge_right_0` pinches the top of `stair1` beside its guard rail, and twin_a01 is its family's last fit shell. Then foundry_heist_vertical's and primos_pizza's stair discharges against their north walls; cbp_town_finale_midbalanced_schemafixed's 2.0 m `third_vomitory` door, half inside the west wall; bank_job's 1 m pocket between a crate stack and a desk."
NEW_OPEN_1 = "1. **Fix the four located floor necks left.** twin_a01's is done (Deli Counter 0.190.0, above). foundry_heist_vertical's and primos_pizza's stair discharges against their north walls, both in the gate's `grid_fragile`; then two the census finds and the gate does not flag: cbp_town_finale_midbalanced_schemafixed's 2.0 m `third_vomitory` door, half inside the west wall, and bank_job's 1 m pocket between a crate stack and a desk."

LAST_LINE = "3. **The register markers** stand inside their counters. Placed on the floor beside the counter, the question ends at the source.\n"

ITEM_190 = """
*STATUS: NARROWED 2026-10-06 -- fixed at the source, not yet proven in a level. Deli Counter 0.190.0 trims every stair ramp's head onto its landing (`stairwell.ramp_head_trim`). Rebuilt, 0 of 174 ramps stand over their landing (all 174 stood 0.19 to 0.21 m over it before); a capsule of Laser Tag's size goes down deli_a03's up-stair in 2.4 s and up in 3.8 s, where as built it stuck on the landing for the full 8 s going down; and the swept gate traverses every stair in 144 of 144 shells. The first fix, sinking each ramp, passed the census and the walk and failed the gate on 94 of 144: kept below. Open: a cold run in which Laser Tag's route through deli_a03's stair completes (9186's seed_9003: 0 of 25 runs, 3,148 stuck events in one cell).*

**190. Every stair's collision ramp stood a riser above the landing it delivers to.** Found 2026-10-06 in cold run 9186, the first run whose bots reached deli_a03's upper floor (item 189; `docs/cold_runs/cold_9186/NOTES.md`, and the stair-head sections of `docs/findings/stairwell_on_one_grid_in_four/README.md`).

**WHAT WAS MEASURED.**
- 9186's seed_9003 went out on Laser Tag's `LT_ROUTE_NEVER_COMPLETED`: its bots walked 70% of the route and finished 0 of 25 runs. Players stuck 3,148 times, every one in a single 2 m cell: deli_a03's upper landing at the head of its up-stair, local (-12, 3.3, -6.99). The route goes up to the objective and has to come back down.
- **The census** (`ramp_ridge_census.py`): every stair collision ramp in the library, 174 in 98 shells, topped out 0.19 to 0.21 m above the floor it delivers to. That is the top face's end corner, `step_rise/2 + (thickness/2) * cos(pitch)` over the landing: the half-step-proud offset that makes a ramp ride the nosings, and half the slab through the tilt. `ramp_foot_extension` (2026-07-21) landed the foot and said it left the head.
- **The walk** (`stair_head_walk.gd`, `run_stair_head_walk.py`): a capsule of Laser Tag's size (r 0.35, h 1.8, no step-up, `floor_max_angle` 45) on deli_a03's up-stair. As built: down stuck on the landing for the full 8 s; up arrived. With the ramp lowered one riser, the control: down in 2.4 s, up in 3.8 s.

**WHY NEITHER INSTRUMENT SAW IT.** Going up, the ledge is a drop, which any body takes. Coming down, it is a 0.2 m riser. The navmesh climbs 0.15 and Lot's walkers step 0.5, while a capsule walks up about 0.10 unassisted (`unassisted_step_max_m`). It sits in the band CLAUDE.md's known contract tension names, between what the navmesh routes and what a body walks.

**REFUTED, KEPT.**
- **Sinking every ramp by the overshoot** (`stairwell.ramp_head_drop`; `patches/patch_dc_ramp_head.py` and its tests, both headed SUPERSEDED). Built, it read 0.000 on the census and walked both ways. The swept nav gate then failed stair traversal on **94 of 144** shells: the ramp ran a riser under the nosings, every visual tread stood above it, and the nav bake reads visual meshes -- the gate's and the site's alike -- and saw 0.206 m risers against a 0.15 climb. The census and the walk had measured collision only. Reverted before release.

**WHAT SHIPPED.** Deli Counter 0.190.0, `stairwell.ramp_head_trim`:
- The head is cut back `overshoot / sin(pitch)` along the incline and the foot is kept, so the top corner meets the landing at the top tread's front edge, where the nosing line does. The ramp still rides the nosings.
- A final leg's discharge collider reaches back over the strip the trim leaves; a landing already reached back over its top tread.
- Scissor channels keep their ramps, having no plate to reach back, and the L-stair builder is untouched. Neither stands in the library: 77 switchback and 72 straight stairs.
- Rebuilt and measured: census 0.000 over the landing on all 174 (`ramp_ridge_census.txt`); walk down 2.4 s and up 3.8 s, and the control, lowered a further riser, now fails going up, so the instrument sees both directions; swept gate 144 of 144.
- `test_stair_ramp_head.py` (7): across legal stairs the head lands, the foot stays and no tread stands above the ramp. Six fail on 0.189.0.

**WHAT GENERALISES.** A collision-only change to a stair is not collision-only. Both nav bakes read the visual treads, so a collision ramp must stay on or above the nosing line wherever it runs, and a collision census can pass a change the bake fails. Measure the gate as well as the collider.

**OPEN.** A cold run in which Laser Tag's route through deli_a03's stair completes: the next run on restaurant_row_001.
"""


def main():
    text = ROADMAP.read_bytes().decode("utf-8")
    assert "\r\n" not in text, "the roadmap is LF; CRLF here means it changed under us"
    assert "**190." not in text, "item 190 already exists"
    edits = (
        (OLD_189 + "\n", NEW_189 + "\n"),
        (LINE_REFUTED_LAST + "\n\n**WHAT SHIPPED.**\n",
         LINE_REFUTED_LAST + "\n" + ADD_REFUTED + "\n\n**WHAT SHIPPED.**\n"),
        (LINE_SHIPPED_LAST + "\n\n**OPEN, IN ORDER.**",
         LINE_SHIPPED_LAST + "\n" + ADD_SHIPPED + "\n\n**OPEN, IN ORDER.**"),
        (OLD_OPEN_1 + "\n", NEW_OPEN_1 + "\n"),
    )
    for old, new in edits:
        n = text.count(old)
        assert n == 1, ("anchor matched %d times" % n, old[:80])
        text = text.replace(old, new)
    assert text.endswith(LAST_LINE), "the roadmap no longer ends with item 189's last line"
    text = text + ITEM_190
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("PIPELINE_ROADMAP.md: 189 NARROWED further; 190 added, NARROWED")


if __name__ == "__main__":
    main()
