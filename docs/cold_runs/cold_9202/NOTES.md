# Cold run 9202 -- 0 interventions; the package says how responders arrive

bank_block_001, 9201's brief and seeds. Tests **Level Factory 0.157.0**
(roadmap 212, `patches/patch_lf_responder_arrivals_sidecar.py`):
`responder_arrivals.json` ships each responder arrival beside its anchor --
the road end a vehicle appears at, the stop, which way it faces, the lane and
stop boxes Lot keeps clear.

Tool versions hashed at `--begin`: Level Factory 0.157.0, then as 9201 --
Lot 0.99.0, Laser Tag 0.25.0, Zoo 1.85.0, Deli Counter 0.203.0, Lux 0.68.2,
Dispatch 0.5.2, Patina 0.29.1, Pixelcoat 0.61.0, Pipeline 0.6.0.

**`INTERVENTIONS: 0`.** The journal holds no entries, and the diff has
nothing changed, added, removed or unattributed. Every leg ran.

## The file, in the shipped package

`responder_arrivals.json`, schema `level_factory.responder_arrivals.v1`, in
the frame of `gameplay_anchors.json` (Godot: x, y up, z = -site y). The
export said `[export] responder arrivals: 3, in responder_arrivals.json`.

| anchor | entry | stop | forward | run in |
|---|---|---|---|---|
| `lot:responder_arrival_responder_spawn_0` | (-29.9, 0, -29.5) | (-29.9, 0, 1.0) | (0, 0, 1) | 30.5 m |
| `lot:responder_arrival_responder_spawn_1` | (-86.5, 0, 22.55) | (-14.0, 0, 22.55) | (1, 0, 0) | 72.5 m |
| `lot:responder_arrival_responder_spawn_2` | (86.5, 0, 19.75) | (7.0, 0, 19.75) | (-1, 0, 0) | 79.5 m |

**Every record names a real anchor.** Each one exists in
`gameplay_anchors.json`, tagged `responder`, at exactly the record's stop.
These are the seed_9054 arrivals 9200 planned, turned into the package's
frame.

**The package's own gates pass:**
- the file is listed in `portable_resource_manifest.json`, whose accounting
  holds: 2,746 listed + 2 declared unlisted = 2,748 files;
- `export_closure_scan.json` reads ok, 0 issues;
- `HANDOFF.md` carries the paragraph that says where the mission starts and
  ends and where responders arrive.

**Everything 9201 proved still holds:** the spawn and extract beats bind to
the van, there are three `responder` anchors, and the walk copy starts at
the van.

## Findings against 9201, 63 -> 63

Nothing moved.

## Other figures

- **Shell:** 3 candidates, all distinct; 0 blockers of 44 findings.
  **Art:** 0 blockers of 63.
- **Seeds:** seed_9054 0 majors at completion 1.00, seed_9155 0 at 0.88,
  seed_9256 1 at 0.84, as in 9200 and 9201.
- **The bake:** 415 models and 1,366 primitive meshes lightmapped, 9 kept
  dynamic; 81 steady rigs baked, 21 failing left live; 217 room fills; 3,641
  users, 86.4 s in the editor.

**Not checked:** a runtime reading the file -- there is none yet; the
gameplay layer is somebody else's. The cruiser that would drive the lane does
not exist yet either.
