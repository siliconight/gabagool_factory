"""Roadmap: 206 records phase 2, the getaway van parked at the spawn (Lot
0.98.0 and 0.98.1, Level Factory 0.155.0, Laser Tag 0.25.0; cold runs 9198
and 9199) and its price, and the walker's answer to what makes the walk back
dangerous; 204 records that the first van package carries no anchor for the
van; 211 is filed: the audit measures cover by its height; 212 is filed:
responders arrive on the way back (the walker's design, 2026-10-08).

    python patch_roadmap_206_phase2.py

Anchored on PIPELINE_ROADMAP.md as patch_roadmap_206_hero_pass.py left it
once its index was regenerated (1,287,502 bytes, LF, as read 2026-10-08):
206's status line by its unique prefix, directly above its heading; 206's
"Unproven" bullet and its "What parking it touches" bullet; 204's last
"earlier packages" bullet; the file's last line, after which 211 goes. Then
run `tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

S206_PREFIX = "*STATUS: NARROWED 2026-10-08 -- the van is built and not yet placed: Zoo 1.85.0's `step_van`"
S206_NEW = (
    "*STATUS: NARROWED 2026-10-08 -- the van is parked at the spawn: Lot 0.98.0 stands Zoo 1.85.0's "
    "`step_van` in two kerb bays at the spawn building's street door, with the crew's spawn and extraction one "
    "point at its kerb-side door; Level Factory 0.155.0 makes the extraction the spawn building; Laser Tag "
    "0.25.0 counts a route walked only when every point was reached. Cold run 9198 (bank_block_001, 0 "
    "interventions): the van on all three candidates, the crew's point 4.0-6.1 m from the spawn building's "
    "door, and the frames went to the walker. It found a crew member standing in the van (seed_9256, "
    "`SPAWN_IN_COLLISION`, never evaluated): Lot 0.98.1, proven by cold run 9199 (0 interventions; seed_9256 "
    "played all 25 runs). Priced on 9198's package: 5 draws where it is in view (17 of 53 headings) and about "
    "0.04 ms there, every station inside budget with it and without. Open: responders on the way back -- the "
    "enemies' one-leg "
    "spread made two of the three fights trivial (crew losses in 25 runs 48 -> 1 and 19 -> 0) and left the "
    "third hard (49 -> 41), and the walker's answer is item 212 -- the package's anchors (item 204), and the "
    "van in daylight.*\n")

OLD_UNPROVEN = (
    "- **Unproven:** no frame time exists with the van in a level, and nothing places it -- phase 2 is next, "
    "and its cold run owes the performance contract's price (draw calls and frame time at fixed stations, with a "
    "control). *As first written:* \"the hero pass, and nothing places the van.\"\n")
NEW_UNPROVEN = (
    "- *As first written:* \"Unproven: no frame time exists with the van in a level, and nothing places it -- "
    "phase 2 is next, and its cold run owes the performance contract's price (draw calls and frame time at fixed "
    "stations, with a control).\" Both answered below.\n"
    "\n"
    "**PHASE 2 -- PARKED AT THE SPAWN (2026-10-08).** The walker: \"go ahead, place it at the spawn\". Three "
    "releases, recorded in one root commit (dfdc49d):\n"
    "- **Lot 0.98.0** (`site_getaway.py`). The van takes the pair of adjacent parking bays, on a kerb the spawn "
    "building's street door faces, that puts its own door nearest that door, within 30 m. It faces the way its "
    "lane travels, so its kerb side, with the crew's door, is against the kerb. One point on the sidewalk "
    "outside that door, 1.2 m in from the kerb, is both the site's `crew_spawn` and its `extraction` (`getaway: "
    "step_van`). `site_audit` says `S_GETAWAY_AT_SPAWN` (INFO) where it said `S_BACKTRACK`, and `place_enemies` "
    "spreads the enemies along the one leg of a there-and-back route. The record is `patches/patch_lot_getaway.py`.\n"
    "- **Level Factory 0.155.0.** The extraction is the spawn building. The draw that chose another is still "
    "made, so no other number a seed gives moves (`patches/patch_lf_getaway_extraction.py`).\n"
    "- **Laser Tag 0.25.0.** A run counts as `ObjectiveReached` only when every route point was reached, not "
    "skipped past when stuck: a there-and-back route ends where it starts (`patches/patch_lt_route_walked.py`).\n"
    "- **Cold run 9198** (bank_block_001 on 9197's seeds, 0 interventions; `docs/cold_runs/cold_9198/NOTES.md`). "
    "The van stood on all three candidates, the crew's point 3.97, 4.50 and 6.09 m from the spawn building's "
    "door. Seed_9054 was picked at route completion 1.00 (0.84 in 9197). Frames from the walk copy "
    "(`tools/look_shots.py`, five given stations round the van) went to the walker: the van in the bays outside "
    "THE BROKE BANK CASINO, the crew's door on the sidewalk side. That level is night and rain, so the van reads "
    "as a silhouette and the ghost and the patina do not show.\n"
    "- **A crew member stood in the van.** On seed_9256 `site_spawns.crew_spawns` put `LT_PlayerSpawn_1` 2.0 m "
    "along +X, at (20.812, -1.8), inside the van's slot: it tested its ring points against the buildings and "
    "the blockers only, and no cover had stood near a spawn before. Laser Tag refused the map "
    "(`SPAWN_IN_COLLISION`) and played no run of it. **Lot 0.98.1** "
    "(`patches/patch_lot_crew_clear_of_cover.py`): `cover_rects`, every cover piece grown by `WALL_MARGIN`, "
    "asked beside `solid_rects`; the test's fixture is that candidate's drawn site, and 4 of its 6 tests fail "
    "without the change.\n"
    "- **Cold run 9199** (0 interventions; `docs/cold_runs/cold_9199/NOTES.md`). Seed_9256 played all 25 runs: "
    "`LT_MAP_SPAWN_IN_COLLISION` and `LT_NOT_EVALUATED` 1 -> 0, its crew at the positions the test predicts, "
    "all on the sidewalk side of the kerb. The six findings that rose are seed_9256's own Laser Tag report, "
    "played for the first time.\n"
    "- **The fight got easy.** Laser Tag flagged `LT_MAP_TRIVIAL_ENCOUNTER` on seed_9155: no crew member lost in "
    "25 runs, against 19 in 9197. Seed_9054 lost one, against 48 and four team wipes. *First attributed to "
    "seed_9054, retracted: the finding is seed_9155's.* `LT_EnemyBrain` walks every enemy that cannot see the "
    "crew toward it from the first frame -- every enemy's median time of death was 3.5 to 10.7 s on both seeds "
    "in both runs, whichever leg it stood on -- so the spread along the route sets when and from where each "
    "arrives. On one leg, six arrive one at a time from one side. 9197's two-leg routes had put two enemies "
    "behind the crew (seed_9054) and two pairs at one distance each (seed_9155), by where the extraction "
    "building happened to stand. A reading, not a proof: no variant was run. The behaviour is kept, since "
    "enemy placement is provisional until a gameplay layer owns it, and 0.98.1 corrects the comment that said "
    "the crew passes the enemies \"going in and coming out\". The walker's answer is item 212.\n"
    "- **Cold run 9199 corrected that reading.** Seed_9256, played with the van for the first time, lost 41 "
    "(49 in 9197). The line from its van to its vault runs through the spawn building, a parking garage, so "
    "the spread pushed two enemies out to either side of it, 17.7 and 23.4 m from the crew and 94 degrees "
    "apart. Crew deaths track enemies arriving together from more than one direction, which the one-leg spread "
    "makes on some sites and not on others. Lot 0.98.1's comment in `place_enemies` gives the single-file "
    "account as if it always held; the next Lot release corrects it.\n"
    "- **The price** (`docs/findings/getaway_van_price/`). Cold run 9198's package, 14 stations by 4 headings, "
    "GL Compatibility; \"off\" is a copy with the van stripped from every scene that carries it, and the "
    "package run twice is the control. The van is drawn at 17 of the 53 headings: 5 draws fewer without it "
    "(3 at six of them), the same at the other 36, and 3,697 meshes against 3,692. Where it is drawn, the "
    "median frame moves a mean of -0.044 ms without it, against the control's +0.012 at the same headings; no "
    "heading leaves the control's spread (-0.096 to +0.082 ms), but seventeen agree. So about 0.04 ms where "
    "it is in view, which is five submissions at this level's ~0.005 ms a draw. The worst view is 1,923 "
    "draws with it and 1,918 without, inside the provisional 11.0 ms and 2,000-draw budget either way.\n")

OLD_TOUCHES = (
    "- **What parking it touches** (each reference re-read 2026-10-07, nothing patched yet):\n")
NEW_TOUCHES = (
    "- **The fight on a there-and-back route -- decided** (the walker, 2026-10-08): \"have responders show up "
    "after the job, on the way back (and this would be on the gameplay layer, but we can make thee assets and "
    "ensure there is clearance and routes for their arrival)\". Item 212. *As first filed:* \"the walker's call. "
    "Every enemy is met on the way in, one at a time, and the walk back to the van is empty.\"\n"
    "- **What parking it touches** (each reference re-read 2026-10-07; *answered by phase 2*, every item below, "
    "by Lot 0.98.0, Level Factory 0.155.0 and Laser Tag 0.25.0):\n")

OLD_204 = (
    "- **The earlier packages:** 9189 and 9193 (restaurant_row_001, 116 anchors, 9 objectives) and 9191 "
    "(deli_001, 171, 12) mark no objective and name no building either. Whether their `deli_counter:*` anchors "
    "are placed buildings' (deli_a01 is a Deli Counter building on that lot) or the unplaced shell's was not "
    "checked.\n")
NEW_204 = OLD_204 + (
    "- **Cold run 9198, the first package with the getaway van (2026-10-08):** the van's crew point and its "
    "extraction, both site-level markers in Lot's site spec, are not among the package's 64 anchors at all. Its "
    "`crew_spawn` is still `deli_counter:A` (-2, 0, 14), the unplaced shell's; its extractions are `lot:EXIT`, "
    "`lot:STREET` and `lot:STREET_25`; its one `player_start` is `lot:mission_start` (-7.03, 0, 0.68). The walk "
    "scene and Laser Tag stand the crew at the van; a game layer reading the package would not know where it "
    "is. Whether Dispatch's Lot input carries the markers was not checked.\n")

OLD_TAIL = (
    "- Lot: wall shrouds on store walls by the door and pedestals at corners, on the streets the walker means by "
    "city and urban -- which themes those are is the walker's call.\n")
NEW_TAIL = OLD_TAIL + (
    "\n"
    "*STATUS: OPEN 2026-10-08 -- found, not fixed: Lot's `site_audit._cover_rects` reads a cover record's `size` "
    "as [plan x, plan y, ...], where every planner writes [plan x, height, plan y] (`lot.py:2123` stands each "
    "box at half the middle number), so the audit measures every cover piece with its height for a depth -- "
    "3.05 m for the getaway van's 6.8 m, 1.73 m for a parked car's 4.7 m. It moves one check, `S_NAKED_ANCHOR`, "
    "and has since v0.17.1.*\n"
    "\n"
    "**211. The audit measures cover by its height.** Found 2026-10-08 writing Lot 0.98.1's "
    "`site_spawns.cover_rects`, which reads `size` the way `lot.py` stands the box.\n"
    "\n"
    "**WHAT IT TOUCHES** (read 2026-10-08):\n"
    "- `site_audit.audit` builds `backstops = cover + _building_rects(site)` (`site_audit.py:173-174`). "
    "`S_NAKED_ANCHOR` asks the distance from the crew spawn and the extraction to the nearest of them, so a cover "
    "piece's extent decides it whenever a cover piece is the nearest backstop.\n"
    "- `S_BARE_LEG` reads only each rect's centre, which the error does not move. *Lot 0.98.1's changelog says "
    "the error feeds two checks; it feeds one.*\n"
    "- `site_getaway._standing` and `lot.py`'s own readers (`lot.py:2123`, `:3342`) read the size the planners' "
    "way.\n"
    "\n"
    "**NEXT.**\n"
    "- Read `size[2]` as plan y, with a test on a piece whose depth and height differ (a parked car at yaw 0).\n"
    "- Run the audit over the specs on disk before and after, and attribute every `S_NAKED_ANCHOR` that moves.\n"
    "- In the same release, correct 0.98.1's two overstatements: its changelog's \"two checks\" (it is one), and "
    "`place_enemies`' single-file account of the one-leg spread, which cold run 9199's seed_9256 contradicts "
    "(item 206).\n"
    "\n"
    "*STATUS: OPEN 2026-10-08 -- the walker's design, not started: responders arrive after the job, on the way "
    "back to the getaway van. Spawning them is the gameplay layer's; the factory makes their assets and "
    "guarantees they can arrive -- an entry, a clear lane, a stop a vehicle fits with its doors open, and a "
    "walkable route from it to the crew's way back, marked in the package. Today the plate is walled on all "
    "four sides with no opening, its roads stop short of the walls, `site_cover` may stand a box truck across "
    "a lane, and Lot's audit rules for responder spawns have never run, because nothing writes the markers.*\n"
    "\n"
    "**212. Responders arrive on the way back.** The walker, 2026-10-08, answering item 206's question of what "
    "makes the walk back to the van dangerous: \"have responders show up after the job, on the way back (and "
    "this would be on the gameplay layer, but we can make thee assets and ensure there is clearance and routes "
    "for their arrival)\".\n"
    "\n"
    "**WHY IT WAS ASKED.** Cold run 9198: with the enemies spread along the one leg of the van's there-and-back "
    "route, Laser Tag's crew lost one member in 25 runs on seed_9054 (48 in 9197) and none on seed_9155 (19). "
    "Every enemy runs at the crew from the first frame, so all six were met on the way in, one at a time, and "
    "the walk back was empty (item 206).\n"
    "\n"
    "**WHAT EXISTS** (read 2026-10-08):\n"
    "- **Lot's audit** checks `responder_spawn` site markers: their spread (`S_RESPONDER_ARC`: all inside 150 "
    "degrees is one wave), camping (`S_RESPONDER_CAMP`: within 12 m of the crew's spawn or extraction) and "
    "absence (`S_NO_RESPONDERS`, INFO). Level Factory never writes the markers, so only the INFO has fired. "
    "`docs/LEVEL_STANDARD.md` section 11: \"where responders stop -- GAP\".\n"
    "- **What `S_RESPONDER_ARC` asks.** It fires when any gap between the responders' bearings from the "
    "objective is wider than 150 degrees, so it wants three or more; its constant's comment reads looser "
    "(\"all responders inside this arc\"). The calibration site, `specs/gs_heist.json`, has three at 90, 213 and "
    "327 degrees and passes. On cold run 9198's seed_9256 every point on the roads bears 215 to 18 degrees "
    "from the objective, so stops on those roads cannot pass it: the finding would be about the road layout, "
    "not the stops.\n"
    "- **Deli Counter's presets** carry building-level `responder_spawn` markers (`presets.py:302`, `:507`), and "
    "Lot's nav QA spawns its bots at them (`lot.py`, `_BOT_TYPES`). Dispatch passes the type through "
    "unvalidated. Laser Tag has no responders.\n"
    "- **The plate is walled** on four sides, 3 m high, with no opening (`lot.py:2101`, `perimeter`, round the "
    "built ground). On cold run 9198's seed_9256 the roads stop short of the walls -- road 0 by 9.5 m at either "
    "end, road 1 by 18.5 m at its north end -- so a vehicle can enter only from inside, at a road's end.\n"
    "- **The fence keeps off the roads** (`site_fences.plan_fences` adds every road's box to its keep-out). "
    "**`site_cover` does not:** it stands cover in the street -- a box truck, a container or a car, turned "
    "across the line it breaks -- and nothing keeps a lane open for a vehicle.\n"
    "- **The vehicle.** Zoo's `simple_car` has a `police` style that is black paint and nothing else: no light "
    "bar, no push bar, no spotlight, no markings.\n"
    "\n"
    "**NEXT, in order.**\n"
    "- **Lot: arrival routes.** For a heist, two or three, each made of four parts:\n"
    "  - an entry at a road's end inside the plate;\n"
    "  - the lane from the entry to a stop;\n"
    "  - a stop where a cruiser fits with its doors open, in a travel lane, outside `CAMP_RADIUS` of the van;\n"
    "  - a walkable route from the stop to the crew's leg back to the van.\n"
    "  Spread them so `S_RESPONDER_ARC` passes. Reserve them before the cover, the fence and the parking are "
    "planned, and check them after all three: a lane or a stop that something now stands in is a finding. "
    "Write them as `responder_spawn` site markers carrying the entry, the lane, the stop's pose and the "
    "route.\n"
    "- **The package** marks them, with the pose and the routes, so the game layer can find them (item 204).\n"
    "- **Zoo: the responder vehicle.** A 1990s cruiser from `simple_car`'s police style: a light bar, a push "
    "bar, an A-pillar spotlight, and an invented department's markings on one texture. The walker's comps come "
    "first, as for the van.\n"
    "- **Price** the cruiser the way the van was priced.\n")


def _replace_status(text, prefix, new_line, heading):
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hits) == 1, "status prefix found %d times" % len(hits)
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2].startswith(heading), "status not above %r" % heading
    lines[i] = new_line.rstrip("\n")
    return "\n".join(lines)


def main():
    data = RM.read_bytes()
    assert len(data) == 1287502, "PIPELINE_ROADMAP.md is %d bytes, read at 1,287,502" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    for old in (OLD_UNPROVEN, OLD_TOUCHES, OLD_204, OLD_TAIL):
        assert text.count(old) == 1, "anchor found %d times: %r" % (text.count(old), old[:60])
    assert text.endswith(OLD_TAIL), "the file does not end on 210's last bullet"
    for new in (S206_NEW, NEW_UNPROVEN, NEW_TOUCHES, NEW_204, NEW_TAIL):
        assert "RESULT_" not in new, "an unfilled result: %r" % new[new.index("RESULT_"):][:40]
    text = _replace_status(text, S206_PREFIX, S206_NEW, "**206. ")
    text = text.replace(OLD_UNPROVEN, NEW_UNPROVEN)
    text = text.replace(OLD_TOUCHES, NEW_TOUCHES)
    text = text.replace(OLD_204, NEW_204)
    text = text[:-len(OLD_TAIL)] + NEW_TAIL
    RM.write_bytes(text.encode("utf-8"))
    print("206 phase 2, 204, 211, 212; %d bytes" % len(text.encode("utf-8")))


if __name__ == "__main__":
    main()
