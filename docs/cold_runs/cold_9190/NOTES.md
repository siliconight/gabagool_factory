# Cold run 9190 -- 0 interventions; the deli case stands in a level

The measurement run for three releases, on 9189's brief (restaurant_row_001):
- **Deli Counter 0.199.0:** layout_lint L25 names every piece through a wall.
  `presets.make` and `migrate_wall_crossing` trim the ones through: every
  deli's case now stops at its partition, x -14.0..-8.185 where it ran to
  -7.0, 0.825 m out into the market aisles.
- **Zoo 1.81.0:** the `deli_case` species. Curved glass, a lit deck of salads,
  cards and parsley, whole logs cut to the glass.
- **Deli Counter 0.200.0:** routes `deli_case_cover` to it.

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.**
- **Findings: 64, the same as 9189.**
- **The draw is 9189's.** Three distinct candidates, seed_9104 picked again
  on the walk test and Laser Tag's route findings.
- **Bake:** 4,310 users (9189: 4,308), 91 s.

## The deli case, in the level

Read in the `presentation_compose` job's composed deli_a01
(`out/presentation/lot/deli_a01/site.tscn`):
- `deli_case_cover` instances `prop_deli_case_delco_1997_03_w582_d110_h130_mglass`.
  That is the species, not 9189's `prop_delco_1997_03_w700_d110_h130_mglass`
  box.
- Its node stands at x -11.0925, the trimmed case.
- `art.log` carries no `ZOO_PARTIAL_BUILD` at all.

**Frames** (`tools/look_shots.py` on this run's walk copy,
`_runs/walk_export_restaurant_row_001`). Its deli_a01 scene is
byte-identical to this run's export. The stations are given, in the site's
frame: deli_a01 stands at (-58, 0, -1.01), unturned, so the case's centre is
at (-69.09, 0.65, 0.19), facing +Z onto the customer floor.

| frame | station (eye -> target) | mean luminance (/255) |
|---|---|---|
| `frame_9190_case_front.jpg` | (-69.09, 1.6, 3.6) -> (-69.09, 0.85, 0.19) | 7.6 |
| `frame_9190_case_three_quarter.jpg` | (-74.0, 1.6, 3.2) -> (-68.5, 0.85, 0.19) | 7.5 |
| `frame_9190_case_deck.jpg` | (-68.0, 1.5, 1.9) -> (-68.6, 0.85, 0.3) | 17.5 |

**What they show.**
- The deck glows under the level's night lighting. On it: the logs with
  their cut faces (genoa's flecks, provolone, ham, swiss's holes, the
  American block), the salad pans, the price cards and the parsley, through
  glass that renders clear. Cycles' preview had shown it milky.
- The enamel base is black at night.
- **Seen, not caused by this run:**
  - furnish's `atm_store` stands in the customer floor directly in front of
    the case (the front frame is half ATM);
  - two `poster_wall_store` boards ("LOTTO HERE", "OPEN 24 HRS") stand in
    the line from the west.
  - Each blocks the service front a customer orders at.

## Laser Tag

Every event count is identical to 9189's, on all three candidates. That is
10 to 12 event types each, counted by the report's own `event` field.
- seed_9104's PlayerStuck is 9 -> 9.
- Its grades and scores are 9189's: PASS_WITH_TUNING 79, 79; WARN 68.

The 1.2 m of case the trim removed changed nothing the report counts.

**Refuted, kept:** a first count keyed the events by a guessed `type` field,
found none, and would have read every candidate as unchanged for the wrong
reason. One real event read first gave `event`.

## The price

`price_case.sh` measured on this run's package:
- **the control:** the shipped package, twice;
- **the change:** a copy standing 9189's box in the case's place
  (`case_box_variant.py`), scaled to the trimmed slot.

Results: `price_case.txt`, read by `docs/cold_runs/cold_9185/compare_prices.py`.
The box is the CHANGE column there, so each "chg - mean(a,b)" is the case's
cost with its sign turned over.

**Over 14 stations:**
- **Draws:** the case costs **+1.0 draw a station** (+0.5 to +1.25).
- **Mesh instances:** 4,368 against the box's 4,366. Its three submissions
  are two more than the box's one.
- **Median frame time:** +0.017 ms. The control's own spread is 0.084 ms
  mean and 0.262 ms max, so it is **under the noise floor**.
- **The largest single station** is `longest_sightline`: +0.22 ms against
  its own 0.11 ms control spread, and inside the run's max spread.

**`cold_worst_ms`** read 180.5 on the box against 55.6 and 56.5 on the
controls. It is not read as a result: in 9185 the same field read 330.9 and
59.9 on two identical controls. It is the first frames' worst, and here it
belongs to the copy that imported a module the others never had.

**Priced: within noise.** That is a deli or two a level, with three
submissions each where the box was one.

## Open, after this run

1. The ATM and the lottery boards standing in front of the case's service
   front. That is furnish's placement in the customer floor, and it is a
   rule to write: keep a service case's front clear.
2. The enamel base reads black at night. Whether the case should light its
   own base (a kick light) is the walker's to judge from the frames.
3. Deli Counter 0.201.0, the deli's window: its first cold run.
