## [0.262.2] - `contracts.GROUNDED`'s deli_counter row re-grounded for factory 1.42.1

Deli Counter 0.286.2 releases the migrations index line committed after 0.286.1 was tagged, which the factory's
`verify-manifest --strict` read STALE. One row, as 0.226.2 re-grounded one for 1.41.0.

### Changed
- **deli_counter 0.286.1 -> 0.286.2**; the stand-in Deli Counter's VERSION and contract command follow it.

### Measured
- The real-tool smoke before: exactly this row DRIFT (the factory's
  `patches/lf_reground_0262_2/smoke_before.out.txt`). After: exit 0, 11 of 12 ran, dispatch's example skipped as before (`smoke_after.out.txt`).
- The suite: exit 0, 2,808 by the progress tally (2,759 passed, 14 skipped, 1 xfail), 0.262.1's count (`suite.out.txt`).

