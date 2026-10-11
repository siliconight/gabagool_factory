## [0.177.3] - The export carries the paint meshes beside the assembly scene

**Cold run 9235 stopped at the export's closure gate, one stage past
9234's stop** (0 interventions, a failed run all the same). 0.177.2's
adapter published Lot 0.114.0's `site_marks_<colour>.obj` and every stage
up to the export found them beside the scene -- Laser Tag, the walktests,
Lux's apply, whose applied scene names them as `res://site_marks_*.obj`.
The export's step 2.5 copies the assembly's `site.tscn` and its `skins/`,
`cover/` and `signs/` -- "THE LIST IS THE CONTRACT", its comment says, and
"a new sibling directory in Lot means a line here" -- and the paint meshes
are sibling FILES, which that list cannot carry. The package's scene named
two meshes "from ./" that were not there, the gate refused it (2 unresolved
res://, 2 unresolved relative) and the bake's scene would not open.

- **Step 2.5 copies every `*.obj` beside the assembly scene to the package
  root**, where both the assembly's relative name and Lux's `res://` name
  resolve. Same rule as the directories: a new sibling in Lot means a line
  here. One test runs the export over an assembly dir holding a scene that
  names its mesh and the mesh beside it, and reads both back from the
  package.
- Nothing else moves; an assembly with no `.obj` exports as before.

**Tests:** 1 in `tests/unit/test_paint_meshes_in_package.py`. **Suite:** RESULT_SUITE.
