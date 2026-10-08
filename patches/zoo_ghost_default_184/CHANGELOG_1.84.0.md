## [1.84.0] - the ghost is the getaway van's own: every step van carries SKEEVY'S WOODER ICE, patched

### The walker's choice

On 1.83.0's frames, which showed the ghost both even and patched
(2026-10-08): "make the ghost the default, patchy version".

### What changed

- **Every step van carries the ghost.** The recipe builds
  `van_forms.ghost_art` and maps the box's sides into it on every build.
  `variant: 1`, which chose between a plain van and the ghost, is gone, and
  so is the genome's `module_variants: 2`. A slot that still asks for a
  variant is told the species has none, as `kit.honour_dressing` tells any
  species.
- **The paint keeps its plain name.** It is `M_Van_paint` again, now always
  the art under the `Wear` colour (`materials.make_wear_textured_material`).
  The flat paint material is no longer made.
- **The patched letters stay as 1.83.0 shipped them**
  (`GHOST_PATCH` 0.30 .. 1). The walker chose these over the even ones.

### Built

The same van as 1.83.0's variant 1 at the default size:
- PASS, with an exact fit;
- 5,372 triangles;
- five submissions;
- the art `Van_ghost_f98037e2`. Its name is identical from system Python
  and from Blender's, because it is named by its definition.

The plain GLB no longer exists: a build without the art is not a step van
this version can make.

### Tests

**`tests/test_step_van.py`: 390 pure, 8 built.** All 398 passed inside
Blender 5.1.1.
- **The material set** expects one `make_material` fewer, and
  `make_wear_textured_material("M_Van_paint", ...)`.
- **The five-submissions test** now finds a `baseColorTexture` on the
  paint.
- **The ghost test** builds the default.
- **The same-file test** builds one van, not two variants.
- **The genome** carries no `module_variants`.

**Suite:** 3,782 passed, 395 skipped, 1 xfailed in 337 s (`python -m pytest -q`): 1.83.0's 3,782 and 396, less the same-file test's second variant (built, skipped without Blender).

