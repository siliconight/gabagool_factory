## [0.165.0] - A traffic signal lights one lens at a time, every head in step

**The walker, 2026-10-09,** walking club_block_014 (roadmap 219, note 9):
"stop lights are only bright for 1 color at a time, and if you have 2 here,
they need to be the same".

**What was there.** Zoo's `traffic_signal` lights all three lenses at
strength 1.6, on purpose: "Which lens is LIT is not baked ... A signal whose
state is baked is a signal that is wrong half the time." It leaves the state
to whoever runs the level. Nothing ran it.

### What it is now

**The import gives each lens its clock** (`assets/godot/zoo_worldskin.gd`,
`_signal_lenses`). Every surface wearing `M_TrafficSignal_Lens_<colour>`
takes one lit shader. It is lit while `mod(TIME, 60)` is in its colour's
window:
- green from 0 to 33 s;
- amber from 33 to 37 s, MUTCD's yellow change interval of 3 to 6 s;
- red from 37 to 60 s.

The windows are whole seconds, so a boundary two windows share is one float
in both, and exactly one lens is lit at every instant. Otherwise the lens is
its own colour at 0.12, dark glass: Zoo's albedo is the full colour, which by
day would read as a painted disc.

**One clock for every signal: no per-node term,** where the shutters and the
turning parts have one. Lot stands a signal only on a yielding leg's corner,
its heads facing the through road. Measured on Lot's tee and crossroads, that
is both directions of the road at a crossroads, and no head faces the side
street. So every head at a junction serves the same traffic and shows the
same lens. Two heads on one pole share a lens mesh a colour.

**A lit shader, in the material.**
- **The model keeps its bake.** A clock in a second UV set, the shutters'
  way, would have left the whole signal unbaked (`light_bake.py`).
- **The glass takes the street's light.**
- **Lux's binder never sees these lenses.** It takes names ending `_Lens`,
  `_Diffuser` or `_Face`, and collects only `BaseMaterial3D`.

**What it will not guess at.** A colour with no window, or a lens exported
with no emission, is left as Zoo made it and warned about.

### The price

- **No geometry, draw or texture added.**
- **The three lens materials are now three `ShaderMaterial`s on one shader,**
  where they were three `StandardMaterial3D`s.
- **Per lens pixel,** a `mod` and two `step`s; on the CPU, nothing per frame.
- **The model's bake is unchanged.**

### Measured in Godot 4.7

`docs/findings/signal_lenses/` at the factory root. Cold run 9213's signal
GLB was imported through this script in a GL Compatibility project:
`[worldskin] signal.glb  3 signal lens surface(s) given the junction's
clock`. All three came back `ShaderMaterial`, each with its window.

A windowed probe sampled both heads every half second from 28 to 42 s:
- green until 33.0, amber from 33.5 to 37.0, red from 37.5;
- the heads agreed in all 31 samples;
- a lit lens read 1.00 and an unlit one 0.06 to 0.11.

*An earlier run is kept,* which had red at 35 s. Its probe clock and the
shader's `TIME` were at least 2 s apart. The probe reads only its own clock
and cannot say why.

### What it does not cover

- **A level.** The bake, the grade and a real night are owed by the proof
  run's frames. Whether a lit custom shader keeps its lightmap is Godot's
  rule, unmeasured here.
- **The bake's emission** is whichever lens is lit when the editor bakes,
  where it was all three.
- **Every junction in a level runs in step,** as a coordinated arterial does.
  An offset per junction would need a key nothing carries.

### Tests

`tests/unit/test_worldskin_signal_lenses.py`, reading the GDScript, as the
shutters' tests do:
- the pass runs for every GLB before the kit branch;
- the names are Zoo's, read off Zoo's recipe when it is beside this repo;
- the windows tile the cycle with one lens lit at every quarter second;
- amber is 3 to 6 s;
- the shader has no per-node term;
- it is lit, not unshaded, and reads no UV2;
- a lens it cannot read is left alone and warned about.

All seven fail on 0.164.0, which has no such constants, function or shader.

**A guard caught the release's first suite run.**
`test_worldskin_crt_motion.py`'s `test_nothing_elses_material_class_changes`
pins which passes REPLACE a surface's material, so that a new one is
deliberate. `_signal_lenses` is one, and joins `MATERIAL_REPLACERS`.

**Suite:** 2,067 passed, 14 skipped, 1 xfailed, 0 failed (exit 0; the
progress characters tallied). That is 0.163.0's recorded 2,048, plus:
- 0.163.1's 9 tests and one more file for `test_sibling_locator.py`;
- 0.164.0's 1;
- this release's 7 and one more file.
