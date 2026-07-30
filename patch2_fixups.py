"""Two fixups: my broken patch script, and a test I invalidated without updating.

1. `patch_run_summary2.py` died with KeyError: '_jid'. I built the inserted code
   with str.format() while it contained f-string braces -- {_jid}, {} and a
   getattr call -- so format() tried to substitute them. Escaping some braces
   and not others is exactly the kind of half-done thing that looks fine. This
   uses token replacement instead, which cannot interpret the payload at all.

2. `test_a_route_never_walked_on_a_full_clock_blocks` asserts the behaviour
   0.20.0 deliberately changed. I patched `lasertag_report.py` through a script
   and never asked what covered it. The test was right about the old contract;
   it needs to be right about the new one, and to carry the reason.
"""
import pathlib
import py_compile

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
CMDS = ROOT / "level_factory" / "apps" / "cli" / "commands" / "__init__.py"
TEST = ROOT / "level_factory" / "tests" / "unit" / "test_lasertag_readiness.py"

# ---------------------------------------------------------------- 1. the CLI
OLD_LINE = 'print(f"    - {_jid}")'

BLOCK = """print(f"    - {_jid}: "
@DEEP@      f"{getattr(summary, 'not_run_reason', {}).get(_jid, '')}")
@BASE@dropped = getattr(summary, "eliminated_candidates", {}) or {}
@BASE@if dropped:
@BASE@    # Not a failure line. Five candidates are generated so the weak
@BASE@    # ones can be dropped, and until the scheduler learned to scope a
@BASE@    # failure, one bad candidate halted the run and took the good ones
@BASE@    # with it.
@BASE@    print(f"  {len(dropped)} candidate(s) eliminated (the rest carried on):")
@BASE@    for _cid, _at in sorted(dropped.items()):
@BASE@        print(f"    - {_cid}  at {_at}")"""


def patch_cli() -> str:
    text = CMDS.read_text(encoding="utf-8")
    if "eliminated_candidates" in text:
        return "cli: already patched"
    if text.count(OLD_LINE) != 1:
        raise SystemExit(f"cli: expected one {OLD_LINE!r}, found "
                         f"{text.count(OLD_LINE)}. Nothing written.")
    n = text.index(OLD_LINE)
    deep = text[text.rfind("\n", 0, n) + 1:n]          # indent of the print
    base = deep[:-8] if len(deep) >= 8 else ""          # indent of `if skipped:`
    block = BLOCK.replace("@DEEP@", deep).replace("@BASE@", base)
    CMDS.write_text(text[:n] + block + text[n + len(OLD_LINE):], encoding="utf-8")
    py_compile.compile(str(CMDS), doraise=True)
    return f"cli: patched and compiles ({CMDS.name})"


# --------------------------------------------------------------- 2. the test
OLD_NAME = "def test_a_route_never_walked_on_a_full_clock_blocks(tmp_path):"
NEW_TEST = '''def test_a_route_never_walked_on_a_full_clock_reports_but_does_not_block(tmp_path):
    """This blocked until Level Factory 0.20.0, and the reasoning was sound when
    it was written: five seeds, 125 matches, route completion 0.0 in every one,
    and the build printing "56 finding(s) -- none blocking". Four of seed 5320's
    runs went the full 180 s with the crew alive and still never reached the
    objective, and that is a measurement rather than a score.

    What changed is that walktest_navqa now measures the same claim directly, on
    every candidate, with no combat in it -- while this number is confounded by
    everything combat does. That same seed 5320 report carries 835 player-stuck
    events and six team wipes alongside the timeouts.

    And the ordering settled it. The scheduler fail-fasts on the first blocked
    job, so while this blocked, seed 5320's own walktest never dispatched: the
    firefight silenced the instrument built to replace it, and the stale report
    left in its place read as a passing geometry check for an evening.

    So it reports, it points at the walktest, and it leaves the verdict there.
    """
    issues = LaserTagAdapter().normalize_validation([_real_report(tmp_path)])
    found = next(i for i in issues if i["code"] == "LT_ROUTE_NEVER_COMPLETED")
    assert found["blocking"] is False
    assert found["severity"] == "major"
    # The category does NOT change: it is still a statement about reachability,
    # and filing it under readiness would lose that.
    assert found["category"] == "reachability"
    assert "4 of those ran the full clock" in found["message"]
    # It has to name the instrument that does own the verdict, or the reader is
    # left with a demoted finding and nowhere to go.
    assert "walktest_navqa" in found["message"]
    # And it still must not be mistakable for the score it sits beside.
    assert "not a difficulty score" in found["message"]
'''


def patch_test() -> str:
    text = TEST.read_text(encoding="utf-8")
    if "reports_but_does_not_block" in text:
        return "test: already patched"
    if OLD_NAME not in text:
        raise SystemExit("test: the old test signature is not there. Nothing "
                         "written -- read the file and re-aim.")
    start = text.index(OLD_NAME)
    nxt = text.find("\ndef ", start + 1)
    if nxt == -1:
        raise SystemExit("test: could not find the end of the old test.")
    TEST.write_text(text[:start] + NEW_TEST + text[nxt + 1:], encoding="utf-8")
    py_compile.compile(str(TEST), doraise=True)
    return f"test: rewritten and compiles ({TEST.name})"


if __name__ == "__main__":
    print(patch_cli())
    print(patch_test())
