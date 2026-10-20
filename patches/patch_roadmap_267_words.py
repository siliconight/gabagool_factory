"""Roadmap 267 NARROWED: the one-word mappings that fit -- Deli Counter 0.240.0.

Anchored: the item's status block and the end of its body with the next item's status, read verbatim from the roadmap
when this was written, must each be there exactly once; nothing is written otherwise. Every line LF. Then
`python tools/roadmap_status.py --write` and `--check` regenerate and verify the index.

    python patches/patch_roadmap_267_words.py
"""
import pathlib
import sys

ROADMAP = pathlib.Path(__file__).resolve().parents[1] / "PIPELINE_ROADMAP.md"
HEADING = '**267. Furniture the generator places that Zoo builds as a box.**'
EDITS = [("roadmap 267's status", '*STATUS: OPEN 2026-10-20 -- measured (`docs/findings/asset_wishlist_2026-10-19/box_slots.py`), not started.*\n\n', "*STATUS: NARROWED 2026-10-20 -- THE ONE-WORD MAPPINGS THAT FIT: Deli Counter 0.240.0 (`patches/patch_dc_one_word_species.py`) routes `roof_ac` to `hvac_unit` (the bank's and the foundry's three roof AC units, 3.0-4.0 x 2.0 x 1.2-1.4) and `club_bar` to `counter` (primos_pizza's and strip_retail_a01's 2.8 x 0.8 x 1.15 serving bar -- not `back_bar`, the shelving behind a bar, 1.8 m and up). Each word claims only those volumes, and Zoo's own `kit.plan_kit` over the rebuilt slots plans all five as their species with no fallback (`patches/dc_one_word_species/zoo_plan_check.out.txt`); the library's plain boxes 1,486 -> 1,481, 142 names -> 138 (`box_slots_library_0240.out.txt`). Not made, and why: `container` -> `cargo_container` would build as the box -- a hinted volume is recorded long side first and Zoo's container is long in depth, and Zoo asks in the slot's own orientation -- so it waits on a rule for depth-long species; `barrier` -> `jersey_barrier` is arena_a02's crowd barrier, the walker's call. Left: those two, the stair guards (1,025) once a frame shows how a box reads as a guard, the runs and the new species the rest want, and the share in a cold run's package. Earlier status kept: OPEN 2026-10-20 -- measured (`docs/findings/asset_wishlist_2026-10-19/box_slots.py`), not started.*\n\n"), ("the end of roadmap 267's body", "the one-word mappings first, the stair guards once a frame shows whether a box reads wrong as a guard -- and the box share measured again on the library and in a cold run's package.\n\n*STATUS: OPEN 2026-10-20 -- read against the factory (`docs/findings/asset_wish", "the one-word mappings first, the stair guards once a frame shows whether a box reads wrong as a guard -- and the box share measured again on the library and in a cold run's package.\n\n**THE ONE-WORD MAPPINGS, 2026-10-20** (Deli Counter 0.240.0; `patches/dc_one_word_species/`). Of the four words the census suggested, each was checked in the order Zoo asks: what the word would claim in every spec and built slot (exactly its own volumes in each case), then whether the species' genome holds the slot's dims in the slot's own orientation. `roof_ac` and `club_bar` passed both and shipped. `container` failed the second on orientation alone: Deli Counter records every hinted volume long side first, and the cargo container is long in depth, as Zoo's jersey barrier, car and truck are, so the honest fix is a depth-long rule in `long_axis_first` and the composer that mirrors it, not a word. `barrier` passed both and is still not a word's to make.\n\n*STATUS: OPEN 2026-10-20 -- read against the factory (`docs/findings/asset_wish")]


def main():
    raw = ROADMAP.read_bytes()
    if b"\r\n" in raw:
        raise SystemExit("REFUSED: the roadmap has CRLF lines; nothing written")
    text = raw.decode("utf-8")
    for what, old, new in EDITS:
        if text.count(old) != 1:
            raise SystemExit("REFUSED: %s is there %d times, not once; nothing written" % (what, text.count(old)))
    for what, old, new in EDITS:
        text = text.replace(old, new)
    i = text.index(HEADING)
    if not text[:i].endswith(EDITS[0][2]):
        raise SystemExit("REFUSED: the status no longer adjoins its heading; nothing written")
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap 267 updated; now tools/roadmap_status.py --write and --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
