# Cold run 9201 -- 0 interventions; the package starts and ends the mission at the van

bank_block_001, 9200's brief and seeds. Tests **Level Factory 0.156.0**
(roadmap 204, `patches/patch_lf_site_markers.py`): Lot's site-level markers
reach Dispatch, so the getaway van's crew spawn and extraction become the
package's mission start and exit, and the responder arrivals become
`ai_spawn` anchors tagged `responder`.

Tool versions hashed at `--begin`: Level Factory 0.156.0, then as 9200 --
Lot 0.99.0, Laser Tag 0.25.0, Zoo 1.85.0, Deli Counter 0.203.0, Lux 0.68.2,
Dispatch 0.5.2, Patina 0.29.1, Pixelcoat 0.61.0, Pipeline 0.6.0.

**`INTERVENTIONS: 0`.** The journal holds no entries, and the diff has
nothing changed, added, removed or unattributed. Every leg ran.

## The package, against 9200's

Both runs picked seed_9054. These are the shipped
`LF_bank_block_001.portable-godot` packages:

| | 9200 | 9201 |
|---|---|---|
| the `spawn` beat binds to | `lot:mission_start` | `lot:getaway_van_crew_spawn_0` |
| the `extract` beat binds to | `lot:EXIT`, `lot:STREET`, `lot:STREET_25` | `lot:getaway_van_extraction_0` |
| the package's `player_start` | (-7.03, 0, 0.68), the centroid of every Lot anchor | (-4.15, 0, 14.95), the van's door |
| anchors | 64 | 68 |
| tagged `responder` | 0 | 3 |
| Dispatch | readiness 100, 10 info | readiness 100, the same 10 info |

**The walk copy moved with it.** `tools/walk_export.py` stands its body at
the package's own `player_start`. 9201's walk copy stands the player at
(-4.15, 1.0, 14.95), the van's door, where every earlier walk of a generated
heist stood them at that centroid. `walk_export.py`'s docstring had measured
the disagreement on this mission before: the anchor at [2.77, 0, -1.29], the
walk scene at [8, 1, 12]. On a heist with the van, the two now agree.

## Findings against 9200, 63 -> 63

Nothing moved. Dispatch's ten notes are word for word 9200's: the `crew_spawn`
and `responder_spawn` "unknown type" notes are the unplaced Deli Counter
shell's own markers -- the other half of item 204 -- not Lot's, which now
arrive mapped.

## Other figures

- **Shell:** 3 candidates, all distinct; 0 blockers of 44 findings.
  **Art:** 0 blockers of 63.
- **Seeds:** seed_9054 0 majors at completion 1.00, seed_9155 0 at 0.88,
  seed_9256 1 at 0.84, as in 9200.
- **The bake:** 415 models and 1,366 primitive meshes lightmapped, 9 kept
  dynamic; 81 steady rigs baked, 21 failing left live; 217 room fills; 3,641
  users, 86.9 s in the editor.

**Not checked:** how each arrival arrives -- the entry, the lane, the stop's
room. A Dispatch anchor holds only a position and tags; Level Factory 0.157.0
ships the rest as `responder_arrivals.json`.
