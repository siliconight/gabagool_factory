# CC0 Fonts for Human-Authored Games

*A practical, source-checked font catalog for games made in Godot, Blender pipelines, and other engines*

## What this guide means by “not AI-looking”

A font license cannot tell you whether a design was made by a person, and a typeface does not become soulful just because it is irregular. For this guide, “not AI-looking” means a type choice that feels deliberate, legible, and rooted in a recognizable design purpose: a period of printing, a kind of sign, a machine interface, a local business, a printed book, or a specific fictional institution.

The list below is vetted first for a source that explicitly identifies the font or pack as **CC0**. It is then screened for practical game use and distinctive typographic character. “Vetted” does not mean every entry has been visually tested at your exact resolution, nor that every creator has made a no-AI statement. The CC0 license and human-authorship provenance are separate questions.

For a grounded, handmade game world, the useful move is usually to give each text a believable owner and job: a shop sign should look like that shop paid someone to make it; a police form should look like a form; a machine label should follow the manufacturer’s visual system. Do not spread a decorative font over every object just to make the world feel varied.

## Fast shortlist

| Need | Start here | Why it earns a test | Watch for |
|---|---|---|---|
| Main UI / menus | **Aileron**, **Vegur**, **Marius1** | Flexible sans families; Aileron has many weights, Vegur has a humanist sans character, Marius1 has broad Latin, Greek, and Cyrillic coverage listed | All need a specimen test at your game’s actual UI size; do not use every available weight |
| Long readable lore / documents | **MFB Oldstyle**, **Seshat Regular**, **Tenderness** | Serif forms suggest printed matter and give menus, books, notes, and paperwork a different voice from the HUD | Check punctuation, accented glyphs, and paragraph texture at small sizes |
| Pixel-game interface | **Pixel Operator**, **Public Pixel Font**, **SG Font Collection** | Designed around pixel grids or bitmap display use, with multiple styles and/or language coverage | Pixel fonts become noisy if used for long paragraphs or mixed with arbitrary scaling |
| Period computer / arcade text | **C-64 Font**, **Kenney Fonts**, **Public Pixel Font** | Clear retro-computing or compact bitmap cues | Use as a system voice, not a universal “retro” filter |
| Distinctive title / faction mark | **Ferrum**, **Medio**, **Not Jam Blackletter 13**, **Not Jam Third Dimension 15** | Strong display silhouettes for a narrow, authored role | Title-only. Test trademark / franchise resemblance, readability, and whether the world plausibly uses it |
| Quiet secondary signage | **Penna**, **Thin Sans**, **Not Jam UI** | Useful alternatives when the leading UI face should not dominate every label | Their distinct proportions can become tiring at small sizes; check screen captures |

**Good first test for a 1990s urban setting:** Vegur or Aileron for system UI, MFB Oldstyle for letters and readable found text, C-64 or Public Pixel for a specific old terminal, and one locally plausible display face for a shop, club, or service business. Make each choice belong to an institution or object; do not turn all signage into “retro typography.”

## Catalog A: broad-use and editorial faces

The pages linked below show CC-0 in Font Library’s license metadata. That catalog is a useful discovery source; re-check the exact download’s included license and version before shipping.

| Font | Best roles | Character and practical notes | Source |
|---|---|---|---|
| **Aileron** | UI, menus, labels, captions | Sora Sagano family with 16 listed styles, from Thin through Black and italics. Its range can carry hierarchy without introducing several unrelated fonts. Prefer Regular/Medium/Semibold for small text; reserve extremes for specific emphasis. | [Font Library: Aileron](https://fontlibrary.org/en/font/aileron) |
| **Vegur** | UI, signage, headings | Sora Sagano describes it as a humanist sans; three styles are listed. A restrained, less mechanically neutral choice for interfaces and ordinary signs. Check glyph coverage: the catalog flags some Western European characters as missing. | [Font Library: Vegur](https://fontlibrary.org/en/font/vegur) |
| **Marius1** | UI, multilingual labels, signage | Sans-serif, with Basic Latin, Greek, Cyrillic, and a broader set of language groups listed. The catalog provides little design description, so inspect its specimen before assigning it a major role. | [Font Library: Marius1](https://fontlibrary.org/en/font/marius1) |
| **FifteenTwenty** | UI or signage after a specimen test | Nine styles are listed. The catalog’s description is sparse; treat it as a candidate rather than a guaranteed recommendation. Check its shapes and metrics before layout. | [Font Library: FifteenTwenty](https://fontlibrary.org/en/font/fifteentwenty) |
| **Penna** | Short labels, storefronts, compact headings | Sora Sagano’s geometric sans has oversized uppercase counters and a small x-height. That proportion gives it character, but small x-height can make little UI text feel tiny. Basic Latin only in the catalog. | [Font Library: Penna](https://fontlibrary.org/en/font/penna) |
| **Tenderness** | Notes, book pages, title cards | Sora Sagano serif, loosely inspired by Garamond and Optima, with old-style figures. A natural fit for printed or literary text. Basic Latin only. | [Font Library: Tenderness](https://fontlibrary.org/en/font/tenderness) |
| **Seshat Regular** | Documents, lore, book text | Sora Sagano roman serif with ligatures. The catalog lists Basic Latin, Dutch, and Euro support, but flags missing Ð, Þ, ð, þ in its Western European coverage. | [Font Library: Seshat Regular](https://fontlibrary.org/en/font/seshat-regular) |
| **Medio** | Editorial headings, menus, labels | Sora Sagano serif based on Tenderness proportions, with Didone-style hairline serifs. The thin strokes can disappear at small sizes, under bloom, or on rough textures; keep it for larger text. Basic Latin only. | [Font Library: Medio](https://fontlibrary.org/en/font/medio) |
| **Ferrum** | Fantasy / ceremonial title marks | Sora Sagano small-caps serif, extra-condensed in its specimen and explicitly inspired by the Final Fantasy series logo. Keep it to a narrow fictional role, and avoid copying that franchise’s recognizable logo treatment. Basic Latin only. | [Font Library: Ferrum](https://fontlibrary.org/en/font/ferrum) |

## Catalog B: pixel, bitmap, and game-facing fonts

### Pixel Operator

A 15-style family by Jayvee Enaguas (HarvettFox96), listed as CC-0 by Font Library. It includes variants such as Pixel Operator 8 and SC. Test each actual file: styles and glyph support differ. Strong candidate for a deliberately pixel-based game interface, status readouts, or a particular machine. Avoid putting it on every in-world sign just because the game has a retro influence.

[Font Library: Pixel Operator](https://fontlibrary.org/en/font/pixel-operator) · [Creator’s repository](https://notabug.org/HarvettFox96/ttf-pixeloperator)

### SG Font Collection

The creator describes this as a free CC0 pack of 19 TTF pixel fonts for games and websites. The page names the following entries and notes that starred styles support Greek, Cyrillic, and Hebrew; its listing shows 17 names while the pack description says 19, so inspect the download for the full inventory.

- Pixel Sans
- Blocky Pixel
- Micro Pixel
- Superwide
- Nano Square
- Nano Bits
- Nano Plus
- Impactful Bits
- Retro Sans
- Scroll Pixel
- Canned Pixels
- Chibi Mono
- Narrow Pixel
- Rune Mono
- Quest Square
- Royalty Mono
- Attomic

Use the names as a visual shortlist, not as a promise of specific readability. The creator’s specimen sheet and the font files should decide which one fits your actual screen scale.

[SG Font Collection](https://spicygame.itch.io/fonts)

### Not Jam Font Pack

The creator’s page says this is a free CC0 TTF pack for games and lists these families. **Inventory note:** the page says “28” fonts, but the numbered list runs from 1 through 29. Verify the current archive and per-font pages before treating the package as a fixed inventory.

- Not Jam Blackletter 13
- Not Jam Chunky Sans 6
- Not Jam Chunky Sans 8
- Not Jam Faithless 9
- Not Jam Glasgow 13
- Not Jam Laika 11
- Not Jam Old Style 11
- Not Jam Pixel 5
- Not Jam Sci Mono 10
- Not Jam Scrawl 9
- Not Jam Serif 11
- Not Jam Signature 17
- Not Jam Slab Serif 11
- Not Jam Third Dimension 15
- Not Jam Toolkit 15
- Not Jam UI 12
- Bore Blasters 16
- Not Jam UI Condensed 16
- Undead Pixel Light 8
- Not Jam Mono Prophet 8
- Not Jam Play 19
- Not Jam Mono Clean 8
- Not Jam Atomic 20
- Not Jam Old Peculiar 8
- Not Jam Mono Clean 13
- Not Jam Giant UI 22
- Not Jam Mono Casual 10
- Not Jam Mono Crooked 8
- Not Jam Novel 13

The creator marks some entries as supporting extended Latin, Cyrillic, or monospaced use. The pack page explains those markers. Pick by specimen and role: UI / UI Condensed / Giant UI for interface trials; Old Style / Serif / Novel for printed text; Scrawl / Signature for brief handwriting props; mono entries for terminal-like content. Do not set long UI text in a novelty face.

[Not Jam Font Pack](https://not-jam.itch.io/not-jam-font-pack)

### Kenney Fonts

Kenney’s official asset page lists **11 files** and explicitly labels the pack Creative Commons CC0. It is a reliable place to test straightforward game-oriented pixel and display lettering. The public listing does not identify the individual font filenames, so use the downloaded archive as the inventory and keep the license file with it.

[Kenney Fonts](https://kenney.nl/assets/kenney-fonts)

### Other individually listed pixel fonts

| Font | Best role | Notable notes | Source |
|---|---|---|---|
| **Public Pixel Font** by GGBotNet | Tiny monospace HUDs, terminal text, compact labels | CC0; creator page says 1,324 glyphs, an 8×8 monospaced grid, and support for 98 languages. Suggested pixel sizes are 8, 16, 32, 64, and 128. Excellent coverage claims still need a game-language test. | [OpenGameArt: Public Pixel Font](https://opengameart.org/content/public-pixel-font) |
| **C-64 Font — Free** by Jamie Cross | Commodore-style screens, game props, title cards | CC0, two versions (solid and pixel-style), 98 glyphs each. The creator’s page says the design is based on the Commodore 64 character set and is marked “No generative AI was used.” Treat it as an intentional C64 reference, not generic 1990s body text. | [C-64 Font](https://jamiecross.itch.io/c-64-font-free) |
| **Thin Sans (Latin 2)** by enekoatxa | Clean small pixel UI, counters, short labels | CC0, TTF and OTF, 242 Adobe Latin-2 characters. The creator labels the page “No AI” and says no generative AI was used. It is inspired by the thin clean font in *Balatro*, so avoid duplicating that game’s complete visual identity. | [Thin Sans](https://enekoatxa.itch.io/thin-sans) |
| **Pixel Font — Free** by Devil’s Workshop | Retro game headers and short in-game copy | CC0, classic thick-thin pixel style, ASCII character set. The creator says to avoid mipmaps for sharp rendering and lists Godot among compatible engines. | [Pixel Font — Free](https://devilsworkshop.itch.io/pixel-font) |

## Catalog C: print, books, and authored documents

### MFB Oldstyle

A particularly useful fit when the game contains letters, ledgers, newspapers, manuals, menus, or readable found documents. Daniel Benjamin Miller’s digital family revives Century Oldstyle, originally designed by Morris Fuller Benton in 1909. The repository includes Regular, Italic, and Bold and identifies its license as CC0-1.0. Its old printed lineage gives you a real typographic story to build around; do not use the same face for the whole HUD just because it looks “classic.”

[Project repository and license](https://github.com/dbenjaminmiller/mfb-oldstyle)

### More print-like options

- **Seshat Regular** — serif with ligatures; good for in-world documents and book text. Check the missing thorn/eth glyphs before localization.
- **Tenderness** — old-style serif; good for notes, menu text, and printed matter with a slightly literary tone.
- **Not Jam Old Style 11**, **Not Jam Serif 11**, **Not Jam Slab Serif 11**, and **Not Jam Novel 13** — candidates within the CC0 Not Jam pack. View the pack’s specimens; the names alone do not guarantee long-text quality.
- **Medio** — title-sized only, where its hairline serifs survive the display conditions.

## What “human-made provenance” is actually documented

The source pages explicitly state that no generative AI was used for **C-64 Font — Free** and **Thin Sans**. Those are creator-page claims, useful as provenance notes, not independent audits. The other catalog entries are included because their listed source identifies them as CC0 and their design/use makes them worth testing; I am not asserting that every creator made a public no-AI statement.

CC0 says something about the rights the creator is dedicating or waiving. It does not certify authorship, artistic quality, originality, trademark clearance, or visual fit. Likewise, a hand-drawn-looking typeface is not automatically a human-made font. If no-AI provenance is a hard requirement for a particular asset, keep a record of the creator’s statement or contact the creator; do not infer that status from the style.

## Typeface rules that keep a game from feeling assembled from a font dump

1. **Assign a typeface to an owner.** The transit agency, pawn shop, hospital, gang, motel, computer terminal, and player HUD should not all sound like one designer picked a trendy font menu.
2. **Use few families and many real functions.** A practical project might have one UI sans, one readable serif for documents, one pixel/mono face for a specific device, and occasional one-off display lettering. Each extra face needs an in-world reason.
3. **Make hierarchy with size, weight, spacing, and placement before adding another font.** A larger line, a stamped date, a narrow column, or a bold label often carries more story than a random alternate typeface.
4. **Do not use novelty fonts as body copy.** Blackletter, scrawl, signature, 3D, chunky pixel, and highly condensed faces work best in short phrases. Keep notes, dialogue, and settings readable.
5. **Keep type aligned to the object that carries it.** Labels should respect panel edges, seams, screw heads, handles, and viewing angle. Text should not float above a surface or collide with a bevel unless that is a deliberate production artifact.
6. **Respect physical production.** Screen print, thermal receipt, label maker, stencil, letterpress, vinyl cut, hand paint, and photocopy have different edges, spacing, ink density, and limits. Use one coherent method per object; do not apply a generic grunge overlay to every letter.
7. **Avoid automatic distress.** Dirt and damage should follow handling, weather, sun exposure, cleaning, and placement. Preserve readable counters and critical words. A pristine decal beside a damaged panel needs a reason, such as a recent replacement.
8. **Avoid fake irregularity as a substitute for authorship.** Random kerning, random rotation, arbitrary capitalization, and randomized placement look like effects. Let the material, owner, use, and history explain variation.
9. **Keep real spacing.** Check word spacing, line spacing, margins, alignment, and optical balance at final size. Do not set every in-world title in tracking so wide it looks like a synthetic “cinematic” treatment.
10. **Limit font effects.** Bevel, outline, glow, drop shadow, extrusion, and chromatic aberration should communicate material, lighting, or function. A stack of effects cannot rescue a weak type choice.
11. **Test glyphs and localization early.** Render the actual game strings: apostrophes, quotes, em dashes, ellipses, currency, diacritics, controller glyphs, and translated text. “Supports Latin” does not guarantee every Western European letter.
12. **Inspect in motion and in context.** A font may look expressive on a specimen and unreadable on a tilted, lit, moving prop. Review in-game screenshots at target resolution, distance, contrast, and post-processing settings.
13. **Keep a type specimen and asset register.** Record the font, source URL, download date/version, license file, planned roles, supported characters, and any edits. This prevents accidental license drift and inconsistent reuse.

## Blender and Godot production notes

- Keep a source copy of every downloaded `.ttf`/`.otf` and its license/readme in your project’s asset records. Use a clear project filename; do not rename the typeface’s internal family metadata unless you are making a modified font and understand the consequences.
- For Blender props, preserve editable text objects in the working file and convert to mesh only for final export when needed. Check text on the actual camera angle and object scale; tiny text that reads in a viewport may vanish in a gameplay camera.
- For Godot UI, import the font and test it in the real `Control` layout. Godot’s font guide covers font resources, fallbacks, MSDF/rasterization, and glyph prerendering. Use fallbacks for characters the chosen font lacks, and leave spare room for translated strings to run longer.
- For pixel fonts, match the rendering scale to the intended pixel grid. Fractional scaling, filtering, mipmaps, or arbitrary camera zoom can blur the design. Follow the font creator’s import guidance and inspect output at the target display size.
- For 3D labels and signs, compare the text size to the object, viewing distance, camera FOV, and lighting. Use texture resolution and UV space that preserve counters and thin strokes. A logo can be readable up close but still fail at gameplay distance.
- Godot’s stable documentation notes that fonts can use fallback fonts and that rasterized glyphs may need prerendering; it also recommends reserving extra layout space because font metrics can differ. See [Using Fonts in Godot](https://docs.godotengine.org/en/stable/tutorials/ui/gui_using_fonts.html).

## CC0 verification checklist before shipping

- Open the source page for the exact font file/version; confirm it says **CC0** or **CC0 1.0**. “Free,” “public domain,” “royalty-free,” and **OFL** are not interchangeable labels.
- Keep the license/readme included with the original download and write down the source URL and date. A pack may contain files with different licenses.
- Check whether the font is modified, bundled with other assets, or redistributed separately in your build. Preserve any notices that the creator requests even when attribution is not legally required.
- If you need evidence of human authorship or no generative AI, save the creator’s statement separately. CC0 alone does not answer that question.
- Check names and symbols used in a logo or title for third-party marks or recognizable franchise resemblance. CC0 does not grant someone else’s trademark rights.

## Source and method notes

This is a curated working list from the source pages linked above, checked on **October 2, 2026**. Font Library’s current CC-0 filter lists ten families: Tenderness, Ferrum, Seshat Regular, Marius1, Vegur, Medio, Penna, Pixel Operator, Aileron, and FifteenTwenty. Other entries are linked to their creator or asset pages. Source metadata and pack inventories can change; re-check the particular download you ship.

CC0 overview: [Creative Commons CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). Godot implementation reference: [Using Fonts](https://docs.godotengine.org/en/stable/tutorials/ui/gui_using_fonts.html).
