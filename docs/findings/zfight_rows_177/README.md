# The z-fight gate read Godot's transforms transposed (roadmap 177's last two pairs)

Found 2026-10-19 working roadmap 177's last block. Its decision was "warn now, block once the library counts
zero", and the two pairs left were deli_a01's `ext_0_E_seg10 / int_0_1_seg18`, reported in cold runs 9322 to
9324 and filed as "partition 1 running the building's full 38 m into the east wall, whose segment ends land on
its faces". They were not geometry. Deli Counter's z-fight gate read each composed module's `Transform3D` with
its basis transposed, and so did six other readers in three repos.

## What the gate reported, and the arithmetic that did not fit it

`compose.summary.json` for deli_a01 (cold run 9324): two pairs, `ext_0_E_seg10` against `int_0_1_seg18`, 0.9 m2
each, on Godot-z planes -5.825 and -6.175 -- the two side faces of partition 1, which runs along x at y 6.0 and
is 0.35 m thick. From the slots (`deli_counter/build/deli_a01.slots.json`): the east wall's end piece is 0.6 m
along the wall and 0.35 m through it, centred on the junction, so its faces lie at z -6.3 and -5.7, not on the
partition's planes. A 0.9 m2 overlap is 0.3 m x 3.0 m -- exactly what the end piece would share with the
partition if its length and thickness were swapped.

## What the engine says

`tools/module_pose_census.py` on cold run 9324's package (`pose_9324_junction.json`; Godot's own world AABBs, on a
mirror of the package, headless):

    ext_0_E_seg10  WallEnd_Panel  x 18.825..19.175  y -0.004..2.996  z -6.300..-5.700
    int_0_1_seg18  WallEnd_Panel  x 18.625..19.000  y -0.004..2.996  z -6.175..-5.825

No face of one lies on a plane of the other. The engine stands the end piece 0.35 m through its wall and 0.6 m
along it, as written: `Transform3D(0, 0, -0.35, 0, 3, 0, 0.6, 0, 0, 19, 1.496, -6)`, read as Godot reads it, is
three ROWS and an origin. The gate (`zfight_gate._scene_module_boxes`) read the nine numbers as COLUMNS. A pure
turn reads the same either way for a box about its own centre, so nothing else had shown it; a turned AND
non-uniformly scaled module -- a wall remainder on a wall running along Godot z -- comes out with two extents
swapped.

Rows is not a new reading. It was measured twice before this, and written down both times:
- Deli Counter 0.120.1 (`tscn_export.godot_basis`): 0.120.0 had believed the columns story and shipped wall
  remainders across their walls on cold run 9013; the placement gate was moved to rows then. The z-fight gate,
  its sibling, was not.
- Lot 0.72.1 (`lot/site_collision.py`) and `lot/site_furniture.plate_facing`: `str_to_var` on
  `Transform3D(c, 0, s, 0, 1, 0, -s, 0, c, ...)` at 30 degrees sends local +X to (0.866, 0, -0.5).

## The class: who read columns, and what each fix measured

| reader | fixed in | measured with the fix |
|---|---|---|
| Deli Counter `zfight_gate._scene_module_boxes` | Deli Counter 0.230.0 | 9324's 16 composed buildings: visible pairs 2 -> 0, none unmasked; buried (intel only) deli_a01 213 -> 220, pharmacy_a01 29 -> 27 (`rows_vs_columns.out.txt`) |
| Level Factory `ground_contact._transform` (and `spawn_placement`, `tactical`, which read through it) | Level Factory 0.218.2 | 9324's three candidates, about 6,000 boxes each: 0 problems and 0 box centres moved either way, every building unturned (`ground_contact_rows.out.txt`) |
| `tools/repetition_census.py` (scale from the triplets' lengths) | the factory root, `tools/godot_transform.py` | 9324's mission buildings: forms 64 -> 59 (deli_a01), 25 -> 24 (office), 24 -> 24 (pharmacy_a01); wall instances and worst runs (18, 11, 7) unchanged; reuse 5.42 -> 5.88 and 7.84 -> 8.17 (`before/`, `after/`) |
| `tools/module_extents.py` (`_tscn_matrix`, `_scale_of`) | the factory root | not re-measured |
| `tools/site_fights.py` (`_m`) | the factory root | not re-measured: its input is a project whose modules resolve from the root, which a compose job's site is not |
| `tools/insert_overhang.py` (`godot_transform`) | the factory root | not re-measured |
| `tools/light_check.py` (`placements`) | the factory root | not re-measured; it moves a point only under a turned building, and no level on disk turns one |

`tools/godot_transform.py` is now the one reader for the factory's tools, and `tools/test_godot_transform.py`
holds it to the engine's numbers and every tool's reader to it: five of its nine tests fail with the tools as
they were (`tools_prove_before.out.txt`), all pass after (`tools_prove_after.out.txt`).

## What the corrected readings change in the record

- **Roadmap 177:** the last two pairs were the instrument's. With Deli Counter 0.230.0 the gate counts 0 visible
  pairs on every building cold run 9324 composed. Whether the LIBRARY counts zero -- the decision's condition for
  BLOCK -- is not measured: a library-wide count needs every building composed with its art, which no run has
  done.
- **Roadmap 74:** "deli_a01 347 wall instances, 64 forms" (cold run 9314) counted one wall-end size on an
  east-west wall and on a north-south one as two forms. Read as rows: 59, and office 24 where it read 25. The
  worst runs it cites stand -- every piece in one wall run shares a turn.

## Not established

- `tools/module_extents.py --selftest` stops on `ModuleNotFoundError: zoo_keeper` inside its kit check, with the
  tool as committed and as fixed alike: its import path, not this change, and not repaired here.
- No level on disk turns a building, so the Level Factory fix and the `light_check` fix changed nothing anyone
  can measure today; each is held by a test reproducing the turned case.
- Other readers may parse `Transform3D` text by another spelling than the patterns searched for (`f[3], f[6]`, the
  word "columns" near a parser); the root test holds the five found, not the ones not found.

## Files

- `rows_vs_columns.py` / `.out.txt` -- Deli Counter 0.229.0's gate both ways over 9324's composed buildings.
- `ground_contact_rows.py` / `.out.txt` -- Level Factory's ground-contact pre-flight both ways over 9324's
  candidates.
- `pose_9324_junction.json` -- the engine's world boxes for the junction's pieces.
- `before/`, `after/` -- `tools/repetition_census.py` on 9324's mission buildings, both readings.
- `tools_prove_before.out.txt`, `tools_prove_after.out.txt` -- `tools/test_godot_transform.py` before and after
  the five tools' fix.
