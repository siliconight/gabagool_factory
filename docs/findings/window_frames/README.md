# A window has a frame and a sill (roadmap 324, the shape step)

The walker, 2026-10-28, after the realism trial's first step (linear sampling, `docs/findings/realism_trial/`): "i
think its less about realistic textures and more about the 3d shape themselves?", and of the plan that followed, "Yes
now you get it".

**RETRACTED, kept here because it was said to the walker.** "3,614 of 4,154 meshes are 12-triangle boxes, almost all
architecture" was counted off seed 9082's package GLBs. Those include the greybox shell under every building; what a
player sees is Zoo's modules, merged per wall side into `lot/<building>/merged/*.res`. The count described the wrong
geometry, and the plan drawn from it ("the work is Deli Counter's shells") named the wrong owner.

**What reads flat, grounded.** Zoo's window module (`core.arch.void_for` + `recipes/_arch.build_slab`, 1.144.0) is a
slab with a hole and a pane at mid-depth. Measured off the package's own GLBs: the bank's `window_delco_1997_01_w160`
is 1.6 x 3.3 x 0.30 m with a 0.045 m pane at the wall's centre -- a 13 cm reveal each side, in the wall's own
material. So the depth was there; nothing framed the glass, nothing stood out of the face, and a reveal lit the same
as the face it is cut into disappears (`frames`' before column: a teal square on the plaster). An Empty's window is
the exception, and from elsewhere: its sash is painted on the pane (`window_panes`) and its stone sill and lintel are
Patina dressing. On this seed every painted window belongs to an Empty with dressing sills (12 rowhomes, 4-7 sills
each); the bank (2 window kinds) and `twin_a01` (5) have none.

**What shipped.** Zoo 1.145.0 (9218c79, `patches/patch_zoo_window_frame.py`): `arch.window_frame_parts`, an aluminium
frame ringing the opening on the pane's plane, 5 cm wide, 12.5 mm proud of the pane on each face, a mullion past a
1.2 m pane; `arch.window_sill_parts`, a 5 cm sill on the slab projecting 5 cm past the outdoor face, in the wall's
material. Not on a painted pane, not on a glass wall. 76 triangles a window (124 -> 200 at the genome's max corner);
the window's coincident-face census 4 pairs a corner, its `RESIDUE` row unchanged. Two defects found on the way, both
fixed before shipping: the first draft's sill ran to the pane's plane (census: the pane's bottom edge 1.5 mm off the
sill's top), and the frame's fixed 7 cm depth was thinner than the pane on a 0.6 m wall -- the depth is now derived
from the pane.

**The first build moved every framed window 2.5 cm off its slot.** Zoo centres a module on what it fits
(`build._recentre`), and the sill stands out of one face only: the bank's window GLB came back with its collider at
-0.175..0.125 instead of +-0.15, a step in the facade at both ends of every window. Caught by reading the package's
GLB, not by a gate. The sill is now left out of the fit (`fit_objects`, as a swung leaf is), and
`tests/test_window_frame.py` fails on that build. Its price is kept as `perf_shifted_*` (WATCH: draws median +2,
largest +13; p95 median +0.016 ms, largest +0.317 ms, floor 0.176 ms); its frames were not kept.

**Measured** on seed 9082 (`_scratch/bank_look_input/batch.json`), control `workspaces/linear-9082-ws` (Zoo 1.144.0,
the realism trial's subject) against `workspaces/frame-9082-ws` (the same batch and seed with Zoo pointed at the
change's clone through its `tools.local.json`; `_scratch/frame_chain.sh`, the shoot `shoot.py`):

- **The package:** both window kinds that are not painted panes and not glass carry the frame (one
  `metal_painted` surface a module, 24-32 triangles) and the sill (in the wall's surface, 104 -> 148 triangles); the
  slab's collider is +-0.15 m in depth again.
- **The frames** (`sheet_inspect.png`, `sheet_level.png`; before left, after right, full frame and a 2x centre crop;
  three new stations at the bank's south windows, world (-67.5, 5.25, 17.97) and (-52.5, 5.25, 17.97)): the window
  reads as a framed, mullioned window on a ledge where it read as a square of colour. Mean and median brightness move
  under 1% -- a frame and a sill are a small share of any frame's pixels; the sheets are the evidence. The vertical
  line beside the near window is in both columns: the joint between wall modules, not this change.
- **The price** (`tools/price_batch.py`, A / subject / A, `perf_frame_*`): **WATCH over 53 headings, draws median +2,
  largest +7 (floor 0); p95 median +0.052 ms, largest +0.432 ms against a floor of 0.279 ms.** The two headings past
  the floor are both `attacker_spawn_2`, at (-62, 1.6, 20.47), 2.5 m off the bank's south face: yaw 270, draws 1258 ->
  1262, p95 6.37/6.48 -> 6.86 ms, with the subject's own pass spread 1.381 ms against the controls' 0.33-0.56 ms; yaw
  0, draws 500 -> 503, p95 3.22/3.41 -> 3.65 ms. The draws are the frame's material on wall sides that had none -- the
  storefront's aluminium is the same surface, so a side with a storefront pays nothing. **The cheaper version** builds
  the frame in the wall's material: +0 draws, and the frame then reads only by its 12.5 mm of relief, as the reveal did.
  Not shipped; the aluminium is what makes it read.

**Unproven.** The walker's verdict. That the step was the only effect of the shift: the shifted build was not walked.
The twin's windows were not shot.

**Next in the shape work:** edges -- the parapet's cap is Patina's `edge_strip`, 10 cm across and 6 cm proud
(`zoo_keeper/core/dressing._COVER`), a hairline at 30 m; then nosings and corner bevels, junctions (baseboards,
crown), then the box props.
