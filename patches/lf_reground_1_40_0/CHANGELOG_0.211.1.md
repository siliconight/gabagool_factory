## [0.211.1] - the certified table re-grounded for factory 1.40.0

`contracts.GROUNDED` moves six rows to the set factory 1.40.0 certifies, ahead of the install test that certifies it,
as 0.172.1's note says it must be. A package carrying these tools with the old rows would print six `drift vs
certified ... re-certify` WARNs at a stranger's first `setup`.
- deli_counter 0.209.1 -> 0.222.0: among them a cut switchback's second flight on the floor under it, and the delis'
  basement closed with the utility room's door.
- laser_tag 0.27.0 -> 0.32.0: among them an arrival counted at the point, not at the end of a short path.
- lot 0.117.0 -> 0.123.0: among them an urban street's trees.
- lux 0.75.0 -> 0.77.0: among them a rig at rest before its scene is packed.
- patina 0.30.0 -> 0.31.0: a prop is not the building.
- zoo 1.103.0 -> 1.112.0: among them the fire escape, the bevel's restart, a desk's stock facing its sitter, and a
  banded door's trade.
- pixelcoat 0.62.0 and dispatch 0.5.2 stand as they were.
- **The stand-in tool repos follow the pins** (`tests/fixtures/repos/*/VERSION`), as
  `test_the_stub_repos_declare_the_grounded_versions` asks. The stub Deli Counter's `contract` command reports
  0.222.0; it had said 0.208.0 since 0.178.4, two re-grounds behind.

**Licensed by the real-tool smoke** (`LF_TOOLS_DIR=<factory> pytest tests/real_tools`): before, exactly the six rows DRIFT and `test_grounded_matches_the_tools_this_smoke_ran` failing on them alone, 10 of 12 ran (the factory's `patches/lf_reground_1_40_0/smoke_before.out.txt`); after, exit 0, 11 of 12 ran, dispatch's example skipped as before (`smoke_after.out.txt`)

**Suite:** exit 0, 2,437 by the progress tally (2,422 passed, 14 skipped, 1 xfail), 0.211.0's count. The first run, with the table moved and the stand-ins not, failed `test_the_stub_repos_declare_the_grounded_versions` on exactly the six; the stand-ins now follow
