"""Roadmap 202: install test 2, and factory 1.35.0 certified from it.

Replaces 202's status block and adds install test 2 after install test 1 in its body. Each anchor
must match exactly once; nothing is written on a miss. The generated index is regenerated
afterwards by `tools/roadmap_status.py --write`, never by this script.

    python patches/patch_roadmap_202_certified.py
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

OLD_STATUS_START = "*STATUS: NARROWED 2026-10-10 -- a stranger's path exists, and its first install test"
NEW_STATUS = (
    "*STATUS: NARROWED 2026-10-10 -- a stranger's path exists, is certified, and has been "
    "followed twice from a fresh unpack (`docs/findings/stranger_install/`). Install test 2, "
    "at Level Factory 0.171.0, built cold run 9222's level again figure for figure with every "
    "tool passing the doctor, the player at the package's player_start and every hint naming "
    "`.\\factory`; factory 1.35.0 certifies exactly that set (`verify-manifest` all ten OK, "
    "every repo tagged). Left: the real `setup --venv` (a download, the walker's yes), a Linux "
    "run, and an install test at Level Factory 0.172.0, whose walk no longer fails on texture "
    "sparkle (roadmap 225).*\n"
)
BODY_ANCHOR_START = "**INSTALL TEST 1** (`docs/findings/stranger_install/install_test_1/`)."
TEST_2 = (
    "\n**INSTALL TEST 2** (`docs/findings/stranger_install/install_test_2/`), at Level Factory "
    "0.171.0, packaged, unpacked into `C:\\stranger_202b\\gabagool` and typed the same way: "
    "`setup` 0 with every tool PASS (they were eight WARNs) and `.\\factory` in its next step; "
    "`make` 0 in 31.5 minutes, 9222's level again (0 of 52 and 0 of 74 blockers, seed_9104, the "
    "same deal, 479 models and 4,259 users); `walk` 1 -- the player at the getaway van's "
    "player_start, the review frames carrying a picture, and two ladder stations failing on "
    "texture sparkle, which Level Factory 0.172.0 (after the test) notes instead. One "
    "deviation, counted, as before: `setup --python` for `--venv`.\n"
    "\n"
    "**CERTIFIED, factory 1.35.0** (`patches/patch_factory_manifest_1_35_0.py`): the manifest "
    "names the set install test 2 ran -- Deli Counter 0.205.0, Dispatch 0.5.2, Laser Tag 0.25.0, "
    "Level Factory 0.171.0, Lot 0.105.0, Lux 0.72.0, Patina 0.30.0, Pipeline 0.6.0, Pixelcoat "
    "0.62.0, Zoo 1.94.0 -- and `verify-manifest` reads all ten OK (that morning: eight DRIFT, "
    "one INCOMPATIBLE). Every repo is tagged at the commit tested, the factory at "
    "`factory-v1.35.0`. It is certified by the install test rather than by "
    "`docs/CERTIFY.md`'s legs, which were written when Zoo was 0.3x.\n"
)


def main():
    raw = ROADMAP.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF; a CRLF means something changed it"
    text = raw.decode("utf-8")
    assert text.count(OLD_STATUS_START) == 1, text.count(OLD_STATUS_START)
    s = text.index(OLD_STATUS_START)
    e = text.index("*\n", s) + 2
    old_status = text[s:e]
    assert text[e:].startswith("\n**202. "), "202's status is not where it should be"
    text = text[:s] + NEW_STATUS + text[e:]
    assert text.count(BODY_ANCHOR_START) == 1
    b = text.index(BODY_ANCHOR_START)
    pe = text.index("\n", b) + 1          # the end of install test 1's paragraph
    text = text[:pe] + TEST_2 + text[pe:]
    i = text.index(NEW_STATUS)
    assert text[i + len(NEW_STATUS):].startswith("\n**202. "), "202's status left its heading"
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 202: certified 1.35.0; replaced a status of", len(old_status), "chars")


if __name__ == "__main__":
    main()
