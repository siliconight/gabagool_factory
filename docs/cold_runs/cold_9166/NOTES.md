# Cold run 9166 -- 0 interventions; the sweep's control, on the new defaults

gas_block_001, seed 9080. Level Factory 0.144.0 (the walker, 2026-10-05:
"yes to both defaults").
- **The Empties are the brief's default.** This brief already asked for
  them (`"empties": "across"`).
- **The light bake is the export's default.** This run passed no
  `EXPORT_FLAGS`, so the bake ran because of the default alone.

**The question it answers:** did 0.144.0 change a level whose brief already
had both? It did not. Every number below matches cold run 9165, which asked
for both explicitly:

| | 9165 (flag) | 9166 (default) |
|---|---|---|
| interventions | 0 | 0 |
| shell | 3 candidates, all distinct; 0 blockers of 40 findings | same |
| art | exit 1 on 55 findings, 0 blockers | same |
| Empties merged | 12 scenes; the per-scene merged counts | identical, row for row |
| light bake | 3,309 users, 75.6 s in the editor | 3,309 users, 79.0 s |

The shell leg took about 25 minutes, as before; the run took 34 in all
(20:54 to 21:28).

**What it does not answer.** gas_block_001 already asked for both, so this
proves the defaults do no harm, not that they do any good. The six
missions that gain the Empties by default are what the sweep that follows
measures (cold runs 9167 to 9175).
