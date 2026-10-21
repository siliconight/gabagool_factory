# Cold run 9368 -- 0 interventions; restaurant_row_001, seed 9003: the control, Deli Counter 0.245.0 from a clone

**What it was for.** The control for Deli Counter 0.246.0 (a room counts only what stands on its own storey) and
0.247.0 (a corner store's selling floor stands its aisle gondolas in rows), the factory's roadmap 148: cold run 9350's
level -- restaurant_row_001 at seed 9003, which draws deli_a03, pharmacy_a01 and the office, the rooms the look
review of 2026-10-19 framed -- on today's tools with Deli Counter as it was before both. Cold run 9367 was this run
once already and stopped at its shell leg (its NOTES).

**Not a shipped run, said so.** Deli Counter was read from a clone at 0.245.0 (147111ee), its library built there
(`build.py --all`, 159 specs, 0 tracebacks) and nav-gated (`nav_gate.py --all`, 157 shells passed, as the commit hook
gates the shipped library), named by the workspace's `tools.local.json`, written before the driver's `init` keeps it.
`before.json` hashes the REAL repos, so it says Deli Counter 0.247.0; the doctor's line is what this workspace read:
`tool:deli_counter vDeli Counter 0.245.0 @ 147111ee`. Every other tool as shipped: Zoo 1.120.1, Level Factory
0.228.0, Lot 0.126.0, Lux 0.79.0, Dispatch 0.5.3, Patina 0.32.0, Laser Tag 0.32.0, Pipeline 0.6.0, Pixelcoat 0.62.0.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0, retries 0); 8.4 min (06:24:06 to 06:32:32).
Shell 0 blockers of 79 findings; art 108 findings, cold run 9350's count on Deli Counter 0.238.0. The export's bake:
154 models lightmapped, 2,907 users.

**What it is for next.** Cold run 9369 is this level on the shipped Deli Counter 0.247.0; the price runs this package
twice as its control (`docs/findings/denser_rooms_148/`).
