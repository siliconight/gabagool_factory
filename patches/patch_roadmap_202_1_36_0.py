"""Roadmap 202: install test 3 certifies factory 1.36.0; the long-paths WARN becomes item 227.

Replaces 202's status block and adds the test's and certification's record to its body. Each
anchor must match exactly once; nothing is written on a miss. The generated index is regenerated
afterwards by `tools/roadmap_status.py --write`, never by this script.

    python patches/patch_roadmap_202_1_36_0.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS = (
    "*STATUS: NARROWED 2026-10-10 -- a stranger's path exists, is certified, and has been followed "
    "twice from a fresh unpack (`docs/findings/stranger_install/`). Install test 2, at Level Factory "
    "0.171.0, built cold run 9222's level again figure for figure with every tool passing the "
    "doctor, the player at the package's player_start and every hint naming `.\\factory`; factory "
    "1.35.0 certifies exactly that set (`verify-manifest` all ten OK, every repo tagged). Left: the "
    "real `setup --venv` (a download, the walker's yes), a Linux run, and an install test at Level "
    "Factory 0.172.0, whose walk no longer fails on texture sparkle (roadmap 225).*\n"
)
NEW_STATUS = (
    "*STATUS: NARROWED 2026-10-10 -- a stranger's path exists, is certified, and has been followed "
    "three times from a fresh unpack (`docs/findings/stranger_install/`). Install test 3, at Level "
    "Factory 0.172.1 and Lot 0.106.0, built cold run 9223's level figure for figure: `setup` 0 with "
    "every tool PASS, `make` 0 in 32.1 minutes, `walk` 0 with all five stations passing the visual "
    "check and the two sparkling ones named as sparkle; factory 1.36.0 certifies exactly that set "
    "(`verify-manifest` all ten OK, Level Factory and Lot tagged, the factory at "
    "`factory-v1.36.0`). The one WARN left on a stranger's first `setup` is the doctor's "
    "long-paths row, item 227. Left: the real `setup --venv` (a download, the walker's yes) and a "
    "Linux run.*\n"
)
BODY_ANCHOR = (
    "It is certified by the install test rather than by `docs/CERTIFY.md`'s legs, which were "
    "written when Zoo was 0.3x.\n"
)
ADDED = (
    "\n**A SECOND LOOK AT 9223'S DOCTOR, before install test 3.** Its notes named one WARN, "
    "Windows' long-paths reminder. There were two: `tool:lot vLot 0.106.0 ... drift vs certified "
    "0.105.0 (grounded); re-certify`, the advice 0.170.0 had taken off a stranger's screen, back "
    "for the one tool that had moved since. A first attempt at the test was stopped at its unpack "
    "on finding it. Level Factory 0.172.1 re-grounds the row (the real-tool smoke 11 of 12, exit "
    "0, `test_grounded_table` failing on that row alone before), `install_test.sh` now prints every "
    "doctor row that is not PASS, and 9223's notes are corrected.\n"
    "\n"
    "**INSTALL TEST 3** (`docs/findings/stranger_install/install_test_3/`), at Level Factory "
    "0.172.1 and Lot 0.106.0, packaged, unpacked into `C:\\stranger_202_3\\gabagool` and typed the "
    "same way: `setup` 0 with every tool PASS and one WARN, the long-paths row; `make` 0 in 32.1 "
    "minutes, 9223's level (0 of 52 and 0 of 74 blockers, seed_9104, the same deal, 479 models and "
    "4,259 users); `walk` 0, the player at the van, both ladders climbed, five stations OK at "
    "0.00% to 0.12% fighting with the two ladder stations' sparkle (3.61% and 2.35%) noted. One "
    "deviation, counted, as before: `setup --python` for `--venv`.\n"
    "\n"
    "**CERTIFIED, factory 1.36.0** (`patches/patch_factory_manifest_1_36_0.py`): Level Factory "
    "0.171.0 to 0.172.1 and Lot 0.105.0 to 0.106.0, the other eight as 1.35.0; `verify-manifest` "
    "all ten OK; tags `v0.172.1`, `v0.106.0` and `factory-v1.36.0`.\n"
    "\n"
    "**THE WARN THAT IS LEFT is the doctor's own** (`docs/findings/long_paths/`): "
    "`windows_long_paths` is printed on every Windows machine without reading the flag, and the "
    "depth it warns about is real, 217 characters below a workspace, 440 and 725 files past 260 on "
    "9223's and 9222's. Item 227.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    assert text.count(OLD_STATUS) == 1, text.count(OLD_STATUS)
    assert text.count(BODY_ANCHOR) == 1, text.count(BODY_ANCHOR)
    text = text.replace(BODY_ANCHOR, BODY_ANCHOR + ADDED)
    text = text.replace(OLD_STATUS, NEW_STATUS)
    i = text.index(NEW_STATUS)
    assert text[i + len(NEW_STATUS):].startswith("\n**202. "), "202's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 202: install test 3, factory 1.36.0, the long-paths WARN to 227")


if __name__ == "__main__":
    main()
