# Cold run 9208 -- 0 interventions; the responders' cruiser is in the package

club_block_014, seed auto, staged from cold run 9207. Tests roadmap 212's
last step:
- **Lot 0.101.0.** Zoo's site kit builds each arrival's car, and the themed
  assembly copies it beside its scene, names it in `responders.json`, and
  stands it nowhere.
- **Level Factory 0.162.0.** `responder_arrivals.json` (schema v3) names
  each arrival's car.

Tool versions hashed at `--begin`: Lot 0.101.0, Level Factory 0.162.0, Laser
Tag 0.25.0, Zoo 1.86.0, Deli Counter 0.203.0, Lux 0.69.0, Dispatch 0.5.2,
Patina 0.29.1, Pixelcoat 0.61.0, Pipeline 0.6.0.

**`INTERVENTIONS: 0`.** The journal holds no entries, and the run's diff is
empty. Every leg ran.

**Picked: seed_9181**, as in 9206 and 9207, on the same figures:
- 9080: 1 major, route completion 0.92;
- 9181: 0 majors, 0.96;
- 9282: 1 major, 0.96.

**Findings:** 58 to 58, no code moved.

## The car, from the kit to the package

`check_vehicle.py` (output `check_vehicle.txt`) reads it in pipeline order.
It was written before the run, and corrected against 9207's real files
first: the GLB scan's fields had been guessed wrong. On 9207 it reads no car
anywhere, as a control should.

| stage | what it shows |
|---|---|
| the site kit | `site_kit.built.json` built `prop_cruiser_delco_1997_01_w220_d554_h158`, status `pass` |
| the themed site | `responders.json` names that file for all three arrivals, at their stops, `missing` empty; the file is in `cover/`; `site.tscn` does not name it |
| the package | `responder_arrivals.json` v3: all three arrivals' `vehicle_scene` is `res://cover/prop_cruiser_delco_1997_01_w220_d554_h158.glb`, the file present (237,892 bytes, with the nine textures it names), `vehicle_findings` empty |
| the gates | closure scan ok, 0 issues; GLB reference scan ok: 440 GLBs and 1,862 references, all resolved (9207: 439 and 1,853) |

**The car stands nowhere.** The bake's lightmap users held at 3,898, the
same as 9207.

## Found: the bake marks the car static

**What moved.** The bake's "models lightmapped" went from 432 to 433. The
extra one is the car's import: the bake sets every GLB sidecar in the
package to `meshes/light_baking=2`, Static Lightmaps, unless the GLB
carries its own second UV set (`light_bake.mark_imports`). The car's
sidecar reads `2`, and an unwrap cache sits beside it.

**Why it matters.** The gameplay layer spawns the car, so it is never in
the bake. Measured in a throwaway Godot 4.7 project holding only the car:

| `light_baking` | the car's five meshes' `gi_mode` |
|---|---|
| `2` | STATIC, on all five |
| `3` | DYNAMIC, on all five |

A static mesh with no lightmap gets neither the baked light nor the
`LightmapGI`'s probes, so a spawned cruiser would read darker than the
level round it. The fix is the bake's: a spawned car's import is set to
`3`, Dynamic, so it samples the probes. That is Level Factory 0.162.1.

## Other figures

- **Shell:** 3 candidates, all distinct; 0 blockers of 42 findings, where
  9207 had 43. The driver's findings diff counts the validation report,
  which held at 58, so the structural count's one is not attributed here.
- **Art:** 0 blockers of 58.
- **The bake:** 433 models and 1,528 primitive meshes lightmapped, 7 kept
  dynamic; 76 steady rigs baked, 13 failing and 2 cycling left live; 172
  room fills; 3,898 users; 82.4 s in the editor.
