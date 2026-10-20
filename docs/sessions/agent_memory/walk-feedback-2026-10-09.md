---
name: walk-feedback-2026-10-09
description: "Walker's walk of club_block_014 (cold 9213), 2026-10-09: twelve notes; 1-6, 9-11 fixed and proven (box truck 9219, bags 9220); 8+12 edge menu sent (D recommended); 7 moon waits"
metadata:
  node_type: memory
  type: project
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-10T04:17:15.947Z
---

The walker walked club_block_014 (cold run 9213, midnight) on 2026-10-09 and
sent four notes, with screenshots.

1. **"strip club is still a tad too dark... still be dark and moody, but lit
   enough for a player to see and experience it."** Comps: VtMB (a bar, the
   Asylum's hall, a poster wall) and a KOTOR 2 cantina, read for format only.
   - **Measured** (luma 0-255, HUDs cropped): our club frame mean 1.8, p50 1,
     98% under 10. VtMB bar mean 36.4, p50 15.3; VtMB hall 42.6, p50 38.7;
     KOTOR 2 38.6, p50 22.2; 19-40% of each comp is under 10.
   - So the den target is a median of about 15 to 39, with real darkness kept
     in the corners.
   - **The cause is in the rules.** Dens get no bake fills (Lux 0.68.2, the
     walker's "keep a bit dark"). The club is lit by `CLUB_WASH_LEVEL` 12
     washes in pools, plus stages, neon and the back bar.
   - **The format the comps show:** colored washes on walls, backlit
     shelves, downlight pools, glow strips, and a floor that reads.
   - **FIXED in Lux 0.72.0** (committed 2026-10-10, cold 9218 proving it):
     bake-only coloured washers on every wall + a fill in the room's own
     colour. Main floor p50 1 -> 8, VIP 0 -> 7. A WHITE fill was refused: it
     greys the office ceiling tile into a grid. Walker's calls queued: the
     brighter fill (4), a dark club ceiling (Deli Counter never sets one),
     a DEN floor in light_check. Sheet:
     `docs/findings/club_light_trials/walker_sheet_0_72_0.png`.
2. **"the windows in any 'den of sin' building should have curtains or
   drapes or blinds... people outside can't see in, and you keep the
   streetlight light out of the club."** Comp: a red-draped bar entry under
   a red neon sign.
   - **FIXED, committed 2026-10-09, not yet proven cold.**
     - Zoo 1.91.0 adds `window_drape`: velvet panels plus a pelmet,
       oxblood, both sides cloth.
     - Deli Counter 0.205.0 hangs one on every strip-club window and drops
       that window's light.
     - Frames: `docs/findings/den_drapes/`.
   - Painted Empty panes were the wrong tool: they are outside-only, over a
     hollow box.
   - **Trap, and its fix.** A drape is under `_HUNG_MIN` (1.8), so furnish
     counted and cleared it as a floor piece, and the library stopped being
     a fixed point. `_hung`/`_is_drape` now make furnish blind to it. A
     general foot-height rule would move 683 volumes.
3. **"far too many Sattelite/Attena that makes the rowhomes look a little
   too uniform and computer generated. perhaps 30% as many?"**
   - They are authored per house in `deli_counter/specs/gs_empty_rowhome_*`:
     `roof_antenna` on a, b, d, e, g, i, j and l, and `roof_dish` on b and
     k. That is 10 fixtures on 9 of 12 houses.
   - Every copy of an archetype repeats its roof.
   - 30% is about 3 fixtures.
4. **"street parking payment 'boxes' should face toward the sidewalk,
   rotating 90 Degrees".**
   - `lot/site_furniture.py` `plan_meters` passes `yaw_extra` 90.0 on both
     kerbs, so the face looks along the street. It needs a turn per side,
     facing away from the road.

5. **"i dont know what this giant grey box is".** `box_truck` is still Zoo's
   PLACEHOLDER SILHOUETTE: one solid box, parked by Lot as cover. Only it
   and `litter_bin` remain as placeholders, and both ship in club_block_014.
   Draw them the way the step van and the cruiser were drawn, with an
   invented Delco livery.
   **FIXED and PROVEN** (Zoo 1.92.0, Lot 0.103.0; cold 9219, 0 interventions):
   a cab-over in four invented fleets; at midnight its livery is lost in the
   moon's shadow, where the bake's bounce is blotched (roadmap 224).
6. **"newpaper stands inside of a bus stop thing and pole?"**
   `lot/site_furniture.py` `plan_furniture` adds `_bus_stop`'s pieces (the
   shelter, bench and flag) to `out` but not to `placed`. So
   `_stop_corner`'s `_free(...)` cannot see them, and a nudge (up to +/-4 m)
   put the news racks on the flag pole and the shelter's end post (9213:
   rack x 6.47 against the post at 6.58; rack edge 7.79 against the shelter
   end at 7.57).
7. **"moonlight seeps into building afar... as i walk forward that light
   goes away".** `delco_night.tres` has `sun_shadow_max_distance = 30.0`.
   Past 30 m the moon is unshadowed and lights rooms through their roofs;
   seen down the airport terminal's 38 m corridor. `lux_preset.gd` had
   claimed this was out of sight; refuted. The walker: "bake the moon, see
   how it looks" (`light_bake_mode` BAKE_STATIC on a copy).
8. **"a visually better/diagetic replacement for the permiter of the
   level, while maintaining the collision and signal to the player that you
   can't go outside of the playable area".** `perim_E` is a bare pale wall.
   The options are a menu with frames: barriers at street ends,
   slatted chain-link, hoarding, rowhome backs and alley walls, and a
   backdrop beyond. See [[fence-marks-the-playable-edge]] and
   [[backdrop-guide-filed-for-later]].
   **MENU FILED AND SENT 2026-10-10** with 12: `docs/findings/edge_menu/`, six
   options framed and priced (none moves frame time); recommended D, the
   chain-link fence + a tree belt + a sodium sky-glow. The walker picks.

9. **"stop lights are only bright for 1 color at a time, and if you have 2
   here, they need to be the same".** Every lens of both heads on a pole
   glowed. **FIXED in Level Factory 0.165.0** (committed 2026-10-09, not run
   cold).
   - The import gives each `M_TrafficSignal_Lens_<colour>` a lit shader on
     one 60 s clock: green 33 s, amber 4 s, red 23 s.
   - No per-node term: every head Lot stands faces the THROUGH road (tee and
     crossroads measured), so "cross street opposite" was moot.
   - Zoo shutters were rejected: a second UV set unbakes the whole model.
   - Proven in a Godot 4.7 probe (`docs/findings/signal_lenses/`).

10. **"need better looking fonts on these signs"** (strip_club_a01's "MOM
    THINKS I'M AT BINGO"). **DECIDED: "use Blue Highway for the shop
    signs". FIXED in Zoo 1.90.0** (committed 2026-10-09, not run cold).
    - **The photographed sign is ZOO's** `storefront_names.paint`: 9213's
      package shows `_card_atlas.build_art`'s material and no Pixelcoat pack.
      *First attributed here to `pixelcoat/core/signage.py`, which is wrong
      for this sign.* Pixelcoat letters the street band (and a door wearing
      it, LF 0.148.0) in Pixel Operator. That is still open, and it is
      Pixelcoat's own change.
    - **Shops are in Blue Highway CONDENSED.** I recommended it with the mock
      ("I'm building it with the weight as a single setting"); the walker did
      not object. It is one setting, `VOICES["shop"]`. **Civic fascias are in
      Aileron Bold**, my call from their catalog's owner rule. Both are worth
      a glance in the proof run's frames.
    - Findings are in `docs/findings/door_sign_type/`.

11. **"need filled black garbage bags stacked near the garbage bins"** (sent
    after the close). This is a new species, a filled bag and a heap of
    them, in Zoo. Lot places the heaps beside the dumpsters (one a building,
    at back or side: [[dumpsters-beside-buildings]]) and the cans.
    **FIXED and PROVEN** (Zoo 1.93.0, Lot 0.104.0; cold 9220): a heap beside
    each dumpster, on its pad. At midnight on the north walls the black bags
    are a black lump; light on the service side, and bags by the litter
    bins, are the walker's calls.

12. **"adding something in the background of our skyboxes to make the
    level not look like it's literally floating in space"** (after the
    close). A horizon backdrop beyond the edge; pairs with item 8.
    [[backdrop-guide-filed-for-later]]:
    `docs/reference/PENNSYLVANIA_BACKDROP_WORLDS_GUIDE.md`, 18 recipes.

**Item 7's trial, the moon baked** (copies of 9213, `_runs/moon_trial`,
sheet sent):
- **The seep is gone.** Down the corridor the centre goes 39.3 to 27.6.
- **Outside is much darker,** and the crisp shadows go:
  - spawn 47.5 to 31.1, extraction 29.3 to 18.2, signal 26.6 to 17.5;
  - the tree's shadow on a wall disappears; trees are kept dynamic and
    cast none into a bake.
- **Rooms move -2.3 to 0.**
- Not a drop-in. The options left: the cull-mask split (interiors on their
  own layer), a longer shadow reach (priced), or a baked moon with its
  energy raised.

The walker closed the round with item 10: "i think that's enough for this
round, thank you".

**How to apply:** fixes land in Lux, Deli Counter, Lot, Zoo and Pixelcoat, each proven in a
cold run of club_block_014 with frames. Tool repos stayed frozen while cold
runs 9215 and 9216 ran. See [[strip-club-comp-lou-turks]],
[[interiors-must-read-at-night]] and [[lighting-spec-filed]].
