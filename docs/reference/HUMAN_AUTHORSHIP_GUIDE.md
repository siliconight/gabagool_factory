# Human Authorship in Procedural 3D Games
## A visual craft and art-direction guide for Blender and Godot

**Purpose:** Help a 3D game feel authored, specific, coherent, and cared for, whether its assets are hand-built, procedural, AI-assisted, or made with a mix of methods.

## North star: handmade, specific, and cared for

The target is not to imitate an AAA production. The target reaction is: **“This may not look like an AAA game, but it looks like humans placed these things and made this stuff with passion and care.”**

That feeling comes from a visible point of view: what the makers notice, choose, emphasize, simplify, connect, and leave out. It does not come from sprinkling noise, damage, crookedness, asymmetry, or tiny details over an otherwise generic result.

This is a guide to **authored visual decisions**, not a checklist for disguising AI or making every asset look irregular. Appearance and production method are separate questions. A hand-made asset can feel generic; a generated asset can be carefully directed and edited. Judge the work by its meaning, coherence, specificity, and craft—not by trying to guess how it was produced.

Use these tests throughout production:

- **Could a person explain why this is here?** The answer can be practical, playful, emotional, or strange, but it should feel chosen.
- **Can I see the maker’s hand?** Look for authored silhouettes, restrained palette choices, recurring visual motifs, and specific little decisions—not generic decoration.
- **Does each unusual detail have a reason?** A hand-painted sign can be uneven because a person painted it. A repaired object can be mismatched because someone replaced a part with what was available.
- **Does this feel cared for at its intended fidelity?** Low detail, simple geometry, and visible seams are acceptable when they are consistent and considered. Care means checking, editing, and composing—not hiding every limitation.
- **Is there room for the player to notice?** A memorable object needs visual breathing room. Do not fill every surface or corner just because the generator can.

Do not use realism or visual complexity as the definition of quality. Favor clarity, personality, cohesion, and authored decisions at the level the team can sustain.

This guide applies whether assets come from Blender Geometry Nodes, scripts, modular kits, runtime generation in Godot, image or text models, shader graphs, or a hybrid pipeline. It covers environments, props, characters, meshes, materials, textures, signs and other text, lighting, shaders, and the rules that connect them.

---

## The short version

A convincing asset has a point of view, a reason to exist, a clear construction logic, a readable silhouette, and a relationship to the people and spaces around it. It looks like one thing made by someone for a purpose—not a pile of attractive details.

Use this order:

1. **Decide what the work is trying to say or make the player feel.**
2. **Study specific people, places, objects, and processes.**
3. **Make an authored sketch, blockout, or prototype that expresses the idea.**
4. **Choose what deserves attention and what should stay quiet.**
5. **Connect forms and details to use, place, time, and ownership.**
6. **Use procedural systems to extend a decision, not make the decision for you.**
7. **Edit, simplify, and integrate the result into the larger work.**
8. **Review it from the player’s view and ask what the choices communicate.**

Procedural generation is one production method. It can extend authored decisions across a large space, but output volume is not authorship. The human feeling comes from the point of view, standards, edits, and relationships that shape the work.

---

## 1. What makes a 3D game feel generic or under-authored

“AI-looking” is often used to describe visual work that feels generic, over-smoothed, over-decorated, or disconnected from any particular maker or place. These traits are not reliable proof that AI made something. They are useful critique terms for weak visual decisions, regardless of production method.

Common symptoms:

- **Generic identity:** A storefront, weapon, chair, or alley could belong to any game or any place.
- **Detail without purpose:** Greebles, decals, grime, cracks, noise, trim, and tiny labels cover a form without explaining it.
- **Randomness mistaken for naturalism:** Every object differs, but no differences follow from use, manufacture, age, location, or ownership.
- **Uniform irregularity:** Everything is crooked, chipped, dirty, asymmetrical, and over-weathered to the same degree.
- **Material confusion:** Wood looks like stone, painted metal looks like plastic, glass looks opaque, or every surface shares one roughness response.
- **Broken construction:** Parts intersect, float, taper impossibly, lack thickness, have no support, or cannot plausibly be assembled.
- **Texture noise:** High-frequency marks compete with the shape; detail vanishes at gameplay distance or shimmers in motion.
- **AI-text artifacts:** Letter-like scribbles, misspelled labels, gibberish, warped logos, inconsistent typography, or fake microtext.
- **Kit repetition:** The same window, lamp, crate, stain, or silhouette appears at the same scale and angle everywhere.
- **Overdesigned clutter:** Every corner has a focal object, every surface has a decal, and every light has a dramatic color.
- **No visual hierarchy:** The player cannot tell what is structural, interactive, dangerous, decorative, foreground, or background.
- **Style drift:** Individually attractive assets do not look like they belong to the same game, region, decade, or production.
- **Uncurated generation:** Technically valid output is accepted as finished art.
- **Borrowed voice without a point of view:** A recognizable artist, game, or trend is imitated, but the work has no reason for those choices beyond resemblance.
- **Surface-level humanity:** Random scratches, crooked signs, grain, asymmetry, or “quirks” are added as tokens of personality without context or cause.
- **No hierarchy of care:** Every asset receives the same amount and kind of polish, so nothing feels especially noticed, loved, neglected, important, or ordinary.

A useful diagnosis is: **Can a player sense what the makers cared about here?** Then ask: can they understand what this is, who uses it, what happened, and why it looks this way? If not, more detail or more randomness is unlikely to help.

---

## 2. The visual contract: define the game before generating assets

Before generating anything at scale, write a compact visual contract. It is the shared constraint set for artists, procedural tools, and AI-assisted steps.

### 2.1 World identity

Specify:

- **Place:** Where is this, and what local conditions shape it?
- **Time:** What year, season, time of day, and level of maintenance?
- **People:** Who owns, uses, repairs, abuses, or avoids this place?
- **Economics:** What is cheap, durable, improvised, branded, scarce, or neglected?
- **Function:** What does the space or object need to do for play?
- **Tone:** What should the player feel—uneasy, familiar, funny, tense, lonely, busy?
- **Reference boundary:** What broad qualities are useful to study, and what recognizable designs must not be copied?

Avoid briefs that only list adjectives: “gritty, cinematic, realistic, detailed, cool.” Translate each adjective into visible decisions. “Neglected” might mean deferred paint repair, mismatched replacement hardware, faded signage, and a maintained walking path—not random dirt on every surface.

### 2.2 Style rules

Record decisions for:

- Silhouette language: blocky, tapered, thin, heavy, rounded, angular.
- Proportion: door and window sizes, street widths, furniture heights, weapon scale.
- Edge treatment: hard edges, broad bevels, soft wear, chipped corners.
- Detail density: where detail is concentrated and where surfaces stay quiet.
- Color range: dominant, supporting, accent, and reserved gameplay colors.
- Material response: roughness range, metal use, glass behavior, emissive intensity.
- Lighting: contrast, color temperature, practical fixtures, shadow softness.
- Texture scale: approximate size of scratches, dirt, grain, labels, and patterns.
- Text system: type families, sign hierarchy, copy tone, aging, legibility.
- Performance envelope: target platform, camera distance, silhouette budget, transparency limits.

### 2.3 Build a small “golden set”

Make a few excellent examples before building a large generator:

- One street segment or room.
- One hero prop and one ordinary prop.
- One material family.
- One sign or text treatment.
- One lighting setup.
- One interaction marker or gameplay-readable element.

These define the bar. New generated outputs should be compared to the golden set in the target game camera, not to a polished Blender close-up.

---

## 3. Human authorship is a chain of decisions

Human-authored quality is not a special surface texture or a visible mistake. It is the result of connected choices: someone has an idea, studies the subject, makes a version, notices what is wrong or missing, revises it, and decides what deserves to remain.

The player does not need to see every step. They should be able to feel the coherence of those choices in the final work.

### 3.1 What authored decisions look like

- **A point of view:** The work selects what matters. A room may feel cramped, proud, improvised, ceremonial, cheap, or carefully maintained through its forms and choices.
- **Specific observation:** Details come from a particular place, time, user, material, activity, or constraint—not from a generic idea of “gritty,” “cool,” or “realistic.”
- **Prioritization:** Important forms and ideas receive attention. Supporting details stay quiet. Some surfaces remain empty.
- **Relationships:** An object’s shape, wear, placement, text, and lighting agree about what it is and how it is used.
- **Revision:** Weak, redundant, confusing, or purely decorative details are removed or redesigned.
- **Variation in care:** A player can tell what was maintained, repaired, improvised, abandoned, or intentionally left plain.
- **Continuity with exceptions:** A shared visual language holds the work together; meaningful exceptions reveal a person, event, or function.

### 3.2 A maker-led process

Use this loop whether working by hand, with a generator, or with AI assistance:

1. **State the intent.** What is this asset or space for, and what should it communicate?
2. **Observe.** Gather concrete references for construction, use, context, material, and history.
3. **Interpret.** Decide what the references mean for this game. Do not merely copy their surface appearance.
4. **Make a rough version.** Sketch, block out, model, arrange, or prototype the central idea.
5. **Choose and edit.** Keep, change, combine, or discard elements based on the intent.
6. **Connect the details.** Make geometry, placement, material, text, wear, and lighting tell the same story.
7. **Review in context.** Check what the player sees and understands; revise the choices that do not land.

The maker’s contribution is strongest when they can explain why the result has these forms and not other forms. A prompt, seed, or reference can start an exploration; it does not replace interpretation and editing.

### 3.3 Do not fake humanity with surface defects

- Do not add random scratches, unevenness, stains, visual noise, film grain, or tilted objects just to make a result look handmade.
- Do not use “quirky,” “lived-in,” “imperfect,” or “full of soul” as a substitute for specific design decisions.
- Do not assume photorealism, cinematic lighting, dense detail, or messy texture makes work feel human.
- Do not treat a visual “AI tell” checklist as a reliable way to identify how an image was made.
- Do not treat a large batch of candidates and a quick favorite-pick as a complete creative process.

Instead, ask what caused a mark, what task an object supports, why a sign is worded this way, why the player notices one thing before another, and what the work would lose if a detail were removed.

### 3.4 Variation is a supporting technique

Variation helps express authorship when it follows a decision. Choose what changes and what stays consistent based on function, fabrication, ownership, place, and history. Randomness may help explore valid options or distribute non-critical detail, but the visual idea and acceptance criteria remain human decisions.

| Design question | Authored choice | Possible procedural support |
|---|---|---|
| What makes this shop recognizable? | Select a distinctive sign shape, color, and entrance treatment | Generate dimensions and mounting within that authored system |
| Why is this chair worn? | Decide who uses it and where the wear should appear | Apply a bounded wear mask to contact areas |
| How does this room feel occupied? | Define the activity and its meaningful objects | Arrange candidate objects around the activity, then review the composition |
| What makes a street feel local? | Select region-specific architecture, businesses, and habits | Populate compatible building and dressing families |

The table describes where tools can assist. It does not prescribe a randomization-first art process.

---

## 4. Establish visual hierarchy at three distances

Evaluate assets and levels at three scales:

1. **Game distance:** silhouette, route, objective, threat, and major value grouping.
2. **Interaction distance:** use, material, ownership, construction, labels, and wear.
3. **Inspection distance:** small fabrication detail, edge quality, texture transitions, and close-up artifacts.

The first two distances carry the experience. Inspection detail should reward attention without becoming the only reason the object works.

### Rules

- Make the primary form readable before adding surface detail.
- Keep important silhouettes distinct from adjacent geometry and the background.
- Reserve high contrast, saturated color, emissive light, and dense detail for specific priorities.
- Let large quiet shapes exist. Empty space is a designed element.
- Check the asset in grayscale and at thumbnail size.
- Check silhouette without textures, then with final lighting.
- If detail disappears at normal play distance, decide whether it is useful, decorative, or wasteful.
- Keep gameplay cues consistent and distinguishable from decoration.

### No-nos

- Every object has the same outline thickness, bevel width, or detail density.
- Important objects rely on a tiny decal to become recognizable.
- Every edge is beveled because it looks “finished.”
- Every surface has high contrast, making the whole scene equally loud.
- A focal point is surrounded by equally bright competing points.

---

## 5. Procedural assets: make the object make sense

A generated asset should have a functional diagram, even if the game is stylized. Know what its main parts do and how they meet.

### 5.1 Silhouette and proportions

- Start from a recognizable base form and lock its proportions.
- Randomize secondary dimensions only within a range that preserves the category.
- Use a small number of deliberate silhouette families rather than endless tiny tweaks.
- Check front, side, top, and three-quarter views.
- Check whether the object reads against both light and dark backgrounds.
- Preserve believable thickness for boards, sheet metal, glass, doors, shelves, and signs.
- Avoid razor-thin slivers, accidental spikes, near-zero dimensions, and hidden self-intersections.

### 5.2 Construction logic

Ask:

- What supports the weight?
- Where do parts join?
- What material is each part made of?
- How is it manufactured?
- How is it installed, opened, repaired, or replaced?
- What is exposed to weather, impact, heat, water, touch, or traffic?
- Where would fasteners, seams, hinges, welds, brackets, rails, or trim go?
- Can a player plausibly interact with it?

Do not add bolts, screws, seams, vents, handles, or cables as ornamental noise. Each should connect parts, permit use, carry a system, or establish scale.

### 5.3 Asset families and variation tiers

Design a family with tiers:

- **Base:** the canonical form and dimensions.
- **Variants:** authored silhouette or configuration changes.
- **Finish variants:** material/color changes that make sense for the owner or region.
- **State variants:** clean, worn, damaged, repaired, abandoned, or temporary.
- **Placement variants:** orientation, grouping, and contextual dressing.

Keep the number of meaningful choices small enough to curate. Several authored variations with strong shapes usually outperform hundreds of noise-driven variants.

### 5.4 Repetition control

- Track what has appeared recently and in the player’s visible neighborhood.
- Avoid same-silhouette neighbors and obvious repeated clusters.
- Vary spacing and grouping before randomly changing the asset itself.
- Use a few distinct “families” with controlled cross-family mixing.
- Avoid mirrored repetition when mirrored construction would be implausible (text, wear, asymmetrical damage).
- Use rotation and mirroring only when the object supports it.
- Review the full set as a contact sheet, not only one asset at a time.

---

## 6. Mesh and topology rules

### For models and generated meshes

- Establish real-world scale and consistent units at the start.
- Apply transforms and set origins/pivots where placement and interaction expect them.
- Keep normals consistent; check for inverted faces, gaps, and accidental non-manifold areas.
- Keep topology predictable where deformation, collision, or future editing needs it.
- Use bevels where they catch light and describe the material. Match bevel width to scale.
- Avoid tiny bevels that disappear in-game and giant bevels that make everything look like soft plastic.
- Use weighted normals or smoothing deliberately; do not let shading hide a broken silhouette.
- Give collision its own simpler shape when a render mesh is too complex or irregular.
- Keep collision aligned with gameplay intent, not just visual geometry.
- Separate moving parts when they need to move; keep static parts together when useful.
- Use modular dimensions and snap rules where pieces must connect.
- Test seams, pivots, sockets, doors, stairs, and transitions in the actual assembled scene.
- Use LODs or simplified distant forms when the game camera requires them.

### Mesh no-nos

- Coplanar surfaces that flicker or produce z-fighting.
- Floating trim and intersections that imply impossible assembly.
- Unintended paper-thin backfaces visible from gameplay angles.
- Excessive unique bevels and tiny support loops on objects that remain small on screen.
- Flat planes pretending to have physical depth when the camera can see the edge.
- Smooth shading across hard corners or faceted shading across surfaces meant to be smooth.
- Geometry added only because a high-poly model looks impressive in Blender.
- Unchecked normals, transforms, pivots, scale, and collision after export.
- Letting procedural generation output zero-area faces or degenerate triangles.

### Blender-to-Godot handoff

Use an agreed export standard. Validate:

- Scale and axis orientation.
- Object names, material names, node hierarchy, origins, and animation tracks.
- UV sets and material slots.
- Tangents/normals and smoothing.
- Collision naming or collision resources.
- Texture paths and packed resources.
- Whether modifiers are applied or intentionally preserved through the export format.
- Whether the exported result matches Blender’s appearance under Godot’s renderer and color management.

Prefer a test scene that imports a representative asset and shows it under neutral, game-like lighting. Do not sign off from the Blender viewport alone.

---

## 7. Materials and textures: show the material, not the noise

A material should communicate what it is made of and how it has been treated. Its response under light matters as much as its base color.

### 7.1 Material identity

For each material family, set a reference range for:

- Base color.
- Roughness.
- Metallic response.
- Normal/bump strength.
- Texture scale.
- Edge behavior.
- Transparency or emission, if any.
- Expected lighting and environment.

Metal is not “a shiny gray.” Painted metal is mostly a coating; bare metal appears where that coating is worn. Wood grain follows the cut and construction. Concrete has aggregate and casting logic. Glass has thickness, reflections, tint, and context.

### 7.2 Texture scale and frequency

- Choose texture frequency based on the material and the game camera.
- Build forms with low-frequency color and shape first; use finer detail sparingly.
- Make scratches, cracks, grain, stains, and noise scale correctly against nearby objects.
- Test at native game resolution and in motion.
- Use a roughness map or normal map only when it contributes to the material at expected distances.
- Keep texture contrast controlled; use value and hue shifts to support form.
- Ensure UVs do not stretch distinctive patterns or create visible seams.
- Give trims, labels, and unique markings intentional UV space.
- Use tiling with authored variation, decals, vertex color, or masks to hide repetition without destroying material identity.

### 7.3 Use procedural texture with restraint

Procedural noise is good for controlled breakup, masks, and variation. It is bad as a universal layer over every surface.

Use it when it is tied to a material process or environmental cause. Examples: fine aggregate in concrete, subtle roughness variation in paint, directional grain in wood, runoff from a roof edge, dust accumulation on horizontal surfaces.

Avoid:

- Identical noise scale on wood, plastic, metal, skin, and concrete.
- High-contrast noise in base color when roughness would communicate the breakup more naturally.
- Multiple noise nodes stacked without a visual reason.
- Procedural detail that changes unpredictably between exports.
- Repeated texture tiles that are obvious at player height.
- Very fine normal detail that shimmers or reads as dirt from a distance.

### 7.4 Wear and damage should tell a story

Wear depends on **cause, exposure, material, and maintenance**.

- Contact wear: handles, corners, seat edges, push plates, handrails.
- Weather wear: sun-facing paint, roof edges, standing water, windward sides.
- Traffic wear: tire paths, footpaths, loading bays, thresholds.
- Heat/smoke: near grills, engines, exhausts, lamps, industrial equipment.
- Water: drip lines, leaks, pooling, damp corners, rust below damaged coatings.
- Repair: patch material, mismatched paint, replaced panels, fresh fasteners.
- Neglect: failed sealant, peeling layers, weeds, dust, broken hardware.
- Cleaning: scrubbed paths, shiny touch zones, cleaner halos around moved objects.

No-nos:

- Even dirt coverage across all surfaces.
- Damage with no plausible impact or environmental cause.
- Rust on every metal object regardless of exposure or coating.
- Cracks that ignore structure and material.
- The same edge-wear mask repeated on every prop.
- “Grunge” used to make a weak shape look detailed.

### 7.5 Color and palette

- Define a palette by role: structural neutrals, local material colors, signs/brands, gameplay cues, and rare accents.
- Ensure neighboring assets relate, but do not collapse into one color.
- Use saturation selectively. A bright accent should mean something.
- Decide whether dirt darkens, desaturates, warms, cools, or stains each material.
- Keep shadow color and highlights consistent with the lighting model.
- Test palette in grayscale, color-blind simulations if relevant, and target display conditions.

A faded neighborhood does not mean every color is beige. Keep a few crisp, repaired, or colorful elements so wear has a baseline to contrast against.

---

## 8. Text, signs, labels, and generated language

Text is one of the fastest ways to make a scene feel authored—or fake.

### 8.1 Decide if text is readable

Every text element belongs to one of three classes:

1. **Gameplay-critical:** must be correct, legible, localized, and tested at play distance.
2. **Story/identity:** should be intentionally written and checked, even if not always readable.
3. **Set dressing:** can be simplified, but should not look like accidental gibberish when visible.

Do not use generated pseudo-letters for large signs or close-up text. Do not rely on AI image output for exact spelling, logos, labels, serial numbers, or branded copy. Generate layouts and imagery if useful, then replace critical text with actual typography.

### 8.2 Typography hierarchy

For a storefront, station, office, or interior, establish:

- Primary identifier: business, room, street, or institution.
- Secondary information: service, hours, directions, safety, or price.
- Tertiary copy: legal, technical, serial, decorative, or flavor text.

Use typefaces, spacing, sign materials, mounting, and print methods that fit the owner and era. A hand-lettered menu, vinyl window lettering, plastic lightbox, painted wall sign, and laser-printed notice should not share one treatment.

### 8.3 Sign placement on the asset

Treat a sign as a designed part of a building or object, not a flat image dropped onto any empty surface. Give each sign a defined surface, owner, audience, viewing direction, mounting method, and information role.

- Place primary identity where a person approaches or looks for the entrance: fascia, canopy, door glass, wall beside the entrance, or a freestanding roadside sign.
- Place service and hours information near the point where it matters: entrance, counter, window, queue, or service area.
- Place warnings, instructions, and wayfinding at the decision point, before the player must act.
- Put private, operational, or low-priority information where staff would use it, not where it competes with the public-facing sign.
- Align signs to the architecture, storefront bays, door frames, window mullions, and other construction lines. An offset can express improvisation, but it should still look intentionally mounted.
- Match the sign to its support: brackets, standoffs, frame, tape, screws, adhesive, clips, wiring, or a plausible painted surface.
- Give the sign enough backing and border to separate it from the wall. Do not let letters visually collide with trim, window frames, hinges, handles, or nearby objects.
- Keep critical text on a surface that faces the likely approach. If the player must turn or move to read it, treat that as a deliberate navigation choice.
- Do not place critical text across a corner, deep curve, seam, UV island boundary, or highly distorted surface. Split the sign into coherent panels if it must wrap.
- Check sunlight, glare, reflections, shadow, dirt, and occlusion. A technically correct sign can still be unreadable in the actual scene.

For each sign-bearing asset, define a **sign zone**: a normalized rectangle or surface region with allowed bounds, margin, facing direction, and a list of permitted sign types. Keep variation within that zone unless a story-specific exception is authored.

### 8.4 Spacing and layout inside a sign

Build each sign from a simple layout grid before styling it. Set a content area, safe margins, alignment, line count, and hierarchy. Let the material and sign shape determine whether the grid is rigid, hand-adjusted, or improvised.

- Establish a clear primary line, then secondary and tertiary lines. Do not make every line equally large, bold, or high contrast.
- Keep a consistent left edge, centerline, or column structure within one sign. Mix alignments only when the sign’s purpose supports it.
- Preserve visible space around text. As a practical starting range, leave at least half a capital-letter height between the text and the sign’s inside edge; use more for formal, premium, or high-visibility signs. Tighten only when the physical medium or local style calls for it.
- For stacked lines, start around 1.1–1.35 times the type size for compact sign copy, then adjust for the typeface, capitalization, and medium. Avoid collisions between ascenders, descenders, outlines, and shadows.
- Use tracking to set the voice and fit the line. All-caps display lettering may need more open spacing; dense information copy needs stable word shapes. Do not stretch tracking to force a line to fill the sign.
- Keep word spacing visibly smaller than the gap between unrelated groups. Use alignment, a divider, or a larger gap to show that two blocks serve different purposes.
- Allow optical correction after the mathematical layout: circular letters, diagonals, and asymmetric shapes can appear off-center even when their bounds are centered.
- Respect the physical process. Painted lettering may vary slightly; vinyl lettering should be more regular; a printed notice should follow paper margins; a handbill can be crowded but should still have an order.

These are starting values, not universal typography laws. Define project presets for sign types and tune them against the intended camera, language, typeface, and physical medium.

### 8.5 Typography, copy, and asset scale

- Use a small, named type system: display, information, utility, and hand-made or expressive lettering. Assign a purpose to each style.
- Keep a consistent scale relationship between primary, secondary, and tertiary information. A secondary line should not rival the business or room name unless it is the main message.
- Limit the number of type families and weights on one sign. Contrast should come from size, weight, spacing, and placement before adding another font.
- Write copy to fit the available surface. Prefer editing the words over shrinking important text until it becomes unreadable.
- Define capitalization, abbreviation, punctuation, number, and line-break rules for repeated sign families.
- Keep text away from the edge, mounting hardware, folds, tears, stains, and damage unless the story specifically calls attention to those conditions.
- For hand-painted or improvised text, vary letterforms as a coherent hand or process would. Do not combine perfect digital spacing with random individual letter rotations.
- Make a deliberate choice about whether texture, wear, or damage passes over the letters. A faded sign can lose ink consistently; random scratches should not erase the only readable word by accident.

### 8.6 Text on 3D surfaces and in the game camera

For every text asset, record its intended reading distance and importance. Judge legibility by the text’s projected size and angle in the actual game camera, not by its size in Blender or its texture resolution alone.

- Gameplay-critical text must remain readable at the point where the player is expected to act. Test the smallest supported resolution, camera distance, and likely approach angle.
- Story and identity text should be readable from its intended viewing spot. If it is too small to read, simplify it into a clean graphic shape rather than preserving tiny pseudo-copy.
- Set a project-specific minimum on-screen character height for each text class. Use a capture or automated image check at target resolution to find text that falls below that threshold.
- Check foreshortening, perspective, curvature, specular glare, transparency sorting, mip levels, texture filtering, and compression. Text that reads head-on may fail from the player’s side.
- Place unique text in controlled UV regions or use a decal/sign mesh designed for that surface. Avoid stretching text through automatic projections or allowing it to cross unrelated UV islands.
- Give text textures enough padding to prevent neighboring atlas content bleeding into glyphs. Include appropriate gutters and mip-safe space around the lettering.
- For decals, prevent z-fighting and accidental projection onto adjacent surfaces. Use a dedicated sign plane, decal bounds, or material setup appropriate to the engine and renderer.
- Verify normal direction, surface depth, and shadow behavior. Text should not float visibly above glass or sink into a wall unless that is the intended fabrication.
- Test from the player’s movement path, while moving, and under final lighting. A still, straight-on preview is not an adequate sign-off.

### 8.7 Text review checklist

- [ ] The text has a defined role: gameplay-critical, story/identity, or set dressing.
- [ ] The sign has a plausible owner, audience, location, medium, and mounting method.
- [ ] Placement aligns with the asset’s architecture and the player’s likely approach.
- [ ] Hierarchy, alignment, margins, line spacing, and tracking are intentional.
- [ ] Copy fits without distorted scaling or arbitrary letter spacing.
- [ ] Readable text is correct and checked at actual in-game distance and angle.
- [ ] Text avoids seams, corners, hardware, glare, and accidental occlusion.
- [ ] UVs, decal boundaries, padding, mip behavior, and compression preserve clean edges.
- [ ] Weathering supports the sign’s age and material without destroying important words.
- [ ] The sign reads as part of the asset rather than an overlay pasted on afterward.

### 8.8 Text no-nos

- Random strings placed to imply detail.
- AI-generated pseudo-writing on hero-facing surfaces.
- Gibberish at every scale, including large signs.
- Text too small to read but sharp enough to attract attention.
- Uniformly perfect kerning on hand-painted or improvised signs.
- Inconsistent spelling, capitalization, phone-number formats, or business names.
- A sign with no plausible mounting, power, weathering, or relationship to the building.
- Repeating the same fake brand, slogan, or label in every room.
- Centering every sign, regardless of its architecture, reading direction, or purpose.
- Using identical margins and line spacing for a handbill, shop fascia, control panel, and street sign.
- Shrinking text to fit long copy instead of editing the copy or changing the layout.
- Placing text where the surface is too oblique, reflective, curved, cluttered, or distant to read.
- Letting text cross a seam, corner, trim piece, window frame, or atlas boundary by accident.
- Randomly rotating individual letters to make a clean sign look handmade.
- Using a whole sign as one large texture when separate, reusable text and backing would give better control.

For distant dressing, use clean shapes and value groupings that suggest sign layout rather than fake text. At interaction distance, write actual copy or omit the detail.

---

## 9. Levels and environments: compose systems, not random placements

A generated level must support movement, decisions, sightlines, combat, navigation, and mood. A scatter of attractive props is not a designed space.

### 9.1 Start with the player experience

Before dressing, define:

- Objective, entry, exit, and critical route.
- Player movement envelope and cover needs.
- Sightlines, blind corners, landmarks, and readable navigation.
- Combat spaces and safe transitions.
- Interaction locations and interaction clearance.
- Expected enemy, player, and prop densities.
- Where the camera is likely to face.
- What changes during play: alarm state, doors, lights, hazards, damage, crowds.
- What the player should notice first, second, and later.

### 9.2 Spatial hierarchy

Build in layers:

1. **Primary structure:** streets, rooms, walls, floor levels, large openings.
2. **Gameplay structure:** routes, cover, chokepoints, traversal, objectives, readable affordances.
3. **Secondary structure:** counters, shelves, vehicles, machinery, furniture, large dressing.
4. **Tertiary detail:** litter, decals, small clutter, signs, wires, loose objects.
5. **Atmosphere:** lighting, fog, audio occlusion, particles, animated environmental cues.

Do not use tertiary detail to compensate for weak primary structure or empty gameplay.

### 9.3 Placement rules

- Snap objects to floors, walls, shelves, curbs, counters, and architectural axes.
- Respect gravity, balance, access, human reach, service clearance, and vehicle envelopes.
- Cluster objects around activities: work, rest, storage, queueing, selling, repair, concealment.
- Preserve negative space where people move, work, wait, or look.
- Make wear and clutter support a plausible daily routine.
- Use deliberate asymmetry. Human spaces are not uniformly scattered.
- Preserve signs of human decisions: a useful workaround, a repaired mismatch, a personal keepsake, a hand-adjusted arrangement, or a locally specific choice.
- Give important props a small number of memorable, authored details. One distinctive detail is often stronger than twenty generic ones.
- Let objects overlap only when their shapes and placement make the overlap believable.
- Align repeated architecture where construction would align it; vary the parts that would actually vary.
- Keep focal dressing out of important combat readability unless it supports gameplay.

### 9.3.1 Give every asset a placement contract

Do not make the placement generator guess what an asset can do. Store placement information with the asset or its definition so the generator can choose valid positions and reject invalid ones.

At minimum, define:

- **Root and pivot:** the stable origin used for placement, rotation, animation, and snapping.
- **Contact point or support plane:** the part that rests on the floor, counter, shelf, wall, ceiling, vehicle, or another asset.
- **Front and use side:** the direction the asset faces, opens, serves, or is approached from.
- **Allowed surfaces:** floor, wall, ceiling, counter, shelf, curb, vehicle bed, or another named surface type.
- **Allowed orientations:** fixed, wall-aligned, road-aligned, freely rotated, or a curated set of angles.
- **Clearance volumes:** space needed for doors, drawers, service access, player interaction, seating, queueing, movement, and maintenance.
- **Neighbor rules:** which objects may attach, touch, overlap, or must remain separated from this asset.
- **Scale and density class:** hero, major dressing, ordinary prop, or small clutter, with project-defined count and spacing ranges.
- **Gameplay role:** cover, obstacle, landmark, interaction, decoration, boundary, or background.

Use semantic anchors such as floor_contact, wall_mount, counter_surface, sign_zone, interaction_front, door_swing, and service_clearance. An anchor is a named position and orientation in the asset’s local space. It lets one generator place a menu on a counter or a notice beside a door without relying on hand-tuned world coordinates.

### 9.3.2 Place in a deliberate order

Generate or author the layout in passes. Later passes should respond to the earlier ones rather than compete with them.

1. **Structure:** room shell, street edges, doors, windows, stairs, and major openings.
2. **Gameplay:** objective, route, cover, traversal, interaction points, threat lanes, and required clearance.
3. **Functional furniture and machinery:** counters, shelves, workstations, appliances, vehicles, and storage.
4. **Activity clusters:** objects that explain work, rest, selling, repair, waiting, eating, or concealment.
5. **Identity:** business signs, local notices, distinctive props, and story evidence.
6. **Small dressing:** litter, loose objects, decals, minor damage, and surface detail.

Lock important earlier passes before generating later dressing. Small-prop regeneration should not silently move the objective, close a route, or change a combat sightline.

### 9.3.3 Use zones, masks, and exclusions

Give each room, street segment, or exterior area a set of placement zones. Examples include public path, work surface, queue, storage, service access, display, private staff area, combat lane, and backdrop edge.

- Each zone has an allowed asset class, density preset, orientation rule, and clearance rule.
- Use weighted masks to express likely placement: high near a work surface or entrance, lower in a route, and zero in an interaction or safety clearance.
- Keep exclusion zones around door swings, stairs, objective interactions, camera-critical sightlines, combat lanes, and traversal edges.
- Generate a small number of coherent clusters around an activity, then leave space between clusters. Avoid uniform prop density.
- Use project-authored density presets such as sparse, ordinary, busy, and cluttered. Define their count or occupied-area ranges per room type; do not use one universal density value for a kitchen, shop floor, alley, and office.
- Treat clutter density as a budget. Stop placing when the zone’s occupied footprint, collision, or visual noise reaches its limit.
- Give outdoor dressing environmental masks: debris gathers at edges, corners, drains, and wind traps; plants need suitable ground and light; parked vehicles need access and turning space.

Random placement is allowed only after the valid zones and exclusions are established. Use deterministic seeds and stable candidate order so a rejected object does not reshuffle the entire room.

### 9.3.4 Compose for the player’s view

Placement should work in the level and in the camera. Review both the plan view and the likely player path.

- Establish what the player should notice first, second, and only on inspection.
- Keep the main landmark and objective distinguishable from the surrounding prop population.
- Avoid placing similar silhouettes at equal spacing along one sightline unless the architecture intentionally repeats them.
- Break long repeated rows with meaningful changes: an entrance, repair, business sign, parked vehicle, change in height, or a deliberate gap.
- Use foreground, middle ground, and background groups. Do not crowd all depth planes with equally detailed props.
- Preserve a clean silhouette around characters, enemies, doors, interactables, and route openings.
- Review from entrances, corners, cover positions, stairs, and expected combat viewpoints, not just from the level editor’s default camera.
- Track duplicate silhouettes and bright accents within a visible camera region, not only by total level counts.
- Use negative space deliberately. A clear patch of counter, wall, sidewalk, or floor can make surrounding objects feel more specific.

### 9.3.5 Set clearances and human-scale spacing

Use project-specific measurements in Godot units, based on the player capsule, animation reach, camera, and interaction system. Do not invent a universal “human scale” value and assume every game needs the same one.

Define and test at least:

- Minimum clear route width and head clearance.
- Player turning and passing space at doors, corners, stairs, and between furniture.
- Door, drawer, gate, cabinet, and machinery operating envelopes.
- Interaction reach and the space needed to stand at each interaction point.
- Queue, seating, work, and service clearances for common activities.
- Cover height and width relative to the player and camera.
- Vehicle approach, parking, loading, and turning envelopes where applicable.
- Separation between overlapping collision shapes and visual meshes.

Show these as debug volumes or editor overlays. Reject an arrangement when required clearance is violated, even if the render looks attractive.

### 9.3.6 Attachment, contact, and alignment checks

- Align floor props to the support plane; align wall props to the wall normal; align furniture to relevant room or counter axes.
- Use contact points to prevent hovering, floor penetration, or props resting on an accidental corner.
- Permit local offsets and crookedness only within a chosen preset, and only for objects that could be moved by people or time.
- Keep manufactured repetition aligned where the construction process would align it: tile courses, shelving, window rows, ceiling lights, and service counters.
- Use small positional or rotational variation for movable objects, not for built-in fixtures or signs whose layout depends on the architecture.
- Check intersections against both render geometry and gameplay collision. A mesh can look separated while its collision blocks the route.
- When an item is attached to another asset, record the relationship so replacing or moving the parent carries the child correctly.

### 9.3.7 Measure spacing without making it mechanical

Use a project scale and spacing presets as guardrails, then make authored exceptions. For each prop class, define a minimum separation, preferred spacing band, allowed overlap, and maximum local density. For each zone, define an occupancy range or placement count that fits its use.

Do not apply identical gaps everywhere. Manufactured systems may repeat precisely; furniture may follow a loose functional layout; personal clutter may cluster around a task; litter may accumulate against edges. The spacing pattern should reveal what placed or moved the objects.

### 9.4 The “why is this here?” test

For each prominent object, answer at least one:

- Who put it here?
- What task does it support?
- What event left it here?
- What route or boundary does it mark?
- What gameplay purpose does it serve?
- What does it tell us about the owner or inhabitants?

Remove or relocate objects with no useful answer, especially if they compete for attention.

### 9.5 Environmental storytelling

Use evidence, not piles of props. A story beat can be communicated through:

- A missing object and its clean outline.
- A repaired break that contrasts with surrounding neglect.
- A route of repeated contact or movement.
- A recently used tool beside an unfinished task.
- A closed door with signs of forced access.
- A business adapting a space for a new use.
- A mismatch between official signage and improvised local behavior.

Make clues spatially coherent. Keep the player’s likely viewpoint and movement path in mind.

### 9.6 Level-generation no-nos

- Uniform prop density in every room and street.
- Random clutter that blocks navigation, interaction, or combat.
- Doors, stairs, counters, or cover at inconsistent scale.
- Repeated room layouts with only different textures.
- Every street dressed to the same density and cleanliness.
- Decorative objects placed without attachment, access, or support.
- Procedural set dressing that obscures landmarks, objectives, or enemy silhouettes.
- Scattering foliage, debris, or litter on surfaces where it would not accumulate.
- Randomly placing lights without accounting for circuits, fixtures, shadows, and exposure.
- Filling empty areas because emptiness feels unfinished. Some spaces should breathe.
- Making every object perfectly centered, evenly spaced, and showroom clean when the setting calls for lived-in human use.
- Making every object crooked, dirty, broken, or quirky to prove that it was “handmade.” Human presence also includes routine, maintenance, and ordinary order.
- Using world-space random coordinates where a local surface anchor or activity zone is available.
- Rotating built-in fixtures, signs, shelves, or architecture as if they were loose clutter.
- Filling a room with independent uniform samples instead of a few functional clusters and clear paths.
- Allowing small dressing to alter the approved route, objective access, combat lanes, or sightlines.
- Measuring only total props per room while ignoring occupied footprint, collision, visual noise, and camera view.
- Using one spacing rule for architecture, furniture, movable props, and litter.
- Treating a visually plausible placement as valid without checking collision, interaction reach, or operating clearance.

### 9.7 Use intentional rhythms

Good environments have patterns and exceptions: repeated windows with occasional repairs; a regular row interrupted by a boarded opening; a corridor that narrows toward a decision; clean public frontage and a cluttered service side. Establish the rule, then break it with a reason.

---

## 10. Lighting and atmosphere

Lighting should reveal the design and direct attention. It should not be a post-processing cover for weak materials or composition.

### Rules

- Begin with a readable base exposure before adding mood.
- Distinguish key light, fill/ambient, practical fixtures, and effects.
- Give each practical light a believable source and throw.
- Use brightness, color, and shadow to establish visual hierarchy.
- Preserve dark detail where the player needs information.
- Avoid placing every important object under a bright pool.
- Choose a limited lighting palette for each space and let functional fixtures motivate exceptions.
- Check the scene at gameplay exposure, on the intended display, and in motion.
- Test dynamic and static lighting choices against real scene performance.

### No-nos

- Teal/orange contrast applied everywhere without a story reason.
- Neon or emissive accents on every surface.
- Pure black shadow zones that hide useful geometry.
- Bloom so strong that text and silhouettes smear.
- Every room lit like a portfolio render instead of its actual use.
- Multiple colored lights fighting without a focal hierarchy.
- Emission used as a substitute for a light source when the engine setup requires actual illumination.
- Lighting artifacts hidden by fog, glare, or color grading.

---

## 11. Shaders: one clear job, controlled behavior

Every shader should have a short purpose statement. If its job cannot be explained in one sentence, it may be doing too much.

### Shader rules

- Expose only parameters that artists or procedural systems need.
- Set documented ranges, default values, and safe fallbacks.
- Keep shader behavior stable across asset scale and coordinate systems.
- Use masks and material inputs where they offer useful art direction.
- Respect normals, tangents, UVs, and color-space expectations.
- Avoid screen-space effects that break at edges, camera motion, or different resolutions.
- Test under multiple lights, distances, angles, and output resolutions.
- Profile in Godot on target hardware and use the actual renderer.
- Keep shader variants and feature toggles understandable and intentional.
- Prefer a small number of reusable shader families with curated parameters to many nearly identical one-offs.

### Shader no-nos

- Noise everywhere because the result looks “procedural.”
- Expensive layered effects on assets that occupy few pixels.
- Unbounded parameters that create broken output.
- Hard-coded world coordinates that make materials slide or pop as the object moves.
- Excessive transparency, screen-space distortion, or overdraw.
- A shader that only looks good under one preview light.
- Duplicating built-in material features in custom code without a visual or performance reason.
- Adding visual effects before verifying basic albedo, roughness, normals, and exposure.
- Runtime randomness that changes material identity every frame or produces flicker.

Treat shader complexity as part of the art budget. A subtle shader that survives motion and varied lighting is better than a spectacular still frame that fails in play.

---

## 12. AI-assisted asset generation: use it as input, not authority

Image, text, and 3D models can help explore shape language, reference options, rough blockouts, decal concepts, or variation ideas. They do not know your project’s scale, gameplay, style rules, topology needs, text requirements, or asset naming conventions unless your workflow enforces them.

### Good uses

- Mood and reference exploration.
- Shape and silhouette alternatives.
- Color-blocking and material studies.
- Background dressing concepts.
- Draft labels and non-critical flavor copy, followed by human editing.
- Rough proxy meshes that are rebuilt or validated before production.
- Generating candidates for curation rather than shipping every output.

### Required cleanup

- Verify ownership, licensing, and provenance for inputs and outputs according to project policy.
- Check topology, normals, scale, UVs, materials, pivots, collision, and optimization.
- Replace broken or meaningless text.
- Remove unnecessary detail and artifacts.
- Rebuild inconsistent parts around a clear construction logic.
- Match the project’s palette, proportions, material response, and detail scale.
- Test in the game scene, not only in a turntable render.
- Record what was generated, edited, approved, and exported when provenance matters.

### No-nos

- Treating “looks plausible in a render” as production readiness.
- Shipping raw generated meshes with non-manifold geometry, hidden intersections, or unusable UVs.
- Accepting fake text, broken logos, malformed hands/faces, or inconsistent repeated parts because they are small.
- Using generated style references as a replacement for a written art direction.
- Asking a model to create “a realistic game asset” without scale, use, material, era, camera, and constraints.
- Generating hundreds of variants and assuming curation will happen later.

---

## 13. Tools should extend human judgment

A procedural or AI-assisted tool should give artists more room to think, shape, and revise. It should not act like an oracle that returns a finished answer or a “big red button” that hides how the result was made. Keep meaningful choices visible and editable.

### 13.1 Generator specification

Every generator should define:

- **Purpose:** what it creates and what it does not create.
- **Inputs:** dimensions, context, seed, style preset, functional needs.
- **Output schema:** nodes, mesh parts, materials, labels, metadata, collision.
- **Constraints:** allowed ranges, adjacency, scale, clearance, alignment, material rules.
- **Placement metadata:** root, contact point, front/use side, allowed surfaces, anchors, clearance volumes, and neighbor rules.
- **Variation model:** which values vary, their distributions, and what drives them.
- **Determinism:** same input and seed should reproduce the same output.
- **Rejection rules:** conditions that make output invalid or visually implausible.
- **Review hooks:** thumbnails, wireframe, collision, UV, material, and in-engine preview.
- **Human control:** controls for intent, selection, local edits, exclusions, undo, and comparison of alternatives.
- **Decision history:** record what was generated, what a person changed or rejected, and which choices are locked.
- **Performance limits:** mesh count, surface count, texture budget, overdraw, shader cost.
- **Failure behavior:** clear fallback asset or error rather than malformed output.

### 13.2 Use semantic parameters

Prefer parameters like:

- business type, construction decade, maintenance level, owner, weather exposure;
- room function, player route, cover density, sightline priority;
- material family, repair state, age band, sign type, fixture type.

Avoid exposing only opaque parameters like noise strength, random amount, distortion, and detail count. Semantic inputs give artists and designers direct control over the reason for variation.

### 13.3 Support deliberate iteration

- Let artists compare alternatives side by side against the stated intent, not just browse an undifferentiated stream of outputs.
- Allow the artist to keep, replace, or locally edit one decision without discarding the rest of the work.
- Lock approved choices so exploration in one area does not undo intentional work elsewhere.
- Make it easy to sketch or block out a direction before generating finished assets.
- Keep seeds and source inputs reproducible for debugging and collaboration, but do not make seed browsing the primary creative interface.
- Store decisions with the output: what was selected, changed, rejected, or intentionally left out.
- Regenerate only when it serves the brief; do not keep iterating after the work already communicates clearly.

### 13.4 Reject bad output automatically

Useful validation checks include:

- Minimum and maximum dimensions.
- No degenerate faces or inverted normals.
- Valid UV bounds and required UV sets.
- No forbidden material or shader features.
- Collision coverage and interaction clearance.
- Placement-zone membership, forbidden-zone overlap, asset orientation, support contact, and clearance volumes.
- Sign-zone bounds, text-safe margins, facing direction, and minimum in-camera size by text class.
- Door, stair, shelf, table, and human-scale constraints.
- Object intersections, floating geometry, floor penetration, and unsupported parts.
- Readable silhouette and gameplay sightline constraints.
- Text validation for spelling, character set, and field length.
- Mesh, material, texture, and shader budgets.
- Duplicate detection within a visible region.
- Missing references, textures, nodes, collision, or metadata.

Automated checks catch technical defects and constraint violations. Art review decides whether the result expresses the idea, belongs in the scene, and deserves to remain. Both are required, and passing the first is not approval for the second.

---

## 14. A practical production workflow

### Step 1: Write the brief

One paragraph for purpose, place, time, user, gameplay role, style, and exclusions.

### Step 2: Gather concrete references

Collect references for shape, construction, materials, use, wear, signs, lighting, and context. Annotate what is being learned from each. Do not build a mood board made only of attractive images.

### Step 3: Make a grayscale blockout

Build the major silhouette and spatial arrangement. Confirm scale, route, interaction, and player readability.

### Step 4: Lock the style rules

Set the palette, proportion, detail scale, edge treatment, material ranges, typography, and lighting logic.

### Step 5: Author the first high-quality example

Make one asset or environment through a clearly directed process. This is the benchmark for intent, craft, and what the work should communicate.

### Step 6: Build or choose tools around the authored example

Use tools to support the actual art direction: expose meaningful controls, keep decisions editable, and make it possible to compare, revise, and reject output at a useful level of detail.

### Step 7: Explore only the alternatives the decision needs

Make a few sketches, blockouts, models, or candidate layouts. Stop exploring when one clearly serves the brief; more candidates do not automatically mean more thought.

### Step 8: Revise the work and the system

Remove, redraw, rearrange, or rebuild choices that do not serve the idea. Improve the tool when it repeatedly obstructs good decisions. Hand-author or closely direct unique, focal, close-up, and gameplay-critical assets.

### Step 9: Import into Godot

Verify material conversion, scale, normals, transparency, texture filtering, LODs, collision, lighting, and renderer behavior.

### Step 10: Review in play

Use the actual player camera, movement speed, target resolution, lighting, and combat or interaction context. Capture screenshots while moving, not just still renders.

### Step 11: Profile and simplify

Measure actual frame cost. Remove invisible work, excessive surfaces, redundant textures, avoidable transparency, or shader features that do not contribute at play distance.

### Step 12: Record the approved recipe

Save source parameters, seed, tool version, asset version, manual edits, and known limitations. Keep the approved output reproducible.

---

## 15. Review rubric

Score each category from 0 to 2:

- **0 — Fails:** distracting, incoherent, broken, or unclear.
- **1 — Acceptable:** works, with visible issues or limited specificity.
- **2 — Strong:** intentional, readable, coherent, and ready for the target use.

| Category | Review question |
|---|---|
| Identity | Does it belong to this particular game, place, time, and owner? |
| Silhouette | Does it read at gameplay distance without relying on texture? |
| Function | Can a player understand what it is and how it is used? |
| Construction | Do parts, supports, joins, and materials make sense? |
| Authorship | Can the team explain the point of view and the choices that make this result specific? |
| Meaning | Do form, placement, text, materials, and wear support the same idea? |
| Variation | Does it differ for a believable reason and fit the asset family? |
| Material | Does each surface respond like the material it represents? |
| Texture | Are scale, contrast, seams, and detail appropriate in motion? |
| Text | Is readable text correct, intentional, and placed plausibly? |
| Composition | Does it support the space, route, focus, and gameplay? |
| Style | Does it match the golden set and visual contract? |
| Technical | Does it import, shade, collide, and perform correctly in Godot? |
| Curation | Has someone rejected weak output and reviewed the full population? |

**Suggested gate:** No zero in identity, silhouette, function, style, or technical. A high total score cannot compensate for a critical failure.

---

## 16. Fast review checklists

### Before generation

- [ ] I can describe the asset’s purpose and owner.
- [ ] Scale and camera distance are known.
- [ ] The shape and material references are concrete.
- [ ] The generator exposes semantic controls.
- [ ] Variation has causes, limits, weights, and stable seeds.
- [ ] Gameplay and performance constraints are included.
- [ ] Text requirements are explicit.
- [ ] Assets have placement metadata: support point, orientation, allowed surfaces, clearance, and neighbor rules.
- [ ] Rooms and outdoor spaces have named zones, density presets, and exclusion masks.

### Before approving a model or prop

- [ ] Silhouette reads without texture.
- [ ] Scale, pivot, normals, and transforms are correct.
- [ ] Construction and support make sense.
- [ ] Materials are distinguishable under game lighting.
- [ ] Texture scale and detail hold up in motion.
- [ ] No accidental intersections, floating parts, or fake text.
- [ ] Collision and interaction clearance work.
- [ ] It belongs to the intended family without looking duplicated.
- [ ] It has a correct pivot, support/contact point, allowed orientation, and required semantic anchors.

### Before approving a generated level

- [ ] The primary layout supports objectives and player movement.
- [ ] Sightlines, cover, routes, and landmarks are readable.
- [ ] Prop density changes with function, not uniform noise.
- [ ] Objects rest on and attach to the world convincingly.
- [ ] Dressing does not block combat, navigation, or interaction.
- [ ] Repetition is controlled across the player’s visible area.
- [ ] Lighting has sources and a hierarchy.
- [ ] Empty space has been reviewed as an intentional choice.
- [ ] Placement was reviewed from the player path and key camera positions.
- [ ] Routes, interactions, door swings, service access, and combat sightlines pass clearance checks.
- [ ] Prop density forms meaningful clusters and varies by zone function.
- [ ] Duplicate silhouettes and high-contrast accents are controlled within visible regions.

### Before shipping a shader or material

- [ ] Purpose and exposed parameters are documented.
- [ ] Defaults are safe and values are bounded.
- [ ] It works across multiple lights and camera angles.
- [ ] Texture coordinates remain stable.
- [ ] Transparency and overdraw are justified.
- [ ] It performs on the target renderer and hardware.
- [ ] The visual benefit is visible at game distance.

### Before approving signage or text on a prop

- [ ] The sign has a role, owner, audience, surface zone, and viewing direction.
- [ ] Text hierarchy, alignment, margins, tracking, and line spacing fit the medium.
- [ ] Critical text is tested at target resolution and expected player distance.
- [ ] Text avoids seams, corners, hardware, glare, and accidental occlusion.
- [ ] Mounting, UVs or decal bounds, padding, and wear have been checked in Godot.

### Final “slop” pass

- [ ] Remove details that have no function, cause, or identity.
- [ ] Reduce noise and contrast where everything is shouting.
- [ ] Replace gibberish with correct text or clean shapes.
- [ ] Fix repeated silhouettes and repeated damage patterns.
- [ ] Look for objects that float, intersect, or ignore gravity.
- [ ] Compare the whole scene to the golden set.
- [ ] Ask a person unfamiliar with the generator what the scene is and where they look first.

---

## 17. Rules worth keeping on the wall

1. **Specificity beats detail.**
2. **A clear point of view beats generic polish.**
3. **Human authorship is visible in the choices that connect the work.**
4. **Imperfections are not proof of humanity; give them a cause.**
5. **A clear silhouette beats a complicated surface.**
6. **Function, context, and meaning should agree.**
7. **Wear follows use, material, exposure, and maintenance.**
8. **Text is either correct or deliberately unreadable as a shape.**
9. **Every prominent object needs a reason to be there.**
10. **Human care is visible in placement, restraint, revision, and curation.**
11. **A clear point of view beats AAA imitation.**
12. **The player camera is the final judge.**
13. **Tools should make human decisions easier to express and revise.**
14. **Generated output is a draft until it has been interpreted and edited.**
15. **Quiet space is part of composition.**
16. **A sign belongs to a surface, a reader, and a moment of decision.**

---

## 18. Reference library: ground the work in human-made places

The reference library should help the team observe how people build, place, print, repair, use, and adapt things. Use real photographs, physical objects, archival material, and documented artist workflows as primary evidence. Do not use AI-generated art galleries or prompt collections as the main visual reference for how the finished game should look; they can reproduce the same generic patterns this guide is intended to prevent.

### 18.1 Build evidence-based reference boards

For each asset family or environment, collect references that answer different questions:

- **Whole-space views:** How are routes, rooms, storefronts, lots, and neighboring buildings arranged?
- **Use views:** Where do people stand, queue, work, wait, store things, and leave objects?
- **Construction views:** How are signs, awnings, railings, fixtures, windows, doors, and repairs attached?
- **Material views:** How do paint, plastic, glass, metal, paper, concrete, and wood age under local conditions?
- **Typography views:** How do real signs organize names, prices, hours, warnings, and secondary information?
- **Exception views:** What has been patched, improvised, moved, neglected, or replaced—and what caused it?

Prefer several views of the same type of place over one perfectly composed image. Record the source, approximate date, location, building or object type, and what visible evidence matters. Annotate the evidence instead of copying the overall photo treatment: “menu taped inside service window,” “lettering follows canopy width,” or “trash accumulates at fence corner.”

Use this chain when turning a reference into art direction: **observation → interpretation → authored choice → visible result → review.** A procedural rule can help carry that choice into many assets, but it is only one possible production step. If an image cannot support a clear observation, it may be mood inspiration, but it should not define a placement or material rule.

For the 1990s Delco setting, prioritize local and period-specific photos, newspaper ads, phone books, business directories, menus, product packaging, and personal snapshots. Broad national archives are useful for comparison, but they cannot stand in for the exact region, decade, or socioeconomic context being depicted.

### 18.2 Recommended references by use

**World layout, placement, and storytelling**

- GDC, [“What Happened Here? Environmental Storytelling”](https://www.gdcvault.com/play/1012647/What-Happened-Here-Environmental): using props, texturing, lighting, and composition to let players interpret a place.
- GDC, [“Interior Design and Environment Art: Mastering Space, Mastering Place”](https://www.gdcvault.com/play/1022089/Interior-Design-and-Environment-Art): applying interior-design thinking to environment art and the organization of rooms.
- GDC, [“Environment Design as Spatial Cinematography”](https://www.gdcvault.com/play/1025736/Environment-Design-as-Spatial-Cinematography): composing a space for a moving player camera and directing attention through environment design.
- [The Level Design Book: Environment Art](https://book.leveldesignbook.com/process/env-art): a practical overview of environment art, readability, massing, and composition in relation to gameplay.

**Signs, typography, and reading distance**

- SEGD, [“Wayfinding Is Where Place Meets Information Design”](https://segd.org/resources/wayfinding-where-place-meets-information-design/): connecting information hierarchy to the decisions people make in a physical space.
- U.S. Access Board, [Chapter 7: Signs](https://www.access-board.gov/ada/guides/chapter-7-signs/): real-world guidance on viewing distance, character size, spacing, contrast, and placement. Use it to understand legibility factors; do not treat code requirements as a universal art style.

**Primary-source American environments**

- National Archives, [Pictures of American Cities](https://www.archives.gov/research/american-cities): photographs documenting streets, transportation, city life, and urban change. Search the catalog by place and date, then verify the original record and context.
- Library of Congress, [Detroit Publishing Company photograph collection](https://www.loc.gov/pictures/collection/det/): a large historic collection useful for studying street organization, storefronts, architecture, and everyday objects. Its images are mostly earlier than the game’s 1990s setting, so use it for long-lived construction patterns, not as direct period evidence.
- National Archives, [1994 Georgetown building comparison](https://text-message.blogs.archives.gov/2012/02/10/a-georgetown-building-in-1994-and-2012/): a specific example of how signage, storefronts, street furniture, and building details changed over time.

**Blender and Godot implementation**

- Blender Manual, [Scatter on Surface](https://docs.blender.org/manual/en/5.0/modeling/geometry_nodes/generate/scatter_on_surface.html): surface distribution, masks, alignment, and instance selection.
- Blender Manual, [Distribute Points on Faces](https://docs.blender.org/manual/en/5.0/modeling/geometry_nodes/point/distribute_points_on_faces.html): point density, normals, rotation, and surface placement behavior.
- Godot 4.7, [Label3D](https://docs.godotengine.org/en/4.7/classes/class_label3d.html): properties and behavior for text placed in 3D space.
- Godot 4.7, [Decal](https://docs.godotengine.org/en/4.7/classes/class_decal.html): decal projection and engine-specific constraints for placed surface markings.

### 18.3 What to put beside each reference

For each board, include at least one annotated example of:

- An asset or sign placed well, with its anchor, surface, viewing direction, and reason for being there.
- A believable cluster, showing the activity that produced it and the clear space around it.
- A readable sign at game distance, with its hierarchy, margins, line spacing, and mounting visible.
- A repair or imperfection with a visible cause.
- A “do not copy” example showing the specific failure: uniform scatter, fake text, impossible attachment, repeated grime, or detail that competes with gameplay.

The purpose of the board is to teach the team what to notice and why. A folder of attractive pictures without observations is not yet an art-direction reference.

### 18.4 References on human authorship and AI-assisted work

These references are useful for discussing process, agency, and authorship. They do not provide a reliable visual test for whether a finished asset was made by a person or a model. Use them to shape the team’s process and standards, not to claim that a particular image “looks human” by rule.

- Stanford HAI, [“Humans in the Loop: The Design of Interactive AI Systems”](https://hai.stanford.edu/news/humans-loop-design-interactive-ai-systems): a useful design principle for tools—preserve human agency, provide granular control, and make the system something people can work with and shape. Apply this to art tools and procedural workflows.
- MIT CSAIL, [“Teaching AI models the broad strokes to sketch more like humans do”](https://news.mit.edu/2025/teaching-ai-models-to-sketch-more-like-humans-0602): useful for thinking about visual development as an iterative, stroke-by-stroke process and AI as a collaborator in sketching. Use the process insight; do not treat AI-generated sketches as finished style references.
- MaviGadget, [“Infuse Soul: How to Make AI Images Truly Human & Realistic”](https://mavigadget.com/blogs/tech-gadgets/infuse-soul-how-to-make-ai-images-truly-human-realistic): it usefully calls attention to specificity, context, and narrative. Its advice to add flaws, grain, and post-processing is not a substitute for authorship; applied mechanically, those steps can become another generic recipe.
- PSDDude, [“AI Art vs Human Art”](https://www.psd-dude.com/tutorials/resources/ai-art-vs-human-art.aspx): an informal side-by-side creative-process comparison that raises useful questions about who makes the idea, composition, and revisions. Treat its scoring and broad claims as opinion, not a validated test.
- Walter Writes, [“AI Art vs Human Art”](https://walterwrites.ai/ai-art-vs-human-art/): useful as a prompt to separate output appearance, creative authorship, and cultural or ethical questions. It is a commercial explainer, not an art-direction standard; do not use detector or legal claims as a visual-quality rubric.
- The Glaze Project, [“What Is Glaze?”](https://glaze.cs.uchicago.edu/whatis.html): a source about protecting artists from style mimicry, not identifying AI images or defining human-looking art. Use it to support a boundary against copying a living artist’s recognizable style as a shortcut.
- Blender Artists, [“Clarification on AI generated work” discussion](https://blenderartists.org/t/clarification-on-ai-generated-work/1598841/13): a community discussion that can help teams discuss disclosure and what they mean by AI-assisted work. Treat it as discussion, not technical evidence or an aesthetic rule.

---

## References

These official references are useful for engine implementation details; they do not replace project-specific art direction.

- Godot 4.7, [3D rendering limitations](https://docs.godotengine.org/en/4.7/tutorials/3d/3d_rendering_limitations.html).
- Godot 4.7, [StandardMaterial3D and ORMMaterial3D](https://docs.godotengine.org/en/4.7/tutorials/3d/standard_material_3d.html).
- Godot 4.7, [Optimizing 3D performance](https://docs.godotengine.org/en/4.7/tutorials/performance/optimizing_3d_performance.html).
- Godot 4.7, [GPU optimization](https://docs.godotengine.org/en/4.7/tutorials/performance/gpu_optimization.html).
- Godot 4.7, [Spatial shaders](https://docs.godotengine.org/en/4.7/tutorials/shaders/shader_reference/spatial_shader.html).
- Blender Manual, [Randomize Transforms](https://docs.blender.org/manual/en/5.0/modeling/geometry_nodes/instances/randomize_transforms.html).
- Blender Manual, [UV Editing](https://docs.blender.org/manual/en/5.0/editors/uv/index.html).
