"""Roadmap 227 CLOSED: Level Factory 0.173.0 reads the long-paths flag and weighs the workspace's depth.

Replaces 227's status block. The anchor must match exactly once; nothing is written on a miss.
The generated index is regenerated afterwards by `tools/roadmap_status.py --write`.

    python patches/patch_roadmap_227_closed.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS = (
    "*STATUS: OPEN 2026-10-10 -- measured, and the fix drafted: Level Factory 0.173.0 "
    "(`patches/patch_lf_long_paths.py`, 9 tests failing on 0.172.1) reads the flag, weighs the "
    "workspace's depth against the 217 a level writes, and PASSes where either is fine. Applied "
    "after factory 1.36.0's tags, not before: it would have moved the set the install test "
    "certified.*\n"
)
NEW_STATUS = (
    "*STATUS: CLOSED 2026-10-10 -- Level Factory 0.173.0 (`patches/patch_lf_long_paths.py`): the "
    "row reads `LongPathsEnabled` and weighs the workspace's path against the 217 characters a "
    "level writes below it; PASS with the flag on, PASS within 260 naming the reach, WARN past it "
    "naming the reach, the 42-character budget and the two remedies; `setup` weighs "
    "`<factory>\\levels`, `doctor` its own. 9 tests, all failing on 0.172.1; suite 2,163 passed. "
    "Applied after factory 1.36.0's tags, so the certified set is not the one carrying it. Left "
    "in the body, not closed by this: what actually fails with the flag off, unmeasured because "
    "this machine's flag is 1.*\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    assert text.count(OLD_STATUS) == 1, text.count(OLD_STATUS)
    text = text.replace(OLD_STATUS, NEW_STATUS)
    i = text.index(NEW_STATUS)
    assert text[i + len(NEW_STATUS):].startswith("\n**227. "), "227's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 227: CLOSED by Level Factory 0.173.0")


if __name__ == "__main__":
    main()
