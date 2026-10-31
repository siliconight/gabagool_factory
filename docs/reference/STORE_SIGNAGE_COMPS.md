# Store signage comps (the walker, 2026-10-31)

The walker, on the vertical slice's shop signs: "store signage still looks...wrong...look at these example/comps",
then "Neon is also fun", "liquor store should have neon beer company signs", "bars should have neon beer company
signs inside (we still need to make a dive bar)", and what to fix: "placement, size of font, neon, better/more varied
CC0 fonts". Three photographs came with it, described here (the images themselves were not filed). They are
REFERENCE ONLY: every name, logo and brand a tool draws stays invented (`fake-delco-brands`: Delco slang, PG-13, never a
real mark -- the photos' beer brands are exactly what must not be copied).

## What the three photos show

**1. A liquor store by day: a painted panel on a red metal mansard.** A long white panel sign runs the whole length
of the shop's frontage, mounted on the face of a red corrugated-metal mansard canopy that overhangs the walk. The name
is in heavy, idiosyncratic display capitals -- a stencil-like hand of its own, not a stock sans -- filling about two
thirds of the panel's height; two panels butt at a visible seam, and the white is grubby. Below the canopy: a
painted brick wall with a ribbon of windows, and every window pane is full -- neon beer logos hung in the glass
(script and bold lettering in red, blue, white and yellow tube), backed by printed beer posters and banners. Graffiti
tags on the glass. A tree overhangs the sign.

**2. A liquor store at night: neon channel letters.** Over a fully glazed, brightly lit storefront, the name stands
as individual neon letters on a dark fascia band: the owner's name in a flowing script ringed by a border of marquee
bulbs, then the word LIQUOR in tall block capitals, each letter its own glowing tube. The sign is the brightest thing
in the frame, and it lights the fascia under it. The shop window is crowded with price posters and beer displays; a
payphone and an ice chest stand by the door.

**3. A roadside liquor store at dusk: rooftop letters and a pole sign.** A small flat-roofed shop with its name in
individual neon letters standing ON the roof edge, set above the canopy, glowing warm white-yellow against the sky;
by the road a tall pole sign in the shape of a stacked oval/arrow with the name again and a ring of bulbs. The whole
front is windows, lit warm from inside and hung with displays.

## What our signs do instead (slice 28, Lot 0.140.0, Pixelcoat 0.68.0)

Every business wears the same object: Lot's `_sign_node`, a dark box 0.22 m deep with Pixelcoat's sign pack printed
on a quad in front -- one condensed sans (Blue Highway), one colour, centred on a solid field with a thin border, at
6:1. It hangs at a fixed `SIGN_Z` 3.6 m whatever the building's height (on a low shed it rides above the wall top),
centred on the footprint's street side rather than over the door or the glazing, at 72 % of the facade capped at 9 m
(a plaque on a 50 m front). The `neon` style is a flat texture too. Window neon exists (Deli Counter
`migrate_window_sign`, Zoo `neon_sign` `window` form, invented beers in `club_names.WINDOW_NAMES`) -- one per
convenience store, its tubes following a 5x7 pixel font's skeleton, so it reads as dot-matrix, not as bent glass.

## What the comps ask of the tools, in order

1. **Placement and size.** A shop's name runs across its frontage on the fascia over the storefront -- between the
   head of the ground floor's glazing and the eave or parapet -- or stands on the roof edge, or on a pole by the road;
   never floating above a roof line, never a plaque on a long front. Letter height is the band's, about two thirds.
2. **Letters with depth.** Channel letters (each letter its own extruded can, a lit face, dark returns) and painted
   panels with seams and dirt -- not a printed rectangle.
3. **Neon.** Tube lettering drawn as one continuous stroke along each letter (a single-stroke font is the shape),
   script and block together, a bulb border on some; it is the brightest thing in a night frame and colours the wall
   under it (a baked light: no runtime cost).
4. **Varied type with an owner, by kind of store.** The walker: "different kinds of stores should have different
   fonts/signage to provide variety". A script, a heavy display face, a neon-tube sans, a tavern slab -- each kind of
   business its own sign type and voice (the bar and the diner in neon, the liquor store and the deli on a painted
   panel, the bank and the chain market in a lit cabinet or channel letters), and the font catalog's rule: every
   typeface has an in-world owner.
5. **Beer neon in the windows** of a beer distributor or liquor store, and **inside a bar** -- invented beers, many
   per front, with posters behind; the dive bar (The Wooder Hole) is still to be built.

## The walker's sign rules (2026-10-31, pasted from a guide on store signs and logos)

What a good store sign does, as the generator must do it (paraphrased; the guide's sources are sign-industry blogs):

* **Legible at a glance, at a distance:** high contrast between letters and field; letters big enough for the street
  -- the commonest failure is text too small or too low in contrast. A clean, heavy face reads best from a car.
* **Succinct:** the business's name, and at most a two-to-three-word descriptor of what it sells ("BEER - ICE - KEGS").
* **Scaled and placed to the architecture:** the name the anchor of the frontage, sized to the building, where trees
  and poles do not block the sightline (Lot already keeps its poles and trees out of a sign band: `sign_bands`).
* **Lit and dimensional:** illuminated, three-dimensional lettering in weather-proof materials over flat print.
* **A logo that is simple, memorable and fits the trade:** one distinct shape or detail; works in one colour.
* **Limited palette and type:** one or two faces a sign, colours chosen for the trade (blue for a bank's trust, green
  for growth) -- variety comes from different businesses having different voices, not from one sign having many.
