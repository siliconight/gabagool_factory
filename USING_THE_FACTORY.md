# Using the factory — getting content out without putting defects in

The other root documents each answer one question. `PIPELINE_MAP.md`: what
this machine is (repos, DAG, artifacts, contracts). `PIPELINE_ROADMAP.md`:
where the work is right now. `CLAUDE.md`: the law for changing tool code.
This file answers the operator's question: **how to navigate this toolset to
get the content you want — and what is supposed to happen when the toolset
cannot make it.** It is written for both kinds of operator, human and agent,
because the factory does not distinguish: the rules that keep an overnight
agent session from corrupting a repo are the same ones that keep a Saturday
design session from doing it.

## Wear one hat at a time

Every task here is done under one of two hats:

- **Making content WITH the tools.** A mission spec, a theme choice, a
  pipeline run, a walk. The tools are fixed; the spec is the material.
- **Growing the tools.** Changing what the toolset can make. This hat is
  governed by `CLAUDE.md` — grounding, versioning, changelogs, tests,
  gates — with no small-change exemption, because small changes are where
  the nine wrong calls of 2026-08-10 came from.

The hats swap constantly in a real session; the discipline is saying which
hat the current edit is under. Confusing them has a named failure mode in
this repo: hand-editing a workspace until the level works while the
pipeline still does not (`CLAUDE.md`, "Where fixes land").

## Content flows one way; findings flow the other

Spec → tools → workspace. A generated file is EVIDENCE about the tool that
made it, never material to fix in place. When output looks wrong, the fix
lands in the owning repo, versioned and changelogged, and the pipeline
re-runs. The routing table, for deciding where a change belongs:

| you want to change...                                        | owner           |
|--------------------------------------------------------------|-----------------|
| floor plans, rooms, storeys, stairs, openings, which rooms get which light anchors | `deli_counter` |
| structural kit modules, dressing props, light-fixture hardware (species) | `zoo` |
| themed surface looks (skin packs)                            | `pixelcoat`     |
| cross-shell cohesion passes, the dressing manifest           | `patina`        |
| site assembly: building placement, routes, cover, spawns     | `lot`           |
| light behavior: rig tuning, ranges, color, flicker, presets  | `lux`           |
| engagement grading (advisory by contract, never blocking)    | `lasertag`      |
| the job graph, staging, validation, caps, exports            | `level_factory` |
| the shipped mission package                                  | `dispatch`      |

`PIPELINE_MAP.md` ("The repos") is the authority when this table and
reality disagree.

## The setting: 1990s Pennsylvania, weighted to Philadelphia and Delco

Every content decision downstream of the geometry — which materials a facade
carries, what a roofline does, whether a building steps or holds a flush
street wall, what a room is full of — answers to a setting, and until
2026-09-07 the setting lived in nobody's file. It is: **1990s Pennsylvania
building types, with the emphasis on Philadelphia urban and Delaware County
("Delco").**

That is the operator's call and it is recorded here rather than argued. What
this section adds is the part the repo can be asked: how much of that setting
the toolset can currently build, measured rather than assumed.

**IT IS A REFERENCE, NOT A SIMULATION, and that distinction governs how every
number below should be read.** This is art. Embellishing and stylizing is
wanted, not tolerated — where it makes sense, it is the point. The setting
says what the work is ROOTED in: the shapes, materials, signage, wear and
street logic of that time and place are the vocabulary being drawn from, and
the job is a version of them that reads as deliberate at gameplay distance.
Nothing here asks for accuracy to a surveyed building, and a finding phrased
as "real ones were not like this" is not automatically a defect. The measured
gaps below are worth knowing because they show where the toolset would fight
a stylized reading, not because reality is the target.

**THE ARCHETYPES ARE ALREADY THE SETTING.** `corner_deli`, `pawn_shop`,
`auto_shop`, `gas_station`, `rowhouse_raid`, `strip_retail`, `foundry`,
`freight_terminal`, `self_storage`, `funeral_home`, `brewery`,
`parking_garage`, `train_yard`. The list also carries `casino`,
`airport_terminal`, `courthouse`, `stadium`, `mansion`, `museum` and
`bank_tower` — and those are IN setting too, as their 1990s Pennsylvania
versions. A regional terminal or a Delco casino in 1997 is a building type,
not a genre slip. Do not prune the list on a reading of its names.

**THE LIBRARY IS LOW-RISE, which is correct and worth knowing before
proposing massing.** 131 library specs: 59 of one storey, 67 of two, 5 of
three. Nothing is taller. So a setback (roadmap 116) reads here as a ROOF
TERRACE — a second approach route, a position above the street, cover on the
roof — and not as a skyline step. Any massing proposal that assumes a tower is
proposing a different game.

**THE PHILADELPHIA HALF OF THE SETTING IS 96% AUTHORED AND UNBUILDABLE, and
this is the sharpest gap the setting exposes.** Zoo carries species styles
for `center_city` at 54 of 56 species and `industrial_flats` at 54 of 56 —
the two families that most obviously read as Philadelphia — and Pixelcoat has
no theme profile for either, so neither can be built. Meanwhile Pixelcoat
ships `bank`, `casino`, `stadium`, `street` and three `rockay_*` variants that
are keys in no Zoo species at all.

```
Pixelcoat profiles   bank casino delco rockay rockay_civic rockay_retail
                     rockay_service stadium street
Zoo species styles   default 56/56   rockay 56/56   center_city 54/56
                     industrial_flats 54/56   delco 39/56   1990s 14/56
                     1980s 5/56   1970s 5/56   bodega 1/56
```

The Delco half is buildable: `delco` exists on both sides. The Philadelphia
half is two profiles away. That is roadmap item 112 restated with a reason —
it was filed as "nine themes, two work", and the setting says WHICH two are
worth closing first.

**BRICK IS 20 OF 131.** Across the library, `concrete` appears 194 times,
`metal` 133, `drywall` 122, `glass` 117, `wood` 115 — and `brick_ext` 20,
`stone_ext` 4. Worth surfacing because brick is a load-bearing part of this
setting's read and the palette barely reaches for it — not because a census of
real rowhomes says so. The tools can carry it; the specs mostly do not ask.
Whether the answer is more brick, a stylized brick, or a deliberately
concrete-heavy take is the operator's call.

**FIRE ESCAPES ARE 2 OF 131.** Deli Counter has built them since 0.4x and two
specs use them. They are a facade signature AND a route — the rare element
that pays in silhouette and in gameplay at once, which is the kind of thing
worth stylizing hard rather than reproducing faithfully.

**WHAT THIS SECTION DOES NOT DECIDE.** Which archetypes should step and which
should hold a flush street wall; what a cornice or a parapet profile should
look like; how a storefront differs from a rowhome facade; which of the
period styles (`1990s`, `1980s`, `1970s`) is the target and which are decade
texture. Those are design calls, they belong to the operator, and the
`## The gap protocol` section below is how they reach the tools once made —
the owning tool grows the capability, and nothing is hand-authored downstream.

## The gap protocol: when the catalog cannot make what the design asks

Sooner or later a design asks for something no tool currently makes. That
moment is not a workaround moment and it is not a failure — it is a
capability request, and it has exactly one correct shape:

1. **Name the gap precisely**, in the owning tool's own vocabulary: an
   anchor type, a skin, a species, a tuning row, an assembly rule.
2. **Find the owner** in the table above.
3. **Grow the capability inside the owner's own grammar** — a new
   Pixelcoat skin pack, a new Zoo species, a new Deli Counter room rule, a
   new Lux tuning entry — versioned, changelogged, and tested like any
   other change to that repo.
4. **Re-run the pipeline.** The request is satisfied by the next build and
   by every build after it, for free.

What the protocol forbids is the shortcut: hand-placing the missing thing
into one workspace. That satisfies one level and leaves the factory unable
to make the next one — one intervention that will be paid again on every
future level that wants the same thing.

Worked example, 2026-08-24 — three small capability additions, zero
hand-placed objects. The design ask was "90s Philadelphia: bare bulbs
below grade." Deli Counter grew the `pendant` anchor derivation (0.98.0:
basements and objective rooms trade the office fluorescent row for sparse
bulbs), Zoo grew the `pendant_fixture` species (0.50.0: the hardware the
marker path ships), and Lux grew the pendant tuning row (0.20.0:
incandescent color, cord drop, filament waver). Every basement in every
future build now gets bulbs, and no workspace was touched. The Pixelcoat
version of the same move: a design needs a look no skin provides →
Pixelcoat mints the skin pack and the kit resolves against it — the design
is not watered down, and no texture is hand-painted into output.

### Minting, step by step: from "the brief wants a planter" to the planter

The protocol above says the owner grows the capability. As of 2026-09-12
each owner has a tool that does the growing to a first, honest state, and
the three share one shape: **report** the queue, **mint** from a template,
**prove** it validates, **register** it, and **say** what the next repo
needs. A new person walks this in an afternoon; what remains afterwards is
the drawing, which is what a person is for.

0. **Look at the real thing first.** Before any of the steps below, search
   the species name and look at ten photographs. A teller line is a
   counter, a glass barrier over it, one service window per station with a
   pass-through at counter height, posts between windows -- and none of
   that is in a box. The recipe's docstring should be able to cite what it
   is a drawing of. (Roadmap 44's teller counters shipped as plain counters
   for a day because nobody had looked.)

1. **Is it asked for?** `python zoo/tools/new_species.py report` lists the
   placement names Deli Counter's specs carry with no species behind them,
   most common first, split into: mint this (no species exists), route this
   (a species exists, the name is not keyed to it), widen this (hinted,
   exists, did not fit -- a range or a bay, not a mint).

2. **Mint the prop.** `python zoo/tools/new_species.py new planter
   --width 1.4 --depth 0.7 --height 0.9 --material concrete --keywords
   planter,planter_box`. Writes the genome (dims as defaults, a 0.5x..2.0x
   range), a placeholder recipe (a solid box at the slot's exact size, one
   named part, collision, an attachment, a docstring saying where the
   drawing goes), a test, and a line in `genome/minted.json`. Prints the
   one line `deli_counter/prop_species.py` needs, and whether the theme
   has a Pixelcoat pack for the material.

3. **Route the name.** Add the printed keyword line to `PROP_SPECIES` in
   `deli_counter/prop_species.py`, before any broader keyword, and
   rebuild the library (`python build.py --all --blender ...`); the
   volume's slot now carries `species: planter` and Zoo builds it as one
   wherever the dims fit its range.

4. **Mint the texture, if the material is new to the theme.**
   `python pixelcoat/tools/new_material.py report --theme delco_1997`
   names the kinds the theme cannot dress; `new terracotta_delco --kind
   plaster --like plaster_delco --colors "#b5613f,#c26e4a,#a3532f" --theme
   delco_1997` writes the grammar from a template, synthesizes it and
   prints the two numbers a skin is judged by (albedo spread and neighbour
   correlation -- under 0.3 it is static, roadmap 140), and maps the kind
   into the theme so `theme-library` builds it. A kind Zoo does not know
   needs its three tables first; the tool names them.

5. **Mint the style, if the theme is new.** `python
   zoo/tools/new_species.py style delco_2005` reports which species would
   wear the uncoloured default under that name; `--write` copies each one's
   nearest ancestor row under the new name, with `--material / --wear /
   --ambient / --color` overrides.

6. **Run it cold.** A brief through `cold_run.py --begin`, the pipeline,
   `--end`: the species appears in the kit index as itself
   (`species_fallbacks` and `species_alternates` say what did not), the
   package carries it, and `tools/walk_export.py` gives you the copy to
   walk. Then draw the recipe -- `desk.py`, `counter.py` and
   `shelving.py` are the pattern -- and the next cold run ships the
   drawing.

What each mint leaves honest: a minted prop is a box wearing its name; a
minted material is the template's surface in new colours; a minted style
is an ancestor's look under a new name. Each is counted as itself in every
report from then on, which is what turns a silence into a request.

## Tools say no out loud

The gap protocol only fires if gaps are VISIBLE. So the convention:

**A tool that cannot satisfy a request says so at build time, naming (1)
what was asked, (2) the nearest capability it does have, and (3) which
repo owns growing the real one.** A skip with a reason is an answer; a
silent skip is a defect. A gap that first surfaces as a dark room in a
walk costs a human playtest to find, and this repo has paid that exact
bill twice in one week: Zoo's fixture pass dropped the new `pendant`
anchors without a word (no `FIXTURES` row → no marker → no light — fixed
in 0.50.0 by adding the species; the silence itself is the open half), and
the marker payload read null from the day the spawner was written until a
probe read the running tree (Lux 0.22.0), a name-parse fallback silently
carrying the whole contract in between.

Where the toolset already does this well, keep it that way:
`LuxFixtureSpawner.spawn` returns every skipped marker with its reason,
and `build_freshness.py` refuses to grade a stale shell library rather
than quietly grading it. Making the signal UNIFORM and machine-readable —
a `CAPABILITY_GAP` line in stdout and report artifacts, counted in Level
Factory run summaries — is roadmap item 62. Until it lands, assume silence
can hide a gap, and count what actually shipped.

## The rails, restated short

The safety rules a content session actually touches; the full law lives in
`CLAUDE.md` and `PIPELINE_MAP.md`:

- **Never hand-edit `factory.manifest.json`** or any generated artifact.
  Candidate → gates → promote; pins are re-earned, not typed.
- **Gates are the contract, not an obstacle.** `--no-verify` is only for a
  failure already attributed to something pre-existing and written down —
  attribute every item in a gate's output before overriding it.
- **Every tool change bumps that repo's version and changelog**, or the
  manifest lockstep check will call the set drifted — because it is.
- **Walk what you ship.** Instruments prove "works"; only eyes currently
  prove "good" (roadmap item 18). A pass with no walk is half a pass.
- **When an instrument and your eyes disagree, one of them is wrong.**
  Establish which before building anything on either.
- **One writer per repo at a time.** Sessions running in parallel split the
  factory by REPO, and a repo changes hands only at a commit. Learned
  2026-08-24: a second session shipped a correct, well-reasoned Deli
  Counter release into the working tree and closed without committing --
  the changes were live in the next build while `git log` still said the
  old version, and the census deltas they caused were mis-attributed for
  half a day before `git status` named the mystery colleague. An
  uncommitted change with no session attached to it reads as nobody's
  work, however good it is.
