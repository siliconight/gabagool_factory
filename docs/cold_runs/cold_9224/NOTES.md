# Cold run 9224 -- 0 interventions, 0 retries; the glow and the fence at the plate's edge, seen and priced

restaurant_row_001, evening and clear, seed auto, staged from 9223's batch
and brief. It proves roadmap 228's steps A and B together: Lux 0.73.0's
horizon glow and Lot 0.107.0's fence at the plate's edge with the wall
behind it unseen. Level Factory 0.173.0's doctor row (roadmap 227) ran too.

Tool versions hashed at `--begin` (`_runs/cold/cold_9224/before.json`):

| tool | version |
|---|---|
| Deli Counter | 0.205.0 |
| Dispatch | 0.5.2 |
| Laser Tag | 0.25.0 |
| Level Factory | 0.173.0 |
| Lot | 0.107.0 |
| Lux | 0.73.0 |
| Patina | 0.30.0 |
| Pipeline | 0.6.0 |
| Pixelcoat | 0.62.0 |
| Zoo | 1.94.0 |

Against 9223: Level Factory 0.172.0 to 0.173.0, Lot 0.106.0 to 0.107.0, Lux
0.72.0 to 0.73.0.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0), **retries 0.**
- **Picked: seed_9104,** on the same three lines as 9222 and 9223.
- **The shell leg:** 0 blockers of 52. **The art leg:** 0 blockers of 74.
- **Findings 74 to 74.**
- **The bake:** 481 models and 1,420 primitive meshes lightmapped (9223:
  479 and 1,478; the wall's tiles are gone), 4,242 users (4,259), 104.0 s.

## The fence at the edge (step B, Lot 0.107.0)

- **What Lot said** (`themed_site_assemble/1/job.log`):
  `LOT_PERIMETER_FENCED: 6 run(s), 589.7 m of chain-link 0.25 m inside the
  wall, which keeps its collision and shows nothing`. The runs: two of
  97.75 m on the south and north edges, one of 99.37 m on the west and
  east (`site.site.drawn.json`, `perimeter.fenced_runs` 6).
- **The wall's tiles are gone from the scene:** `site.tscn` names `perim_`
  16 times (the four bodies and their shapes) against 324 in 9223's.
- The row fences and the band's lamp stand as 9223 stood them.

## Seen: the edge before and after

`edge_frames.sh` shot 9223's package and 9224's at the same stations,
through each package's entry scene (`edge_before_after.png`; the sky band
over every camera in `sky_band.txt`):
- **Down the main road to either end and up the side road,** 9223 ends at
  a pale band, the moonlit wall, the brightest thing at the end of the
  street. 9224 ends at the chain-link, the dusk sky behind it; the glow
  band sits low over the horizon at this hour.
- **From the elevated camera over the north edge,** the fence's posts and
  fabric stand where the wall's band stood, and the dusk glow lies across
  the sky above the roofline: the band's luma 74 to 100, its warmth -67
  to -28 (`elev_S` the same).
- **Where the edge is not in view** (the facade on road 0, the objective,
  the spawn) nothing moves.
- **Not changed and worth a look:** at evening the glow is Blue Hour's
  (`horizon_glow_energy` 0.6, 14 degrees), fainter than Delco Night's; the
  road ends at the fence rather than at a gate, as roadmap 228 decided.

## Priced: the glow and the fence together

`docs/findings/horizon_glow/price_glow.py` on copies of the two packages,
9223's as the control, at Level Factory's fixed stations (`price/`):

| run | draws, +mean a heading | p95 frame, +median | p95 frame, +worst |
|---|---|---|---|
| control 1 (9223) | 0.0 | +0.29 ms | +1.74 ms |
| **9224** | **-3.7** | **-0.74 ms** | **+1.46 ms** |
| control 2 (9223) | 0.0 | -0.29 ms | +0.46 ms |

- **Draws: -5 a heading median,** -28 at `camera_socket_0` where the
  wall's tiles were most of the view, +17 at `extraction_15` facing 270
  where the fence's runs are; 28 headings fewer, 25 more, none the same.
  The two controls agree to the draw.
- **Frame time: inside the noise.** The controls' own spread is a median
  0.80 ms a heading (their medians 7.72 and 6.54 ms: the first run of the
  three is the slowest, as the glow's price found too), and 9224 sits at
  -0.74 ms against their mean, p90 +0.05, worst +1.46.
- This level is heavier than club_block_014's, where the glow alone was
  priced: about 2,900 draws a heading against 1,150.

## Roadmap

228's steps A and B are proven. C (Zoo 1.95.0), D (Lot 0.108.0) and E
(Level Factory 0.174.0) were drafted and tested on copies while this ran,
and land after it; cold run 9225 proves them.
