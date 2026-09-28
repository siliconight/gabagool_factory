# More CC0 faces for the factory's lettering

PROPOSED. Nothing here is built. The walker, 2026-09-28: "I'm curious if we
can find other cc0 fonts to add to our factory to expand the looks and feels
(still being used by our toolset tho)". This records how a face gets in
today, what a candidate has to be, and a shortlist whose licences were read
at their primary source. It was researched read-only: no font file was
downloaded and nothing in a tool repo changed.

Scope, said plainly: every face is baked into textures at build time, so it
costs no frame time. It widens how levels look. It does not move
interventions-per-level.

## How a face gets in today

- **One face at runtime.** `zoo/tools/mint_pixel_type.py` loads a TrueType
  file with PIL (`:52-53`) from Pixelcoat's `signage.FONT_DIR`, hard-wired to
  `assets/fonts/pixel_operator/` (`pixelcoat/pixelcoat/core/signage.py:97-104`),
  renders each character at `PX = 16` (`:37`), and writes one table,
  `zoo_keeper/core/pixel_type_glyphs.py` (`:34`). `pixel_type.py` imports
  that one table (`:16`); `LINE`, `ASCENT`, `DESCENT` are module globals, and
  `render`, `width`, `wrap`, `fit_scale` take no face argument (`:18, 26-109`).
- **96 glyphs**: printable ASCII and ¢ (`mint:35-36`).
  `tests/test_vending_machine.py:305-309` re-mints and asserts the bytes.
- **What a candidate must be for that path**: a TTF/OTF PIL opens; drawn on a
  grid that renders pure on/off at exactly 16 px (a grey pixel stops the mint,
  `:70-72`; an 8 px grid passes as a doubled bitmap); whole-pixel advances
  (`:60-62`); no kerning (glyphs are laid at their advances,
  `pixel_type.py:48-56`). Bigger sizes are whole-number scales only.
- **A gap to close whichever face comes next**: the mint never checks the
  face actually has each character. A face without ¢ or lowercase would mint
  PIL's missing-glyph box and pass -- CLAUDE.md's "an unrecognised shape must
  fail" rule. It needs a character-map check.

Other lettering paths: Pixelcoat's signs snap to 16 px steps, uppercase, and
round grey to ink at 0.5 (`signage.py:104-164`); neon uses a private 5x7
bitmap turned into tubes (`zoo/.../neon_forms.py:13-50`); segment digits were
deliberately not added until "a second species wants segment digits"
(`register_forms.py:198-215`); and the pumps must stay mechanical price
wheels (`docs/proposals/GAS_STATION_SHOP.md:93-101`).

## What adding faces would take

- **A, a face parameter** (needed by every candidate): the mint takes a font
  file, a pixel size and an output module; `pixel_type` gets a face registry.
- **B**, the character-map check, and a per-face character set.
- **C**, a BDF / hex reader (plain text, no PIL). **D**, a PNG-sheet reader.
- **E, outline mode**: rasterise at a chosen size, round grey the way
  Pixelcoat does, handle or refuse kerning. Scale 2 is then an enlargement,
  not the face at 32 px.
- **F**: neon built from any `pixel_type` table instead of its private 5x7.

## The shortlist

Licences quoted from the primary source named. "Fit" is what the mint needs.

| Face | Author | Letters in the game | Grid | Licence, source | Fit |
|---|---|---|---|---|---|
| Pixel Operator HB / SC / 8 / Mono | Jayvee Enaguas | fascia and labels (SC), small print (8), price columns (Mono) | 16 / 8 | "CC-0", fontlibrary.org/en/font/pixel-operator | A |
| Modern DOS | Jayvee Enaguas | receipts, box print, CRT text, 1990s ads | 8x16, 9x16, 8x14 | CC0 1.0 per the author note; github.com/notpeter/ttf-moderndos | A (16-row) |
| Unscii 8 / 8-mcr / 8-fantasy / 16 | viznut | arcade and tech branding, card-shop posters, CRT | 8x8 / 8x16 | "the other variants are in the Public Domain", viznut.fi/unscii | A or C. Not `unscii-16-full` (GPL) |
| X11 misc-fixed 5x7 ... 9x15B | X.Org / Markus Kuhn | warnings, ingredients, price tags, receipts | per name | "Public domain font", cl.cam.ac.uk/~mgk25/ucs-fonts.html | C |
| m5x7 | Daniel Linssen | labels, price cards, small print | 5x7 | CC0 1.0, managore.itch.io/m5x7 | A (unmeasured). m3x6 / m6x11 are attribution, excluded |
| monogram | datagoblin | register tape, shelf tags | 6x9 | CC0 1.0, datagoblin.itch.io/monogram | A |
| Public Pixel | GGBotNet | bold packaging, slush and snack toppers | 8x8 | CC0 1.0, ggbot.itch.io/public-pixel-font | A |
| Home Video | GGBotNet | TV and VCR screens, 1990s ad panels | 20 px | CC0 1.0, ggbot.itch.io/home-video-font | A at 20 px |
| Digit Tech (segment) | GGBotNet | register customer display, clocks. Not the pumps | outline | CC0 1.0, ggbot.itch.io/digit-tech-font | E, B |
| Minisystem, Capacitor | Ray Larabie | register VFD -- the walker's "green font on a black screen" | outline | "The CC0 release has no licensing restrictions", typodermicfonts.com/public-domain/ | E |
| Fake Receipt | Ray Larabie | receipt curl, hoagie labels, lottery slips | outline | as above | E |
| Deftone Stylus, Sloe Gin Rickey, Fabian | Ray Larabie | neon, diner and club names | outline | as above | E (and F for neon) |
| Erratic Cursive, Crayon Libre | GGBotNet | hand-lettered price signs, banners | outline | CC0 1.0, ggbot.itch.io | E |
| BitScript; Dirty Hand | devurandom; qubodup | hand lettering at texel scale | low-res; 16 px | "CC0" on each OpenGameArt page | A (BitScript TTF); D (Dirty Hand) |
| Droid 1997, Vanilla Whale, Olivers Barney, Kingsbridge, Huxtable | Ray Larabie | condensed fascia and price cards; slab box and ad serifs | outline | typodermicfonts.com/public-domain/ | E |

Typodermic's page lists 307 CC0 releases and separates "that exact
public-domain font" from same-named commercial families. Take files only from
the public-domain page.

## Unverified, or where sources disagree

- **Kenney Fonts: the sources disagree, so hold off.** kenney.nl and the
  pack's License.txt say CC0; Kenney's own FontStruct pages label Kenney High,
  Mini, Pixel and Blocks "Attribution Share Alike". Worth resolving -- Kenney
  High would be the best CC0 condensed pixel face.
- **Tom Thumb** (3x5 micro face): relicensed from BSD-3 code with the
  original author's permission; CC0 is one of three offered choices.
- **Modern DOS** is extracted from IBM-era ROM fonts; the dedication is the
  converter's. The primary notabug repository was not opened.
- Read from the pages only, not from the files: which faces render pure
  on/off in PIL (only Pixel Operator has been measured), which carry ¢ or
  kerning, and the Typodermic faces' coverage.
- Excluded as not CC0: Dogica (OFL), m3x6 and m6x11 (attribution),
  Pixeloid and Kaph (OFL), unscii-16-full (GPL).

## Where to start, if this is taken up

A and B first -- a face parameter and a character-map check -- then two
faces the current mint takes as-is (Pixel Operator SC for condensed fascia,
m5x7 or monogram for small print), each measured through the mint before it
is trusted. The outline faces (E) are where the scripts, VFD digits and
hand-lettering live, and they are the bigger job.
