# Open items re-measured against today's toolchain (2026-10-15)

Two roadmap items whose status was measured before the tools that answered them shipped, re-read on the
checkouts of the morning of 2026-10-15 (Level Factory 0.215.1, Deli Counter 0.223.0, Lux 0.77.0, Zoo 1.112.0) and
on cold run 9314's package (urban_row_001). Each has an instrument beside this README and its output; the roadmap
carries the verdicts.

## 55. The level ships sign fixtures with no sign art, and three of four cannot be addressed

**What it found (2026-08-18, re-seen 2026-09-05):** four 1.4 m `AreaPanel_Surface` quads at head height in
`presentation/lux.applied.tscn`, blank -- the emitter faces of Lux's area-light rigs, with nothing ever put on
them -- three of the four under engine-generated `@Node3D@<n>` names. What would close it: artwork on the panel,
or a stated decision that the emitter face is invisible and Zoo's marker carries the sign; a name from the
spawner; a count in the validation output.

**What shipped since, each read in Lux's CHANGELOG:**
- **0.33.0** turns the area rig's preview quad off for a sign: the hardware is the panel, Zoo's sign cabinet
  carries `M_SignBox_Face`, and a second emissive quad through it was "the same white square from another angle".
- **0.34.0** names a rig `<name>_dup<k>` when the container already holds its name; `add_child` had renamed every
  rig after the first building's to `@Node3D@<n>`.
- **0.36.0** builds a window's rig with its light and no `AreaPanel_Surface` at all.

**Measured on 9314's package** (`sign_panels_55.py`, `sign_panels_55_9314.out.txt`): 964 nodes; `AreaPanel_Surface`
0; engine names 0; spawner names 205; the scene's two `QuadMesh` sub-resources are the two sign faces,
`Quad_sign_b0` under `Mat_sign_b0` with `signs/sign_scrapple_sons_deli_albedo.png` and its emissive, `Quad_sign_b1`
with `sign_docs_discount_drugs`. The 22 `panel_size = Vector2(1.4, 1.4)` lines are a rig property, not geometry.

**REFUTED AND KEPT:** the first read of this scene grepped `size = Vector2(1.4, 1.4)` and counted seven
"1.4 m quads"; they were the rigs' `panel_size` properties, and the instrument now counts those apart.

**The count in the validation output** was not added: the class it would count -- a blank Lux card -- no longer
exists in a package. A sign with no art is now a Zoo sign face without a texture, which the export's closure scan
and `glb_materials` read, not a Lux surface. CLOSED on the roadmap.

## 171. Exterior access exists and almost never gets placed

**What it found (2026-09-23):** across 370 specs, 2 carrying a `fire_escapes` assembly and 3 ladders with an
exterior placement mode; it asked for a derived rule (storeys and independent stairs), not a dialled share, and for
the route value to be measured, since an exterior stack is an alternate entry.

**What shipped since:** Zoo 1.110.0 draws a fire escape a storey at a time; Deli Counter 0.220.0 stands one on a
walk-up's front -- a walk-up six storeys or fewer and not a corner block, `fire_escape_stack: "front"`, a rule
CHOSEN and not derived, as its entry says -- with no collision ("the lowest landing stands a storey up"); Level
Factory 0.209.0 merges the stack with the building's front (cold runs 9303, 9304).

**Measured on today's specs** (`exterior_access_171.py`, `exterior_access_171.out.txt`): of the library's 159 specs,
7 carry a fire escape -- the five walk-up Empties' stacks (`gs_midrise_a`, `_b`, `_g`, `_h`, `_i`) and the two
assemblies 171 counted (`apartment_walkup_a01`, `rowhouse_raid`); of 78 library ladders, 3 are exterior, as
before. Every urban level stands the walk-ups it deals, so a city street carries fire escapes now and a strip
level does not.

**REFUTED AND KEPT:** the first census grepped `"fire_escape_stack": "<CAPITAL>"` and found none; the field's
value is `"front"`, lowercase, as the schema's enum says. Read the schema before the regex.

**What is left of 171:** the stack is visual only, so it is not an entry route and nothing has measured one; the
rule is chosen, not derived from a building's stairs; the library's other walk-ups (`apartment_walkup_a01`,
`rowhouse_raid`) carry the older assembly. NARROWED on the roadmap.

## 148. Nothing dresses the inside of a building

**What it found (2026-09-11):** the walker asked for "surface dressing on the walls and floor as extra
non-collision layers ... posters, garbage, clocks, vents, smoke detectors"; Layer 3 scattered litter, weeds and
pebbles over the site's ground as one MultiMesh and nothing walked an interior wall, ceiling or floor. What would
close it: the interior surfaces reachable by the Layer 3 chain, one species placed by one rule, and a walk that
finds a room reading as inhabited.

**What shipped since, by another road:** not the Layer 3 chain but Deli Counter's furnish recipes placing Zoo
species a slot at a time -- posters on four wall kinds (2026-10-02), litter bins, dust sheets, a neon sign, the
desks' stock, the shop goods, the fixtures, the club's and the bar's dressing. **Measured** (`interior_dressing_148.py`,
`interior_dressing_148_9314.out.txt`): of the ask's seven kinds, Zoo has species for two by name -- posters
(`poster`, `poster_wall`) and garbage (`litter_bin`, `litter_scrap`, `trash_bags`) -- and `vent_stack` and
`exhaust_fan` are roof pieces, not a ceiling grille; nothing for a clock, a smoke detector, a light switch or an
exit sign. On 9314's package the deli carries 22 prop species including three poster walls and two litter bins,
the pharmacy three poster walls and a litter bin, the office its desks, cabinets and machines and none of the
asked kinds.

**What is left of 148:** clocks, ceiling vents, smoke detectors, switches and exit signs do not exist as species;
interior litter is a bin, not a scatter; and the no-collision interior dressing LAYER the item names -- one
MultiMesh over a room's walls and ceiling, placed by a rule on room roles -- is not built: every interior piece is
a furnish slot. NARROWED on the roadmap; the walker's eye on whether a room reads as inhabited is the last line.

## 14. Seed 5017 has a collision trap the path query cannot see

**What it found (2026-08-12):** four walkers stuck at one coordinate on seed 5017's site, a lot-demo-era level,
with every path proof passing -- a lip, a doorway narrower than the capsule, or geometry the bake smoothed over.
Its status asked for a re-measure "after the first run on a level that has walls".

**Measured today:** seed 5017 is in no cold run's batch and no record names it; the generators that built that site
are two months and several hundred releases gone, so the trap itself cannot be re-read. What catches its class
now: Deli Counter 0.214.0 widens every walkable door to the agent contract's 1.25 m (roadmap 197); the walk test
walks the crew's body over every leg of every candidate (roadmap 208), and cold run 9314's reads every path proof
and every walker `ok` on all three candidates, with Laser Tag's crew at 0 player-stuck events on each
(`cold_9314/fight_fields_9313_9314.out.txt`). SUPERSEDED on the roadmap by 197 and 208, with that figure.

## 66. `verify-manifest` prescribes a remedy that under-proves what it certifies

**What it found (2026-08-25):** every DRIFT line ended "re-run the real-tool smoke and re-certify" -- one suite,
ten tests in five seconds that build no geometry -- where `docs/CERTIFY.md` requires three more legs; and six of
the smoke's ten tests could skip on a missing fixture with the total never changing. What would close it: a
remedy line that names the legs, and a smoke that prints what it ran and what it skipped.

**What shipped since, read in Level Factory's CHANGELOG and code:** 0.67.1 (2026-09-11), "a DRIFT line names the
runbook, and the smoke says what it ran" -- both asks, seventeen days after the item was filed, and never
recorded against it. Today `ContractResult.message` (`packages/tools/contracts.py`) reads, for DRIFT: "re-certify
per docs/CERTIFY.md: the real-tool smoke (adapters and contracts, no geometry), the zoo walkabout (Blender), the
engine leg (Godot) and the lux visual leg, as the changed tool requires; then promote the manifest", pinned by
`tests/unit/test_drift_remedy_names_the_legs.py`; `tests/real_tools/conftest.py` writes a coverage block after
every run, each test by name as ran or skipped with the skip's reason. Seen in this repo's own record: the 1.40.0
re-ground's smoke read "ran 10 of 12 real-tool tests, 1 skipped, 1 FAILED" before the table moved and "11 of
12" after (`patches/lf_reground_1_40_0/smoke_before.out.txt`, `smoke_after.out.txt`).

**Two caveats, neither this item's:** the `docs/CERTIFY.md` the line names lives at the factory root and not in
Level Factory's tree, so read from a bare Level Factory checkout the path resolves to nothing (0.97.0's note); and
CERTIFY.md is written against zoo 0.34.0 and pixelcoat 0.10.0, while since factory 1.36.0 the set has been
certified by an install test (roadmap 202) -- the runbook the remedy names is the older of the two proofs. The
doctor's own row still says only "re-certify", which is terse and not wrong. CLOSED on the roadmap.

## 147. One centre row at a 4.0 m reach cannot light a room wider than 8 m, and the median room is 12 m

**What it found (2026-09-11):** Deli Counter laid ONE fluorescent row per room on its centreline and Lux ranged
each lamp 4.0 m, so a 12 m room was lit in an 8 m band with its walls dark; over 692 rooms the median short
side was 12.0 m, p90 21.0, 83 % wider than 8.4 m. What would close it: rows that cover the room by a derived
spacing, and the per-mesh light census before and after, because item 54's cap of 8 lights a mesh was the ceiling
a second row had to fit under -- three ward tiles were already at 9 and 10 by reach.

**What shipped since:** Deli Counter 0.206.0 (roadmap 229) lays rows by the room's work plane -- with A the
height from the work surface to the lamp, rows at most 1.5 x A apart across the shorter axis, the outer row within
half of that of its wall, held to 3 rows and 12 lamps a room; 0.207.0 lays them down a shop's aisles; 0.207.1
gives a home's room a fixture a bay. Level Factory 0.159.0 made the perf harness's light census count what the
renderer PAIRS (a baked light on a lightmapped mesh is skipped) beside what reaches.

**Measured** (`row_census_147_today.txt`, 0.206.0's own instrument re-run; `room_widths_147.out.txt`;
`light_cap_147_9308.out.txt`): the rooms are what they were -- 714 in 130 built specs, median short side 12.0 m,
p90 21.0, 80 % wider than 8.4 m -- and the lighting is not: 1,004 fluorescent rows, 957 of them off their room's
centreline, 431 rooms with a row and 390 of those with more than one run (0.206.0's census read 513 of 513 on the
centreline before it). On cold run 9308's package, by the renderer's pairing, 3 of 3,275 meshes carry more than 8
lights -- the horizon glow (238), one wires cell (32), one roof (9) -- and no room floor or ceiling tile; by reach
alone 162 do, which is the number 147's instrument would have counted and is not what is drawn (211 of the
lights are baked into the lightmap's 3,153 users).

**Two caveats:** the rows' spacing is derived from the work plane and the fixture guide's 1.5 x A, and Lux's range
from the drop -- two derivations, deliberately, not the "one formula named in both places" this item proposed,
and the rows at 2.7 to 6 m stand closer than twice Lux's 4.0 m reach, which is why they cover; and cold run
9005's hospital, where the dark ward was walked, was not re-walked. CLOSED on the roadmap.

## 56. The global light budget is derived from scene text, and the running level has twice as many lights

**What it found (2026-08-23):** `max_renderable_lights` was written from a count of light DECLARATIONS in the
package's `.tscn` files, and the running tree held twice that -- an instanced rig counts once in the text and N
times at run time, and the spawner's area-light rigs are in no `.tscn` at all. Above the cap GL Compatibility draws
nothing, so whole areas stayed dark. Lux 0.17.0 removed the doubling the same day; the item stayed open for the
class: a derivation that counts an instanced rig once and a spawned light zero times, and asked for the cap to be
derived from the running tree, or made instance- and spawner-aware, with a check that the shipped cap and a
runtime count cannot drift apart silently.

**What shipped since:** Level Factory 0.87.0, "interiors read dark, and the light budget counts what Lux built",
citing this item: the Lux driver counts every `Light3D` in the running tree after its last bake and writes
`lux.quality.json["lights_in_tree"]`; `packages/core/godot_project.package_light_budget` writes the cap as the
larger of the scene-text count and that census; `tests/unit/test_project_godot_agreement.py` pins the cap to the
package's count and the preview's `project.godot` to the export's.

**Measured today:** cold runs 9308, 9313 and 9314 each record `lights_in_tree` 239 (205 fixture, 19 daylight, 14
club) and each package writes `max_renderable_lights=239`; the applied scene declares 238 light nodes, the
spawner's rigs packed into it; and the perf harness's own census of the running tree on 9308's package, an
instrument the driver does not share, counts 238 positional lights (`light_cap_147_9308.out.txt`) -- inside the
cap, where the item's package held 272 against a cap of 136.

**The check this item asked for:** the cap cannot be below the driver's count by construction, and the perf
harness is the independent reading of the same tree; nothing refuses an export on the comparison, because what
could exceed the cap at run time is a light the gameplay layer spawns, which the package does not contain by
contract. CLOSED on the roadmap.

## 105. Lot builds one arrangement of buildings, and nothing varies it

**What it asked (2026-09-06):** not more arrangements but a measurement first -- the same brief at several seeds,
the plans compared by building positions and the space between them -- because until that number exists "more
arrangements" is a preference and not a target.

**Measured** (`arrangements_105.py`; `arrangements_105_9314.out.txt`, `arrangements_105_9311.out.txt`): the three
seeded candidates of urban_row_001 (cold run 9314) and of restaurant_row_001 (cold run 9311), each plan read off its
candidate's drawn site spec.
- **The mission buildings stand in one arrangement at every seed and in both missions:** three in a row facing
  south at rot 0, at x -51 / +1 to +4 / +48 to +54 -- deli, pharmacy, office -- and the 1 to 6 m shifts between
  seeds are the drawn archetype's own width (deli_a03 against deli_a01, pharmacy_a02 against pharmacy_a01), not a
  different plan. seed_9003's three stand at the same coordinates in both missions.
- **What varies by seed is the block, not the row:** the same `block` road grammar cuts its two side streets and
  the rear lane at different x per seed (9003: side streets at x 25.0 and -80.2; 9104: -20.0 and +75.2; 9205:
  -21.0 and +76.2), identically in both missions for a given seed; and the far side's deal of Empties differs by
  seed in archetype and spot (0 of 13 Empties at the same spot between any two seeds on the urban street, 0 of
  26 on the strip).
- Both missions are `site_shape: strip`; no other shape was in the set, so what `site_shape` varies was not read.

**So 105's premise holds, with its number:** one arrangement of the mission's buildings in six plans across two
briefs; the seed moves the streets and the backdrop around it and never the row. The item's next step is its own
-- a plan grammar that varies where the buildings stand and which faces address the street, measured against
sightlines and cover before it ships. OPEN on the roadmap, measured.

## 80. Deli Counter's one-mesh-in-VRAM discipline is not carried past the export; its two next pieces were dead

**What it found (2026-08-29):** Deli Counter shares one mesh datablock across identical modules and the art pass
keeps it (241 instances of 36 PackedScenes on bank_block_001), and the renderer still draws 241 instances; the
MultiMesh exporter (`dressing_scene.py`) was called by nothing and Patina's `instances.json` was read by nothing.
What would close it, in its own reordered list: world-space UVs on the kit materials first; MultiMesh second and
only for dressing, the light budget measured before any wall follows; `instances.json` third, "still worth
having, no longer the cheapest thing available". Its status said `--triplanar` lived in `walk_themed.py` as a
runtime flag that printed "NOT what ships", with the fill rate unpriced.

**What shipped since, each read off the checkouts and 9314's package:**
- **World-space UVs ship on every kit module.** `zoo_worldskin.gd` is the modules' import script -- "World-space
  UVs on kit modules, applied AT IMPORT and baked into the .scn" -- and the package runs it since Level Factory
  0.57.0 ("the package runs the script it was already shipping"; 0.58.0 keeps the tile period). 9314's package
  carries it in all 13 building folders; `walk_themed.py` and its runtime flag are gone.
- **MultiMesh for the dressing and the backdrop.** `dressing_scene` is called by `dressing_layer.py` and
  `backdrop_layer.py`: 9314's export log reads "surface dressing: 4,439 instances of 4 meshes, 4 draw calls" and
  "backdrop: 297 instances of 7 module(s) ... 25 draw calls".
- **The walls were not MultiMeshed, and the tension the item named was answered the other way.** Level Factory
  0.143.0 (roadmap 182) merges an Empty's modules one mesh a side per material -- 686 draws and 0.88 ms saved on
  cold run 9162's level, hiding all 25 Empties having bounded it at 816 and 1.87 ms -- which trades the shared
  datablock for submissions, by the rule CLAUDE.md records from the 2026-09-16 measurement: draw calls are the
  budget, not triangles. The mission's buildings keep their instanced modules. The per-mesh light budget the
  item said had to be measured first is measured by what the renderer pairs (roadmap 147's record: no room tile
  over 8 on 9308's package).
- **`instances.json` is still read by nothing** (0 files in Level Factory's packages mention it), which the item
  itself placed third and optional once the other two existed.

CLOSED on the roadmap; the per-instance channel that remains unwired is roadmap 76's question, not this one's.

## 99. A theme has to exist in two repos, and only two do

**What it found (2026-09-05):** nine Pixelcoat profiles, four Zoo styles with real species coverage, and an
intersection of two (`rockay`, `delco`); `center_city` and `industrial_flats`, Zoo's best-covered styles after
`rockay`, had no profile and could not be asked for; every brief used one of the two. What would close it: a
decision and then content -- profiles for the two covered styles (cheapest), or species styles for the seven
uncovered profiles, or a shared vocabulary with the doctor reporting the intersection rather than two lists.

**Measured today** (the doctor's `themes` row in install test 9's setup log; `packages/tools/themes.py`; the
cold-run briefs): Pixelcoat carries 13 profiles -- `bank, card_shop, casino, center_city, delco, delco_1997,
industrial_flats, rockay, rockay_civic, rockay_retail, rockay_service, stadium, street` -- so the cheapest option
happened: `center_city` and `industrial_flats` have profiles, and the themes that exist on both sides are four,
rockay (128 of 133 species), center_city (126), industrial_flats (126) and delco (119). The reconciliation the
item called a "shared vocabulary" exists as a rule rather than a list: `themes.zoo_style_for` resolves a brief's
theme to a Zoo style by name, then by the name minus a trailing qualifier -- `delco_1997` -> `delco` -- the
fallback Zoo 0.57.0 taught the theme path, which is why every level builds under a theme Zoo's style list does
not carry. The doctor still prints the two lists and the partial styles, not the intersection. And variety
between levels is still what the briefs ask: of 301 cold-run briefs on disk, 298 ask for `delco_1997` and 3 for
`delco`; no brief has asked for `center_city`, `industrial_flats` or `rockay` since they became askable.

NARROWED on the roadmap: the ceiling moved from two themes to four; what the doctor reports and what the briefs ask
for have not.

## 107. Level Factory should own the final export, not Lot

**What it asked (2026-09-06):** not to move code first but to write down what the export needs from Lot, "because
the current answer is spread across three regexes and a docstring, and the list itself is the deliverable"; then
a manifest Lot emits describing its site, which the exporter consumes instead of pattern-matching paths.

**The list, read off `packages/exporting/export.py` at 0.215.1** (its 21 uses of `themed_site_dir`, the output of
Lot's `themed_site_assemble` job):
1. **`site.tscn`, the assembly scene.** Copied to the package root as `site.tscn` (every `res://site.tscn` Lux
   and the entry scene name must resolve to the assembly). Read twice before that: `_standing_lot_ids` finds
   every `lot/<id>/site.tscn` it names through `_LOT_SITE_REF` -- the building packages the scene stands, which
   is what ships since 0.207.0 -- and `_assembly_building_dir` decides whether the composed root belongs under
   one lot from three facts read off disk: an assembly scene exists, it names exactly one `lot/<id>/site.tscn`,
   and the composed root has no `lot/` of its own. `_ROOT_SITE_REF` matches the assembly's own
   `res://site.tscn` reference.
2. **Three sibling directories, copied whole:** `skins/` (the ground's Pixelcoat maps, Lot 0.58.0), `cover/`
   (the cover modules, Lot 0.59.2), `signs/` (the shop signs, Lot 0.69.0). The exporter's own comment: "THE LIST
   IS THE CONTRACT ... a new sibling directory in Lot means a line here", after cold run 9039 shipped a street
   whose signs were in none of them.
3. **Every `*.obj` beside the scene,** copied by name: the road paint, the wires, the drains (Lot 0.114.0 and
   after), after cold runs 9234 and 9235 shipped the scene without them.
4. **`responders.json`:** which vehicle scenes to mark dynamic for the bake (`responder_vehicle_scenes`) and the
   arrivals the package records (`write_responder_arrivals`).
5. **`*.provenance.json` sidecars** beside each copied file, and Lot's site gameplay record (`site.site.gameplay.json`,
   reached through the staged inputs rather than this directory) for `gameplay_anchors.json`.

Lot's job emits none of this as a manifest: its `out/` holds the scene, `lot/`, `cover/`, `signs/`, the OBJs,
`site.markings.json`, `responders.json` and the provenance sidecars, and the exporter's contract with it is the
list above, held by the closure gate (which refuses a package with an unresolved reference) rather than by a
schema. The regexes are two, not three, since 0.207.0 folded the third into `_standing_lot_ids`.

NARROWED on the roadmap: the list exists; the manifest Lot would emit and the exporter would consume is the
design step still owed, and it is Lot's and Level Factory's together.

## 84. Zoo computes per-vertex wear, exports it correctly, and the engine does not use it

**What it found (2026-08-29):** 1,896 kit surfaces carried COLOR_0 and 0 of 19 materials read it -- Godot's glTF
importer never sets `vertex_color_use_as_albedo` -- and the measured counter-argument that forcing it on for the
kit multiplies the 2 m module signature by 3.8x, because the wear is computed per module. "The fix is a decision
rather than a flag."

**The decision was made and built, read off the checkouts:** Level Factory 0.86.0's `zoo_worldskin.gd`
(`_vertex_colour_albedo`) draws COLOR_0 as albedo on every GLB that is an object rather than a tile -- a car, a
container, a chair, a lamp -- for any material some surface of which is not white, and leaves it off for the kit
(`KIT_PREFIXES`) and the tiled families (`ceiling_`, `floor_`, `roof_`, `_dressing.glb`), which is exactly the
3.8x argument applied: objects wear, tiles do not. `tests/unit/test_vertex_colour_and_clutter_skins.py` pins both
halves (every object GLB runs the pass and no tile does; the flag goes on only for tinted materials with colours
on every surface), from the measurement that 0 of 1,650 surfaces drew it on walk 9052_rain before. Zoo 1.59.0
then built on it -- a car's paint rides its vertices, measured on the eight cars of cold run 9141 -- which is the
engine using the layer.

CLOSED on the roadmap. The kit's own wear stays off by that decision; that the wear repeats per module is item
79's root cause, as the status already said, and stays there.

## 74. Every wall in every building is the same 2.00 m module, and it gets worse the longer the facade

**What it found (2026-08-29):** `tools/repetition_census.py` over twelve shipped buildings: `longest_identical_run`
median 19, range 7 to 28; the walked bank_block_001 at 14 was a good day. What would close it: the vocabulary
growing with the span (a bay library, `wallCorner`) or per-instance work landing with a second ruler that reads
appearance -- "not a threshold".

**Re-measured** (`repetition_74_9314.out.txt`, `repetition_74_9314.json`, the same instrument on cold run 9314's
three mission buildings as composed): deli_a01 347 wall instances, 27 stems, 64 forms, reuse 5.42, worst run 18
(`ext_-1_N`, 21 segments, 86 % one form); office 196 / 14 / 25 / 7.84 / 11; pharmacy_a01 73 / 13 / 24 / 3.04 /
7, where the baseline read it at 67 / 12 / 20 / 3.35 / 7. Every run's pitch is 2.00 m. In the ruler's own terms
nothing moved, and it says why: it measures the form vocabulary, and what shipped since is per-instance --
world-space UVs on every module (roadmap 80's record), which end the per-module texture restart without changing
that a run of eighteen is eighteen placements of one mesh. The second ruler, one that reads appearance, still does
not exist; the Empties, merged one mesh a side, are outside this ruler altogether.

OPEN on the roadmap, re-measured: the number is today's, and the item's two closing moves are still the two.

## 76. Every mechanism this factory has for making two copies of one module look different is implemented, and none of them is wired in

**What it found (2026-08-29):** four mechanisms read in the code, none reachable from a brief -- Patina's theme
(`patina_theme` is not a brief field, so every level gets `default`), `art_mode` hardcoded `vertex-color`,
`--slot-variation` never passed, Pixelcoat's generation-7 stack unreachable from a theme -- with world-space
projection already counted in the status as a result (88, confirmed by eye). What would close it: not all four,
and a decision about which LAYER owns variation that the item deliberately deferred until 75's rebuilt level had
been looked at.

**Re-read 2026-10-15, at Level Factory 0.215.1 against cold run 9314:**

1. `apps/cli/commands/__init__.py:1123` and `:1131` still read `getattr(model, "patina_theme", "") or "default"`
   under the same comment (`:1120`); `patina_theme` occurs in `schemas/mission.brief.schema.json` 0 times. 9314's
   Patina job ran `-m patina.cli deli_a01.glb --mode vertex-color --out ... --theme default`.
2. `"art_mode": "vertex-color"` at `:1117` and `:1130`, both branches.
3. `slot_variation`, `slot-variation` and `instances.json`: 0 hits in `level_factory/packages` and `apps` outside
   tests. Patina still implements the pass (`patina/cli.py:241-248`, `slots.apply_slot_variation`).
4. The planner's Pixelcoat job is `theme-library --theme delco_1997` (9314's `job.log`), the profile path through
   `material_grammar.build_theme_library`. That path reaches two of `weathering.py`'s six functions --
   `pooling_mask` and `wetness_mask`, the wet maps (Pixelcoat 0.46.0, pooling 0.49.0) -- and none of
   `edge_wear_mask`, `grime_mask`, `streaks`, which only `pipeline_generation_7.py` calls, reached from
   `process --mode generation_7` or `build <recipe>`; the `variations` maps likewise. So the wear half is where the
   item left it, and the wet half crossed over -- uniform per material, which is not two copies looking different.

**What moved under the item:** 75 closed by measurement the day it was filed (spectral power at the 2 m pitch
1548 -> 1044, vertex layer held); 84 decided the vertex-wear layer -- objects wear, tiles do not, the kit's COLOR_0
stays off; and since Level Factory 0.143.0 the Empties reach the package as one mesh a side per material: on 9314,
10 of the 13 buildings, 6,490 surfaces merged into 136 meshes (`merge_empties.json`, `lf.merge_empties.v1`, `ok`).
That changes the trade the item weighed per-instance variation against: a merged side is one ArrayMesh with its
own vertex arrays, so vertex-colour variation applied before the merge costs the merged mesh nothing it does not
already pay, and the instancing economy now covers the three mission buildings (deli_a01's 347 wall instances of 27
stems, 74's record), not the level. The layer question stays unsettled here, as the item asked.

OPEN on the roadmap, re-read: the four mechanisms sit where they were at today's line numbers, the wet half of
the fourth crossed over, and the ground the deferred decision stands on has moved.

## 57. Asset boundaries are implementation details; architectural boundaries are what the player should see

**What it found (2026-08-23):** a grammar, not a patch -- five pieces, the walk as judge each time: edge metadata
in the slots contract, a corner module family, one demonstrated continuity mechanism with its cost measured
against the instancing economy, weathering moved to building space, and a mid-distance instrument. Status:
FRAMED, UNWORKED, and never revisited.

**Re-read 2026-10-15:**

- **The corner:** shipped without a family. Deli Counter 0.102.0 / 0.102.1 (item 58) insets each exterior run and
  seats a `wallEnd` unit post at each corner: ENV_CORNER_OPEN 988 -> 0 over 124 buildings, zero new modules, the
  gate catching its own regression. `deli_a01.slots.json` today: 59 `size_mod: end` posts against 478 full
  modules; `wallCorner` 0 hits in `deli_counter.py`.
- **The continuity mechanism:** shipped. World-space triplanar on every kit material, Level Factory 0.57.0 (item
  88): texel-density mismatch 47x / 66x / 12.5x -> 1.0x over 3,554 surfaces, confirmed by eye. Its cost against
  the instancing economy is nil by construction -- the module stays one GLB instanced N times, the projection is
  an import flag -- and its frame cost (three samples a texel) has not been priced on the station harness; the A/B
  instrument is `tools/walk_themed.py --triplanar`, a walk project. It forecloses a trim-sheet atlas (88's record)
  and needed an exception for a lit face whose picture is its UVs (LF 0.140.0).
- **Edge metadata:** not there. Slot manifest 1.3.0's fields are `role`, `size_mod`, `style`, `material`,
  `material_in`, `wall`, `story`, `facing`, `fit`, `transform`, `kit_axis`, `current_ref`, `species`, `variant`,
  `stock`, `form`, `room`, `interactive` -- provenance and fit, nothing that says what an edge means.
- **Weathering in building space:** not there (76's record): Patina's per-slot pass unwired, the kit's vertex wear
  off by 84's decision, Pixelcoat's wear / grime / streaks on the recipe path only. World triplanar makes a
  texture's grime continuous across a seam; nothing responds to the building.
- **The mid-distance instrument:** not there. 78's four instruments measure appearance and none is pointed at the
  kit path; 74's re-measure today says the ruler that reads appearance still does not exist.

Two of five, and one fact bearing on the item's core trade: for the Empties -- 10 of 9314's 13 buildings -- the
per-side merge (LF 0.143.0) has spent the instancing economy already, so there the seam is one mesh's texture,
not N copies of one.

NARROWED on the roadmap: 2 of 5 shipped, each judged by the walk; the three left are named with what stands in
their place today.

## The nine items that had no status line

`roadmap_status.py` reported nine open items "resting on a sentence rather than a status line": 19, 20, 24, 28 and
35 never had one (they predate the convention), and 44, 45, 153 and 154 have a status block the index cannot read
because it runs to several paragraphs. Each was re-read 2026-10-15 against cold run 9314's package
(`workspaces/cold-9314-ws/.level_factory/exports/LF_urban_row_001.portable-godot`), today's built library (158
specs under `deli_counter/build/`) and the tool repos at their current versions, and given a dated status line.

## 19. Every tool grew a Godot half before there was a DAG to say who owns what

**What it said:** at least four editor/runtime addons across the toolchain, none of which survives a bare folder
drop; the honest default is that one addon ships, and it is Lux; the lighting chain is the pattern done right.

**Today's package:** no `addons/` directory and 0 `res://addons` references in any scene or resource. It carries
`runtime/lux` (25 scripts, 4 shaders, 7 presets, referenced by `presentation/lux.applied.tscn`) and
`runtime/skymint` (2 scripts, 1 shader -- the sky provider that arrives with Lux, Level Factory's changelog). Zoo's
half is one import script at the root, `zoo_worldskin.gd`; Patina's, Pixelcoat's and Deli Counter's Godot halves
ship nowhere in it; 0 `Decal` nodes, so the decal question the item left open is answered by absence (Patina's
`decals.py` exists and reaches no package). The exterior half of the lighting chain, refuted in the body, was
fixed by Lot 0.79.0 (the poles are the anchors, worst distance 0.0000 m), and the lights reach the package
(`light_bake.json`, 238 lights in the applied scene -- 56's record).

CLOSED: the rule the item proposed is the shipped package's state.

## 20. Patina's Godot half is a renderer from before Lux was one

**What it said:** retire `ps1.gdshader` and the Patina plugin so the vertex-colour channel means one thing
everywhere; the texture-ownership question (Patina posterised sets against Pixelcoat) left open.

**Today:** the files still exist in the repo -- `patina/godot/addon/patina/` (plugin, dock, apply script, shader)
and `patina/godot/shaders/ps1.gdshader`, their README still saying the half "has not been walked in the editor
yet" -- consumed by nothing in any tool repo (0 references outside that folder and the docs) and shipped in no
package (9314: 0 addons; its 5 shaders are Lux's and SkyMint's). In every package COLOR_0 has one reader,
`zoo_worldskin.gd`'s `_vertex_colour_albedo`, albedo on objects and off on tiles (84). The open question settled
itself: `art_mode` is `vertex-color` on both branches (76), Patina's texture half never runs, and Pixelcoat is the
skin. The "connects" half of the migration (a PS1 preset beside Lux's, `shell.patina.json` feeding Lux uniforms)
was overtaken by the walker's realism call.

NARROWED: the ambiguity is gone from every package; left is deleting the dead folder, a Patina release.

## 24. Lux gives runtime scaffolding an `owner`, which is what bakes it into a saved scene

**What it said:** owner is the whole difference between runtime scaffolding and a saveable member; nine
assignment sites; the multiplication (four suns, three stacks) never isolated; a second WorldEnvironment in the
editor.

**Today:** 21 `owner =` sites across `lux/addons/lux/runtime/` (environment 1, fixture spawner 2, light loader
12, lighting 1, post-FX 5); 18 of the runtime scripts are `@tool`, and 15 of those ship in the package under
`runtime/lux`, so a package opened in the editor and saved still has the trap the item describes. The second
WorldEnvironment is gone: `ensure_world_environment` searches the scene for an existing one before creating its
own (Lux 0.49.0, for a sky provider). The multiplication is still not isolated, and the call-site rule the item
asks for is not written.

OPEN, re-read: what would close it is that rule, proven by loading a shipped `lux.applied.tscn` in the editor,
saving, and diffing.

## 28. The VRAM question is about zoo's GLB embedding, not about pixelcoat

**What it said:** Deli Counter shares meshes (333 instances, 14 GLBs on rockay), Zoo shares materials, and the
gap is `export_format="GLB"` embedding the same pack into every module file -- "14x, not 1x" -- a Zoo export
change, read off the exporter and never counted.

**Counted** (`embedded_textures_28.py`, `embedded_textures_28_9314.out.txt`): Zoo 1.2.0 (2026-09-21, "a pack
texture is one file, not sixty copies", `share_textures`) writes a pack's images beside the GLB in `_tex/`, named
by content hash, and the GLB references them by `uri`. On 9314's package: 329 GLBs, 0 embedded images; 314
reference 1,250 images by uri, 277 distinct files, 8.9 MiB on disk, 0 missing, 4.51 references a file; 94
distinct images by content, 45 of them written in more than one `lot/<id>/art/zoo/_tex/` folder, one in 17. The
duplication left is per building folder, not per module. What the engine keeps resident is 238's question
(`docs/findings/texture_memory/`: the reflection atlas was 82 % of it). The machinery the item pointed at --
`pack_importer.gd`'s shared `.tres`, `atlas.py` -- is not what did it.

CLOSED: the export change the item asked for shipped, and the count says so.

## 35. The graybox/art relationship: it is a SWAP, and most of the recommended shape is already the contract. What is missing is the library

**What it said:** the swap contract's five agreements already hold; the library lacks interior and exterior
corners, columns, beams, stair flights and landings, parapets, thickness transitions and every seam-management
piece; the material guidance is inapplicable to geometry with no UVs.

**Today, on the 158 built specs:** the contract stands (slot manifest 1.3.0). Roles: wall 24,768, prop 9,947,
window 1,453, doorway 1,001, floor and ceiling 586 each, breach 271, roof 146. Exterior corners: a `wallEnd` post
at every corner (58: 988 -> 0 open; Zoo also carries a `wallCorner` species sized from 950 posts, which Deli
Counter never emits). Parapets: 1,910 `parapet_*` slots. Stairs: 1,044 stair-named slots, `stair_rail` as a
species. Columns: Lot's `col` nodes on the sites (239 on 9314's). Piers, plinth (0.45 m) and cornice (0.12 m) on
every solid wall module (`relief_parts`, 75). Coping, base course and curbs as Patina dressing (248). UVs on
every module, world-projected (88). No species or slot is named for a beam, a thickness transition, a baseboard,
crown trim or a fascia.

NARROWED: most of the list exists; the four pieces above do not.

## 44. The green boxes could be cars, and the collision would not change

**What it said (2026-09-11):** 721 of 1,443 placements name a species Zoo has and it fits 142; scope (1) Deli
Counter stamps a species hint on each prop slot, (2) Zoo builds it at the slot's dims or the `prop` box and says
which, (3) the run species gain a bays mode.

**Today:** (1) shipped -- 8,458 of 9,947 prop slots across the 158 specs carry `species` (85 %); 9314's three:
deli_a01 127 of 142 (22 species), office 60 of 73, pharmacy_a01 26 of 28. (2) shipped -- each `<id>_kit.built.json`
records `species_fallbacks` with the reason: 9314's three builds record one (deli_a01's `loading_pallet_stack`,
4.50 x 2.50 x 1.50 m outside the species' range, built as `prop`) and 0 missing; the stems carry the species
(`prop_counter_delco_1997_05`, ...), and 9 of deli_a01's 75 prop modules are plain `prop_`. (3) partly --
`counter` (`bay_max` 4.0), `shelving` (2.4) and `teller_line` (2.0) repeat by bays; `bench` has no bays and no
`locker` species exists. The 2026-09-11 fit count is not re-run: the hint changed what it would mean, and today's
figure is the fallback count.

NARROWED: (1) and (2) shipped, (3) three of five; the species' look is the walker's.

## 45. Large playable surfaces are visually flat, and the fix is not more grass

**What it said:** a collisionless instanced dressing layer, its manifest the deliverable, with a field list and
a definition of done.

**Today:** the layer exists end to end. Patina's `surface_dressing.py` writes the manifest -- `surface_zone_id`,
`asset_set`, `placement_mode` (scatter / seam / cluster / anchor), `density`, `scale_range`, `height_band`,
`collision_policy`, `shadow_policy`, `seed`, `quality_tier`; not `yaw_range`, not `exclusion_tags` -- Lot's
`site_surfaces.py` names the zones, Zoo builds the clutter species the asset-set file names, and Level Factory's
`dressing_scene.py` ships it as MultiMesh in its own scene (9314: 4,439 instances in 4 draws,
`urban_row_001_dressing.tscn`; the writer emits no collision node). The lock (LF 0.31.0) protects collision. The
test the item names -- hide the layer and the level plays the same, Laser Tag the judge -- has not been run as
an A/B, and "no visible uniform scatter from primary views" is the walker's.

NARROWED: built and shipped; two manifest fields and the A/B are what is left.

## 153. A street reads as ordered when its furniture says where cars and people go, and the lot has none of that furniture yet

**What it said:** three layers (markings, the kerb line, waiting places) and the cars, with step zero being
roads rather than paths; closed by a walker's eye-height judgement.

**Today, 9314's seed_9104 site** (`site.slots.json`, `site.markings.json`): step zero shipped -- 4 roads, 10
sidewalks, 4 kerb cuts, 6 frontages. Markings: crosswalk bars 34, stop bars 4, centre line 21, edge lines 12,
bay ticks 54; no arrows, no yellow kerb face. The kerb line: streetlight 2, traffic signal 2, sign post 7,
fire hydrant 2, parking meter 47, litter bin 4, newspaper box 4, mailbox 2, utility pole 12 with wires
(`site_wires_*.obj`), pole flyers 10, payphone 3, chain-link fence 8; no bollards placed (the species exists),
no utility cabinet, no bike rack. Waiting places: bus shelter 3, bench 3, 46 street trees in grates (honey
locust 32, pin oak 7, London plane 7); no planters. Cars: 22 `simple_car` parked in the bays the ticks draw, 3
cruisers, a step van. No walk note has judged the street as one to drive and cross.

NARROWED: every layer has shipped pieces; the six absent ones and the judgement are what is left.

## 154. The buildings are designed all at once, and Delco buildings are not

**What it said:** the decade is a layer on older fabric; five asks routed to five tools, the two structural ones
Deli Counter's (the twin, the accretion); closed by a walk that reads the place as built over time.

**Today:** the twin exists as one archetype, `twin_a01` (whether its halves differ is unmeasured); the accretion
has no vocabulary (0 hits). Surfaces: `siding_delco`, `shingle_delco` and `fieldstone_delco` grammars exist;
glass block and EIFS do not. The objects: utility poles and wires shipped (240; 12 poles on 9314's site),
`satellite_dish`, `shop_awning`, `security_camera` and `roller_grill` are species; window air conditioners and
security bars are not. The corridor: 241's urban type stands buildings 2.0 m off the sidewalk among mid-rises;
buildings at the road with parking beside or behind is still not a Lot plan. Patina's per-instance
differentiation is unwired (76). The judgement is not recorded.

NARROWED: one structural ask exists as an archetype, the other has no vocabulary; the surfaces and objects are
half there.

## 178. The instruments report and nothing blocks, and that is one defect rather than four

**What it said (2026-09-24):** four instruments, all reporting, none blocking -- the z-fight gate printing FAIL
and ERROR on five runs called zeros; Lot's isolation warning on 65 of 79 sites; Lot's `objective_approaches` at
0 on 38 of 79 and never above 2; `test_navgate_population` blocking only after a library rebuild -- and a fifth
on 2026-10-11, a bake that failed shipping the package unbaked and counting zero. Three shapes: fires-always-
blocks-nothing (a threshold nobody chose), blocks-but-rarely-runs, and deliberately non-blocking with a frozen
baseline (the model). The decision owed per instrument: block, freeze-and-fail-on-new-entrants, or delete.

**Re-measured 2026-10-15, per instrument:**

- **The fifth, the unbaked package:** `tools/cold_drive/cold_drive.sh` stops the run when the package was asked
  to bake and `light_bake.json`'s `ok` is not true (root 4bf7bb5, 2026-10-11, the day it was found -- "the
  bake's own report decides"); Level Factory 0.178.5 retries the editor bake (`BAKE_ATTEMPTS` 2) and records
  every attempt. 9314's record: `ok` true, one attempt, 81.4 s in the editor, 215 room fills. Shape 1 became
  shape 3's cousin: a report that is read and acted on.
- **`test_navgate_population`:** `_live()` reads `deli_counter/build/*.navgate.json` and the tests skip only when
  `build/` is absent. On this machine `build/` holds 157 of them, newest 2026-10-15 08:44 (the library was
  rebuilt for Deli Counter 0.223.0), and the suite that ran after it passed them. The cadence is the library
  rebuild's, which this month is most Deli Counter releases; between rebuilds the comparison is against the last
  one. Still shape 2, with a shorter period.
- **Lot's isolation warning** (`lot_intel_178.py`, `lot_intel_178.out.txt`): `site_tactical.build_graph` joined
  the buildings that share a road in Lot 0.77.0 (2026-09-24, the day this item was filed: "the site graph
  includes the street, because the buildings do"), which was the objection to gating it. Over the 324 cold-run
  sites on disk, in 107 workspaces: 4 read an isolated building, all four in one lot-shape experiment
  (`shape-sweep-9500-ws`: `shape_courtyard_9500`, `shape_l_9500`, `shape_row_9500`), 0 on any cold run proper.
- **Lot's `objective_approaches`:** over the same 324 sites, 0 on 14, 1 on 16, 2 on 289, 3 on 4, 4 on 1 --
  where the item read 0 on 38 of 79 and never above 2. `site_layout_lint` S5 still warns only. A threshold is a
  design call, not a measurement.
- **The z-fight gate:** fires and blocks nothing, still. 9314's `presentation_compose` composed 17 scenes and
  printed `z-fight gate [FAIL]` with `ERROR: coplanar surfaces detected -- the package would flicker` for
  deli_a01 (2 pairs in 755 solids) and office (2 in 425), `[OK]: 0` on the other 15, and exited 0. Deli Counter
  0.198.0 judges a pair by its facing side (177: 436 pairs were 5), and the decision -- block, warn or delete,
  on pairs no frame has shown -- is the walker's and still owed.

Two of the five changed shape (the bake blocks, the navgate test runs every rebuild), two moved under a Lot
fix and read near zero, and one is where it was.

NARROWED: what is left is one walker's decision (the z-fight gate), the isolation warning's graduation by 59's
rule once the four experimental sites are attributed, and a threshold for the approaches, which is design.

## 20, closed the same day: Patina 0.32.0

The leftover named above -- deleting the dead folder -- shipped as Patina 0.32.0
(`patches/patch_patina_godot_half_gone.py`, proof in `patches/patina_godot_half_gone/`): `godot/` removed (8
files), the six texts that described the half as alive reworded, `shell.patina.json`'s `shader` block kept for the
schema. Found on the way: `patina/version.py` said 0.30.0 against `VERSION`'s 0.31.0, so every 0.31.0 manifest
and GLB carried `generator: "Patina 0.30.0"` -- 9314's `deli_a01.patina.json` does. Both read 0.32.0 and
`tests/test_version_file.py` pins them together; the proof script shows it failing with `version.py` flipped back
to 0.30.0. Suite 402 passed, 1 skipped.

CLOSED on the roadmap.

## 178, the four isolated sites attributed

The four sites Lot's isolation warning still fires on are all from `shape-sweep-9500-ws`, a lot-shape
experiment whose workspace was locked on 2026-09-23 -- the day before Lot 0.77.0 joined buildings that share a
road, and before Level Factory wrote `building` on a door path. Their `site.json` door paths carry `a`, `b` and
`width` only (`{"a": [-28.0, -41.15], "b": [-28.0, -62.6], "width": 4.0}`), so `street_members` cannot tell whose
door reaches the sidewalk; a site written today carries `"building": "b0"` on every door path (9314's seed_9104:
9 of its 10 paths). The warning is reading an old spec shape, not an unreachable building: on every site written
by today's Level Factory, 0 of 320.

That is the attribution 59's rule wanted before the warning could graduate WARN -> FAIL. The graduation itself
is a Lot change with a cold run behind it, and is not made here.
