# Texture memory and repeated surfaces: the tiling guide checked against the repo

A read-only research pass, 2026-10-19, over `docs/reference/Texture_Tiling_Variation_Blender_Godot_4_7.md` -- which
the walker paired with roadmap 238 (texture memory) and Pixelcoat's Quake II notes -- and the repository. **V** = it read
the cited place; **I** = it inferred. It ran the finding's own `texture_census.py` and three stdin censuses over cold
runs 9334-9337's packages, and wrote nothing. Its report, as given.

## 1. Verdict

**The big texture-memory cut has already happened, and it was mostly not the textures.**
- Of cold run 9245's 515.6 MiB, about 257 MiB was the reflection atlas; Level Factory 0.198.0 cut that to 8 MiB.
- Every level texture has shipped S3TC-compressed since Level Factory 0.190.0 (the walker's "compressed everywhere").
- A current package reads 65.6 MiB after warm-up and about 76 MiB in play: under item 238's 100 MiB bar.

**What is left in the level's own ~30 MiB is duplication, not format.** In 9335's package, 458 image files are only 118
distinct images, because every building ships its own copies of each texture pack. One texture per content is the
largest remaining cut: about -10 to -12 MiB on a multi-building lot, with no change to the look.

**The biggest look gain is a different move, and it costs almost no memory.** The factory has done the guide's first
step (clean base tiles at one world-projected density) and its triplanar step. It has no variation at any scale above
the 2-3 m tile: every "macro" band sits inside the tile, and wall tiles repeat exactly once per 2 m module. The guide's
steps 3-4 would add it for under 1 MiB: on the ground a broad mask plus a second seed of the same recipe; on walls a
tint from world position in vertex colour; marks placed where something caused them.

**One rule joins them:** get variation from low-frequency data, not from more texture resolution. And the walker's "too
soft or noisy" may lead to filtered (realism-style), denser or uncompressed skins, any of which is only affordable after
the deduplication.

## 2. Where the 516 MiB went

**Cold run 9245** (restaurant_row_001, Level Factory 0.179.0): 515.6 MiB of textures at load; 546 of 579 import
sidecars lossless, i.e. uncompressed in VRAM (V: `docs/findings/texture_memory/README.md:19-25`; `census_9245.txt:3`).
The first attribution, to the sky's 140 images, is RETRACTED: the sky is not resident (V: README.md:60-70).

**Cold run 9273** (same mission, Level Factory 0.197.0), one fresh process per arm, a control reading 314.6 MiB twice
(V: `split_9273.txt:9-48`; README.md:84-108):

| Part | MiB |
|---|---|
| Reflection atlas (64 slots x 256^2, half-float, for 23 room probes) | ~257 (82 %) |
| LightmapGI (1024^2 x 16 layers, BC6H) | 21.3 |
| The level's own textures (57.3 - 21.3 - 5.7) | ~30 |
| Empty window | 5.7 |
| Dressing / backdrop / shadow atlases | 1.3 / 0.7 / 0 |

**Now:** with 0.198.0's atlas (32 slots x 64^2), cold run 9274 holds 65.6 MiB after warm-up; in play, 9276 reads 76.0
MiB, about 8 MiB of it unattributed (V: `PIPELINE_ROADMAP.md`, item 238; README.md:163-187). Since 0.190.0 every shared
texture, skin and sign ships `compress/mode=2` with mips, normal maps red-green compressed (V:
`level_factory/CHANGELOG.md:1058-1100`). In 9335 (0.219.0), 458 of 458 level images are VRAM-compressed,
`high_quality=false`, S3TC (V: census; `skins/asphalt_delco_albedo.png.import`); only SkyMint's 139 (not resident) and
4 validation overlays are lossless. Sizes: 250 at 256^2, 128 at 128^2, asphalt 512^2, road paint 1024^2 RGBA; the
realism atlases are non-power-of-two (e.g. 470x1307).

**The lever item 238 lists as left, "compression of the level's own ~30 MiB", is already spent** (I: 9273 postdates
0.190.0). What sits in that 30 MiB is duplication:

| Package | Files | Distinct images | Est. BC + mips as shipped | Est. deduplicated |
|---|---|---|---|---|
| 9335 restaurant_row | 458 | 118 | 23.3 MiB | 11.5 MiB |
| 9336 urban_row | 417 | 121 | 21.5 MiB | 11.2 MiB |
| 9337 gas_block | 466 | 123 | 26.4 MiB | 14.7 MiB |
| 9334 county_hospital | 89 | 67 | 7.5 MiB | 6.9 MiB |

Counts V; MiB I (BC1 at 0.5 B/px, x4/3 for mips). In 9335, concrete_delco's albedo alone is 31 files of one image. Item
28 counted this per-building duplication and left residency to 238; the engine does not deduplicate.

**Not measured:** how much of 9245 -> 9273's -201 MiB was 0.190.0; per-texture residency (the monitor gives a total);
what deduplication saves in the engine; the 8 MiB in play; any GPU but the RTX 2060; bandwidth or frame cost of
compression; the shading cost of triplanar.

## 3. The guide against the factory

| Guide technique | Factory today | Verdict | Memory | GL Compatibility draws / shader |
|---|---|---|---|---|
| Better source tile | Crack nets refuted: "A sparse feature in a TILING texture advertises the tile", so concrete carries no cracks (V) | DONE | 0 | 0 |
| Consistent tile scale | 128 px/m power-of-two packs (V: `pixelcoat/pixelcoat/core/material_grammar.py:905-924`); Zoo texel 1.0, "walked and approved" (V: `zoo/CHANGELOG.md:10796-10842`); world projection keeps each pack's size (V: `zoo_worldskin.gd:1544-1555`; `lot/lot.py:1133-1137`). Residue: asphalt at 512 px over 3 m is 171 px/m beside sidewalk at 102 px/m at every kerb | DONE, with residue | 0 | 0 |
| Per-piece UV offset or rotation | Road paint: a SHA-1 offset per marking, baked into merged UVs (V: lot.py:1090-1110, 2318-2347). Kit modules are instanced and share UVs; world projection made walls continuous on purpose | PARTLY; on walls CONFLICTS | 0 | 0 if baked into UVs; as a material per piece once 227 submissions |
| Tile variants A/B | Pixelcoat output is fixed by its seed, but a theme builds one pack per kind; the generation-7 `variations` maps are unreachable from a theme (V) | NEW | +0.17 MiB per 512^2 BC1 map | +1 fetch if blended in the material; as extra materials, 13.16x the materials cost 4.65x the ms (V: `tint_merge_ab.gd:16`) |
| Broad mask over metres | Nothing above the tile: asphalt's macro band is 3 cells on a 3 m tile; wall tiles equal the 2 m module (V) | NEW | ~0.04 MiB (256^2) | +1 fetch planar, +3 triplanar; 0 draws |
| Vertex paint | Zoo bakes wear into vertex colour (V: `materials.py:700-720`); Godot draws it on objects but not on tiles, because per-module wear tripled the 2 m pattern (V: `zoo_worldskin.gd:1080-1087`); merged Empties own their vertex arrays; Patina's height bands reach only the greybox path | PARTLY | 0 | 0 |
| Decals / overlay meshes | No Decal node on GL Compatibility (V: accents guide :1151). Overlay quads ship: road paint, alpha-tested, merged per 32 m cell (V) | Meshes DONE; Decal CONFLICTS | Atlas-sized | +1 draw per cell in view |
| Triplanar | On kit walls, slabs, stairs and the ground (V) | DONE, never priced | 0 | 3 fetches per map |
| Godot Detail + mask | Unused; with UV1 triplanar the mask follows UV1's tile scale (I), so it cannot be broad | NEW, weak | Small | +6-9 fetches (I) |
| Near/far blend | Only forced mip chains (V) | NEW, do last | 0 | A branch plus fetches |
| Stable per-piece seed | SHA-1 keys; a node-position hash in shaders (V) | DONE | 0 | 0 |

## 4. Plan, ranked

1. **Find what the walker's 238 verdict is actually seeing, before building anything** (root `look_shots`,
   `tools/texel_density.gd`). World triplanar already ships on every kit wall, and the guide itself says triplanar
   "solves projection, not repetition", so more triplanar is not the answer to "needs 3d UV Tri stuff?". Suspects (I):
   the 2.0 m wall tile equal to the module pitch; BC1 over per-texel grain (drywall's fine layer is about 1.6 texels per
   feature); lightmap chart edges; relief steps at module seams. Arms at the two review cameras: as shipped; an
   unchanged copy (the null control); `--inspect studio` (takes the bake out); wall packs lossless (the positive
   control, which must move pixels); wall skins' `uv1_scale` x 0.8 (a 2.5 m period). No memory, no look risk.
2. **Ship one texture per content per package** (Level Factory export). On a copy of 9335's package, point every GLB at
   one shared `_tex/<hash>`; read `texture_split_probe.gd`'s mission arm against the unchanged copy read twice; frames
   must differ only at the null control's level. Expected -10 to -12 MiB on multi-building lots, ~0 on the hospital.
   Each file's import settings must move with it (normal maps name their own path in `roughness/src_normal`). The
   prerequisite for denser or lossless skins.
3. **Give the ground one broad layer, one shader per family** (Lot writes the material; Pixelcoat supplies a second-seed
   B pack and a mask). Lot's 57 ground material sub-resources (12 distinct) become one shader material per family:
   planar from above, pack A, pack B and the mask, roughness in alpha -- 3 fetches against today's 6 (I). The mask
   follows causes Lot knows (lane centres, kerbs, parking bays), sampled at texel centres. In the same patch asphalt
   `meters_per_tile` 3 -> 4, exactly 128 px/m and a 4 m repeat. About +0.5 MiB; 0 draws. Priced as the CRT pass was.
4. **Give walls a world-derived broad tint in vertex colour, on merged sides** (Level Factory `merge_empties`): a low-
   frequency world value (8-15 m) plus causes (height above grade, sills, corners), on the merged duplicate material
   only. Control: the 2 m spectral power on an elevation (Zoo 0.54.0's measure). 0 memory, one multiply. Posterize to
   the theme palette -- the Quake II "constraint" behind Patina's families. Mission buildings stay instanced and need a
   shader converted from Godot's own generated material code; never a `next_pass` (a draw per surface, 2.27-4.29 us
   each, V).
5. **Place inserts where a cause puts them** (Pixelcoat makes the atlas; Lot and Deli Counter place it): cracks,
   patches and stains as one shared alpha-tested atlas on merged quads, the road-paint pattern -- the Quake II note's
   "composition over fields" (V: `pixelcoat/docs/CONTRAST_DIRECTION.md:324-348`). 0.33 MiB; +1 draw per cell in view.
6. **The skins' sampling and density -- the walker's call, after 1-2.** 9335's 77 distinct nearest-sampled textures
   cost 5.1 MiB as BC1, 8.9 as BC7, 35.5 lossless; the 23 realism atlases already hold more texels than all of them;
   the accents guide's 512 px/m would be 16x today's texels, about 74 MiB as BC1 even deduplicated (I). BPTC is
   already a dependency (the lightmap is BC6H).

**Where the realism trial supersedes the Quake II note:** realism replaced it for hero props (filtered atlases at three
times the density) and reversed its lossless pins; tiled skins still follow its 128 px/m, nearest-sampled (70 against
23 filtered in 9335's GLBs); its panel composer and bevel bands are unbuilt (I).

## 5. Questions only the walker can answer

1. Should tiled skins stay pixel (nearest, 128 px/m, approved in Zoo 0.55.0), or follow the realism trial -- and at
   what density?
2. If pixel: BC1 up close, or BC7 (+3.8 MiB deduplicated), or lossless (+30 MiB)?
3. May wall tiles stop repeating once per 2 m module? It reverses an approved look.
4. How much broad variation, and must every patch have a cause?
5. Which hardware sets the texture budget? Item 238 closes under 100 MiB, measured on an RTX 2060.
