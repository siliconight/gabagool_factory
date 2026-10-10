# The streetlight shadow selftest's on-axis control (roadmap 222)

**Question.** Lux's windowed `tools/streetlight_shadow_selftest.gd` has two
controls that prove its instrument sees a shadow at all:
- **the slab:** a slab a metre under the lamp blacks the pool;
- **the cap:** the lamp moved onto the pole's axis at the lens point, at bias
  0.03, is blacked by the shaft's cap 5 mm below it.

Earlier on 2026-10-10 the cap control failed twice, on Lux 0.71.0 HEAD and on
0.72.0's draft, with the GPU idle:
- **the readings:** on the axis 0.447, against 0.459 unshadowed. The control
  wants under a tenth;
- **the record:** 0.71.0's own changelog has it passing.

Why does a control that passed stop seeing its shadow?

**Answer: it does not fail now, and why it failed then is not established.**

## Measured, 2026-10-10 from 04:30

**The selftest, unchanged:**
- once on a working-tree copy of Lux 0.72.0, then five times more in a row on
  the same copy (`selftest_runs.txt`);
- once in the Lux repo itself, whose working tree was clean before and after.

All seven print `placed 0.453 unshadowed 0.459 on the axis at the lens 0.001
under a slab 0.000`, and `streetlight shadow selftest: PASS`. The machine was
the same, with Godot 4.7 stable and NVIDIA 616.56 (`probe1.txt` prints the
adapter).

**The two probes** build the selftest's lamp from Lux's own loader
(`rig_for_anchor` for a streetlight) over a bare 0.06 m shaft. They read the
same band of the frame as the selftest, as luma 0..1. To run one, copy it
into a Lux checkout's `tools/`; it opens a window and quits itself.

**`shadow_gap_probe.gd` (`probe1.txt`):** the shaft's cap 5 mm, 2 cm, 5 cm,
10 cm and 30 cm under the lamp, at biases 0.00, 0.01, 0.03 and 0.10. The
unshadowed pool reads 0.447 throughout.

| gap | bias 0.00 | 0.01 | 0.03 | 0.10 |
|---|---|---|---|---|
| 5 mm | 0.447 | 0.000 | 0.001 | 0.081 |
| 2 cm | 0.447 | 0.000 | 0.000 | 0.004 |
| 5 cm | 0.000 | 0.000 | 0.000 | 0.000 |
| 10 cm | 0.185 | 0.185 | 0.185 | 0.185 |
| 30 cm | 0.419 | 0.419 | 0.419 | 0.419 |

- **At the selftest's own setting the pool is black.** That is a 5 mm gap at
  bias 0.03, reading 0.001.
- **At 10 and 30 cm the pool is partly lit at every bias.** The cap sits
  further below the lamp and covers less of a 55 degree cone. This is what
  the geometry says should happen.
- **At bias 0.00 and gaps of 2 cm or less, the shadow is not drawn at all:**
  0.447, the unshadowed pool. At 0.10, the pole's own bias, a 5 mm cap lets
  0.081 through. That is the selftest's own reason for running its control
  at 0.03.

**`shadow_gap_probe2.gd` (`probe2.txt`): is the first read after switching
the shadow on the stale one?** In the first probe, bias 0.00 was always read
first after `shadow_enabled = true`. The selftest's control is also its
first read after switching back on. So per gap the second probe takes six
reads:
- with the shadow off;
- with it on at bias 0.03, twice with nothing changed in between;
- at bias 0.00, twice;
- at bias 0.03 once more.

| gap | off | on, 0.03 | again | 0.00 | again | 0.03 |
|---|---|---|---|---|---|---|
| 5 mm | 0.447 | 0.001 | 0.001 | 0.447 | 0.447 | 0.001 |
| 2 cm | 0.447 | 0.000 | 0.000 | 0.447 | 0.447 | 0.000 |
| 5 cm | 0.447 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

**Refuted: the first read after switching on is not stale.** Bias 0.03 is
black on its first read, and bias 0.00's lost shadow is lost on both reads.
What decides the 5 mm and 2 cm cases is the bias, not the order.

## What is not known

- **What was different during the two failing runs.** The code, the binary
  and the driver are the same as now. Not recorded then, and worth
  capturing the next time the test fails:
  - the window's state: minimised, covered, or the display asleep;
  - the frame itself, saved beside the reading;
  - what else held the GPU.
- **Why bias 0.00 loses the shadow at a 2 cm gap** while 0.01 keeps it. That
  is a fact about Godot's spot shadow in the Compatibility renderer, and the
  cap control does not depend on it.
