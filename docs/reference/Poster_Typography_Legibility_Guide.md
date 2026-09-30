# Making Poster Text Pop and Stay Legible

## A practical typography guide for pixel-style posters in Blender and Godot 4.7

This guide covers how to make titles, slogans, dates, prices, and small copy stand out on poster art that appears on 3D walls. It focuses on the pixel-style, 1990s in-world graphics used in the poster atlas: blocky display type, limited palettes, hard-edged panels, and small supporting text.

The goal is not to make every word equally readable. A player should recognize the main message first, then discover secondary information if they move closer. Text can become a texture at distance; the title, venue, offer, or event name should not.

---

## 1. The order to solve typography problems

When text does not read, fix problems in this order:

1. **Words:** shorten the message.
2. **Hierarchy:** decide which line matters most.
3. **Size:** enlarge the important line.
4. **Shape and spacing:** widen letters or add breathing room.
5. **Contrast:** separate the text from its background.
6. **Backing shape or effect:** add a panel, outline, or shadow only if needed.
7. **Texture:** add print character last.

A glow or thick outline cannot fix a headline that is too small, too long, or crowded into the illustration.

## 2. Design a readable hierarchy

Give each text line a clear job:

| Role | What the player should get | Typical treatment |
|---|---|---|
| Main title | Band, venue, product, film, or event name | Largest, most distinctive, strongest contrast |
| Hook / offer | The short promise, slogan, or joke | Smaller than title, but still readable at approach distance |
| Details | Date, location, price, supporting act, or instruction | Compact grouped block with simpler type |
| Microcopy | Fine print, legal joke, serial number, tear-off detail | Decorative texture unless the player can approach closely |

Choose one dominant line. If the headline, offer, date, and label all use the same size, color, and outline, none of them dominates.

### A practical size pass

At the final poster aspect ratio:

- Make the title visibly larger than every other text role.
- Keep the hook or offer short enough to fit in one or two strong lines.
- Group details into one block; do not scatter small labels across the page.
- Treat tiny text as atmosphere, not important communication.
- Check the rendered poster in the actual level before deciding that the type is large enough.

Exact sizes depend on the poster resolution, physical dimensions, camera distance, and display resolution. Judge the projected size in the game, not the Blender text-object size.

## 3. Make contrast do most of the work

### Check value before hue

Bright red on dark red may feel colorful but still blur together. Convert the design to grayscale: the title should separate clearly from the field behind it. Use a strong light-dark difference first, then use hue to establish mood.

For pixel-art posters, test the title against the darkest and lightest neighboring colors. Keep enough difference between:

- Text and its immediate background.
- The backing panel and the surrounding artwork.
- The hook and the title.
- Adjacent text lines.

Do not use several bright colors at the same intensity for every line. Save the brightest accent for the most important word or offer.

### Use a backing plate when the art is busy

Put text on a shape that gives it a quiet field:

- Solid rectangle or banner.
- Ticket, label, price tag, or painted sign panel.
- Dark strip across the top or bottom.
- Light paper-colored knockout inside a dark illustration.
- Irregular brush/ink patch for a handbill.

The plate should be large enough to leave padding around the letters. Avoid squeezing text to the edge. Keep the plate simple; a decorative border inside a busy background can reduce legibility again.

### Reserve clear space

Keep busy illustration, repeated dots, halftone, and distressed texture away from the title's counters and narrow strokes. A clear-space mask can stop procedural marks from crossing text. If the poster is meant to look layered or pasted, overlap the paper edges, not the critical letters.

## 4. Pick and adjust type for pixel art

### Use roles, not a pile of fonts

Start with one display face for the title and one plain face for details. A third face can be used for a small hand-written note if the poster needs it. Keep font choice consistent within a poster family, then customize selected headlines for personality.

- **Display type:** recognizable shape, strong weight, distinctive silhouette.
- **Support type:** uncomplicated, open counters, readable numerals and punctuation.
- **Handwritten accent:** use sparingly for corrections, signatures, or personal notes.

Check that the font has the characters needed for fictional names, dates, apostrophes, dollar signs, ampersands, and punctuation. Missing glyphs can quietly break a batch render.

### Space letters deliberately

Pixel fonts often have tight counters and uniform widths. Small spacing changes can make a big difference:

- Increase tracking when adjacent letters touch or look like one shape.
- Open the line spacing when stacked uppercase lines merge vertically.
- Avoid squeezing a long title horizontally until the counters collapse.
- Break long names at a natural phrase or syllable boundary.
- Keep similar line lengths when the composition is formal; vary them when the layout should feel hand-made.
- Check numerals such as `1`, `7`, `0`, and `8` at final size; dates and prices need to remain distinct.

If a word still does not fit, edit the copy or choose a wider title area. Do not solve every fit problem by shrinking the type.

### Make a custom wordmark from type

For a band, venue, or store name:

1. Start with a font that already has the right basic character.
2. Render it large and inspect the whole word as one silhouette.
3. Adjust tracking and line breaks.
4. Customize one or two letters: lengthen a stem, cut a corner, tilt a terminal, or add a small inline.
5. Keep the rest of the letters simple so the name remains readable.
6. Compare the mark in solid black and white before applying color or effects.

The purpose is to make the name feel owned by that fictional business, not to decorate every character.

## 5. Pixel-style text effects

Use effects to separate text from its background. Choose one primary effect and, at most, one supporting effect.

### One-pixel outline

A one-pixel dark or light border can clarify letters against uneven art. Use the thinnest outline that survives at the actual texture size. Thick borders close counters in letters such as `A`, `B`, `e`, and `a`; check those counters after applying the effect.

Use a light outline on dark artwork or a dark outline on light artwork. Avoid double outlines unless the type is very large and the poster family calls for a sign or arcade display look.

### Hard offset shadow

Duplicate the title, color the copy darker, move it down and slightly sideways by a small whole-pixel amount, and place the main text over it. This creates depth like an extruded sign or printed drop shadow.

Keep the offset consistent for every line in that title lockup. A tiny hard shadow reads as depth; a large soft shadow makes pixel lettering muddy.

### Two-color inline or split fill

Use a second color inside part of a large headline: top half light / lower half dark, or a narrow highlight stripe. Keep enough value contrast between the fill and outline. This works best on large display lettering, not fine print.

### Glow or light halo

Reserve glow for text that plausibly emits light, such as a neon sign, marquee, or luminous arcade display. Build a sharp bright letter core, then add a restrained halo behind it. Keep a dark border or dark surroundings so the letters do not dissolve into the glow.

For ordinary printed posters, use ink contrast, a plate, or an outline instead of a glow.

### Bevel and extrusion

Use shallow hard-edged shading on large letters to suggest painted wood, raised sign letters, or metallic trim. Shade all letters from the same light direction. Keep the bevel narrow and preserve the interior openings. Avoid 3D bevels on small pixel fonts; they usually consume the letter shape.

## 6. Make type feel human-made

Hand-made does not mean inconsistent everywhere. Establish a typographic system, then make a few deliberate deviations:

- Let one headline word be slightly larger or tilt by a few degrees.
- Vary line width in a hand-painted sign.
- Add a single handwritten correction or marker underline.
- Break a border or let a letter overlap an illustration edge on purpose.
- Use a slightly uneven baseline for a photocopied club flyer.
- Keep supporting copy cleaner so the headline's roughness feels intentional.

Do not randomize each letter's rotation or size independently. That often looks like a bad font render instead of human lettering. Vary words, lines, or hand-drawn components as units.

## 7. Blender workflow for legible poster lettering

### Set up live text first

1. Create Blender Text objects for title, hook, detail block, and microcopy.
2. Keep each role as a separate object or named text field.
3. Set a front-facing orthographic camera and use the final poster aspect ratio.
4. Turn on guides for margins, title zone, image zone, and footer.
5. Choose the font and establish size, alignment, and line spacing before adding decoration.
6. Render at the intended final pixel resolution; do not judge from a huge viewport preview.

Blender Text objects expose paragraph controls such as alignment and spacing. Use those controls to establish a clean layout, then adjust individual headlines where needed.

### Build an outline from an alpha mask

For procedural outline variants:

1. Render the text with a transparent background or as a clean mask.
2. Use Blender's Compositor `Dilate/Erode` node to expand the mask slightly.
3. Put a flat outline color behind the original, undilated text.
4. Composite the original fill over the expanded mask.
5. Inspect the counters and gaps in letters; reduce the expansion if they close.

For a pixel-art result, render at the target resolution or scale by an integer amount. Avoid blur and subpixel offsets.

### Build a hard shadow

1. Duplicate the text mask.
2. Color it with the shadow color.
3. Offset it a small whole number of pixels down and sideways.
4. Place the original text above it.
5. Keep the same offset direction across the complete title group.

A geometry duplicate behind a Text object can also work for a simple shadow or shallow extrusion. Use the compositor when you need per-pixel control.

### Preserve editability and reproducibility

Keep live text and font assets in the `.blend` source. Render the approved poster to an opaque PNG for Godot. Record the font, title text, sizes, tracking, line spacing, effect settings, and output resolution in the poster data. Pack or otherwise include approved font files so batch renders do not substitute fonts on another machine.

## 8. Family-specific text treatment

| Poster type | Title treatment | Supporting information |
|---|---|---|
| Concert poster | Very large, condensed, stacked, arced, or rough; may overlap art if the silhouette stays clear | Venue/date/support acts grouped as one compact block |
| Band poster | Treat the band name as a repeatable wordmark; customize one or two letters | Tour dates can use a consistent list or stamp system |
| Movie poster | Title integrated with the image or placed in a strong top/bottom band | Tagline is short; credits stay in a narrow footer |
| Collectible fantasy | Series/set mark plus an elegant or carved-feeling title; preserve open area around the hero image | Small lore copy can be ornamental; rarity/series marks should use a consistent position |
| Vintage advertisement | Short slogan with large, sturdy lettering; product name and price are easy to find | Supporting details use plain type and simple alignment |

Change the treatment to fit the fictional source. A photocopied bar flyer, glossy theater one-sheet, collector promo, and supermarket sale card should not all use the same outline, glow, or title placement.

## 9. In-game legibility tests

Review typography on the actual 3D wall, not only as a flat PNG:

1. Put the poster on its intended wall mesh in a representative Godot scene.
2. Set the expected player camera and distance.
3. Check it head-on, at an oblique angle, and under the level's brightest and dimmest lighting.
4. Compare the title and hook at the smallest distance where you expect players to read them.
5. Inspect a screenshot at the game's target resolution.
6. If the text blurs, simplify shapes, increase contrast, widen spacing, or enlarge it before increasing the whole texture resolution.

Godot 4.7 recommends mipmaps for 3D textures to reduce grain at a distance. Pixel-art textures can be harmed by VRAM compression, so compare the project's import modes and review the poster in-engine. Preserve mipmaps when distant stability matters; verify how the chosen filtering and compression affect the pixel edges on target hardware.

### Fast pass/fail check

- Can I identify the main title in one second?
- Can I separate title, hook, and details without reading every word?
- Do letters keep their counters and gaps at the intended distance?
- Does the title contrast in grayscale?
- Is the effect treatment consistent with the poster material?
- Is any small text being treated as required when it is too small to read?
- Does the poster still look like printed or painted matter instead of a floating game UI label?

## 10. Common fixes

| Problem | Try this first |
|---|---|
| Bright letters still disappear | Put them on a darker or quieter plate; check grayscale contrast |
| Headline looks cramped | Shorten the wording, increase tracking, or use a wider line before shrinking type |
| Outline makes letters muddy | Reduce outline thickness and inspect the letter counters |
| Shadow looks like a second blurry title | Use a hard whole-pixel offset and reduce the distance |
| Too many text effects compete | Keep one effect on the title and make secondary copy plain |
| Every poster uses the same type layout | Create several layout presets and choose by poster family |
| Small copy turns to noise on the wall | Remove it, simplify it, or make it part of the printed texture rather than required information |
| Pixel text shimmers at distance | Test mipmaps/filtering/compression in Godot; simplify narrow strokes and tiny patterns |

---

## References

- [Blender Manual: Text properties](https://docs.blender.org/manual/en/5.2/modeling/texts/properties.html)
- [Blender Manual: Compositor Dilate/Erode node](https://docs.blender.org/manual/en/4.5/compositing/types/filter/dilate_erode.html)
- [Godot 4.7: Importing images](https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/importing_images.html)
- [Figma: Graphic design principles](https://www.figma.com/resource-library/graphic-design-principles/)
