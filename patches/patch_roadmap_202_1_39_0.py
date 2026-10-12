"""Roadmap 202: install test 8 and factory 1.39.0. Replaces 202's status block (asserted once) and
appends one body paragraph at the end of 202's body (before the next item's status block). The
index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_202_1_39_0.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = ("*STATUS: NARROWED 2026-10-11 -- the path a stranger follows is certified a third time, with no "
                   "deviation from the page and no finding: install test 7")
STATUS_NEW = (
    "*STATUS: NARROWED 2026-10-12 -- the path a stranger follows is certified a fourth time, with no "
    "deviation from the page and no finding: install test 8, at the set factory 1.39.0 certifies "
    "(Deli Counter 0.209.1, Laser Tag 0.27.0, Level Factory 0.193.1, Lot 0.117.0, Zoo 1.103.0, the "
    "other five as 1.38.0), exited 0 on `setup` (every doctor row PASS at this set's versions, 0 `drift "
    "vs certified` lines, the three pins from pip's cache), `make` (7.9 minutes where test 7's took "
    "34.1 -- roadmap 239's cuts on the stranger's own path; the level tests 3 to 7 built, three roofs "
    "dressed, baked on the bake's first attempt, the closure clean) and `walk` (5.6 minutes against "
    "10.9, both ladders climbed, all five stations, the package still baked after it), the fixture "
    "layers as test 7's. Its two findings over test 7 are an unpicked candidate's, Laser Tag 0.26.0's "
    "enemy body on a scene the same byte for byte -- measured, not the speed cut "
    "(`docs/findings/grader_speed/body_or_clock_ab.sh`). `verify-manifest` all ten OK; tags `v0.209.1`, "
    "`v0.27.0`, `v0.193.1`, `v0.117.0`, `v1.103.0` and `factory-v1.39.0`. Left: a Linux run -- the "
    "walker has no Linux machine (2026-10-11), so `factory.sh` and START_HERE.md's Linux lines are "
    "written and unproven.*")

BODY_ADD = """

**INSTALL TEST 8, 2026-10-12** (`docs/findings/stranger_install/`, `install_test_8/`). The 1.39.0 set -- five tools moved since test 7, most of them roadmap 239's cold-run speed work (Laser Tag 0.27.0, Lot 0.117.0, Level Factory 0.179.1 to 0.193.1), beside an enemy that is the agent contract's body (Laser Tag 0.26.0), dressed roofs (Level Factory 0.179.0, Zoo 1.101.0 and 1.102.0, Deli Counter 0.209.0 and 0.209.1) and every mesh's faces in one order (Zoo 1.103.0) -- packaged at its heads, unpacked into a folder that had never held a factory, and typed with the page's own `setup --venv`: no deviation, no finding. What it adds to what a stranger is promised is time: `make` 34.1 -> 7.9 minutes and `walk` 10.9 -> 5.6 on the same level and machine, the first measurement of roadmap 239 on the path a stranger types rather than the factory's own drive. Every count that moved against test 7 is attributed in the record: the three roof-props layers (+3 lightmapped models), Level Factory 0.187.0's merge of the Empties (236 -> 148 meshes, the users and files with it), and two findings on seed_9205, which was not picked -- Laser Tag reads its crew dying in 7.0 s where test 7's read 75.7, on a scene the same byte for byte, and `docs/findings/grader_speed/body_or_clock_ab.sh` puts that on 0.26.0's enemy body and not on 0.27.0's clock: the old body under the new clock reads test 7's report in every field. A certification that counts what moved, not only what exited 0, is what found it; nothing in the gates' verdicts would have."""


def main():
    status_new = STATUS_NEW
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    i = text.find(STATUS_OLD_HEAD)
    assert i >= 0 and text.count(STATUS_OLD_HEAD) == 1, "202's status block not found once"
    j = text.find("\n", i)
    old_status = text[i:j]
    assert old_status.endswith("*") and old_status.count("*STATUS:") == 1, old_status[-80:]
    assert "INSTALL TEST 8, 2026-10-12" not in text, "already applied"
    text = text[:i] + status_new + text[j:]
    h = text.find("\n\n**202. Handing the factory to a stranger.**")
    assert h > 0 and text.count("\n\n**202. Handing the factory to a stranger.**") == 1
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h, "no status block after 202's body"
    text = text[:nxt] + BODY_ADD + text[nxt:]
    assert "\n\n**202. " in text[text.find(status_new):text.find(status_new) + len(status_new) + 40]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 202: status replaced, one paragraph appended; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
