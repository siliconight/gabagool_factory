"""Roadmap 202: install test 9 and factory 1.40.0; and item 256, the venv's unpinned dependencies, which
test 9 found. Copied from `patch_roadmap_202_1_39_0.py`: replaces 202's status block (asserted once),
appends one body paragraph at the end of 202's body (before the next item's status block), and appends
item 256 after the last item (255, the file's last line). The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_202_1_40_0.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = ("*STATUS: NARROWED 2026-10-12 -- the path a stranger follows is certified a fourth time, with no "
                   "deviation from the page and no finding: install test 8")
STATUS_NEW = (
    "*STATUS: NARROWED 2026-10-14 -- the path a stranger follows is certified a fifth time, with no deviation "
    "from the page: install test 9, at the set factory 1.40.0 certifies (Deli Counter 0.222.0, Laser Tag 0.32.0, "
    "Level Factory 0.211.1, Lot 0.123.0, Lux 0.77.0, Patina 0.31.0, Zoo 1.112.0, the other three as 1.39.0), "
    "exited 0 on `setup` (every doctor row PASS at this set's versions, 0 `drift vs certified` lines, the three "
    "pins from pip's cache), `make` (7.9 minutes, as test 8's; 0 of 78 and 0 of 110 blockers; seed_9003 picked "
    "where tests 3 to 8 picked seed_9104, Level Factory 0.202.0's tie going to the lower seed; three roofs "
    "dressed, baked on the bake's first attempt, the closure clean) and `walk` (5.2 minutes against 5.6, the "
    "site's four ladders climbed, all nine stations, the package still baked after it). Every finding that "
    "moved against test 8 is attributed, Laser Tag's by a two-by-two of scene and grader on both unpicked seeds "
    "(`docs/findings/stranger_install/lt_share_ab.sh`, every control reading its own job in every field). Its "
    "one finding is the venv's: it pins its three packages and not the nine they bring, and pip downloaded "
    "wrapt 2.5.1 where test 8 took 2.5.0 (item 256). `verify-manifest --strict` all ten OK; tags `v0.222.0`, "
    "`v0.32.0`, `v0.211.1`, `v0.123.0`, `v0.77.0`, `v0.31.0`, `v1.112.0` and `factory-v1.40.0`. Left: a Linux "
    "run -- the walker has no Linux machine (2026-10-11), so `factory.sh` and START_HERE.md's Linux lines are "
    "written and unproven -- and item 256.*"
)

BODY_ADD = """

**INSTALL TEST 9, 2026-10-14** (`docs/findings/stranger_install/`, `install_test_9/`). The 1.40.0 set -- seven tools moved since test 8, most of it the walker's streets: the urban street (item 241), Philadelphia's poles, stoops and drains (240, 179), every walkable door at the contract's width (197), Laser Tag's bots keeping to the mesh and arriving at the point (242, 246), the sun baked and a package carrying only what its scene stands, the same bytes from two runs (247), a pick's tie broken on the grade (245), and the walker's walk of 2026-10-14 (250) -- packaged at its heads, unpacked into a folder that had never held a factory, and typed with the page's own `setup --venv`: no deviation from the page. The level is another candidate's. Level Factory 0.202.0 no longer counts LOT_DESTINATION_ABOVE_FLOOR where the walk test walked every leg, which ties seed_9003 with seed_9104 at 0 majors, route completion 1.00 and PASS 90 and gives the tie to the lower seed, so this is the first install test to build seed_9003 -- the move 0.202.0's census named. What moved against test 8 is attributed in the record: the export's 32 findings are the picked candidate's and moved with the pick, Lot's 61 are test 8's candidate by candidate, and Laser Tag's 20 -> 17 are unpicked candidates', split by a two-by-two of scene and grader (`lt_share_ab.sh`): seed_9104's player-stuck warning went with the grader, seed_9205's enemy-stuck and instant-contact warnings went and an overexposed one came with the scene, and seed_9205's player-stuck warning needed both. The two-by-two's first run had no import pass and its swapped arm read BROKEN -- the instrument failing, not a reading, kept in the script's header. Its one finding is not the tools': the venv's nine unpinned packages, wrapt 2.5.0 -> 2.5.1 in two days (item 256)."""

LAST_ITEM_HEAD = "**255. A partition that stops short of where its rooms meet.**"
ITEM_256 = """
*STATUS: OPEN 2026-10-14 -- FOUND BY INSTALL TEST 9: the venv pins three packages and not the nine they bring. Two days apart, one package installed wrapt 2.5.0 (test 8, from pip's cache) and wrapt 2.5.1 (test 9, downloaded). Proposed: pin all twelve. Level Factory's.*

**256. The venv pins three packages, not the nine they bring.** Found by install test 9 (`docs/findings/stranger_install/README.md`, "Install test 9"; `install_test_9/setup.txt`). Level Factory's `setup --venv` runs `pip install pillow==12.3.0 pygltflib==1.16.5 jsonschema==4.26.0` (`packages/tools/interpreter.py`, `PINNED`, whose comment gives the reason for a pin: a different Pillow is a different PNG encoder and resampler). pip resolves what those three require from whatever PyPI holds that day: dataclasses-json, deprecated, jsonschema-specifications, marshmallow, mypy-extensions, referencing, rpds-py, typing-inspect and wrapt. Three more, attrs, packaging and typing-extensions, come from Blender's own site-packages through `--system-site-packages` and move with Blender. **Measured:** install test 8 (2026-10-12) took wrapt 2.5.0 from pip's cache; install test 9 (2026-10-14), the same three pins, downloaded wrapt 2.5.1 (pygltflib's `deprecated` asks `wrapt<3,>=1.16`); the other eight resolved to test 8's versions. Not measured: whether anything the factory makes differs with it. **Why it matters:** the package is what a stranger is handed, and a certified set certifies an environment it does not fix -- a dependency's broken release would break a stranger's `setup` with nothing in the factory changed, and the doctor would not say why. **Proposed:** `PINNED` names all twelve, each `==` the version a certifying install test ran (test 9's "Successfully installed" line), installed so that pip resolves nothing -- a constraints file, or `--no-deps` over the full list -- and the doctor's `tools_python` row reads them; a re-ground moves them as it moves a tool's row. Not started.
"""


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    assert "INSTALL TEST 9, 2026-10-14" not in text and "\n**256. " not in text, "already applied"
    i = text.find(STATUS_OLD_HEAD)
    assert i >= 0 and text.count(STATUS_OLD_HEAD) == 1, "202's status block not found once"
    j = text.find("\n", i)
    old_status = text[i:j]
    assert old_status.endswith("*") and old_status.count("*STATUS:") == 1, old_status[-80:]
    text = text[:i] + STATUS_NEW + text[j:]
    h = text.find("\n\n**202. Handing the factory to a stranger.**")
    assert h > 0 and text.count("\n\n**202. Handing the factory to a stranger.**") == 1
    nxt = text.find("\n\n*STATUS:", h + 10)
    assert nxt > h, "no status block after 202's body"
    assert text[:nxt].endswith("nothing in the gates' verdicts would have."), text[nxt - 80:nxt]
    text = text[:nxt] + BODY_ADD + text[nxt:]
    k = text.find(STATUS_NEW)
    assert text[k + len(STATUS_NEW):].startswith("\n\n**202. "), "202's status no longer adjoins its heading"
    # 256 after 255: 255's heading line is the file's last line.
    last = text.rstrip("\n").rsplit("\n", 1)[-1]
    assert last.startswith(LAST_ITEM_HEAD) and text.count(LAST_ITEM_HEAD) == 1, last[:80]
    assert text.endswith("\n") and not text.endswith("\n\n"), repr(text[-5:])
    text = text + ITEM_256
    for line in ITEM_256.splitlines()[1:]:
        assert not (line.startswith("**") and line[2:3].isdigit()) or line.startswith("**256. "), line[:40]
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 202: status replaced, one paragraph appended; item 256 appended; now roadmap_status.py "
          "--write / --check")


if __name__ == "__main__":
    sys.exit(main())
