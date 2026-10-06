# Cold run 9173 -- 0 interventions; county_hospital_001 exports on Level Factory 0.144.2

Breadth sweep, cold run 9171 again. The same brief (staged from 9171), on
Level Factory 0.144.2: the site spec is written again at dispatch, once the
Deli Counter job has built the shell it measures. Seed picked by the driver.

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.** 9171's
functional-regression refusal is gone.

**The fix, checked on the run's own records.**
- **Each candidate's `site.site.gameplay.json` has ONE version.** All three
  were written during the shell leg (01:19 to 01:20) and none after the
  lock. 9171 had two each, the selected one rewritten two seconds after its
  lock.
- **The shell leg now builds the measured site.** seed_9208's file is
  byte-identical to the one 9171 reached only after its lock
  (`sha256:b1761575...`), and seed_9006's matches 9171's second version too
  (`5e1223991eae...`). Measured sites are the same bytes run to run.
- **The shipped site** (seed_9006): plate 87 x 71 m (+-43.5, +-35.5), b0 at
  (-3, 0).

**The picker chose seed_9006, not 9171's seed_9208.** The candidates now
assemble on their measured plates, so their walktest and Laser Tag findings
changed with them. That is the point: the site that is judged is the site
that ships.

**Other figures.**
- **No Empties:** no lot library, as expected.
- **The bake, by default:** 114 models and 790 primitive meshes lightmapped,
  3 kept dynamic; 42 steady rigs baked, 23 failing left live; 1,634 users,
  41.6 s in the editor.
- **Shell:** 3 candidates, all distinct; 0 blockers of 43 findings.
- **Art:** 0 blockers of 57 findings.
- **Occluders:** 308 of 318 solid modules.
- **Time:** 43 minutes, 01:19 to 02:02 (9171 took 77).
