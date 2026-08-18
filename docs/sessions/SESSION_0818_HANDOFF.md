# Session handoff — 2026-08-18

Written at the end of the session, from the artifacts, not from memory. Every
number below was measured on this date unless it says otherwise.

## State at close

```
level_factory   0.43.3   tag v0.43.3   suite 866 passed, 11 skipped, 0 failed
lot             0.44.0   git 0028666   suite 336 passed, 0 failed, clean tree
factory         1.29.0   tag factory-v1.29.0
```

Both repos committed and clean. `PIPELINE_ROADMAP.md` has 55 items; the derived
status table is regenerated (`python tools\roadmap_status.py --write`).

## What shipped

| version | what |
|---|---|
| 0.38.0 | item 48: `_art_run` read the invocation's graph, so `batch create` drew from 123 shells and `run --art` from 98. Keyed on the brief instead. |
| 0.39.0 | item 49: `export_mission` step 2.5 overwrote the root `site.tscn` and copied nothing else. Every single-shell themed export since 0.37.0 was unopenable. |
| 0.40.0 | item 50: packages shipped two resource manifests; the stale one had the better name. |
| 0.41.0 | item 53: `lux.quality.json["preset"]` was the `--preset` argument echoed back. Now reads `LuxRoot.get_current_preset()` as `preset_applied`, raises `LUX_PRESET_NOT_APPLIED`, and stops reporting a failed `ResourceSaver.save` as success. |
| 0.42.0 | the Lux stage never hashed the driver it runs. `probe` reports **Lux's** repo commit; both drivers live in level_factory. 0.41.0 would have cache-hit and reported success. |
| 0.43.0 | per-object light cap — **wrong mechanism**, see below |
| 0.43.1 | `assert LuxAdapter.adapter_version == "0.4.0"` — a check protecting a cache invalidation, fired **on** one. Now `>=`. |
| 0.43.2 | removed the per-object cap — **wrong the other way**, see below |
| 0.43.3 | both light caps, derived and bounded by the package |
| factory 1.29.0 | re-certified on the first lit package a Godot process has loaded |

## The light thread, settled

GL Compatibility has two limits and they fail differently:

```
max_renderable_lights   default 32   GLOBAL   -> lights not drawn at all
max_lights_per_object   default  8   PER-MESH -> a mesh drops lights
```

Hardware, same route, five runs:

```
per-obj  global   result
      8      32   heavy blinking
     64      32   still blinks, areas stay dark
      8     256   clean, load hitch SMALLER
     64     256   clean
     40     256   clean            <- shipped
```

Shipped values are derived in `packages/core/godot_project.py`:
`max_renderable_lights` = the package's light count; `max_lights_per_object` =
`min(count, 40)`. Below the engine defaults neither is written.

**Both are mitigations.** 111 of 920 meshes exceed the per-mesh default of 8,
and every offender is a building-wide roof or floor/ceiling plate 34–52 m
across. That is roadmap 54.

## Open, ranked

1. **54 — one mesh spans a whole room.** Room-sized plates would need neither
   cap. Closing it means a re-measured census showing zero meshes over 8, at
   which point `PER_OBJECT_CEILING = 40` is deleted rather than tuned.
2. **55 — four blank sign faces.** `AreaPanel_Surface`, 1.4 × 1.4 m QuadMesh,
   y 2.5; three of four rigs are `@Node3D@<n>` and cannot be addressed.
3. **The load-in hitch.** Smaller after 0.43.2 dropped a cap. **Not measured** —
   no frame timing captured. Do not quote it as a finding.
4. **41 — dressing routed through the props channel.** All three published
   numbers re-measured and dead; `allowed_inward_intrusion_m` still appears
   only in the roadmap, four times, all proposing it, zero in code.
5. **53 third-ranked** — 27 Lux filename literals across 8 modules. Tidiness.
6. Older: 14 (collision trap, untouched since 2026-08-12), 44/45 (specified,
   nothing built), 46 (9 state machines per building reaching nobody),
   9/10/12/36 (nav, narrowed), Dispatch fixture data for the last skipped
   `real_tools` test.

## Method notes worth carrying

**Five mechanisms were published wrong and corrected in place**: the Lux preset
echo; `walk_preview` "silently renders unlit" (it substitutes a rig and reports
which); the per-object cap, twice, in both directions; and "it's committed"
inferred from a tag existing. The roadmap names each as wrong rather than
quietly rewriting it — keep doing that.

**Every light finding came from a human walking the level.** Closure scan
`ok: true`, portability `PASS`, 866 tests green — all true the whole time the
level blinked, went dark in rooms, and had a seam across the floor. The
headless checks cannot reach that class of defect. Run `walk --play` more often
than feels necessary.

**Two selftest needles spanned a line break** and silently tested nothing. Keep
needles short and within one wrapped line.

**A selftest whose result nobody waits for is a check that cannot fail.**
0.43.0 was committed red because the commit was pasted in the same block as the
selftest. Run the selftest, read the last line, *then* commit.

**The device bridge serves stale files.** `packages/core/ids.py` and
`adapters/presentation/__init__.py` were served pre-fix all session. When a
sandbox import fails on a symbol that exists on disk, suspect the bridge before
the code.

## Instruments added

- `tools/glb_materials.py` — which shipped meshes have no base-colour texture,
  and which of those render flat white. Parser verified against a synthetic GLB.
- `tests/unit/test_lux_preset_readback.py` — source-shape, says so in its own
  docstring.
- `tests/unit/test_lux_driver_in_fingerprint.py` — behavioural.
- `tests/unit/test_project_godot_agreement.py` — the two `project.godot`
  writers share one rule; the test pins the properties, not the coincidence.

## The one thing a headless run still cannot answer

Whether the level looks right. That needs somebody in it.
