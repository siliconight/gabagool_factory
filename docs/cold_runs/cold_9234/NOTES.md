# Cold run 9234 -- Lot 0.114.0 + Level Factory 0.177.1 on 9233's lot: STOPPED at the export's closure gate

**What it tested:** roadmap 231's first lever -- the road paint as one OBJ
mesh per paint colour beside the site scene (Lot 0.114.0), lightmapped
through the import pass (Level Factory 0.177.1 asks the wavefront sidecar
for `generate_lightmap_uv2`) -- on 9233's brief and lot
(restaurant_row_001, `block` grammar, `cluster: auto`, seed auto), to be
priced against 9233's package at the fixed stations.

**Result: 0 interventions, and a FAILED run.** `driver.log` ends
`STOPPED: export`, exit 5:

    EXPORT_CLOSURE_BROKEN: 0 unresolved res:// reference(s), 0 misrooted,
    2 unresolved relative, 0 absolute path(s), 0 external reference(s)
      site.tscn: relative ext_resource resolves to nothing: site_marks_090_075_020.obj (from ./)
      site.tscn: relative ext_resource resolves to nothing: site_marks_090_090_088.obj (from ./)

Every stage before it ran as 9233's did: three candidates (seeds 9003,
9104, 9205; 9104 picked on the walktest and Laser Tag's route findings, as
9233 picked it), 0 blockers on both legs, findings 86 on the shell leg and
122 on the art leg. The bake ran on the refused package -- `472 model(s)
and 1136 primitive mesh(es) lightmapped, 211 steady rig(s) baked, 29
failing and 0 cycling left live` -- but the two paint meshes were not
among the models, because they were not in the package.

## The cause, read off the tree

Lot's job wrote both meshes beside its scene
(`jobs/restaurant_row_001.themed_site_assemble/1/out/site_marks_090_075_020.obj`,
`..._088.obj`: 13 and 103 quads on the smoke build of this lot's kerb
probe) and declared each as a Mesh ext_resource, as 0.114.0 says. The
composed site in the package references them "from ./" and they are not
there: `LotAdapter.collect_outputs` (`adapters/lot/__init__.py`) publishes
a job's `.tscn/.json/.csv/.glb/.gd/.png` and nothing else, so the OBJs
never left the job's work dir. The scene was published without its meshes,
the compose and Lux stages loaded it with two resources missing (nothing
in them reads a Mesh ext_resource that resolves to nothing), and the
export's closure gate was the first instrument to say so -- correctly, and
three stages after the drop. It is the shape cold run 9016 had with the
skins (`.png` joined the list on 2026-09-12), and the comment above the
list already said why: a published artifact has to be the whole artifact.

The 0.177.1 clone proof could not have caught it: the adapter's publish
list is exercised by the pipeline, not by `light_bake`'s tests, and the
one test that pins the list (`test_the_lot_adapter_publishes_the_skins_beside_the_scene`)
asks for the skins and nothing more.

## What this run is evidence of

- The lever's own mechanics held as far as they were reached: Lot wrote
  the meshes and the scene, the closure gate resolved every other
  reference (81 resources, 74 relative references, 2 unresolved), and
  nothing upstream of the export objected to the scene's new shape.
- Not the price, not the look, not the bake of the paint: the package is
  refused, so nothing in it is measured. 9234's package is NOT a subject.
- A failed run at 0 interventions is still a failed run; it is recorded
  here and not counted as a zero.

## The fix

Level Factory 0.177.2 (`patches/patch_lf_obj_published.py`): `.obj` joins
`collect_outputs`' suffixes, with a test that stands a scene, its mesh and
its manifest in a work dir and reads all three back. Cold run 9235 reruns
this brief on Lot 0.114.0 + Level Factory 0.177.2 and takes over this run's
price plan: 9233's package the control, `tools/draw_census.py` the pool
check, `price_glow.py` and `price_vs_mean.py` the price, `paint_frames.sh`
(9235's folder; `tools/paint_stations.py`) the same stations in both
packages for the eye.

## Instruments

- `paint_frames.sh` (written for this run, carried to 9235's folder to run on
  its package; a refused package is not a subject):
  `tools/paint_stations.py` derives seven stations from the drawn spec and
  the markings manifest -- down each of the three streets, short of each
  street's first crosswalk, off the first bay ticks -- and `look_shots`
  shoots them in 9233's package and the subject's; `paint.png` puts the
  per-marking materials beside the one mesh a colour, bar for bar.
