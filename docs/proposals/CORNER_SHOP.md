# The corner shop: a lit storefront at grade on the urban street (roadmap 241)

**The comps** (`docs/reference/URBAN_MIDRISE_COMPS.md`): "Corners carry the life. The corner building has the shop
at grade (lit, awning), homes above. The middle of the block is residential." Frame 2: "a lit restaurant at street
level under an awning -- the warm light the eye goes to first."

**Today.** The urban wall is mid-rise Empties (Deli Counter's `empty_midrise`) with windows at grade and a lobby
door. An Empty has no lights by design; its windows are paint (Zoo's `window_panes`, one atlas, one material).
The builder's own comment lists the corner shop as a capability it does not have.

## The first cut, in order

1. **Zoo: a shop pane.** A second painted atlas, `shop_panes`, beside `window_panes`. A storefront is wider than a
   sash and shows a different room, so it gets its own cell shape (landscape) and material.
   - The states, appended only: a deli (warm, a case and shelves), a grocery (cool fluorescent, shelf rows), a
     bar (dim amber, a neon glow low), a laundromat (cool, a row of machines), a roll-down gate (closed, unlit),
     and dark glass.
   - Lit cells glow through a separate emission image, so Lux's power cut darkens them as it does `_Face`.
   - It costs no light: one more material, on a corner shop's front only.
   - `_arch.py`'s pane branch builds a facade window whose `pane` is a shop state on the shop atlas.
   - `kit.py` keys the shop state into the module stem, as it keys a window pane.
2. **Deli Counter: the corner variant.** `empty_midrise(..., shop=...)`: the ground floor's front bays on the shop
   side become shop windows (wide, a low sill), with the pane authored on the opening (`pane: shop_*`) instead of
   chosen, and a shop door. Homes stay above.
   - Built as their own archetypes beside the six, with no two alike.
3. **Level Factory: where it stands.** The terrace knows where a road crosses the far side (`_blocked`). The block
   either side of a crossing, and at the plate's ends, is a corner, and takes a corner variant.
4. **Later steps:** a Zoo awning species over the shop (there is none), and the sign band (`neon_sign` and
   `sign_box` exist; the invented brands are the fake Delco names).

## As built, 2026-10-14

- **Step 1, Zoo 1.107.0 (fbbe818).** `core.shop_panes` as listed above, `M_Shop_pane_Face`. `recipes/_arch.py`'s
  `PANE_ATLASES` picks the atlas by the state.
- **Step 2, Deli Counter 0.218.0.** `empty_midrise(..., shop=...)` and `EMPTY_CORNERS`, four blocks:
  - a deli, a bar, a laundromat and a grocery;
  - 12 to 18 m wide and 5 to 8 storeys;
  - every front bay at grade a 2.4 m `SHOP_WINDOW` but the door's.

  Three decisions the list above left open:
  - **The prefix is `gs_cornershop_`, not `gs_corner_`.** `gs_corner_station` is an enterable gas station that
    Level Factory's clusters name as a corner store.
  - **The shop's door is the block's front door,** centred, with the authored finish and, on two of the four, the
    iron security door. The homes above keep the service door behind. A glazed shop door needs a painted leaf
    Zoo does not have.
  - **Built as their own archetypes,** no two alike, as proposed.
- **Step 3, Level Factory 0.206.0.** Each run of the urban wall opens and closes on a corner block. A run lies
  between two roads crossing the far side, or a road and the plate's end.
  - **The plate's ends count as corners,** as proposed. A run is one block face, and its ends are the block's
    corners.
  - **On urban_row_001 no road crosses the far side.** Both side streets leave the through road northward, so
    the wall is one run, and its corners stand at the plate's ends.
  - **The near side's corners** (the side streets' T-junctions) are the mission's own buildings, so `infill`
    stands no corner block.
- **Level Factory 0.206.1 (c189baf).** Cold run 9295's seed_9003 closed its wall 12.70 m short of the run's end,
  traced to a fill that stopped on a spent bag. The fill now deals afresh: over 600 walls the worst shortfall went
  14.20 -> 4.10 m (`patches/lf_corner_fill/`).
- **Proven:** cold runs 9295 and 9296, 0 interventions each.
  - Every candidate's wall opens and closes on a lit shop, and the pick held at PASS 100.
  - Priced at -4.0 draws a heading, a p95 within its floor and +4.2 MiB video memory.
  - Seen: `docs/findings/urban_street/ab_9295/corner_sheet.png`.

- **Step 4's awning: Zoo 1.108.0 (b028d3d) and Deli Counter 0.219.0 (42fe102a).**
  - Zoo's `shop_awning` is a canvas shed (a slope, a 10 in valance, closed ends) in four colours, as the form.
  - Each corner block hangs one over its storefront in its shop's colour: a deli's red, a bar's black, a
    laundromat's navy, a grocery's green.
  - It is 1.2 m out, sunk 8 mm into the wall, its valance 0.1 m over the storefront's head. No collider.

## Next

- **The awning is built and proven** (cold run 9297, 0 interventions, nothing the graders read moved). At night it
  barely reads: unlit dark canvas over a glow that lights nothing. Brighter canvas or a light under it is the
  walker's call, and its frame time is still to price on a quiet machine.
- **The sign band** over the shopfront: `neon_sign` and `sign_box` exist, and the brands are the invented
  Delco ones.
- **The walker's calls:**
  - the shops' glow, since the cool ones run nearly white;
  - the corners' heights, since they step the skyline down at the plate's ends;
  - the open questions below.

## Costs to price before it ships

One more material per corner shop facade. The merged facade group then draws one more surface, and two or
three corners a street means a few draws. It costs no light, since the glow is emission paint. Price it the
cover merge's way at the fixed stations.

## Open for the walker

- Which shops. The comps show a restaurant; the states above are a first set.
- Whether a corner shop's glow should change with the time of day (open by day, gated at midnight).
