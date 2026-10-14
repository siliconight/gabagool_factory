## [0.200.0] - An urban street: the brief asks, and the far side stands a continuous mid-rise wall

**Factory roadmap 241, steps 2 and 3: the first cut.** The walker, 2026-10-11, chose a new urban level type:
mid-rise blocks of five to twelve storeys at the sidewalk line, touching block after block, where a gap is an
event and not the default (the factory root's `docs/reference/URBAN_MIDRISE_COMPS.md`). Deli Counter 0.213.0
built the family, `gs_midrise_a` to `_f`, named out of the prefix this repo hands every terrace. This release
is the brief that asks for them, and the far side of the street.

- **`MissionBrief.streetscape`.** `"urban"` asks for the urban street, and absent or any other word keeps
  today's strip. `models.streetscape_effective` is the one rule for what a brief GETS: urban only where a
  terrace stands (`empties_effective`, which needs a lot library and two or more buildings). The
  functional signature carries `streetscape` only then, so no existing brief's lock moves.
- **`building_library.empties_for_brief`** draws an urban brief's Empties from the mid-rise family
  (`MIDRISE_PREFIX`, `gs_midrise_`) and every other brief's from the rowhomes, as before.
  `empty_rows(build_dir, prefix)` reads either. The planner's art jobs and the compose rows both ask
  this one function, so the themed and the placed Empties cannot differ.
- **`empties.terrace(..., continuous=True)`** stands the row without the alley every five to eight houses:
  one wall, broken only where a road crosses the far side. Off (the default), the terrace draws exactly as
  before. Every front stands on the line the rowhomes' did, `FRONTAGE` (2.0 m) behind the far sidewalk:
  the strip the near side keeps too.
- **An urban brief over an older library says so.** If the lot library holds no `gs_midrise_*` Empty, the
  compose stage prints `URBAN_WITHOUT_MIDRISES`, and no wall stands. It does not quietly stand the rowhomes.
- **The adapter knows `empty_midrise`.** `_VALID_PRESETS` is a copy of Deli Counter's registry, and
  `test_dc_preset_registry` compares the two. It has failed since Deli Counter 0.213.0 added the preset,
  unseen, because nothing ran this suite after that release. No archetype names it, so no brief resolves
  differently.
- **What this cut does not do.**
  - The near side, the mission's own buildings among mid-rise Empties with no plate between them, is the
    next cut. It meets what Lot lays after the roads (parking, pads, dumpsters).
  - Heights drawn by cause (taller away from the action) are not drawn yet; the deal draws for variety.
  - The 2.0 m frontage stays.
  - Tree pits, the corner shop and the dusk haze are their owners' (241's list).
- **`tests/unit/test_streetscape_urban.py`** checks the field's default and signature, what a brief gets,
  the mid-rise draw, the continuous wall on the line, and the strip terrace unchanged.

**Suite:** `python -m pytest -q`: exit 0, 2,365 passed, 14 skipped (the real-tool smoke, needing `LF_TOOLS_DIR`), 1 xfail, counted off the progress marks. `test_streetscape_urban.py` fails to import on 0.199.0. `test_dc_preset_registry`, which failed on 0.199.0 beside Deli Counter 0.213.0 and later, passes
