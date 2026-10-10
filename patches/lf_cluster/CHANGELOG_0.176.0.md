## [0.176.0] - The buildings beside the objective are drawn by a cluster template, when the brief asks

**Roadmap 230.** The walker's adjacency and layout guide
(`docs/reference/PA_1990S_ADJACENCY_AND_LAYOUT_GUIDE.md`) names eighteen
neighbourhood recipes, each an anchor with the uses that support it and the
ordinary fabric around it. `building_library.pick_lot` drew the buildings
beside the archetype from the whole library by seed alone, with no reason
for any two to be neighbours, which is why a new building family changed
every seed's level.

- **`MissionBrief.cluster`** (recorded; in the functional signature when
  set, since it changes which buildings stand): a template's id
  (`C03_station_neighborhood`, `C11_hospital_edge`...) or `auto`, the
  archetype's words deciding (`cluster.TEMPLATE_BY_WORD`: a hospital is the
  hospital edge, a gas station the roadside lodging, a station or a deli the
  station neighbourhood, a warehouse the industrial edge, a strip club the
  evening main street). Empty, the default, keeps the draw 0.175.1 made,
  byte for byte.
- **`cluster.CATALOG_FAMILIES`** maps the guide's building ids onto the
  library's families that are that use (a corner store is `stop_n_go`,
  `convenience_store` or `gs_corner_station`; a fuel station `gas_station`,
  `cr_gas`, `gas_street` or `fuel_stop_heist`; a pizzeria stands in for the
  guide's restaurant). A use the library has no family for (a tavern, a
  diner, a hardware store) is skipped, not invented: the slot falls to the
  ordinary draw.
- **`pick_lot(..., preferred=)`** draws the template's families first, in
  the guide's order, after the anchor and before the library's remainder;
  `lot_for` and `lot_for_brief` thread it; the site spec records
  `cluster_resolved` (`asked`, `got`, `known`, `preferred`) beside
  `surroundings_resolved`, so an unknown spelling is said on disk.

**Tests:** 9 in `tests/unit/test_cluster.py`: the eighteen templates, the
catalog's shape, the unchanged draw for a brief that names nothing, the
archetype's words under `auto`, an unknown spelling said not guessed, the
guide's order, the template's families drawn first, a missing family
skipped with the lot still full, the anchor still first. **Suite:** RESULT_SUITE.
