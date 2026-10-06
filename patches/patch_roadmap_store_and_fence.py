"""PIPELINE_ROADMAP.md: close 185 (demo shells), and file 186 (the detail in
the generator), 187 (two names on one building) and 188 (the fence at the
playable edge), each with its status line. Run `tools/roadmap_status.py
--write` then `--check` after.

    python patch_roadmap_store_and_fence.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ROADMAP = ROOT / "PIPELINE_ROADMAP.md"

ANCHOR_185 = "**185. Demo and reference shells are drawn into real levels.** Found in the\n"
STATUS_185 = (
    "*STATUS: CLOSED 2026-10-06 -- Deli Counter 0.187.0 says it: five demo and "
    "reference specs carry `demo: true`, carried into their validation manifests, "
    "and Level Factory 0.144.4's `source_exclusion` refuses a shell whose manifest "
    "says so. Cold run 9178 (card_block_001, whose 9174 lots had drawn "
    "`setback_demo` and `pvp_station_ref`) drew neither on any candidate, 0 "
    "interventions.*\n\n")

TAIL = '''

*STATUS: NARROWED 2026-10-06 -- the gas station and the convenience store are done and proven: Deli Counter 0.188.0, Zoo 1.75.0, Pixelcoat 0.58.0, Level Factory 0.146.0; cold runs 9181 (a never-seen one-building convenience store, generated) and 9182 (gas_block_001), both 0 interventions. The strip club's band no longer contradicts its neon (item 187's option D). Open: deli detail; the brief words still refused (`deli`, `night_deli`, `stop_n_go`, `corner_store`, `nightclub`).*

**186. The detail put into a building type must live in the logic every level runs for it.** The walker, 2026-10-06: "the care and detail we put into the strip club and flappahs convient store [should not] just get lost to the next phase of level creation. That level of detail should be in the logic that is called when a level calls for a Gas Station, Convient Store, or a strip club."

**WHAT WAS WRONG.**
- **Migrated, not generated.** Some of that detail lived only in spec files a migration had edited: the window beer sign and the sale posters were in every library store, and in 0 of the 6 stores `presets.gas_station` generated.
- **The Flappahs store had no recipe.** It sat in the gas-station family as `gas_station_a03`, and `convenience_store` was an alias for the forecourt station.
- **A generated store's identity was read off the mission id.** `presets.gas_station` wrote no `preset` key.
- **The brand had two spellings.** Zoo had FLAPPHAS and Pixelcoat FLAPPAHS, and `delco_1997` had no FLAPPAHS sign at all.
- **The words a brief reaches for were refused.** `mini_mart`, `service_station` and `gentlemens_club` never reached a recipe.

**WHAT SHIPPED.**
- **Deli Counter 0.188.0.**
  - `convenience_store` is a recipe of its own.
  - a03 becomes `convenience_store_a01`.
  - The generated store gets the window sign, the posters and its `preset`.
- **Zoo 1.75.0:** FLAPPAHS, and a convenience store's door says it.
- **Pixelcoat 0.58.0:** FLAPPAHS is the only name a station or store can be dealt.
- **Level Factory 0.146.0.**
  - The brief words resolve.
  - A generated row reads the preset it was built from.
  - A fascia is dealt a name, never the price board.
'''

TAIL += '''
*STATUS: NARROWED 2026-10-06 -- option D shipped: Level Factory 0.147.0 (a band names a shop; 68 of 148 library shells are dealt one, where all 148 were) and Zoo 1.76.0 (a retail strip is not a strip club). Open: a named shop's band and door still say two different names -- option A (one table, Zoo's names on both) or B (the door says the band's name) is the walker's call.*

**187. A building carries two names.** Found 2026-10-06, measuring the strip club's open item (`docs/findings/two_names_one_building/`).

**WHAT WAS MEASURED.** A building can carry two lit name signs:
- the band Lot hangs on its street face, dealt by Level Factory from Pixelcoat's sign profile;
- the box over its door, which Zoo names from `storefront_names`.

Of the 95 library shells with a door box, the band's pool held the door's name for 6.

**THE WORST PAIRINGS.** A police station could be dealt STATE WINE + SPIRITS, because Pixelcoat's `civic` family means state-run commerce. A hospital shipped as CORNER TAP (cold runs 9171 and 9173). A casino wore CLUB VELVET (9179). In 9182 an airport wore DELCO STORAGE and a funeral home KEYSTONE SAVINGS.

**THE OPTIONS** (the finding's README):
- **A.** One name table that every sign reads.
- **B.** The door says the band's name.
- **C.** One sign a building.
- **D.** Stop the absurd pairings now.
'''

TAIL += '''
*STATUS: OPEN 2026-10-06 -- phase one shipped: Zoo 1.77.0's `chain_link_fence` (two draws a run) and Lot 0.97.0's `site_fences`, closing an Empty row's gaps and ends; Pixelcoat 0.59.0 lists `chain_link` as a kind Zoo knows. Cold run 9183 is its first level: seven fences on gas_block_001, 0 interventions, findings 57 -> 57 against 9182 on the same candidate. Seen at 7 m, an alley reads as a gated alley. Seen along a 16.8 m run, the far fabric is cut away -- alpha-test mip thinning, the fabric being about 25 % wire -- and that is the next step (coverage-preserving mips, a lower cutoff for this kind, or a distant card; a look-and-price call). Priced against 9182 run twice: +3.8 draws a station, +0.020 ms median against a control spread of 0.124 ms -- under the floor; 22 of its +32 mesh instances are ground tiles Lot splits at each fence's edge, a cheap follow-up. Open after that: the plate perimeter, which needs the backdrop behind it because the fence is see-through; vacant lots; Empties not in a row.*

**188. The fence at the playable edge.** The walker, 2026-10-04: "I like the idea of a fence between playable areas and non playable areas, thats good feedback to the player".
- A fence goes wherever playable ground meets an Empty's back, a vacant lot or the backdrop.
- The mock is `docs/findings/backdrop_mock/`.

**PHASE ONE: AN EMPTY ROW'S GAPS.** Every gap in a row of Empties that a player's capsule fits through (0.7 m) is a way behind the row. So is the ground from each end of a row to the plate.
- Each is closed along the row's front line.
- Never across a road, path, building or blocker.
- Never enclosing a mission marker.
- On cold run 9180's site: three runs, 3.0, 13.5 and 22.0 m.

**WHY NOT THE PERIMETER FIRST.** The perimeter is four opaque 3 m boxes ("the edge of the world: bright, flat, dead"). Chain link is see-through, so a fence there shows the void beyond the plate until a backdrop stands behind it, which is the walker's next item after the Empties.
'''


def main():
    assert "PRICE_88" not in TAIL, "fill in item 188's price before applying"
    data = ROADMAP.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.count(ANCHOR_185) == 1, "item 185's head"
    i = text.index(ANCHOR_185)
    assert "*STATUS:" not in text[max(0, i - 400):i].split("\n\n")[-1], "185 already has a status"
    text = text[:i] + STATUS_185 + text[i:]
    assert "**186." not in text and "**187." not in text and "**188." not in text
    text = text.rstrip("\n") + "\n" + TAIL
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap: 185 closed; 186, 187, 188 filed")


if __name__ == "__main__":
    main()
