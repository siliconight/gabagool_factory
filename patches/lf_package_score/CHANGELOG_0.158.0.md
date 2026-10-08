## [0.158.0] - The package names the score and its buildings, and only buildings that are there

**Roadmap 204's remaining half.** Measured on cold run 9194's package and
again on 9191's and 9200's, three things a game layer reading
`gameplay_anchors.json` would have been misled by.

### The generated shell's anchors were wrong either way

The staging handed Dispatch the mission's generated Deli Counter shell's
anchors beside Lot's, in the shell's own frame.
- **On a library lot** the shell is never placed, so they were the anchors
  of a building not in the level, listed first. On 9194, its
  `crack_vault` sat near the spawn building while the score's vault was the
  last anchor in the file.
- **On deli_001 (cold run 9191), where the shell IS placed** -- as b0 at
  (6, 0) -- all 85 duplicated Lot's b0 anchors by name, 6 m off.

Lot's gameplay already holds every placed building's markers in site space,
the shell's among them when it is placed. So the shell's anchors, props,
interactives and ladders are now staged only when the site has no markers to
stand in for them. Its glb still passes through, as the resolver's file
check.

### No objective was the score

Every anchor carried `"objective": ""`.
- **The tag.** `stage_dispatch_inputs(lot_site=)` reads the Lot job's drawn
  site spec for its `objective` building, and that building's objective
  anchors are tagged `score`.
- **The flow.** `mission_flow` writes spawn -> score -> extract -- a heist's
  three beats, where the package said two. The score beat is written only
  when something carries the tag, because a beat that binds to no anchor is
  a Dispatch blocker.

### No anchor named its building

Every anchor carried `"source_building": ""`, though Lot namespaces each
marker by building. `markers_to_anchors` now passes `building` through, and
Dispatch writes it as `source_building`.

### Measured on cold run 9202's own outputs

seed_9054, staged both ways and built by the real Dispatch 0.5.2:

| | as 9202 shipped | with 0.158.0 |
|---|---|---|
| beats | spawn -> extract | spawn -> **score** -> extract |
| the score beat binds to | -- | `lot:A_6`, b0's vault, at (-54, -3.9, -12.0) |
| anchors | 68 (35 of them the unplaced shell's) | 33, all Lot's |
| anchors naming a building | 0 | 28 (b0 12, b1 9, b2 7) |
| Dispatch notes | 10 info | 7 info |

**The five anchors with no building** are the van's two and the three
responder arrivals, which belong to the site, not to a building.

**The three Dispatch notes that went** were artefacts of the shell's
anchors:
- its `crew_spawn` and `responder_spawn` "unknown type" notes;
- the one Deli Counter <-> Lot nav bridge, `deli_counter:A` 1.08 m from
  `lot:MAIN_W`.

Readiness stays at 100, with 0 blockers.

### Tests

`tests/unit/test_dispatch_score_and_buildings.py` checks five things:
- no shell anchor when the site carries its buildings;
- every Lot anchor names its building;
- the score is the objective building's objective, and only it;
- the flow goes spawn, score, extract;
- with no site spec, nothing is tagged and the flow is the old two beats.

A site with no markers still stages the shell's anchors.

**On 0.157.0** the file cannot import: there is no `mission_flow`, and
`stage_dispatch_inputs` takes no `lot_site`.

**Suite:** exit 0; 2,021 passed, 14 skipped (the real-tool smokes,
`LF_TOOLS_DIR` unset), 1 xfailed.
- That is 0.157.0's 2,014, plus this file's 6, plus the one case
  `test_sibling_locator.py` adds for a new source file.
- Tallied off the progress lines: the conftest prints no summary.
