# Procedural Poster Art for 3D Game Walls

## Blender-first production guide for Godot 4.7

This guide describes how to make convincing, varied 2D posters with procedural tools, render them from Blender, and display them on 3D walls in Godot 4.7. It is aimed at a small environment-art team building reusable content for a stylized 3D game.

The visual references provided for this guide cover several related but distinct traditions: limited-color concert screen prints, band and venue posters, expressive music graphics, classic movie one-sheets, illustrated collectible-card promotion, and vintage commercial posters. The goal is to borrow their design logic and material character, not reproduce a specific copyrighted composition or logo.

The key production principle is: **procedural tools should create controlled variation and production speed; an artist should still choose the idea, hierarchy, and final composition.** Fully random layouts tend to look like templates. A strong poster usually has one memorable image, a clear type hierarchy, a deliberate palette, and a few imperfections that feel intentional.

---

## 1. What the poster needs to do in a game

A wall poster is both a graphic and a world prop. It should:

- Read as a distinct rectangle from the expected player distance.
- Communicate a subject, event, or fictional brand quickly.
- Fit the time period, location, and social character of its environment.
- Look plausible under the level's lighting rather than glow like a UI panel.
- Remain legible enough to reward a closer look, without requiring players to stop.
- Be cheap to render, author, revise, and reuse across many wall placements.

Decide its intended viewing distance before designing. A hero poster beside a door can carry small print and fine illustration. A poster on a far wall needs a simpler silhouette and fewer words. If a player can approach it, make sure the headline and central image hold up at arm's length.

### Three useful viewing bands

These are practical starting points, not hard engine limits:

| Use | Approximate in-world size | Main read | Detail expectation |
|---|---:|---|---|
| Distant dressing | 0.25–0.45 m tall | Color block and silhouette | No reliance on fine text |
| Ordinary wall poster | 0.45–0.75 m tall | Headline, image, broad layout | Secondary copy can be texture detail |
| Hero/inspectable poster | 0.7–1.1 m tall | Full composition and small details | Consider close-up texture and paper wear |

Set a project-specific standard after reviewing a representative corridor or room from the player camera. Human scale matters more than the nominal pixel dimensions.

---

## 2. Read the references as design systems

Treat each reference family as a toolkit. Mix the principles, not every treatment at once.

### Live concert and event screen prints

Useful characteristics:

- A few strong inks, often two to five colors.
- Large, condensed, hand-drawn, or blocky event lettering.
- Central iconography or a striking abstract image.
- Visible print registration, overprint, paper tone, and ink texture.
- Dense venue/date/supporting-act information around a dominant title.
- Slightly imperfect edges and handmade rhythm.

Procedural levers: ink count, palette, print misregistration, halftone scale, edge wear, title arc/stack, border style, paper stock.

### Band posters and artist promotion

Useful characteristics:

- A distinctive band mark or word shape.
- Portrait, mascot, symbol, or instrument as the image anchor.
- High-contrast, theatrical lighting or silhouette.
- Repeated tour dates or venue text used as texture and rhythm.
- A mood that signals a genre before the player reads the copy.

Procedural levers: image treatment, title lockup, portrait crop, support-copy density, tour-list pattern, limited palette.

### Movie one-sheets

Useful characteristics:

- One dramatic image that summarizes a premise or emotional promise.
- A clear title near the top or bottom, often with a strong tagline.
- Deliberate figure/scale hierarchy and directional light.
- Small, tightly packed credit text in a footer block.
- A genre-specific palette and a controlled amount of mystery.

Procedural levers: top-heavy vs bottom-heavy title, focal point, vignette, sky/ground split, title treatment, credit-block density.

### Collectible and fantasy-promo posters

Useful characteristics:

- Rich illustrative detail and a strong focal character or artifact.
- Layered depth, dramatic color contrast, and controlled glow.
- A recognizable series emblem or set mark.
- Decorative frames, seals, or rarity-like motifs used sparingly.
- Enough open space for the title or product name to remain readable.

Procedural levers: frame family, illustration crop, accent-color placement, emblem location, foil/gloss accent mask. Avoid turning all the detail into noise.

### Vintage commercial and institutional posters

Useful characteristics:

- A simple promise or slogan with large type.
- Flat, assertive color and an easily recognized product or character.
- Slightly awkward, charming illustration or period-specific printing.
- Repetition and simple shapes that remain readable at a glance.

Procedural levers: limited palette, chunky silhouette, type scale, registration offset, worn corners, paper discoloration.

---

## 3. Poster families and art direction

Before building a generator, define a small set of poster families. Each family should have rules that a procedural system can vary without losing its identity.

Example family definitions:

| Family | Layout rule | Image rule | Type rule | Surface rule |
|---|---|---|---|---|
| Venue gig bill | Venue + event headline + date block | Band silhouettes, instruments, or abstract burst | Tall condensed title; compact lineup | Screen print, 2–4 inks |
| Local band handbill | Band mark + one image + venue/date | Rough portrait, mascot, or photocopy collage | Uneven scale, distressed display face | Cheap paper, copied grain |
| B-movie one-sheet | Tagline + dramatic image + title + credits | One central threat or hero | Large genre title; tiny credit strip | Gloss or aged paper |
| Fantasy collector promo | Series mark + key art + set name | Heroic illustration with layered atmosphere | Elegant title with decorative frame | Fine paper, selective foil cue |
| Shop/event advertisement | Slogan + product image + location | Simple character or product silhouette | Friendly, high-contrast lettering | Old ink, faded stock |

Create 3–6 families first. A poster set with strong family distinctions feels authored even when many pieces share a generator.

For each family, define:

1. **Purpose:** What should a passerby understand?
2. **Era and place:** Who printed it, where, and with what budget?
3. **One-sentence hook:** What makes the poster memorable?
4. **Hierarchy:** What is read first, second, and third?
5. **Palette grammar:** Which colors dominate, and what gets the accent?
6. **Texture grammar:** New, pasted, printed cheaply, sun-faded, or repeatedly handled?
7. **Allowed variation:** What can the tool change safely?
8. **Protected features:** What must remain consistent for recognition?

---

## 4. A practical procedural design model

Think of a poster as structured content assembled into a designed page, not as a pile of random effects.

### Content data

Keep the variable content separate from the layout rules. A JSON, CSV, or Blender custom-property record can hold:

```json
{
  "poster_id": "venue_014",
  "family": "gig_bill",
  "headline": "THE NIGHT SHIFT",
  "venue": "THE BLUE COMET",
  "date": "FRI • OCT 18",
  "support": ["TIN ANGEL", "PAPER TIGER"],
  "tagline": "ONE NIGHT ONLY",
  "palette_id": "acid_cream_red_black",
  "image_motif": "crowd_silhouette_03",
  "wear_profile": "cheap_pasteup_medium",
  "seed": 41827
}
```

Names, dates, and slogans should be fictional and checked for accidental resemblance to real brands or artists. Use explicit generated copy rather than letting the system invent text at render time; this keeps spelling, humor, and world lore reviewable.

### Separate design controls from random seed

Use a seed only to choose among approved options. Do not let it decide whether the headline is readable or the key art is cropped badly. Good variation controls include:

- Approved layout templates.
- Grid and alignment options.
- Palette swatches with foreground/background contrast checks.
- Type family and scale range per text role.
- Image motif, crop, rotation, and duotone treatment.
- Frame and border modules.
- Paper tone, grain, halftone, and wear amount.
- Small secondary marks such as ticket stubs, seals, or printer marks.

Make high-impact choices artist-controlled: focal image, headline wording, visual direction, contrast, and final crop.

### Use weighted, bounded variation

Randomness should stay inside authored limits. For example:

- Choose one of four title positions, weighted to the family default.
- Offset one ink channel by a small amount, not by a full letter width.
- Select 1–3 wear masks, but exclude the focal title and face.
- Choose one accent color from that family's approved swatches.
- Use layout-specific minimum text sizes and clear-space rules.

Provide both a fixed-seed reproducible mode and an artist override mode. Store the seed with every approved output so it can be regenerated exactly.

---

## 5. Blender-first authoring workflow

Blender is useful here as a procedural layout bench, texture compositor, lighting/material previewer, and batch renderer. The final poster face is normally a flat image; it does not need to be a complex 3D scene.

### Recommended project organization

Create one reusable `.blend` generator file with collections or scenes for:

- `POSTER_CANVAS`: a front-facing plane, UVs, aspect guide, and margin guides.
- `TYPE`: text objects organized by semantic role (headline, date, credits, marks).
- `ART`: illustration planes, shapes, photo/painted layers, and masks.
- `PRINT_EFFECTS`: halftone, offset channels, paper fibers, stains, edge wear.
- `MATERIAL_PREVIEW`: paper shader and optional physical poster mesh.
- `CAMERA_ORTHO`: camera looking squarely at the canvas.
- `OUTPUT`: resolution, color management, file format, and naming configuration.

Keep the poster face in a consistent coordinate system. A 1.0 × 1.5 unit canvas is convenient for a 2:3 poster. Other useful ratios are 3:4, 4:5, and 1:1. Preserve each intended aspect ratio; do not stretch artwork just to fill an available wall slot.

### Build a controllable layout grid

Use Blender's 2D layout view or an orthographic camera. Create guides for:

- Trim edge and safe area.
- Headline and image zones.
- Credit/footer block.
- Optional frame and bleed.
- Focal-point safe region.

A poster should have one dominant area, one supporting area, and one small-detail area. As a rough starting point, reserve about half the page for the key image, one quarter for headline/title, and the rest for event details, margins, and credits. Change this by family, not randomly.

### Type handling

Blender Text objects are useful for procedural placement and batch rendering. For production:

- Load approved font files from a project-controlled folder.
- Use role-based font choices: display face, supporting face, compact details.
- Save font licensing and attribution information alongside the asset source.
- Convert text to curves only when needed for reliable packaging or art effects; keep an editable source version.
- Favor a few deliberate size/weight changes over many unrelated typefaces.
- Check the actual rendered pixels at in-game size. Small body copy often reads best as texture, not as text the player must decode.
- Avoid relying on font substitution on another machine. Pack resources or render the final image before delivery.

### Use Geometry Nodes where geometry helps

Geometry Nodes can help generate repeated physical or graphic elements, such as:

- A run of ticket stubs, staples, tape strips, rivets, torn-paper tabs, or border marks.
- Repeated tour-date lines or decorative dots if the type is rendered separately.
- A stack of overlapping poster sheets for a wall collage.
- A simple paper curl or corner lift on a hero prop.
- Consistent randomized placement for small, nonessential marks.

Use layout constraints and named inputs. A node group should expose clear parameters such as `Poster Ratio`, `Border Width`, `Wear Seed`, `Staple Count`, and `Curl Amount`. Do not build essential words as generated geometry unless there is a real gameplay reason to read them in 3D.

### Build print character in layers

A flexible texture stack can include:

1. Paper base color and subtle fibers.
2. Main image or illustration.
3. Large title and event text.
4. Palette reduction, duotone, or ink separation.
5. Halftone pattern or coarse print grain.
6. Small color-channel registration offset.
7. Localized scuffs, folds, stains, and faded areas.
8. Edge wear and paste residue.

Keep wear separate from the content. That makes it possible to generate clean and worn variants from the same artwork. Use masks to protect faces, logos, and key text from the strongest damage.

### Procedural print effects

Prefer a small number of clear effects, each with a specific print explanation:

- **Limited ink palette:** Quantize values to a chosen set of inks; retain a separate paper color.
- **Halftone:** Use a dot screen in shadow or midtone regions. Vary dot size or angle by ink layer. Keep dots large enough to survive mipmapping.
- **Misregistration:** Offset one color pass by a few source pixels, usually only on edges. The game camera may hide microscopic offsets.
- **Photocopy grain:** Use uneven black density, crushed contrast, toner noise, and occasional streaks.
- **Screen-print edge:** Use slight ink spread or imperfect mask edges, not a global blur.
- **Paper wear:** Add fold lines, corner grime, pinholes, sun fade, and paste residue with masks and restrained contrast.
- **Gloss/foil cue:** Use a separate mask and roughness variation on the physical poster, not a bright metallic overlay baked across the entire image.

Noise is not automatically material realism. A single strong fold, sun-faded band, or offset color pass often reads better than uniform grunge everywhere.

### Color management and output

Render with an orthographic camera, centered on the flat canvas. Use a fixed, documented color-management setup and check the exported PNG in an image viewer and in Godot. Do not assume Blender's viewport appearance exactly matches the game renderer.

Good starting output sizes:

| Intended use | Suggested source size |
|---|---:|
| Background dressing | 512 × 768 or 768 × 1024 |
| Standard wall poster | 1024 × 1536 |
| Hero / close inspection | 1536 × 2304 or 2048 × 3072 |

These are starting points. A more detailed texture costs memory after import, and a distant poster will be mipmapped down. Use power-of-two dimensions when required by project/platform constraints; otherwise keep a consistent aspect ratio and validate actual imports. Export a lossless PNG as source. Let Godot apply the project's selected runtime texture compression. Avoid JPEG for crisp text and flat screen-print edges unless file size is a deliberate priority and artifacts have been reviewed.

Use transparent PNG only when the poster truly needs a nonrectangular silhouette or torn transparent holes. For ordinary paper, export opaque paper color; alpha blending can introduce sorting and overdraw costs for no visual benefit.

### Batch generation and review

A Blender Python script can read content records, set exposed properties, render each design, and write consistent names such as:

```text
res://art/posters/source/gig_bill_014.png
res://art/posters/source/gig_bill_015.png
```

The script should:

- Validate required text fields and output dimensions.
- Log poster ID, family, seed, and source `.blend` version.
- Render a contact sheet with IDs for fast review.
- Save a thumbnail and full-resolution output.
- Flag suspiciously empty layouts, out-of-bounds text, and low-contrast combinations when feasible.
- Never silently overwrite an approved output; write a version or require an explicit overwrite flag.

An artist should review every final image at thumbnail size and at intended in-game distance. Procedural validation catches mechanical problems; it cannot reliably judge whether the composition is memorable.

---

## 6. Make the physical object in Blender

There are three useful construction levels.

### A. Flat poster plane: default choice

A single thin plane or very shallow mesh with one material is usually sufficient. UVs should fill the poster texture exactly. Give the plane a small offset from the wall so it does not z-fight. Add a subtle edge thickness only if it will be visible from the player camera.

### B. Paper poster with physical edge

For a closer hero prop, use a thin quad/solidify shell or a shallow mesh with:

- Slightly rough paper material.
- A tiny bend or curled corner.
- A narrow, dark edge or visible paper thickness.
- Optional tape, staples, pin, or paste marks as separate low-cost geometry.

Keep the poster face nearly planar so its image remains crisp and easy to render. The geometry should support the story: freshly posted, cheap handbill, carefully framed promo, or repeatedly layered wall.

### C. Poster cluster / wall collage

Build a reusable wall dressing set with a few size tiers and overlap rules. Avoid placing dozens of individually unique high-resolution textures if a smaller set of authored poster sheets can sell the same wall. A collage sheet can be a single atlas texture mapped to a wall panel, while a few close posters remain separate objects.

### Physical material guidance

The printed face is mostly diffuse. Use modest roughness variation to suggest ink and paper; avoid strong metallic response unless the art depicts foil. A little normal or bump detail can help close-up surfaces, but it should not make the poster look like leather or stone. Taped plastic sleeves and glossy coated prints can use a distinct material, but reserve them for believable cases.

If the design has transparent torn-away regions, use alpha scissor for mostly binary cutouts when appropriate. Avoid alpha blending for ordinary rectangular posters. A backing paper surface or an opaque damaged-paper image is generally simpler.

---

## 7. Godot 4.7 integration

### Recommended scene structure

For a placed poster, use a small reusable scene such as:

```text
Poster (Node3D)
├── Face (MeshInstance3D)
├── Backing (MeshInstance3D)   # optional
├── Fasteners (MeshInstance3D) # optional, shared mesh/material
└── CollisionShape3D           # only if interaction needs it
```

The face can be a `QuadMesh` or imported low-poly mesh with UVs. Apply a `StandardMaterial3D` whose Albedo texture is the rendered poster image. Use opaque rendering, enable mipmaps through 3D texture import, and set the material roughness to suit the paper. If you need a project-specific shader for tint, fade, or palette effects, start from the same simple opaque surface behavior.

For batches of different posters, assign the texture per instance or use a texture atlas / shared material strategy if profiling shows material changes are costly. Do not make one unique complex shader per poster.

### Import and texture settings

Godot imports image files as textures. For 3D use, make sure the import produces mipmaps and an appropriate compression mode for the target renderer/platform. Mipmaps reduce shimmering and grain at distance. Review compressed output for banding in flat gradients, tiny type disappearing, and halftone patterns turning into moiré. If a poster is a deliberately pixelated or highly graphic image, compare VRAM compression against lossless import and choose based on measured quality and memory needs.

Keep source artwork in the project, but distinguish it from runtime-ready art so large working files are not accidentally used in scenes. A clean structure could be:

```text
art/posters/source/       # editable .blend, data, source PNGs
art/posters/runtime/      # approved imported textures / atlas pages
scenes/props/poster/      # reusable scene and material
```

Godot can import Blender scenes, and glTF/GLB is a recommended interchange route for 3D assets. For the poster image itself, importing the rendered PNG directly is simpler than embedding the entire authoring scene. Export a small GLB only when the physical prop geometry is useful.

### Wall placement and z-fighting

Place the face just in front of the wall surface. For a poster mounted on a wall with normal `n`, use a small offset such as a few millimeters in world scale, then inspect grazing angles. Avoid coplanar faces. If the wall is curved or irregular, use a conforming mesh or decal-like approach; a flat plane can visibly float or cut into the wall.

A slight shadow gap and a thin paper edge often communicate attachment better than a dramatic shadow. Keep the plane almost flush; a large offset makes it look like a floating UI card.

### When to use a Decal instead

Use a `Decal` when the art should project onto a surface or conform across wall detail, and when the project uses a renderer that supports decals. In Godot 4.7, Decals are supported in Forward+ and Mobile, but not Compatibility. They project onto surfaces rather than adding real geometry. A plane is the safer default for a rectangular physical poster and provides predictable UVs and sorting. Test decals on the target renderer and wall material before committing.

### Lighting and readability

Do not make the poster emissive just to preserve readability. Let the room light it. If a key word or image disappears in the expected lighting, revise the design contrast or use a plausible local fill light in the environment. In a dim location, paper often reflects a little ambient illumination while colors remain muted; a saturated self-lit rectangle will look like a screen.

Test the poster in:

- The actual level exposure and color grading.
- Bright and dim versions of the room if the lighting changes.
- Front-on and oblique player-camera angles.
- The lowest expected resolution and performance mode.
- The intended distance, with motion and the normal field of view.

### LOD and visibility

A small poster is usually cheap in geometry, but texture memory and overdraw scale with the number of unique images. Use a few authored distance tiers:

- Close: full-resolution texture, visible paper edge and fasteners.
- Medium: same face texture, no tiny geometry details.
- Far: lower-resolution texture or a shared poster-wall atlas.

Use distance visibility or level streaming where the scene contains large numbers of posters. Avoid keeping many large unique texture resources resident for distant rooms if the project can unload or atlas them.

---

## 8. Texture budgeting and visual fidelity

A 1024 × 1536 RGBA8 image is about 6 MiB before mipmaps and compression; a full mip chain adds roughly one third before platform-specific compression. Actual runtime memory depends on the import format and renderer. A 2048 × 3072 image is four times the base texel count of 1024 × 1536. This is why close inspection should be intentional rather than the default for every wall prop.

A practical policy:

- Distant props: 512–768 px on the long edge.
- Standard posters: around 1024–1536 px on the long edge.
- Hero posters: 2048 px on the long edge only when players can approach and read detail.
- Use an atlas for walls of many small posters when independent interaction is unnecessary.
- Reuse paper, tape, fastener, and frame materials.
- Avoid separate normal/roughness maps unless close-up lighting makes them matter.

Check for color banding in large flat fields and inspect very small type after mipmapping. If small print is only there to imply authenticity, its texture-like appearance is acceptable. If it carries gameplay information, provide readable authored text or an interaction/UI treatment rather than expecting the poster texture to serve as a scalable interface.

---

## 9. Reuse, atlases, and variation without repetition

A convincing wall should not look like the same poster stamped everywhere. Build a manageable content library with variation in:

- Poster family and aspect ratio.
- Main silhouette and image scale.
- Dominant palette.
- Type hierarchy and direction.
- Paper condition and attachment method.
- Wall placement, overlap, rotation, and age.

A modest set of 12–24 well-differentiated posters can dress many rooms if placement, scale, and condition vary. Keep hero pieces unique and let background posters repeat more freely.

For atlas workflows:

- Pack posters into a regular grid or designed sheet with gutters.
- Add sufficient edge padding to reduce neighboring-tile bleeding in mipmaps.
- Keep atlas UVs away from tile borders.
- Use consistent resolution per tile.
- Do not put hero posters and tiny background stickers in the same atlas if they need radically different mip behavior.

A poster atlas is useful for a large static collage; individual textures are easier when posters are inspectable, destructible, or swapped at runtime.

---

## 10. Quality checks

### Design review

- Is the first read obvious in one second?
- Does the poster belong to the correct family, place, and era?
- Does the image support the message rather than compete with the title?
- Is the palette controlled and distinct from nearby posters?
- Does it look authored, not merely randomized?
- Are names, dates, and marks intentional and free of accidental real-world references?

### Texture review

- Are margins and trim respected?
- Is any text clipped or unintentionally too small?
- Does wear support the material story and preserve focal areas?
- Does the image hold up after downsampling and mipmapping?
- Are there compression artifacts, moiré, or unintended transparent edges?

### In-engine review

- Does the face sit cleanly on the wall at all camera angles?
- Does it read under actual level lighting and color grading?
- Is the paper too glossy, too bright, or too dark?
- Does it shimmer at distance?
- Is the chosen resolution justified by the player's approach distance?
- Does it work with the project's renderer and target hardware?
- Are collision and interaction present only when required?

### Batch validation

For generated batches, render a contact sheet and inspect it for:

- Duplicated or near-duplicated compositions.
- Weak or unreadable title contrast.
- Repeatedly awkward line breaks.
- Text outside the safe area.
- Accidental image crops through faces or important symbols.
- Overuse of the same palette, texture, or layout.
- Broken fonts or missing assets.

---

## 11. Common failure modes

| Failure | Why it happens | Fix |
|---|---|---|
| Every poster looks like the same template | Variation changes only the words or color | Create distinct family grids, image treatments, and aspect ratios |
| Too much procedural grunge | Noise is used as a substitute for art direction | Give wear a physical cause and protect the focal image |
| Small text turns into mush | It was judged only at full-resolution render size | Review in-game at intended distance and simplify details |
| Poster looks like a glowing UI panel | Emission or excessive albedo brightness | Use opaque paper, realistic roughness, and level lighting |
| Text or colors blur at an angle | Mipmaps, compression, UVs, or texture resolution are unsuitable | Inspect import settings, use correct UVs, increase source resolution only when justified |
| Poster flickers against wall | Coplanar surfaces | Offset the face slightly or use a conforming mesh |
| Decal disappears or behaves differently across platforms | Renderer support differs | Verify Godot renderer; use a plane for compatibility |
| Generated designs feel random | Seed has too much authority | Use weighted choices, bounded ranges, and artist approval |
| Many textures inflate memory | Unique high-resolution outputs for every placement | Reuse, atlas, reduce resolution, and stream by level |
| Materials look plastic | Strong specular/low roughness or wrong normal scale | Keep paper rough, subtle, and mostly diffuse |

---

## 12. A minimal team pipeline

1. **Art direction:** Define location, era, purpose, family, and one-sentence hook.
2. **Content record:** Fill the text, motifs, palette ID, wear profile, and seed.
3. **Layout:** Choose a family template and establish the hierarchy.
4. **Illustration:** Add or select one strong image anchor; create a specific crop.
5. **Procedural pass:** Apply approved palette reduction, print texture, and restrained wear.
6. **Artist pass:** Adjust the focal point, spacing, contrast, and any awkward generated results.
7. **Render:** Export clean opaque PNG at the target resolution; generate contact-sheet preview.
8. **Physical prop:** Use a plane by default; add thickness, curl, tape, or staples only when visible.
9. **Godot import:** Apply project texture import settings, material roughness, and wall offset.
10. **Level review:** Check in the real camera and lighting; revise based on actual read distance.
11. **Optimization:** Reduce resolution, atlas, or remove geometry where it does not change the player-facing result.
12. **Catalog:** Record poster ID, family, source file, seed, resolution, intended era/location, and approved placement use.

---

## 13. Suggested reusable generator controls

Expose these as Blender properties or a small UI panel; hide technical node details from artists.

### Design controls

- Family / layout preset.
- Poster ratio and output resolution.
- Headline, venue/brand, tagline, date, supporting copy.
- Display/support font roles.
- Image motif and crop position.
- Palette preset and accent color.
- Border / frame / footer style.
- Density of secondary information.

### Print controls

- Number of inks.
- Halftone enable, screen angle, and scale.
- Registration offset and direction.
- Grain amount and scale.
- Ink spread / edge roughness.
- Paper tone and fiber amount.
- Fade direction and amount.
- Wear profile and seed.

### Prop controls

- Paper thickness.
- Curl corner and amount.
- Tape/staple/pin set.
- Backing color.
- Roughness range.

Provide sensible family defaults. Artists should be able to press “render variant” and get a useful proposal, then lock specific choices while trying others. Include a reset-to-family-defaults button and an explicit `Approved` state for final output.

---

## 14. Deliverables and naming

For each approved poster, keep:

```text
poster_id.blend                 # editable authoring source or link to generator source
poster_id.json                  # content and reproducibility data
poster_id.png                   # rendered poster face
poster_id_preview.png           # optional contact-sheet-sized preview
poster_id.glb                   # optional physical hero prop
```

Suggested identifiers are semantic and stable, such as `gig_bluecomet_014` or `film_midnight_006`, not just `poster_final_final2`. Track seed, output size, family, palette, source art, font licenses, and intended use in the data file or asset catalog.

---

## 15. Short production specification

A finished standard wall poster should meet these defaults unless a family brief overrides them:

- Flat opaque artwork with a deliberate aspect ratio.
- One dominant image or symbol and a readable primary title.
- A controlled palette with a clear foreground/background relationship.
- Small text treated as atmosphere unless intentionally inspectable.
- Procedural print character applied in separate, adjustable layers.
- 1024–1536 px on the long edge for ordinary placements; higher only for close inspection.
- One simple UV-mapped face with a `StandardMaterial3D` in Godot.
- Mipmaps enabled and texture import/compression reviewed in engine.
- Small wall offset to prevent z-fighting; no unnecessary alpha or emission.
- A successful check in the actual scene, lighting, camera, and target renderer.

---

## References

Official documentation consulted for engine and authoring workflow:

- [Godot 4.7: Using decals](https://docs.godotengine.org/en/4.7/tutorials/3d/using_decals.html)
- [Godot 4.7: Standard Material 3D](https://docs.godotengine.org/en/4.7/tutorials/3d/standard_material_3d.html)
- [Godot 4.7: StandardMaterial3D class reference](https://docs.godotengine.org/en/4.7/classes/class_standardmaterial3d.html)
- [Godot 4.7: Importing 3D scenes](https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/importing_3d_scenes.html)
- [Godot 4.7: Importing images](https://docs.godotengine.org/en/4.7/tutorials/assets_pipeline/importing_images.html)
- [Blender Manual: Geometry Node Editor](https://docs.blender.org/manual/en/latest/editors/geometry_node.html)
- [Blender Manual: Compositor](https://docs.blender.org/manual/en/latest/compositing/index.html)

Godot's renderer support and import options can change across releases; use the 4.7 documentation and verify settings in the project's exact renderer and export targets.
