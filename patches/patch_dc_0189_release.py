"""Deli Counter 0.189.0: VERSION and CHANGELOG for `patch_dc_grid_sweep.py`,
`patch_dc_grid_baseline_tests.py`, `patch_dc_grid_baseline.py`,
`patch_dc_deli_a03_stair_door.py` and `patch_dc_0189_fixed_points.py`.

    python patch_dc_0189_release.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

ENTRY = '''## [0.189.0] - the nav gate bakes at eight grid origins, and deli_a03's stair door no longer tears on half of them

**Found 2026-10-06, closing cold run 9185** (roadmap 189 at the factory
root, `docs/findings/stairwell_on_one_grid_in_four/`).
- 9185 lost two candidates of three to deli_a03.
- Its objective upstairs joins the ground floor at 4 of 8 voxel-grid origins.
- A navmesh's grid starts at the corner of whatever is baked, so the
  building alone and the building in a site sit on different grids.
- This gate baked one origin, the building's own bounds, and passed it.

### The gate sweeps

**`nav_gate.gd` `_grid_sweep`** bakes the same parsed geometry again at eight
origins inside one cell:
- `GRID_FRACTIONS`: eight X phases, eight Z phases and four Y phases;
- fractions of the contract's cell, so they follow `agent_contract.json`.

Beside each traversable stair and each checked marker it writes `grid`, the
origins where that stair or marker connected. It decides nothing.

**`nav_gate.py` scopes it:**
- An interior marker the base bake reached, but not at every origin, is
  listed in `interior_grid_fragile` and makes the shell not `navigable`.
- A stair that traverses at only some origins does the same.
- `interior_unreachable` keeps its string format, which other tools parse.
- **The exit code is unchanged.** It is still the base bake's stairs.

**Level Factory reads `navigable` to choose themed-lot shells**, so a
grid-fragile shell leaves themed lots with no Level Factory change.
- Measured with Level Factory's own `themed_fitness` on this library: 102
  shells fit before, 101 after.
- twin_a01 leaves. It is the twin family's only shell, and no brief names
  that family.

### The library run

`nav_gate.py --all`: 144 shells, every exit passing. Eight flagged:

| shell | what connects at only some origins |
|---|---|
| deli_a03 | objective_A (4/8) -- fixed below |
| foundry_heist_vertical | stair_0, stair_1 |
| primos_pizza | stair_0; objective_COUNT_SAFE, loot_STASH (6/8) |
| twin_a01 | stair_1; objective_UPSTAIRS (7/8) |
| cr_deli, night_deli, corner_deli_heist_01 | objective_REGISTER (2/8) |
| fuel_stop_heist | objective_REGISTER (4/8) |

**`navgate_baseline.json` freezes the seven still fragile** (`grid_fragile`),
each with a reason that says what was measured and names no unlocated neck.
- Six were unfit for a themed lot before the sweep too. Five had markers
  unreachable at the base bake; foundry_heist_vertical had empty slot
  coverage.
- The register markers stand inside their counters, and which side of the
  counter they snap to is not yet located.

**`test_navgate_population.py`, three new tests:**
- a newly fragile shell fails;
- a fixed shell still listed fails;
- every result must carry the sweep, or a gate run from before it would
  read as "nothing fragile".

### deli_a03's `office_stair_door`: 1.25 m to 2.4 m

- **The stairwell's only walkable way in is this door.** At 1.25 m on x
  -15.0, all but its east 0.2 m opened over `deli_stair_down`'s slab hole
  (x -17.0 to -14.6, from y 6.2). That is by design: it is the basement
  flight's own door.
- **The way up turned inside the reveal**, onto the 1.6 m strip beside
  `deli_stair_up`, and that turn baked at 4 of 8 origins.
- **At 2.4 m on x -14.5** (pos -0.38; openings snap to the spec's 0.5 m
  grid), the west part still meets the basement flight's top. The east part
  opens about 0.5 m, five cells after erosion, straight onto the strip.
- **Gated:** objective_A at 8 of 8 origins, navigable.
- **The census at the factory root,** baking as the site does (imported
  colliders): 0 split pairs. Both instruments agree.
- The reason travels on `deli_stair_up`'s `meta` as `door_why`, beside
  `open_under_why`. An opening has no `meta` in the schema.
- **Re-furnished** (`migrate_furnish_recipes`), because the library must stay
  a fixed point of furnish. Exactly one piece moved: the work table
  `table_work_r9a51d20f_5`, y 2.91 to 3.91. Re-built and re-gated after it
  moved: 8 of 8.

### `material_kind.SKIN_KINDS` carries `chain_link`

It is a literal copy of Zoo's `KNOWN_KINDS`, and Zoo 1.77.0 added the
chain-link fence's fabric. `test_material_kind.py` had failed on every
checkout since, which would have refused this commit at the hook. No spec
here writes the material, so it needs no `KIND_BY_MATERIAL` row.

### Tests

- **`test_navgate_grid.py`, 8.** Five fail on 0.188.0:
  - a reached-but-fragile marker is not navigable, and says why;
  - a fragile stair is not navigable;
  - a result from before the sweep reads as it did;
  - the verdict prints both;
  - the gate sweeps fractions of a cell through `filter_baking_aabb` (read
    as source).
  - The three that pass on 0.188.0 are invariants: what every origin
    reaches stays navigable, the unreachable format is unchanged, and the
    street stays deferred.
- **`test_navgate_population.py`, 3 new and 1 extended.** Proven in order:
  - with no baseline, they fail on all eight shells;
  - with seven frozen, they fail on deli_a03 alone;
  - after the door, they pass.

**Suite** (`python -m pytest -q`): 1,240 passed, 2 skipped.

'''


def main():
    v = DC / "VERSION"
    assert v.read_bytes() == b"Deli Counter 0.188.0", v.read_bytes()
    cl = DC / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## [0.188.0] - the Flappahs store"), text[:60]
    cl.write_bytes((ENTRY + text).encode("utf-8"))
    v.write_bytes(b"Deli Counter 0.189.0")
    print("Deli Counter 0.189.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
