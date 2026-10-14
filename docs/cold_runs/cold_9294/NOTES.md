# Cold run 9294 -- street trees: an urban street is planted as a city block is (Lot 0.123.0, Level Factory 0.205.0)

**What it tested:** urban_row_001 (9292's brief unchanged) on Lot 0.123.0 (4e4859f) and Level Factory 0.205.0
(e13306a). The compose stage writes `streetscape: "urban"` into the site spec, and Lot plants an urban street's
sidewalks every 30 ft (9.144 m), each block's row centred between corners kept 30 ft clear: Philadelphia's siting
guidelines, read at source (`docs/reference/STREET_TREES.md`). **seed_9104 named** against 9292's (roadmap 245: a
pick follows the grade, and grades move with any change near a fight). Laser Tag 0.32.0, Deli Counter 0.217.0,
Zoo 1.106.0. Staged from cold run 9293.

**Result: 0 interventions (journal 0, unattributed files 0). The street is planted at 30 ft; the pick held; every
fight moved with the furniture.**

- **The spec says urban:** the site spec each candidate's `lot_assemble` ran on
  (`.level_factory/temp/urban_row_001/candidate_<seed>/site.json`, the path in its `job.log`) carries
  `streetscape: "urban"`; 9292's carries no `streetscape`.
- **The trees** (`docs/findings/urban_street/street_counts.py`, `street_counts.out.txt`; seed_9104, 9292 -> 9294):
  - **19 -> 46** on the whole plate.
  - **The through road's kerb L, 5 -> 14.** Gaps are 9.14 m, with 30.03 m across a side street's corners.
    One pair reads 7.14 and 11.14 m, where one tree stands 2.00 m off its station. Lot's `_nudged` steps a tree
    for a piece already standing, a marker or a shop band, and drops one whose station is within 0.8 m of a cut;
    which one stepped this tree is not traced.
  - **Kerb R, 6 -> 18,** every gap 9.14 m.
- **Everything else on the street:**
  - Poles 12, hydrants 2, bus shelters 3 and meters 47, as before.
  - **The bus stop's kit moved with the row:** news racks 6 -> 4, payphones 2 -> 3. Lot lays the stop's mailbox,
    racks and payphone out after the trees (`site_furniture.py:939` before `:1051`). Each steps up to 4 m along
    the band past anything standing, and is not placed where no step is free. So a new row can drop one stop's
    rack and free another's payphone; which tree did which is not traced.
  - **The poles stepped round the crowns:** 4 of the 12 stand 1 or 2 m off 9292's stations, `POLE_STEPS`' first
    steps. The pole line is planned after the trees, and `site_poles._room` keeps a pole out of a tree's crown.
- **The pick held: seed_9104 at PASS 100.**

      seed 9003: 0 major (not counted: LOT_DESTINATION_ABOVE_FLOOR, LT_MAP_TRIVIAL_ENCOUNTER), route completion 1.00, grade PASS_WITH_TUNING 89
      seed 9104: 0 major, route completion 1.00, grade PASS 100
      seed 9205: 0 major (not counted: LOT_DESTINATION_ABOVE_FLOOR), route completion 1.00, grade PASS 90

- **Every fight moved; no spawn did** (`docs/findings/urban_street/fight_fields.py`, `fight_fields.out.txt`).
  - **The spawns stood still:** on all three candidates, every enemy and crew spawn stands at 9292's transform,
    and Laser Tag evaluated each under the same seed.
  - **Laser Tag's version change cannot account for it.** 0.31.0 -> 0.32.0 changes only a route point whose
    path stops short. Such a point is logged as RoutePointUnreachable, through the same `_log_event` that carries
    208-225 RouteProgress events a report. It is logged 0 times in 9294's 75 runs. On sixteen lots, 0.32.0 read
    0.31.0 exactly in every field (`docs/findings/lt_arrival/`).
  - **What moved was the street.** Shots blocked rose on all three:

      seed     shots blocked    crew deaths    first enemy shot (mean)    grade
      9003     202 -> 267        5 -> 0        1.96 -> 2.69 s             PASS 90 -> PASS_WITH_TUNING 89
      9104     409 -> 501        8 -> 13       6.57 -> 4.06 s             PASS 100 -> PASS 100
      9205     211 -> 347        1 -> 17       2.65 -> 2.22 s             PASS 90 -> PASS 90

  - **seed_9003's crew lost nobody** in 25 runs. Laser Tag held its score below PASS on that alone
    (TRIVIAL_ENCOUNTER, "89, from 90"), a verdict the pick shows and does not count (Level Factory 0.202.0).
    Recorded, not tuned.
- **Findings: 109,** two fewer than 9292's 111. The driver's delta reads "0 -> 109" because the workspace it
  compares against (9293) ran restaurant_row_001.

## The time

    run    shell   art     export   walk   retire   the drive
    9292   108 s   180 s   197 s    11 s    3 s     8.6 min (514 s)
    9294   114 s   192 s   220 s    12 s   19 s     9.6 min (576 s)

- **The export is 23 s longer.** The light bake read 91.9 s in the editor against 76.4 s, over 3,143 users
  against 3,119.
- **The retire is 16 s longer.** It removed 1.2 GB (one item) where 9292's removed nothing.

## Seen and priced against 9292

**Seen** (`docs/findings/urban_street/ab_9294/ab_sheet.png`, 9292 left, 9294 right; `ab_record.sh`'s two edge
stations, the spawn, the objective and four elevations). Down the street and from the spawn, the far sidewalk
reads as a planted row running into the distance, where 9292 stood two or three trees. Two looks for the walker,
neither traced: from the spawn, the tree just ahead of the camera shows its crown from below against the sky as
angular dark boards; and its grate shows as a warm square.

**Priced** (`ab_9294/price/price.txt`; 53 headings at 14 stations, the same in both, control-subject-control):
- draws +28.6 a heading on the mean, against the controls' 0.0: 39 headings up (at most +138), 9 down (as far
  as -160), 5 the same;
- p95 +0.02 ms at the median, against a 0.10 ms floor;
- memory identical: textures 78.9, buffers 68.4, video 147.2 against 147.3 MiB;
- the scene's light census moved: lights 237 -> 238, live-light pairs 1,818 -> 1,675, and the wire mesh
  `site_wires_c502_499` no longer over the 8-light cap (49 lights in 9292). Not traced to the headings that drew
  fewer (`docs/findings/urban_street/README.md`).
