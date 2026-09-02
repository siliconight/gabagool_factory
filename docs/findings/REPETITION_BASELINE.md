# Facade repetition: the first reading

**Date:** 2026-08-29
**Instrument:** `tools/repetition_census.py` (new)
**Raw:** `docs/findings/REPETITION_LIBRARY_BASELINE.json`,
`docs/cold_runs/cold_7003/repetition_before_relief.json`

## Why there is a number at all

Walked `bank_block_001` seed 7003 in the themed walk project and the buildings
read as machine-made Lego. Every other claim in this factory is measured; that
one was not, so it was going to be answered by squinting, and a value tuned
that way cannot be reproduced across themes or defended against the next
person's eye. So: a ruler first, then a decision.

## What is measured

Per wall run, from either the composed `.tscn` or Deli Counter's own
`*.slots.json`:

- `segments`, `span_m`, `pitch_m`
- `distinct_stems` / `distinct_forms` -- a **form** is a mesh AND the scale it
  was stretched to, because DC scales `wallEnd` per slot and three wallEnds at
  three widths are three things, not one
- **`longest_identical_run`** -- consecutive identical forms in spatial order.
  Floor 1, ceiling the run's own segment count. This is the Lego number.
- `dominant_share` -- the most-placed form's share of the run

No threshold is applied. Where the gate belongs is a taste call.

## The reading

Twelve buildings off the shipped library, plus the one that was walked.

| building | insts | stems | forms | reuse | worst | runs that are 100% one form |
|---|---|---|---|---|---|---|
| large_warehouse_a03 | 356 | 13 | 33 | 10.79 | **28** | 7 / 15 |
| arena_a01 | 237 | 10 | 27 | 8.78 | **27** | 4 / 10 |
| arena_a03 | 238 | 16 | 32 | 7.44 | **26** | 3 / 11 |
| country_club_a01 | 179 | 13 | 23 | 7.78 | 20 | 5 / 10 |
| supermarket_a03 | 184 | 11 | 21 | 8.76 | 20 | 5 / 10 |
| bank_tower_a01 | 176 | 5 | 20 | 8.80 | 19 | 4 / 10 |
| mansion_a03 | 272 | 12 | 29 | 9.38 | 19 | 6 / 16 |
| depot_a01 | 110 | 9 | 23 | 4.78 | 13 | 0 / 6 |
| bank_tower_a03 | 99 | 5 | 23 | 4.30 | 9 | 0 / 6 |
| gas_station_a01 | 79 | 12 | 29 | 2.72 | 8 | 0 / 6 |
| pharmacy_a01 | 67 | 12 | 20 | 3.35 | 7 | 0 / 6 |
| strip_retail_a02 | 54 | 12 | 22 | 2.45 | 7 | 1 / 6 |

`worst_run` median **19**, range 7 to 28.
`bank_block_001` seed 7003 (the one walked, read from its composed scene) sits
at **14** -- *below* the library median. What was walked is not an outlier; it
is a good day.

## What the shape of the table says

**Repetition tracks facade length, not authoring.** The small buildings score
well because their runs are short enough that they cannot repeat -- a 14 m run
holds seven modules and cannot hold twenty. The large ones score badly in
direct proportion to their spans. `large_warehouse_a03` has seven runs that
are 100% a single form; `mansion_a03` has six.

Every run in every building measured sits at pitch **2.00 m**, which is
`DC_MODULE`'s default and `_wall_span`'s tiling of each solid span into whole
modules of that size (`deli_counter.py:756`). The metronome is exact, and it
is the thing the eye reads as manufactured before it reads any single panel.

The consequence for planning: **there is no floor.** A 100 m facade is fifty
identical panels. Any fix that does not scale with run length is a patch on
today's buildings, not a position on future ones.

## What this ruler cannot see

It measures the repetition of the **form vocabulary**. Per-instance variation
-- Patina's `--slot-variation`, Pixelcoat's gen-7 `variations` -- changes how
two copies of one mesh look without changing that they are one mesh, so a run
of fourteen would still read fourteen here after that work landed. A flat
number is not that work failing; it is this ruler not pointed at it. Judging
per-instance variation needs a second instrument that reads appearance, and
none exists.

Also unverified: the two readers (composed scene, slot manifest) have not been
cross-checked on a single building. The check needs a workspace that both
generated and composed, and level_factory hardlinks its job outputs, so a
`shell.slots.json` has to be copied before it can be pulled off the machine.
Until that is done, compare slots to slots and scenes to scenes.

## Not concluded here

The census does not say which layer should own variation. It says how much
there is to fix and that the problem grows with building size.
