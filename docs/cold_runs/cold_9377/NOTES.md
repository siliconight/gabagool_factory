# Cold run 9377 -- 0 interventions; restaurant_row_001, seed 9003: a level's package carries its buildings' drawings

**What it was for.** The factory's roadmap 296. The walker, of roadmap 293's exploded axonometric: seen in "both" a
review page and a level's export -- "It could even get into the game where the players can 'scope out' the level and
see the buildings the level assembles". Deli Counter 0.257.0 (9b1d5238) draws a building into its package's
`drawings/` when it is named the spec -- the axonometric and a plan a storey, each kept by Godot as the file it is --
and Level Factory 0.232.0 (6ce0e8e) names it and writes `buildings.json` at the package's root. Cold run 9376's level
again, staged from it.

**Tools** (`_runs/cold/cold_9377/before.json`, every repo clean at `--begin`): Deli Counter 0.257.0, Level Factory
0.232.0; the rest as 9376 -- Lot 0.126.1, Zoo 1.120.1, Lux 0.79.0, Dispatch 0.5.3, Patina 0.32.0, Laser Tag 0.32.0,
Pipeline 0.6.0, Pixelcoat 0.62.0.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0); 9.6 min (21:35:37 to 21:45:12). The
validation record 108 findings, none blocking. The `--end` line's FAILING is the factory root's hygiene counting this
block's own records before they are committed, not the run.

**What it shows** (`patches/lf_drawings/cold_compare.py` and `package_check.py`, each with its `.out.txt`; 9376's
staged scenarios and record read from copies taken before this run):

- **The level is 9376's.** The three Laser Tag candidates' staged scenarios byte for byte, the 108 findings by code,
  candidate and message, the bake's 153 models, 118 primitive meshes and 2,947 users: drawings are files a game reads,
  never scene content.
- **The package names its buildings and carries their drawings.** `buildings.json`: 29 instances -- deli_a03,
  pharmacy_a01 and office, each with its axonometric and its plans (three, one, three), and 26 Empties. Every one of
  the ten drawings it names is in the package, each beside the keep `.import`; 350 KB of drawings in all. No drawing
  became a texture: of the 2,875 entries in the import cache the walk copy took from the export
  (`_runs/walk_9377_restaurant_row_001/.godot/imported/`), the only textures made of an SVG are the package's two
  icons, `icon.svg` and `lux_root.svg`. The closure verdict is clean, and it resolves every `res://` the index names.
- **Two holes, both Level Factory's, read here and closed in 0.232.1:**
  - **The 26 Empties were composed with no spec.** An Empty's row comes from `building_library.empty_rows`, not
    `index`, and carried none -- so their packages held no record, and the index gave each "its package carries no
    drawings" where the reason is that it is a facade.
  - **The mission shell's drawings shipped at the package's root**, nine files, beside an index of three buildings:
    Deli Counter draws the composed root's building, the shell, and a varied lot does not stand it.
- **Refuted and kept, the instrument's first reading**: `package_check.py` looked for the import cache beside the
  package, found none -- the walk copy had taken it -- and printed "0 .ctex made of an .svg", a check with nothing to
  read reported as a pass. It now reads the walk copy's cache, says how many entries, and prints NOT CHECKED when it
  finds no cache.

**The walk copy** is `_runs/walk_9377_restaurant_row_001` (the drive wrote it to `_runs/walk_export_restaurant_row_001`
and it was renamed after the run).
