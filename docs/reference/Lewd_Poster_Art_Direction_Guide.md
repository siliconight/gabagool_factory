# Lewd Poster Art Direction for a Video Game

## Crass, suggestive posters for dive bars, strip clubs, and alleys

This guide gives artists and technical artists a practical direction for fictional adult nightlife posters in a stylized 3D game. It covers tone, poster copy, visual treatment, procedural variation, and review. The target is loud, tacky, suggestive humor with overconfident action-game bravado: cheap glamour, double meanings, and boasts that collapse into a punchline.

Keep the posters fictional, readable in-world, and suggestive rather than graphic. The intended tone is environmental storytelling: a glance should tell the player what kind of venue this is and what kind of people run it.

### A useful joke structure

Build copy from a simple setup and turn:

1. **Make a ridiculous promise:** beauty, danger, romance, fame, or a night no one will remember.
2. **Add an adult double meaning:** use a word that can read as ordinary nightlife copy and as innuendo.
3. **Deflate the boast:** undercut it with a cheap practical detail, neighborhood complaint, or self-own.

The joke can sit in the headline, a fake disclaimer, a tiny venue rule, or the mismatch between polished imagery and a grimy location. Keep the hierarchy clear: headline first, image second, funny fine print as a reward up close.

### Different locations need different levels of polish

| Location | Poster character | Good sources of humor | Material treatment |
|---|---|---|---|
| Dive bar | Loud, cheap, local, slightly desperate | Bad bands, questionable drink specials, regulars, broken jukeboxes, overconfident bartenders | Photocopy grain, marker edits, beer rings, curled corners |
| Strip club | Brash glamour with a wink | Fake luxury, ridiculous VIP promises, tacky stage names, absurd house rules, inflated claims | Saturated spot colors, faux gold, airbrushed gradients, glossy accents over worn paper |
| Alley / telephone pole | Unofficial, layered, half-obscured | Handbills, handwritten corrections, parody ads, local rumors, passive-aggressive notices | Torn edges, paste stains, overlapping sheets, rain fade, staples and tape |

Use a different visual voice for each place. A strip-club handbill can be flashy and carefully composed; the bar flyer can look hastily copied; the alley's layered posters can make the jokes feel discovered rather than presented. Not every poster needs a sexual gag. Mix adult humor with local band bills, fake civic notices, odd jobs, lost-pet flyers, and ordinary neighborhood clutter so the whole world does not feel one-note.

### Sample fictional copy

Use these as tone and structure examples, not fixed required text:

- **THE VELVET VOLTAGE** — *Open late. Standards closed.*
- **TONIGHT AT THE MUDDY BOOT** — *Live music, cold beer, one working microphone.*
- **LADIES' NIGHT** — *Two drinks, one bad decision, no refunds.*
- **THE GOLDEN GARTER** — *World-class glamour. Parking-lot-class parking.*
- **DANCE LIKE NOBODY'S WATCHING** — *Someone is. It's Gary from security.*
- **THE BIG SHOW** — *Small stage. Enormous confidence.*
- **NOW HIRING: DOOR STAFF** — *Must be calm, polite, and able to lift a jukebox.*
- **NO COVER BEFORE NINE** — *After nine, we charge for the privilege of hearing the same song again.*
- **TONIGHT ONLY** — *Tomorrow, we'll deny everything.*
- **PLEASE DO NOT FEED THE REGULARS** — *They know when you have fries.*

Keep text fictional, brief, and specific to the venue. A single strong line usually plays better than a paragraph of jokes. If the gag depends on reading tiny copy, it belongs on an inspectable hero poster; background posters should land through the headline and image alone.

### Art direction and procedural controls

Add an optional `Lewd / Sleaze` family tag to the generator, then expose controlled parameters rather than a generic “adult” filter:

- **Suggestiveness:** none, cheeky, pin-up, or risqué silhouette.
- **Bravado:** earnest, boastful, knowingly ridiculous, or self-deprecating.
- **Copy gag:** innuendo, fake disclaimer, bad promise, house rule, or local insult.
- **Glamour level:** handbill, bargain-bin glam, faux luxury, or deliberately shabby.
- **Illustration style:** silhouette, pulp airbrush, crude cartoon, photocopied photo treatment, or hand-painted sign.
- **Wear:** clean promo, thumbtacked, beer-stained, rain-damaged, or layered paste-up.

Keep the joke category and level artist-selected. Let the seed choose among approved palettes, layouts, wear masks, and small decorative marks; do not let it generate unchecked sexual copy or select arbitrary imagery. Store the final wording in the poster's content record so it can be reviewed and translated consistently.

### Keep the joke from turning into noise

- Make the poster's main gag understandable at a glance.
- Use one innuendo or absurd boast as the center; avoid stacking several unrelated jokes.
- Use period-feeling type, illustration, and printing, but do not reproduce a specific game's logo, character, catchphrase, or exact composition.
- Make adult venues unmistakably adult through context and signage. Depict only clearly adult performers and patrons; keep sexualized imagery out of youth-coded settings.
- Prefer confident, ridiculous fictional businesses and institutions as the target of the joke. Avoid making a real-world protected group the punchline.
- Keep poses and silhouettes suggestive rather than explicit. This reads cleanly on a wall prop, works at distance, and leaves room for the player's imagination.
- Match the level of grime to the prop's location and history instead of applying the same dirt pass to every image.
- Check the game's intended rating and platform content rules during review; the safe art direction is the one that matches the shipped game's audience and presentation.

### Quick review pass

At thumbnail size, ask: does it read as a venue or event poster, does the joke land, and is the main image still the focal point? In the level, check that suggestive details do not become explicit or misleading when mipmapped, distorted at an angle, or partially covered by another poster. Make sure a joke still works when only its headline is visible.

---

