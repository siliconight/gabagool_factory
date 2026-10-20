## [0.226.1] - the certified table re-grounded for factory 1.41.0

`contracts.GROUNDED` moves six rows to the set factory 1.41.0 certifies, ahead of the install test that certifies it,
as 0.172.1's note says it must be. A package carrying these tools with the old rows would print six `drift vs
certified ... re-certify` WARNs at a stranger's first `setup`.
- deli_counter 0.222.0 -> 0.240.0: among them a lid on every roof hatch and its hole matching it, every hole in a
  floor given a cause and made an optional route, the walker's open-floor table, the facade planner's first rows,
  and two box slots built as the species they name.
- dispatch 0.5.2 -> 0.5.3: a declared drop's off-mesh link reaches the package.
- lot 0.123.0 -> 0.126.0: among them an isolated building as a major finding, a declared drop's nav link in site
  space, and every piece at a bus stop facing the road.
- lux 0.77.0 -> 0.79.0: runtime scaffolding ownerless in the editor, and a morning and a high noon.
- patina 0.31.0 -> 0.32.0: the Godot half removed.
- zoo 1.112.0 -> 1.117.0: among them the roof hatch, a floor hole that says why it is there, a desk's computer on,
  and a payphone's four looks with their marks small and mostly weather.
- laser_tag 0.32.0 and pixelcoat 0.62.0 stand as they were.
- **The stand-in tool repos follow the pins** (`tests/fixtures/repos/*/VERSION`), as
  `test_the_stub_repos_declare_the_grounded_versions` asks; the stub Deli Counter's `contract` command reports
  0.240.0, and the stub Dispatch's contract and build lock 0.5.3.

**Licensed by the real-tool smoke** (`LF_TOOLS_DIR=<factory> pytest tests/real_tools`): before, exactly the six rows
DRIFT and `test_grounded_matches_the_tools_this_smoke_ran` failing on them alone, 10 of 12 ran, dispatch's example
skipped as before (the factory's `patches/lf_reground_1_41_0/smoke_before.out.txt`); after, exit 0, 11 of 12 ran, dispatch's example skipped as before (`smoke_after.out.txt`)

**Suite:** exit 0, 2,566 by the progress tally (2,551 passed, 14 skipped, 1 xfail), 0.226.0's count (`suite.out.txt`)

