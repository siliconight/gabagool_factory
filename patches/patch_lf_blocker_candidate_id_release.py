"""Level Factory 0.144.1: VERSION and the CHANGELOG entry for
`patch_lf_blocker_candidate_id.py`, written after the failing test and the
suite were measured.

    python patch_lf_blocker_candidate_id_release.py
"""
import pathlib

LF = pathlib.Path(__file__).resolve().parent.parent / "level_factory"

ENTRY = '''## [0.144.1] - The export reads a blocker's candidate from its own `candidate_id`

**Cold run 9170 (card_block_001, the breadth sweep) could not export.**
- Its shell and art legs printed "blockers open: 0". The export then
  refused over `LT_NOT_EVALUATED` on seed_9061, a candidate nobody chose;
  the driver had picked seed_9263.
- Laser Tag had refused seed_9061's map in 2 s (`UNREACHABLE_SPAWN: Enemy_5
  could not path to the player spawn`). That is a bad candidate, which is
  what three candidates are for.
- The refusal was the defect. The finding, verbatim from the run's
  validation file:

      {"blocking": true, "candidate_id": "card_block_001.candidate.seed_9061",
       "code": "LT_NOT_EVALUATED", "location": "", ...}

**Two queries of one question again, as at cold run 9074.**
- `cmd_run`'s `aggregate` reads the finding's `candidate_id`, and discounted
  it as belonging to a candidate that was not chosen.
- `_open_blockers` (`apps/cli/commands/__init__.py`) read the candidate only
  from `location`, falling back to the stage id. It found none and failed
  safe, as its docstring says it must when it cannot tell.
- The 9074 fix taught it to compare candidates. It never learned that a
  finding can name its candidate in a field rather than in a location.

**The fix.** The candidate is now the finding's `candidate_id` first, then
its location. Every fail-safe case still blocks: no selection recorded, or a
blocker naming no candidate anywhere.

**Tests** (`test_export_blockers_candidate_aware.py`).
- 9170's shape on an unselected candidate is discounted. It fails on 0.144.0.
- The same blocker on the selected candidate still refuses.

**Suite:** 1,923 collected: 1,908 passed, 14 skipped, 1 xfail.

'''


def main():
    version = LF / "VERSION"
    changelog = LF / "CHANGELOG.md"
    v = version.read_bytes()
    assert v == b"0.144.0", v
    c = changelog.read_bytes()
    assert b"\r\n" not in c
    assert c.startswith(b"## [0.144.0] - "), c[:60]
    version.write_bytes(b"0.144.1")
    changelog.write_bytes(ENTRY.encode("utf-8") + c)
    print("Level Factory 0.144.1: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
