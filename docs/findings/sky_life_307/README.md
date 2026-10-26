# Life in the sky: a flock and an airliner, prototyped (roadmap 307)

The walker, 2026-10-25: "random birds and commercial airplanes in the sky to add some live to the sky". This is the
roadmap item's starting shape built on a scratch copy of cold run 9391's walk copy. No tool repo is touched. It is
not shipped.

## What was built

- **The flock** (`birds.gdshader`): one MultiMesh of 30 quads (1.0 x 0.28 m, folded at the body), one draw. Each
  bird's place in a loose 14 m flock, its wing beat (14-20 Hz strokes with a glide), and its heading come from its
  instance id and the clock in the vertex shader, so there is no script and no per-bird CPU. Every 150 s the flock
  crosses a 300 m chord 120 m out and 80 m up, for 35 % of the period. The rest of the time it is collapsed to one
  point and draws nothing. The chord's bearing comes from the crossing's index and a seed, so a level replays the
  same.
- **The airliner** (`airliner.gdshader`): one MultiMesh of seven unit boxes, one draw:
  - fuselage 38 m, wing 34 m, tailplane, fin;
  - a red and a green nav light and a tail strobe (`INSTANCE_CUSTOM.a` says which; they glow by `night`).

  It flies an approach track every 180 s: 5 km long at 75 m/s, 1,500 m out, descending 1,250 -> 1,000 m. That is
  inside the walk camera's 4,000 m far plane and `look_shots`' 2,000 m. An approach is a cause for this place:
  Philadelphia International sits on Delaware County's line. At approach height there is no contrail, so none is
  drawn.
- Both are unshaded, with no fog, no shadow, outside the bake (`gi_mode 0`), with a custom AABB that holds the level
  and every camera, and `ignore_occlusion_culling`.
- `proto_sky.py <walk copy> <centre x,z> [pin [bearing]]` writes them into a copy's `_walk.tscn`. `pin` holds both
  clocks for proof frames.

## What it looks like

`street_bearing300_pinned.webp`, at the street eye (7.9, 1.7, 16.7), looking 33 degrees up toward bearing 300, in
the level's own `blue_hour`. `street_bearing300_zoom6x.webp` is the centre at 6x. The airliner reads as an aircraft
about 12 px across: a pale cross with a tail. The flock is a loose cloud of one- to three-pixel dark marks, which is
what a flock is at 150 m. Neither has been seen moving yet: these are still frames with the clock held.

## On the way, refuted and kept

1. **The first frames showed nothing at either aim point**, and two causes were stacked:
   - `look_shots` aimed into a street tree and a rowhouse roof (the first station, bearing 270, flock at 45 m: the
     roofline 20 m off hides the sky below about 25 degrees from the street, which is why the flock now flies at
     33).
   - In the walk, the nodes were culled whatever their bounds. A MultiMesh's own `custom_aabb` was added first,
     while the station still aimed into the tree, so its effect on its own was never measured. It is kept.
2. **`sky_pixels.gd`'s first version** moved the walk's camera and counted magenta. It read 0 for a plain box too,
   because the walk's warm-up sweep drives its own camera for about 560 frames. Refuted; its comment says so. Its
   second version, in a bare scene with only a camera and copies of the two nodes, counted the diagnostic box at
   52,821 lit samples. So the shader and the MultiMesh drew. What hid them in the walk was occlusion culling (on in
   the walk: `occlusion_culling: True` in every `look_shots` record), and `ignore_occlusion_culling = true` brought
   both into the frame.
3. A diagnostic shader used `return` in `vertex()`. Godot refuses it ("Using 'return' in the 'vertex' processor
   function is incorrect"), and the compile failure printed only in a windowed run (`sky_compile.gd`, which also
   showed the real shaders compile).

## The price

`price.py` priced it on the clock, against 9391's walk copy twice, in one session, over the package's 53 headings
(`price_<arm>.json`, `price_compare.out.txt`).

| arm - ctrl | draws | median ms, mean of headings | median of the differences | worst heading |
|---|---|---|---|---|
| ctrl2 (the control again) | -47 total, at one heading | +0.055 | +0.030 | +0.395 |
| sky | **+2 at every heading** (+106) | +0.079 | +0.070 | +0.837 |

- **Draws: exactly as expected.** Both bounds hold every camera, so the two nodes are submitted at every heading
  whether or not anything is in the sky.
- **Frame time: at the noise floor, a little over it.** The mean is +0.024 ms past the control's own spread, and the
  median of the differences is +0.04 ms past it. That is two submissions' worth on this machine, about what 2 of
  roughly 700 draws should cost. Not a rounding of zero; small.
- **One p95 spike.** The sky arm reported `extraction_15` over its frame budget: yaw 270, p95 14.24 ms against 9.99
  and 9.62 in the controls, with the median 9.71 against 9.38 and 9.31 (`extraction_15.out.txt`). A single hitch
  in one heading, with the median barely moved, is the shape a first-use shader compile would make. That is not
  established: the station order was not recorded. A ship would warm the two shaders up with the rest (the walk's
  warm-up sweep, `Mission/Warmup`).
- **Found on the way: 9391 is over a draw budget without any sky.** Both controls reported `attacker_spawn_5` at
  2,004 draws, over budget. In cold run 9391's own price, 9389's walk copy was inside budget at every station and
  9391's was over at this one. That is the brass knob's +582 draws, which Level Factory 0.242.0 answers. The next
  cold run's price should show it inside again.

## Open

- **Motion.** The flock's beat and drift, and the airliner's pace, need a walk to judge. A still frame cannot.
- **Time of day.** The `night` uniform is fixed at 0.5. It should read Lux's time of day.
- **Seeds.** `seed` should be the level's.
- **Placement.** `centre` should be the plate's centre, not a station.
- **Variety.** A gull and a pigeon species and a second aircraft (a regional jet) are open.
- **Owners.** Zoo would own the meshes as species; Level Factory or Lux would place them and own the shader.
