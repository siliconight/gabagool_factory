"""The level standard v1.1: the capability sweep's corrections, each re-checked
against the code before it went in.

    python patch_level_standard_v1_1.py

v1 (commit aa7bb67, corrected in 65b03d8) leaned on `USING_THE_FACTORY.md` and
`docs/DELCO_1997_ART_DIRECTION.md` for Pixelcoat's coverage, and both are stale.
It also missed the score-building pick, the vault and safe species, Deli
Counter's objective kinds and combat audit, the perimeter wall, the walk-only
ladders and the unwired escalation hooks. Every claim below was re-read in the
code on 2026-10-07:
  - pixelcoat/profiles/themes/ lists 13, center_city and industrial_flats
    among them; delco_1997 maps 42 kinds incl. stone, siding, shingle
  - site_variation.site_placements draws spawn and objective independently
    (`ids[next(rng) % count]` twice)
  - `"perimeter": {"height": 3}` in the site spec; plan_fences closes "every
    Empty row's gaps and ends"
  - zoo genome species vault_door, drop_safe, safe_deposit_boxes, teller_line,
    cash_stack
  - deli_counter/combat_audit.py H_ONE_ROUTE (MED), H_NO_STEALTH (INFO)
  - tools/walk_ladders.gd "Walk copy -- DEV ONLY ladder climb volumes"
  - objective_hypotheses read only in models.py's functional_signature;
    seed_policy read nowhere

Anchored on docs/LEVEL_STANDARD.md as 65b03d8 left it (LF). Every anchor must
match once; nothing is written on a miss.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "LEVEL_STANDARD.md"

EDITS = [
    # 3.2 Philadelphia
    ("- **Philadelphia is two profiles away.** Zoo has `center_city` and\n"
     "  `industrial_flats` styles; Pixelcoat has no theme for either\n"
     "  (`USING_THE_FACTORY.md`, \"The setting\").\n",
     "- **Philadelphia's themes exist on both sides now.** Pixelcoat carries\n"
     "  `center_city` and `industrial_flats` among its 13 themes, and Zoo has\n"
     "  styles for both. No level has been built in them yet.\n"
     "  `USING_THE_FACTORY.md`'s \"two profiles away\" predates them.\n"),
    # 8 materials
    ("| material families | Pixelcoat skins, 29 kinds in the 1997 theme | BUILT; brick is 20 of 131 specs, stone has no grammar (`USING_THE_FACTORY.md`) |",
     "| material families | Pixelcoat's `delco_1997` theme maps 42 material kinds, stone, siding and shingle among them (89 material grammars) | BUILT. The specs rarely ask for them: brick is 20 of 131 (`USING_THE_FACTORY.md`, whose \"29 kinds, no stone\" is stale) |"),
    # 8 cultural signifiers: what is missing
    ("| cultural signifiers | Zoo's street furniture (signal, stop sign, mailbox, meter, payphone, newspaper box, shelter, hydrant, bollard, street trees), the invented Delco brands, posters | BUILT; EYE |",
     "| cultural signifiers | Zoo's street furniture (signal, stop sign, mailbox, meter, payphone, newspaper box, shelter, hydrant, bollard, street trees), the invented Delco brands, posters | BUILT; EYE. GAP: utility poles and wires, window air conditioners, security bars, roll-down gates, awnings (`DELCO_1997_ART_DIRECTION.md` asks for each; no species) |"),
    # 4 the score building
    ("- **Objective anchors** reach the package: 9 on cold run 9193's level.\n"
     "  BUILT.\n",
     "- **Objective anchors** reach the package: 9 on cold run 9193's level.\n"
     "  BUILT.\n"
     "- **The heist grammar exists in Deli Counter's spec types:**\n"
     "  - `Objective` kinds: drill, hack, grab, thermite, interact;\n"
     "  - `LootSpawn`;\n"
     "  - `Zone` kinds: extraction, secure, drop;\n"
     "  - `interactives` state machines: a vault door (locked, unlocked, open,\n"
     "    breached), teller windows, safe-deposit boxes, breach walls, doors;\n"
     "  - Zoo species: `vault_door`, `drop_safe`, `safe_deposit_boxes`,\n"
     "    `teller_line`, `cash_stack`.\n"
     "  BUILT as data.\n"
     "- **The score building is a seeded pick, not a decision.**\n"
     "  `site_variation.site_placements` draws the spawn and the objective\n"
     "  building independently from the seed. It ignores the archetype, and it\n"
     "  ignores which building holds the objective rooms. The objective can even\n"
     "  be the spawn building. GAP, owner Level Factory: the score should be the\n"
     "  building the brief asked for. Dispatch's mission flow is spawn -> extract\n"
     "  only.\n"),
    # 4.1 stealth and technical
    ("| stealth / concealed | a side or rear door (Deli Counter's rear staff entries; Lot's side-door landings) | BUILT; GAP: nothing marks a route as the quiet one |",
     "| stealth / concealed | a side or rear door (Deli Counter's rear staff entries; Lot's side-door landings); Deli Counter's combat audit reports `H_NO_STEALTH` and `H_ONE_ROUTE` per building | BUILT; MEASURED per building; GAP at site scale |"),
    ("| technical (alarms, power, credentials) | -- | GAP: no alarm, power or credential state exists. Lux's power cut and `reacts_to_alarm` lights are the only hooks |",
     "| technical (alarms, power, credentials) | the `hack` objective kind | BUILT as data; GAP for alarm, power or credential state (§11: the hooks exist and nothing calls them) |"),
    # 5 tactical gates off for LF sites
    ("- **Lot's tactical graph** (`site_tactical`, in the gameplay manifest) holds\n"
     "  buildings, edges, the spawn, objective and extraction designations, and\n"
     "  `objective_approaches`.\n",
     "- **Lot's tactical graph** (`site_tactical`, in the gameplay manifest) holds\n"
     "  buildings, edges, the spawn, objective and extraction designations, and\n"
     "  `objective_approaches`.\n"
     "  - Its hard gates fire only when the site spec carries a `mode`, and\n"
     "    Level Factory writes none. On every generated site it is intel, not a\n"
     "    gate (roadmap 200).\n"
     "  - The crew's route is a straight polyline: spawn -> objective ->\n"
     "    extraction.\n"),
    # 7.2 ladders
    ("| ladders and roof hatches | Deli Counter, Lot's ladders reach the site (Lot 0.76.0) | BUILT |",
     "| ladders and roof hatches | Deli Counter; Lot's ladders reach the site (Lot 0.76.0); Dispatch makes them AI nav links | BUILT as geometry and AI links. GAP for players: a player can climb one only in a walk copy (`tools/walk_ladders.gd`, DEV ONLY) |"),
    ("**The library is low-rise, which is correct:** 59 of 131 specs one storey,\n"
     "67 two, 5 three, none taller (`USING_THE_FACTORY.md`). Height comes from:\n",
     "**The library is low-rise, which is correct:** 59 of 131 specs one storey,\n"
     "67 two, 5 three, none taller (`USING_THE_FACTORY.md`).\n\n"
     "Across 146 non-generated specs: stairs 98, ladders 60, basements 49, slab\n"
     "holes 12, ramps 6, fire escapes 2, setbacks 2. A generated building's spec\n"
     "carries only archetype, mode, theme and seed, so a brief cannot ask for\n"
     "storeys or a basement. Height comes from:\n"),
    # 9 decals
    ("| maintenance gradient | -- | GAP: wear is per style, not per owner or use |",
     "| maintenance gradient | Pixelcoat grammar wear (chips, streaks); Zoo's style `wear`; Deli Counter's `state`, `vacant`, `security_door` | BUILT, uniform: wear is per style, not per owner or use (GAP). Patina runs its `default` theme in the pipeline, and its decals exist only in a builtin theme the pipeline never selects |"),
    # 10 visual life
    ("What exists is visual life, under \"levels feel alive\":\n"
     "- screens that play (Zoo 1.45.0);\n"
     "- moving parts: hot-dog rollers turn, the slush machine churns (Zoo 1.55.0);\n"
     "- one failing fluorescent tube a room and cycling street poles (Lux 0.62.0).\n",
     "What exists is visual life, under \"levels feel alive\":\n"
     "- screens that play (Zoo 1.45.0);\n"
     "- moving parts: hot-dog rollers turn, the slush machine churns (Zoo 1.55.0);\n"
     "- tree crowns sway and CRT screens roll, driven by the weather's wind\n"
     "  (`zoo_worldskin.gd`, `lf_wind`);\n"
     "- one failing fluorescent tube a room and cycling street poles (Lux 0.62.0);\n"
     "- the club's stage lights cycle; Lux rain.\n"),
    # 11 escalation
    ("| escalation shape (room -> building -> perimeter -> block -> district -> extraction) | -- | GAP: no alarm or escalation state is represented anywhere (`docs/LEVEL_RECIPE.md`). Lux's alarm pulse and power cut are lights, not state |",
     "| escalation shape (room -> building -> perimeter -> block -> district -> extraction) | the pieces exist and nothing calls them: Deli Counter's light anchors carry `reacts_to_alarm`; Lux has `pulse_alarm_lights`, `set_mission_phase` and the Mission Goes Hot preset; Lot's site audit checks `responder_spawn` and `horde_spawn` markers Level Factory never writes | GAP: no escalation state is represented anywhere (`docs/LEVEL_RECIPE.md`); the hooks are built and unwired |"),
    # 12 the playable edge
    ("| a credible playable edge | a chain-link fence along the playable edge (Zoo 1.77.0, Lot 0.97.0); far fabric blended | BUILT |",
     "| a credible playable edge | a 3 m perimeter wall round the plate (the site spec's `perimeter`); chain-link fences closing the Empty rows' gaps and ends (Zoo 1.77.0, Lot 0.97.0, phase one) | BUILT as a wall; EYE as a transition |"),
    ("| streets, wires, roofs continuing past the boundary | -- | GAP: the walker's Pennsylvania backdrop guide (`docs/reference/PENNSYLVANIA_BACKDROP_WORLDS_GUIDE.md`, 18 recipes) is filed for after the \"alive\" queue |",
     "| streets, wires, roofs continuing past the boundary | -- | GAP: `docs/proposals/BACKDROP_WORLD.md` (proposed, not started) and the walker's Pennsylvania backdrop guide (`docs/reference/PENNSYLVANIA_BACKDROP_WORLDS_GUIDE.md`, 18 recipes), filed for after the \"alive\" queue |"),
    # 13 perf tools
    ("| Frame target | 60 FPS, 16.7 ms, the walker's call (2026-09-27): a whole frame shared with gameplay, AI, netcode, audio and UI | MEASURED: the fixed-station harness (`_runs/perf_inner/run.py`) reports median and p95 per view |",
     "| Frame target | 60 FPS, 16.7 ms, the walker's call (2026-09-27): a whole frame shared with gameplay, AI, netcode, audio and UI | MEASURED: the fixed-station harness (`_runs/perf_inner/run.py`; Level Factory's `tools/perf_stations_run.py`, stations from `gameplay_anchors.json` at four headings) reports median and p95 per view. There is no performance stage in the planner, and `docs/PERFORMANCE_CONTRACT.md` is proposed, not enforced |"),
    # 15.2 edge
    ("| the playable edge ends without a transition | the fence | BUILT |",
     "| the playable edge ends without a transition | the 3 m perimeter wall; fences on the Empty rows | BUILT as a wall; EYE as a transition |"),
    # Appendix A rows
    ("| heist (the score) | `archetype` (+ `objective_hypotheses`) | Level Factory's archetype aliases, then Deli Counter's preset or library family | BUILT |",
     "| heist (the score) | `archetype` | Level Factory's archetype aliases, then Deli Counter's preset or library family | BUILT; GAP: the score building is a seeded pick, not the archetype's (§4) |\n"
     "| the score's steps | `objective_hypotheses` | only the functional lock's signature (`models.py`); no builder | GAP |"),
    ("| weather | `weather` | `_preset_for`: rain becomes Heavy Rain and overrides the slot | BUILT, with that trade |",
     "| weather | `weather` | `_preset_for`: rain becomes Heavy Rain and overrides the slot. Rain also sets Pixelcoat's wet maps, Lot's wet ground and the wind that sways trees (`lf_wind`) | BUILT, with that trade; fog, snow and overcast read as clear |"),
    ("| players | `crew_size` (4), `crew_health` | Laser Tag | BUILT |",
     "| players | `crew_size` (4), `crew_health` | Laser Tag; `crew_size` also places the crew's spawns (Lot) | BUILT |"),
    ("| route shape | `route_shape`, `extraction_relationship`, `verticality` | Lot, Level Factory | BUILT |",
     "| route shape, extraction, height | `route_shape`, `extraction_relationship`, `verticality` | no builder: `route_shape` is Level Factory metadata that Lot ignores, and the other two feed only the functional lock's signature | GAP (roadmap 200) |"),
    ("| -- | `candidate_count` (3), `seed_policy` | Level Factory: builds 3, picks one | BUILT |",
     "| -- | `candidate_count` (3) | Level Factory: derives the seeds, builds 3, picks one | BUILT |\n"
     "| -- | `seed_policy` | nothing | unused |"),
    # Part II vault methods and door
    ("| quiet / credentials | -- | GAP: no credential state |\n"
     "| technical (alarm, security) | -- | GAP: no alarm state |\n",
     "| quiet / credentials | the vault door's `unlocked` state | BUILT as a state; GAP: nothing grants it |\n"
     "| technical (alarm, security) | the `hack` objective kind | BUILT as data; GAP: no alarm state |\n"),
    ("| loud (drill) | the geometry; nothing escalates | BUILT, partly |",
     "| loud (drill, thermite) | the `drill` and `thermite` objective kinds; the vault door's `breached` state | BUILT as data; GAP: nothing escalates |"),
    ("| heavy mechanical vault door | not checked | not checked |",
     "| heavy mechanical vault door | Zoo's `vault_door` species and the `vault_door` interactive | BUILT |"),
    ("| local: utility transformer, alley couch | not checked / -- | GAP |",
     "| local: utility transformer, alley couch | -- (no utility pole or wire species either) | GAP |"),
    # Part II priorities: the score building first
    ("1. **A third approach.** A fourth enterable building on the site, or (better)\n",
     "0. **The score is the building the brief asked for.** Today the objective\n"
     "   building is a seeded pick, independent of the archetype and of which\n"
     "   building holds the vault (§4). Owner: Level Factory. It is the cheapest\n"
     "   item here and the one every other item assumes.\n"
     "1. **A third approach.** A fourth enterable building on the site, or (better)\n"),
]


def main():
    data = DOC.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    for old, new in EDITS:
        assert text.count(old) == 1, "anchor found %d times: %r" % (text.count(old), old[:70])
        text = text.replace(old, new)
    DOC.write_bytes(text.encode("utf-8"))
    print("LEVEL_STANDARD.md: %d edits, %d -> %d bytes" % (len(EDITS), len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
