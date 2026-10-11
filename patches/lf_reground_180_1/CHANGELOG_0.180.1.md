## [0.180.1] - Re-grounded to Lot 0.117.0: the walk test's clock no longer waits

**Roadmap 239.** `contracts.GROUNDED` and the stand-in repo move one row:
lot 0.116.0 -> 0.117.0. Nothing else changes.

Lot 0.117.0 is the walk test's half of 0.180.0's lever. Its setup script
makes the navigation map and the site's region update synchronously before
it bakes, and `walktest.py` launches the scene under `--fixed-fps 60`: on
cold run 9247's three staged walk tests, 4.2 to 5.3 s against 122.0 to 150.1
s, each report its job's but the director's `map_iteration` diagnostic
(2 -> 1), the same twice and three at once. Level Factory's
`walktest_navqa` job runs Lot's `walktest.py`, so the flag is Lot's to pass
and this release only follows the version.

**Real-tool smoke:** 12 tests against the factory's own tools: before this release exactly the one row read DRIFT (lot grounded 0.116.0, installed Lot 0.117.0), after it 11 passed and 1 skipped (dispatch's example inputs absent, as before)

**Suite:** 2,251 passed, 16 skipped, 0 failed (JUnit, 2,267 tests), as 0.180.0
