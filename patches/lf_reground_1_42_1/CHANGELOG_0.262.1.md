## [0.262.1] - `contracts.GROUNDED` re-grounded for factory 1.42.1: eight rows

Factory 1.42.0 was certified and published with this table still at 1.41.0's versions: its install test's setup
read five `drift vs certified ... re-certify` lines, and the factory's record said the manifest's promotion would
clear them. It does not: the doctor reads this table, and 0.172.1's rule is that any tool's release owes it its row
before the factory certifies a set carrying it. Re-grounded ahead of install test 14, which certifies 1.42.1.

### Changed
- **Eight rows**: deli_counter 0.241.0 -> 0.286.1, dispatch 0.5.3 -> 0.5.4, laser_tag 0.32.0 -> 0.32.1, lot 0.126.0
  -> 0.135.0, lux 0.79.0 -> 0.80.0, patina 0.32.0 -> 0.32.1, pixelcoat 0.62.0 -> 0.63.0, zoo 1.117.0 -> 1.142.0 --
  every release since factory 1.41.0, the last four the releases that carry each repo's MIT `LICENSE`.
- The stand-in tools follow the pins: the eight fixture repos' VERSION files, the stub Deli Counter's contract
  command reporting 0.286.1 and the stub Dispatch's contract and build lock 0.5.4.

### Measured
- The real-tool smoke before: exactly these eight rows DRIFT, 10 of 12 ran, Dispatch's example skipped as before
  (the factory's `patches/lf_reground_1_42_1/smoke_before.out.txt`). After: exit 0, 11 of 12 ran, dispatch's example skipped as before (`smoke_after.out.txt`).
- The suite: exit 0, 2,808 by the progress tally (2,759 passed, 14 skipped, 1 xfail) (`suite.out.txt`).

