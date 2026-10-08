# Cold run 9203 -- 0 interventions; the package names the score and its buildings

bank_block_001, 9202's brief and seeds. Tests **Level Factory 0.158.0**
(roadmap 204's remaining half, `patches/patch_lf_package_score.py`):
- **The score:** the site's objective building's objective anchors are
  tagged `score`, and the flow is spawn -> score -> extract.
- **Buildings:** each anchor names its building as `source_building`.
- **No unplaced shell:** the generated Deli Counter shell's anchors are
  staged only when the site carries no markers of its own.

Tool versions hashed at `--begin`: Level Factory 0.158.0, then as 9202 --
Lot 0.99.0, Laser Tag 0.25.0, Zoo 1.85.0, Deli Counter 0.203.0, Lux 0.68.2,
Dispatch 0.5.2, Patina 0.29.1, Pixelcoat 0.61.0, Pipeline 0.6.0.

**`INTERVENTIONS: 0`.** The journal holds no entries, and the diff has
nothing changed, added, removed or unattributed. Every leg ran.

## The package, against 9202's

Both runs picked seed_9054. These are the shipped
`LF_bank_block_001.portable-godot` packages:

| | 9202 | 9203 |
|---|---|---|
| beats | spawn -> extract | spawn -> score -> extract |
| the score beat binds to | -- | `lot:A_6`, b0's vault, at (-54, -3.9, -12.0) |
| anchors | 68 (35 of them the unplaced shell's) | 33, all Lot's |
| anchors naming a building | 0 | 28 (b0 12, b1 9, b2 7) |
| Dispatch | readiness 100, 10 info | readiness 100, 7 info |

These are exactly the figures measured on 9202's own outputs before the run.
- **The five anchors with no building** are the van's two and the three
  responder arrivals, which belong to the site.
- **`responder_arrivals.json`** still names an existing anchor in every
  record.
- **The walk copy** still stands its player at the van, (-4.15, 1.0, 14.95).
- **The resource manifest** accounts for 2,748 files, as 9202's did. The
  change is in the contents of `gameplay_anchors.json`, not the file count.

## Findings against 9202, 63 -> 60

**`DISPATCH_FINDING` 10 -> 7.** The three that went were artefacts of the
unplaced shell's anchors, as predicted:
- its `crew_spawn` and `responder_spawn` "unknown type" notes;
- the one Deli Counter <-> Lot nav bridge, `deli_counter:A` 1.08 m from
  `lot:MAIN_W`, which 9194 and 9198 carried too.

The art leg's total fell by the same three, 63 -> 60.

## Other figures

- **Shell:** 3 candidates, all distinct; 0 blockers of 44 findings.
- **Seeds:** seed_9054 0 majors at completion 1.00, seed_9155 0 at 0.88,
  seed_9256 1 at 0.84, as in 9200 to 9202.
- **The bake:** 415 models and 1,366 primitive meshes lightmapped, 9 kept
  dynamic; 81 steady rigs baked, 21 failing left live; 217 room fills; 3,641
  users, 87.4 s in the editor.

**To know before comparing:** the perf harness and `tools/look_shots.py`
take their stations and cameras from `gameplay_anchors.json`. Their station
sets change with 0.158.0, so frame times across it compare different
stations.
