# Making Strong 2D Poster Art With Procedural Tools

## A practical artist's guide for Blender and Godot 4.7

This guide teaches an artist to design and illustrate poster art for a 3D game. It covers concert and band posters, movie posters, collectible fantasy art, and vintage advertising. The workflow starts with visual decisions an artist can judge, then uses Blender to make selected parts repeatable: type placement, geometric motifs, limited palettes, print effects, and controlled variation.

The guiding idea is simple: **procedural tools should multiply good design decisions, not make them for you.** The artist chooses the idea, focal image, silhouette, value pattern, composition, and type hierarchy. Nodes and scripts can then help build supporting detail and consistent variants.

The visual principles used here are practical applications of alignment, balance, contrast, hierarchy, proportion, repetition, movement, proximity, and negative space. They are not a rigid formula. Learn what each principle does, then break it on purpose when the image benefits. The linked references at the end offer related advice on graphic design fundamentals, constrained practice, mixed media, and game-art workflows.

---

## 1. What makes poster art work?

A poster has three reads:

1. **At a glance:** silhouette, dominant color, subject, mood.
2. **After a few seconds:** title, event, product, or story promise.
3. **Up close:** supporting copy, details, print character, and small jokes or marks.

Choose one primary message before drawing. Write it in one sentence, such as: “This is a strange late-night show with explosive energy.” Every major image, color, shape, and type choice should support that message.

### The main design principles, in artist language

| Principle | What to do while making a poster |
|---|---|
| Hierarchy | Make the first-read item largest or highest-contrast; place supporting information in descending order of importance. |
| Contrast | Separate the focal image from its background using value, scale, shape, texture, or color. Concentrate the strongest contrast. |
| Balance | Distribute visual weight. A small bright shape can counter a large dark shape; the layout does not need to be symmetrical. |
| Alignment | Snap related text and symbols to shared edges, centers, baselines, or a deliberate grid. Break alignment only to create emphasis. |
| Proportion | Set the relative size of image, title, and details. Large elements feel important; size changes also create mood. |
| Proximity | Keep related information together, such as venue, date, and address. Use space to separate unrelated groups. |
| Repetition and rhythm | Repeat colors, shapes, or marks to make a family feel cohesive. Change spacing or scale to create movement. |
| Movement | Use curves, diagonals, gaze direction, light beams, or repeated shapes to guide the eye from image to title. |
| Negative space | Leave quiet areas around the focal point and text. Empty space is part of the composition, not unused canvas. |
| Unity | Keep line quality, palette, shapes, type, and surface treatment in the same visual world. |

### Three tests that reveal problems early

- **Thumbnail test:** shrink the poster until the long edge is about 120–160 pixels. You should still recognize the big image and find the title.
- **Grayscale test:** remove color. The focal point, background, and text should still separate by value.
- **Blur test:** apply a strong blur or squint. The major masses should create a deliberate pattern, not an even field of noise.

If a poster fails one of these, fix the composition before adding detail.

---

## 2. A repeatable artist workflow

Use this order for every design. Do not start by picking fonts, painting texture, or building nodes.

### Step 1: Define the brief

Record:

- What is being advertised or represented?
- Who is meant to notice it?
- What feeling should it create?
- Where will it hang, and how far away is the player?
- Which facts must be readable and which are atmosphere?
- Which poster family and era does it belong to?

Collect a small reference board with 6–12 examples. For each image, write down what you are studying: title scale, silhouette, palette, lighting, print method, or layout. Do not trace a single poster or copy its signature arrangement.

### Step 2: Write the visual hook

Describe the image in one short sentence: “A singer is lit like a comet,” “The monster hides behind the title,” or “A tiny product looks impossibly heroic.” If the hook takes a paragraph to explain, simplify it.

### Step 3: Draw 3–6 thumbnails

Use a rectangle for the page, one shape for the image, and rough bars for title and copy. Try different focal positions and eye paths. Keep thumbnails black, white, and one gray; this forces attention onto composition.

### Step 4: Choose hierarchy and layout

Assign the reads:

1. Main image or title.
2. Secondary title or promise.
3. Event details / series mark.
4. Fine print or decorative detail.

There is no single required order. A movie poster may lead with the image; a vintage ad may lead with the slogan; a concert handbill may lead with the band name. Make the decision explicit.

### Step 5: Build the image from large shapes

Draw the biggest silhouette first, then the major light and shadow shapes. Use a small set of clear shapes before adding anatomy, texture, or tiny objects. Check for tangencies: avoid edges that barely line up in ways that merge unrelated forms.

### Step 6: Set values, then color

Work in grayscale until the subject and background separate. Add color only after the value pattern is readable. Assign each color a job: paper/background, dark structure, main image, focal accent, optional secondary accent.

### Step 7: Add type and supporting graphic shapes

Use a display face for the main title and a simpler supporting face for dates, locations, and credits. Keep related copy grouped. Leave space around the image's focal point and the title. Use graphic shapes to connect them rather than decorating every gap.

### Step 8: Add texture and finish

Choose a printing/material story: crisp screen print, cheap photocopy, glossy movie promo, illustrated collector art, or faded commercial poster. Add only effects that support that story. Keep the clean art separate from all texture layers.

### Step 9: Review at game scale

Render a contact sheet, then place the artwork on its actual wall in Godot. Review at the real camera distance, under the level's lighting, and at oblique angles. Change the art if it does not read in context.

---

## 3. Art techniques and how to use them

These are hands-on techniques for making a flat image more readable, dimensional, expressive, or memorable. Pick two or three that support the brief; do not stack every technique onto one poster.

### A. Silhouette and negative-shape design

1. Fill the main subject as a single dark shape.
2. Remove interior detail and inspect its outline.
3. Look for clear gaps between arms, legs, props, and torso.
4. Exaggerate the pose or angle that communicates the subject.
5. Compare the shape against the background at thumbnail size.

Use this for characters, instruments, monsters, bottles, cars, and symbols. A readable silhouette is often the fastest way to improve an image.

### B. Three-value blocking

1. Make a grayscale version.
2. Assign the image to dark, middle, and light groups.
3. Put the focal subject in one value group and its immediate background in another.
4. Reserve the brightest or darkest accent for the focal point and title.
5. Add a fourth value only to separate overlapping forms.

Avoid airbrushing values together early. Hard-edged value shapes make a poster feel graphic and make mistakes easier to see.

### C. Shape exaggeration and proportion

Enlarge the feature that makes the subject recognizable: a dramatic hat, oversized instrument, long shadow, giant moon, tiny person against a huge object, or comically small product with a heroic spotlight. Keep the rest of the proportions simpler so the exaggeration is clear.

### D. Directional composition

Choose one movement pattern:

- **Diagonal:** energy, impact, danger, speed.
- **Arc or curve:** flowing movement, dance, magic, journey.
- **Radial burst:** spectacle, live event, explosion, announcement.
- **Vertical stack:** monumentality, authority, theatrical scale.
- **Frame or tunnel:** reveal, mystery, focus on a central subject.

Use 3–5 large directional shapes, then add small repeated marks only if needed. Make the direction lead toward the image, title, or key detail.

### E. Overlap and depth

Separate the page into foreground, subject, and background. Let one shape overlap another to make the order clear. Use partial occlusion, changing scale, and value separation before relying on blur. Keep the title readable if it crosses the image; use a banner, outline, or clear-space mask where necessary.

### F. Light-and-shadow illustration

Choose one main light source. Paint the subject as a base shape, then add a large shadow shape and a smaller light-facing shape. Use a rim light only along selected edges facing the background. Add reflected light sparingly. A simple light pattern with clear edges often reads better than many soft gradients.

### G. Line weight and edge control

Use heavier outlines on the shadow side or outer contour and lighter interior lines. Keep the sharpest, most detailed edges near the focal point. Soften or simplify background edges. When drawing with Grease Pencil, use separate materials or layers for outline, fill, and accent strokes so thickness and color can be adjusted independently.

### H. Limited palette, duotone, and selective color

Start with 3–5 inks plus paper. For duotone, map dark values to one hue and lights to a contrasting hue; use a third accent only at the focal point. For selective color, keep most of the image neutral and color one meaningful object or area. Check grayscale afterward so hue is not doing all the structural work.

### I. Collage and found-text texture

Build a collage from shapes, scans, drawn marks, and short text fragments. Overlap at least three distinct scales: a large background shape, medium image fragments, and small printed details. Use a mask to cut collage pieces into a silhouette or frame. Keep word fragments legible only when their meaning matters; otherwise treat them as pattern. In a game asset, use original or licensed materials, not un-cleared magazine scans.

### J. Texture and mixed-media surface

Create separate layers for paper, ink, image, and wear. Use paper grain at low contrast, roughen only selected edges, and place scratches where handling or printing would cause them. Mix smooth and rough areas to create contrast. Texture should support form and material; it should not obscure small text or the focal image.

### K. Halftone and screen-print effect

1. Start from a clean grayscale or ink-separated image.
2. Mask halftone into selected shadows or midtones.
3. Choose a dot size large enough to survive the game texture's mipmaps.
4. Keep other regions smooth so the dots have contrast.
5. Offset one ink layer a few pixels for imperfect registration.
6. Inspect the result small; remove patterns that shimmer or make moiré.

### L. Metallic or glossy accent

Make a separate mask for foil, metallic ink, or glossy coating. Restrict it to a few letters, stars, border marks, or a product highlight. In a printed image, imply metallic shine with sharp alternating light/dark bands; on a physical 3D poster, use modest roughness variation on only the masked region. Large uniform metallic areas make the image look like a UI effect.

### M. Background completion

A background can stay simple, but it should look intentional. Add one or two quiet cues that locate the subject: an arch behind a figure, a horizon, faint architecture, a spotlight halo, or a cloud bank. Keep contrast and detail lower than the focal image. If the empty area supports the title and mood, preserve it as negative space instead of filling it.

### N. Purposeful imperfection

Make one controlled imperfection: offset a print layer, roughen an edge, break a line, vary a repeated shape, leave an uneven wash, or let one element crop awkwardly by design. Keep the rest of the composition controlled. Randomness reads as a mistake when the artist cannot point to what it adds.

### O. Visual text and type as image

Treat the title as a shape as well as language. Test words in blocks before selecting a typeface. Stack, arc, crop, outline, or reverse text only when it still reads. Tiny support copy can create visual density, but the most important information must remain legible. Keep separate roles for title, subtitle, event details, and fine print.

---

## 4. How to make each poster family

Each recipe begins with the family’s communication goal, then gives a practical drawing plan. Apply the general art workflow in Section 2 to each one.

### Live concert poster

**Goal:** stop someone walking past and make the show feel immediate.

1. Choose the band name, venue, date, and one visual hook: instrument, performer, mascot, symbol, or sound made visible.
2. Make a 3–4 ink palette. Use one dark, one paper tone, one loud accent, and optionally a second accent.
3. Choose an energetic composition: diagonal instrument, radial burst, raised arm, or repeated rhythm of speakers/lights.
4. Make the title the strongest type shape. Group venue, date, and support acts into one compact block.
5. Draw the central image in 2–4 large value shapes. Add hand-drawn contour or a rough photocopy effect if it fits the venue.
6. Add halftone to shadows, one small registration shift, and a few marks suggesting cheap print stock.
7. Shrink to thumbnail. The band name and main symbol should still read.

**Blender setup:** Grease Pencil layers for the image and ink colors; Text objects for title and lineup; a Geometry Nodes group for repeated dots or rays; compositor masks for grain and registration shift. Keep the burst outside the lettering's safe region.

### Band poster

**Goal:** express the band's identity and genre before the viewer reads all the copy.

1. Define three visual adjectives for the band, such as “angular, cold, mechanical” or “warm, loose, handmade.”
2. Pick an image anchor: portrait, silhouette, mascot, instrument, or emblem. Avoid a generic image unrelated to the band’s identity.
3. Choose a pose/crop and lighting style that matches the adjectives: hard frontal portrait, dramatic side light, flat silhouette, or loose collage.
4. Design the band name as a distinctive word shape. Draw custom lettering only if you can keep it readable; otherwise pair one display font with a simpler support font.
5. Use repeated motifs from the band identity—stars, bolts, flowers, eyes, wires, or stripes—in a controlled rhythm.
6. Add tour dates or venue information as a consistent block, not scattered labels.
7. Keep the series recognizable across multiple dates by locking the logo, type roles, and palette while varying the portrait, accent, or background.

**Blender setup:** Keep the band mark as editable curve/text artwork; use duplicated motifs or Geometry Nodes for the repeated identity pattern; store the date and venue in named text fields or data properties. Use masks so texture does not damage the mark.

### Movie poster

**Goal:** promise a story and genre through a single image.

1. Write the premise as an image sentence: “A lone diver sees a city under the lake.”
2. Choose one dramatic relationship: tiny hero / huge threat, two faces separated by a crack, object foreground / danger behind, or light / darkness.
3. Build depth with foreground frame, middle subject, and distant atmosphere. Use overlap and scale before blur.
4. Direct the viewer with gaze, light beams, diagonals, smoke, or leading lines. Keep the focal area away from the credit block.
5. Establish a cinematic value structure: one bright area, one dominant dark mass, and a middle-value field.
6. Place the title at the top or bottom where it supports the image. Reserve a compact footer for credits.
7. Add a short tagline only if it sharpens the premise. Remove copy that explains what the image already says.

**Blender setup:** Use flat planes or Grease Pencil layers for foreground/midground/background; add soft atmosphere with masked color fields, not global blur. Use a separate title and credit group, then render the final image. Test from the in-game angle; perspective can compress type.

### Collectible fantasy poster

**Goal:** make the central hero, creature, artifact, or event feel worth studying while keeping an unmistakable focal point.

1. Choose one hero subject and one secondary story element. Do not give every character or magic effect equal emphasis.
2. Pose the figure along a readable diagonal, S-curve, or triangular arrangement. Direct face, weapon, spell, or gaze toward the focal object.
3. Separate three depth planes: foreground frame or effects, central subject, and quieter distant setting.
4. Use a limited base palette plus one high-chroma accent for the magic, relic, or focal costume.
5. Paint shadows as grouped shapes. Add rim light to selected contours; do not outline every edge with glow.
6. Add frame filigree, seals, runes, or series marks only after the central composition reads. Reuse shapes and border motifs to imply a set or collection.
7. Reserve an open area for title and series mark; keep fine detail away from that space.

**Blender setup:** Draw the character with Grease Pencil or compose layered 2D planes; use curve/mesh modules for frame ornaments; make one procedural pattern for runes or stars but curate the final placements. A selective roughness/gloss mask can suggest foil on the physical poster, while the illustration remains mostly matte.

### Vintage advertisement

**Goal:** make one product or promise instantly recognizable and memorable.

1. Write a short promise of 3–7 words. The copy should work at a glance.
2. Pick one central object, mascot, or character. Make its silhouette simple enough to read when very small.
3. Exaggerate proportion, pose, or scale to give it charm: oversized product, tiny hero, dramatic hand, or impossible smile.
4. Use a flat background shape and 2–4 colors. Make the slogan and object contrast strongly.
5. Draw hard-edged shadow shapes and a small highlight. Avoid realistic gradients unless they belong to the chosen print era.
6. Add one decorative frame, badge, or burst to make the promise feel official or theatrical.
7. Apply limited wear: faded ink, paper tint, uneven registration, or slightly imperfect hand lettering.

**Blender setup:** Use simple mesh planes, curves, and Grease Pencil fills for flat shapes; use a color-ramp or palette remap for restricted inks; use Text objects for the slogan and convert only the final render to a flat image. Keep a clean version and a worn version.

---

## 5. Blender procedures for procedural illustration

The interface changes between Blender releases, so treat this as a node strategy rather than a guaranteed exact socket-by-socket graph. Keep the controls named and visible to artists.

### Reusable canvas scene

Create a saved authoring scene with:

- A front-facing canvas plane with fixed UVs and guide marks.
- An orthographic camera aimed squarely at the canvas.
- Separate collections or Grease Pencil layer groups for paper, shapes, subject, type, print, and wear.
- A fixed output resolution and color-management preset.
- A material preview plane that shows the render on paper under plausible room light.

Use a 2:3 canvas as a starting point. Add trim and safe-area guides. The source image should be opaque unless torn transparent holes are part of the art.

### Grease Pencil drawing recipe

1. Create a drawing object and add named layers: `ROUGH`, `SILHOUETTE`, `SHADOW`, `LIGHT`, `DETAIL`, `ACCENT`.
2. Use a solid-fill material for the silhouette and a small number of stroke/fill materials for inks.
3. Draw a clean silhouette before facial features or texture.
4. Lock the silhouette layer when its contour works; draw values and accents above it.
5. Use layer visibility to compare the image with and without details.
6. Render a clean pass before adding compositor effects.

Grease Pencil supports layered strokes and fills; layers can be grouped, hidden, locked, and used as masks. This helps artists isolate artwork stages and constrain changes.

### Geometry Nodes recipe: repeated motifs

Use Geometry Nodes for motifs that are genuinely repeated: dots, stars, ticket marks, rays, confetti, border ornaments, or halftone-like graphic modules.

1. Make one clean motif as a curve or simple mesh.
2. Create a set of points within a defined rectangle, curve, or authored mask.
3. Use `Instance on Points` to place the motif at those points.
4. Drive rotation and scale with bounded random values and a saved seed.
5. Expose count, region, scale range, rotation range, and seed as named inputs.
6. Exclude the title area and focal face/subject with a selection mask or manually cleared region.
7. Render multiple seeds in a contact sheet; remove distributions that look accidental.

The point distribution can be regular for orderly vintage decoration, flowing along a curve for movement, or irregular for handbills. Start with intentional point placement, then randomize only a few supporting variables. Avoid uniform scatter across the whole page.

### Compositor recipe: print pass

Keep an unprocessed render as the source. Then:

1. Duplicate or isolate an ink/color pass.
2. Remap grayscale values to the chosen ink colors using a color-ramp or equivalent palette mapping.
3. Add a small transform offset to one ink pass; expose X/Y offset as artist controls.
4. Mask grain or halftone into selected shadows.
5. Composite a low-contrast paper texture underneath the art.
6. Add wear with an explicit mask rather than global noise.
7. Mix the effect back at a restrained amount and compare it to the clean source.

Test the halftone and grain after downsampling to the target texture. Some fine patterns alias or shimmer once mipmapped; enlarge dots or remove the effect if needed.

### Typography procedure

1. Write all copy in a content sheet before laying out the poster.
2. Mark its role: main title, secondary line, event data, credit, or decorative microcopy.
3. Use one display family and one support family by default.
4. Place related data in one grouped block. Use a shared left edge, center line, or baseline to make it feel intentional.
5. Check hierarchy by squinting: title first, then image or promise, then details.
6. Inspect every line break at thumbnail scale.
7. Keep text live in the source file; render it into the final poster image for Godot.

### Batch generation procedure

A Blender Python script or controlled manual batch can:

- Read a poster ID, family, text, palette, motif, and seed.
- Apply only approved parameter ranges.
- Check that required text and fonts exist.
- Render one preview and one final output per approved combination.
- Create a contact sheet labeled with poster ID and seed.
- Record resolution, source scene, palette, and settings.

Do not silently overwrite reviewed artwork. Save approved outputs with stable IDs and retain their settings so they can be reproduced.

---

## 6. Exercises that build the skill

These are short deliberate-practice tasks. Each one trains one visual decision at a time.

1. **One object, five silhouettes:** draw the same microphone, bottle, mask, or creature in five distinct outlines using only black.
2. **Three-value poster:** build a complete image using only dark, middle, and light. No texture or soft brush.
3. **Four-color limit:** make the same poster with four inks plus paper. Assign each color a specific job.
4. **Same image, three compositions:** shift only the focal point and title layout; compare thumbnail reads.
5. **Collage rebuild:** cut a reference photograph into 8–12 large shapes and reconstruct it with flat colors; then replace the photo with original drawn shapes.
6. **Light study:** draw one object under a top spotlight, side light, and backlight. Use only one shadow shape and one highlight shape per version.
7. **Background study:** make a background that supports the subject with only two shapes and one texture layer.
8. **Imperfection study:** make one clean screen-print image, then create three versions with different registration offsets or ink chips. Choose the effect that adds character without hurting clarity.
9. **Family sheet:** create five posters using the same title/data hierarchy but different family art direction: concert, band, movie, collectible, vintage ad.
10. **Distance test:** place each design in Godot at its intended wall size. Fix whichever element stops reading first.

Keep dated versions. The goal is not just to finish a poster; it is to see which choice made the poster clearer or more expressive.

---

## 7. Godot 4.7 wall display and review

Use the poster as an opaque PNG on a UV-mapped quad or shallow paper mesh. Set the Albedo texture on a `StandardMaterial3D`; enable mipmaps for 3D use and check the project’s texture compression. Set moderate-to-high roughness so it reads like paper. Add a small offset from the wall to prevent z-fighting. Use transparency only for actual holes or a torn silhouette.

Place the poster in a test scene that matches the real camera distance, lighting, color grading, and angle. Check:

- Does the image read on approach?
- Does the palette shift or flatten in the actual lighting?
- Does halftone shimmer or alias at distance?
- Does the texture remain legible when viewed at an angle?
- Is the poster too bright, too glossy, or too dark next to nearby props?
- Could a lower resolution work just as well?

A rectangular poster plane is usually the predictable choice. A Godot Decal can project art onto irregular surfaces, but renderer support differs; verify the target renderer before choosing it.

---

## 8. Review checklist

### Art and composition

- Can I explain the poster’s purpose in one sentence?
- Does the thumbnail have one clear focal point?
- Does the silhouette read without interior detail?
- Do value groups separate the subject from its background?
- Does the eye move through the image in a deliberate order?
- Is negative space protecting important shapes and text?
- Is the background finished enough to feel intentional, but quiet enough to support the subject?

### Graphic design

- Is the hierarchy obvious without explaining it?
- Are title, event/product details, and small copy grouped by role?
- Is alignment consistent or intentionally broken for emphasis?
- Are repeated shapes, colors, and type styles building unity?
- Is the palette limited and functional?

### Technique and procedure

- Does every texture/print effect support the chosen material story?
- Are procedural elements confined to allowed areas?
- Can an artist lock important choices and vary supporting ones?
- Can every approved variant be regenerated from its saved seed and settings?
- Does the final image look authored rather than merely randomized?

### Engine integration

- Does it work at the real game distance and camera angle?
- Are mipmaps and compression preserving the intended visual style?
- Is the material opaque and appropriately rough?
- Is resolution proportionate to how close players can get?

---

## References and further study

The following resources informed this guide. The practical steps above adapt their ideas to poster illustration, procedural art, and in-game viewing.

- [Allise Nicole: 10 Ways to Make Your 2D Art More Interesting](https://artistallisenicole.com/2016/02/21/10-ways-2d/) — text as visual texture, surface variation, selective color, attention to eyes and backgrounds, sketching, collage, and intentional imperfection.
- [Game Development Stack Exchange: Learning to Create Better Art (2D Games)](https://gamedev.stackexchange.com/questions/16930/learning-to-create-better-art-2d-games) — fundamentals and repeated practice matter more than a particular software package; constraints can make practice more focused.
- [Figma: 13 Graphic Design Principles and How to Apply Them](https://www.figma.com/resource-library/graphic-design-principles/) — alignment, contrast, balance, hierarchy, color, whitespace, proportion, repetition, rhythm, movement, emphasis, proximity, and unity.
- [Kevuru Games: How to Create 2D Game Art](https://kevurugames.com/blog/how-to-create-2d-game-art-everything-you-need-to-know/) — concept, style direction, sketching, color exploration, cleanup, review, and engine integration.
- [UC Berkeley Library Design Guide](https://guides.lib.berkeley.edu/design)
- [Shillington: The ABC of Design, Five Principles of Graphic Design](https://www.shillingtoneducation.com/blog/the-abc-of-design-five-principles-of-graphic-design) — alignment, balance, contrast, hierarchy, and repetition.
- [Washington State Farmers Market Association: Fundamentals of Graphic Design Handout](https://wafarmersmarkets.org/wp-content/uploads/2024/02/Graphic-Design-Handout-K-Nelson-2024.pdf) — zoom-out checks, purpose, readability from viewing distance, tone, concision, and removing unnecessary elements.
- [London School of Design and Marketing: Five Graphic Design Principles](https://lsdmlondon.com/design/5-graphic-design-principles-every-designer-should-know/)
- [Blender Manual: Grease Pencil layers and masks](https://docs.blender.org/manual/en/latest/grease_pencil/properties/layers.html)
- [Blender Manual: Geometry Nodes instances](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/instances.html)
- [Godot 4.7: Standard Material 3D](https://docs.godotengine.org/en/4.7/tutorials/3d/standard_material_3d.html)
- [Godot 4.7: Importing images](https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/importing_images.html)
- [Godot 4.7: Using decals](https://docs.godotengine.org/en/4.7/tutorials/3d/using_decals.html)
