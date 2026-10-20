# The drop-edge probe models the body (roadmap 173, What is left item 7), 2026-10-20: shipped, Level Factory 0.222.0

**What was asked.** The lattice phase sweep (`../phase_sweep/`) found one phase of the gate's 0.5 m lattice at which
restaurant_row_001 -- passed by the shipped phase -- was refused, and its flood reached a quarter less of the level.
Both were attributed to the standing probe's model of a body, and two candidate repairs were named, "neither started":
a body-fit test before a gap counts as a fall, and a standing test that ignores what a body steps over. This is both.

**What shipped** (Level Factory 0.222.0, `patches/patch_lf_edge_probe_body.py`; the instrument `walkable_edge.gd`,
synced to the factory's `tools/walkable_edge.gd`, sha256 98a9dab4f6310da7):

- **`STEP_M` 0.1025**, the contract's `clearances.unassisted_step_max_m`. The standing capsule (`PROBE_R` 0.20,
  `STAND_M` 1.80) stands that far up, its head where it was: a solid wholly below what a body walks over -- Lot's
  0.0974 m kerb, a threshold, a floor hatch's 3 cm frame -- no longer occupies the cell beside it. A slab's underside
  and a floor's edge under a wall stay occupied (the slab is 0.3 m deep, the wall a storey tall).
- **A body-fit test before a fall.** A drop that passes the barrier ray and the block capsule is asked whether a
  sphere of `BODY_R` (0.35, the contract's radius) fits in the opening it would fall through: its top 2 cm under the
  surface the body stands on, sampled along the step from 0.35 to 1.05 m past the cell every 5 cm. A drop no sample
  fits is `too_narrow`, reported and not an edge. Any opening 0.75 m or wider along the step holds a sample wherever
  the rim falls in the cell's half-step. **What it cannot see, written into the source:** the samples move along the
  step only, so a row within 0.35 m of an opening's side is too narrow as well, and the opening's middle rows report
  it; the gate refuses on any one row.

## The fixture (`level_factory/tests/unit/test_edge_probe_body.py`)

Small scenes of boxes through a real Godot, as `test_edge_seam.py` runs the seam:

- **A kerb.** Lot's 0.0974 m kerb with its face 0.038 m east of a column of cells -- the distance the sweep measured
  at the main road's south sidewalk. On 0.221.0 the flood reaches 480 cells, all on the ground west of the kerb; the
  sidewalk and the ground beyond it are unreached. Fixed: both reached.
- **A slot beside a hole.** A storey slab 3.3 m up, holding a 2.4 m hole with a 2.0 m block standing in it to the
  slab's top -- deli_a03's flight beside its hole, leaving a 0.4 m slot -- and a 2.2 m empty hole. The storey is
  shifted over a ground that stays put, four offsets a little over a quarter cell apart. **Found while writing it:**
  shifting the ground with the storey moved nothing, because the grid starts at the drawn extent's west edge; the
  first version of the test passed its slot assertion on 0.221.0 for that reason and was caught by the prove run
  failing on the wrong line. With the ground fixed, offsets 0.13 and 0.26 put a column in the slot 0.37 and 0.24 m off
  the block, where the probe fits on the floor below and 0.221.0 reports a 3.3 m unguarded drop, 15 rows -- the
  sweep's refusal, reproduced -- and 0.0 and 0.39 put it 3 mm and 0.11 m off, occupied, as the shipped phase did.
  Fixed: no row across the slot at any offset, and the 2.2 m hole found on all four sides at every offset.
- `STEP_M` and `BODY_R` are read against the real contract (`deli_counter/agent_contract.json`).

All six fail on 0.221.0 (`patches/lf_edge_probe_body/prove_tests_on_0221.out.txt`).

## On packages (`gate_ab.py`, `instruments.py`, `table.py`; `gate_ab/`, `logs/`, `table.out.txt`)

`instruments.py` writes an instrument at the phase sweep's six phases; `gate_ab.py` (the breadth sweep's, with the
new keys printed and a slim report kept per arm) runs the gate's own measure, classify and assert on a copy of a
package through every arm. Old is 0.221.0's instrument (the shipped one, sha256 352cad39, at p00), new is 0.222.0's.
Packages: precinct_yard_001 (cold runs 9343 and 9344 -- the same level; their arms agree to the cell, and `gate_ab/`
holds 9344's, whose files replaced 9343's under one name, `logs/` both), urban_row_001 (9345), deli_001 (9346).
**Each control arm reproduces its export's own scan** (reached, standable, unguarded and every count).

| package | reached at the six phases, old | reached, new | unguarded at p00, old -> new | too narrow | verdict |
|---|---|---|---|---|---|
| precinct_yard_001 | 120,461 .. 133,172 | 120,819 .. 134,967 | 54 -> 35 | 11 .. 26 | passes, every arm |
| urban_row_001 | **39,266** .. 52,524 | 51,614 .. 52,848 | 28 -> 14 | 4 .. 22 | passes, every arm |
| deli_001 | 25,505 .. 26,650 | 25,734 .. 26,669 | 35 -> 23 | 4 .. 20 | passes, every arm |

- **The moat is gone.** urban_row_001 at p11, the sweep's refusing phase, reached 39,266 of 60,205 cells on 0.221.0 --
  a quarter of the level lost, as restaurant_row_001's was -- and 52,030 of 66,419 on 0.222.0, in line with its other
  phases. Standable cells rise 2,400 to 6,700 a level: the cells beside low things.
- **No verdict moves**, 18 of 18 passing on each side.
- **Rows only the new probe finds:** 0 at the shipped phase on all three; at most 4 at any other, each attributed and
  each in a class the gate files -- the precinct's declared floor hatch in apartment_walkup_a01 (whose 3 cm frame no
  longer occupies the cell beside the hole, so its drops are asked), outdoor roof and storey rims, and a flight's own
  side on urban_row_001.
- **The slot's refusal is not on these packages**: none carries deli_a03. It is proven on the fixture.
- **Not attributed:** precinct_yard_001's reach still spans 14,000 cells across the phases, p33 the high end on both
  instruments; that spread is not the kerb's.

## What is left

- A package with deli_a03 through the same sweep (restaurant_row_001's seed 9003 still draws it).
- The precinct's phase spread above.
- The phase sweep's other open question -- refuse a row only where two phases agree, or sample finer at a drop --
  is less pressing with both of its attributed causes repaired; it stays open.
