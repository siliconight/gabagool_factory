# Cold run 9269 -- the street's drains, in a real drive

**What it tested:** Lot 0.120.0 in a real drive of restaurant_row_001: the street's drains (factory
roadmap 179, the walker's of 2026-10-04) -- a manhole cover at every junction and along a long run, a
storm inlet a corner in the gutter, the odd lid in the sidewalk behind one, each a floater (a 4 mm
skirt, 3 mm proud of the paint), with the art only. The rules as read in
`docs/reference/STREET_DRAINS.md`. Everything else as in 9268.

**Result: 0 interventions, 0 tool files changed.** seed_9104 picked as before. Findings 117 -> 117.
**And a defect, found by looking at the corner frame:** four of the eight grates stand over a
crosswalk bar -- fixed in Lot 0.120.1 and proven in cold run 9270.

## As built

- **The drains:** Lot printed `[lot] drains: 4 manhole cover(s), 8 inlet(s), 4 sidewalk lid(s)` in
  the themed site's job (`restaurant_row_001.themed_site_assemble/1/job.log`): a cover at each of the
  four junctions (the main road's two T's, the lane's two), none along a run (no stretch between
  junctions reaches 121.9 m), two corners an inlet at each T, a lid behind four of the inlets. The
  package carries them as 8 `site_drains_*.obj` (4 cells, the iron and the dark), 4,184 triangles.
- **The graded lots carry none**, as meant: the three `lot_assemble.candidate.*` jobs wrote no drains
  line and no drains OBJ (seed_9104's job: 38 paint OBJs, 0 drains, 0 wires; the themed job: 38, 16 and
  14 -- the paint is the control that the count looked in the right place).
- **The bake** lightmapped them: 505 models (9268: 497) and 224 primitive meshes, 3,346 users (3,338),
  the bake 29.95 s (30.09) and its editor 59.2 s (60.5) -- `light_bake.json` in each package.

## The frames (`drains.sh`, `drains.png`)

9268 left (no drains), 9269 right, the same lot (seed_9104) so the stations stand in the same place:
`corner` (the main road's north kerb at the west T's west corner: an inlet, its lid and its throat),
`junction` (the cover at that T's centre), `lane` (the side street's kerb at the lane's mouth), and
two controls with no drain in view, `up` (a facade) and `hatch` (the deli's roof).

    station    mean |d| (codes)    pixels over 8 codes   over 32
    corner     2.30 / 2.17 / 2.14   2.044 %               0.138 %
    junction   2.60 / 2.31 / 2.16   3.104 %               0.232 %
    lane       1.83 / 1.73 / 1.82   1.127 %               0.122 %
    up         2.78 / 2.45 / 2.65   2.684 %               0.260 %   (control)
    hatch      2.34 / 1.93 / 2.08   0.051 %               0.002 %   (control)

**The whole-frame numbers do not separate the drains from the noise:** `up`, a control, moved as much as
the drain stations. A map of the pixels past 32 codes does: at `corner` they gather into the grate and
the lid, at `junction` into the cover's ellipse; at `up` they lie along the facade's long edges and the
lit windows' edges, nowhere in particular. 9268's controls had moved 0.007 % and 0.41 % past 8 codes.

**Why the controls moved: the atlas repacked** (`lm_users.gd`, `lm_users.py`, `lm_users.out.txt`). First
written here as a hypothesis, then measured. Each bake's lightmap users dumped -- a node path, the
rect the atlas gave it, its slice -- and compared:

- **9268 -> 9269**, the 8 drain meshes added (3,338 -> 3,346 users): of the 3,338 users both bakes
  carry, **127 kept their rect and slice**; 567 moved to another slice and 2,644 moved within their
  slice. Every texel of nearly every mesh was baked somewhere new.
- **9269 -> 9270**, the same meshes with four grates moved (3,346 users each): **all 3,346 kept rect and
  slice**, and the controls moved 0.187 % and 0.000 % past 8 codes (`cold_9270/`).

So a change that adds or removes a lightmap user re-bakes the whole level's light in a new layout, and
a frame comparison across it carries that noise everywhere. Its controls are the only way to read
it. Paired as above, the atlas is the measured difference between the two sessions. That it is the
whole of the controls' movement is the inference; nothing else here was found to differ.

What the crops show: at `corner` a dark grate in the gutter against the kerb, the lid a dark plate on
the sidewalk behind it, litter that was already there now lying on the grate -- and the grate's road
end against a crosswalk bar's end, which the paint section below measures. At `junction` the cover is
a dark disc at the T's centre. **`lane` sees no drain:** a near object fills the frame's centre where
its two inlets are, and the map past 32 codes is empty there; the station was chosen from
coordinates, not from a frame.

## The paint (`drain_paint.py`, `drain_paint.out.txt`)

Each drain piece's footprint from the shipped OBJs (faces joined into parts, parts within 0.1 m merged,
the plan hull of the piece; its count checked against the count Lot printed), against the job's
`site.markings.json` (125 markings), plan metres:

- **4 of 8 inlets lie over a crosswalk bar**, 0.155 m^2 each, 27.8 % of the grate: all four on the main
  road's north kerb at its two T's, both corners. The lane's four are clear by 1.15 m.
- **2 of 4 covers lie on a bar**, 73 % of the frame's hull: the lane's two junctions, where the side
  street paints its crosswalk centred on the lane. Kept: the walker's photograph has a round cover out
  in a crosswalk, and the cover stands 3 mm proud of the paint.
- The 4 lids are clear, the nearest bar 0.82 m off.

RETRACTED, KEPT in the probe's docstring: its first version clustered vertices nearer than 0.3 m and
read 36 pieces against Lot's 16 -- a lid's corners are 0.46 m apart with nothing between them, so each
lid read as four pieces of no area and each inlet as two. Its overlaps were real paint under real
halves; its counts were not, and the count check now refuses a mismatch.

**Why the four** (Lot's own records, printed for this lot): road 0's north kerb drops for the side
street's carriageway and `CUT_MARGIN` each side, 59.912-71.112 m along the road, while road 0's
crosswalks at that T are painted in line with the side street's sidewalks, 57.762-60.262 and
70.762-73.262 m (`site_streets.painted_walks`). 0.120.0 stood the grate a hand past the dropped
stretch -- inside the crosswalk. The rule it quotes (TxDOT: an inlet upstream of the crosswalk) was
asked of the ramp alone. **Lot 0.120.1** steps each grate along the kerb past every marking nearer than
a hand, the lines along a road excepted; on this lot the four move 2.15 m and the rest stay.

**And a second thing the same printout shows, filed as roadmap 244:** road 0's crosswalks at a T have
almost no ramp under them. Its south kerb has no cut at all, and the north kerb's dropped stretch takes
0.35 m of each 2.5 m walk; the rest of each crosswalk lands against a raised kerb.

## The price (`price/`)

9268's package both controls, 9269's the subject (the harness names it `glow`), Level Factory's 53
station headings, GL Compatibility:

    controls' spread, median over 53 headings: p95 0.05 ms, draws 0.0 (the noise floor)
    run        draws +mean   draws +min   draws +max   p95 +median ms  p95 +max ms
    control_1          0.0            0            0             0.02         0.33
    subject            1.2            0            5             0.03         1.14
    control_2          0.0            0            0            -0.02         0.17

Draws 788 -> 789 a heading on the mean, +0 to +5 (the worst heading 2,805 -> 2,807); the p95's median
2.94 and 2.81 ms for the controls and 2.95 for the subject, +0.03 ms against a 0.05 ms floor. Eight
meshes, at most five of them drawn at any heading: the cost is the draws and nothing in the frame time
can see them.

## The time

    run    shell   art     export   walk   retire   the drive
    9268   95 s    166 s   168 s    10 s    4 s     7.7 min (462 s)
    9269   91 s    156 s   167 s    10 s    3 s     7.4 min (441 s)

## What is evidence of what

- The drains: Lot's line in `restaurant_row_001.themed_site_assemble/1/job.log`; the 8 OBJs in the
  package; the candidates' jobs for their absence.
- The look: `drains.png`, `drains.log`; the PNGs under `_scratch/frames_9269_drains/`.
- The paint: `drain_paint.py`, `drain_paint.out.txt`; the job's `site.markings.json`.
- The price: `price/`; the count: `cold_run.py --end`.
