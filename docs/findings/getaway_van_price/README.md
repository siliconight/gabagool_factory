# The getaway van's price (roadmap 206)

**Question.** What does the crew's getaway van cost a frame, in the level
it stands in?
- **What it is.** Zoo 1.85.0's `step_van`: one prop a level, five
  submissions, 13,792 triangles at its default size.
- **Where it stands.** Lot 0.98.0 parks it at the spawn building's kerb.
- **The rule that asks.** CLAUDE.md, "every frame is spent on somebody else's
  machine": price a look on/off, at several stations, with a no-change
  control.

**Method** -- the parking fields' (cold run 9141, `docs/cold_runs/cold_9141/NOTES.md`):
- **On:** cold run 9198's exported package, as built.
- **Off:** a copy with the van's node stripped by `strip_van.py`, from every
  scene that carries it. The first fields price stripped `site.tscn` only
  and was void: the package loads Lux's re-save of the site, which keeps its
  own copy of every node.
- **Control:** the "on" package run again. Its spread is the noise this
  harness cannot see past.
- **Harness:** Level Factory's fixed-station harness,
  `level_factory/tools/perf_stations_run.py`, GL Compatibility, windowed.
  Headless draws nothing, so it cannot measure a frame.

**Where the harness stands, and so what it can see of the van.** The
stations are not chosen here. `perf_stations.gd` takes up to 12 anchors from
the package's `gameplay_anchors.json`, round-robin across eight types, and
turns four headings at each. On 9198's package, two of the twelve stand near
the van, which is at Godot (-2.5, 17.5):
- `crew_spawn_1`, `deli_counter:A`, at (-2.0, 14.0), 3.5 m away;
- `extraction_13`, `lot:EXIT`, at (6.0, 13.0), 9.6 m away.

The van's own crew point is not a station, because the package carries no
anchor for it (roadmap 204). So the price below is the van seen from a few
metres away at some headings, and absent at most of the rest -- which is how
a player meets it too.

**Instruments here:**
- **`strip_van.py`** makes the "off" copy (`strip.log`).
- **`van_headings.py`** lists the headings whose draws moved, each with its
  frame-time difference beside the control's (`van_headings.txt`).

**Records:** the harness's reports are `van_on.json`, `van_off.json` and
`van_on2.json`, with the runner's logs beside them. The comparison is
`patches/zoo_cover_merge/price_robust.py` (`price_robust.txt`). It compares
"off" against the mean of the two "on" runs, and names any heading where
those two runs disagree by more than 1.0 ms.

## Result

**Five draws where it is seen, and about 0.04 ms of frame time there.**
Measured 2026-10-08 on cold run 9198's package (bank_block_001, seed_9054),
GL Compatibility, NVIDIA RTX 2060, 14 stations by 4 headings, two passes a
heading.

**The instrument sees the van.** The draws column moves only where the van is:
- the van is drawn at 17 of the 53 headings, where "off" draws 5 fewer (3 at
  six of them);
- it draws the same at the other 36;
- the mesh census reads 3,697 meshes on and 3,692 off.

That is the known change, so the control the rule asks for -- a difference
the instrument can see at all -- is met by the draws.

**Frame time** (`price_robust.txt`, `van_headings.txt`):

| | median frame, off minus the mean of the two "on" runs |
|---|---|
| the 17 headings that draw the van | mean -0.044 ms, -0.111 to +0.018 |
| the other 36 headings | mean -0.004 ms |
| the control, on2 minus on, all 53 | median +0.008 ms, -0.096 to +0.082 |
| the control at those 17 | mean +0.012 ms |

- **No heading's difference leaves the control's spread.** The largest is
  -0.111 ms, at `attacker_spawn_8` 270, beside an 8.6 ms frame.
- **But it is consistent.** Seventeen headings averaging -0.044 ms against
  the control's +0.012 at the same headings reads as a real cost of about
  0.04 ms where the van is in view: five submissions at the
  ~0.005 ms a draw this level runs at (9.6 ms for 1,923 draws at the worst
  view).
- **p95 is noisier,** -0.476 to +0.915 ms across all headings, and is not
  used here.
- **No heading was unstable** between the two controls by more than 1.0 ms
  in the median.

**Against the budget.** The worst view is `longest_sightline` at 90: 1,923
draws on and 1,918 off, 10.62 / 10.06 ms p95 on and 9.99 off, inside the
provisional 11.0 ms and 2,000 draws. Every station is inside budget with the
van and without it.

**What this does not cover.**
- **Other hardware.** One machine, one level. The budget is provisional
  until an exported-build measurement on a low-end GL Compatibility machine.
- **More than one van.** The van is one prop a level. A level with several
  vehicles of its build (roadmap 212's responders) would pay its 5 draws
  each, and that price belongs to whoever puts them there.
- **Lights on the van.** It has no lights; its glass and lamps are
  materials.
- **The night grade.** This level is night and rain, so the van is lit by
  the street, not the sun. That changes what the frame shows, not what it
  submits.

**Copies deleted.** Each pass ran on a full copy of the package (148 MB
here, 279 MB with its import cache). The three under `_runs/perf_inner/` and
`_runs/van_off_9198/` were deleted once their reports existed beside this
README. Price copies left behind filled the disk once and killed cold run
9163.
