# Cold run 9213 -- 0 interventions; the payphone lit, and indoors a wall unit

club_block_014, seed auto, staged from cold run 9212. It tests three releases
for roadmap 210, which the walker called on 2026-10-09: "yes light it, and do
the indoor wall form".
- **Zoo 1.89.0:** the header's face and a hood lamp's diffuser on a second,
  backlit atlas, and `LuxEmit_payphone_hood` under the diffuser carrying its
  height above the ground.
- **Lux 0.70.0:** the `payphone_hood` row that marker spawns.
- **Deli Counter 0.204.0:** a payphone against a wall asks for the `wall`
  form. 39 payphones in 38 specs were refurnished and rebuilt.

The finding is `docs/findings/payphone_light/`.

Tool versions hashed at `--begin`: Zoo 1.89.0, Lot 0.102.0, Level Factory
0.163.0, Laser Tag 0.25.0, Deli Counter 0.204.0, Lux 0.70.0, Dispatch 0.5.2,
Patina 0.29.1, Pixelcoat 0.61.0, Pipeline 0.6.0. Zoo, Lux and Deli Counter
moved since 9212.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0). Every leg ran.

**Picked: seed_9181**, on the same figures as 9206 to 9212.

**What held:**
- **Findings: 72 to 72.**
- **The art leg:** 0 blockers. It exits 1 at the approval gate, as 9211's
  and 9212's did.
- **The light bake:** 432 models lightmapped and 7 kept dynamic, as before.
  - **Steady rigs baked: 76 to 79,** the three payphone lamps. 13 failing
    and 2 cycling are left live, as before.
  - **Lightmap users: 3,892 to 3,895,** the three payphones' lit meshes.
  - 88.5 s in the editor, against 92.8.

## The payphones in the level

Three, each with its lamp spawned, `Spawned_payphone_hood` under
`LuxFixtureLights` (read by `docs/findings/payphone_light/stations.py`):

| where | built as | lamp, Godot | caller side |
|---|---|---|---|
| Lot's bus stop, `cover_101` | the booth, `auto` | (34.273, 2.308, -2.075) | -X |
| the airport terminal, `airport_terminal_a02` | `..._fwall_mmetal` | (-23.413, 2.211, 3.480) | +X |
| the funeral home, `funeral_home_a03` | `..._fwall_mmetal` | (79.270, 2.211, 13.413) | -Z |

- **The street lamp stands exactly where the probe stood** before the
  release.
- **The airport terminal's checks against its spec.** The volume is at x
  -26.59, y -5.48, turned 180 degrees, and the building at (3, 0, -2):
  Godot (-23.59, 1.15, 3.48). The lamp is 0.177 m from there toward the
  caller.

## At midnight

`tools/look_shots.py` on the walk copy. Manifest:
`payphone_shots_manifest.json`.

| station | 9212 (no lamp) | the probe, live, 0.75 | 9213, baked |
|---|---|---|---|
| `payphone_caller`, centre mean | 20.5 | 94.8 | 81.8 |
| `payphone_walk`, centre mean | 14.9 | 34.3 | 29.1 |

Nothing clipped. The 9212 column is 9212's own manifest. The "before"
frames in the image are the probe's energy-0 control, because 9212's own
shots were not kept, and that control reproduced 9212's figures to 0.1.

**`payphone_street_before_after.png`**, the bus-stop booth:
- **9212** is the silhouette.
- **In 9213** the inside of the booth is lit. Every line on the instrument
  reads, and the shelf and the cord show. There is a pool on the pavement
  in front of the booth, and the PHONE header glows over the booth's top.
- **The baked lamp reads 14% under the live probe** at the caller's view
  (81.8 against 94.8). Neither cause below was isolated.
  - **Two differences the probe could not carry are the candidates:** the
    header's shadow, which the geometry puts on the pavement past about
    0.9 m out, and the payphone's lightmap at 0.2 m a texel.
  - **The bake's bounce** works the other way.

**`payphone_indoor_wall_units.png`:** the airport terminal's and the funeral
home's payphones, 1.4 m and 3 m out.
- **They stand as wall units:** no post, the conduit down to the floor, the
  phone book under the shelf, the PHONE header lit.
- **Both rooms read dark at midnight,** and the payphone is the brightest
  thing in each frame. The rooms' own light is not this change's. It is
  noted here because it is what the frames show.

**One station missed.** `booth_far`, 7 m down the sidewalk, looks at a dark
box in the foreground, and the booth is behind it. It is in the manifest and
not in the frames.

## The package against 9212's

`docs/findings/weighted_normals/pkg_diff.py`, output `pkg_diff.txt`.

**What the releases moved:**
- **The street booth's GLB:** its JSON chunk differs. It has the lit mesh,
  the second material and the marker.
- **The indoor payphones:** each building's
  `prop_payphone_..._h230_mmetal.glb`, a booth, is gone, and
  `..._h230_fwall_mmetal.glb` stands in its place.
- **The atlases:** 1.88.0's `Payphone_256x1243` has gone from all three.
  - The booth carries `Payphone_256x1182`, the wall units
    `Payphone_256x1326`.
  - Each has `PayphoneGlow_289x121`.
- **The bake.**

**What the pipeline moved on its own:** four fixture and dressing GLBs,
re-ordered, with the same triangles as multisets, and the import sidecars,
`.tscn` ordering and manifests. These are the same kinds of change 9212's
notes record, which the 9209-9210 control showed the pipeline makes with
Zoo unchanged.

## The price

The weighted-normals method (`docs/findings/weighted_normals/README.md`):
- **The four runs:** `_runs/perf_inner/run.py` on 9212's package
  (`pl_off`), 9213's (`pl_on`), 9212's again (`pl_off2`, the control) and
  9213's again (`pl_on2`). Each package copy was deleted once its report was
  written.
- **The harness:** Level Factory's fixed stations, 53 headings, GL
  Compatibility.
- **The reading:** `patches/zoo_cover_merge/price_robust.py`, against the
  mean of the two controls. Output `price_robust.txt`; reports `pl_*.json`
  and `.log`.

| | median frame moved | mean | range |
|---|---|---|---|
| the controls, one against the other (52 stable headings) | +0.039 ms | +0.049 | -0.578 to +0.855 |
| `pl_on` | -0.021 ms | +0.039 | -0.672 to +0.989 |
| `pl_on2` | +0.000 ms | +0.003 | -0.593 to +0.692 |

- **The frame: nothing measurable.** Both runs sit inside the controls'
  own spread.
- **The draws:** 23 of 53 headings gain 1 to 4, identically in both runs.
  The two controls agree with each other at all 23.
  - 1 is one payphone in view: its lit mesh, the one more draw the walker
    was quoted.
  - The larger gains are more than one payphone in view, or one in a
    shadow pass too.
- **One heading was unstable between the controls:** `attacker_spawn_8` at
  270, 11.76 against 12.80 ms. It is left out of the stable rows.
- **The 8-light cap, paired** (the census that knows the bake, Level
  Factory 0.159.0):

  | | lights | static | pairs | over the cap | worst mesh |
  |---|---|---|---|---|---|
  | 9212 | 95 | 78 | 1,576 | 0 | 6 |
  | 9213 | 98 | 81 | 1,579 | 0 | 6 |

  - The three lamps baked static, and none crosses the cap.
  - **The reach census,** kept one release for comparison, reads 33 over
    in both. Its worst mesh goes from 31 to 32, and the 32 is a mesh that
    read 30 in 9212: `b1/Dressing/CoverW_concrete_delco_1997`, the airport
    terminal's west cover (`b1` stands at (3, 0, -2)).
    - The only new lights are the three lamps, so two of them reach its
      bounds.
    - The paired census, which knows the bake, keeps every mesh at 6 or
      under.
    - Its pairs rose by 3, 1,576 to 1,579. Which meshes took them was not
      read.
- **The scene:** 3,951 meshes against 3,948, the three lit meshes.
