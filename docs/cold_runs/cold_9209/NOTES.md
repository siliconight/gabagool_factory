# Cold run 9209 -- 0 interventions; the responders' car ships set to sample the probes

club_block_014, seed auto, staged from cold run 9208. Tests **Level Factory
0.162.1** (roadmap 212): the light bake sets the responders' car to Dynamic
GI, so a spawned car samples the lightmap's probes.

Tool versions hashed at `--begin`: Lot 0.101.0, Level Factory 0.162.1, Laser
Tag 0.25.0, Zoo 1.86.0, Deli Counter 0.203.0, Lux 0.69.0, Dispatch 0.5.2,
Patina 0.29.1, Pixelcoat 0.61.0, Pipeline 0.6.0. Only Level Factory moved
since 9208.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), and the run's diff
is empty. Every leg ran.

**Picked: seed_9181**, on the same figures as 9206 to 9208: 9080 at 1 major
and route completion 0.92, 9181 at 0 majors and 0.96, 9282 at 1 major and
0.96. **Findings:** 58 to 58.

## The car's import

`check_vehicle.py` is 9208's instrument, plus the car's import line and the
bake report's `spawned`. Run on 9208 first as the control. Output:
`check_vehicle.txt`.

| | cold run 9208 | cold run 9209 |
|---|---|---|
| the bake's log | 433 models lightmapped, 7 kept dynamic | 432 lightmapped, 7 kept dynamic, **1 spawned set dynamic** |
| the car's sidecar | `meshes/light_baking=2` | `meshes/light_baking=3` |
| the car's unwrap cache | present | absent |
| `light_bake.json` `imports.spawned` | no such key | `["cover/prop_cruiser_delco_1997_01_w220_d554_h158.glb"]`, nothing unmatched |
| lightmap users | 3,898 | 3,898 |

Measured in 9208's notes: on Godot 4.7, `3` gives the car's five meshes
gi_mode DYNAMIC, which samples the `LightmapGI`'s probes. `2` gave STATIC,
which outside the bake meant no light from either.

**Everything else held:**
- the site kit built the car, `pass`;
- `responders.json` names it for all three arrivals and `site.tscn` stands
  nothing;
- `responder_arrivals.json` v3 names it for every arrival, present in the
  package;
- the closure and GLB-reference scans are clean: 440 GLBs, 1,862 references
  resolved.

## What the car costs

| | cost |
|---|---|
| the package | 259,531 bytes (9208's package): the 237,892-byte GLB and its own 21,639-byte livery image. Its other eight textures are shared with modules already there. |
| a frame, unspawned | nothing: it is in no scene |
| each car the gameplay layer spawns | five meshes (five draws) and 3,476 triangles, lit by the probes |

How many it spawns is the gameplay layer's to say.

## Other figures

- **Shell:** 3 candidates, all distinct. **Art:** 0 blockers of 58.
- **The bake:** 432 models and 1,528 primitive meshes lightmapped, 7 kept
  dynamic, 1 spawned set dynamic; 76 steady rigs baked, 13 failing and 2
  cycling left live; 172 room fills; 3,898 users; 86.7 s in the editor.
