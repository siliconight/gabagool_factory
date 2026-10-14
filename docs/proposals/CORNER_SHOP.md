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

## Costs to price before it ships

One more material per corner shop facade. The merged facade group then draws one more surface, and two or
three corners a street means a few draws. It costs no light, since the glow is emission paint. Price it the
cover merge's way at the fixed stations.

## Open for the walker

- Which shops. The comps show a restaurant; the states above are a first set.
- Whether a corner shop's glow should change with the time of day (open by day, gated at midnight).
