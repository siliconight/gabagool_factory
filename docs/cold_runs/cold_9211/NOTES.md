# Cold run 9211 -- 0 interventions; every Zoo part ships with weighted normals

club_block_014, seed auto, staged from cold run 9210. Tests **Zoo 1.87.0**
(roadmap 214, trial 1): every visual part's corner normals are weighed by
face area at export, so a bevelled part's big faces read flat instead of as a
dome. The finding is `docs/findings/weighted_normals/`.

Tool versions hashed at `--begin`: Zoo 1.87.0, Lot 0.102.0, Level Factory
0.163.0, Laser Tag 0.25.0, Deli Counter 0.203.0, Lux 0.69.0, Dispatch 0.5.2,
Patina 0.29.1, Pixelcoat 0.61.0, Pipeline 0.6.0. Only Zoo moved since 9210.

**`INTERVENTIONS: 0`** (journal 0, unattributed files 0). Every leg ran.

**Picked: seed_9181**, on the same figures as 9206 to 9210:
- 9080 at 1 major and route completion 0.92;
- 9181 at 0 majors and 0.96;
- 9282 at 1 major and 0.96.

**What held:**
- **Findings: 72 to 72,** none raised or cleared.
- **The art leg:** 0 blockers open.
- **The light bake:** the same 432 models lightmapped, 7 kept dynamic, 1
  spawned set dynamic, 3,898 users. It took 88.3 s in the editor, against
  97.4.

## The package against 9210's: normals, and what is derived from them

`docs/findings/weighted_normals/pkg_diff.py`, output `pkg_diff.txt`. The
control is 9209 against 9210 (`pkg_diff_control.txt`), two runs in which Zoo
did not change.

| | 9209 -> 9210, the control | 9210 -> 9211 |
|---|---|---|
| files, each package | 2,833 | 2,833 |
| files that differ | 115 | 504 |
| GLBs that differ | 3 | 143 |
| GLB JSON chunks that differ | 0 | 0 |
| differing GLB bytes inside NORMAL data | 364 | 2,760,672 |
| differing GLB bytes outside it | 3,025, in 3 GLBs | 3,432, in 11 GLBs |
| of those GLBs, same triangles (position, uv, colour) as a multiset | all | all 11 |
| lightmap unwrap caches that differ | 2 | 119 |
| `bake.exr` | 51,399,991 -> 51,390,738 bytes | 51,390,738 -> 50,582,001 bytes |

**What the weighting moved:**
- the normals of 143 GLBs;
- Godot's lightmap unwrap of 119 of them, because the unwrap reads normals.
  31 caches came out smaller, 23 larger and 65 the same size: 5.82 to 5.98
  MB in all;
- three dressing MultiMesh resources: litter_scrap, rubble_frag and
  weed_tuft. A fourth, pebble, also differs in the control;
- the bake.

**Every byte outside the normals is vertex ORDER.**
- 2,885 are index bytes; the rest are positions, UVs and colours that moved
  with their vertices.
- Every one of the 11 GLBs holds the same triangles as before, compared
  regardless of order.
- The exporter de-duplicates vertices in an order that follows their normals,
  so new normals can re-order a primitive.

**The control differs too, and that difference is the pipeline's own.** It
shows:
- 3 fixture and dressing GLBs re-ordered with no Zoo change;
- 14 `.tscn` files and about 80 import sidecars;
- the manifests and reports;
- a light bake that is not bit-identical run to run.

The same categories appear in 9211 and are not the weighting's.

## The price and the frames

In the finding: `docs/findings/weighted_normals/README.md`.
