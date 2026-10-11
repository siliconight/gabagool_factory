## [0.179.0] - Roof props reach a level: a job of their own per enterable building

**Roadmap 181.** Zoo 0.25's rooftop scatter -- units, vent stacks, exhaust
fans, skylights, a dish -- was planned by nothing. The Zoo adapter's kit
branch added `--roof-props` to the kit's command for a job spec key,
`roof_props_slots`, that no planner wrote; and had one written it, the
command could not have run both: `zoo_cli` answers `--roof-props` before
`--build-kit` and returns. Found 2026-10-05 while the Empties took the
dressing path for their antennas; closed here with Zoo 1.101.0 (the props
keep off the roof's hatches and landings, stand in the box they occupy,
and draw as one roof) and Deli Counter 0.209.0 (the landings on the roof
slot, the third layer, the gate's third arm).

- **`zoo_roof_props_build`**, a stage of its own in LAYER_ART, planned per
  enterable building whose slot manifest carries a roof slot
  (`building_library.has_roof_slot`; 133 of the library's 145 do), after
  the lot and the skin library, with the compose waiting on it. An Empty
  is planned in its own loop and gets none: its roof is never reached and
  carries its antenna already. The mission's own shell gets one unseen (its
  slots are its Deli Counter job's). The brief's **`roof_props: false`**
  plans none; `true` is the default, outside the functional signature (a
  roof prop is art and changes nothing a lock protects).
- **The job spec** reads its own slots as the kit does (the library row's,
  or `shell.slots.json`), the theme, the seed and the Pixelcoat library;
  **the adapter's `roof_props` mode** plans one Blender command
  (`--roof-props <slots> --out <work> --no-blend`, with `--skins`,
  `--theme`, `--wet`, `--seed`, `--density` when given) and expects
  `<building>_roofprops.built.json` and `.glb`. The kit branch's dead
  `roof_props_slots` read is gone, with a note where it stood.
- **A third content layer through the compose:** `roofprops_glb` resolved
  per building like the dressing and the fixtures (validated, hashed,
  passed as `--roofprops`), the driver bundling it through Deli Counter's
  `roofprops_glb`, and `_circulation_arms` and `circulation_gate` reading
  the `roofprops` arm 0.209.0 writes.

### Tests

`tests/unit/test_roof_props_stage.py`, eight tests: every enterable
building gets its own roof job and the compose waits on it; a building
without a roof slot gets none; an Empty gets a kit and no roof job; the
brief can plan none and reads the key; each job reads its own slots and
the skin library; the adapter plans the command and refuses missing slots;
the kit command no longer carries `--roof-props`; the gate reads the
third arm. `test_fanout.py`: the fake library's shells carry a roof slot,
the fan-out and compose lists name the stage, and the single-shell golden
plan grows the job (deliberately: nothing the lock protects moves). The
fake Zoo answers `--roof-props` with the index and GLB the adapter expects,
the stub composer takes the third layer, and the integration run asserts
the stage succeeded.

**Suite:** RESULT_SUITE
