# Cold run 9249 -- the export, cut where the profile said

**What it tested:** three Level Factory releases on the export, the
constraint 9248 measured (7.0 of its 14.3 minutes): 0.181.0 (the greybox
census reads the bake's import cache instead of importing the package
again), 0.182.0 (the shared textures' import pins applied again after the
last import and read back off what ships) and 0.183.0 (the editor's import
of the lightmap kept, not done again). restaurant_row_001 on 9245's lot and
seeds, every other tool as in 9248.

**Result: 0 interventions, 0 tool files changed; baked on its first
attempt** (3,491 lightmap users). seed_9104 picked, the three candidates
reading as in 9247 and 9248. Findings 122 -> 122.

## The drive: 14.3 -> 12.1 minutes

    leg                     9247    9248    9249
    shell + art (minutes)   15.0     5.7     5.8
    export                   7.6     7.0     4.7   (282 s against 418)
    walk copy + retire       1.7     1.6     1.6
    the drive               24.3    14.3    12.1

The export's own log says what 0.181.0 to 0.183.0 did:

- `import cache removed` now comes after the greybox census, which read the
  bake's cache instead of importing the package from scratch;
- `import pins: 415 of 415 shared-texture sidecar(s) carry their pins; 78
  re-pinned after an import reset them` -- the light bake's first import
  reset 78 this time, and the package shipped every one pinned;
- `light_bake.json` lists `lightmap_import_copied`: the editor's two cache
  entries for `bake.exr`, so the bake's second import found them current.

## Where the time is now

The shell and the art legs together (5.8 minutes) are now more of the drive
than the export (4.7). Read off 9248's jobs: the art leg spans about 249 s
but its 78 jobs add up to 186 s, run one Blender job at a time. The drive
can now profile its legs (`PROFILE_LEGS=1`); cold run 9250 did.

**REFUTED, KEPT:** this note first said `presentation_compose` took 63.7 s
"of which its command was 1.6 s", from the job's `job.log`. The compose job
runs one command per building, sixteen of them, and `job.log` is rewritten
by each, so it holds the last building's 1.6 s alone -- the factory had
already recorded that `job.log` shows only the last building. The 63.7 s is
the sixteen commands one after another (cold run 9250's notes).

## What is evidence of what

- 0 interventions, the bake, the findings, the legs: this run's journal and
  logs; 9247's and 9248's the same way.
- The export's three changes: its own log lines and `light_bake.json`.
