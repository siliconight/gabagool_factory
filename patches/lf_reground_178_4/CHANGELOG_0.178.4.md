## [0.178.4] - Re-grounded to the set factory 1.38.0 certifies

**Roadmap 202.** `contracts.GROUNDED` and the stand-in repos move four
rows to the tools factory 1.38.0 is certified with:

| tool | was | now |
|---|---|---|
| Deli Counter | 0.207.1 | 0.208.0 |
| Lot | 0.115.0 | 0.116.0 |
| Zoo | 1.97.0 | 1.100.0 |
| Lux | 0.74.0 | 0.75.0 |

Nothing else changes.

**Why now, and before the install test.** 0.172.1's note says a tool's
release owes this table its row before the factory certifies a set
carrying it: a package with these tools and the old rows prints four
`drift vs certified ... re-certify` WARNs at a stranger's first `setup`,
advice they cannot act on.

**Licensed by the real-tool smoke,** `LF_TOOLS_DIR=<factory> pytest
tests/real_tools`: before, 10 of 12 ran and `test_grounded_matches_the_tools_this_smoke_ran` failed on exactly the four rows (`deli_counter grounded 0.207.1 installed Deli Counter 0.208.0 [DRIFT]`, lot 0.115.0 against 0.116.0, lux 0.74.0 against 0.75.0, zoo 1.97.0 against 1.100.0) while `test_real_deli_new_level`, `test_real_lot`, `test_real_lux_addon_and_driver_invocation` and `test_real_zoo_plan` ran against the new versions; after, 11 of 12 ran and the run exited 0, `test_real_dispatch` skipped as before, its example's build inputs absent.

**Suite:** 2,226 passed, 14 skipped, 1 xfailed, exit 0, as 0.178.3 -- the re-grounding is proven by the smoke, which skips in this suite without LF_TOOLS_DIR; here `test_the_stub_repos_declare_the_grounded_versions` and the facade's `test_doctor_passes` read the moved stand-ins.
