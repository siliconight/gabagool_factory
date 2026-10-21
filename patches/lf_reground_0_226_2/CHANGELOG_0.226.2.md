## [0.226.2] - the certified table's deli_counter row at 0.241.0

`contracts.GROUNDED` moves one row for factory 1.41.0: deli_counter 0.240.0 -> 0.241.0, where a ramp's slab cut stops
at its head, railed, with a landing past it. 0.226.1 grounded the table to the set 1.41.0 was to certify; that set's
install test then stopped at the export on a parking garage's ramp (the factory's install test 10), Deli Counter
0.241.0 fixed it, and the set the factory certifies carries it. Without this row a package carrying 0.241.0 prints a
`drift vs certified ... re-certify` WARN at a stranger's first `setup`.
- **The stand-in follows the pin**: `tests/fixtures/repos/deli_counter/VERSION`, and the stub's `contract` command
  reports 0.241.0.

**Licensed by the real-tool smoke** (`LF_TOOLS_DIR=<factory> pytest tests/real_tools`): before, exactly this row
DRIFT (the factory's `patches/lf_reground_0_226_2/smoke_before.out.txt`); after, exit 0, 11 of 12 ran, dispatch's example skipped as before (`smoke_after.out.txt`)

**Suite:** exit 0, 2,566 by the progress tally (2,551 passed, 14 skipped, 1 xfail), 0.226.1's count (`suite.out.txt`)

