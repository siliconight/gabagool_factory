# Item 48 -- the draw moved between two runs of the same job

*Written 2026-08-15, the night it was measured. Roadmap item 48.*

**Why this file exists.** Every number in roadmap item 48 came off
`workspaces\unlit-3b-ws` and `_runs\3b\`, and `.gitignore` line 20 ignores
`_runs/`. That workspace is scratch this session created for roadmap 47 stage
3b and can be deleted at any time; `fingerprint.last.json` has *already*
overwritten the first graybox assemble, which is why the table in item 48
carries only two of the three. This file is the evidence, in the repo, at full
precision, so the item can be re-checked after the workspace is gone.

---

## 1. The mechanism, located

`level_factory/apps/cli/commands/__init__.py`:

```python
# line 238 -- DOES THIS RUN HAVE AN ART LAYER?
_art_run = any(j.stage_id == "themed_site_assemble"
               for j in plan.graph.jobs())

# line 942, inside _write_site_spec -- which pool the GREYBOX pass draws from
if themed_map or art_run:
    before = len(complete)
    complete = building_library.require_themed_shells(complete, count)
    ...
lot = building_library.pick_lot(complete, seed, count)
```

`_art_run` is read off **the graph planned by this invocation**. It is not a
property of the mission, the brief, or the candidate. So:

| invocation | plans `themed_site_assemble`? | `_art_run` | pool | `pick_lot(pool, 5017, 1)` |
|---|---|---|---|---|
| `batch create` | no | `False` | 123 | `cr_garage` |
| `run --art --unlit --gameplay` | yes | `True` | 98 | `landmark_hall_a03` |

Same job id. Same seed. Same `pick_lot`. A different list handed to it.

**This is not an accident, and the code says so.** The comment above line 942
records that the narrowing was deliberately extended to the greybox branch,
and why: `probe_pool_divergence.py` had measured that on `lot_demo_001`,
*14 of 15 building slots already carried an archetype other than the one Laser
Tag graded, and 13 graded archetypes never shipped at all.* The stated fix was
"grade the pool that ships."

That fix made the graybox pass and the themed pass agree **within one
invocation**. It could not make them agree **across** invocations, because
`batch create` plans no art layer -- and `batch create` is where the graders,
the structural checks and the functional lock all run.

The divergence did not close. It moved: from within-a-run, to between the run
that grades and the run that ships.

`building_library.lot_for()` -- the other selector, used by `_lot_for_compose`
-- is NOT the path taken here. It returns `[], []` for `building_count < 2`,
and this brief asked for one building. Its own comment carries the same
warning from the other direction: *"a narrower pool re-selects every lot
already built and graded."*

---

## 2. What ran

`_runs\3b\run.log`. The same job id appears in both passes.

```
 26  === batch create ===
 27  created batch 'unlit_3b' with 1 mission(s): unlit_probe_001
 28  [site] 4 archetype(s) excluded from the lot for a missing manifest: bank, kitbash_demo, rarity_demo, survival_demo
 29  [site] 11 entr(y/ies) in C:\Projects\gabagool_studios\gabagool_factory\deli_counter\build are not source archetypes and were not offered to the lot: gs_facade_rowhome, gs_facade_storefront, lf_art_probe_001_5017, lf_category5_baie_dore_001_5017, lf_category5_baie_dore_001_5118
 30    unlit_probe_001.deli_generate.candidate.seed_5017 succeeded
 31    unlit_probe_001.lot_assemble.candidate.seed_5017 succeeded
 32    unlit_probe_001.walktest_navqa.candidate.seed_5017 succeeded
 33    unlit_probe_001.laser_tag_evaluate.candidate.seed_5017 succeeded
 34  
 35  candidates: 1 built, all distinct
 36  
 37  Structural checks passed  (blockers open: 0, total findings: 14)
...
 45  === approve lock ===
 46  approved functional_shell_locked for unlit_probe_001
 47  [site] 4 archetype(s) excluded from the lot for a missing manifest: bank, kitbash_demo, rarity_demo, survival_demo
 48  [site] 11 entr(y/ies) in C:\Projects\gabagool_studios\gabagool_factory\deli_counter\build are not source archetypes and were not offered to the lot: gs_facade_rowhome, gs_facade_storefront, lf_art_probe_001_5017, lf_category5_baie_dore_001_5017, lf_category5_baie_dore_001_5118
 49  [site] graded lot (art run): 98 of 123 shell(s) can carry a theme -- the graded draw and the shipped draw come from the same pool
 50    unlit_probe_001.deli_generate.candidate.seed_5017 succeeded
 51    unlit_probe_001.lot_assemble.candidate.seed_5017 succeeded
 52    unlit_probe_001.zoo_fixtures_build               succeeded
 53    unlit_probe_001.pixelcoat_build                  succeeded
 54    unlit_probe_001.patina_apply                     succeeded
 55    unlit_probe_001.zoo_kit_build                    succeeded
 56    unlit_probe_001.patina_dressing                  succeeded
 57    unlit_probe_001.zoo_dressing_build               succeeded
 58    unlit_probe_001.presentation_compose             succeeded
 59    unlit_probe_001.themed_site_assemble             succeeded
 60    unlit_probe_001.dispatch_handoff                 succeeded
 61    unlit_probe_001.laser_tag_evaluate.candidate.seed_5017 succeeded
 62    unlit_probe_001.lux_fixture_gate                 succeeded
 63    unlit_probe_001.walktest_navqa.candidate.seed_5017 succeeded
 64  
 65  candidates: 1 built, all distinct
 66  
 67  Structural checks passed  (blockers open: 0, total findings: 21)
 68  
```

And the export, at the end of the same log:

```
 88  === export art-unlit ===
 89  export blocked by functional regression:
 90    - collision_fingerprint changed after art pass
 91    - gameplay-anchor registry changed after art pass
```

---

## 3. The two sites

| | `site_graybox.json` | `site_now.json` |
|---|---|---|
| archetype | `cr_garage` | `landmark_hall_a03` |
| openings | 17 | 13 |
| colliders | 178 | 176 |
| markers | 12 | 7 |
| rooms | 4 | 4 |
| bytes | 56,499 | 52,712 |
| sha256 | `1d01f32493650e4171233e936b845e12` | `e89c7814f244c967b0c7230e5bd7f23f` |

Those are the numbers the functional lock compares. `collision_fingerprint`
and the gameplay-anchor registry both changed because the building changed.

---

## 4. The fingerprints, verbatim

Reproduced whole; they are small, and they are what the claims rest on.

### `lot_assemble.candidate.seed_5017` -- the THIRD assemble (graybox, 22:01:21Z)

```json
{
  "adapter_version": "0.4.0",
  "digest": "sha256:e838c66248a492f405189a06a0c3c37403de4d96b144d36b796f19cbd5906b45",
  "evaluated_utc": "2026-08-15T22:01:21.185390+00:00",
  "inputs": {
    "building_hashes": {
      "cr_garage.gameplay.json": "sha256:86ae69090bd1c80740b5d24acde119b689859f3f517224684b2f0748b04ec75c",
      "cr_garage.glb": "sha256:3f26f522fb50e21c413461b4bb12aa21cfcabc9c2a7e69c47167ec21e4286951",
      "shell.glb": "sha256:a929d7d2f5361e19fa1395b55ce65c0e6d27b197418f200fd29fda02bf09df7f"
    },
    "navqa": true,
    "site_spec_hash": "sha256:577d42ff4d14588c3ca04d5192cc806d2ae80b8cf39b7a33c29db7fbf85f2cc8",
    "walkable": true
  },
  "repository_commit": "1de7ae201d742b1d2ecda16eea3c0fcc67c946a6",
  "tool_version": "Lot 0.41.0"
}
```

### `lot_assemble.candidate.seed_5017` -- as it stood at 21:49:26Z (the art run)

```json
{
  "adapter_version": "0.4.0",
  "digest": "sha256:7db2ed94b3339432b0f42175c002eb23014d3064a6e5f0c786657ed084168873",
  "evaluated_utc": "2026-08-15T21:49:26.048638+00:00",
  "inputs": {
    "building_hashes": {
      "landmark_hall_a03.gameplay.json": "sha256:bf425c1d697a3839cf6e1087bb41f6e8ab239cdfd45e251a2430e4a28e7f5c0a",
      "landmark_hall_a03.glb": "sha256:819d19db8252a8df820b10f721b9aa645c15111f94c26bd2647155e4a998689b",
      "shell.glb": "sha256:a929d7d2f5361e19fa1395b55ce65c0e6d27b197418f200fd29fda02bf09df7f"
    },
    "navqa": true,
    "site_spec_hash": "sha256:ab8f6f563378199cc73f1a1ba0c756df717d55bc4a3988701ae379c59c278a9e",
    "walkable": true
  },
  "repository_commit": "1de7ae201d742b1d2ecda16eea3c0fcc67c946a6",
  "tool_version": "Lot 0.41.0"
}
```

`shell.glb` is
`sha256:a929d7d2f5361e19fa1395b55ce65c0e6d27b197418f200fd29fda02bf09df7f` in
**both**. The lot is the same lot; the building standing in it is not.

The FIRST graybox assemble -- the one under `batch create`, whose site the
graders and the lock measured -- has been overwritten; `fingerprint.last.json`
keeps only the last. Its archetype is known from the lock and from the graded
counts, both of which are `cr_garage`.

---

## 5. lot_demo_001: the graders and the assemble cannot be joined

### `lot_assemble` (adapter 0.4.0)

```json
{
  "adapter_version": "0.4.0",
  "digest": "sha256:d7a63ea52a4f495333af2a223da5f159b3e7443b266cfde6ebff0f1cdd37ac34",
  "evaluated_utc": "2026-08-13T23:20:57.201545+00:00",
  "inputs": {
    "building_hashes": {
      "arena_a03.gameplay.json": "sha256:64b41b6bc0b42e0c61059dce5c804243c7e3bc04739cdefa405fd9819dede2a8",
      "arena_a03.glb": "sha256:e8893db02edc0c279f5ee5c32bc52247d61605076292f4de3a9e90dc4fb3e8dc",
      "large_warehouse_a01.gameplay.json": "sha256:edbd95cef2d4e73779478eae45a117e53ebb5ccd929d28aae6272d082045a2bd",
      "large_warehouse_a01.glb": "sha256:b2cf59354f130fdfe01d1b9719c2d07d2dfade1bd03a1b1bcaa3d0b4888b525a",
      "mansion_a02.gameplay.json": "sha256:5326efc768914a434d1761021d537a042b3f1105467d79a7e54dd52c5652d278",
      "mansion_a02.glb": "sha256:1f1150f1d3990370ceac6e839423602bc4e72900c76e8dd9d48a4dc839ba60df",
      "pvp_station_ref.gameplay.json": "sha256:0d36a28a12b4aa0cba9db7c540b7c6a5cdb1f64832041ebba01a6056d5f4cd38",
      "pvp_station_ref.glb": "sha256:535777228f046d99bdff96f61e72d0c953ae7d994e617fa8cbbc66210cfcb565",
      "shell.glb": "sha256:ea47e0036cff23e7b17bdb34efa276036a7a43adb86af5f1ca2528e234f69e51",
      "strip_club_a03.gameplay.json": "sha256:dc67effbd82efe8af41de5fa770adabfd26f235796270b1c12517b68ffa69a43",
      "strip_club_a03.glb": "sha256:72d896c303ec7a3673754b683038e39d38e887f165a035753c9eedfcaefc2137"
    },
    "navqa": true,
    "site_spec_hash": "sha256:1e6623f9a58da7513617f375eddb90efde95e1ac3724822fc7eceb942a99e614",
    "walkable": true
  },
  "repository_commit": "8286f18cab4618298c341a885b3f4ed3f8a32382",
  "tool_version": "Lot 0.33.0"
}
```

### `walktest_navqa` (adapter 0.1.0)

```json
{
  "adapter_version": "0.1.0",
  "digest": "sha256:96444c13ce887c48855592b5688f4ad721f4bb7d91062278b100d24c6dac6945",
  "evaluated_utc": "2026-08-13T23:21:16.383579+00:00",
  "inputs": {
    "contract": "lot.walktest.0.1",
    "director_hashes": {
      "godot/addons/heist_nav_qa/nav_qa_director.gd": "sha256:c73b96e2bd293d22171e17ef18ca99bf42ece2303865f0811b7abba1bba73707",
      "godot/addons/lot/lot_navqa_setup.gd": "sha256:394b2fdc008122060cd42941940d1207118dc6fceeedc6a8715023baba5a0326",
      "godot/addons/lot/lot_player.gd": "sha256:6bcbd157e1201795127ca658c0ba858f166516b7b3b318a763ec3de26d0db0cd",
      "godot/addons/lot/lot_site_walk.gd": "sha256:1dfa7c130ef4228a873c9ceb471f309611e70be20f32f738f0c66cf7a2b8624f",
      "godot/addons/lot/mp_smoke.gd": "sha256:c4dc14e8e855cc2b5974e836cd4f6dfe57bde7500efa3cfbc6b83b49b9d59288",
      "godot/addons/lot/mp_smoke_node.gd": "sha256:16bebe54f6a087b0c1e8e70c8bc574b7a4640299b54aebd6efba4af3bde36934",
      "walktest.py": "sha256:d3c9771c80bd66952702896dd23a7fb11edf4a6362d227e5979f83f8bc08a091"
    },
    "scene_hash": "sha256:b3bd2815f3f57a735014d0adde87237ba128339d468357485ee694b8b4f6f773"
  },
  "repository_commit": "8286f18cab4618298c341a885b3f4ed3f8a32382",
  "tool_version": "Lot 0.33.0"
}
```

### `laser_tag_evaluate` (adapter 0.3.0) -- `addon_hashes` elided, 47 entries

```json
{
  "adapter_version": "0.3.0",
  "digest": "sha256:37d83a7c3f998250c94898decf17ef3d5f631d132cfeed97e7688867da9539a7",
  "evaluated_utc": "2026-08-13T23:21:16.984792+00:00",
  "inputs": {
    "addon_hashes": "<47 entries elided -- see _runs/3b/fp_lasertag.json>",
    "enemy_count": 6,
    "map_contract": "lt_hooks.v1",
    "run_count": 25,
    "scenario": {
      "enemy_count": 6,
      "enemy_health": 2,
      "player_count": 4,
      "player_health": 6
    },
    "scene_hash": "sha256:abf3edf58b4c5d4b63b4e61572bd215ba39ccdb8a047912fb764c2410a8f9f34",
    "seed": 5219
  },
  "repository_commit": "a1c442ed2c2ba7c3f7a89c56039b426bb73fc058",
  "tool_version": "Laser Tag 0.8.0"
}
```

**The join does not exist.**

```
lot_assemble         building_hashes + site_spec_hash    no scene hash
walktest_navqa       scene_hash                          no building hashes
laser_tag_evaluate   scene_hash                          no building hashes
```

No key in common. "Did the graders grade what shipped?" is inferred from job
ordering and nothing else. Here the ordering is tight -- assemble
`2026-08-13T23:20:57.201545+00:00`, walktest `23:21:16.383579+00:00`, Laser
Tag `23:21:16.984792+00:00`, so 19.2 s and 19.8 s -- but tight ordering is an
argument, not a check.

The two graders' own `scene_hash` values differ from each other
(`sha256:b3bd2815...`, `sha256:abf3edf5...`), so they do not agree on a
subject identifier either. Whether that is legitimate -- Laser Tag evaluates
inside `LT_MapEvalHarness.tscn`, walktest walks the site scene -- is exactly
the sort of thing no artifact currently records.

### And its lock post-dates its assemble by 23h36m

```
lot_assemble           2026-08-13T23:20:57Z
functional lock        2026-08-14T22:56
```

So `lot_demo_001`'s lock records a POST-art state and has nothing left to
disagree with. It exports cleanly for that reason, not because its draw is
stable. Roadmap 47 stages 1-3a were all measured on that mission, which is why
none of them saw this.

---

## 6. Provenance of every file quoted here

| file | bytes | sha256 |
|---|---|---|
| `_runs/3b/run.log` | 6,151 | `d2abf67a8a29fde3064dc40c17ef3b10da38cbf1` |
| `_runs/3b/site_graybox.json` | 56,499 | `1d01f32493650e4171233e936b845e12c266865d` |
| `_runs/3b/site_now.json` | 52,712 | `e89c7814f244c967b0c7230e5bd7f23f2e03326e` |
| `_runs/3b/fp_graybox.json` | 776 | `af32dee00110c741b1abf8f8a8653c42edc1b300` |
| `_runs/3b/fp_art.json` | 792 | `95c38696e453d59a0e7109abc2e083818a6227fe` |
| `_runs/3b/fp_lotdemo.json` | 1,654 | `09076ba2c622fc20ce15c2d281681bba821af316` |
| `_runs/3b/fp_walktest.json` | 1,279 | `0b0fa524ab1891e94b1df0acda3a86020051c5bc` |
| `_runs/3b/fp_lasertag.json` | 6,670 | `11fc3640d3704e52d65f8fdcbafeb0ec0727cc41` |

Workspace: `workspaces\unlit-3b-ws`, created by `tools\run_3b_unlit.ps1`;
mission `unlit_probe_001`, seed 5017, one building, one candidate, run once
from empty.

The tool set at run time is in `run.log` lines 9-22. Six of nine tools were at
WARN for drift against the certified set. That is expected for a probe
workspace and is recorded here so nobody later mistakes this for a certified
run -- but it also means the exact archetype ids above are a property of THIS
library state, and a re-run against a re-certified set may pick different
buildings while reproducing the same divergence.
