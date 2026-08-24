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
