# A fixture's same-material parts, merged inside it (roadmap 233)

**The question.** A building's fixtures ship as one GLB of many placements,
exported unmerged on purpose: merging across fixtures would cost culling.
So a fixture whose parts share a material pays a draw for each part. Which
fixture species carry two or more parts in one material, and how many draws
does one placement of each shed if its parts merge inside it and never
across two?

**DRAFTED AND MEASURED ON A CLONE, NOT YET LANDED OR PRICED.** The patch is
Zoo 1.100.0 (`patches/patch_zoo_fixture_merge.py`): `merge.pack_by_material`
takes each part's placement as a unit, and `build.build_fixtures` exports
merged by it. A cold run prices it in a level.

## Measured on Zoo 1.99.0 (`parts_probe.py`, `parts_1.99.0.txt`)

Each species in `core.fixtures.FIXTURES` built at its genome's default
corner through the kit path, in Blender 5.1.1, its visual meshes listed by
material:

| species | meshes | materials | a placement could shed |
|---|---|---|---|
| streetlight | 4 (pole, base, head in one metal; lens) | 2 | 2 |
| pendant_fixture | 3 (cord, socket in one metal; bulb) | 2 | 1 |
| sign_box | 3 (arms, cabinet in one metal; face) | 2 | 1 |
| wall_pack | 3 (arm, body in one metal; lens) | 2 | 1 |
| canopy_lights, club_fixture, dome_fixture, fluorescent_fixture | one mesh a material | -- | 0 |

## The layer, merged and not (`layer_count.py`, `layer_merge_off.txt`, `layer_merge_on.txt`)

Cold run 9239's three buildings on restaurant_row_001, built on a clone of
Zoo 1.100.0 from Deli Counter's own lights manifests with each job's sign
pack (theme delco_1997), once merged and once with `--no-merge-parts`.
A submission is one primitive of one visual mesh node:

| layer | fixtures | unmerged | merged | shed | LuxEmit markers, both |
|---|---|---|---|---|---|
| deli_a01 | 116 | 257 | 232 | 25 | 116 |
| office | 61 | 128 | 122 | 6 | 61 |
| pharmacy_a01 | 24 | 52 | 48 | 4 | 24 |

35 fewer, the count the census above predicts: 27 pendants, 3 sign boxes
and 5 wall packs, one each. In the deli the pendants' metal is 23 meshes
where it was 46, the sign box's and the wall pack's 1 where each was 2;
every lens, the domes, the troffers and the sign's face count the same
both ways. No streetlight is in the figure: Lot places a street's lamps as
site furniture (`lot/site_furniture.py`'s `_piece`, species `streetlight`),
which Zoo builds as a module through the kit path, and a module's parts
already merge by material. A streetlight reaches this layer only through
a lights manifest that asks for one.

What a merge must keep, read off the consumers: Lux finds a failing
fixture's lens by MATERIAL name (`M_*_Lens`, `_Diffuser`, `_Face`) and by the
mesh's distance to its lamp (`lux_failing.gd`'s `find_lens`), and spawns
lamps at the `LuxEmit_*` empties; nothing in Level Factory, Lux, Lot, Deli
Counter, Patina or the factory's tools reads a fixture part's object name.
A lens is the only part in its material in every species above, so it
ships as itself.
