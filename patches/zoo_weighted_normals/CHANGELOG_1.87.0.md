## [1.87.0] - weighted normals: a bevelled part's faces read flat, and its edges catch the light

### What was wrong

The walker's modern low-poly standard (`docs/reference/`, roadmap 214) asks
for controlled normals. Its Addendum A.4 puts weighted normals first of four
trials, because they cost no texture and no triangles.

What Zoo shipped on a bevelled part was a dome:
- **`shade_by_angle` smooths every fold under 50 degrees.** That is what
  turns a one-segment chamfer into a highlight instead of a facet.
- **The default corner normal weighs a fan's faces by corner angle.** So a
  big face and the 1.4 cm chamfer beside it count about the same, and every
  corner of the big face leans toward the chamfer.
- **Measured** on a 0.6 x 0.4 x 0.5 m crate built through `bm_to_object`
  and read back out of its GLB: all 36 big-face corners sat **28.89
  degrees** off their face.
- **The same 28.9 degrees** `bm_to_object`'s docstring measured on a wall
  panel and called "shaded as a dome". The walls avoided it by keeping every
  edge hard; the props kept it.

### What changed

**`core.normals.weighted_corner_normals`** (new, pure Python). Each corner's
normal is the AREA-weighted sum of the faces in its fan.
- **A fan** is Blender's own split: the corners of one vertex, joined across
  an edge that is not sharp, borders two faces, has both faces smooth, and
  is wound consistently.
- **So** a big face keeps its own normal, and a chamfer between two big
  faces rolls from one to the other.

**`bpylayer.geometry.weight_normals(me)`** writes them as the mesh's custom
normals.

**`export.export_glb(..., weighted_normals=True)`** weighs every visual part
before packing. That is after everything that moves a vertex, so the normals
come from the geometry that ships.

**`merge`** carries each part's corner normals into the packed mesh when any
part has custom ones.
- **Why it has to.** A new mesh's normals are recomputed from its edges.
  That reproduced the parts' default normals exactly, because nothing welds;
  it cannot reproduce custom ones.
- **A fix it brings with it, measured.** Ingest of a file whose two parts
  share a material lost the author's normals in the merge: 8 of 104 kept on
  1.86.0, 104 of 104 now.

**Ingest passes `weighted_normals=False`:** an imported mesh keeps the
normals its author made.

**The control.** `build.DEFAULT_OPTIONS["weighted_normals"]` (True) reaches
every export. `--no-weighted-normals` turns it off: `tools/zoo_cli.py` passes
it into all four of its option sets, and `tools/preview_specimen.py` into its
three builds. A before/after is then one piece built twice.

### What it does, measured

From `docs/findings/weighted_normals/`, against 1.86.0's shading exported
from the same scene.

**The crate:**
- **Splay:** 28.89 to 2.40 degrees mean on its big faces.
- **The same 48 vertices.**
- **Through the merge:** two such crates packed into one mesh read 2.40
  too.

**Every species** (`census.py`, each built once at its default corner and
exported both ways), 121 of 122 (`boots` does not build through the kit
path, as `test_coincident_faces.DID_NOT_BUILD` already records):
- **Unchanged in 121 of 121:** vertices, triangles, primitives and file
  bytes. That is the cost: no draw call, no vertex, no byte.
- **Big-face corners over 10 degrees off their face,** all species:
  15,114 to 5,498.
  - To 0: canopy_lights 756, safe_deposit_boxes 540, pallet_stack 312,
    pool_table 276, back_bar 264, stair_rail 240, payphone 180 (one of the
    standard's approval assets) and teller_line 144.
  - booth_seat 480 to 12.
  - The trees about halve; the cars move least (cruiser 888 to 735), because
    a curved body is meant to be off its faces.
- **81 species changed.** In the other 40, no triangle corner's normal moved
  over 1 degree: the parts kept faceted on purpose (the hydrant, the vending
  machine), the walls, and the flat panels.
- **The largest move anywhere is 40.08 degrees** (cheesesteak), the same
  figure the fan probe read in the mesh itself.

### Tests

`tests/test_weighted_normals.py`, 12:
- **On a chamfered prism:**
  - a big face keeps its own normal (0.401 degrees off, the area ratio's
    figure);
  - the chamfer rolls from one face to the other;
  - a sharp edge, a flat face or reversed winding each splits a fan;
  - every fold hard is every face its own normal;
  - degenerate fans keep the default;
  - the corner order is the mesh's.
- **The fixture's own check:** the default would put that face 22.5 degrees
  off.
- **The wiring, pinned in the source:**
  - every build export passes the option;
  - ingest passes False;
  - the merge carries corner normals.

On 1.86.0 the module does not import, so all 12 fail.

**Suite:** 4,027 passed (4,015 + 12), 395 skipped, 1 xfailed, `python -m pytest -q`.

