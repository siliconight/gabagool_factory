"""Roadmap 55 CLOSED and 171 NARROWED, re-measured 2026-10-15 against today's toolchain
(`docs/findings/open_items_remeasure/`). Replaces each item's multi-line status block (each asserted once, from its
first line to the line ending the block's `*`). The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_55_171_remeasured.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

ITEMS = [
    ("*STATUS: OPEN 2026-09-05 -- SEEN AGAIN ON A SECOND MISSION AND THE ART\nDECISION IS NOW MADE: IT IS A BUG.",
     "\n\n**55. The level ships sign fixtures with no sign art, and three of four cannot\nbe addressed.**",
     "*STATUS: CLOSED 2026-10-15 -- answered by three Lux releases and re-measured on cold run 9314's package "
     "(`docs/findings/open_items_remeasure/`, `sign_panels_55.py`). Lux 0.33.0 turned the area rig's preview quad "
     "off for a sign -- the hardware is the panel, Zoo's cabinet carries the face -- and 0.36.0 builds a window's "
     "rig with no `AreaPanel_Surface` at all; 0.34.0 names a rig `<name>_dup<k>` where `add_child` had renamed every "
     "rig after the first building's to `@Node3D@<n>`. On 9314's `lux.applied.tscn`: 964 nodes, `AreaPanel_Surface` "
     "0, engine names 0, spawner names 205, and the scene's only two quads are the sign faces under Zoo's art "
     "(`sign_scrapple_sons_deli` and `sign_docs_discount_drugs`, albedo and emissive). The count this item asked "
     "for in the validation output was not added: the class it would count, a blank Lux card, no longer exists in "
     "a package; a sign with no art is a Zoo face without a texture, which the closure scan reads. The first "
     "re-read counted seven 1.4 m quads that were the rigs' `panel_size` property, kept as refuted there.*"),
    ("*STATUS: OPEN 2026-09-23 -- A BUILT CAPABILITY THAT IS ESSENTIALLY UNUSED. 2\nfire escapes in 370 specs; "
     "3 ladders in the whole library are exterior.*",
     "\n\n**171. Exterior access exists and almost never gets placed.**",
     "*STATUS: NARROWED 2026-10-15 -- re-measured against today's specs (`docs/findings/open_items_remeasure/`, "
     "`exterior_access_171.py`): of the library's 159 specs, 7 carry a fire escape where 2 of 370 did -- the five "
     "walk-up Empties' `fire_escape_stack: \"front\"` (Deli Counter 0.220.0, Zoo 1.110.0's `fire_escape` a storey a "
     "slot, merged with the front by Level Factory 0.209.0; `gs_midrise_a`, `_b`, `_g`, `_h`, `_i`) and the two "
     "assemblies this item counted -- so every urban level stands the fire escapes of the walk-ups it deals, and a "
     "strip level stands none. Exterior ladders 3 of 78, as before. Left: the stack is visual only (no collision), "
     "so it is not the alternate entry route this item asked to measure; 0.220.0's rule is chosen (a walk-up of six "
     "storeys or fewer, not a corner block), not derived from a building's stairs as the item proposed; and the "
     "library's two older walk-ups carry the assembly, not the stack.*"),
]


def main():
    raw = RM.read_bytes()
    assert b"\r\n" not in raw, "the roadmap is LF"
    text = raw.decode("utf-8")
    for old_head, heading, new in ITEMS:
        i = text.find(old_head)
        assert i >= 0 and text.count(old_head) == 1, ("status block not found once", old_head[:60])
        # the block runs to the first line that ends with `*` at or after its head
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
    print("roadmap 55 CLOSED, 171 NARROWED; now roadmap_status.py --write / --check")


if __name__ == "__main__":
    sys.exit(main())
