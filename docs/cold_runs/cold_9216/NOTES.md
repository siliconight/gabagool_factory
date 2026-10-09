# Cold run 9216 -- 0 interventions, 0 retries; the sky in the bake on a clear afternoon

card_block_001, seed auto, staged from cold run 9178 with its brief and
seeds: afternoon, clear, so Delco Summer Afternoon. It shows **Level Factory
0.164.0** (roadmap 217) where it was measured to matter: shade under a clear
sky. The walker's call, 2026-10-09: "yes bake the sky in".

Tool versions hashed at `--begin`: Level Factory 0.164.0, Zoo 1.89.0, Lot
0.102.0, Laser Tag 0.25.0, Deli Counter 0.204.0, Lux 0.71.0, Dispatch
0.5.2, Patina 0.29.1, Pixelcoat 0.61.0, Pipeline 0.6.0.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), **retries 0.**

**Picked: seed_9263.** It carries card_shop_a01, country_club_a01,
video_store_a01 and the 12 empty rowhomes. The candidates were all
distinct, and the shell leg had 0 blockers of 47 findings.

## The sky in the bake

**The control** is the walk copy re-baked with the sky off, the way every
level was baked from 0.131.0 to 0.163.1 (`tools/lux_rebake.py
--bake-environment none`, 78.2 s in the editor). Both were checked with
`tools/light_check.py` at the level's own slot (`light_check/`: the reports,
and the control's bake log). Luma after the grade:

| station | sky off | as shipped |
|---|---|---|
| extraction | 65.6 | 79.9 |
| spawn | 95.3 | 100.2 |
| elevations | 61.2 to 159.8 | +1.9 to +6.4 |
| overview | 136.3 | 136.8 |
| rooms | 19.0 to 66.5 | +0.0 to +1.2 |

- **What it looks like** (`sky_in_the_bake.png`, sent to the walker).
  Without the sky, the only light in shade is warm bounce off sunlit ground:
  - the extraction's wall reads rust-brown;
  - the spawn's sidewalk reads orange;
  - the east elevation's brick reads as mud.

  With the sky, shade is daylight, and the brick and paving read.
- **Both pass:** 19 PASS, 0 WARN. The street outshines the rooms either
  way, as a clear afternoon should.
- **The bake took 81.7 s,** and the scene carries no `environment_mode`
  line: 1 is Godot's default, which it does not write. 9215's notes say
  more.

## Roadmap 218: the import pass

`LF_card_block_001.portable-godot.import.log` sits beside the package with
both passes complete: `import pass 1: exit 0`, `import pass 2: exit 0`.

## What held

- **The export:**
  - 1,164 occluders from 1,169 solid modules;
  - the Empties merged, 12 into 236 meshes;
  - 429 models and 1,388 primitives lightmapped;
  - 70 steady rigs baked and 13 failing left live;
  - 116 room fills and 3,119 users.
- **Findings: 66 to 67 against 9178,** which is many releases back.
  - Lot's site audit is newly counted: `S_STREET_CROSS` 0 to 8,
    `S_GETAWAY_AT_SPAWN` 0 to 4, `S_RESPONDER_ARC` 0 to 4.
  - `LOT_PACING_OUTSIDE_TARGET` went 0 to 4. Pacing is not a hard rule.
  - Several Lot and Laser Tag codes fell: `LOT_CREW_SPAWN_PUSHED` 4 to 0,
    `LOT_COVER_PLACED` 3 to 0, `LT_MAP_PLAYER_STUCK` 2 to 1 and others.
  - None is attributed to this run's change. The bake moves no finding
    code.
