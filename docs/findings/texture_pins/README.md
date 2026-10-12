# Shared textures lose their import pins in a random sixth of every export

**Found 2026-10-11, by a control.** Measuring Level Factory 0.181.0 (the greybox
census reading the bake's cache, `docs/findings/grader_speed/`), cold run 9248's
own export was compared with a re-export of the same code, to learn what two
exports of unchanged code differ in. Among the expected classes (the bake's EXR,
regenerated uids, manifests) was one that is a defect: the import sidecars of the
shared textures under `_tex/`.

`export._pin_shared_texture_imports` pins three keys on every one of them, each
for a measured reason written in `_write_import_sidecars`' docstring:
`compress/mode=0` (lossless; `2` for a texture every sampler filters, 0.128.0),
`process/fix_alpha_border=false` (the default rewrites RGB under transparent
texels: 7.755 % of pixels differ) and `mipmaps/generate=true` (without the chain
`zoo_worldskin.gd`'s import-time pass rebuilds each texture as its own
ImageTexture and undoes the sharing).

**Measured, three packages of one lot** (`_tex/` sidecars, of 415):

    package                                  pinned   Godot's defaults
    cold run 9248's export (LF 0.180.1)        350        65
    a re-export, the same code                 340        75
    a re-export, Level Factory 0.181.0         338        77

48 sidecars differ between the first two: WHICH ones lose their pins varies
from export to export. A defaulted sidecar is a fresh one -- `compress/mode=0`,
`mipmaps/generate=false`, `process/fix_alpha_border=true`,
`detect_3d/compress_to=1` -- as if Godot met the texture with no sidecar.

## REFUTED, KEPT: the first pass leaves textures unimported

The export verifies its import passes by MODELS only
(`occluders.unimported_models`), so a pass that skipped some textures would
leave the pin step nothing to pin and the second pass would write defaults.
`pin_loss_probe.py`: one `--import` on a copy with every sidecar removed, three
trials -- 0 of 415 PNGs under `_tex/` left without a sidecar, each time.

## REFUTED, KEPT: the sidecar step loses them

`pin_step_probe.py`: Level Factory's own `_write_import_sidecars` (pass one, the
pins, the GLB sidecars rewritten, the cache removed, pass two) on a stripped
copy, twice: all 415 pinned after it, and all 415 after one more `--import` over
its cache. The pins are lost LATER in the export.

## Where: the light bake's first import

`pin_phase_probe.py` runs the real export in-process (cold run 9248's
workspace, its own package held aside and put back) with a pin census before
and after each later phase (`pin_phase_probe.out.txt`):

    phase                                       pinned   defaulted
    before the occluder bake ... before the
      light bake's first --import                 415         0
    after the light bake's first --import         329        86
    after its second --import, the census,
      the cache drop, and as shipped              329        86

The pass that loses them is the one that re-imports every model
`mark_imports` moved to static lightmaps (the UV2 unwrap). Reproduced on a copy
with the engine's verbose log (`pin_bake_import_probe.py`): that one pass
imported textures **1,843 times for 476 models** -- the same shared file again
and again, several imports of it in flight at once -- and 64 of 415 sidecars
came out with the defaults. Each model's re-import imports the textures it
uses, and a shared texture is used by many.

## REFUTED, KEPT: Godot's 3D detection

Every sidecar, pinned or not, carries `detect_3d/compress_to=1`, the engine's
rule for re-importing a texture when a 3D scene uses it -- a rule the pins
contradict, since they choose the compression themselves. `pin_detect3d_probe.py`
pinned it off and ran the same reproduction: 62 of 415 defaulted, and the same
1,843 texture imports. Not that setting.

## The fix: read the pins back off what ships (Level Factory 0.182.0)

The trigger is inside the engine's import of a scene's textures, so the export
cannot stop the race without owning the engine; it can stop the race SHIPPING.
`_repin_after_imports`, between the cache drop and the closure verdict, applies
the shared and sign pins again over the files that ship, reads every shared
sidecar back, and refuses a package that still carries a wrong or a missing
pin. Measured on the same workspace (`pin_phase_probe_0182.out.txt`): the bake's
import reset 80, the read-back re-pinned 80, and the package shipped 415 of 415
pinned. Cold run 9248's own shipped package, audited the same way, needed 65.

**Not fixed, and said:** the cache the bake read was built with the pins the
race left, so the lightmap was baked against a few textures without their mip
chain or with the alpha border filled. Nothing a lightmap stores depends on
either. A pass that unwrapped the models without re-importing their textures
would remove the race itself; roadmap 239's export work is where that belongs.

## What is evidence of what

- The counts: the census script reads each sidecar's two always-pinned keys
  (`mipmaps/generate`, `process/fix_alpha_border`); "defaulted" means both at
  the engine's defaults, and no sidecar was ever seen with one key of each.
- The 1,843: `Importing file:` lines for PNGs in one verbose `--import`.
- The packages: cold run 9248's workspace, re-exported in place with its own
  package held aside and restored byte for byte by moving it back.
