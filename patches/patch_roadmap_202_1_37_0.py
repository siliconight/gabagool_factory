"""Roadmap 202: install tests 4 to 6 and factory 1.37.0. Replaces 202's status block (asserted
once) and appends one body paragraph at the end of 202's body (before the next item's status
block). The index is NOT touched here: run `python tools/roadmap_status.py --write` then
`--check` after it.

    python patches/patch_roadmap_202_1_37_0.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = ("*STATUS: NARROWED 2026-10-10 -- a stranger's path exists, is certified, and has been "
                   "followed three times from a fresh unpack")
STATUS_NEW = (
    "*STATUS: NARROWED 2026-10-11 -- the path a stranger follows is certified again, now with the "
    "page's own `setup --venv` and its download (the walker's yes, 2026-10-11) and no deviation from "
    "the page: install test 6, at the set factory 1.37.0 certifies (Deli Counter 0.207.1, Level "
    "Factory 0.178.3, Lot 0.115.0, Lux 0.74.0, Zoo 1.97.0, the other five as 1.36.0), exited 0 on "
    "`setup` (every doctor row PASS, `worst: PASS`, the first time), `make` (32.3 minutes, the level "
    "install tests 3 to 5 built, baked, the closure clean) and `walk` (all five stations, and the "
    "package still baked after it). Three defects a stranger would have met, found by install tests "
    "4 and 5 and fixed in Level Factory: Blender's sitecustomize printing an error at every step from "
    "inside the venv (0.178.1); `walk` replacing the package `make` baked with an unbaked one, as "
    "every walk since 0.144.0 had (0.178.3); and the walk's shot bot failing a level for a failing "
    "tube's flicker (0.178.3). `verify-manifest` all ten OK; tags `v0.207.1`, `v0.178.3`, `v0.115.0`, "
    "`v0.74.0`, `v1.97.0` and `factory-v1.37.0`. Left: a Linux run -- the walker has no Linux machine "
    "(2026-10-11), so `factory.sh` and START_HERE.md's Linux lines are written and unproven.*")

BODY_ADD = """

**INSTALL TESTS 4 TO 6, 2026-10-11** (`docs/findings/stranger_install/`, `install_test_4/` to `install_test_6/`). The walker said yes to the PyPI download, and the tests typed the page's own `setup --venv` for the first time. **Test 4**, the released 1.36.0 zip: `setup`, `make` and `walk` all exited 0, and every tool the venv started printed `Error in sitecustomize ... blender.shared` -- twelve times on the way to one first level. Blender's own `sitecustomize.py`, seen through `--system-site-packages`, adds a DLL directory three folders above `sys.executable`, which inside a venv names a folder that is not there. Level Factory 0.178.1 writes the venv its own, doing what Blender's does from Blender's folder (a test on Blender's real Python, with the control). **Test 5**, the 1.37.0 set at Level Factory 0.178.2 (re-grounded to it, the real-tool smoke failing on exactly the four rows before and passing after): `setup` with every doctor row PASS and no error, `make` baked -- and `walk` exited 1, with two findings. The shot bot failed `Ladder_ladder_0_base` at 1.39% fighting that read 1.27% with the camera NOT moved, twice: a failing tube's flicker (Lux 0.74.0 puts one in a room), not depth; the depth left over was 0.12%, test 4's figure. And Level Factory 0.178.0's new note under an unbaked export printed in the walk's output, which led to the code: `walk` re-exported with the walk's own arguments, which carried no bake, into the folder `make` had shipped to, so the stranger's package after `walk` held 2,526 files with no `bake.exr` where `make` had left 3,008 and a bake -- every walk since 0.144.0, in every install test, silently. Level Factory 0.178.3 hands the walk the export's own bake default and gives the shot bot two still frames bracketing the moved one, judging only the pixels they agree on (proven on test 5's preview, all five stations passing, and on the bot's own two-quad control, still failing at 2.02%). **Test 6** certified the set (above), the package baked after the walk at 3,014 files. What the three have in common: none failed a step's exit code before it was looked for, and two were found by an instrument written for something else -- a note saying what a step did, and a control with the camera still."""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    i = text.find(STATUS_OLD_HEAD)
    assert i >= 0 and text.count(STATUS_OLD_HEAD) == 1, "202's status block not found once"
    j = text.find("\n", i)
    old_status = text[i:j]
    assert old_status.endswith("*") and old_status.count("*STATUS:") == 1, old_status[-80:]
    assert "INSTALL TESTS 4 TO 6" not in text, "already applied"
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
