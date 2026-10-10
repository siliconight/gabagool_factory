## [0.175.0] - The brief names what stands beyond the edge, or the archetype decides

**Roadmap 228, step D's other half.** The walker asked for edges that differ
by level. Lot 0.108.0 lays the backdrop from the site spec's `surroundings`
recipe, `borough` when unnamed; until this, nothing wrote the field, so every
level backed onto rowhomes. Now:
- **`MissionBrief.surroundings`** (recorded, optional): `borough`, `none`,
  `yards`, `parkland` or `roadside`. Not in the functional signature: the
  backdrop has no collision and changes nothing a lock protects, like the
  weather.
- **Unnamed, the archetype and the site shape decide**
  (`site_variation.surroundings_of`, a table stated so it can be argued
  with): an `industrial_warehouse`, or a `yard` site, backs onto `yards`; a
  `county_hospital`, or a `campus`, onto `parkland`; a `gas_station` or a
  `convenience_store` on a `strip` onto `roadside`; everything else onto
  the `borough`.
- **The site spec carries what was asked, what it got and whether the word
  was known** (`surroundings`, `surroundings_resolved`), as `site_shape`
  does, so a spelling nobody knows falls back to the borough on disk rather
  than only in the geometry; the writer says so out loud.

Lot 0.108.0 lays `yards`, `parkland` and `roadside` as the borough with
`LOT_BACKDROP_RECIPE_PENDING`; Lot 0.109.0 lays them from Zoo 1.96.0's
tree and warehouse and the cargo container. For its stacked containers, a
backdrop piece may carry `z`, its foot's height above the plate, and the
composition (`backdrop_layer.manifest_from_drawn`) stands the module at
that foot plus half its height.

**Tests:** 5 tests (16 cases), every one failing on 0.174.0, which has no `surroundings_of` and no field, and passing on the draft. **Suite:** 2,190 passed, 14 skipped, 1 xfailed, exit 0 (2,173 as 0.174.0, the 16 new cases and the sibling guard's case for the new file).
