"""Roadmap 107 NARROWED: the list of what the export needs from Lot, written 2026-10-15
(`docs/findings/open_items_remeasure/`). Replaces 107's status block (asserted once, from its first line to the
line ending the block's `*`). The index is NOT touched here: run `python tools/roadmap_status.py --write` then
`--check` after it.

    python patches/patch_roadmap_107_narrowed.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUS_OLD_HEAD = "*STATUS: OPEN 2026-09-06 -- AN OWNERSHIP QUESTION RAISED FROM A WALK"
HEADING = "\n\n**107. Level Factory should own the final export, not Lot.**"
STATUS_NEW = (
    "*STATUS: NARROWED 2026-10-15 -- the first deliverable exists: the list of what the export needs from Lot, "
    "read off `export.py`'s 21 uses of the themed site at 0.215.1 (`docs/findings/open_items_remeasure/`). The "
    "assembly `site.tscn`, copied to the package root and read twice before that -- `_standing_lot_ids` for the "
    "`lot/<id>/site.tscn` references that say which building packages ship (0.207.0), `_assembly_building_dir` "
    "for whether the composed root belongs under one lot, three facts read off disk; three sibling directories "
    "copied whole, `skins/`, `cover/`, `signs/`, by a list the exporter's own comment calls the contract; every "
    "`*.obj` beside the scene (the paint, the wires, the drains); `responders.json` for the vehicles marked "
    "dynamic and the arrivals; the provenance sidecars; and Lot's site gameplay record through the staged inputs. "
    "Two regexes, not three, since 0.207.0. Lot's job emits none of it as a manifest, and the contract is held by "
    "the closure gate refusing an unresolved reference. Left: the manifest Lot emits and the exporter consumes, a "
    "design step for Lot and Level Factory together.*"
)


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    i = text.find(STATUS_OLD_HEAD)
    assert i >= 0 and text.count(STATUS_OLD_HEAD) == 1, "107's status block not found once"
    j = i
    while True:
        k = text.find("\n", j)
        assert k > 0
        if text[i:k].endswith("*"):
            break
        j = k + 1
    old = text[i:k]
    assert old.count("*STATUS:") == 1 and old.endswith("*"), old[-80:]
    assert text[k:].startswith(HEADING), ("the block does not end just above its heading", text[k:k + 80])
    text = text[:i] + STATUS_NEW + text[k:]
    m = text.find(STATUS_NEW)
    assert text[m + len(STATUS_NEW):].startswith(HEADING), "107's status no longer adjoins its heading"
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap 107 NARROWED; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
