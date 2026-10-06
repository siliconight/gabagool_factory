# Cold run 9177 -- 0 interventions; gas_stop_001, the last of the breadth sweep

Breadth sweep, run 10 of 10. gas_stop_001's brief as last run cold (9011,
September), on Level Factory 0.144.2, with the seed picked by the driver
(seed_9011).
- **The brief:** a strip site with three buildings and a lot library, so it
  gains the Empties by default.

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.**

**From the defaults alone:**
- **The terrace:** each candidate stood three real buildings, one of them a
  gas station, and the 12 Empties:
  - seed_9011: cr_garage, gas_station_a03, self_storage_a01;
  - seed_9112: funeral_home_a01, gas_station_a02, pharmacy_a02;
  - seed_9213: gas_station_a03, marina_a02, parking_garage.
- **The merge,** identical to every library mission's in the sweep:

      [export] Empties merged: 12 scene(s), 1061 mesh(es) of 1660 surface(s) -> 236 merged mesh(es), 962 collider(s) kept

- **The bake:** 363 models and 1,452 primitive meshes lightmapped, 6 kept
  dynamic; 70 steady rigs baked, 17 failing left live; 2,896 users, 75.5 s
  in the editor.

**Other figures.**
- **Shell:** 3 candidates, all distinct; 0 blockers of 37 findings.
- **Art:** 0 blockers of 55 findings.
- **Surface dressing:** 3,542 instances of 4 meshes in 4 draw calls.
- **Occluders:** 1,278 of 1,282 solid modules.

With this run, all ten missions of the sweep have built cold and exported at
0 interventions. The sweep's own record is
`docs/findings/breadth_sweep_2026-10-06/`.
