# Cold run 9215 -- 0 interventions, 0 retries; the import pass checks itself, and the sky is in the bake

bank_block_001, seed auto, staged from cold run 9214 with its brief and
seeds: afternoon with rain, so Heavy Rain. It tests two Level Factory
releases.
- **0.163.1:** the import pass checks its own work (roadmap 218). 9214's
  first pass imported 0 of 425 models and the export went on.
- **0.164.0:** the sky is in the bake (roadmap 217), the walker's call:
  "yes bake the sky in".

Tool versions hashed at `--begin`: Level Factory 0.164.0. The rest are as
9214: Zoo 1.89.0, Lot 0.102.0, Laser Tag 0.25.0, Deli Counter 0.204.0,
Lux 0.71.0, Dispatch 0.5.2, Patina 0.29.1, Pixelcoat 0.61.0, Pipeline
0.6.0.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), **retries 0.**
Every leg ran on the first try. Picked seed_9054, as in 9200 to 9214.

## Roadmap 218: the import pass

- **The log is beside the package:**
  `LF_bank_block_001.portable-godot.import.log` reads `import pass 1: exit
  0` and `import pass 2: exit 0`.
- **Both passes imported every model,** so nothing was repeated: the first
  pass, then the re-import after the sidecar rewrite.
- 0.163.1's retry was not needed here. The path that ran is the check, and
  it passed.

## Roadmap 217: the sky in the bake

**The bake scene carries no `environment_mode` line, and that is the
mode.** Godot writes a property only when it differs from its default:
- 9213's bake (0.163.0, mode 0) reads `environment_mode = 0`;
- this one omits it, because 1, the scene's environment, is LightmapGI's
  default;
- `directional = false` and `use_denoiser = true` are omitted the same way.

**What it changed, against 9214** (`tools/light_check.py` at the level's
own slot, luma after the grade; `_runs/sky_proof/check_9215`, not kept):

| | 9214, no sky | 9215, the sky | the re-bake trial |
|---|---|---|---|
| extraction | 41.5 | 43.6 | 43.6 |
| spawn | 53.4 | 54.8 | 54.7 |
| facades | 70.2 to 96.7 | +0.3 to +2.3 | +0.3 to +2.3 |
| rooms | 36.6 to 83.8 | -0.1 to +0.1 | -0.1 to +0.1 |

- **The pipeline does what the trial did,** within 0.1 everywhere
  (`docs/findings/lighting_spec_vs_lux/`).
- **Under rain the sky adds little,** as the trial said. Cold run 9216, on
  a clear afternoon, is where it shows.
- **The 12 WARNs stand:** Heavy Rain's shadowless sun lights the rooms
  through their roofs. That is roadmap 217's open call.

## What held

- **Findings: 74 to 74,** against 9214.
- **The export is 9214's retry, line for line:**
  - 1,481 occluders from 1,491 solid modules;
  - the Empties merged, 12 into 236 meshes;
  - 415 models and 1,366 primitives lightmapped;
  - 83 steady rigs baked and 21 failing left live;
  - 217 room fills and 3,639 users.
- **The bake took 124.8 s against 89.1 s.** The trial's paired re-bakes
  took 90.2 s with the sky and 91.2 s without it, so the sky is not the
  cause. Other work on the machine is the likely one; it was not measured.
