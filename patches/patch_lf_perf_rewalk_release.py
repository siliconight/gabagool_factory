"""Level Factory 0.144.3: VERSION and the CHANGELOG entry for
`patch_lf_perf_rewalk.py`.

    python patch_lf_perf_rewalk_release.py
"""
import pathlib

LF = pathlib.Path(__file__).resolve().parent.parent / "level_factory"

ENTRY = '''## [0.144.3] - The price probe counts the scene as it is when it counts

**The breadth sweep's close-out could not price county_hospital_001** (cold
run 9173's package). `tools/perf_stations.gd` printed its sightline line, went
silent, and quit on its 600 s watchdog with nothing measured. It did that
twice, and nine other missions priced normally.

**Not the level.** A clock probe loaded the same package and ran 300 frames
in 2.8 s: 1.77 s for the first ten, which is shader warm-up, and about 15 ms
a frame after.

**The probe.** A debug copy of it showed the real cause:

    [dbg] draw-call check 0: 378
    [dbg] counting 6444 node(s)
    SCRIPT ERROR: Left operand of 'is' is a previously freed instance.

- The probe walks the scene once, at load, and reads that list again after
  about seventy frames, for the mesh count and the light census.
- The hospital's warm-up frees its own nodes by then; the clock run saw draw
  calls fall to 1 from frame 110.
- `is` on a freed instance is a script error. It killed the probe's
  coroutine and left nothing to quit but the watchdog.
- A level whose warm-up finishes quickly is a small level, which is why the
  street blocks never met it.

**The fix.** The tree is walked again immediately before the mesh count, and
the light census reads that fresh list with no frame between them.

**Measured after:** county_hospital_001 priced completely. 33 views, median
1.65 ms, worst 2.71 ms, none over 16.7 ms at p95, and the two passes agreed
within 0.41 ms.

**Tests.** `tests/unit/test_perf_rewalk.py` pins the order in the probe's
source: a walk between the last frame the probe waits on and the count, and
no `await` between the count and the census. Godot does not run in the suite;
the hospital's price is the run that proves it. The test fails on 0.144.2.

**Suite:** 1,931 collected: 1,916 passed, 14 skipped, 1 xfail. That is
0.144.2's 1,929, plus this test, plus its `test_sibling_locator` case.

'''


def main():
    version = LF / "VERSION"
    changelog = LF / "CHANGELOG.md"
    v = version.read_bytes()
    assert v == b"0.144.2", v
    c = changelog.read_bytes()
    assert b"\r\n" not in c
    assert c.startswith(b"## [0.144.2] - "), c[:60]
    version.write_bytes(b"0.144.3")
    changelog.write_bytes(ENTRY.encode("utf-8") + c)
    print("Level Factory 0.144.3: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
