## [0.160.0] - The light bake keeps a cycling rig live

**Roadmap 213, decided 2026-10-08.** The walker: "Stage can be brighter, im
ok with live or baked, whatever you think is the best". The call: live, so
the club's stage colour cycle runs.
- **The defect.** The bake marked every Lux rig resource without a
  `failing_kind` BAKE_STATIC (`mark_steady_rigs`), and a baked stage rig
  stops cycling (`lux_stage_light_rig.gd`, `_cycles()`). So every club
  package shipped its stage show frozen on one colour.
- **Lux 0.69.0 is the other half.** A cycling rig's lamps carry no indirect
  energy, so a live stage bakes no frozen bounce. The stage is lit at
  `CLUB_STAGE_LEVEL` 24, up from 3.

### The trap

The cycle is the rig NODE's: `cycle_period_s` and `colors` are
`LuxStageLightRig` exports. `mark_steady_rigs` reads rig RESOURCES, which
carry only `bake_mode` and the lamp numbers. So:
- **`_cycling_rigs`** reads the scene's node blocks for the resources a
  cycling node uses. It asks the rig's own test: `cycle_period_s` over 0,
  across two or more `colors`.
- **`mark_steady_rigs`** leaves those resources as Lux wrote them. It
  returns a third count, `cycling`, which the bake's log line prints:
  "N failing and N cycling left live".
- **One cycling user is enough.** A resource shared by a cycling node and a
  still one stays live.

### Measured on the real scene

Cold run 9204's club_block_014, its Lux job's pre-bake `lux.applied.tscn`,
marked by each version on a copy:

| | baked | failing, live | cycling, live |
|---|---|---|---|
| 0.159.0 | 78 | 13 | -- |
| 0.160.0 | 76 | 13 | 2 |

- **0.159.0 is the run's own log line:** "78 steady rig(s) baked, 13
  failing left live".
- **The two left live are the club's stages:** `Resource_b1dm2` and
  `Resource_jitlq`, "Stage Light (baked)" by name. They carry no
  `bake_mode` line, which is Lux's Realtime.

### Tests

`tests/unit/test_light_bake_cycling.py`, 2 tests.
- **The fixture** puts a cycling stage node beside one of each way not to
  cycle: still, one colour, zero period. It adds a resource shared between
  a cycling node and a still one, a failing tube and a steady rig.
- **On 0.159.0** the first test fails, since every stage resource is baked.
  The second passes on both versions: it is the control.
- **`test_light_bake.py`'s** two assertions on the return carry the new key,
  `"cycling": 0`.
- **Suite:** 2,029 passed, 14 skipped, 1 xfailed, 0 failed (exit 0;
  progress characters tallied).
