# Cold run 9274 -- the reflection atlas, sized to the package

**What it tested:** Level Factory 0.198.0 in a real drive of restaurant_row_001. The package's
project.godot now writes the reflection atlas from the package's own probes:

- its slots are the probe count, rounded up to a power of two;
- its face size is 64.

Godot's default had been 64 slots of 256 (roadmap 238; `docs/findings/texture_memory/`). Measured by part
on cold run 9273's package, that default atlas was 257 of its 314.6 MiB of texture memory. Everything else
as in 9273.

**Result: 0 interventions, 0 tool files changed.**

- seed_9104 was picked as before, and the candidates graded as in 9273.
- **Findings 117 -> 117**, the same issue ids as 9273's.
- The merge and the bake are 9273's to the count: 172 merged meshes, 567 models and 3,392 users.

## What the package says (`atlas.log`)

    reflections/reflection_atlas/reflection_count=32
    reflections/reflection_atlas/reflection_size=64

There are 23 ReflectionProbe nodes in the package's scene text, and 23 in the running tree.

## What it holds (`memory.txt`)

`texture_split_probe.gd -- mission` on an imported copy, read after the warm-up:

    9273 (64 x 256, the default)    314.6 MiB
    9274 (32 x 64)                   65.6 MiB    -249.0 (-79 %)

The prediction was 73.5 MiB at 64 x 64 less 32 slots' 8 MiB, which is 65.5.

## The frames (`atlas.png`, `atlas.log`)

9273 left and 9274 right, at look_shots' derived stations and twelve interiors:

- **Brick rooms:** 0 % of pixels moved past 8 codes.
- **Concrete and drywall rooms:** 0.17 to 0.35 %, and one drywall room, `in_drywall_delco_1997_2`, 2.675 %.
- **Exterior stations:** at most 0.23 %.
- **Past 32 codes:** no frame moved more than 0.02 % (at spawn, where 2026-10-13's two-render control
  moved 0.015 %).

The sheet's two rooms and its overview read the same side by side. This is the pattern
`docs/findings/texture_memory/atlas_frames.sh` predicted at 64 on 9273's package. What 128 or 256 would
buy back is a sharper reflection on a glossy surface, and these interiors are rough.

## The price (`price/`)

9273's package is both controls, 9274's the subject:

    controls' spread, median over 53 headings: p95 0.07 ms, draws 0.0
    subject: draws +0.0 (mean, min and max), p95 -0.02 ms at the median, +0.90 at the worst heading
    (the controls' worst: +0.70 and +0.24)

The draws are identical, and the frame time sits inside the noise.

## The time

    run    shell   art     export   walk   retire   the drive
    9273   94 s    169 s   173 s    12 s    3 s     7.8 min (469 s)
    9274   94 s    161 s   172 s    12 s    3 s     7.7 min (459 s)

## What is evidence of what

- The package's settings: its `project.godot`.
- The memory: `memory.txt` here, and 9273's in `docs/findings/texture_memory/split_9273.txt`.
- The look: `atlas.png` and the diffs in `atlas.log`; the shots stay under `_scratch/frames_9274_atlas/`.
- The price: `price/`. The count: `cold_run.py --end`.
