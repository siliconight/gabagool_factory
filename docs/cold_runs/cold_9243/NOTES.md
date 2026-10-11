# Cold run 9243 -- 9242 again on Level Factory 0.178.5: the scene opened, and the image came back empty

**What it tested:** the fix for 9242's unbaked package. Level Factory 0.178.5
keeps the bake's editor awake, asks for the scene until it opens, judges the
wait on a clock and keeps the editor's output. Same lot, same tools as 9242
otherwise (Zoo 1.100.0's fixture merge), to be priced against 9241.

**Result: 0 interventions, 0 stops -- and the package shipped UNBAKED again,
for a different reason.** Three candidates, seed_9104 picked as before,
findings 123. The kept editor log (`<package>.lightbake.log`, in the
workspace) says what happened:

- The plugin asked for the scene at frame 190; the ask was DROPPED -- the
  scene opened only after the second ask, at frame 300, 29.6 s in. 0.178.5's
  retry was needed, and worked.
- The bake ran 46 s, then the editor read its lightmap image back EMPTY:
  `src_image_len == 0`, "Error importing 'res://bake.exr'",
  `BAKE_ERROR_CANT_CREATE_IMAGE`, and the dialog "Failed creating lightmap
  images. Make sure the lightmap destination path is writable." The plugin
  read the dialog, reported it and quit; the export shipped unbaked.

**The same package bakes on the next try** (`docs/cold_runs/cold_9242/
rebake_probe.py` with `REBAKE_RUN=9243`, Level Factory's own `bake()` on a
fresh copy, 0.178.5): ok, 38.2 s, 491 models lightmapped with the responders'
car kept dynamic -- the shape of 9241's pipeline bake -- and **3,483 lightmap
users, 9241's 3,518 less the 35 fixture meshes Zoo 1.100.0 merges away.**
So the empty image is not the package's. What got between the editor's
write and its read, the logs do not say; an antivirus scan of the fresh file
is one candidate and nothing more.

## What changed because of it

- **Level Factory 0.178.6** tries a failed bake once more on a fresh copy
  (`BAKE_ATTEMPTS` = 2), keeps every try's editor log and reports the tries.
- **The cold drive stops** when an export asked to bake ships unbaked
  (`patches/patch_cold_drive_bake_stop.py`), reading the package's
  `light_bake.json` rather than its log: 9242 and 9243 both counted zero with
  an unbaked package, and from here neither would.
- The price is NOT taken here (an unbaked package against a baked one).
  Cold run 9244 repeats this run on 0.178.6 and takes it.

## What is evidence of what

- 0 interventions, 123 findings, the unbaked package: this run.
- The dropped first ask and the empty image: this run's kept editor log.
- The package baking on a second try, and the 35-user drop: the probe's
  bake of a copy, on 0.178.5, spawned set as 9241's.
