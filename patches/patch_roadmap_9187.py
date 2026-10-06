"""PIPELINE_ROADMAP.md after cold run 9187 and Lot 0.97.3:
- 190 CLOSED. 9187's deli_a03 candidate finished 25 of 25 Laser Tag runs
  through the stair that stopped 9186's at 0 of 25.
- 189: its second open item refuted and kept. The gate's re-snap is what a
  level's bake does, so `patch_dc_grid_stand_point.py` is HELD. The four
  necks left each get the rule that would fix them, and the register markers
  are a gameplay-layer call.
- 185 gets the trace it lacked: seed_9061's refusal was an enemy inside an
  Empty.
- 191 is new: an enemy pushed into an Empty, fixed at the source in Lot
  0.97.3.

Run `tools/roadmap_status.py --write` then `--check` after.

    python patch_roadmap_9187.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ROADMAP = ROOT / "PIPELINE_ROADMAP.md"

OLD_190 = "*STATUS: NARROWED 2026-10-06 -- fixed at the source, not yet proven in a level. Deli Counter 0.190.0 trims every stair ramp's head onto its landing (`stairwell.ramp_head_trim`). Rebuilt, 0 of 174 ramps stand over their landing (all 174 stood 0.19 to 0.21 m over it before); a capsule of Laser Tag's size goes down deli_a03's up-stair in 2.4 s and up in 3.8 s, where as built it stuck on the landing for the full 8 s going down; and the swept gate traverses every stair in 144 of 144 shells. The first fix, sinking each ramp, passed the census and the walk and failed the gate on 94 of 144: kept below. Open: a cold run in which Laser Tag's route through deli_a03's stair completes (9186's seed_9003: 0 of 25 runs, 3,148 stuck events in one cell).*"
NEW_190 = "*STATUS: CLOSED 2026-10-06 -- Deli Counter 0.190.0 trims every stair ramp's head onto its landing (`stairwell.ramp_head_trim`). Rebuilt, 0 of 174 ramps stand over their landing (all 174 stood 0.19 to 0.21 m over it before); a capsule of Laser Tag's size goes down deli_a03's up-stair in 2.4 s and up in 3.8 s, where as built it stuck on the landing for the full 8 s going down; and the swept gate traverses every stair in 144 of 144 shells. PROVEN in cold run 9187 (restaurant_row_001, 0 interventions): seed_9003, whose objective is deli_a03's upper floor and whose extraction is the deli, finished 25 of 25 Laser Tag runs, reaching the objective in all 25, with 3 stuck events, all on the ground floor -- where 9186's finished 0 of 25 with 3,148 stuck events at the stair head. The first fix, sinking each ramp, passed the census and the walk and failed the gate on 94 of 144: kept below.*"

OLD_190_OPEN = "**OPEN.** A cold run in which Laser Tag's route through deli_a03's stair completes: the next run on restaurant_row_001.\n"
NEW_190_OPEN = "**PROVEN, cold run 9187** (`docs/cold_runs/cold_9187/NOTES.md`). seed_9003's mission is 9186's: spawn at the far building, objective and extraction at deli_a03, the objective on its upper floor (`LT_ObjectivePoint` at height 3.30). 25 of 25 runs finished and all 25 reached the objective, PASS_WITH_TUNING 79. The three stuck events stand at ground level, (6.0, 0.0, -29.0) twice and (-13.5, 0.0, -27.9), nowhere near a stair head 3.3 m up. The candidate's two other buildings differ from 9186's (depot_a01 and self_storage_a01): twin_a01's return to the themed pool, 101 -> 102 of 127, reshuffled the draw.\n"

OLD_185 = "**NOT CONNECTED, AS FAR AS MEASURED.** seed_9061's `UNREACHABLE_SPAWN` was not\ntraced to `setback_demo`. Nothing here says the demo shell caused it.\n\n"
NEW_185 = OLD_185 + "**TRACED 2026-10-06 (item 191).** seed_9061's refusal in 9170 and 9174 was its Enemy_5 standing inside Empty e15, pushed there off the route by Lot's spawn placer. `setback_demo` played no part.\n\n"

OLD_189_STATUS_TAIL = " Open: four located floor necks (foundry_heist_vertical's and primos_pizza's stair discharges, a door half inside a wall, a cover pocket); have the gate test the base bake's standing point rather than re-snap; the register markers inside their counters.*"
NEW_189_STATUS_TAIL = " Open: four located floor necks, each to be fixed by a rule rather than a spec edit (two stair heads facing a wall, a door running past the end of its wall, a cover pocket); the register markers on their counters, a gameplay-layer call. Refuted and kept: that the gate should test the base bake's standing place -- its re-snap is what a level's bake does, so `patch_dc_grid_stand_point.py` is held.*"

OLD_189_FRIDGE = "- **That twin_a01's fridge pinched its stair**, this item's first OPEN entry. `fridge_right_0` stood nearest where the route tore, at the top of `stair1` beside its guard rail. Built in scratch with all four tall pieces against the end walls (`twin_exp`), the shell still connected at 7 of 8. The flight itself was 0.9 m, which leaves one cell after the bake's erosion; at 1.2 m with the furniture untouched it connects at 8 of 8, gate and census.\n\n**WHAT SHIPPED.**\n"
NEW_189_FRIDGE = OLD_189_FRIDGE.replace("\n\n**WHAT SHIPPED.**\n", "\n") + "- **That the gate's sweep should test the base bake's standing place rather than re-snap**, this item's second OPEN entry until 2026-10-06. Drafted as Deli Counter 0.191.0 (`patches/patch_dc_grid_stand_point.py`, dry-run clean, HELD). A level's own bake snaps a marker at whatever origin the building lands on, so a register inside its counter is on the counter top in some levels and on the floor in others: the re-snap reports a hazard real in play. Testing the standing place would stop the gate seeing it.\n\n**WHAT SHIPPED.**\n"

OLD_189_OPEN_1 = "1. **Fix the four located floor necks left.** twin_a01's is done (Deli Counter 0.190.0, above). foundry_heist_vertical's and primos_pizza's stair discharges against their north walls, both in the gate's `grid_fragile`; then two the census finds and the gate does not flag: cbp_town_finale_midbalanced_schemafixed's 2.0 m `third_vomitory` door, half inside the west wall, and bank_job's 1 m pocket between a crate stack and a desk.\n"
NEW_189_OPEN_1 = ("1. **Fix the four located floor necks left, each by a rule rather than a spec.** twin_a01's is done (Deli Counter 0.190.0, above).\n"
                  "   - **Two stair heads facing a wall.** foundry_heist_vertical's and primos_pizza's flights top out toward their north walls with 1.08 and 1.05 m of landing and discharge plate before the wall's face (`necks.txt`), about 0.3 m after the bake's erosion. Both are in the gate's `grid_fragile`. The rule: a flight's head leaves a corridor (1.2 m) of floor before a wall it faces, a layout-lint sibling of L21.\n"
                  "   - **A door running past the end of its wall.** cbp_town_finale_midbalanced_schemafixed's 2.0 m `third_vomitory` door is centred 0.03 m beyond the west wall's inner face, so about 0.97 m of it opens. L18 catches a wall ending inside a door, not a door's aperture running past its own wall's end: that is the rule to add.\n"
                  "   - **A cover pocket.** bank_job's auto-placed crate stack stands 0.99 m from a desk on a route. Auto cover should leave a corridor beside whatever it stands next to.\n"
                  "   - The last two the census finds and the gate does not flag.\n")

OLD_189_OPEN_2 = "2. **In nine shells the floor holds and the marker moves**: cr_deli, night_deli, corner_deli_heist_01, fuel_stop_heist, the four gas stations, gs_auto_shop and night_auto. The route survives at the failing origin; the marker snaps to a counter top or a pocket. The gate's sweep should test the base bake's standing point at every origin, not re-snap.\n"
NEW_189_OPEN_2 = "2. **In nine shells the floor holds and the marker moves**: cr_deli, night_deli, corner_deli_heist_01, fuel_stop_heist, the four gas stations, gs_auto_shop and night_auto. The route survives at the failing origin; the marker snaps to a counter top or a pocket. That is how a level bakes it too, so the gate keeps re-snapping (REFUTED, KEPT, above); the fix is where the markers stand.\n"

OLD_189_OPEN_3 = "3. **The register markers** stand inside their counters. Placed on the floor beside the counter, the question ends at the source.\n"
NEW_189_OPEN_3 = "3. **The register markers** stand on their counters: `presets.py` places REGISTER at z 0.9 (`:730`, the deli; `:1784`, the station's shop), so a bake snaps it to the counter top at some origins and the floor at others. Where the crew stands to take a register is the gameplay layer's call. Placed on the floor beside the counter, the question ends at the source.\n"

ITEM_191 = """
*STATUS: NARROWED 2026-10-06 -- fixed at the source in Lot 0.97.3, not yet run in a level. Every `UNREACHABLE_SPAWN` refusal in cold runs 9164 to 9186 -- four, on two candidates -- was an enemy Lot's spawn placer pushed inside an Empty, which it could not see. 0.97.3 keeps every spawn out of the blockers and every enemy out of the band behind an Empty row's front line, the ground its fences shut off. With the collision reading Lot passes, 0.97.2 reproduces every shipped enemy on six candidates; 0.97.3 moves 9186's Enemy_5 out of e9 to 1.33 m clear of the row, moves 9174's two out of e15 and the band to open ground (pushed 50.0 and 45.0 m), and moves no enemy on any candidate of 9178 or 9187. A fixture test on 9186's site as drawn fails four of five on 0.97.2. Open: a cold run on 0.97.3.*

**191. An enemy pushed into an Empty.** Found 2026-10-06, reading cold run 9186's refused seed_9205 (`docs/findings/enemy_inside_an_empty/`).

**WHAT WAS MEASURED.**
- **Every refusal is the same defect** (`unreachable_spawns.py`). Laser Tag refused four candidates in cold runs 9164 to 9186 on `UNREACHABLE_SPAWN`: seed_9061 in 9170 and 9174, seed_9205 in 9179 and 9186. In each, Enemy_5 stood inside an Empty: e15, then e9.
- **The control:** the other 17 enemies of 9186's three candidates stand in the open, and so do all 18 of 9187's.
- **The mechanism.** `site_spawns.place_enemies` pushes a route sample sideways until `outdoors()` calls it open ground. `outdoors()` asked `footprints()`, which reads `site_spec["buildings"]`, and an Empty is a blocker. 9186's Enemy_5 is 24.00 m off the route's last leg, the run's own `LOT_ENEMY_SPAWN_PUSHED` figure.
- **Why the fence did not catch it.** `plan_fences` leaves a row open rather than strand a marker behind its front line, but it skips a marker that stands inside a house. 9186's fence went up around an enemy already shut in.
- **The band too** (`place_variants.py`, collision reading). On 9186 the Empties alone are enough. On 9174's seed_9061 they are not: kept out of the Empties only, Enemy_4 and Enemy_5 land behind the row's front line, on ground its fences shut off.

**WHY IT MATTERS.** Each refusal costs a candidate, and a brief whose every candidate puts an enemy in an Empty needs a person.

**REFUTED, KEPT.** The first comparison of the three keep-out rules measured on the declared-footprint occluders `place_enemies` falls back to, without saying so.
- It quoted "Enemy_4 pushed through its house into the strip behind the row" as Lot's placement for 9186.
- That is the fallback's. Under the collision reading Lot actually passes, 9186's Enemy_4 never moves.
- A traceback showed the fallback's occluder call going through the patched function, and the collision reading was added. With it, 0.97.2 matches every shipped enemy; without it, 9186's Enemy_4 does not.

**WHAT SHIPPED, Lot 0.97.3.**
- `site_extent.blocker_rect`: one reader for a blocker's plan rect, used by the ground, the fences and the spawns. There had been three copies of the rule.
- `site_fences.shut_band` / `shut_bands`: the band behind a row's front line, which `plan_fences` computed inline.
- `site_spawns.solid_rects` (footprints and blockers) is asked by `crew_spawns`, `clear_crew_spawn` and `place_enemies`. `place_enemies` also keeps out of `shut_band_rects`.
- `tests/test_spawns_keep_out_of_empties.py` (5), on `tests/fixtures/restaurant_row_001_seed_9205.site.json`, 9186's site as drawn. Four fail on 0.97.2. Suite 664 -> 669.

**NOT CHANGED, OPEN.**
- `plan_cover` measures sightlines against `footprints()` alone, so an Empty is not cover to the cover planner. Whether it should be has a visible effect, and is its own question.
- The band's moves can be large (9174: 50.0 and 45.0 m, to the far side of the route). `LOT_ENEMY_SPAWN_PUSHED` reports them; whether a long push should prefer a slide along the route is untested.

**OPEN.** A cold run on Lot 0.97.3. It will move no enemy on restaurant_row_001's current candidates, so that run measures for regressions; it is not a proof of the fix.
"""


def main():
    text = ROADMAP.read_bytes().decode("utf-8")
    assert "\r\n" not in text, "the roadmap is LF; CRLF here means it changed under us"
    assert "**191." not in text, "item 191 already exists"
    edits = ((OLD_190, NEW_190), (OLD_190_OPEN, NEW_190_OPEN), (OLD_185, NEW_185),
             (OLD_189_STATUS_TAIL, NEW_189_STATUS_TAIL), (OLD_189_FRIDGE, NEW_189_FRIDGE),
             (OLD_189_OPEN_1, NEW_189_OPEN_1), (OLD_189_OPEN_2, NEW_189_OPEN_2),
             (OLD_189_OPEN_3, NEW_189_OPEN_3))
    for old, new in edits:
        n = text.count(old)
        assert n == 1, ("anchor matched %d times" % n, old[:80])
        text = text.replace(old, new)
    assert text.endswith(NEW_190_OPEN), "the roadmap no longer ends with item 190"
    text = text + ITEM_191
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("PIPELINE_ROADMAP.md: 190 CLOSED; 189's second open item refuted; 185 traced; 191 added")


if __name__ == "__main__":
    main()
