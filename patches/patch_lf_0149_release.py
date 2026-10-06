"""Level Factory 0.149.0: VERSION and CHANGELOG for
`patch_lf_presentation_every_building_tests.py` and
`patch_lf_presentation_every_building.py`.

    python patch_lf_0149_release.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

ENTRY = '''## [0.149.0] - Every placed building's package is read, and the circulation gate reaches a finding

Found while cold run 9187 ran, checking roadmap 177 against the runs since
(`docs/findings/presentation_gates/` at the factory root).

**One manifest read of sixteen.** A varied lot composes one package a
building under `presentation/lot/<id>/`.
- `normalize_validation` read `next(...)` of the sorted manifests, which is
  the first building's.
- In 9187 three of fifteen buildings failed z-fight: deli_a01 203 pairs,
  office 121, rail_station_a02 117. One finding was recorded, deli_a01's.
- `_placed_manifests` reads each `lot/<id>` package. With no lot it reads the
  root, exactly as before.
- A varied lot's root is the mission's own shell, composed for the output
  contract and not placed. Its dangling refs would block a level that does
  not contain it.
- Every finding now names its building, in `location` and at the head of its
  message.

**The circulation gate reaches a finding.** Nothing read `circulation_check`,
and every cold run from 9164 to 9187 failed it on every building.
- `PRESENTATION_CIRCULATION` is one finding an arm that failed (shell or
  dressing), naming the props and how far each intrudes.
- It is born moderate and advisory, as a new gate is here.
- Deli Counter 0.191.0 makes the gate honest. On 9187's fifteen buildings it
  then names one thing: deli_a01's counter island over its stairwell.
- An unreadable manifest is said (`PRESENTATION_MANIFEST_UNREADABLE`). It
  used to return quietly and take every finding about its package with it.

**The driver prints the gate from its arms.** Deli Counter writes
`{"ok", "shell", "dressing"}`. `run_presentation_compose.py` printed the
counts from the top of it, "0 prop conflict(s) across ? circulation
volume(s)" on every building: a red with nothing in it.
- `circulation_gate` prints each arm's conflicts, volumes, and what it
  excused.
- The error line no longer says "dressing" when the shell arm failed.

**Measured on 9187's composed outputs** (manifests written by Deli Counter
0.190.0):
- 3 z-fight findings, one a failing building.
- 17 circulation findings: 15 merged-cover dressing arms and 2 shell arms.
  The next run's recompose under 0.191.0 should leave one.

**Tests:** 10.
- `test_presentation_gates_are_reported.py`, 7:
  - every placed building is read;
  - an unplaced mission shell is not read in a lot, and a single shell
    reads its root;
  - a failing arm is a finding, a passing check says nothing, and a gate
    that did not run is said;
  - an unreadable manifest is said.
- `test_circulation_gate_reads_its_arms.py`, 3.
- Seven fail on 0.148.0. The three that pass do so by design; one of them,
  the unplaced root, passed only because the sort put a lot building first.

**Suite:** 1,979 collected: 1,964 passed, 14 skipped, 1 xfail. That is
0.148.0's 1,968 collected and these 10, and one more case of
`test_sibling_locator.py`, which is parametrized over the repo's files and
counts the new test file (294 -> 295, measured on 0.148.0's code today).

'''


def main():
    v = LF / "VERSION"
    assert v.read_bytes() == b"0.148.0", v.read_bytes()
    cl = LF / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## [0.148.0] - One business a shell"), text[:60]
    cl.write_bytes((ENTRY + text).encode("utf-8"))
    v.write_bytes(b"0.149.0")
    print("Level Factory 0.149.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
