# Cold run 9183 -- 0 interventions; gas_block_001 with a band that names a shop, and the fence at the playable edge

The proof run for:
- Level Factory 0.147.0: a band names a shop.
- Zoo 1.76.0: a retail strip is not a strip club.
- The fence's first level: Zoo 1.77.0's `chain_link_fence`, stood by Lot
  0.97.0's `site_fences`, wearing the `chain_link` fabric Pixelcoat 0.59.0
  lists.

It is 9182's brief and seeds, and the driver picked seed_9181 again, so the
two runs compare one candidate. That candidate stands
`airport_terminal_a02`, `funeral_home_a03`, `gas_station_a02` and 32
Empties (e0 to e31).

**Every leg ran, `INTERVENTIONS: 0`, and the package exported.** No tool
file changed during the run: the candidates' specs came out byte-identical
to 9182's.

**Against 9182, the same candidate:**

| | 9182 | 9183 |
|---|---|---|
| draws | airport, funeral home, gas_station_a02 | the same |
| shell findings | 0 blockers of 39 | 0 blockers of 39 |
| art findings | 0 blockers of 57 | 0 blockers of 57 (the driver's diff: 57 -> 57) |
| bands | `flappahs`, `delco_storage` (airport), `keystone_savings` (funeral home) | `flappahs` only |
| fences | none | 7 |
| bake | 4,280 users, 86.7 s | 4,312 users, 95.3 s |

**The fences** (`site.tscn`, `cover_198` to `cover_204`):
- five 3.0 m alleys in the 32-house terrace, between e5/e6, e10/e11,
  e15/e16, e21/e22 and e27/e28;
- the row's two ends, 13.0 m and 16.8 m, out to the plate;
- all along the front line at Lot y -42.11, three modules
  (`prop_chain_link_fence_delco_1997_01_w300/w1300/w1680_d6_h183`), wearing
  `chain_link_galvanized`.

**Seen** (`tools/look_shots.py` on the walk copy, given stations at a
standing eye height of 1.6 m):
- **Seven metres out from the alley between e10 and e11, it reads as an
  alley gate.** The fabric spans from the brick house's corner to the sided
  house's, the posts are at each side, and the top rail is level with the
  door heads.
- **Along the 16.8 m end run, the near half reads and the far half loses its
  fabric.** The posts and rail stand against the bright perimeter wall with
  nothing between them.
  - This is alpha-test thinning. The fabric is about 25 % wire, so its
    smaller mips average under the 0.5 cutoff and are cut away.
  - Item 188 records it. The fix wants coverage-preserving mips, a lower
    cutoff for this kind, or a distant card. Each has a cost, and which to
    take is a look-and-price call.
- **The station 7 m out from the alley between e5 and e6 stood over a
  parked car,** whose roof filled the frame. The station was wrong; the fence
  was not.

**Priced** (`_runs/perf_inner`, 14 fixed stations, GL Compatibility).
9182's package ran twice as the control and 9183's once, interleaved
(`fence_9182_a`, `fence_9183_a`, `fence_9182_b`).
- **Draws:** +3.8 a station against the control's mean. The most was +14 at
  `longest_sightline`, the station that sees the most fence. The control's
  two runs drew identically.
- **Median frame:** +0.020 ms against the control's mean. The control's own
  spread was 0.124 ms on average and 0.309 ms at most, so this is under the
  instrument's floor.
  - Only `longest_sightline` moved beyond its spread: +0.39 ms against
    0.29, at 10.52 ms median and 11.11 ms p95.
- **Scene:** +32 mesh instances and +51 nodes, all attributed by diffing
  the two packages' scenes:
  - +7 `cover` instances: the fences, two meshes each;
  - -2 bands, each a `sign_b`, a `face` and a `mesh`;
  - +22 ground tiles (`mesh_t`): +5 each under `Ground` and `Ground_15`,
    +1 each under `perim_N` and `perim_S`, and the rest elsewhere.
- **Why the ground tiles.** Lot's ground tiling splits a tile at the edge of
  every standing piece, and a 6 cm fence is now one.
  - The plate is the same 246 x 118 m in both runs, so the plate did not
    grow.
  - A fence stands on the ground and needs no cut in it, so this is a cheap
    Lot follow-up, not a defect in the fence.
