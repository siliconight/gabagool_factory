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
