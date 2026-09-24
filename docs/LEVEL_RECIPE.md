# The level recipe — what a generated level must let a player DO

The walker, 2026-09-24:

> The procedural tool's job is no longer "make me a believable Delco block."
> It becomes: "make me a fun heist level, using a believable Delco block as
> the material."

Every gate this factory has measures whether a level WORKS — can a body get
from A to B, do the stairs connect, does the package load. `PIPELINE_ROADMAP.md`
item 18 has said since it was raised that none measures whether a level is
GOOD, and put a number on it: of eight problems found by walking a generated
level, **four were invisible to every gate in the pipeline**.

This file is the other half. It describes a level by what a player can do in
it, and it is deliberately the SMALL version — the walker's own MVP, not the
full recipe it was cut from. A contract nobody can measure is a wish list.

## The MVP

```yaml
id: flappahs
heist: robbery
shape: t_junction
target: convenience_store

approaches:          { min: 3 }
player_choices:      { min: 2 }
combat_spaces:       { min: 3 }
escape_routes:       { min: 2 }
navigation_loops:    { min: 1 }
alarm_changes:       { min: 2 }
supporting_buildings:{ min: 2 }
empty_buildings:     { min: 4 }

requires:
  - alternate_entry
  - stealth_route
  - greed_opportunity
  - defensive_position
  - escape_not_equal_entry
```

## What already answers each line, and what does not

THE POINT OF THIS TABLE is that roughly half of the MVP is aggregation of
signals the tools already compute and nobody gates on, and the other half does
not exist at any level. Knowing which is which is what stops this becoming a
year of work before anything is measurable.

| line | instrument today | owner |
|---|---|---|
| `approaches` | `site_tactical._distinct_routes_to` counts edge-distinct first hops to the objective; `site_layout_lint` S5 warns under `SPREAD_MIN` 90 deg of angular spread. Both INTEL, neither gates. | Lot |
| `combat_spaces` | Deli Counter tags every room `combat_range: close/medium/long`. Never aggregated per site. | DC tags, Lot aggregates |
| `defensive_position` | DC tags rooms `fortifiable: true`. Never counted. | DC / Lot |
| `greed_opportunity` | `loot` in gameplay.json. Not related to risk. | Lot |
| `supporting_buildings`, `alternate_entry` | `site_enterability` answers "can you reach a building's entries". | Lot |
| `empty_buildings` | **nothing places them** — roadmap 106, open. | Level Factory |
| `escape_routes` | extraction anchors exist; **the inequality with the entry is unmeasured**. | Lot |
| `navigation_loops` | the nav graph exists; loops are never counted. | Lot |
| `alarm_changes` | **nothing**. No escalation state is represented anywhere. | absent |
| `player_choices` | **nothing**. | absent |
| `stealth_route` | **nothing**. | absent |

## Two absences that are architectural, not missing measures

**Nothing varies between playthroughs.** Everything is baked at export: one
navmesh, one set of spawns, one door state. Patrick Murphy's account of Payday
2's "Hoxton Breakout" is the counter-model — entrances selected dynamically,
the fuse box relocated, three of five side objectives chosen in any order — and
his claim is that replayability comes from elements that change WITHIN one
level rather than from more levels. The hooks exist here (`interactives` are
state machines, `collision_per_state` says which states are solid) and nothing
chooses among them at runtime.

**More layouts give more levels; dynamic elements give more play per level.**
They are different axes and only the first is currently expressible.

**`building_library.pick_lot` is anti-district.** Its contract is "no two from
the same family", which deliberately SCATTERS archetypes. Kevin Lynch's
districts, and the walker's Delco seams (`commercial -> alley -> rowhomes`),
need the opposite: clustering by land use with a named transition between. That
is an inversion of the current picker, not a gap in it.

Two smaller findings from the same reading: the brief's `landmark` field is
**read by nothing** — the same defect `weather` had before Lux consumed it —
and `_write_site_spec` declines to emit courtyards on purpose, *"there is
nothing here to derive its position from; emitting one at an arbitrary point
would be a number nobody chose."* Lynch's nodes were deferred for want of a
reason to place them, and a recipe is exactly that reason.

## How a gate here earns its threshold

The same way every other number in this repo did, and for the reason
`tools/repetition_census.py` states: a tool has no taste, so it reports and a
person decides. **Measure the corpus first, set the bound second.** A threshold
picked before the distribution is known either passes everything, in which case
it is decoration, or fails everything, in which case it stops the build over a
number nobody chose.

`tools/level_recipe_census.py` is that measurement for the `approaches` line.
It scores every site plan on disk and prints the distribution. It sets no
threshold and says so.

## What this file is not

It is not a replacement for the traversal gates. A level that fails `nav_gate`
is broken whatever it scores here; a level that passes both is merely not
obviously bad. And it says nothing about whether a level is FUN, which no file
can — it says whether the level affords the things fun is made of.
