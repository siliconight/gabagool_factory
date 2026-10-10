## [0.172.1] - Re-grounded to Lot 0.106.0

**Roadmap 202.** `contracts.GROUNDED` and the stand-in Lot repo move from
Lot 0.105.0 to 0.106.0. That is the release that keeps a lamp or a tree out
of a shop band's span (roadmap 226, proven in cold run 9223). Nothing else
changes.

**Why now.** Cold run 9223's doctor WARNed:

    tool:lot  vLot 0.106.0 @ e3b8b468 — drift vs certified 0.105.0 (grounded); re-certify

The run's notes recorded only the Windows long-paths reminder beside it.
`setup` on a package carrying Lot 0.106.0 would print the same advice to a
stranger, who cannot act on it. Install test 3 was stopped at its unpack on
finding it, before its setup ran.

**Licensed by the real-tool smoke,** `LF_TOOLS_DIR=<factory> pytest
tests/real_tools`.
- **Before:** 10 of 12 ran. `test_grounded_matches_the_tools_this_smoke_ran`
  failed on one row, `lot grounded 0.105.0 installed Lot 0.106.0 [DRIFT]`,
  while `test_real_lot` passed against 0.106.0.
- **After:** 11 of 12 ran and the run exited 0. `test_grounded_matches_the_tools_this_smoke_ran` passes; `test_real_dispatch` skipped as before, its example's build inputs absent.

**Suite:** 2,153 passed, 14 skipped, 1 xfailed, exit 0, as 0.172.0. The change is proven by the smoke, which skips in this suite without `LF_TOOLS_DIR`; here `test_the_stub_repos_declare_the_grounded_versions` holds the stand-in Lot to the new row.
