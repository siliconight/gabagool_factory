# Cold run 9195 -- STOPPED at the art leg on a defect older than the run; 0.152.0 and 0.153.0 seen working up to there

gas_block_001, 9184's brief and seeds (`seed_base` 9080). Tests Level Factory
0.152.0 on a second archetype (the score is the gas station, and the crew
spawns elsewhere) and 0.153.0 (the brief's mode and pacing window reach Lot,
and the adapter reports Lot's verdict). Tool versions hashed at `--begin`:
Level Factory 0.153.0, Lux 0.68.2, Deli Counter 0.202.0, Lot 0.97.4, Zoo
1.81.0, Laser Tag 0.23.2.

**The run produced no level.** The shell leg passed (3 candidates, all
distinct, 0 blockers of 45 findings); the art leg stopped on one blocker
(52 findings), so there was no export and no walk. `--end`:
`INTERVENTIONS: 0` (journal 0, unattributed files 0, one observation) --
nothing was touched, and nothing was shipped either.

## The blocker: gas_station_a02's cooler run, older than this run

`PRESENTATION_PLACEMENT_MISMATCH` (blocker, collision), seed_9080:

    gas_station_a02: 1 themed module(s) do not match the greybox footprint
    (visual off the collision); 166/167 aligned. Worst: cooler_run
    (prop_cooler_run_delco_1997_04_w328_d90_h220: placed [3.28, 2.2, 0.9]
    on greybox [25.442, 2.2, 0.9])

**It was already there in 9184.** 9184's compose manifest for the same
building (`.../gas_block_001.presentation_compose/1/out/presentation/lot/
gas_station_a02/portable_resource_manifest.json`) reads the identical
`placement_check`: 167 checked, 166 matched, 1 mismatched, `ok: false`, the
same cooler run at 25.442 m against a placed 3.28 m. 9184 ran Level Factory
0.147.0, which read one placed building's package of many; 0.149.0 ("Every
placed building's package is read") is what made this one visible, and no
cold run since had placed gas_station_a02 (9185 to 9194 ran other missions).

**What it is:** the greybox lays a cooler run 25.442 m long; the theme's kit
bundles two cooler-run modules, 3.28 m and 8.00 m wide; the composer placed
the 3.28 m one. Not attributed further: whether the length or the kit is
wrong is roadmap 205's question.

## Level Factory 0.152.0: the score is the gas station

| candidate | spawn | objective (`objective_from`) | extraction | route completion |
|---|---|---|---|---|
| seed_9080 (picked) | b1 rail_station_a01 | b0 gas_station_a02 (archetype) | b0 gas_station_a02 | 1.00 |
| seed_9181 | b2 funeral_home_a03 | b0 gas_station_a02 (archetype) | b0 gas_station_a02 | 1.00 |
| seed_9282 | b2 freight_terminal_a02 | b0 gas_station_a02 (archetype) | b1 casino_a02 | 0.52 |

The breadth sweep's reading of this brief at seed_9080 put the crew's spawn
in the score building; here the spawn is the rail station. Two of the three
candidates extract from the score itself -- the pattern the brief-pacing
census counted on 43 of 136 multi-building specs
(`docs/findings/brief_pacing_mode/`); its pacing leg reads
`travel b0->b0 0.0`.

**The picker read route completion** (`tools/cold_drive/pick_candidate.py`,
changed in 4760cae): seeds 9080 and 9181 tied at 0 majors and 1.00, and the
lower seed won; seed_9282 (0.52) would have lost on completion either way.

## Level Factory 0.153.0: the brief's pacing reaches Lot

From each candidate's shell-leg `site.site.gameplay.json`:

| candidate | Lot's estimate | target | status |
|---|---|---|---|
| seed_9080 | 2.8 min (1.8-3.8) | 25-35 min | likely TOO SHORT vs target |
| seed_9181 | 3.1 min (2.0-4.2) | 25-35 min | likely TOO SHORT vs target |
| seed_9282 | 3.4 min (2.2-4.6) | 25-35 min | likely TOO SHORT vs target |

- `mode: heist` on all three, and the breakdown counts travel (seed_9282:
  b2 -> b0 34.8 s, b0 -> b1 19.4 s) before setup (30 s) and objective work
  (120 s). Until 0.153.0 every level was judged against 7-15 min with no
  travel counted.
- Level Factory raised `LOT_PACING_OUTSIDE_TARGET` three times, moderate,
  non-blocking: "pacing estimate 2.8 min (1.8-3.8 min) vs target 25-35 min:
  likely TOO SHORT vs target (counted: travel, setup/positioning, objective
  work)".
- Lot's heist gate, which the mode switches on, passed in the real assembly
  of all three candidates.
- `batch create` named the brief's unbuilt fields -- shown by re-running it
  into a scratch workspace, because the driver keeps only its last line:
  `[batch] gas_block_001: recorded, not built -- nothing builds from
  route_shape, objective_hypotheses, extraction_relationship, verticality,
  landmark yet (roadmap 200)`. This brief's `objective_hypotheses` are a
  bank's ("enter_bank", "reach_vault", ...), cloned with the brief and never
  noticed, because nothing reads them.

**Not checked:** frames, frame time, the package -- none exists.
