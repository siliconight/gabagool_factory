## [0.193.1] - re-grounded to Zoo 1.103.0, a mesh's faces in one order (factory roadmap 239)

**Why.** Zoo 1.103.0 makes every Zoo job build the same bytes twice -- every
mesh's faces sorted before it is written, operators given their input in one
order, the faces a fill or a bisect makes started at their lowest vertex --
and cold runs 9260 and 9261 baked one lightmap. The grounded table still said
1.102.0, so a package carrying Zoo 1.103.0 would print `drift vs certified
1.102.0 ... re-certify` at a stranger's first `setup`, ahead of the install
test that certifies factory 1.39.0.

**What changed.** One row of `contracts.GROUNDED`, zoo 1.102.0 -> 1.103.0,
and the test stand-in's `tests/fixtures/repos/zoo/VERSION`.

**Measured:** the real-tool smoke (LF_TOOLS_DIR=<factory> pytest tests/real_tools) read exactly the zoo row DRIFT on 0.193.0 -- grounded 1.102.0, installed 1.103.0 -- and on 0.193.1 11 passed, 1 skipped (dispatch's example ships no build inputs), 0 failed

**Tests:** 2,332 passed, 16 skipped, 0 failed (JUnit, 2,348 tests), as 0.193.0
