# Window displays: the walker's music-store comps, and what each tool owes them

The walker, 2026-10-08:

> For later, I want to add to the roadmap the ability to create certain
> buildings with a Window Display on the front, we can start with a
> Guitar/Music Store

Six photographs came with it. They were shown in chat and are not stored
here. What follows is what was read off them -- format only. The stores, the
neon words' makers, and every mark on the instruments, amplifiers and posters
are real, and none is reproduced. Roadmap 209 tracks the work.

## WHAT A WINDOW DISPLAY IS

A shop window treated as a stage, not as glass onto the selling floor:

- **A riser** across the window's foot, one or two steps, carpeted -- or a
  white cloth thrown over boxes, in one comp. Instruments stand along it on
  floor stands, their bodies to the glass.
- **A back that carries more.** Guitars hang by their headstocks on a dark
  wall or slatwall, in a row or a grid. Amplifier heads and cabinets stack
  behind, and a poster hangs at the back.
- **Words in the glass.** Neon hangs inside the window -- a script word over
  a block one, "GUITARS", "BASSES", "ACOUSTICS" in the comps, one in a clear
  frame. One window carries gold script lettering on the glass itself.
- **Light.** The display is lit: track spots or downlights over it, and at
  night the window is the brightest thing on the street. Two of the comps
  frame each window in a coloured neon outline tube.
- **Clutter that says it is a shop.** Price tags hang from the headstocks,
  a pedal or two sits on the riser, a small practice amp on the floor, and
  flyers are taped inside the door.
- **Depth.** The selling floor shows behind it -- shelves, more guitars on
  the walls -- so the display is a layer in front of a room, not a picture.

## THE SIX COMPS

1. **A two-storey music store at night.**
   - Upstairs: three display windows full of acoustic guitars hung in rows,
     with a neon script sign in the middle one.
   - Between the floors: a sign band with the store's name in large block
     capitals.
   - Downstairs: two display windows framed in coloured neon tube, electric
     guitars on stands in tiers on one side and basses under a neon word on
     the other. The entry door is at the side.
2. **One ground-floor window by day.** A neon word over a script word hangs
   in a clear frame inside the glass. Electric guitars stand on a two-step
   carpeted riser with a pedal on the step and a figure at the back. The
   frame is outlined in neon tube, and the street is reflected.
3. **The first store's upper floor, straight on at night:** three windows,
   each framed in coloured neon, acoustic guitars hung in a grid, and the
   sign band under them.
4. **A window of electric guitars** hung in two rows by their headstocks
   behind a neon word, with a parked car reflected in the glass.
5. **A daytime window.**
   - A row of brightly coloured electric guitars on floor stands across the
     front, and more hung above against a dark wall.
   - Amp heads and cabinets stacked behind, and a poster at the back.
   - Price tags, and gold script on the glass.
6. **A night window.** A white-draped riser with guitars on stands across
   it, more guitars hung on slatwall above, track spots on the ceiling, the
   shop's shelves behind, and flyers in the door.

## WHAT EXISTS TODAY (read 2026-10-08)

- **Deli Counter's storefront.** It is a storey-0 exterior wall of
  `storefront_glass`, built modular, its slots tagged
  `glazing: "storefront"` (0.153.0) and glazed see-through by Zoo (1.18.0).
  The room behind is lit from outside through it (0.157.0). The window bay
  itself holds nothing: pieces are kept clear of shop windows, for example
  the slush machine's migration.
- **Zoo** has no instrument species. The nearest pieces:
  - `neon_sign` (`core/neon_forms.py`);
  - `video_rack`, a spines-out tall aisle;
  - `pack_wall`, slatwall stock, with `slatwall` already a material kind;
  - `display_case`;
  - `poster_wall` and `poster`, which already fill store windows;
  - a crude guitar icon in `poster_art`, used for flyers ("GUITAR
    LESSONS").
- **No building family** in Deli Counter's library is a music store.

## WHAT EACH TOOL OWES IT (to be confirmed against the code)

- **Deli Counter: the window bay as a zone.**
  - The first metre or so behind a display storefront becomes its own
    zone, with slots for a riser, a back, hanging rails and words in the
    glass.
  - A music-store family whose front carries display windows. Two storeys
    of them in comp 1, with a sign band between.
- **Zoo: the instruments, made the way the draw-call rule wants.**
  - **Guitars** in their forms (solid body, single-cut, semi-hollow,
    acoustic, bass), on a floor stand or hung by the headstock.
  - **Draw calls.** A window of twelve guitars in twelve colours is ONE mesh
    with its colours in the vertex, never twelve materials.
  - **The rest of the window.** Amp heads and cabinets, a riser (carpeted
    or draped), price tags, pedals.
  - **Neon words** from `neon_sign`, with a neon outline around the frame.
- **Lux: the window lit as a display.** Spots over the riser, the neon's
  glow, and the window as the street's brightest thing at night. Within
  `max_lights_per_object` (8), and priced the way the performance contract
  asks.
- **The name.** An invented Delco music store on the sign band, under the
  fake-brands rule: never a real store's name.
- **Lot and Level Factory.** The store fronts the street, which Level
  Factory 0.132.0 already turns every front door to.
