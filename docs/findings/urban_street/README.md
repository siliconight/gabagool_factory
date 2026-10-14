# The first urban street: a mid-rise wall across the street, seen and priced (roadmap 241)

The walker chose a new urban level type on 2026-10-11 (`docs/reference/URBAN_MIDRISE_COMPS.md`): mid-rise
blocks at the sidewalk line, touching, block after block. Then, 2026-10-13: "go ahead with the census, then
241".

## What shipped: Level Factory 0.200.0 (65cf5e7), steps 2 and 3, the first cut

- **The brief asks.** A brief asks with `streetscape: "urban"`. `models.streetscape_effective` decides what
  it gets: urban only where a terrace stands, and the functional signature carries it only then.
- **Every other brief is today's strip,** lock and terrace unchanged; the suite holds both.
- **An urban brief's far side** is a continuous wall of Deli Counter 0.213.0's mid-rise Empties
  (`building_library.empties_for_brief` draws `gs_midrise_*`; `empties.terrace(continuous=True)` drops the
  alley every five to eight houses). One fault found on the way: the adapter's preset list had not learned
  Deli Counter 0.213.0's `empty_midrise`, so `test_dc_preset_registry` had been red, unseen.

## Proven: cold run 9287 (`docs/cold_runs/cold_9287/`)

`urban_row_001` is restaurant_row_001's brief plus `streetscape: urban`. It ran at 0 interventions, and every
candidate's site stood 8 or 9 mid-rises across the street, themed. The near side's lots are 9285's buildings
exactly, so this folder's A/B isolates the far side:

    bash docs/findings/urban_street/ab_record.sh 9285 restaurant_row_001 9287 urban_row_001

**Seen** (`ab_9287/ab_sheet.png`, 9285 left, 9287 right):
- **The two road ends** look down the street, and the far side's three-storey rowhomes are now brick blocks
  that leave the frame's top.
- **From the south** (orthographic, `elev_S`), the wall's backs are dark, with lit windows.
- **From the north,** the wall stands taller than everything in front of it, at two heights.
- **The near side** is still the strip's one-to-three-storey row.

**Priced** (`ab_9287/price/price.txt`; Level Factory's fixed-station harness, 53 headings, control-subject-control):

    draws a heading     807 -> 736 on the mean (-71.6; -302 to +58)
    p95 frame time      -0.15 ms at the median (the controls' floor 0.03 ms)
    textures            76.0 -> 74.4 MiB
    buffers             47.9 -> 68.6 MiB
    video memory        123.9 -> 142.9 MiB

**What the price says.**
- **The wall is cheaper to draw than the terrace it replaced.** Eight or nine shells merged per side, against
  about two dozen rowhomes.
- **It costs about 19 MiB more resident memory, all of it buffers,** the geometry of five- to twelve-storey
  facades. Both controls read 47.9 MiB here. An earlier measurement (roadmap 238) saw buffers vary from 48.0
  to 56.1 MiB between runs of one package, and +20.7 is outside that.
- **The lightmap:** 3,037 users, against 3,392.

## What the walker is asked

- **The frames.** Is this the wall the comps meant, before the near side follows?
- **The near side, next.** The mission's own buildings among mid-rise Empties, with no plate between them.
  It meets what Lot lays after the roads (parking, pads, dumpsters), so it is its own cut.
- **Not drawn yet:**
  - heights by cause (taller away from the action);
  - the 2.0 m frontage, kept;
  - tree pits;
  - the corner shop at grade;
  - the dusk haze.

## Not attributed

- **Laser Tag's `LT_MAP_BLIND_MAP`** (moderate) is on all three candidates where 9285 had it on two: 52 to
  63% of positions never seen from an enemy spawn. A gapless, taller wall cutting sightlines is the obvious
  reading, and it is not measured. Enemy spawns are provisional until a gameplay layer owns them.
- **The bake's 60 fewer models** (566 -> 506) and 355 fewer users are read as the shell count, eight or
  nine shells where there were about two dozen. They have not been counted shell by shell.

## The near side: the second cut (cold runs 9288 and 9289)

**Lot 0.121.0 (bb6011d).** The planners that keep clear of what stands -- fields, pylons, dumpsters, pads, cover --
are handed every Empty as an obstacle. Until now they read only the mission's buildings, which was harmless
while Empties stood only across the road. `lot_replay.py` replayed the picked `lot_assemble` jobs of cold runs
9278 to 9287 from their own `job.log` before and after: 10 jobs, 0 files differ. The control, two replays
before, was 0 too.

**Level Factory 0.201.0 (27fc03d).** `empties.infill` stands Empties along the near building line between
the mission's own buildings. Each building keeps a 4 m passage on both sides. Side streets and the service lane
are never built over.

**Cold run 9288: nothing stood.** `near_room.py` measured why. The library buildings, their passages and the
block grammar's side streets leave rooms of 12.67, 11.35, 7.33 and 6.70 m, and the narrowest mid-rise
measures 15.3.

**Deli Counter 0.217.0 (b3c2354b): three narrow mid-rises,** 12.30, 10.30 and 6.60 m as built. Every other
shell is byte-identical.

**Cold run 9289:** one or two narrow blocks stand on the near side of each candidate, and the picked one
grades PASS 100. Against the strip (`ab_9289/`), over the 52 headings that stood in the same place
(`price_matched.py`; the geometry-derived `longest_sightline` station moved):
- draws -38.5 a heading on the mean;
- p95 -0.26 ms at the median, against a 0.12 ms floor;
- video memory 123.9 -> 161.9 MiB, buffers 47.9 -> 83.0.

**Found, not fixed:**
- **One candidate's enemy spawns found no ground** (`LOT_ENEMY_SPAWN_UNPLACEABLE`), and Laser Tag refused
  it. By elimination it is the near-side block and the far-side wall together. Enemy placement is
  provisional.
- **A 6.70 m room stayed open.** The deal had already spent its one narrow block; a fresh bag when nothing
  left fits is the refinement.

## The starved candidate, traced: Lot 0.122.0

**The instrument.** `spawn_filters.py` reruns a candidate's own `lot_assemble` job, as its `job.log` records it,
into `_scratch/`. It wraps `site_spawns.place_enemies` so that every spot asked of `outdoors` and of the fairness
test is recorded with its answer, and classes each refusal by Lot's own rects:
- off the plate;
- in a building or an Empty;
- in a shut band alone;
- on the standoff or the separation;
- an unfair opening.

**Its control:** the rerun must reproduce the job's `Enemy_N` transforms and spawn findings. It held on all three
of 9289's candidates (`spawn_filters.out.txt`).

**Corrected once, kept.** The probe's first run read -6 for "standoff or separation" on every candidate's last
enemy. After the last enemy's loop, `_findings` asks the fairness test again of every enemy placed
(`site_spawns.py:1312`), and the probe had charged those six questions to the last enemy. It now stops counting
there, and both outputs here come from the corrected probe.

**What it measured on Lot 0.121.0** (`spawn_filters.out.txt`). Every Empty row's band is kept out of enemy
placement: the ground behind the row's front line, across the plate's whole width (`site_fences.shut_bands`).
- **seed_9205.** The near-side block is a row of its own. Its band runs from y = -12.2 to the plate's north edge:
  the mission's own half of the plate, with the objective in it. The far row's band shuts y < -32.2. What is left
  is the 20 m street, open and within 45 m of the crew's path, so all six enemies were dropped. For the first
  enemy alone, 5,724 spots were tried:
  - 2,044 off the plate;
  - 1,035 in a building or an Empty;
  - 1,994 in a band alone;
  - 644 an unfair opening.
- **seed_9104.** The same band; all six enemies stood in the street (y -12.7 to -22.6).
- **seed_9003.** Two blocks make one row, and its front was judged to be its north edge. Its band covers the
  plate south of y = 3.6: the street, and the crew's whole route.

**Why that was wrong.** The fences already knew. `plan_fences` leaves a row open, unfenced, when a mission marker
stands behind it, and on all three candidates it did (`LOT_FENCE_SKIPPED`). Enemy placement kept out of the band
of a row that nothing shut. Of the 276 `lot_assemble` job logs on this disk, a row was left open in 3, and they
are these.

**Lot 0.122.0 (030901f).** `site_fences.markers_behind` is now the one question, asked by both:
- `plan_fences` asks it in place of its own copy;
- `shut_bands` leaves out any row it finds a marker behind;
- `place_enemies` passes its spawn, objective and extraction.

**After** (`spawn_filters_0122.out.txt`):
- seed_9205 places all six enemies, between b0 and b1;
- seed_9104's six stand between the buildings, found after 1 to 80 spots each, where 0.121.0 needed 133 to
  1,357;
- seed_9003 moves three of its six.

**Strip levels do not move.** The picked jobs of cold runs 9278 to 9287 were replayed on both versions
(`lot_replay.py`): 10 jobs, 420 files, 0 differ.

**Proven in the pipeline: cold run 9290** (`docs/cold_runs/cold_9290/`), 0 interventions.
- **Every candidate was graded,** all PASS 90, route completion 1.00, no guard stuck. seed_9205 stood all
  six of its enemies.
- **The fights moved with the enemies.** They now stand between the buildings, near the crew's route. The
  enemy's first shot averaged 1.93 to 2.65 s, under Laser Tag's 3 s minimum and above Lot's 1 s reaction
  contract, so every candidate's `combat_pacing` fell from 15 to 5 (`INSTANT_CONTACT`), and seed_9003 and
  seed_9104 fell from PASS 100 to 90.
  - Recorded, not tuned: enemy placement is provisional, and those are encounter categories.
- **The pick** was a three-way tie, so the lowest seed: seed_9003 (Level Factory 0.202.0, roadmap 245).

**What it does not settle.**
- **The band itself.** It spans the plate's whole width. That is right for a terrace whose end fences run to the
  plate's edge, and wrong for a row that is not one. Today it never reaches one: a near-side row's band holds the
  objective or the street, so the row is left open.
- **A near-side row with no mission point behind it** would be fenced, and its end runs would close the
  passages Level Factory keeps beside each building. Not seen; not built for.
- **Where an urban street's enemies should stand** is the gameplay layer's to decide; Lot's placement is
  provisional.

## The spent deal: Level Factory 0.203.0

**The defect.** `empties.infill` deals the near side's blocks as the far side deals them: every design once,
then a new bag. A room stayed open whenever what was left in the bag was too wide for it, even though the next
bag held a design that fits. Cold run 9289's seed_9104 kept a 6.70 m room that its 6.6 m block fits, because
that block had been dealt already.

**Its size.** On the test street of `level_factory/tests/unit/test_near_side_fresh_deal.py` (rooms of 42, 22
and 32 m; designs of 15, 24 and 6.6 m; forty seeds), 0.202.0 left 58 of the 120 rooms with a design's width or
more standing empty, some of them whole.

**Level Factory 0.203.0 (c132c30).** Where nothing left in the bag fits the room and some design does, a fresh
deal goes behind the remainder, which still shows first where it fits. A remainder no design fits asks nothing
of the stream.

**On urban_row_001** (`near_blocks.py`, `near_room.py`, cold runs 9289 to 9291):

    seed_9003   2 blocks in 9289, 9290, 9291: the 12.67 m room holds the 12.30 m block, the 11.35 m room a 6.6 m one
    seed_9104   1 -> 2: the 7.33 m room and now the 6.70 m room between b1 and b2, a 6.6 m block in each
    seed_9205   1 -> 2: the same two rooms, the same two blocks

**Cold run 9291** (`docs/cold_runs/cold_9291/`, 0 interventions): every near-side room on the three candidates now holds a block, each left with less than 6.6 m. The pick went to the higher grade, seed_9104 at PASS 100. Its new block covers the spot where one
enemy stood, and that enemy now stands 5 m away; the first enemy shot came at 6.62 s, not 1.93, and crew
deaths fell from 31 to 8. One residue is
by the deal, not a defect: seed_9003's 11.35 m room took the 6.6 m block where the 10.30 m one would have left
0.05 m, so 4.75 m stays open.

## Heights by cause: Level Factory 0.204.0

**The rule.** The comps (`docs/reference/URBAN_MIDRISE_COMPS.md`) say "the tallest stand furthest away", the
skyline stepping up with distance. The roadmap wrote it down: heights by cause, taller away from the action,
never by jitter.

**The defect.** Until 0.204.0 the wall's heights fell where the deal put them. 9291's seed_9104 stood 16.5,
22.7, 16.5, 32.5, 26.2, 19.6, 13.2, 38.7, 19.8 and 26.2 m from west to east.

**Level Factory 0.204.0 (065ab60).** On an urban wall each block is the one on the bag whose height is nearest
the height a block standing there is drawn toward. That target is the shortest design's height across from the
action's centre, rising with distance to the tallest's at the plate's farther end.
- **The action's centre** is the middle of the span the spawn, objective and extraction buildings cover.
- **The heights** are read off the shells' collider hulls (`street_line.shell_top`: 13.2 m at four storeys to
  38.7 m at twelve).
- **Every design is still dealt once a bag.**

**Measured** (`wall_heights.py`, `wall_heights.out.txt`): the rank correlation of a block's distance from the
action's centre with its top.

    seed     action's centre    9291 (dealt)    9292 (by cause)
    9003     x -28.5            +0.40           +0.93
    9104     x  -2.5            -0.05           +0.92
    9205     x -27.0            +0.03           +0.91

On the test street of 120 walls: median +0.03 dealt, +0.82 by cause (`patches/lf_heights_by_cause/measure_rho.py`).

**Cold run 9292** (0 interventions, seed_9104 named against 9291's). The grades and the findings are as 9291's.

**Seen** (`ab_9292/skyline_sheet.png`). The standard sheet's elevations crop the wall, so the wall's skyline was
shot from behind the near side and from the street, tilted up. It is low across from the action and rises to
both ends.

**Priced** (`ab_9292/price/price.txt`, 53 headings): draws -7.6 a heading on the mean, p95 +0.04 ms against a
0.04 ms floor, memory identical. It is the same ten blocks, reordered.

## Street trees: Lot 0.123.0 and Level Factory 0.205.0

**The gap.** The comps show street trees in pits along both sidewalks. Lot already planted them in grates on both
sidewalks, but halfway between lamps 25 m apart, a Delco strip's spacing.

**Read at source** (`docs/reference/STREET_TREES.md`): Philadelphia's siting guidelines (PHS / TreeVitalize,
2010) say 15 to 30 ft between trees and 30 ft from a corner.

**What shipped:**
- **Lot 0.123.0 (4e4859f)** plants an urban street's sidewalks every 30 ft (9.144 m), each block's row centred
  between corners kept 30 ft clear.
- **Level Factory 0.205.0 (e13306a)** tells Lot the street is urban (`streetscape` in the site spec).
- **A strip plants as before:** the picked jobs of cold runs 9278 to 9287 replayed, 0 of 420 files moved.

**Cold run 9294** (seed_9104 named against 9292's; `street_counts.py`, `street_counts.out.txt`):
- **Trees 19 -> 46.** On the through road, one kerb went from 5 to 14 trees: the gaps are 9.14 m, 30 m across
  a side street's corner, and 7.14 and 11.14 m where one tree stepped 2 m off its station (t 126.79 to
  124.80). `_nudged` steps a tree for a piece already standing, a marker or a shop band; which one stood
  here is not traced. A station within 0.8 m of a cut is not stepped but dropped (CORRECTED: this said a cut
  steps a tree too). The other kerb went from 6 to 18, every gap 9.14 m.
- **Poles 12, hydrants 2, bus shelters 3 and meters 47,** as before.
- **The bus stop's kit moved with the row:** news racks 6 -> 4, payphones 2 -> 3. The stop's mailbox, racks and
  payphone are laid out after the trees (`site_furniture.py:939` before `:1051`), each piece stepped up to 4 m
  along the band past anything standing, and not placed where no step is free. So a new row can drop one
  stop's rack and free another's payphone; which tree did which is not traced.
- **The poles moved with the trees:** 4 of the 12 stand 1 or 2 m off 9292's stations (road 0, kerb R: 37.2 ->
  38.2, 70.4 -> 69.4, 133.8 -> 132.8; road 2, kerb R: 27.86 -> 29.86), `POLE_STEPS`' first steps. The pole
  line is planned after the trees, and `site_poles._room` keeps a pole out of a tree's crown. The wires hang
  from the poles.

**The fights moved; no spawn did** (`fight_fields.py`, `fight_fields.out.txt`, 9292 against 9294):
- **The spawns stood still.** On all three candidates every enemy and crew spawn stands at 9292's transform, and
  Laser Tag evaluated each under the same seed.
- **Laser Tag 0.31.0 -> 0.32.0 cannot account for it.** It changes only a route point whose path stops short,
  and says so with `RoutePointUnreachable`. That event goes through the same `_log_event` as RouteProgress,
  which shows 208 to 225 times a report; RoutePointUnreachable shows 0 times in 9294's 75 runs.
- **Shots blocked rose on all three**, 202 -> 267, 409 -> 501 and 211 -> 347. Crew deaths went 5 -> 0, 8 -> 13
  and 1 -> 17. seed_9003 lost nobody, and Laser Tag held it below PASS on that alone (TRIVIAL_ENCOUNTER, 90 ->
  89). The pick shows that verdict and does not count it; seed_9104 held at PASS 100. Recorded, not tuned.

**Seen** (`ab_9294/ab_sheet.png`, 9292 left, 9294 right).
- **Down the street and from the spawn,** the far sidewalk reads as a planted row running into the distance,
  where 9292 stood two or three trees.
- **Two looks for the walker:**
  - **The crown from below.** From the spawn, a tree stands just ahead of the camera, and its crown, seen from
    under it against the sky, reads as angular dark boards.
  - **A warm square** at that tree's foot, its grate catching a light. Neither is traced.

**Priced** (`ab_9294/price/price.txt`; 53 headings at 14 stations, the same in both, control-subject-control):
- **Draws +28.6 a heading on the mean**, against the controls' 0.0: 39 headings up (at most +138), 9 down (as
  far as -160), 5 the same.
- **p95 +0.02 ms at the median**, against a 0.10 ms floor.
- **Memory identical:** textures 78.9, buffers 68.4, video 147.2 against 147.3 MiB.
- **The scene's light census moved:**
  - lights 237 -> 238;
  - live-light pairs 1,818 -> 1,675, and meshes with no live light 1,992 -> 2,178;
  - `site_wires_c502_499`, over the 8-light cap at 49 lights, no longer over it.

  Of the 9 headings that drew fewer, 6 look at yaw 0. At the four largest, object counts fell with the draws:
  extraction_16 -160 draws and -111 objects, camera_socket_0 -137 and -135, patrol_point_13 -126 and -77 at
  yaw 0 and -80 and -80 at yaw 90. Whether the census's move accounts for them, and which pairs went where, is
  not traced.
