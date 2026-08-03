# Session 0803 — dressing, and learning to look at the result

Picks up from `SESSION_0802.md`. Everything below is committed unless the
"Open" section says otherwise.

---

## The one-paragraph version

The day started as "fix the Patina dressing scale defect" and turned into
finding that **nothing in this pipeline has ever looked at its own output**.
Nine defects were fixed. Every one of them was found by a human walking a level
and saying "that looks wrong", while the build reported *structural checks
passed, 0 blockers*. So the second half of the day went into the missing organ:
a render gate, a producer/consumer sweep, and the first rule that says where
dressing may not go. The dressing itself is measurably better and still not
good, and the reason is in "What I actually think" below.

---

## What shipped

### Patina 0.19.0 — placement
| Defect | Was | Now |
|---|---|---|
| `dims` × `scale` squared every wall remainder | gutter at z **12.61** on a 3.7 m storey | `Slot.size()`, one rule, one place |
| ground families measured from the foundation | curbs at **−4.30**, under the basement | storey 0's floor plane, **0.00** |
| conduit referred to no light | **60** runs at 4.77–5.67 m | **4**, to real DC wall packs, 2.45–2.85 |
| a normal alone can't orient a strip | 64 roofline caps + 64 curbs pointing at world **+X** | `tangent` rides through; strips run along their wall |
| conduit span still scaled a hint | 2.45 m run built as a **6.53 m** bar | `size` used directly |
| `--extract-family` split a Windows path on the drive colon | red on Windows, green on Linux | splits on the last colon, digits only |

### Patina — the keep-out rule (new, `patina/openings.py`)
**Dressing never intersects a traversable opening.** Door, garage, window,
breach. `frame` is the sole exemption, because surrounding an opening is its
purpose. Enforced **once** over the assembled order list, so a family added
later is covered without anyone remembering.

An opening is a **lane, not a plane**: the box is extruded along the wall
normal by a derived reach — half the wall thickness, the deepest a cover stands
proud, and one nav agent radius (0.40, from Lot's own walk-scene
NavigationMesh). 0.675 m each side on a 0.35 m wall.

Windows are in it for the reason you'd want: **glass breaks, so a window is a
firing line**. Pinned by tests that cover both across the glass and behind it.

`openings.violations()` is the gate. It has already earned itself twice: once
catching a shortened conduit sitting **0.5 mm** under a door head after
millimetre rounding, and once catching that the rule was testing the wrong box
entirely (below).

### Zoo
- Covers resolve the **Pixelcoat skin library** — the dressing job never got
  `skins_dir` or `--theme`, so 2,255 covers shipped as one flat grey material
  while the walls beside them wore a real `concrete_polished_casino` pack.
- **World-continuous UVs.** `cube_project_uv` reads local vertex coords and
  covers are built at the origin, so all 1,374 panels sampled one patch of
  concrete. The grid you saw was the texture restarting per cell, not the
  3 cm gaps.
- `strip_yaw` moved from `bpylayer` to `core`, which is why the yaw bug
  survived: it lived in the one layer the 219-test suite cannot reach.
- `dress_cover`'s docstring claimed UVs came from `uv_region`. They never did.

### Instruments (`tools/`)
- **`shot_diff.py`** — the counterpart `look_shots.gd` never had. Statistics
  always, pixels on `--images`, thresholded at 8/255. Only blown highlights,
  crushed shadows and uniform frames are *regressions*; everything else is
  *change* for a human. Reports unchanged shots too. Refuses across differing
  adapter/renderer/viewport **and subject**.
- **`orphan_artifacts.py`** — `never_wired.py` one layer out, where the seam is
  a file. Found `.trim.png`, `.trim.json`, `.instances.json` named only by
  Patina itself across nine repos.
- **`anchor_storeys.py`**, **`anchor_planes_diff.py`** — which plane each
  dressing family is measured from, and what the fix moved.
- **`walk_themed.py`** — defaults into `_runs/`, refuses to assemble inside the
  workspace, ships **Lux** (and enables the plugin), removes Lot's second sun,
  renders `gl_compatibility` like the export, and rebuilds while the editor is
  open.

---

## Verified in the shipped build

```
Cover_panel_field  1315      Cover_curb          58  [0.00]
Cover_gutter_run    299      Cover_base_course   57  [0.00]
Cover_pilaster      285      Cover_conduit_run    4  [2.40, 2.45, 2.80]
Cover_edge_strip     64  [7.70, 9.00]
materials: ['M_Skin_concrete_rockay']   images: 2

keep-out: dropped {base_course 7, curb 6, panel_field 59, pilaster 14}
          shortened {conduit_run 4}
gate:     0 violations in the manifest, 0 in the built geometry
```

Suites: Patina **248**, Zoo **219 + 2 skipped**, Level Factory green.

---

## Retractions — kept above the results that replaced them

1. **"None of your fixes are in the GLB."** They all were. I read an
   11,871,348-byte stale copy while the bridge reported 12,085,372. I know that
   failure mode and staged the same path twice anyway. **Stage a path you have
   never staged before, and check the byte count against the device.**
2. **"The B=255 metallic channel is a landmine."** It is the *correct* neutral —
   glTF defines those channels as multipliers against `metallicFactor`. Writing
   B=0 would have hard-coded "never metallic" and been the actual bug. Called
   from reasoning, without measuring.
3. **"Every mesh loads at its local origin."** `cli.py:75` bakes them. The
   collapse was my instrument omitting `bake_visual_transforms()`.
4. **"The roofline strips are architecture, leave them."** Waved through on
   reasoning. The render said otherwise and you were right.
5. **`orphan_artifacts.py`'s loudest line was noise** — `level.schema.json` at
   157 mentions, because section B only checked the workspace and not the repos.
6. **A blanket keep-out margin** sized to the widest cover dropped 11 gutters
   and all 4 conduits that were never near a hole. Per-cover is the right lever.
7. **The room-interior rule was measured and rejected** — it flagged 1034 of
   2098 orders, including 603 of 1315 panel fields, because `gameplay.json`
   room bounds include the wall plane. A rule that flags half the dressing is
   measuring the wall.

---

## The pattern, now at eight

Designed correctly, never wired: `LuxLightLoader` · Zoo's `LuxEmit_*` markers ·
`upstream_artifact_hashes` · `provenance.inputs` · Patina's trim atlas ·
`instances.json` · `uv_region` · the Pixelcoat skin library on the dressing job.

From inside the code a wired thing and an unwired thing look identical. The
only thing that tells them apart is somebody looking at the output — which is
why the render gate matters more than any single fix above.

---

## Open, in the order I'd take it

1. **Conduits need a definition, not a patch.** They currently run from the
   *pavement* up to each wall pack, which is why they keep crossing doorways —
   nothing runs electrical service up from the street to a lamp. Options: a
   short **stub** from the fixture to a junction box (0.3–0.6 m, always clear),
   a **service drop** from the roofline, or **retire the family**. I'd take the
   stub. **This is a decision, not a task.**
2. **Two gates are written and unwired.** `openings.violations()` isn't in the
   LF Patina adapter, and `shot_diff` isn't after `lux_apply`. Both are one
   adapter change from being automatic rather than remembered.
3. **Zoo should publish its cover dimensions as a contract.** Patina currently
   *mirrors* `_COVER`'s cross-axis and span scaling to enforce the keep-out —
   and one of those mirrors went stale **within the same day it was written**
   (conduit's span scaling, which I'd removed that morning). Patina cannot
   enforce a geometric rule on geometry it does not specify.
4. **Three live leads from `orphan_artifacts.py`**: `zoo.catalog.json` is named
   in `dispatch/cli.py` and `resolver.py` and exists nowhere; the dispatch
   manifests declare `lux.profile.json` / `lux.volumes.json` /
   `shell.collision.json` that are never written; 917 `.provenance.json` files.
5. **`themed_site_assemble` cache-hit right after `presentation_compose`
   re-ran** — `upstream_artifact_hashes` is populated nowhere (roadmap 39).
6. **The three building types** — facades, enterable, mission — still queued.

---

## What I actually think

The tools are ahead of the feedback loop, and that is the bottleneck.

"Alive" is specificity, and the pipeline currently maximises sameness: *for
every wall slot, emit a gutter, a pilaster and a full panel grid*. That is
tiling, not placement. The Bloodborne writeup names the two techniques that
break it — **inserts over a continuous tileable**, and **vertex-paint variation
between instances** — and you have both. The tileable is continuous as of
today. The variation is `instances.json`, computed, deterministic, and never
emitted.

Nothing breaks the silhouette either. `wall_base` was specified for "dumpsters,
pallets, electrical boxes, AC units" and `roofline` for "HVAC, vents, tanks,
the silhouette breakers" — both currently emit 10 cm strips. That is why
buildings still read as boxes with good concrete on them.

And the naming matters more than it sounds: **none of the 2,184 orders is set
dressing.** They are facade articulation — pilasters, gutters, base courses,
frames — wearing the word "dressing". Articulation gets checked like
architecture (does it respect the building). Set dressing gets checked like
gameplay (does it respect the player). Splitting `dressing.json` along that seam
would give each half the gate it needs and make the missing half visible as
missing, rather than as 64 edge strips.

More keep-out rules will not fix this. Rules subtract. The next real gain is
spending the variation that is already computed, then building the prop layer
against the gameplay gates from day one — with the render gate in place so it
takes hours instead of a day.
