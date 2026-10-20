---
name: reflection-atlas-is-the-vram
description: "roadmap 238 NARROWED 2026-10-13: Godot's default reflection atlas was 82 % of texture memory; LF 0.198.0 sizes it per package (32 x 64), cold 9274 314.6 -> 65.6 MiB; sky NOT resident; measure by fresh-process arms"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-13T15:23:19.535Z
---

Cold run 9273's package read 314.6 MiB of texture memory after its warm-up. 257 MiB of that was the reflection atlas: Godot's default, 64 slots of 256² × 6 faces in half-float, holding the level's 23 Lux `room_ambient` probes. The findings are in `docs/findings/texture_memory/`.

**Shipped:** LF 0.198.0 (`godot_project.py`) writes the atlas from the package: the slots are the probe count rounded up to a power of two, and the face size is `REFLECTION_ATLAS_SIZE` = 64. Cold run 9274: 65.6 MiB (−79 %), frames unchanged to the eye, price flat. Root commit 758bae3; roadmap 238 is NARROWED.

- **What was retracted:** the 2026-10-11 census said the sky's 140 images were resident. None are, because SkyMint builds two skyboxes from their faces. The census also counted `bake.exr` as 0 (Pillow can't open EXR), so its total matched the engine's by coincidence.
- **Measuring texture memory:** never free parts of a loaded level and re-read the monitor; 266.9 of 314.7 MiB stayed after freeing the whole scene. Instead, rebuild the mission in a fresh process per arm with one part left out (`texture_split_probe.gd`), with `mission.tscn` as the control. Test project settings with an `override.cfg`.
- **The trap:** fewer slots than probes floods `rpi->atlas_index < 0` (113,494 times) and stalls the run.

**Left (roadmap 238):**
- the walker's eye on `cold_9274/atlas.png`; 128 or 256 is that one constant;
- the memory probe in every cold run's record;
- compression of the level's ~30 MiB.

**Why:** performance over look; VRAM on low-end GL Compat cards had never been priced correctly.

**How to apply:** a level with glossy surfaces may want 128. Price on interior frames (`atlas_frames.sh`) before raising it. Related: [[performance-beats-graphics]], [[sun-baked-by-default]].

**2026-10-13, LF 0.199.0 (e89c96d; root 81c10b5):** the perf harness reads texture/buffer/video memory after warming every station and prints it; price_glow.py prints each run's. Two instruments, two moments: harness 76.0 MiB textures on 9276 (in play) vs texture_split_probe mission 65.6 (after the package's warm-up, ~1 draw). perf_memprobe.py: 67.9 at load -> 76.0 after the station warm; not the shadow atlases; window ~1.3 MiB; ~8 MiB unattributed. Buffers unsteady run to run (48-56 MiB). Compare prices on the harness figure. Harness bug noted, not fixed: current_scene set before add_child (engine refuses).
