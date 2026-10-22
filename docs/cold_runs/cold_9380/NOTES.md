# Cold run 9380 -- STOPPED at the export; restaurant_row_001, seed 9003: the scout model refused as unimported

**What it was for.** The factory's roadmap 295: Deli Counter 0.259.0 (b97b1125) builds each building's scout model
into its package as `drawings/scout.glb`, kept (`importer="keep"`); Level Factory 0.234.0 (c458dc2) names it in
`buildings.json`. Staged from cold run 9379.

**The journal reads `INTERVENTIONS: 0`, and the level did not ship.** The export stopped at its import check:

    internal error: the import pass left 3 of 537 model(s) unimported after 3 attempt(s) and this build had a Godot
    to run it with; first: lot/deli_a03/drawings/scout.glb

The check counted every `.glb` as a model Godot must import, and waited for an import the keep sidecar exists to
prevent. A run that stops is not a level, whatever its intervention count: this is the pair of releases above
breaking every export that stands a building with an inside -- caught here, before anyone else's level.

**Fixed by Level Factory 0.234.1** (5c9d3d7, `patches/patch_lf_keep_model.py`): `occluders.kept`; `package_models`
and the export's import passes skip a model its sidecar keeps. Proven by cold run 9381.
