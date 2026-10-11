# Cold run 9235 -- Lot 0.114.0 + Level Factory 0.177.2 on 9233's lot: STOPPED at the export's closure gate, one stage past 9234's stop

**What it tested:** 9234's plan again after Level Factory 0.177.2 taught
the Lot adapter to publish `.obj` -- roadmap 231's first lever, the road
paint as one OBJ mesh per paint colour beside the site scene (Lot
0.114.0), lightmapped through the import pass (Level Factory 0.177.1) --
on 9233's brief and lot (restaurant_row_001, `block` grammar, `cluster:
auto`, seed auto), to be priced against 9233's package.

**Result: 0 interventions, and a FAILED run.** `driver.log` ends
`STOPPED: export`, exit 5:

    EXPORT_CLOSURE_BROKEN: 2 unresolved res:// reference(s), 0 misrooted,
    2 unresolved relative, 0 absolute path(s), 0 external reference(s)
      presentation/lux.applied.tscn: unresolved res://site_marks_090_075_020.obj
      presentation/lux.applied.tscn: unresolved res://site_marks_090_090_088.obj
      site.tscn: relative ext_resource resolves to nothing: site_marks_090_075_020.obj (from ./)
      site.tscn: relative ext_resource resolves to nothing: site_marks_090_090_088.obj (from ./)
    [export] WARNING light bake failed, the package ships unbaked: the bake
      did not complete: {'error': 'bake.tscn did not open', 'ok': False}

Every stage before the export ran as 9233's did: three candidates (seeds
9003, 9104, 9205; 9104 picked, as 9233 and 9234 picked it), 0 blockers on
both legs, findings 86 on the shell leg and 122 on the art leg.

## What moved since 9234, and what did not

0.177.2 worked: the two meshes left the Lot job this time. They stand in
`jobs/restaurant_row_001.themed_site_assemble/1/out/` beside `site.tscn`
and in every stage's staging dir that read the scene --
`staging/restaurant_row_001.laser_tag_evaluate.candidate.seed_*/`,
`walktest_navqa.candidate.seed_*/`, `lux_apply/` -- and Lux's applied
scene names them as what the import made of them:
`[ext_resource type="ArrayMesh" path="res://site_marks_090_090_088.obj"]`,
with the two `Mat_site_marks_*` materials and the two MeshInstance3D nodes
carried through. So the paint was lit, walked and evaluated; it was the
package it never reached.

The export's step 2.5 (`packages/exporting/export.py`, "THE ASSEMBLY
SCENE") copies the assembly's `site.tscn` to the package root and then its
sibling DIRECTORIES by name -- `skins/`, `cover/`, `signs/` -- with the
comment "THE LIST IS THE CONTRACT ... a new sibling directory in Lot means
a line here." The paint meshes are sibling FILES. Nothing in that step, or
in the composed-root copy before it, carries a loose file from the
assembly dir: the package root holds `site.tscn`, `skins/`, `cover/`,
`signs/` and no `site_marks_*.obj`, exactly as the list says. The relative
reference from `site.tscn` and the `res://` reference from Lux's scene both
resolve to the package root, so both failed, and the bake -- which opens
the package's scene in the editor -- could not open a scene with two
missing meshes and shipped the package unbaked.

Three defects of one shape, now: cold run 9016's skins (a `.png` the
adapter did not publish), 9234's meshes (an `.obj` the adapter did not
publish), 9235's meshes (an `.obj` the export did not carry). Each list
was a contract nobody had told about the new sibling, and each was caught
by the closure gate, the last instrument in the chain, which is the gate
working and the reason it exists. The 0.177.2 proof did not reach this
step because `collect_outputs` has a test of its own and step 2.5 is
exercised only by an export over a themed dir.

## What this run is evidence of

- The lever's mechanics hold through every stage up to the export: the
  meshes are imported as ArrayMesh by the wavefront importer (Lux's scene
  shows the type), walked and lit.
- Not the price, not the look, not the bake of the paint: the package is
  refused and unbaked, so nothing in it is measured. 9235's package is NOT
  a subject.
- A failed run at 0 interventions is still a failed run; recorded here,
  not counted as a zero.

## The fix

Level Factory 0.177.3 (`patches/patch_lf_obj_in_package.py`): step 2.5
copies every `*.obj` beside the assembly scene to the package root, with a
test that runs the export over an assembly dir holding a scene that names
its mesh and the mesh beside it, and reads both back. Cold run 9236 reruns
this brief on Lot 0.114.0 + Level Factory 0.177.3 and takes over the price
plan: 9233's package the control, `tools/draw_census.py` the pool check,
`price_glow.py` and `price_vs_mean.py` the price, `paint_frames.sh` (9236's
folder; `tools/paint_stations.py`) the same stations in both packages for
the eye.
