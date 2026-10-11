"""Roadmap 202: install test 7 and factory 1.38.0. Replaces 202's status block (asserted once) and
appends one body paragraph at the end of 202's body (before the next item's status block). The
index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_202_1_38_0.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = ("*STATUS: NARROWED 2026-10-11 -- the path a stranger follows is certified again, now with "
                   "the page's own `setup --venv` and its download")
STATUS_NEW = (
    "*STATUS: NARROWED 2026-10-11 -- the path a stranger follows is certified a third time, with no "
    "deviation from the page and no finding: install test 7, at the set factory 1.38.0 certifies "
    "(Deli Counter 0.208.0, Level Factory 0.178.6, Lot 0.116.0, Lux 0.75.0, Zoo 1.100.0, the other "
    "five as 1.36.0), exited 0 on `setup` (every doctor row PASS at this set's versions, 0 `drift vs "
    "certified` lines, the three pins from pip's cache), `make` (34.1 minutes, the level tests 3 to 6 "
    "built, baked on the bake's first attempt, the closure clean) and `walk` (10.9 minutes, both "
    "ladders climbed, all five stations, the package still baked after it) -- and the package's "
    "fixture layers carry Zoo 1.100.0's merge, the deli's 23 pendants 23 metal meshes. "
    "`verify-manifest` all ten OK; tags `v0.208.0`, `v0.178.6`, `v0.116.0`, `v0.75.0`, `v1.100.0` and "
    "`factory-v1.38.0`. Left: a Linux run -- the walker has no Linux machine (2026-10-11), so "
    "`factory.sh` and START_HERE.md's Linux lines are written and unproven.*")

BODY_ADD = """

**INSTALL TEST 7, 2026-10-11** (`docs/findings/stranger_install/`, `install_test_7/`). The 1.38.0 set -- five tools moved since test 6: a home's rooms hang a dome (Deli Counter 0.208.0, Zoo 1.98.x, Lux 0.75.0), a service lane lights its own length (Lot 0.116.0), a fixture's same-material parts are one mesh (Zoo 1.100.0), and the light bake keeps its editor awake and tries a failed bake once more (Level Factory 0.178.5, 0.178.6) -- packaged at its heads, unpacked into a folder that had never held a factory, and typed with the page's own `setup --venv`: no deviation, no finding. What the instrument counts now that it did not: the doctor's `drift vs certified` lines at setup (0.178.4's re-grounding, claimed 0 and read 0) and the package's fixture layers after the walk (1.100.0's merge, claimed one metal mesh a pendant and read 23 for the deli's 23, where 1.97.0 shipped 46) -- a certification that counts what each moved tool claimed in the package a stranger receives, where tests 3 to 6 counted exit codes and stations. The bake took its first attempt (127.7 s, 3,780 users), so 0.178.5 and 0.178.6 were carried and not exercised. `make` ran 34.1 minutes against test 6's 32.3, beside three test suites and three repository clones this machine ran at the same time."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    i = text.find(STATUS_OLD_HEAD)
    assert i >= 0 and text.count(STATUS_OLD_HEAD) == 1, "202's status block not found once"
    j = text.find("\n", i)
    old_status = text[i:j]
    assert old_status.endswith("*") and old_status.count("*STATUS:") == 1, old_status[-80:]
    assert "INSTALL TEST 7, 2026-10-11" not in text, "already applied"
    text = text[:i] + STATUS_NEW + text[j:]
    h = text.find("\n\n**202. Handing the factory to a stranger.**")
    assert h > 0 and text.count("\n\n**202. Handing the factory to a stranger.**") == 1
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h, "no status block after 202's body"
    text = text[:nxt] + BODY_ADD + text[nxt:]
    assert "\n\n**202. " in text[text.find(STATUS_NEW):text.find(STATUS_NEW) + len(STATUS_NEW) + 40]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 202: status replaced, one paragraph appended; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
