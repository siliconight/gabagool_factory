# Cold run 9174 -- 0 interventions; card_block_001 exports on Level Factory 0.144.2

Breadth sweep, cold run 9170 again. The same brief (staged from 9170), on
Level Factory 0.144.2, which carries 0.144.1's fix: the export reads a
blocker's candidate from its own `candidate_id`. Seed picked by the driver.

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.** 9170's
refusal is gone.

**The fix, checked on the run's own records.** Everything about the level
matches 9170:
- the same three candidates, drawing the same buildings;
- the same pick, seed_9263;
- the same 50 shell and 68 art findings;
- the same one blocking finding, still recorded:

      ('LT_NOT_EVALUATED', 'card_block_001.candidate.seed_9061', location '')

The selection is `card_block_001.candidate.seed_9263`. So the export
discounted seed_9061's blocker, which belongs to a candidate nobody chose,
where 9170's refused over it. Same level, same finding, now attributed to
the right candidate.

**From the defaults:**
- **The Empties:** all 12 on every candidate:

      [export] Empties merged: 12 scene(s), 1061 mesh(es) of 1660 surface(s) -> 236 merged mesh(es), 962 collider(s) kept

- **The bake:** 429 models and 1,464 primitive meshes lightmapped, 6 kept
  dynamic; 82 steady rigs baked, 17 failing left live; 3,438 users, 81.0 s
  in the editor.

**Still open, for the walker:** seed_9061 draws `setback_demo` and seed_9162
draws `pvp_station_ref` (9170's notes).
