"""Roadmap 259 NARROWED, 2026-10-19: Deli Counter 0.229.0 (54f5b5d4, `patches/patch_dc_freshness_sources.py`) watches
20 more modules and the agent contract, names the 12 kept out with why, and a test classifies every module a build
reaches; `layout_lint` stays unwatched by decision, which is what is left. The status line is replaced whole, the
OPEN 2026-10-19 status kept after it verbatim; a BUILT paragraph goes after the item's last line, the last line of
the file. Anchored on the status line's sha256 with the heading two lines below it, and on the last line's sha256.
The index is NOT touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_259_narrowed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"
STATUS_SHA = "58a02a8db33d7bcb9e6e3de50e1e267df995469a289586ccd25c9bb796e5daed"
HEADING_PREFIX = "**259. Deli Counter's freshness gate watches 22 of the 54 modules a shell build reaches.**"
OLD_PREFIX = "*STATUS: OPEN 2026-10-19 -- "
LAST_SHA = "100e6959bcb3cf840cc8f04d5c8c5b55a29ce913bbd5ae80a7f067cd611590b8"

NEW = ("*STATUS: NARROWED 2026-10-19 -- built, with one module left out by decision. Deli Counter 0.229.0 (54f5b5d4, "
       "`patches/patch_dc_freshness_sources.py`): `GEOMETRY_SOURCES` gains 20 modules and `agent_contract.json`, "
       "still a literal; `NOT_BAKED`, a new literal, names the 12 a build reaches that are kept out, each with why; "
       "`test_freshness_sources.py` walks the build's imports and fails on a module in neither (4 of its 5 fail on "
       "0.228.0). No rebuild: every judged shell was built after the newest source added; the gate reads 159 shells "
       "newer than `level_design.py`, now its newest source, and Level Factory's guard reads 44 sources and 0 "
       "stale. Left, a call made 2026-10-19 and meant to be changed: `layout_lint` stays unwatched, as "
       "`test_gates_that_only_read_shells_are_not_watched` holds it, though stairwell reads its `_host_openings` "
       "and `DOOR_APPROACH_M` and stair_pitch acts on its findings -- moving those into a geometry module watches "
       "them without watching the lint. Earlier status kept: OPEN 2026-10-19 -- ")

BODY = [
    "",
    "**BUILT, 2026-10-19** (Deli Counter 0.229.0, 54f5b5d4; `patches/patch_dc_freshness_sources.py` and "
    "`dc_freshness_sources/`). **Watched now:** agent_contract, ledge_cover, level_design, material_kind, "
    "prop_species, rarity, setbacks, skin_style, stair_pitch, stoop, tactical, tscn_export, vault_room, zoo_export, "
    "the six migrations presets call, and `agent_contract.json` -- 44 sources where there were 23. **Named as kept "
    "out** (`NOT_BAKED`, each with why): circulation, zfight_gate, evidence and the eight gates and reports it "
    "calls, and layout_lint. **The test** (`test_freshness_sources.py`, 5) reads both literals the way Level "
    "Factory reads the tuple, with `ast`, and fails when a module the build reaches is in neither, so the next "
    "module the builder imports is classified the day it lands. **Proven:** 4 of the 5 fail on 0.228.0 (the "
    "fifth, that the tuple is a literal naming files, holds before and after); on 0.229.0 they and the gate's "
    "own ten pass; the suite 1581 passed, 2 skipped; the hook passed. **No rebuild, measured before writing:** "
    "the newest added source, `level_design.py`, is 09:45:29 and the oldest judged shell 09:47:47, so the gate "
    "reads 159 shells up to date against it. **The decision left in:** `test_gates_that_only_read_shells_are_not_"
    "watched` keeps `layout_lint.py` out so a lint edit does not demand a rebuild. Its premise -- that editing a "
    "checker does not make a shell stale -- is refuted in its own docstring, and the cost argument is kept. "
    "**What would close this:** move `_host_openings` and `DOOR_APPROACH_M` into a geometry module stairwell "
    "imports instead, decide whether stair_pitch may act on lint findings at all, and watch what remains.",
]


def _sha(line):
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    lines = raw.decode("utf-8").split("\n")
    hits = [i for i, l in enumerate(lines) if _sha(l) == STATUS_SHA]
    assert len(hits) == 1, f"item 259's OPEN status found {len(hits)} times"
    i = hits[0]
    assert lines[i + 1] == "" and lines[i + 2].startswith(HEADING_PREFIX), "the status no longer adjoins 259's heading"
    old = lines[i]
    assert old.startswith(OLD_PREFIX) and old.endswith("*")
    assert lines[-1] == "" and _sha(lines[-2]) == LAST_SHA, "item 259 is no longer the end of the file"
    for k in range(i + 3, len(lines) - 1):
        assert not lines[k].startswith("*STATUS:"), "another status after item 259 at line %d" % (k + 1)
    for block in BODY:
        assert not (block.startswith("**") and block[2:3].isdigit()), "a body line would parse as an item"
    lines[i] = NEW + old[len(OLD_PREFIX):]
    assert lines[i].startswith("*STATUS: NARROWED 2026-10-19 -- ") and lines[i].endswith("*")
    lines[-1:-1] = BODY
    RM.write_bytes("\n".join(lines).encode("utf-8"))
    print("roadmap 259 NARROWED (Deli Counter 0.229.0); now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
