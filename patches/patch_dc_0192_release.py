"""Deli Counter 0.192.0: VERSION and CHANGELOG for `patch_dc_stale_pieces_tests.py`,
`patch_dc_stale_pieces.py`, `patch_dc_migrate_stale_pieces.py` and
`patch_dc_stale_pieces_baseline_apartment.py`.

    python patch_dc_0192_release.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

ENTRY = '''## [0.192.0] - a piece where a stair now is: L23 asks every piece, and 17 pieces in 10 shells move

**Found by 0.191.0's restored circulation gate.** Its one real finding on
cold run 9187's buildings was deli_a01's `counter_island_upper_hall_2`, 0.8 m
inside `deli_stair_up`. The census that followed
(`docs/findings/presentation_gates/stale_pieces.py` at the factory root)
counted 64 pieces in 18 of 146 shells standing over a slab opening or in a
stair's walk on their own storey. The census cannot tell two causes apart:
- **Stale.** The presets, `seed_cover` and `furnish` each clear a piece of
  the stairs when they PLACE it, and each is idempotent by name. A piece
  placed before a stair lengthened or widened is never asked again.
  - deli_a01, a02 and a03 each stood a counter island 41% over the up-stair's
    hole across the flight's arrival, another 54% over it, and a crate stack
    over the basement stair's.
  - **0.190.0 put twin_a01's two wardrobes 0.12 m2 each over its widened
    hole.** Under 0.189.0's 0.9 m flights they stood clear. Its swept gate
    passed, because walking is unaffected.
- **Unseen.** `furnish` and `seed_cover` clear the STAIRS
  (`_stair_reserved_rects`), not an authored `slab_holes` opening. Today's
  furnish still stands apartment_walkup_a01's dining set over one.

**What shipped:**
- **`layout_lint` L23 (WARN):** `stair_space`, `piece_story`, `stale_pieces`
  and `stale_piece_findings`. It measures, and says no cause.
- **`level_design.reseat_piece`** moves a piece to the nearest place that
  meets every condition:
  - in its room;
  - 0.15 m clear of the stairs' holes and walks;
  - 0.05 m off every other piece;
  - out of any door's approach it was not already in;
  - for a piece `seed_cover` placed, only where `_seed_clear` takes one.

  The search is a 0.1 m grid out to 12 m, nearest first. `_seed_clear`'s door
  rule is now `_seed_clear_doors`, one spelling that both ask.
- **`migrate_stale_pieces.py`** moves every stale piece the baseline does not
  freeze, then refurnishes, so the spec stays a fixed point of furnish. It
  moved 17 pieces in 10 shells:
  - deli_a01, a02 and a03: both counter islands and the crate stack. The
    upper halls are relaid by furnish around the islands.
  - twin_a01: both wardrobes, 0.4 m outward.
  - night_deli's and primos_pizza's stairwell pieces, strip_retail_a01's
    boiler, and the bank family's manager cabinet slivers.
- **`stale_pieces_baseline.json`** freezes 47 pieces in 8 shells, each with
  why. `test_stale_pieces.py` fails a new piece, and a fixed one still
  listed.
  - cbp_town_finale and final_stand: tables, cartons and desks wholly inside
    large openings. They could be authored space or floating furniture, so a
    frame comes first.
  - foundry_heist_vertical: a skylight box and a roof AC over roof openings,
    possibly by design.
  - The garages: columns at a ramp opening, which are structure.
  - apartment_walkup_a01: furnish over an authored hole. The fix is in the
    generator.

**Refuted first, kept:**
- **Moving apartment_walkup_a01's dining set.** It is furnish's, and the
  refurnish puts it back.
- **A migration that did not refurnish.** Moving deli_a01's islands changes
  where furnish lays its hall, and `test_club_fixtures`' fixed point failed
  on deli_a01.
- **A 6 m reach.** It left four pieces unplaced; 12 m placed them all. The
  deli islands went 6.4 m east, and the primos shelf about 6 m.
- **Two storey rules.**
  - The census's round put a hung sign on the storey above.
  - A plain floor put final_stand's `boss_desk`, 5 cm below storey 2's floor
    line, on storey 1.
  - `piece_story` takes the nearest floor within a slab (0.25 m), and floors
    anything else.
- **The first hung-sign test** set the sign's centre, not its base, 2.2 m
  up, and was wrong.

**Measured after:**
- **The nav gate** on all 11 shells rebuilt (the 10 moved, and
  apartment_walkup_a01 rebuilt from its unchanged spec): every verdict is as
  0.191.0's commit run had it.
  - deli_a02, night_deli, strip_retail_a01 and primos_pizza were already not
    navigable, for the same markers.
  - night_deli's register still connects at 2 of 8 origins, and primos's
    stair at 6 of 8.
- **The circulation gate's shell arm** on the rebuilt delis is clean, where
  it named deli_a01's island.
  - twin_a01's porch deck and stoop read 0.2 m into its front doorways. They
    are walkable pieces at a door, a false positive this does not touch.
- **Lint:** the L23 warnings went, and nothing else changed except L9 counts
  moved by the deli refurnish (advisory).
- **Themed fitness:** unchanged, 102 of 127.

**Tests:** `test_stale_pieces.py`, 11. Synthetic L23 and re-seat cases, a
pin on twin_a01, and the population against the baseline. All fail on
0.191.0.

**Suite:** 1,268 passed, 2 skipped. That is 0.191.0's 1,257 and these 11.

'''


def main():
    v = DC / "VERSION"
    assert v.read_bytes() == b"Deli Counter 0.191.0", v.read_bytes()
    cl = DC / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## [0.191.0] - the circulation gate reads"), text[:60]
    cl.write_bytes((ENTRY + text).encode("utf-8"))
    v.write_bytes(b"Deli Counter 0.192.0")
    print("Deli Counter 0.192.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
