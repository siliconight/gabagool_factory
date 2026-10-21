# arena_a02's barriers as crowd rails (Zoo 1.118.0, Deli Counter 0.242.0)

**What was asked.** Roadmap 267 counted the library's prop slots that name no species and build as plain boxes. The
walker's look review of 2026-10-20 asked what arena_a02's four `barrier` volumes -- 3.0 x 0.8 x 1.2 m, in a line
across the event floor -- should be, and answered "Crowd rails (a new model)", not the concrete jersey barrier. So
Zoo draws a new species and Deli Counter routes the word to it.

**What the word claims** (`barrier_words.py`, `barrier_words_0241.out.txt`): `barrier` names exactly arena_a02's four
volumes in the library's specs and their four built slots, 3.0 x 0.8 x 1.2 long side first, no species. Nothing in
Level Factory's per-candidate specs or Deli Counter's furnish names one. `level_design`'s cover tagger reads the word
as cover (`_COVER_NAME_HINTS`).

## The species (Zoo 1.118.0, `patches/zoo_crowd_barrier/`)

`crowd_barrier` is one panel of the interlocking steel barricade crowds stand behind at an arena's gates: a welded tube
frame on two flat feet, pickets between its rails, hooks at one end that drop over the next panel's leg. Its numbers
are the common fabricated sizes, since no code governs a barricade: 1-1/2 in legs, 1-1/4 in rails, 3/4 in pickets at
5-1/4 in clear -- fourteen to the 7.5 ft panel -- the bottom rail 8 in up, 24 in flat feet. The genome's defaults are
that panel, 7.5 ft x 43 in; its ranges hold arena_a02's slot. `core/crowd_barrier_forms.py` argues each choice:

- **Eight-sided tubes**, because Zoo's export smooths a fold under 50 degrees: eight read round, six read as bar.
- **No face on another's, and no open end showing.** Pickets and hook arms turn a sixteenth of a circle; every tube
  end left open sits inside the member it runs into and is narrower than that member's flats.
- **One material, one part, one submission:** galvanised steel, `metal_bare`, the chain-link fence's grey.
- **Collision: the panel.** The feet are under any step.

Measured: 348 / 412 / 508 tris at the genome's corners (476 at arena_a02's), 0 coincident pairs in Blender's census
with the bollard as the control; arena_a02's four slots through `zoo_cli --build-kit` build one module, one mesh, one
primitive, one material, its bounds the slot's exactly. 520 is the budget, the standard's small-clutter class.

## Two decisions, both changeable

**The kind.** Zoo's kit keeps a slot's known kind even when the genome does not offer it (`dna.resolve_module_plan`):
built from the spec's `metal`, the barricade came out `prop_crowd_barrier_..._mmetal`, in `M_CrowdBarrier_metal` --
the theme's metal pack, not the galvanised grey (`patches/zoo_crowd_barrier/kit_metal.log` and
`kit_metal_glb_facts.out.txt`: the same four slots in the spec's `metal`, against `kit.log` and `kit_glb_facts.out.txt`
in `metal_bare`). Deli Counter's rule for this is the dartboard's (`level_design.
_PROP_MATERIALS`): a piece asks for its species' own kind. Deli Counter 0.242.0 writes the four volumes in
`metal_bare`, and the stem carries no `_m`.

**Declaring the kind, and where.** Renaming the volumes' kind alone was the first cut, and the library build answered
"UNRESOLVED MATERIALS in 'arena_a02': metal_bare x4": a kind the spec does not declare builds with no acoustics and
the building's default skin style (`patches/dc_crowd_barrier/record_moves.out.txt`). The second cut declared it after
`metal`, and the rebuilt slots moved 50 styles (`record_moves_declared_after_metal_REFUTED.out.txt`): a slot's style
is its material's place in the palette, and `floors.ensure_finish_palette` appends carpet, tile, ceiling_tile and
plaster after the authored list, so anything declared before them pushes them on. Shipped: arena_a02 declares those
four itself, in the finish palette's order and values, then `metal_bare` last. Its rebuilt records move in exactly the
four barriers -- species, kind, style 4 -> 10 -- and their four surfaces' acoustics (`record_moves_final.out.txt`);
Zoo plans them `prop_crowd_barrier_delco_1997_10_w300_d80_h120` and builds it from the real slots as the same module
the kit record built under `_04_` (`patches/dc_crowd_barrier/kit_real_slots.log`).

**The collider, and the cover.** The four volumes keep the convex 3.0 x 0.8 x 1.2 box the composer keeps in the
greybox, so the barriers block bodies, sight probes and shots exactly as the boxes did, and the cover tagger still
reads them as cover. A barricade you can see through that stops a shot is a mismatch a player can notice. Whether a
shot should pass between the pickets is the gameplay layer's (a collider that stops bodies and not shots) and the
walker's call; nothing here changes how a level plays.

## The level that shows it

No cold run had placed arena_a02. Level Factory's own `lot_for_brief` over 400 seeds of the club brief
(`find_arena_seed.py`, `find_arena_seed_9000_9400.out.txt`) found five whose lot stands it; seed 9014 draws
strip_club_a01, arena_a02 and card_shop_a01, and cold run 9358 drew exactly that. 9358 is the control, on Zoo 1.117.0
and Deli Counter 0.241.0; 9359 the same seed on 1.118.0 and 0.242.0.

## The frames (`compose_frames.py`)

Five given stations along the barrier line (`tools/look_shots.py --station`, site metres, the arena at site
(-2, 0, -4.01) unturned): `close_hook` (barrier_1's hook end from 2 m), `near` (3 m), `normal` (6 m), `far_line` (the
four from 10.5 m) and `far_side` (from across the line), each in the inspection light (`--inspect studio`, what is
there) and the level's own night light (how it is lit). `barriers_9358_vs_9359_inspect.jpg` and
`barriers_9358_vs_9359_lit.jpg`: the control's box beside the crowd rails.

- In the inspection light the rails read at every distance -- the frame, eighteen pickets, both hooks -- and the
  cartons stacked behind barrier_1, which the box hid, show between the pickets.
- In the level's own light this arena's event floor is all but black at night, box and rails alike: its troffers
  light the ceiling 5.5 m up and little reaches the floor. Not this change's; a question for the walker.
- **The feet were missing.** Deli Counter lays a room's floor finish as a 2 cm skin over the slab and stands every prop
  on the slab under it (`floors.SKIN_THICK`); 1.118.0's 9.5 mm flat-bar feet lay wholly under the carpet, and the legs
  stood planted in it -- a barricade that could not stand. Zoo 1.118.1 draws the feet as 2 x 1-1/2 in rectangular
  tube, 1.8 cm proud of the skin (`patches/zoo_crowd_feet/`). Any prop whose ground detail is thinner than 2 cm loses it
  the same way in a Deli Counter building; nothing else measured here shows it.
- Cold run 9360 framed 1.118.1 at the same stations (`feet_9359_vs_9360_inspect.jpg`): each barricade stands on its
  two tube feet, clear of the carpet.

## Re-scoped by the walker: the barricades go outdoors, the arena gets a queue

Shown the feet, the walker asked "what are these crowd barriers for....concerts?", chose "queue lanes to the box
office", and then: "stanchion or stanchions are likley more common for banks and indoor common areas", "metal barriers
are for outdoor concerts or riot protection from police", "retractable belt stanchion" (with a photo). So the steel
barricade is the outdoors' -- Lot's, for an outdoor concert or a police line, not yet placed anywhere -- and Zoo 1.119.0
(`stanchion_run`) and Deli Counter 0.243.0 (`ticket_queue`) take arena_a02's four off its event floor and lay the box
office's queue in retractable-belt stanchions: `docs/findings/ticket_queue_267/`. `crowd_barrier` stays a species and
the word `barrier` still routes to it.
