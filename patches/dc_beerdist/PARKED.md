# Deli Counter 0.297.0, a beer distributor -- PARKED at a pause (2026-10-31)

The walker asked for a safe pausing point mid-ship. State:

- The work is in the scratch clone `_scratch/dc-beerdist` (Deli Counter at e75c73d3): `presets.beer_distributor`
  (+ `BEER_NEON_EACH`, `REGISTRY`), `specs/beer_distributor_a01.json` (made by `new_level.py`), its build,
  `tests/test_beer_distributor.py`, VERSION 0.297.0 and its CHANGELOG entry.
- Proven: `fails_on_old.out.txt` (3 tests fail on 0.296.0); nav gate passed (3/3 entrances, 2/2 markers); layout lint
  clean (0 FAIL, 0 WARN).
- NOT run: the repo's gate (`ship_change.py gate deli_counter _scratch/dc-beerdist`) was stopped part-way at the pause --
  `gate.out.txt` is incomplete and proves nothing -- and the clone's full suite.
- Resume: run the gate, then the suite, then `ship_change.py patch` and `apply` (the message and doc are drafted in the
  session's scratchpad as `ship_dc_beerdist.py`'s outputs; rewrite them if lost). Then apply the parked Level Factory
  0.276.0 (`patch_lf_beer.py`), then build a slice to see the distributor on Delco Avenue.
