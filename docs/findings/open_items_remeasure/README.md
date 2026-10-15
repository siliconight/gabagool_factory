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
