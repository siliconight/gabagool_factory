# Cold run 9242 -- the fixture merge on 9233's lot

**What it tested:** Zoo 1.100.0 (roadmap 233): a building's fixtures layer
merged by placement -- a fixture's parts that share a material one mesh, no
two fixtures sharing one -- so a pendant's cord and socket, a sign box's arms
and cabinet and a wall pack's arm and body each draw once. Built on the
clone from cold run 9239's manifests, the lot's three layers went from 437
submissions to 402 (`docs/findings/fixture_merge/`). On the same lot as
9241 (restaurant_row_001, 9233's brief), priced against 9241's package, the
same lot one Zoo release earlier; on Level Factory 0.178.4, whose change is
the doctor's grounded table only.

**Result: 0 interventions, 0 stops -- and the package shipped UNBAKED.** Three
candidates, seed_9104 picked as in 9241, findings 123 as 9241. The export's
light bake reported `{'error': 'bake.tscn did not open', 'ok': False}` after
83.7 s in the editor (9241's baked in 94.4 s), restored the presentation
scene and shipped the package without its lightmap. A failed bake is a
WARNING in the export, so the run counted zero; the package is a worse level
than 9241's and nothing stopped. That gap is the first finding here.

**The merge reached the package:** the mission's tree holds 25,859 nodes
where 9241's held 25,894 -- the 35 fixture meshes Zoo 1.100.0 merges away.
The price against 9241 is NOT taken: an unbaked package against a baked one
measures the bake, not the merge. Cold run 9243 repeats this run on Level
Factory 0.178.5 and prices it.

## Why the bake did not open (`rebake_probe.py`)

The editor's output went to DEVNULL, so the export kept nothing. The probe
runs Level Factory's own `bake()` on a fresh copy of this package, keeping
the editor's output:

| bake | plugin | result | editor | the scene |
|---|---|---|---|---|
| the export, 0.178.4 | as shipped | did not open | 83.7 s | -- |
| probe, 0.178.4 | as shipped | did not open | 371.8 s | never (`editor.log`) |
| probe, scratch plugin | the three changes | baked, 3,483 users | -- | open after 21.0 s (`editor_fixed.log`) |
| probe, 0.178.5 | as landed | baked, 3,483 users | 102.5 s | open after 20.2 s, frame 240 (`editor_0178_5.log`) |

The failing log shows the editor's first open re-importing every texture it
finds used in 3D -- the package ships Compatibility sidecars, the bake runs a
Forward+ copy -- then twelve `scenario is null` errors and the plugin's
give-up. The plugin waited on the scene in FRAMES (180, then 3,000) and asked
for it once; an editor whose window has no focus sleeps 100 ms a frame, and
a bake opens its window on the walker's desktop while they work, so 3,180
frames came to minutes (371.8 s is 3,180 frames at about ten a second plus
the import). Level Factory 0.178.5 holds the editor's low-processor mode off,
asks once the file scan is idle and again until the scene opens, judges the
wait on a clock, and keeps the editor's output beside the package. The three
changes were proven together; which alone would have been enough was not
isolated.

The copies read 3,483 lightmap users where 9241's pipeline bake read 3,518,
and that difference is NOT attributed: the probe's runs read the responders'
car from a key the report does not carry and baked it (492 models, 0 spawned
dynamic; the car is 5 meshes), which a pipeline bake keeps dynamic. It reads
`imports.spawned` now; nothing from these copies is priced, and 9243 measures
the merge's users in a pipeline bake.

## What is evidence of what

- 0 interventions and the 123 findings: this run.
- The unbaked package and the bake's failure: this run's export and its
  `light_bake.json` (83.7 s, the result above).
- The cause: the probe's logs, on copies of this package; the fix: Level
  Factory 0.178.5, proven on the same copy.
- The merge's price: not here. Cold run 9243.

## What it says about the counter

A run that ships a package without the lightmap it was asked to bake counted
zero interventions. The export's warning was read by a person, not by the
clock. Roadmap 178 holds that defect's family -- the instruments report and
nothing blocks -- and this is its newest member.
