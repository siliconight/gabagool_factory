# Realism trial, step 1: textures sampled linear (roadmap 324)

The walker, 2026-10-28: "how would we make our assets look more realistic? less low poly geometry? Without taking a
huge hit on performance?", and the target, "the look of Xbox 360 Games like Halo 3 and Gears of War ... we don't have
to make it look like Runescape either". Then: "yes build seed 9082 with linear filtering".

**What was wrong.** Every Pixelcoat material pack (118 in `pixelcoat/build`) asked its consumer for `nearest`
sampling -- the retro look's, kept after realism replaced it -- and Zoo's pack material hardcoded `Closest` whatever a
pack asked (`materials._textured`; the sign path had honoured the hint since Zoo 1.94.0). With 53 of the 118 packs at
128 px and 54 at 256, that is what read as blocky up close.

**What shipped.** Zoo 1.144.0 (7841864): the pack material samples as the pack asks. Pixelcoat 0.64.0 (59628f2): a
material pack asks for `linear`, with the mip chain every pack already asked for; signs' pixel lettering and decals
unchanged. Changing either alone would have changed nothing -- Zoo's knob was dead until both moved.

**Measured** on seed 9082's bank (`bank_block_001`, the walker's batch `_scratch/bank_look_input/batch.json`), the
control `workspaces/stair-check-0264-ws` (built 2026-10-28 14:44, nearest) against `workspaces/linear-9082-ws` (the
same batch and seed on Zoo 1.144.0, Pixelcoat 0.64.0; `linear_chain.sh` in `_scratch`, the shoot `linear_shoot.py`):

- **The package**, its GLBs' glTF samplers (mag/min filter): control 139 NEAREST/NEAREST + 14 LINEAR/LINEAR_MIPMAP_LINEAR;
  subject 146 LINEAR/LINEAR_MIPMAP_LINEAR + 7 NEAREST. The change reached the package.
- **The frames** (`frames/`, seven given stations and the derived ones, in the level's light and under
  `look_shots --inspect studio`): mean and median brightness move under 1% everywhere -- sampling does not change how
  bright a surface is, so brightness could not have shown it. Edge energy (standard deviation of a 3x3 Laplacian over
  the whole frame) falls on the close and interior views, studio light: vault wall -35.1%, vault -33.6%, vault_west
  -29.5%, lobby_east -21.1%, lobby_floor_close -15.9%, objective -40.5%, spawn -42.9%; the orthographic elevations,
  where a texture is already sampled from its mips, -2.6% to -4.9%, the near-null. In the level's own light the same
  views fall 6-22% and the elevations move under 1%. `sheet.py` draws `sheet_inspect.png` and `sheet_level.png`,
  nearest left and linear right, full frame and a 2x centre crop. The rain streaks on the spawn wall differ between the
  two because the rain is at a different moment, not because of sampling.
- **The price** (`tools/price_batch.py`, A / subject / A): the first run (`perf_linear_*`) read draws +0 and a floor
  of 4.045 ms -- the controls disagreed past the 1.0 ms the verdict trusts, a WATCH saying re-price; something else may
  have been running. Re-priced with nothing else running (`perf_linear2_*`): **PASS over 53 headings, draws +0 (floor 0),
  p95 median -0.007 ms, largest +0.187 ms against a floor of 0.549 ms.** Both reports kept.

**What it did and did not do.** It removes the retro noise -- plaster and concrete lose their salt-and-pepper speckle,
the tile floor and the panelling read as surfaces rather than grids. It does not add detail: at 128-256 px many
surfaces now read smooth and soft up close. The trial's next steps are what add the target's look: normal maps for
the 100 packs that carry none (18 of 118 do), then bevels and wear in vertex colour on one building family and one
prop family, each priced the same way.

**Unproven.** That the walker reads it as better: the frames are sent, the walk copy is
`workspaces/linear-9082-ws/.level_factory/preview/bank_block_001_walk`.
