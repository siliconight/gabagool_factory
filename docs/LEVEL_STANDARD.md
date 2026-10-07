# The Level Standard -- what a real level is, and how this factory makes one

The walker, 2026-10-07:

> My goal is to start to codify a schema or repeatable level of excellence, so
> we can start making real levels and not just technical demos. ... have it be
> something that knows how to guide future requests of levels. It will be
> something we iterate on, as we learn.

**This is v1.3** (2026-10-07). v1.3 adds what the package says about the
score (§4, roadmap 204) and the brief's pacing reaching Lot, seen in cold
run 9195 (Part 0, §5, Appendix A; roadmap 200;
`patches/patch_level_standard_v1_3.py`). v1.2 recorded cold run 9194, the
first level whose score is the building its brief asked for (§4, §5,
Part II's first item and Appendix A; `patches/patch_level_standard_v1_2.py`).
v1.1
re-checked v1's tool claims against the code by a full capability sweep
and corrected 26 (`patches/patch_level_standard_v1_1.py` lists each, and
the code it was checked against). Its spine is the walker's own draft, *Level Factory --
Repeatable Heist Level Generation Schema & Gold-Standard Proposal Example*,
kept unedited at `docs/reference/LEVEL_FACTORY_STANDARD_v0.docx`.

Every section of that draft is here. What v1 adds:
- **Where each requirement lives in this factory.** Each one names the tool
  that makes it, the knob or field that asks for it, and the check that
  catches it, with a status tag (below) saying how far that has got.
- **What this game is, where it differs from a generic heist.** The
  walker's standing calls are folded in: five times of day, dens of sin,
  shooting galleries, draw calls as the budget, and the authorship guide's
  "why is this here?"
- **How a level is requested, built, judged and fixed here** (Part 0). That
  is the part that guides the next request.
- **What a real level must pass:** zero interventions, then the scorecard.
- **The documents it absorbs.** `LEVEL_RECIPE.md`'s MVP becomes the
  measurable core. `AUTHORSHIP_GUIDE_APPLIED.md`'s per-run review rubric
  becomes the scorecard record.

What v1 does NOT do is pretend. Where nothing in the factory makes a thing the
draft asks for, the line says GAP and names the owner who would grow it
(`USING_THE_FACTORY.md`, "The gap protocol").

**Companions, read for their own domains and not restated here:**

| document | owns |
|---|---|
| `USING_THE_FACTORY.md` | which repo owns which change; the gap protocol; minting a prop |
| `docs/reference/DYNAMIC_WALKABLE_CITY_LEVEL_DESIGN_BRIEF.md` | hub, spokes, loops, edges, adjacency: the district |
| `docs/reference/LAND_PRESSURE_AND_SPATIAL_LOGIC.md` | parcels, land pressure, open-space roles, coverage metrics |
| `docs/reference/HUMAN_AUTHORSHIP_GUIDE.md` and `docs/AUTHORSHIP_GUIDE_APPLIED.md` | what "authored" means, prop by prop |
| `docs/DELCO_1997_ART_DIRECTION.md` | the setting's look, with an owner column |
| `docs/LAYOUT_RULES.md` | egress, the secure chain, combat-space rules inside buildings |
| `docs/STREET_RULES.md` | stop signs, crosswalks, street furniture rules |
| `docs/PERFORMANCE_CONTRACT.md` and `docs/DRAW_CALL_BUDGET.md` | frame budgets and how to measure them |
| `docs/COLD_RUN.md` | the run that measures interventions-per-level |

---

# Part 0 -- How a level is requested, made and judged here

## 0.1 Two gates, and which one makes a level real

**WORKS** is the gate every tool already measures: can a body get from A to B,
do the stairs connect, does the package load, does the frame fit the budget. A
level that fails it is broken whatever it looks like.

**GOOD** is the gate this standard is for. Does it read as a place someone
built, and does it play as a heist with choices in it? `PIPELINE_ROADMAP.md`
item 18 records that it does not exist as a gate. Of eight problems found by
walking a generated level, four were invisible to every check in the pipeline.

> **A technical demo passes WORKS. A real level passes both, at zero
> interventions.**

**Zero interventions** is `CLAUDE.md`'s metric. Between the brief and the
walk, nobody changed a tool, a spec, the brief or a theme, dropped a file into
the workspace, or re-ran with different arguments (`docs/GLOSSARY.md`,
"Intervention"; `tools/cold_run.py` counts them). A level that needed six
hand-patches is six defects, not a level.

## 0.2 The status tags

Every requirement below carries one tag, the state of the factory on the
date in its line. They are what a request can be promised.

| tag | meaning |
|---|---|
| **GATE** | A check fails the build or the cold run when this is wrong. |
| **MEASURED** | An instrument reports it; nothing fails on it yet. |
| **BUILT** | A tool makes it; nothing checks it. |
| **EYE** | Judged by the walker from frames or a walk; no instrument can. |
| **GAP** | Nothing makes it yet. The line names the owner who would grow it. |

Moving a line from GAP to BUILT, or from BUILT to MEASURED, is progress on the
GOOD gate. **Moving it to GATE is a decision**, and `LEVEL_RECIPE.md` sets the
rule for it: measure the corpus first, set the bound second. A threshold
chosen before the distribution is known either passes everything or fails
everything.

## 0.3 The request loop

1. **Write the request** (Appendix A). One sentence of fantasy, the place,
   the score, the time-of-day slot, crew and session, tone and playstyle, and
   the must-haves.
2. **Translate it into a mission brief.** Appendix A's table says which
   request fields the factory reads today
   (`level_factory.mission_brief.v0.1`). A field with no brief field yet goes
   into `notes` and is reported as a GAP against this run. It is never
   silently dropped.
3. **Run it cold** (`docs/COLD_RUN.md`):
   - stage it with `tools/cold_drive/stage_batch.py`;
   - drive it with `tools/cold_drive/cold_drive.sh`;
   - close it with `tools/cold_run.py --end`.
   Level Factory builds three candidates and picks one on the walk test and
   Laser Tag's route findings. `INTERVENTIONS` is the first number read.
4. **Review it** (Part I §15, Appendix C):
   - the gates and findings first;
   - then the instruments: frames, the censuses, Laser Tag, the price;
   - then the walker's walk;
   - and the scorecard, recorded beside the run in
     `docs/cold_runs/cold_N/SCORECARD.md`.
5. **Fix forward.** Every problem the review finds lands in the tool that
   owns it, versioned and tested (`docs/SHIPPING_A_CHANGE.md`), and the brief
   runs again. Nothing is hand-placed into the level (`USING_THE_FACTORY.md`,
   the gap protocol).
6. **Grow this standard.** When a review finds a quality no line here names,
   add the line, with its tag and owner. The standard is the record of what
   "good" has been found to mean.

**A level is done** when one cold run of its brief passes both gates at zero
interventions. Its source is then the brief and the seed that was picked:
the same tools rebuild it from those two.

## 0.4 What this game is

These are standing calls. A request overrides them only by saying so.

- **Setting:** 1990s Pennsylvania, weighted to Delaware County and
  Philadelphia; a reference, not a simulation. Embellishing and stylising
  are wanted (`USING_THE_FACTORY.md`, "The setting").
- **Shape of play:** a series of shooting galleries. Buildings, the roads
  between them, and props that are cover AND life. Report the mix of those;
  do not enforce a floor on it.
- **Players:** co-op crews of 1-4, online. Every frame is spent on somebody
  else's machine, so performance beats looks when they compete. A look is
  priced before it ships, not refused unpriced (`CLAUDE.md`).
- **Time of day:** five slots -- morning, high noon, afternoon, evening,
  midnight -- set once per level. The sky and every light level follow the
  slot (§17).
- **Night interiors:** a person must be able to read a room at night. Dens
  of sin (strip clubs, dive bars) are whole buildings kept dark and coloured
  on purpose.
- **The brands:** every name on a sign is an invented Delco brand, PG-13 and
  crass, never a real mark. A lit machine glows.
- **Authorship:** the test for any object is "could a person explain why
  this is here?" (`docs/reference/HUMAN_AUTHORSHIP_GUIDE.md`).

---

# Part I -- The Standard

Each section opens with v0's requirement, kept or tightened, then
**In this factory**: who makes it, which knob asks for it, what checks it, and
the status. Versions as of 2026-10-07: Level Factory 0.151.0, Lot 0.97.4, Deli
Counter 0.202.0, Zoo 1.81.0, Pixelcoat 0.61.0, Patina 0.29.1, Lux 0.68.2, Laser
Tag 0.23.2.

**The headline, measured on cold run 9193's level** (restaurant_row_001, the
most-tested brief this factory has):

| measure | value | what it means |
|---|---|---|
| interventions | 0 | it **works** |
| Lot's pacing estimate | 1.6-3.4 min, "likely TOO SHORT vs target" | **not yet evidence about session length.** The estimate is setup (30 s) plus one objective (120 s) and nothing else: Level Factory sets no `mode`, so `site_pacing` counts no travel (a heist's spawn -> objective -> extraction); it counts the objective building's own markers (1 objective, 0 loot in Lot's merged markers, where the package's room-level anchors number 9 objectives and 5 loot); and it judges against Lot's default 7-15 min, because the brief's `target_minutes` (25-35) is written where `site_pacing` does not look (roadmap 200). **Since Level Factory 0.153.0** the estimate counts a heist's travel and reads the brief's window: cold run 9195's three candidates read 2.8-3.4 min against 25-35, "likely TOO SHORT". It counts travel, setup and objective work, and no fighting |
| site-level objectives, loot, zones, encounter legs | all 0 in Lot's gameplay manifest | the heist is nine `objective` anchors, five `loot`, three `extraction`, 23 doors and 12 breach walls inside the buildings (`gameplay_anchors.json`, `interactives.json`), and nothing at site scale ties them into a plan |
| objective approaches | 2 | `tools/level_recipe_census.py`: 122 of 141 site plans score 2 and 2 of 141 reach 3. The count is graph degree, so 3 needs a fourth building or a measure of approaches as a player meets them |

**That table is the distance between a technical demo and a real level.**
Most of this standard is about closing it.

## 1. Factory Principles

v0's ten principles hold:
- generate causes before objects;
- design the district before the building list;
- the score is central in movement, not geometry;
- spokes need cross-links;
- ordinary fabric is not filler;
- verticality must change play;
- the art hierarchy supports the gameplay hierarchy;
- human behaviour makes believable clutter;
- replay comes from reinterpretation;
- performance is a design constraint.

**This factory adds four**, each paid for by a recorded mistake
(`CLAUDE.md`):

| principle | meaning here |
|---|---|
| **Fix the generator, never the level.** | A problem in a level is evidence about the tool that made it. The fix lands in the owning repo and the brief runs again (`USING_THE_FACTORY.md`). A level with hand-patches is the defects wearing a level's clothes. |
| **Measure the corpus before setting a bound.** | A tool has no taste: it reports, and a person decides. A threshold chosen first passes everything or fails everything (`docs/LEVEL_RECIPE.md`). |
| **A number that cannot move is not evidence.** | Prove an instrument can see a difference before believing a null result (`CLAUDE.md`, "A null result is not a refutation"). |
| **Every frame is spent on somebody else's machine.** | A look is priced in draw calls and frame time before it ships (§13). |

## 2. Generation Pipeline

v0 orders the work from large relationships to detail, in sixteen steps. The
factory's pipeline runs in stages (`tools/cold_drive/cold_drive.sh`), and
each of v0's steps lands in one of them -- or in none:

| v0 step | factory stage and owner | status |
|---|---|---|
| 1 mission fantasy | the brief (`level_factory.mission_brief.v0.1`) | GAP: no fantasy field (Appendix A) |
| 2 location + district | brief `theme`, `site_shape`, `road_grammar`; Lot assembles the site | BUILT for the street; GAP for a district (`building_library.pick_lot` scatters families: "anti-district", `docs/LEVEL_RECIPE.md`) |
| 3 time / season / weather | brief `time_of_day`, `weather` -> a Lux preset | BUILT for three slots (§17); GAP for season |
| 4 score / anchor | brief `archetype` -> a Deli Counter preset or library family; objective rooms | BUILT |
| 5 movement graph | Lot: paths, walks, crossings, the tactical graph; Level Factory's spurs | BUILT; MEASURED by approaches only (§5) |
| 6 land + parcel logic | Lot: pads, parking fields, yards, fences | BUILT; MEASURED by `tools/landuse_census.py` |
| 7 companion uses | the lot library's draw | BUILT, but drawn, not reasoned: no adjacency rule (§6) |
| 8 exploration + verticality | Deli Counter: stairs, ladders, hatches, floor holes, basements, terraces | BUILT |
| 9 art + cultural identity | Pixelcoat skins, Zoo species, the invented brands | BUILT; EYE |
| 10 human history + dressing | Deli Counter furnish, Patina, Lot surface dressing, posters | BUILT; EYE |
| 11 ambient life + audio | -- | GAP (§10) |
| 12 combat / escalation | Laser Tag scores bot crews against enemies | MEASURED (advisory); GAP for escalation |
| 13 extraction | extraction anchors | BUILT; GAP for a choice of extraction |
| 14 backdrop world | Lot's fence at the playable edge, Empties across the road | BUILT in part (§12) |
| 15 performance check | the fixed-station price | MEASURED |
| 16 traversal + plausibility | nav gate, walk test, Laser Tag, findings, frames | GATE for traversal; EYE for plausibility |

**The pipeline itself** is: plan -> shell (three candidate sites) ->
approvals -> art -> export (with the light bake) -> findings -> walk copy. A
cold run times it at roughly 30-45 minutes a brief on this machine.

## 3. Required Inputs

### 3.1 Mission fantasy

v0: one sentence saying what the players are trying to do and what makes this
place interesting to rob. **Status: GAP.** The brief has no field for it
(Appendix A). Until it does, the request's sentence goes in the brief's
`notes`, and the review reads the level against it.

### 3.2 Location contract

v0's nine questions are: region, municipality type, district archetype,
density, terrain and infrastructure, dominant transport, socioeconomic
character, surrounding uses, and development history.

**In this factory:**
- **Region and era are fixed:** `theme: delco_1997`. Pixelcoat's Delco
  profile and Zoo's `delco` styles carry them.
- **Philadelphia's themes exist on both sides now.** Pixelcoat carries
  `center_city` and `industrial_flats` among its 13 themes, and Zoo has
  styles for both. No level has been built in them yet.
  `USING_THE_FACTORY.md`'s "two profiles away" predates them.
- **Terrain is flat.** Lot builds "no terrain, no organic shapes"
  (`lot.py`). Height comes from buildings, kerbs and basements.
- **Density, surrounding uses and history** have no brief field: GAP, owner
  Lot (`docs/reference/LAND_PRESSURE_AND_SPATIAL_LOGIC.md`, §4 lists the
  inputs a generator should take).

### 3.3 Time context

| dimension | in this factory | status |
|---|---|---|
| era | 1997, fixed by the theme | BUILT |
| season | -- | GAP: Lux (sky, foliage tint), Zoo (street trees in leaf) |
| time of day | five slots, three built (§17) | BUILT, partly |
| weather | clear or rain; rain is an overcast day and overrides the slot | BUILT, partly: rain should layer over any slot (`_preset_for`) |

## 4. Score / Anchor Contract

v0's score record asks, for the score:
- what is valuable, and why it is here;
- how value moves;
- who has access;
- its public, employee and service faces;
- its normal and criminal access, and its landmark role.

**Keep it.** It is the record that makes a building a score rather than a
room with a marker in it.

**In this factory:**
- **The score is a building chosen by `archetype`.**
  - Deli Counter generates 23 presets (`presets.REGISTRY`): bank, corner deli,
    convenience store, pawn shop, gas station, strip club, video store,
    office, police station, warehouse and more.
  - The lot library adds 40-odd drawn families: bank branch, credit union,
    pharmacy, rail station, casino, freight terminal and others.
  - BUILT.
- **Objective rooms** carry the `objective_room` role (vaults, cash rooms,
  executive suites, server rooms). Lux lights them moody. BUILT.
- **Objective anchors** reach the package: 9 on cold run 9193's level.
  BUILT, and unmarked (roadmap 204). No anchor names its building and
  none marks the score: on cold run 9194's bank level the score's vault
  is the last of five objective anchors. On a library lot the mission's
  own generated shell, which the lot does not place, contributes anchors
  in its local frame, listed first. The package's own readers depend on
  that list: `tools/look_shots.py` takes the first anchor of each type for
  its eye-level shots, and the perf harness takes its stations from it
  (§13). GAP, owner Level Factory: mark the score, name each anchor's
  building, and stage no anchor from a shell the lot does not place.
- **The heist grammar exists in Deli Counter's spec types:**
  - `Objective` kinds: drill, hack, grab, thermite, interact;
  - `LootSpawn`;
  - `Zone` kinds: extraction, secure, drop;
  - `interactives` state machines: a vault door (locked, unlocked, open,
    breached), teller windows, safe-deposit boxes, breach walls, doors;
  - Zoo species: `vault_door`, `drop_safe`, `safe_deposit_boxes`,
    `teller_line`, `cash_stack`.
  BUILT as data.
- **The score is the building the brief asked for** (Level Factory
  0.152.0, roadmap 201). On a library lot `pick_lot` places the
  archetype's family first, and `building_library.score_building` makes
  that building, b0, the objective. The spawn is drawn among the others,
  and the site spec records which rule decided (`objective_from`:
  `archetype` or `seed`). With no family for the archetype the seeded pick
  stands, and says so. Proven in cold run 9194: all three bank_block_001
  candidates put the score in a bank's basement vault. BUILT. Dispatch's
  mission flow is spawn -> extract only.
  - *v1.1 read GAP here, correctly at the time:* the spawn and the
    objective were two independent seeded draws, blind to the archetype,
    and the objective could be the spawn building.
  - *What it exposed:* on bank_branch_a04 the crew wedges leaving the
    vault (roadmap 203, §5).
- **The score record** (why here, faces, access) is written nowhere. GAP:
  Level Factory, a `score` block the review reads against the frames.
- **The secure chain** (a public hall to a manager to a vault, each door
  harder) is `docs/LAYOUT_RULES.md` §B, enforced by layout lint for the
  families it covers. BUILT for banks and casinos.

### 4.1 Approach families

v0 wants 3-5 meaningfully different approaches, not 3-5 cosmetic doors.

| family | in this factory | status |
|---|---|---|
| public / obvious | the front door on the street (Level Factory 0.132.0 turns every front door to the road) | BUILT |
| stealth / concealed | a side or rear door (Deli Counter's rear staff entries; Lot's side-door landings); Deli Counter's combat audit reports `H_NO_STEALTH` and `H_ONE_ROUTE` per building | BUILT; MEASURED per building; GAP at site scale |
| technical (alarms, power, credentials) | the `hack` objective kind | BUILT as data; GAP for alarm, power or credential state (§11: the hooks exist and nothing calls them) |
| spatial / adjacent building | breach walls (Zoo's breach species; 12 in cold run 9193) | BUILT inside a building; GAP between buildings (no shared wall is breachable) |
| vertical | ladders, roof hatches, terraces | BUILT |
| below-grade | basements under the score | BUILT; GAP for tunnels or utility runs between buildings |
| loud | breach walls; the vault | BUILT for geometry; GAP for escalation (§11) |

## 5. Movement & Route Contract

v0's route record covers a route's two ends, distance and time, exposure,
cover, observation, height change, access, advantage, cost, the real-world
reason, and the alternative when it is blocked.

**In this factory, the routes exist as geometry and are only partly
described:**
- **Lot lays the street network**: through road, cross road, walks to real
  doors, side-door landings, crossings (`docs/STREET_RULES.md`).
- **Lot's tactical graph** (`site_tactical`, in the gameplay manifest) holds
  buildings, edges, the spawn, objective and extraction designations, and
  `objective_approaches`.
  - Its hard gates fire only when the site spec carries a `mode`. Level
    Factory writes `heist` since 0.153.0 (roadmap 200), so the heist gate
    -- spawn, objective and extraction joined -- runs on every generated
    site. It passed all 144 candidate specs on disk before it was
    switched on, and cold run 9195's three assemblies after. GATE.
    *v1.2 read: Level Factory writes none, so it is intel, not a gate.*
  - The crew's route is a straight polyline: spawn -> objective ->
    extraction.
- **`encounters.legs`** are meant to hold each leg's route choice, open
  ground and cover. They were **empty** on cold run 9193's pick.

### 5.1 Required network behaviours

| v0 behaviour | instrument | status |
|---|---|---|
| at least three distinct approaches | `tools/level_recipe_census.py` (`site_tactical._distinct_routes_to`) | MEASURED: 2 of 141 site plans reach 3. The count is the objective building's degree in a building graph, so a 3-building site cannot exceed 2. A measure of approaches as a player meets them (streets, doors, sightlines) is GAP, owner Lot |
| a short loop near the score | -- | GAP: the nav graph exists and loops are never counted |
| a longer bypass | -- | GAP |
| a shortcut with a readable cost | breach walls and ladders are shortcuts; nothing records their cost | BUILT, unmeasured |
| recovery when a route is unsafe | -- | GAP: no route is ever blocked, so recovery is never asked |
| dead ends only with a purpose | -- | GAP |
| everything reachable | Deli Counter's nav gate on every library build; Level Factory's structural checks ("blockers open") on every leg of a run; the walk test (`walktest_navqa`), which picks the candidate; Laser Tag's route completion and stuck events, which the cold driver's pick reads since roadmap 203 | GATE (nav gate, blockers); MEASURED (walk test, Laser Tag: advisory by contract). GAP: the walk test proves home -> each anchor and a chain through them, never the mission's order (spawn -> objective -> extraction). Cold run 9194's crew wedged on the leg it skipped, leaving the vault (roadmap 203) |

**v0's route record is the missing output.** Level Factory should write one
per route the plan intends, so the review can test them (§15.4). Owner:
Level Factory with Lot.

## 6. Parcels, Adjacency & Building Roles

### 6.1 Parcel logic

v0: parcels after routes, each accounting for frontage, access, service,
parking, deliveries and neighbours.

**In this factory, Lot does part of it:**
- a pad under each dumpster (Lot 0.93.0);
- parking fields in gaps (0.94.0);
- yards and fences (0.97.0, the playable edge);
- every front door facing the street (Level Factory 0.132.0).

**MEASURED by `tools/landuse_census.py`.** The unassigned remainder of the
plate ran 55-64% in 2026-10-03's census, against the land-use guide's
under-15% band. Verges and vacant lots are what move it (owner Lot).

### 6.2 Companion uses

| v0 relationship | in this factory | status |
|---|---|---|
| support (parking, loading, security) | parking fields, pads, dumpsters behind and beside | BUILT |
| complement (pharmacy and deli near a bank) | the lot library draws N families with "no two from the same family" | GAP: drawn, not chosen for a shared customer. `pick_lot` scatters by design |
| contrast (row homes, church, warehouse) | the Empties terrace across the road (12 non-enterable shells by default) | BUILT, one pattern |
| buffer / transition | -- | GAP: no transition parcel exists |

### 6.3 Building classes, as the factory builds them

| v0 class | in this factory | count on a typical level |
|---|---|---|
| A, score | the building Lot designates `objective` | 1 |
| B, major companion | the other lot buildings, fully enterable | 2 |
| C, minor companion | -- (every lot building is fully built) | 0 |
| D, ordinary fabric | Empties: dark interiors, shut doors by design, merged per side for draws | 12 |
| E, backdrop | -- | GAP (§12) |

v0's Building Purpose Test still applies: why would the player go here? Valid
answers are objective, route, loot, information, equipment, vantage,
concealment, shortcut, combat position or extraction. **Nothing records the
answer per building.** GAP: the building schedule (§14 E), owner Level
Factory. Until it exists, the review asks it of every enterable building.

## 7. Exploration & Verticality

### 7.1 Exploration rewards

| v0 reward | in this factory | status |
|---|---|---|
| information (schedules, codes, patrols) | -- | GAP |
| spatial advantage (shortcut, bypass, roof) | ladders, hatches, breach walls, terraces | BUILT |
| resource (tools, key items, optional loot) | `loot` anchors (5 on cold run 9193) | BUILT, as markers; GAP for what a loot point holds |
| tactical position (cover, vantage, fallback) | `cover` anchors (63 on 9193), Lot's cover plan, fortifiable rooms | BUILT |
| narrative / identity | posters, signs, brands, dressing | BUILT; EYE |

### 7.2 Vertical layers

**The library is low-rise, which is correct:** 59 of 131 specs one storey,
67 two, 5 three, none taller (`USING_THE_FACTORY.md`).

Across 146 non-generated specs: stairs 98, ladders 60, basements 49, slab
holes 12, ramps 6, fire escapes 2, setbacks 2. A generated building's spec
carries only archetype, mode, theme and seed, so a brief cannot ask for
storeys or a basement. Height comes from:

| element | in this factory | status |
|---|---|---|
| stairs | Deli Counter, every multi-storey building; pitch follows storey height (`CLAUDE.md`, "Known contract tensions") | BUILT; GATE (nav gate) |
| basements | Deli Counter (`has_basement`) | BUILT |
| ladders and roof hatches | Deli Counter; Lot's ladders reach the site (Lot 0.76.0); Dispatch makes them AI nav links | BUILT as geometry and AI links. GAP for players: a player can climb one only in a walk copy (`tools/walk_ladders.gd`, DEV ONLY) |
| floor holes (attack angles) | Deli Counter `slab_holes`, tagged `vertical_attack_angle` | BUILT |
| roof terraces (setbacks) | Deli Counter (roadmap 116) | BUILT, rare |
| fire escapes | Deli Counter, since 0.4x | BUILT, used by 2 of 131 specs. v0's MacDade vertical route needs one, and the setting needs more (`USING_THE_FACTORY.md`) |
| bridges, overpasses, embankments | -- | GAP: Lot has no terrain ("No terrain, no organic shapes", `lot.py`) |

**v0's rule holds:** a vertical connection is invalid if it does not join usable
nodes or does not change play. The nav gate checks the first. Nothing checks
the second (GAP).

## 8. Art Direction Contract

v0: define the visual identity after the spatial logic is stable, and make art
reinforce route readability, hierarchy, region, era and tone.

**The visual contract already exists.** `docs/DELCO_1997_ART_DIRECTION.md`
holds the walker's statement of the place, with an owner column. The
authorship guide is the test of whether an object is authored. A request's
visual thesis and tone words (v0 §8.1) are read against both.

| v0 art field | in this factory | status |
|---|---|---|
| visual thesis, tone words | the request; `DELCO_1997_ART_DIRECTION.md` for the setting | EYE |
| colour hierarchy (~70% base / 20% commercial / 10% accent) | Pixelcoat's `delco_1997` palette; `tools/art_standard_audit.py` measures the material library's chroma, value range and edge density against a controlled-contrast standard | MEASURED for the environment layer; EYE for the frame |
| material families | Pixelcoat's `delco_1997` theme maps 42 material kinds, stone, siding and shingle among them (89 material grammars) | BUILT. The specs rarely ask for them: brick is 20 of 131 (`USING_THE_FACTORY.md`, whose "29 kinds, no stone" is stale) |
| exterior lighting | the Lux preset of the slot (§17) | BUILT |
| interior lighting by use | by room kind, not use (§17) | GAP |
| weathering, maintenance gradient | Zoo's `Wear` attribute, seeded per style; Patina's passes | BUILT, uniform: wear has no cause (`docs/AUTHORSHIP_GUIDE_APPLIED.md`, shortfall 2) |
| cultural signifiers | Zoo's street furniture (signal, stop sign, mailbox, meter, payphone, newspaper box, shelter, hydrant, bollard, street trees), the invented Delco brands, posters | BUILT; EYE. GAP: utility poles and wires, window air conditioners, security bars, roll-down gates, awnings (`DELCO_1997_ART_DIRECTION.md` asks for each; no species) |
| landmark hierarchy | neon and pylon signs, lit storefronts, the brief's `landmark` field | BUILT as objects; GAP as a hierarchy (the field is read by nothing) |
| 5-8 hero props | Zoo species exist for many (the deli case, the registers, the video poker cabinet, the ATM) | BUILT as props; GAP: nothing chooses a level's heroes |
| signage and typography | Zoo's `smooth_type` faces by role (display, information, utility); Pixelcoat's brand names; every string written and denylisted | BUILT |
| vehicles, street furniture | Zoo cars, box truck, bus shelter, payphone; Lot places them by rule (`docs/STREET_RULES.md`) | BUILT |
| vegetation | Zoo street trees | BUILT, sparse |
| gameplay readability | props contrast with floor and walls (the walker's rule) | EYE |

**v0's hero-prop rule matters most here.** A hero prop is something a player
remembers or navigates by, not a costly asset. The factory can make them --
Zoo's species minting (`USING_THE_FACTORY.md`) is how the deli case was
made -- and has no step that names 5-8 for a level and places them where they
are seen. GAP, owner Level Factory (the request's `hero_props`, Appendix A)
with Lot and Deli Counter placing.

## 9. Human History & Set Dressing

v0: 3-6 visible historical events; a maintenance gradient by owner and use;
dressing derived from behaviour; 3-6 environmental story clusters.

| v0 item | in this factory | status |
|---|---|---|
| controlled history | Deli Counter's twin (two homes on one party wall, differentiated); Patina's per-Empty alterations (a TV antenna, a satellite dish: Patina 0.29.0) | BUILT, two moves. GAP for additions, conversions, vacancy as a district pattern (`DELCO_1997_ART_DIRECTION.md`, "the accretion") |
| maintenance gradient | Pixelcoat grammar wear (chips, streaks); Zoo's style `wear`; Deli Counter's `state`, `vacant`, `security_door` | BUILT, uniform: wear is per style, not per owner or use (GAP). Patina runs its `default` theme in the pipeline, and its decals exist only in a builtin theme the pipeline never selects |
| behaviour-based dressing | dumpsters beside or behind each building on a pad, from four invented haulers (Lot 0.90.0, 0.93.0); Deli Counter's furnish by room recipe (the deli case, registers, shelves, the poker cabinets); posters on four wall kinds; Lot's surface dressing | BUILT. The dumpster is the model v0 asks for: a use that needs waste handling derives the bin, the pad and the side it stands on |
| environmental story clusters | -- | GAP: nothing composes a small scene (a smoker's chair and crate behind the shop) |

**The authorship guide's test is the review's test here.** For each dressed
area, could a person explain why this is here? Furnish fills slots from
recipes. Rooms are not built round an activity, and density is not a per-zone
budget (`docs/AUTHORSHIP_GUIDE_APPLIED.md`, shortfall 4).

## 10. Ambient Life & Audio

v0: define who belongs here before the robbery and how they use the space,
and give it regional, district, building and local audio.

**In this factory, nothing.** No generator emits an audio player, and no
civilian exists. GAP, owner not yet named: it would be a new tool, or a
runtime layer beside Lux.

What exists is visual life, under "levels feel alive":
- screens that play (Zoo 1.45.0);
- moving parts: hot-dog rollers turn, the slush machine churns (Zoo 1.55.0);
- tree crowns sway and CRT screens roll, driven by the weather's wind
  (`zoo_worldskin.gd`, `lf_wind`);
- one failing fluorescent tube a room and cycling street poles (Lux 0.62.0);
- the club's stage lights cycle; Lux rain.

All BUILT. Audio is not yet on the walker's "alive" queue: wind's later
steps and a changing world come next there.

## 11. Combat, Escalation & Extraction

**In this factory, the encounter is Laser Tag's to grade, and it is advisory
by contract.**
- **The scenario:** bot crews (`crew_size` 4, `crew_health` 5) against
  enemies (`enemy_count` 6, `enemy_health` 2).
- **Where they stand:** Lot's spawn, patrol and enemy hooks. On cold run
  9193: 8 attacker spawns, 3 defender spawns, 5 patrol points, 63 cover points.
- **What it reports:** a grade (PASS, PASS_WITH_TUNING, WARN), events (shots,
  stuck, route progress) and findings (`LT_MAP_ENEMY_PATHING_BROKEN`).
- **Spawns are provisional.** The gameplay layer that will own them lives
  outside Level Factory, so a level-quality measure keys off geometry, not
  spawn placement.

| v0 item | in this factory | status |
|---|---|---|
| escalation shape (room -> building -> perimeter -> block -> district -> extraction) | the pieces exist and nothing calls them: Deli Counter's light anchors carry `reacts_to_alarm`; Lux has `pulse_alarm_lights`, `set_mission_phase` and the Mission Goes Hot preset; Lot's site audit checks `responder_spawn` and `horde_spawn` markers Level Factory never writes | GAP: no escalation state is represented anywhere (`docs/LEVEL_RECIPE.md`); the hooks are built and unwired |
| enemy access: arrival, staging, ingress, flanks | spawn, patrol and hook anchors | BUILT as points; GAP as a plan |
| which shortcuts enemies share | -- | GAP |
| where responders stop | -- | GAP |
| 2-3 extraction possibilities | extraction anchors (3 on 9193) | BUILT as points; GAP for a choice. The brief's `extraction_relationship` is read by nothing, and nothing varies between runs |
| replay by reinterpretation | `interactives` are state machines, and `collision_per_state` says which states are solid | GAP: nothing chooses among states at runtime (`docs/LEVEL_RECIPE.md`, "Two absences") |

## 12. Backdrop World

v0: the playable district must appear embedded in a larger place. Never let
the world simply stop.

| v0 item | in this factory | status |
|---|---|---|
| a credible playable edge | a 3 m perimeter wall round the plate (the site spec's `perimeter`); chain-link fences closing the Empty rows' gaps and ends (Zoo 1.77.0, Lot 0.97.0, phase one) | BUILT as a wall; EYE as a transition |
| non-playable continuation | the Empties terrace across the road | BUILT, one row |
| streets, wires, roofs continuing past the boundary | -- | GAP: `docs/proposals/BACKDROP_WORLD.md` (proposed, not started) and the walker's Pennsylvania backdrop guide (`docs/reference/PENNSYLVANIA_BACKDROP_WORLDS_GUIDE.md`, 18 recipes), filed for after the "alive" queue |
| distant landmark, skyline | Lux's skybox | BUILT as sky; GAP as massing |
| moving traffic, continuing audio | -- | GAP |
| a landmark that implies access that is not there | -- | EYE |

## 13. Performance Contract

> v0: "The Level Factory must receive technical budgets before final art
> generation. Performance is not a cleanup pass."

**The budgets this game has** (`docs/PERFORMANCE_CONTRACT.md`,
`docs/DRAW_CALL_BUDGET.md`):

| budget area | the figure | status |
|---|---|---|
| Frame target | 60 FPS, 16.7 ms, the walker's call (2026-09-27): a whole frame shared with gameplay, AI, netcode, audio and UI | MEASURED: the fixed-station harness (`_runs/perf_inner/run.py`; Level Factory's `tools/perf_stations_run.py`, stations from `gameplay_anchors.json` at four headings) reports median and p95 per view. There is no performance stage in the planner, and `docs/PERFORMANCE_CONTRACT.md` is proposed, not enforced |
| Renderer | GL Compatibility, the low-end target on purpose | GATE: packages ship on it |
| Draw calls | ~2,000 in the worst sightline, provisional, measured on an RTX 2060 in a debug build | MEASURED: no gate; cold 9088's worst station read 5,739 |
| Lights | at most 8 lights reaching one mesh (`max_lights_per_object`); steady lights baked into a lightmap, failing ones live | BUILT: the light bake (Level Factory 0.131.0) |
| Players | every client pays every frame, so a look's cost multiplies by the session | the rule behind `CLAUDE.md`'s "price a look" |

**What the factory measured last.** In the 2026-10-06 breadth sweep, all
views of ten missions came in under 16.7 ms p95. That is not a promise for a
new brief.

**How a look is priced** (`CLAUDE.md`, the hard rule): draw calls AND frame
time at fixed stations, before and after, on GL Compatibility, against a
control that proves the instrument can see a difference. A look that loses
the price ships cheap, and the record says what the expensive version would
have bought.

**Missing from v0's table, and from the factory** (GAP):
- network replication cost;
- memory and VRAM residency;
- streaming;
- cold-launch shader stalls, which are measured once (`cold_worst_ms`) and
  never gated.

Owner: `level_factory` (orchestration) with each tool for its own share,
per the contract's §6.

## 14. Required Outputs

v0: a generated level is not complete when geometry exists; it returns an
inspectable design package.

**In this factory, the package already carries part of v0's list**, and the
rest is the clearest list of what to build next:

| v0 output | what exists today | status |
|---|---|---|
| A. mission summary | the brief, in the workspace and the cold-run folder | BUILT, partly (no fantasy, score record) |
| B. district plan | -- | GAP |
| C. route graph | Lot's `tactical` (buildings, edges, designations, approaches) and `encounters.legs` (empty on 9193) | BUILT, partly; GAP for v0's route record (§5) |
| D. parcel plan | Lot's `yard_plan`, `field_plan`, `parking_plan`, `fence_plan`, pads | BUILT, partly |
| E. building schedule | Lot's `buildings`, `enterability` | GAP: no class, use or purpose per building (§6.3) |
| F. vertical network | `vertical_links` (stair, floor hole, hatch) and `ladders` | BUILT |
| G. art direction | the theme and the preset | BUILT, partly |
| H. cultural identity | the theme | BUILT, partly |
| I. set dressing plan | `furniture_plan`, Patina's dressing manifest, `dressing_layer.json` | BUILT, partly |
| J. ambient life / audio | -- | GAP |
| K. combat plan | `cover_plan`, the spawn and patrol anchors, Laser Tag's report | BUILT, partly; GAP for escalation |
| L. extraction plan | extraction anchors | BUILT, partly |
| M. backdrop plan | `fence_plan` | BUILT, partly |
| N. performance report | the fixed-station price (on demand, not per run); `light_bake.json` | MEASURED on demand |
| O. validation report | Level Factory's findings, Laser Tag's report, `INTERVENTIONS`, the cold run's `NOTES.md` | BUILT |

Where these live: Lot's gameplay manifest (`site.site.gameplay.json` in the
lot-assembly job) and the package (`gameplay_anchors.json`,
`interactives.json`, `light_bake.json`).

## 15. Scoring, Warnings & Failure Gates

### 15.1 The scorecard, recorded per run

v0's fourteen categories are kept, scored 0-5. **v1 makes the scorecard a
record:** `docs/cold_runs/cold_N/SCORECARD.md`, filled in by the walker or the
reviewer after the walk (Appendix C). The authorship guide asked for exactly
this, "the one item that needs no code" (`docs/AUTHORSHIP_GUIDE_APPLIED.md`).

Each category names the evidence that exists for it, so a score is argued
from something:

| category | evidence today | status |
|---|---|---|
| Place | `tools/landuse_census.py` (remainder, pads, fields); frames | MEASURED + EYE |
| Score | objective anchors present; the score record (§4, GAP); frames of the score from each approach | EYE |
| Routes | `tools/level_recipe_census.py`; Laser Tag's route completion and stuck events | MEASURED + EYE |
| Exploration | loot anchors counted; the walk | EYE |
| Verticality | `vertical_links` and ladders counted; the walk | MEASURED (count) + EYE |
| Adjacency | -- | EYE |
| Navigation | frames from the spine's stations (`tools/look_shots.py`) | EYE |
| Visual identity | the review frames | EYE |
| Cultural specificity | the review frames, against `DELCO_1997_ART_DIRECTION.md` | EYE |
| Human touch | the review frames, against the authorship guide | EYE |
| Interior readability (new) | `docs/findings/night_interiors/night_interior_census.py`: one station a room | MEASURED + EYE |
| Replayability | -- | GAP: nothing varies between runs, so this cannot score above 1 today |
| Combat | Laser Tag's grade and events; the walk | MEASURED (advisory) + EYE |
| Extraction | extraction anchors; the walk | EYE |
| Performance | the price: median and p95 frame time and draws at fixed stations, on GL Compatibility | MEASURED |

**v0's pass rule:** average >= 4.0, nothing below 3.0, and Place, Score,
Routes, Navigation and Performance critical.

**The decision v1 leaves to the walker.** Replayability cannot score 3 until
something varies between runs. Every level fails v0's rule on that one line
until then. **v1's proposal:** record it, and leave it out of the pass rule
until the first state that varies exists.

### 15.2 Hard failures, against the factory's gates

| v0 hard failure | the check that exists | status |
|---|---|---|
| the score has no clear playable approach | Lot's enterability (clear and routed entries); the walk test picks a candidate that reaches it | MEASURED |
| a required route is disconnected or ends at invalid geometry | Deli Counter's nav gate (library build); Level Factory's blockers; the walk test; Laser Tag's route completion | GATE (nav gate, blockers) |
| a vertical connection does not join usable spaces | the nav gate; stair checks (`tools/check_stair_pitch.py`) | GATE |
| all approaches have the same tactical profile | -- | GAP |
| entrances, service, entry or extraction lack access | enterability (clear and routed entries a building) | MEASURED |
| buildings block required routes or clearance | Lot's site gates; layout lint's door and clearance rules | GATE |
| unexplained leftover parcel area | `tools/landuse_census.py`: the remainder | MEASURED (55-64%, no bound set) |
| landmarks and affordances unreadable at player height | -- | EYE |
| the playable edge ends without a transition | the 3 m perimeter wall; fences on the Empty rows | BUILT as a wall; EYE as a transition |
| performance over the hard budget | the price | MEASURED, no gate: the 2,000-draw figure is provisional (§13) |

### 15.3 Design warnings

v0's ten warnings are kept as the review's questions:
- one chokepoint for every route;
- every spoke a dead end;
- a hidden hub with no reveal;
- decorative verticality;
- buildings with no entrance logic;
- height, spacing and frontage varying with no district pattern;
- density, wealth, vacancy and maintenance treated as one control;
- long blank walks or repeated blocks;
- backdrop landmarks implying access;
- uniform clutter.

None has an instrument yet. Each is answered by EYE in the scorecard until
one does.

### 15.4 Traversal review

For every entry point and the score: the fastest route, the safest, the most
elevated, the service route, and one alternate after a blocked edge. Review at
eye level first, then top-down.

**In this factory:**
- Laser Tag's bots walk the spine.
- The walk copy (`tools/walk_export.py`) lets the walker walk it.
- `tools/look_shots.py --station` frames any eye-level view.

The five named routes are not generated as routes (GAP, the route record of
§5). Until they are, the reviewer names them on the walk and records them in
the scorecard.

## 16. Minimal Designer Brief

v0's ten-line brief is the request, and Appendix A maps it field by field to
what the factory reads. The factory expands it into:
- site, routes, parcels and buildings: Lot, Deli Counter, Level Factory;
- verticality: Deli Counter;
- art and culture: Pixelcoat, Zoo;
- lighting: Lux;
- dressing: Deli Counter, Patina, Lot;
- combat: Laser Tag grades it;
- the backdrop: Lot and Zoo, in part;
- the performance price: on demand;
- validation: the gates and findings.

It does not yet expand into ambient life, audio, escalation, extraction
choice, or a district story.

## 17. Lighting and time of day (new in v1)

v0 puts lighting inside art direction. This game makes it a section of its
own, because it decides whether a level reads at all, and because the walker
set it as a slot per level.

**The five slots.** The walker, 2026-10-07: every level is set at one of
morning, high noon, afternoon, evening, or midnight. The sky and every light
level follow the slot, and one bake per level is baked for its slot.

| slot | brief `time_of_day` | Lux preset today | status |
|---|---|---|---|
| morning | -- | none: falls through to Gas Station Fluorescent | GAP (Lux preset, Level Factory word) |
| high noon | -- | none: falls through to Gas Station Fluorescent | GAP (Lux preset, Level Factory word) |
| afternoon | `afternoon` | Delco Summer Afternoon | BUILT |
| evening | `evening` | Blue Hour | BUILT |
| midnight | `night` | Delco Night | BUILT |
| rain, any slot | `weather: rain` | Heavy Rain, an overcast DAY: it overrides the slot | BUILT, with that trade recorded in `_preset_for` |

**What the preset carries:**
- **BUILT:** the sun or moon, the sky and skybox, the ambient,
  `fluorescent_energy_scale` (the interior fixtures, brighter at night), and
  `bake_room_fill` (Lux 0.68.0, the rooms' floor).
- **GAP:** window light. Every window spot ships at 3.0 at every hour,
  though at midnight it moved interiors by under 1 code
  (`docs/findings/night_interiors/`).

**Night interiors read** (the walker, 2026-10-07):
- **Ordinary rooms:** a person can read the room's walls, pieces and way
  through. **MEASURED** by `docs/findings/night_interiors/night_interior_census.py`
  (one station a room).
  - Cold run 9193: 16 fluorescent rooms average 39.2 of 255, and 8 bulb-lit
    rooms 23.4.
  - Moody rooms (basements, vaults) stay darker than fluorescent rooms on
    purpose: half the floor (Lux 0.68.2, `BAKE_FILL_BULB_SHARE`).
- **Dens of sin:** whole buildings with a tinted club room keep their built
  dark and colour (Lux 0.68.2). **BUILT.**

**The interior/exterior inversion**
(`docs/proposals/INTERIOR_EXTERIOR_BALANCE.md`). By day the street outshines
the shop; by night the lit shop window is the beacon. Lux 0.55.0 scales the
fixtures by preset for it. Whether each slot's frames read that way is
**EYE**.

**v0's lighting table for MacDade** (Part II §12) is per use: bank lobby,
pharmacy, laundromat, homes. Today the factory lights by room KIND, not by
use: a fluorescent row, moody pendants, the club set, a counter accent, heat
lamps, storefront spill. Lighting a use differently (cool pharmacy, warm
dining) is a Deli Counter anchor rule plus a Lux tuning row: **GAP**.

## 18. Determinism, candidates and acceptance (new in v1)

v0 does not say how a generated level is chosen or reproduced. This factory
does:

- **Every candidate is seeded.** A brief with `candidate_count` 3 builds three
  distinct sites from three derived seeds. Level Factory picks one on the walk
  test and Laser Tag's route findings, and the pick is reported, not hidden:
  "picked seed_9104 on the walktest and Laser Tag's route findings".
- **The same brief and the same tools build the same level.**
  - A run's identity is its brief plus the versions of ten tool repos, which
    `tools/cold_run.py` hashes at `--begin`.
  - A new building family in the library changes every seed's draw. Anchor a
    baseline on a brief that pins its draw before comparing across library
    growth.
- **Acceptance is a cold run** (`docs/COLD_RUN.md`): `INTERVENTIONS: 0`, every
  leg run, the package exported, the gates passed. Then the scorecard.
- **A level is never hand-finished.** If the walk finds something wrong, the
  fix lands in the tool and the brief runs again. The finished level is the
  brief's output, not an edited workspace.

## 19. Growing this standard (new in v1)

This document is meant to be wrong in places, found out, and corrected.

- **Each line's status is dated by the versions** at the head of Part I.
  When a tool grows a capability, the line moves from GAP to BUILT, and the
  shipping change says so (`docs/SHIPPING_A_CHANGE.md` step 8: record it where
  the next person will look).
- **A review finding a quality no line names adds the line**, with a tag and an
  owner. "Interior readability" entered this way on 2026-10-07, from the
  walker's note that night interiors read black.
- **A walker's standing call enters §0.4**, quoted, with its date.
- **Refutations stay**, above what replaced them. The repo's habit is to keep
  them where they were made: a retracted line is cheaper to keep than to
  rediscover.
- **v0 stays** as the walker wrote it (`docs/reference/LEVEL_FACTORY_STANDARD_v0.docx`).
  A later version that changes v0's intent says so, and why.

---

# Part II -- The gold standard: MacDade Savings & Loan District

v0's worked example is kept as the target, in full, in
`docs/reference/LEVEL_FACTORY_STANDARD_v0.docx`, Part II. It is the level this
standard is aiming at:
- a mid-1990s Delco commercial intersection;
- a neighbourhood savings bank as the score;
- four edges with four characters;
- five approaches;
- companion businesses with reasons to exist;
- landmarks at three tiers;
- lighting by use;
- three extractions.

**Read it first.** What follows is the same example read against the factory,
element by element: what a request for MacDade would get today, and what it
would take to get the rest. That is how any request should be read before it
runs. Statuses are as of 2026-10-07; "not checked" means nobody has looked.

### The district and its edges

| v0 | today | status |
|---|---|---|
| north: busy commercial arterial, bus stop, the bank visible | Lot's through road; Zoo's bus shelter | BUILT; GAP for traffic |
| east: older attached commercial strip and a narrow service alley | strip retail exists as a family; alleys are open work ("true alleys" on the walker's queue) | BUILT, partly; GAP for the alley |
| south: residential transition (duplexes, row homes, garages) | the Empties terrace of row homes; twins and walk-ups in the library | BUILT, partly: Empties are non-enterable |
| west: former light-industrial edge, fenced utilities | warehouse, auto shop and freight terminal families; the fence | BUILT, partly |
| a boundary following streets and property edges, not a rectangle | the plate is rectangular and the fence marks it | GAP |

### The score

| v0 | today | status |
|---|---|---|
| a bank on a prominent corner | the `bank` preset; bank branch and credit union families | BUILT |
| lobby, teller line, manager and loan offices | yes; the teller counters are a species (roadmap 44) | BUILT |
| security room, break room, rear service corridor | not checked per family | not checked |
| drive-through teller | -- | GAP: Deli Counter (a drive lane) with Zoo (the canopy) |
| second-floor records, basement vault | `bank_branch_a02`-`a04`: two storeys, a basement and vault rooms; `a03` adds `records_secure` | BUILT |
| public, employee and service faces | front and side doors exist; nothing records which face serves whom, and there is no armoured-car bay | BUILT, partly; GAP for the service face |

### How the vault can be solved

| v0 method | today | status |
|---|---|---|
| quiet / credentials | the vault door's `unlocked` state | BUILT as a state; GAP: nothing grants it |
| technical (alarm, security) | the `hack` objective kind | BUILT as data; GAP: no alarm state |
| spatial (breach a shared wall) | breach walls inside a building | BUILT, partly; GAP between buildings |
| vertical (upper access) | ladders, roof hatches | BUILT |
| loud (drill, thermite) | the `drill` and `thermite` objective kinds; the vault door's `breached` state | BUILT as data; GAP: nothing escalates |

### Routes A-E

| v0 route | today | status |
|---|---|---|
| A main street | the through road and the front door | BUILT |
| B commercial back route via the service alley | a rear door exists; the alley does not | GAP (Lot: alleys) |
| C residential approach | the Empties terrace is backdrop, not a route | GAP |
| D vertical: companion second floor, fire escape, roof, bank upper level | fire escapes are rare (2 of 131 specs); there is no roof-to-roof crossing | GAP (Deli Counter: fire escapes on companions; Lot: roof-to-roof crossings) |
| E utility / basement from the laundromat | no laundromat; no tunnel between buildings | GAP |
| a short loop, a long loop, a conditional shortcut, recovery when the front is held | unmeasured (§5.1) | GAP |

### The companions

| v0 building | today | status |
|---|---|---|
| Delco Pharmacy (B) | the `pharmacy` family (2 specs) | BUILT |
| Ron's Pizza & Steaks (B) | `primos_pizza` (1 spec) | BUILT, one design |
| Delco Check Cashing (C) | -- | GAP: Deli Counter, a new family |
| Laundromat (C) | -- | GAP: Deli Counter family; Zoo washers and dryers |
| ordinary offices and shops (D) | office and strip retail families; Empties | BUILT |
| residential transition (D/E) | Empties, twins, walk-ups | BUILT |
| light-industrial parcel | warehouse, auto shop | BUILT |
| neighbours chosen for shared customers | the library draws families apart on purpose | GAP (§6.2) |

### Landmarks and hero props

| v0 | today | status |
|---|---|---|
| freestanding bank sign (primary) | pylon signs exist for stores | BUILT, partly |
| pizza rooftop sign, pharmacy sign (secondary) | fascia signs and neon for every business | BUILT, partly; GAP for rooftop signs |
| church steeple, water tower | -- | GAP (backdrop, §12) |
| local: newspaper box, bus shelter | Zoo species | BUILT |
| local: utility transformer, alley couch | -- (no utility pole or wire species either) | GAP |
| station wagon | Zoo's car species | not checked for a wagon |
| chunky exterior ATM | Zoo's ATM | BUILT |
| washer/dryer wall | -- | GAP |
| heavy mechanical vault door | Zoo's `vault_door` species and the `vault_door` interactive | BUILT |
| choosing 5-8 heroes for this level | -- | GAP (§8) |

### Time, light and extraction

| v0 | today | status |
|---|---|---|
| 5:15 PM, late summer, warm hazy light | **that is the afternoon slot, not evening.** Blue Hour has its sun 4 degrees up, just after sunset. A request for MacDade asks `time_of_day: afternoon` (Delco Summer Afternoon) | BUILT; GAP for season |
| lighting by use: warm bank, cool pharmacy, warm pizza dining, bright laundromat, harsh check cashing, dim warehouse, tungsten homes | fluorescent rows, moody bulbs, the counter accent, porch lights | BUILT by room kind; GAP by use (§17) |
| three extractions, one active per run | extraction anchors | BUILT as points; GAP for one active per run |

### The density target, against today's typical level

| v0 element | target | typical today |
|---|---|---|
| primary score | 1 | 1 |
| major companions | 2-3 | 2 |
| minor gameplay buildings | 1-3 | 0 |
| ordinary district buildings | 5-10 | 12 Empties |
| ground approaches | 3+ | 2 (`level_recipe_census.py`) |
| vertical approach | 1+ | yes, inside the score |
| short loop / long bypass | 1+ each | not measured |
| conditional shortcut | 1+ | breach walls, ladders |
| secondary landmarks | 2-4 | fascia and neon, not composed as landmarks |
| hero prop clusters | 5-8 | not chosen |
| environmental story clusters | 3-6 | 0 |
| extraction possibilities | 2-3 | 3 anchors, none chosen |

### What MacDade would take, in the order that buys the most

0. **The score is the building the brief asked for.** DONE: Level Factory
   0.152.0, proven in cold run 9194 (§4). It sent the crew into a bank's
   vault for the first time, and on one bank variant they wedge leaving it
   (roadmap 203): a defect no level could show while the score was
   elsewhere.
1. **A third approach.** A fourth enterable building on the site, or (better)
   a measure of approaches as a player meets them. Owner: Lot, Level Factory.
   It moves the Routes category, which v0 makes critical.
2. **The request becomes the plan.** A `fantasy`, a score record, a building
   schedule (class, use, why a player goes in) and the route records, written
   into the package where the review can read them. Owner: Level Factory.
   This is how every later request becomes checkable.
3. **Session length, measured.** First make the pacing estimate measure the
   level (roadmap 200): a heist `mode` so it counts travel, and the brief's
   `target_minutes` reaching it. Then read what the level holds against the
   request's session, and add structure where it falls short: more
   objectives, loot that holds something. Owner: Level Factory, Lot.
4. **The companions MacDade names:** a check-cashing and a laundromat family
   (Deli Counter, with Zoo's props), and a bank drive-through.
5. **The alley and the climb:** service alleys behind commercial rows (Lot);
   fire escapes on companion buildings (Deli Counter). Both a facade
   signature and a route.
6. **A district, not a draw:** neighbours chosen for a shared reason (Lot's
   picker, roadmap 199).
7. **State that changes:** an alarm, escalation, and one extraction active per
   run. A runtime layer; owner to be named. It unblocks Replayability and v0's
   escalation shape.
8. **Light by use** (Deli Counter anchors, Lux rows), **morning and high
   noon** (Lux, Level Factory), **audio and ambient life** (new), **the
   backdrop** (Lot, Zoo, per the backdrop guide).

---

# Appendix A -- The level request (v0's Minimal Designer Brief, mapped)

Write a request in these fields. The table after it says which the factory
reads today, so every request also states what it cannot yet have.

```yaml
# --- what the walker writes ---
heist:        Neighborhood Bank                  # the score, in words
fantasy:      Rob a small bank near closing time and escape through the
              surrounding commercial district.   # ONE sentence
location:     1990s Delco commercial corridor
district:     aging suburban commercial intersection; residential edge south,
              light industry west                # the land-use story
scale:        medium                             # buildings to enter
density:      medium-high                        # land pressure
time:         afternoon                          # 5:15 PM, late summer -- morning | high_noon | afternoon | evening | midnight
weather:      clear
tone:         [familiar, worn, mundane, warm]
playstyle:    stealth -> loud
session_min:  [15, 25]
players:      4
must_have:    [alternate_entry, stealth_route, greed_opportunity,
               defensive_position, escape_not_equal_entry]   # LEVEL_RECIPE.md
hero_props:   [freestanding bank sign, drive-through canopy, station wagon]
dens_of_sin:  none                               # or which buildings stay dark
notes:        anything else, in plain words
```

| request field | brief field (`level_factory.mission_brief.v0.1`) | read by | status |
|---|---|---|---|
| heist (the score) | `archetype` | Level Factory's archetype aliases, then Deli Counter's preset or library family | BUILT; GAP: the score building is a seeded pick, not the archetype's (§4) |
| the score's steps | `objective_hypotheses` | only the functional lock's signature (`models.py`); no builder | GAP |
| fantasy | -- (`display_name`, `notes`) | nothing | GAP: Level Factory, a `fantasy` field the review reads back |
| location / district | `theme` (`delco_1997`), `site_shape`, `road_grammar` (T, or `crossroads`) | Lot, Pixelcoat | BUILT for the street; GAP for the district story (land use by zone: Lot, roadmap 199) |
| scale | `building_count`, `lot_library`, `empties` (`across` by default) | Level Factory, Lot | BUILT |
| density / land pressure | -- | nothing | GAP: Lot (`docs/reference/LAND_PRESSURE_AND_SPATIAL_LOGIC.md` §4) |
| time | `time_of_day` | Level Factory `_preset_for` -> a Lux preset | BUILT for afternoon, evening, night; GAP for morning, high noon (§17) |
| weather | `weather` | `_preset_for`: rain becomes Heavy Rain and overrides the slot. Rain also sets Pixelcoat's wet maps, Lot's wet ground and the wind that sways trees (`lf_wind`) | BUILT, with that trade; fog, snow and overcast read as clear |
| tone | -- | nothing | EYE: the review checks it against the frames |
| playstyle | -- | nothing | GAP: no alarm or escalation state exists (§11) |
| session_min | `target_minutes` | Lot's pacing estimate, as its window (`pacing.target_minutes`, Level Factory 0.153.0); a level outside it raises `LOT_PACING_OUTSIDE_TARGET`, non-blocking. What the window means -- a session, which the estimate cannot reach without a combat term, or the structural route, which it measures at about 3 min -- is the walker's call. *v1.1 read "Laser Tag's scenario timing, BUILT": wrong; nothing in Laser Tag reads it, and before 0.153.0 nothing read it at all* | BUILT (cold run 9195) |
| players | `crew_size` (4), `crew_health` | Laser Tag; `crew_size` also places the crew's spawns (Lot) | BUILT |
| enemies | `enemy_count` (6), `enemy_health` | Laser Tag spawns the count over Lot's hooks; **Lot always places six hooks** | BUILT, partly: below six the spread is uneven (`models.py`) |
| route shape, extraction, height | `route_shape`, `extraction_relationship`, `verticality` | no builder: `route_shape` is Level Factory metadata that Lot ignores, and the other two feed only the functional lock's signature. `batch create` says so out loud since Level Factory 0.153.0 (`UNBUILT_BRIEF_FIELDS`) | GAP (roadmap 200) |
| landmark | `landmark` | **nothing reads it** (`docs/LEVEL_RECIPE.md`, re-checked 2026-10-07) | GAP: Lot or Level Factory |
| must_have | -- | `tools/level_recipe_census.py` measures one of them (approaches) | MEASURED for one; GAP for four |
| hero_props | -- | nothing | GAP: minted per prop by Zoo (`USING_THE_FACTORY.md`, minting) |
| dens_of_sin | -- | Lux 0.68.2 keeps any building with a club room dark | BUILT for clubs; a dive bar needs the club set (Deli Counter) |
| -- | `candidate_count` (3) | Level Factory: derives the seeds, builds 3, picks one | BUILT |
| -- | `seed_policy` | nothing | unused |

**The brief file today** looks like `docs/cold_runs/cold_9193/briefs/restaurant_row_001.json`.
Its `notes` are where a cold run records what it tests, what it predicts and
what to check after. That habit is worth keeping for every level request:
- **predicted:** what the run should show;
- **check after:** which frames and numbers decide it.

---

# Appendix B -- The checklist, with what checks each line

v0's checklist, each line with what answers it today. The review walks it
top to bottom, and every EYE line is a reviewer's tick.

| v0 check | answered by | status |
|---|---|---|
| one-sentence mission fantasy is clear | the request; `notes` | EYE |
| location and district archetype specific enough to drive land use | the brief's `archetype`, `theme`, `site_shape` | BUILT; GAP for a district |
| era, season, time and weather explicit | `theme`, `time_of_day`, `weather` | BUILT; GAP for season |
| the score has a plausible reason to exist at the site | the score record (GAP) | EYE |
| three approaches with distinct tactical profiles | `tools/level_recipe_census.py` | MEASURED (2 of 141 reach 3) |
| short loop, bypass, shortcut, blocked-route recovery considered | -- | GAP |
| parcels and buildings have frontage, customer and service access, operating space | Lot's enterability; doors to the street; pads and fields | BUILT; MEASURED (`tools/landuse_census.py`) |
| every playable companion has a reason for player entry | the building schedule (GAP) | EYE |
| ordinary fabric supports density, sightlines, history, transitions | the Empties terrace | BUILT; EYE |
| vertical routes connect valid nodes and change play | the nav gate (valid nodes) | GATE; EYE (change play) |
| primary, secondary and local landmarks are distinct | the brief's `landmark` is read by nothing | EYE |
| colour, materials, lighting and hero props support the gameplay hierarchy | `tools/art_standard_audit.py` (the environment layer) | MEASURED, partly; EYE |
| cultural signifiers subtle, plural, location-specific | the brands, street furniture, posters | EYE |
| weathering follows causes; maintenance varies by owner and use | -- | GAP |
| set dressing derives from human behaviour | furnish recipes, dumpsters on pads | BUILT, partly; EYE |
| ambient NPCs and audio belong to the district | -- | GAP |
| combat expands through the authored environment | Laser Tag (advisory) | MEASURED, partly; GAP for escalation |
| extraction is a gameplay decision, not a finish trigger | -- | GAP |
| the backdrop continues streets, utilities, roofs, terrain, activity | the fence, the Empties | BUILT, partly |
| performance constraints known before polish | the price (`docs/PERFORMANCE_CONTRACT.md`) | MEASURED |
| **new:** night interiors read, dens of sin excepted | `night_interior_census.py` | MEASURED |
| **new:** zero interventions | `tools/cold_run.py --end` | GATE |
| scorecard average >= 4.0, nothing below 3.0 | Appendix C | EYE |
| no critical category fails (Place, Score, Routes, Navigation, Performance) | Appendix C | EYE |

# Appendix C -- The scorecard record

Copy into `docs/cold_runs/cold_N/SCORECARD.md` after the walk. Every score
cites its evidence: a frame, a census line, a Laser Tag count, the price, or
"walked".

```markdown
# Scorecard -- cold run N, <mission_id>, seed <seed>

Reviewer: <name>    Date: <date>    Slot: <time_of_day>    Interventions: <n>

| category | 0-5 | evidence |
|---|---|---|
| Place | | landuse_census: remainder ..%; frames ... |
| Score | | the score from each approach: frames ... |
| Routes | | approaches = ..; Laser Tag route completion ..; walked |
| Exploration | | loot anchors ..; walked |
| Verticality | | vertical links ..; walked |
| Adjacency | | why each neighbour is there: ... |
| Navigation | | could I reorient without a HUD? frames ... |
| Visual identity | | one screenshot that names this level: ... |
| Cultural specificity | | ... |
| Human touch | | the authorship guide's "why is this here?" on 3 areas: ... |
| Interior readability | | night census: ROW .. / MOODY ..; rooms under 10: .. |
| Replayability | (recorded, not passed) | what varies between runs: ... |
| Combat | | Laser Tag grade ..; stuck ..; walked |
| Extraction | | ... |
| Performance | | median .. ms, p95 .. ms, worst view .. draws |

Average: ..   Lowest: ..   Critical failures: ..

## What the walk found that no line names
(each becomes a line in docs/LEVEL_STANDARD.md, with a tag and an owner)

## What lands where
(each finding, the repo that owns its fix, and the roadmap item)
```
