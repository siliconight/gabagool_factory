## 0.119.2 - the wires' pixel floor is written as a float, so a scene reads it

**Factory roadmap 240, found in cold run 9264's package.** 0.119.1 wrote the wire material's
`shader_parameter/min_px = 1` -- an integer literal for the shader's `float min_px`. Godot reads that
as no value: the scene Lot writes loads `min_px` as null, and Lux's re-save of it
(`presentation/lux.applied.tscn`) writes `shader_parameter/min_px = null`. The wires drew as meant only
because a null parameter falls back to the shader's own default, which is 1.0 too; any other
`WIRE_MIN_PX` would have been dropped without a word -- a knob with no effect.

- **`min_px` is written as a float** (`1.0`), which Godot reads, keeps through a re-save and hands to
  the shader. The colour beside it was always read.

**Measured:** `docs/findings/pole_line/min_px_resave.gd`, Godot 4.7 headless: a scene written `shader_parameter/min_px = 1` or `= 2` loads the parameter null and saves it again as `null`; written `1.0` or `2.0` it loads, saves and reads back as written. Cold run 9264's package carried the null in Lux's re-saved scene; its frames drew right only because the shader's default is the same 1.0

**Tests:** The shader test now asks for `shader_parameter/min_px = 1.0`; `test_a_float_uniform_is_written_as_a_float` sets WIRE_MIN_PX to 1, 2 and 1.5 and asks each line for a decimal point and its value. On 0.119.1 both fail: `min_px = 1`, no decimal point

**Suite:** 819 passed, where 0.119.1 passed 818: the new test
