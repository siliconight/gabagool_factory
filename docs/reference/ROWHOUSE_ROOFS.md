# What a rowhouse roof is made of (roadmap 240, the roofscape)

Filed 2026-10-12, when the walker asked of the "silver roofs" on roadmap 240: "where are you getting
that from vs. concrete? ... silver doesn't seem like a material for rooftop, perhaps aluminum but I'd
want to ground that in something first". The walker's call after reading this: **tar now, the coating
later** -- Deli Counter 0.210.0 roofs the rowhome Empties in `tar`; the aluminum coating waits for a
source on the 1990s.

## Where "silver" came from, and "concrete"

- **"Silver"** was a description, not a source: the factory's reading of the walker's aerial comp of
  2026-10-11 ("Their roofs are FLAT and most are SILVER or WHITE coated, some black tar",
  `docs/reference/PHILLY_STREET_COMPS.md`; the photograph was not stored), and a comment in Deli
  Counter 0.175.0 ("A 1990s rowhouse roof is flat tar, silver-coated") that cited nothing.
- **"Concrete"** was what the code did: `presets.empty_rowhome` set `roof_material = "concrete"` under
  that comment. In the delco themes Pixelcoat skins `concrete` as `concrete_delco`; under `street` as
  `cinderblock_delco`, a block wall with mortar lines. Every other roof in a delco level was already
  `tar`, Zoo's roof default for the theme (`zoo/zoo_keeper/genome/species/roof.json`).

## What the sources say

- **The material is a membrane, and "silver" is a coating on it.** Roof coatings sold as silver are
  asphalt carrying aluminum flakes, made for asphalt built-up roofs and modified-bitumen membranes: the
  flakes "leaf to the surface to reflect over 50% of the sun's rays" ([Karnak 97AF][karnak]); Garland's
  Silver-Shield claims under-roof temperatures down "up to 15°F" ([Garland][garland], a maker's claim);
  Barrett's Ram Ultra-Silver is SBS-modified asphalt for modified membranes ([Barrett][barrett]).
- **Philadelphia rowhouses: weak, and modern.** A roofer's sponsored article lists modified bitumen
  among the city's common flat roofs ([PhillyVoice, sponsored][phillyvoice]); a row-house renovation
  guide recommends a WHITE coating on the bitumen ([Designblendz][designblendz]); a Philadelphia row-home
  owner with a 2015 rubber (EPDM) roof asks whether "a silver coating" can stand in for ventilation
  ([Green Building Advisor][gba]). None of these is about the 1990s.
- **White roofs are mostly after 2010.** Philadelphia's cool-roof law, signed May 2010, requires
  reflective roofs on new low-slope construction ([Architect][architect]; [EP Online][eponline], the
  "Coolest Block" contest the same month). A modern aerial's white roofs are likely later than 1997.

## What is not grounded

How many Philadelphia rowhouse roofs carried an aluminum coating in the 1990s -- the question the
coating waits on. A way to answer it: 1990s USGS black-and-white aerial photographs of Philadelphia
rowhouse blocks, where a coated roof reads bright and bare tar dark (a download, so the walker's yes
first).

[karnak]: https://superarbor.io/products/karnak-97af-fibered-aluminum-roof-coating-reflective-silver-1-gal-can
[garland]: https://media.garlandco.com/m/7b86b377c4119163/
[barrett]: https://www.arcat.com/product/ram-ultra-silver-roof-coating-220067
[phillyvoice]: https://www.phillyvoice.com/choosing-right-philadelphia-area-roofing-company-05999-969/
[designblendz]: https://www.designblendz.com/blog/historic-row-house-renovation-dont-touch-that-hammer-until-you-check-out-these-must-read-tips-0
[gba]: https://greenbuildingadvisor.com/question/philadelphia-row-home-roof
[architect]: https://www.architectmagazine.com/technology/philadelphia-adopts-cool-roof-law_o
[eponline]: https://eponline.com/articles/2010/05/18/wolf-street-block-wins-cool-roof-philadelphia-aims-to-be-greenest.aspx
