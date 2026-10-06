# Cold run 9175 -- 0 interventions; restaurant_row_001, the no-library path on 0.144.2

Breadth sweep, run 8 of 10. restaurant_row_001's brief as last run cold
(9003, September), on Level Factory 0.144.2, with the seed picked by the
driver (seed_9104).
- **The brief:** a strip site with three buildings and no lot library, so
  each candidate places three copies of one generated `shell.glb` and the
  Empties do not apply. No `crew_size`, so it ran at today's 4.

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.** This is the
second no-library mission through on 0.144.2, after 9173. Before that fix,
this path's site was re-assembled after the lock and refused at export (cold
run 9171).

**The bake, from the default:** 179 models and 1,226 primitive meshes
lightmapped, 6 kept dynamic; 205 steady rigs baked, 19 failing left live;
4,871 users, 65.6 s in the editor. That is the most steady rigs of any
mission in the sweep: three copies of one shell carry three copies of its
lights.

**Other figures.**
- **Shell:** 3 candidates, all distinct; 0 blockers of 60 findings.
- **Art:** 0 blockers of 80 findings, the most of any mission so far.
- **Surface dressing:** 2,925 instances of 4 meshes in 4 draw calls.
- **Occluders:** 873 of 909 solid modules.
- **Time:** about 19 minutes, 02:31 to 02:50.

**Not checked yet:** frames and frame time, after the sweep.
