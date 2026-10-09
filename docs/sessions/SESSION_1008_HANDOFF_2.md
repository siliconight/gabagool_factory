# Session handoff 2 -- 2026-10-08, evening

Written at the close, from the artifacts. It follows `SESSION_1008_HANDOFF.md`,
whose open pieces this session took up. Read `CLAUDE.md` and the memory
index first, then this, then `PIPELINE_ROADMAP.md` items 214 and 215.

## State at close

| repo | version | unpushed commits |
|---|---|---|
| zoo | 1.86.0 | 6 |
| lot | 0.101.0 | 8 |
| level_factory | 0.162.1 | 9 |
| lux | 0.69.0 | 2 |
| lasertag | 0.25.0 | 1 |
| deli_counter, dispatch, patina, pixelcoat, pipeline | 0.203.0, 0.5.2, 0.29.1, 0.61.0, 0.6.0 | 0 |
| factory root | -- | 27 before this handoff's commit |

- **Clean.** Every tool repo has a clean tree.
- **Nothing running.** No cold run is in flight, and no Godot or Blender
  process is left.
- **Not pushed.** Commits are local; push only when the walker asks.
- **Disk:** 25 GB free (95% used). `tools/factory_retire.py` lists 13.3 GB
  retirable in 17 items, cold-run workspaces beyond the newest 12. Nothing
  was retired; `--apply` is the walker's call or the disk's. Each cold run
  adds about 0.7 GB.

## What shipped

**Roadmap 213 CLOSED: the club's stage, live and brighter.**
- **The change.** Lux 0.69.0 and Level Factory 0.160.0.
- **Cold run 9205.** The stage reads as the 8x copy the call was made
  from, and the frozen first colours on the lamp housings are gone.

**Roadmap 212 CLOSED: responders can arrive, and their car ships.** Cold
runs 9206 to 9209, 0 interventions each.
- **Zoo 1.86.0, the cruiser.** A 1990s Crown Victoria lettered DELCO COUNTY
  POLICE, liveries `black_white` and `white_blue`. Five meshes, 3,476
  triangles. `simple_car`'s own cars hashed unchanged.
- **Lot 0.100.0 and 0.100.1.** The vehicle is Zoo's, the lane steers round
  the getaway van (0.649 m on every candidate), and the planner checks the
  boxes it records.
- **Level Factory 0.161.0.** The steered lanes ship as boxes.
- **Lot 0.101.0 and Level Factory 0.162.0.** The site kit builds the car,
  and the package names it for every arrival and stands it nowhere.
- **Level Factory 0.162.1.** The car's import is Dynamic, so a spawned one
  samples the lightmap's probes.

**Roadmap 214 OPEN: the walker's modern low-poly standard.**
- **Filed** in `docs/reference/`, with the original `.docx`.
- **Addendum A**, from the walker's notes: subdivision, sculpt and
  retopology, multires.
- **The Zoo mapping:** nine gaps, measured.
- **Zoo's README** points at it.

**Roadmap 215 OPEN, split out of 212.**
- **`S_RESPONDER_ARC`.** All three arrivals sit within 6 degrees of the
  objective on club_block_014.
- **The site audit reaches no report.** Its findings are in Lot's job log
  only.

## Waiting on the walker -- ask before building

1. **The cruiser's livery:** `black_white` (the default) or `white_blue`.
   Frames are in `docs/findings/cruiser_build/`. Changing the default is one
   constant, `cruiser_forms.DEFAULT_LIVERY`.
2. **Optional: a stage-lamp lens that follows the lamp's colour.** The 8x
   frames the stage call rested on showed lit housings that were really the
   old bake's frozen colours. Not built, not priced.
3. **Offered, not asked for:** a `.docx` of the standard with Addendum A
   folded in. The `.md` carries it; the `.docx` is unchanged.

## Ready, no input needed

- **Roadmap 214's trials** (Addendum A.4), cheapest first, each priced
  on/off at fixed stations:
  - weighted normals;
  - convex-edge wear in vertex colour (`wear_colors` darkens concave
    vertices only);
  - a procedural bake source;
  - detail on it.
- **Roadmap 214's record gaps:** the missing asset-record fields, and a
  budget class per genome.
- **Roadmap 215:** carry the site audit into Level Factory's validation
  report first, so whatever it says is counted. Then the arc question.
- **Roadmap 208:** `docs/findings/walktest_crew_body/rewalk.py --variant
  crew_full`.

## Mistakes caught this session, kept where they happened

- **A phantom major** (cold run 9206, seed_9080). The planner checked
  unrounded boxes, and the record rounded them onto the van. Fixed in Lot
  0.100.1.
- **The car baked static** (cold run 9208). Fixed in Level Factory 0.162.1.
- **A source-order test** failed the first 0.162.1 suite on the bake's
  split call. Fixed and recorded.
- **Two wrong first-draft claims in the Zoo mapping:** `simple_car`'s bevels
  and the counter species' name. Corrected before filing.
- **An instrument written against a guessed schema** (the GLB scan's
  fields). Corrected against 9207's real file before it read 9208.
