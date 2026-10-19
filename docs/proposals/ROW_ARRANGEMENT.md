# The row's arrangement: what a seed varies, and what it could (proposal, 2026-10-19)

**Status: PLANNED, not built.** Roadmap 105's first step past its measurement. Mapped read-only against Level
Factory 0.218.2 and Lot on 2026-10-19. Re-read every cited line before patching (CLAUDE.md, grounding).

## What the item measured

Roadmap 105 (2026-10-15, `docs/findings/open_items_remeasure/arrangements_105.py`): six plans -- three seeds each of
urban_row_001 and restaurant_row_001 -- stand the mission's buildings in ONE arrangement. Three in a row facing
south at rot 0, at x -51, +1 to +4 and +48 to +54: deli, pharmacy, office. The seed varies the block (where the
side streets and the rear lane cut) and the far side's Empties, not the row. Both missions are `site_shape: strip`.

## Why, read off the code

1. **The order is the pick's.** `level_factory/packages/pipeline/building_library.pick_lot` puts the brief's
   archetype first (the anchor), then the template's families in the guide's order (`C03_station_neighborhood`:
   pharmacy, then office; roadmap 230), then random families. `site_variation.site_placements` lays the list west
   to east in that order (`row_offsets`). So urban_row_001 stands deli, pharmacy, office on every seed, and the
   objective -- the anchor -- always at the west end.
2. **The turn and the stagger were removed on purpose.** `site_placements` still draws a cardinal yaw and an
   across-row stagger per building, and discards both on a row: Level Factory 0.132.0 turns each front door to the
   through road (`fronts`), and 0.135.0 stands every street edge on one building line (`street_line`). Both are
   realism -- a door on the street, a building line -- and a row that undid either would read as damaged, not
   designed. They stay.
3. **What a seed still varies on a row:** the along-row nudge (`_ALONG`, up to 6 m), the drawn archetypes' own
   widths, the block grammar's side streets and rear lane, and the far side's Empties.
4. **Other shapes exist and turn buildings.** `SHAPES = ("row", "L", "courtyard")`. An L stands its arm on a
   second street; a courtyard rings a court. A brief that asks `strip` gets `row`, and both measured missions ask
   `strip`.

## The options, each a dial

- **A. A seeded mirror of the row** (Level Factory, smallest). Per candidate, the stream decides whether the picked
  list is laid west to east or east to west. Every neighbour pair is kept, so no template's adjacency audit moves.
  The objective stands at either end, and the side streets, the rear lane and the van move against it. The cost:
  on a symmetric street a mirror plays as a reflection; on a block whose side streets the seed cuts at different
  x, it is a different approach.
- **B. The corner building fronting the cross street** (Lot and Level Factory). The row's end building, where a
  side street meets the through road, turns its front door to the side street -- `fronts` already knows how to
  turn a front to a road. Philadelphia corners do this, and it gives a candidate a building entered off the main
  line.
- **C. A gap in the row** (Lot): a vacant lot or a yard between two buildings, where the seed says. It belongs with
  roadmap 188's remaining fence work (vacant lots) and the land-use guide.
- **D. The side of the street** (Level Factory): which side of the through road the mission's buildings stand on,
  the other side keeping its Empties.

## The call this proposal recommends

A first, then B. A is one reorder inside `lot_for` keyed on the candidate seed -- the planner, the compose spec and
the site spec all read `lot_for_brief`, so they cannot disagree -- behind a brief or profile dial,
`row_order: seeded | picked`, default seeded: a call meant to be changed. B waits on A's numbers.

## How to measure

- **Offline, before any build:** over 20 seeds of each strip mission, how often the objective changes ends, and
  that no adjacency audit line appears that did not before (`S_ADJACENCY`).
- **Cold runs:** every strip mission once, then the breadth sweep: interventions, the picked candidate's grade,
  Laser Tag's route completion, sightlines and pacing, against each mission's last run.
- **Frames:** spawn toward objective on two candidates of urban_row_001, before and after.

## What is the walker's

Whether a mirrored row reads as variety at all, and B's look: a corner store entered from the side street.
