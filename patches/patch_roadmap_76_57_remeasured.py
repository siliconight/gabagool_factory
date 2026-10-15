"""Roadmap 76 re-read (OPEN) and 57 NARROWED, 2026-10-15 (`docs/findings/open_items_remeasure/`). Replaces each
item's status block (each asserted once, from its first line to the line ending the block's `*`). The index is NOT
touched here: run `python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_76_57_remeasured.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

ITEMS = [
    ("*STATUS: OPEN 2026-08-29 -- FOUR MECHANISMS READ IN THE CODE, NONE REACHABLE\n",
     "\n\n**76. Every mechanism this factory has for making two copies of one module\nlook different is "
     "implemented, and none of them is wired in.**",
     "*STATUS: OPEN 2026-10-15 -- re-read at Level Factory 0.215.1 against cold run 9314 "
     "(`docs/findings/open_items_remeasure/`): the four mechanisms sit where they were, at today's lines. "
     "`commands/__init__.py:1123` and `:1131` still read `patina_theme` off a model that has no such field (0 "
     "in `mission.brief.schema.json`; 9314's Patina job ran `--mode vertex-color --theme default`), `art_mode` "
     "is `vertex-color` at `:1117` and `:1130`, `slot_variation` and `instances.json` are 0 hits outside tests "
     "while Patina still implements the pass, and the planner's Pixelcoat job is `theme-library`, the profile "
     "path, which reaches weathering's wet half (`pooling_mask`, `wetness_mask`; Pixelcoat 0.46.0 and 0.49.0 -- "
     "uniform per material, not two copies differing) and none of its wear half (`edge_wear_mask`, `grime_mask`, "
     "`streaks`, the `variations` maps: `pipeline_generation_7.py` only, from `process --mode generation_7` or "
     "`build`). The ground the deferred layer decision stands on moved: 75 closed by measurement the day it was "
     "filed, 84 decided the vertex-wear layer (objects wear, tiles do not), and since Level Factory 0.143.0 the "
     "Empties reach the package one mesh a side per material -- 10 of 9314's 13 buildings, 6,490 surfaces into "
     "136 meshes -- so a merged side's vertex arrays are its own and the instancing economy per-instance "
     "variation was weighed against now covers the three mission buildings (deli_a01: 347 wall instances of 27 "
     "stems), not the level. The layer question stays unsettled here, as the item asked. Earlier status, kept: "
     "filed 2026-08-29 with the world-space projection re-measured against a null run (item 90) clearing the "
     "floor on 7 of 8 shots, max |delta| 43-217 against 7-16, confirmed by eye to fix item 88; the earlier "
     "\"13.6-19.0% of pixels\" reading survived its own audit, though the floor it was quoted against did not.*"),
    ("*STATUS: OPEN 2026-08-23 -- FRAMED, UNWORKED. Raised from the 2026-08-23\n",
     "\n\n**57. Asset boundaries are implementation details; architectural boundaries\nare what the player "
     "should see.**",
     "*STATUS: NARROWED 2026-10-15 -- two of the five pieces shipped, each with the walk as judge, re-read "
     "(`docs/findings/open_items_remeasure/`). The corner: Deli Counter 0.102.0 / 0.102.1 (item 58) seats a "
     "`wallEnd` unit post at every corner, ENV_CORNER_OPEN 988 -> 0 over 124 buildings with zero new modules -- "
     "a family was not needed (`deli_a01.slots.json` today: 59 `end` posts against 478 full modules; "
     "`wallCorner` 0 hits). The continuity mechanism: world-space triplanar on every kit material, Level Factory "
     "0.57.0 (item 88), texel density 47x / 66x / 12.5x -> 1.0x over 3,554 surfaces and confirmed by eye; its "
     "cost against the instancing economy is nil by construction (the module stays one GLB instanced N times, "
     "the projection is an import flag), its frame cost has not been priced on the station harness (the A/B "
     "lives in `tools/walk_themed.py --triplanar`, a walk project), it forecloses a trim-sheet atlas (88) and "
     "needed an exception for a lit face's own UVs (LF 0.140.0). Left, named: edge metadata -- slot manifest "
     "1.3.0 carries provenance and fit (`wall`, `story`, `facing`, `size_mod`, `material`, `fit`) and nothing "
     "that says what an edge means; weathering in building space -- Patina's per-slot pass unwired, the kit's "
     "vertex wear off by 84's decision, Pixelcoat's wear / grime / streaks on the recipe path only (76's "
     "record); the mid-distance instrument -- 78's four measure appearance and none is pointed at the kit path, "
     "74's ruler reads form. One fact bearing on the core trade: since LF 0.143.0 the Empties ship one mesh a "
     "side (10 of 9314's 13 buildings), so there the instancing economy is already spent and the seam is one "
     "mesh's texture, not N copies of one.*"),
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    for old_head, heading, new in ITEMS:
        i = text.find(old_head)
        assert i >= 0 and text.count(old_head) == 1, ("status block not found once", old_head[:60])
        j = i
        while True:
            k = text.find("\n", j)
            assert k > 0
            if text[i:k].endswith("*"):
                break
            j = k + 1
        old = text[i:k]
        assert old.count("*STATUS:") == 1 and old.endswith("*"), old[-80:]
        assert text[k:].startswith(heading), ("the block does not end just above its heading", text[k:k + 80])
        text = text[:i] + new + text[k:]
        m = text.find(new)
        assert text[m + len(new):].startswith(heading), "status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 76 re-read, 57 NARROWED; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
