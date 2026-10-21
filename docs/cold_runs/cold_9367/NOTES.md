# Cold run 9367 -- STOPPED at its shell leg; restaurant_row_001, seed 9003: a control with no navgate manifests

**What it was for.** The control for Deli Counter 0.246.0 (a room counts only what stands on its own storey) and
0.247.0 (a corner store's selling floor stands its aisle gondolas in rows), the factory's roadmap 148: cold run 9350's
level -- restaurant_row_001 at seed 9003, which draws deli_a03, the office and pharmacy_a01, the rooms the look review
of 2026-10-19 framed -- on today's tools, with Deli Counter read from a clone at 0.245.0 (147111ee) whose whole library
was built there (`build.py --all`, 159 specs, 0 tracebacks). The clone reaches the run through the workspace's
`tools.local.json`, written before the driver's `init`, which keeps one already there.

**Not a shipped run, said so.** The real repo stays at 0.247.0 and `before.json` hashes the real repos, so it names
Deli Counter 0.247.0 (e1cbd7e1) -- which is NOT what this workspace read. The doctor's line is the evidence:
`tool:deli_counter vDeli Counter 0.245.0 @ 147111ee`. Lot reads one file from the real sibling repo,
`agent_contract.json`, identical in both versions.

**Stopped at the shell leg; INTERVENTIONS: 0** (journal 0, unattributed files 0, retries 0). The zero says nothing
was touched, not that the run worked. `level_factory run` refused before writing a job; reproduced in a scratch
workspace with the same `tools.local.json`: "a themed lot of 3 needs 3 fit families and the library offers 0: (none).
127 of 127 indexed shell(s) are unfit -- 127 with absent". `building_library` judges a shell fit from its
`<id>.navgate.json` (`THEMED_FIT_INPUTS`); Deli Counter's nav gate writes those, its commit hook runs the gate over the
shipped library, and nothing ran it over the clone. The control's setup's defect, not the pipeline's: cold run 9368 is
this control again, after `nav_gate.py --all` over the clone.
