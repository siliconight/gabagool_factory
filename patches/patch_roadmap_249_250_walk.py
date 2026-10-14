"""Roadmaps 249 to 252, 2026-10-14: the merged modules out of the package, proven in the pipeline; the walker's
walk of cold runs 9305-9307; and two findings from writing the fresh runs' notes.

- 249: OPEN -> CLOSED, the evidence in the status; one body paragraph after WHAT WOULD CLOSE IT, at the end.
- 250, new, NARROWED: the walk's nine findings, 1-4 fixed and run fresh (cold runs 9308-9310), 5-9 open.
- 251, new, OPEN: the light bake's log says "lightmapped" of primitives it does not bake.
- 252, new, OPEN: the backdrop's ground was shipped unpriced.

The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check`.

    python patches/patch_roadmap_249_250_walk.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

S249_OLD = (
    "*STATUS: OPEN 2026-10-14 -- FOUND ATTRIBUTING COLD RUN 9304'S PACKAGE. Of urban_row_001's 612 GLBs, 289 -- 9.2 "
    "MB with their import files -- are named by no scene or resource, and 315 of the light bake's 632 model imports "
    "are files no scene names, mostly the modules Level Factory merged the Empties from. Not yet traced: what else, "
    "if anything, loads them.*")
S249_NEW = (
    "*STATUS: CLOSED 2026-10-14 -- LEVEL FACTORY 0.210.0 (4a63d38): THE KIT MODULES ONLY MERGED SLOTS INSTANCED "
    "LEAVE THE PACKAGE. After the merge and before the light bake, `merge_empties.drop_merged_modules` removes each "
    "merged Empty's `art/zoo/*.glb` that no file of the package names by its bare file name, with its `.import` and "
    "`.unwrap_cache`. On a mirror of cold run 9305's package: 284 removed, 6,876,497 bytes, 4 kept and each "
    "attributed; Level Factory's closure scan reads both copies alike; a first import 115.0 -> 102.9 s and 124.6 -> "
    "113.5 s in two runs; 16 frames differ from the unchanged copy in fewer pixels than that copy differs from "
    "itself. Cold runs, 0 interventions each and nothing the graders read moved: 9308 (urban_row_001, against 9305) "
    "removed 284, the bake's models 632 -> 348, the package 205.6 -> 198.5 MB and 3,343 -> 2,487 files, every file "
    "that left or joined attributed; 9309 (gas_block_001, against 9307) 218, 547 -> 329, 166.9 -> 163.4 MB; 9310 "
    "(restaurant_row_001) 218, 564 -> 346 (`docs/findings/merged_modules/`).*")

B249_ANCHOR = (
    "**WHAT WOULD CLOSE IT:** the export leaves out, or never marks for the bake, a module only merged slots "
    "instanced, every file it leaves out attributed and every file a script or the gameplay layer loads kept, priced "
    "by the editor's import time and the package's size against the run before.\n")
B249_NEW = B249_ANCHOR + (
    "\n**FIXED, 2026-10-14** (`docs/findings/merged_modules/`: `mirror.sh`, `mirror_steps.py`, `package_files.py`; "
    "`patches/patch_lf_drop_merged_modules.py` and `lf_drop_merged_modules/`; `docs/cold_runs/cold_9308/`, "
    "`cold_9309/`, `cold_9310/`). **Level Factory 0.210.0** (4a63d38): for each Empty the merge report merged, an "
    "`art/zoo/*.glb` that no file of the package names -- by its bare file name, in a scene, resource, script, "
    "manifest or config, the import cache and the package's two file lists aside -- leaves with its sidecars. A bare "
    "name, not a path, so a module sharing its file name with one another lot's scene instances is kept. **On the "
    "mirror:** of 9305's 286 merged-only modules 284 went, and gs_midrise_b's and gs_midrise_f's "
    "`wallEnd_delco_1997_01_mbrick_idrywall.glb` stayed because deli_a01's scene instances a module of that name; the "
    "other two kept are the corner awnings their scenes instance. The import ran a then b both times, so its order "
    "is not controlled. The frames: 2,023 pixels differ by more than 24 levels of 255 between two shots of the "
    "unchanged copy and 1,299 between it and the dropped one; one frame, `extraction`, differs more against the drop "
    "(194) than against its control (1), not attributed, its frames gone. **Refuted and kept:** the first frame "
    "check had no control and counted any differing pixel; it read 70-93 % of every frame different, which two shots "
    "of one copy do. **The cold runs:** the export's own line, `merged Empties' modules no file names: 284 removed "
    "(6.9 MB), 4 named and kept`; every file that left 9305's package or joined 9308's, and 9307's or 9309's, is a "
    "module's, a door box's sign texture (250's finding 4) or a corner shop's pane emission (its finding 1). The "
    "editor's bake read 75.3 -> 71.5 s, 61.9 -> 61.5 s and 59.8 -> 60.6 s, one run each beside other Godot jobs: not "
    "a price. **Left, not this item's:** `assets/lot.glb` and `assets/shell.glb`, named by no scene and not "
    "attributed; the responders' cruiser, shipped for the gameplay layer by design (212); the two wall ends kept by "
    "a name collision.\n")

S250 = (
    "*STATUS: NARROWED 2026-10-14 -- THE WALKER'S WALK OF COLD RUNS 9305-9307, NINE FINDINGS BY EYE. 1-4 fixed in the "
    "tools and run fresh for the walker's demo, 0 interventions each: Zoo 1.111.0 (9176f8d) -- a lit shop's room "
    "glows at 90/255 of its paint, and every desk's stock faces its sitter; Zoo 1.112.0 (8d1e2a4) -- a door under its "
    "building's band says its trade, the walker's choice; Level Factory 0.211.0 (5c67868) -- a ground under the "
    "backdrop. Cold runs 9308, 9309 and 9310, nothing the graders read moved; 2 and 4 seen at the walker's own spots, "
    "1 seen improved, 3 seen in the inspection light. Open: 5, the deli's basement partitions' openings; 6, a "
    "`floor_hole` cut bare (144's residue); 7-9, the office's stair core (144's dearer answer); and two taste calls "
    "(`docs/findings/walk_2026-10-14/`).*")
H250 = (
    "**250. The walker's walk of cold runs 9305-9307: nine findings by eye.** The walker walked the three newest levels "
    "on 2026-10-14, before a stakeholder demo, and sent frames from the debug walk; "
    "`docs/findings/walk_2026-10-14/README.md` holds each, with where, whose and what was traced. **1:** the corner "
    "grocery's window read as bars and dots up close -- Zoo's `shop_panes` glow blowing its pale shelf backing to "
    "white. **2:** at the fence the plate's ground ended and the backdrop stood on nothing. **3:** the cubicles' "
    "computers faced the panel -- `cubicle_forms` handed the stock `pi if out > 0 else 0`, turning every item's front "
    "toward the spine on both sides of every bank. **4:** the pharmacy's name twice, band and door box, on a "
    "one-storey front -- the walker's own option A of 2026-10-06 (187), seen where the two stack. **5:** the deli's "
    "basement partitions stop in a big opening. **6:** a hole in the deli's ground-floor ceiling -- an authored "
    "`floor_hole` (`vertical_attack_angle`, Deli Counter 0.80.0) cut bare, which 144 left as designed, unmarked, and "
    "read as a bug until something visual says drop here. **7-9:** the office's stair core in restaurant_row_001 -- a "
    "gap in its enclosure, \"looks wrong in general\", and the second flight's solid underside ending in mid-air, "
    "where the walker expects it to come down to the ground. A core built from per-step boxes with no enclosure, "
    "soffit or rail a person expects: 144's \"Zoo stair species built to DC's flight geometry\", asked for by a "
    "person.")
B250_FIXED = (
    "**FIXED, 2026-10-14: 1-4** (`patches/patch_zoo_desk_facing_shop_glow.py`, `patch_zoo_door_trade.py`, "
    "`patch_lf_backdrop_ground.py`, each with its folder; `docs/cold_runs/cold_9308/`, `cold_9309/`, `cold_9310/`). "
    "**Zoo 1.111.0** (9176f8d): the room behind a lit shop's goods glows at `ROOM_GLOW` 90/255 of its paint, "
    "`EMISSION` kept at 2.2; and each bay's stock is turned to the side its drawers face, `0.0 if out > 0 else pi`, "
    "with a test reading each region's facing against its drawer fronts. **Zoo 1.112.0** (8d1e2a4): a door whose "
    "building's band names the shop paints its trade -- PHARMACY, DELI, OPEN 24 HOURS -- in the colours `sign_for` "
    "gives the name; a door with no band is unchanged. **Level Factory 0.211.0** (5c67868): one dark plane under the "
    "backdrop, 30 m past it and 0.10 m under the plate, outside the bake. Each new test fails on the version before. "
    "**The cold runs**, fresh for the demo, each its predecessor's brief and seed: 9308 (urban_row_001) and 9309 "
    "(gas_block_001) moved 0 of 32 fields on any candidate against 9305 and 9307; 9310 (restaurant_row_001) grades "
    "as 9306's; findings 109, 105 and 112, unchanged; each walk copy loads headless with no engine error. **Seen**, "
    "9305 against 9308 at the walker's spots: 2, dark ground past the east fence; 4, PHARMACY over the door, cream on "
    "navy, under the band, and DELI and OPEN 24 HOURS read off their painted faces; 1, the shelves and goods read "
    "where they had clipped to white, still a flat painting up close; 3, every CRT's screen and keyboard facing the "
    "aisle on both banks, where 9305's showed their backs -- seen in the inspection light built for it at the "
    "walker's ask, `tools/look_shots.py --inspect studio`, after the level's own night light read a screen and its "
    "back alike (`cubicles_9305_9308_inspect.png`).")
B250_LEFT = (
    "**Left:** 5, not yet traced; 6, a design call -- dress the hole as deliberate, trim and a guard, or as damage, "
    "its gameplay role kept; 7-9, Deli Counter's stair core, frames to the walker before any build; and two taste "
    "calls for the walker -- whether the door's trade sign should wear the band's colours, yellow on black, rather "
    "than its own, and whether a corner shop's window wants depth, a redrawn pane or a shallow interior, priced "
    "first. The backdrop's ground went out unpriced (252).")

S251 = (
    "*STATUS: OPEN 2026-10-14 -- FOUND WRITING COLD RUN 9308'S NOTES. The light bake's log line counts every inline "
    "primitive given a UV2 in every scene of the package as lightmapped: the level's 112 in the content scene and "
    "again in the Lux-applied copy the bake instances, and the backdrop's ground, which is never baked. A wording, "
    "not a level: the bake's users are what it bakes.*")
H251 = (
    "**251. The light bake's log says \"lightmapped\" of primitives it does not bake.** `[export] light bake: N "
    "model(s) and M primitive mesh(es) lightmapped` prints the sum of `add_primitive_uv2`'s per-scene counts "
    "(`light_bake.py`), and that function writes `add_uv2 = true` on every inline `BoxMesh`, `QuadMesh`, `PlaneMesh`, "
    "`CylinderMesh` and `PrismMesh` in every `.tscn` of the package. **Measured on cold run 9308's "
    "`light_bake.json`:** `site.tscn` 112, `presentation/lux.applied.tscn` 112, `site_backdrop.tscn` 1 -- the log's "
    "225. `bake.tscn` instances `presentation/lux.applied.tscn` alone, so the content scene's 112 are the same "
    "primitives counted a second time; and `site_backdrop.tscn`, the backdrop's ground (250's finding 2), is loaded "
    "by `mission.tscn` at run time, outside `bake.tscn`, and `bake.lmbake` names no node of it. 9305's log read 224 "
    "the same way. It also hands the ground a UV2 nothing uses. **WHAT WOULD CLOSE IT:** the line counts the "
    "primitives in the scene the bake instances, and `add_primitive_uv2` leaves scenes outside the bake alone, with "
    "a test reading a real package's report.")

S252 = (
    "*STATUS: OPEN 2026-10-14 -- FOUND WRITING COLD RUN 9308'S NOTES. Level Factory 0.211.0's ground under the "
    "backdrop shipped as \"one draw\", read off its scene and not priced: a shaded plane 422 x 338 m under the whole "
    "level, which is the shape this repo refuses on sight -- more lights reaching one mesh than "
    "`max_lights_per_object` lets it draw. Price it against itself with the node removed.*")
H252 = (
    "**252. The backdrop's ground was shipped unpriced.** Level Factory 0.211.0 (5c67868) lays `BackdropGround`, a "
    "`PlaneMesh` with a near-black `StandardMaterial3D`, under the backdrop (250's finding 2): 422 x 338 m on 9305's "
    "mirror, from 30 m past the backdrop's last row, 0.10 m under the plate. Its changelog says \"One draw\"; that is "
    "read off the scene. Unmeasured: a shaded mesh whose bounds span the level is reached by every lamp in it, more "
    "than the 8 `max_lights_per_object` lets one mesh take, and how GL Compatibility draws those lights on it, and "
    "which 8 it keeps, was not read. This repo prices a look before it ships; this one went out for the walker's "
    "demo with its shape and its frames checked and its cost not. **WHAT WOULD CLOSE IT:** cold run 9308's package "
    "priced against itself with `BackdropGround` removed, at the price tool's headings with a control, draws and "
    "frame time; if it costs more than one draw, an unshaded material or a ring that stops at the plate's edge, "
    "shown to the walker as a tradeoff.")

NEW_ITEMS = "\n" + "\n\n".join([S250, H250, B250_FIXED, B250_LEFT, S251, H251, S252, H252]) + "\n"


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
    assert "INSPECT_3" not in B250_FIXED, "250's finding 3 is still a placeholder"
    assert "\n\n**250. " not in text, "already applied"
    for old in (S249_OLD, B249_ANCHOR):
        assert text.count(old) == 1, ("anchor not found once", text.count(old), old[:60])
    s, h, e = _span(text, 249)
    assert text[s + 2:h] == S249_OLD, "249's status is not where it was read"
    assert h < text.find(B249_ANCHOR) < e and text.endswith(B249_ANCHOR), "249's body anchor is not the file's end"
    for block in (S249_NEW, B249_NEW, NEW_ITEMS):
        for line in block.splitlines():
            if line.startswith(("**250. ", "**251. ", "**252. ")):
                continue
            assert not re.match(r"\*\*\d+\.", line), ("a body line would parse as an item", line[:40])
    text = text.replace(S249_OLD, S249_NEW).replace(B249_ANCHOR, B249_NEW) + NEW_ITEMS
    for number, head in ((249, "*STATUS: CLOSED 2026-10-14 -- LEVEL FACTORY 0.210.0 (4a63d38)"),
                         (250, "*STATUS: NARROWED 2026-10-14 -- THE WALKER'S WALK"),
                         (251, "*STATUS: OPEN 2026-10-14 -- FOUND WRITING COLD RUN 9308'S NOTES. The light bake"),
                         (252, "*STATUS: OPEN 2026-10-14 -- FOUND WRITING COLD RUN 9308'S NOTES. Level Factory")):
        s, h, e = _span(text, number)
        assert text[s + 2:].startswith(head), (number, "status does not adjoin its heading", text[s + 2:s + 80])
        assert "\n\n" not in text[s + 2:h], (number, "a blank line inside the status")
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 249 CLOSED; 250 NARROWED, 251 and 252 OPEN, new; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    main()
