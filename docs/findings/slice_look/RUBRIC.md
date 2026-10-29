# The slice's self-review rubric

The walker, 2026-10-29: "can you self identify the gaps, and responsibly chip away at them when im gone as well?
(self judge on your end?)". The target is theirs, 2026-10-28/29: the fidelity of an Xbox 360-era shooter (Halo 3,
Gears of War) on anybody's machine, "less about realistic textures and more about the 3d shape themselves", made by
our tools, borrowing nothing from those games. This file is how a gap is named and how a fix is judged while nobody
is watching, so the walker can check the judgement afterwards instead of trusting it.

## The walker's bar, 2026-10-29 (governs everything below)

"Things still look simple, and computer made... I want to get to a place where these levels looks handcrafted,
bespoke, varied, realisitic where possible, artistic where possible, and ultiamtely start to look like osmething that
would stand out in a crowd of games. The Seventh generation target is to mainly call out the detail and placement of
hard surfaces/assets, shadows, contrast of colors used, and detail of set dressing."

So the four axes the slice is judged on, before anything else:

- **Hard surfaces and their placement**: detailed, layered, bevelled assets, placed as a person would have placed
  them -- off the grid where life would put them off it, grouped, leaning, worn -- not aligned in rows by a rule.
- **Shadows**: objects grounded by contact shadow and occlusion; strong lit/shadow structure on facades and streets.
- **Colour contrast**: a palette with deliberate contrast between surfaces, accents and light, not uniform mid-grey.
- **Set dressing detail**: the small things that say who lives and works here, at the density a lived place has.

And the test above them: **does it look made by a person, and varied, or generated?** A frame where the same
treatment repeats, where everything is aligned to the same rule, or where nothing departs from the default is a gap
even if nothing in it is broken.

## What a gap is

A gap is something visible in the slice's frames that a player of a 2007-era console shooter would read as unfinished
or generated. Each one is written down with: the frame and station it is seen in, what is wrong in plain words, the
tool that owns it (grounded in source, not guessed), and a rank.

The questions, in the order they are asked of every frame:

1. **Silhouette.** Does every object read as a made thing at 10 m and 30 m -- edges bevelled, parts proud of each
   other, no slab that is one box where the real thing has parts (sills, copings, frames, trims, lips, kerbs)?
2. **Junctions.** Where two things meet -- wall and ground, wall and roof, prop and floor, building and building --
   is there a part that makes the meeting (a base course, a coping, a kerb, a skirt), or a raw seam, a gap, a float,
   a z-fight?
3. **Surface response.** Does each material read as what it is under the level's light: matte stays matte, metal and
   glass catch light, nothing flat-shaded and nothing uniformly grey? (Within GL Compatibility: no screen-space
   effects, no depth reads.)
4. **Light.** Do the light sources read as sources, is there contrast between lit and shadowed, is anything black that
   should be lit or lit that should be dark?
5. **Density and life.** Is the ground and the street dressed the way a lived place is -- at a density the walker has
   set (rooms 12-25 % floor, open ground only on purpose) -- or bare?
6. **Repetition.** Does the same module, texture or prop repeat visibly side by side?

## How a gap is ranked

Rank = how much of the frame it affects x how many frames it appears in x how cheap the fix is, judged in that order.
A defect (a float, a z-fight, a hole, a stray) outranks a missing detail of the same size, because it reads as broken
rather than plain.

## What a fix must show before it ships

- **It lands in a tool repo** through `tools/ship_change.py`, with a test that fails without it; never an edit to the
  slice's workspace.
- **Before / after frames of the slice** at the same stations, in the level's light and under the studio light, kept
  in a findings folder with what was measured.
- **A price** (`tools/price_batch.py`, A / subject / A). PASS ships. WATCH ships only when the look is clearly better
  and the draws are explained; FAIL does not ship.
- **No regression elsewhere**: the owning repo's whole suite on the clone (for Zoo, `ship_change.py bpy` too).
- **An honest verdict in the record**: "reads better", "barely visible", or "worse", with the frame that shows it. A
  change that does not move the frame is said to be so, and the next gap is taken instead of polishing it.

## What is not decided alone

Left for the walker, written down and not shipped:

- Anything that changes a look the walker has already said they like ("walker taste overrides art budget"; the
  references fill blanks and never override).
- Colour, palette and mood choices, names and brands, the time of day and weather of the slice.
- A new dependency, download or licence; anything published or released.
- A change whose price is WATCH or FAIL with no clear win.

## The log

`docs/findings/slice_look/README.md` holds the gaps as they are found, ranked, and each fix's outcome against this
rubric, newest first.
