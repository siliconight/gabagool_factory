"""Roadmap: items 193 and 196 move on Deli Counter 0.202.0.

    python patch_roadmap_0202.py

Anchored on both status lines in full, as read 2026-10-07 (1,226,956 bytes,
LF). Then run `tools/roadmap_status.py --write` and `--check`.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RM = ROOT / "PIPELINE_ROADMAP.md"

S193_OLD = ("*STATUS: NARROWED 2026-10-06 -- the rule exists and 17 pieces moved; 47 are frozen, 30 of them over "
            "AUTHORED openings that furnish cannot see. Layout lint L23 (Deli Counter 0.192.0) asks every piece "
            "whether it stands over a slab opening or in a stair's walk on its own storey: 64 pieces in 18 of 146 "
            "shells. `migrate_stale_pieces.py` moved 17 in 10 shells by each piece's own placement rule and "
            "refurnished each spec -- deli_a01-a03's counter islands and crate stacks, twin_a01's wardrobes "
            "(0.190.0's wider flights had put them over the hole) and five small ones; every nav-gate verdict is "
            "as before, themed fitness unchanged at 102 of 127, and in cold run 9188 deli_a01's circulation "
            "conflict is gone. `stale_pieces_baseline.json` freezes 47 in 8 shells and fails a new one. Open: "
            "furnish and seed_cover check stairs, not authored `slab_holes`; cbp_town_finale's and final_stand's "
            "tables stand inside 28 x 22 m and 10 x 8 m openings with nothing declared under them.*\n")
S193_NEW = ("*STATUS: NARROWED 2026-10-07 -- the rule exists and 46 pieces moved; 18 are frozen, every one authored "
            "or structure. Layout lint L23 (Deli Counter 0.192.0) asks every piece whether it stands over a slab "
            "opening or in a stair's walk on its own storey: 64 pieces in 18 of 146 shells. `migrate_stale_pieces.py` "
            "moved 17 in 10 shells by each piece's own placement rule and refurnished each spec -- deli_a01-a03's "
            "counter islands and crate stacks, twin_a01's wardrobes (0.190.0's wider flights had put them over the "
            "hole) and five small ones; every nav-gate verdict is as before, themed fitness unchanged at 102 of "
            "127, and in cold run 9188 deli_a01's circulation conflict is gone. Deli Counter 0.202.0 makes "
            "`_seed_clear` -- which furnish and seed_cover both ask -- keep a standing piece 0.3 m off an authored "
            "hole in its own storey's floor, and the refurnish moved apartment_walkup_a01's dining set and "
            "cbp_town_finale's and final_stand's 26 furnished pieces off theirs: `stale_pieces_baseline.json` 47 "
            "in 8 shells -> 18 in 7. Open: the 18 -- cbp_town_finale's and final_stand's AUTHORED tables, "
            "consoles, statue and cover standing inside atrium holes nothing fills, foundry's roof pieces over "
            "roof openings, the garages' columns at a ramp opening's edge -- each a look, not a rule.*\n")

S196_OLD = ("*STATUS: OPEN 2026-10-07 -- measured, not fixed: 155 of the library's 4,086 furnished wall pieces stand "
            "against a room edge with no built wall behind them, in 18 of 146 shells "
            "(`docs/findings/wall_pieces_without_walls/`); the generated deli does it too (cold run 9191's frame). "
            "The fix belongs in `level_design._wall_slots`.*\n")
S196_NEW = ("*STATUS: NARROWED 2026-10-07 -- fixed in the generator, unproven in a level. Deli Counter 0.202.0: "
            "`_wall_slots` offers a slot only where a built wall (`layout_lint.built_walls`) holds the piece's "
            "whole run, the unheld slots dropped after the shuffle so only a piece that stood against nothing moves "
            "(dropped before it, the first draft re-rolled 33 specs); the refurnished library's census reads 0 of "
            "3,998 (was 155 of 4,086 in 18 shells), 20 specs moved, 153 fewer pieces, cigarette machines 121 -> "
            "119. The furnish and club probes stood their rooms in walls that were open edges, and now stand them "
            "in the shell. Open: the next cold run that draws a deli, to see the customer floor's open edge bare; "
            "a partition is still unfurnished (`_seed_clear` keeps every piece 1.0 m off a partition's line).*\n")


def main():
    data = RM.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    for old in (S193_OLD, S196_OLD):
        assert text.count(old) == 1, "anchor found %d times: %r" % (text.count(old), old[:70])
    text = text.replace(S193_OLD, S193_NEW).replace(S196_OLD, S196_NEW)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: 193 and 196 moved on; %d -> %d bytes" % (len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
