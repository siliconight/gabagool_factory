# Next

Written 2026-08-12. Everything below was measured, not remembered. The long
version is `SESSION_0812.md`.

## Start here

```powershell
cd C:\Projects\gabagool_studios\gabagool_factory
python -m level_factory -C lot-demo-ws run lot_demo_001 --art --gameplay
python -m level_factory -C lot-demo-ws walk lot_demo_001 --play
```

**Why the run first:** selection changed to `seed_5219` and the functional lock
was re-taken against it, but everything downstream of the lock was still built
from `seed_5118`.

## State

- Selection is `lot_demo_001.candidate.seed_5219`. The previous marker said
  `seed_5118` and was written 2026-08-04; nothing automatic reconsiders it.
- Last run: **structural checks passed, blockers open 0**, 75 findings.
  `dispatch_handoff` succeeded for the first time this session.
- `CLOSURE_ENFORCED = True`. A broken export now stops the run instead of
  printing a warning, and the message names all seven counters.
- `portable-godot` and `pure-shell` both scan clean; `portability-test` returns
  `PASS` with `parser_error_count: 0` in a clean Godot 4.7 project.
- All eleven repos committed and pushed. `autocrlf=input` everywhere, so
  recorded byte counts survive a checkout.

## The decision waiting for you

`seed_5219` is not obviously the better level. It is the more *interesting* one.

```
                        seed_5017   seed_5118   seed_5219
route completed            0%          0%          60%
overexposed positions      69%         37%          83%
player stuck              534        1179         1562
enemy stuck /25 runs        24          43          115
readiness                   48          45      cleared FAIL
```

It finishes the mission far more often and punishes you far more while doing
it. That is a design call, and `SESSION_0811` is explicit that Laser Tag exists
to inform it rather than make it. Walk 5219 before committing to it.

## Open, in the order I would take them

1. **Rebuild the archetype library.** The ladder still climbs into a solid
   roof, and it is not the code -- `patch_dc_roof_voids.py` is fully applied.
   `deli_counter/build/*.slots.json` was baked 2026-08-05, three days before
   the fix, and all five placed buildings carry a roof slot with **no `voids`
   key at all**. `deli_generate` cache-hits and the library is not rebuilt per
   run, so the corrected code has never reached the artifact Zoo dresses.
   Regenerate the library with the current Deli Counter. Evidence and the
   corrected status line are in `LADDER_INTO_SOLID_ROOF.md`.
2. **A doorway module is narrower than the opening it sits in.** Overlay, from
   the walk: `look Doorway 4.36 m y 2.76`, slot `ext_0_S_open0`, source `zoo`.
   It floats high in the opening and the real gap is dark below it -- the
   dimensions clause of `ASSET_SWAP_CONTRACT`, and roadmap item 35.
3. **The walktest never ran for the candidates that need it.** Both 5017 and
   5118 report `LT_ROUTE_NEVER_COMPLETED`, and the finding's own text says
   `walktest_navqa` walks the same spine with no combat in it and would say
   which leg failed -- and that it never ran for those candidates. Every
   traversal conclusion is confounded until it does.
4. **Roadmap item 41: the dressing layer.** 2,255 nodes named
   `Cover_panel_field` (1,389), `Cover_pilaster`, `Cover_gutter_run`,
   `Cover_base_course`, `Cover_curb`. Structural art routed through the
   decoration channel, which is why nothing checks it. The only open item a
   viewer notices, and the source of "dressing all over in a way that doesn't
   look good".
5. **Roadmap item 8: stranded anchors.** The file calls it "the highest-leverage
   item", the fix is ~400 `map_get_path` queries between anchor pairs, and an
   anchor that reaches zero others is stranded rather than blocked. Cheapest
   thing on the list.
6. **Roadmap item 12: props bake walkable.** 61 islands a metre off the floor,
   above `agent_max_climb`. A plausible cause of the stuck counts above, and
   nobody has connected the two.
7. **`PIPELINE_MAP.md` has no generated block**, so `factory_map.py --check` can
   only audit by name -- and reports `walktest_navqa` and `themed_site_assemble`
   named nowhere in it. Paste the generated section over the hand-written DAG
   table, markers included, and `--write` maintains it after that.
8. **25 roadmap items still rest on a sentence rather than a status line.**
   `python roadmap_status.py --unclassified` lists them.

## Instruments, all of which measure without changing anything

```powershell
python -m level_factory -C lot-demo-ws validate lot_demo_001
python -m level_factory -C lot-demo-ws portability-test lot_demo_001
python probe_lux_free.py <export_dir>                      # is Lux needed? (output only)
python patch_lf_reroot_packages.py --probe <export_dir>    # packages staged at the wrong root
python patch_lf_closure_relative.py --probe <export_dir>   # non-res:// ext_resource paths
python patch_lf_strip_walk_chrome.py --probe <export_dir>  # dev chrome in the deliverable
python roadmap_status.py --check                           # roadmap index vs its items
python factory_map.py --selftest                           # DAG table vs the planner
```

## Two things not to forget

**`res://` is absolute.** Three tools each correct in isolation produced a
broken package because a path written against one root was copied under
another. Any future stage that relocates a staged package is the same bug
waiting.

**A stale ARTIFACT looks exactly like broken code.** Twice on 2026-08-12: an
export that scanned clean while missing its geometry, and a ladder that failed
against a fix which was applied but had never reached the prebuilt library.
Before concluding the code is wrong, date the artifact it consumed.

**A whole-file SHA is the wrong guard for a patch.** `patch_dc_roof_voids.py`
reports DRIFTED because its target grew 7.5 KB from unrelated work, while every
one of its own anchors is intact. Guard per anchor with an occurrence count --
unrelated drift is not your drift.

**A check can guard the wrong field and look fine.** `ensure_mission_anchors`
guarded on anchor TYPE while the binder reads TAGS, so five real extraction
points blocked the mission that zero would have passed. The functional lock has
the same shape: `_protected_inputs_for_gate` binds it to the brief's functional
signature, not to the candidate, so **changing the selection does not
invalidate the lock** -- re-approve `functional_shell_locked` by hand, as was
done on 2026-08-12, or it silently describes the old shell.
