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
