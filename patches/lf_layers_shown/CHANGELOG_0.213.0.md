## [0.213.0] - The output layers, shown: the light apart from the art

**The walker, 2026-10-15** (the factory's roadmap 257): "I want Level Factory to clearly show the output layers
calling out how lighting/render is separate from art ... I thought we did the work to make that another step in
the output layers?" The work was done -- 0.35.0 made the light a layer of its own (`LAYER_LIGHT` is `lux_apply`
alone; `--unlit` declines it; the fixtures stay in the art) and 0.36.0 added `export --mode art-unlit` -- and the
package recorded it (`LF_MANIFEST.json`, `output_layers.json`: `["art", "gameplay", "light"]`). Nothing a reader
meets first said so, each read off the files at 0.212.0 and cold run 9312's package: the README's Output layers
section described a Graybox base and two layers, Art and Gameplay, with Lux inside `--art`, and named neither
`light`, `--unlit` nor `art-unlit`; `output_layers.json`'s own label read `graybox+art+gameplay` of a package
carrying the light, because `export.py` spelled it from `("art", "gameplay")` while `planner.label_for_layers`
spelled `graybox+art+light+gameplay` for the same set; `HANDOFF.md` said nothing about layers; the export's log
printed no layers line; `docs/RENDER_PASS_SPLIT.md` still opened "Not implemented".

- **`output_layers_record(layers)`:** `output_layers.json` with its label spelled by `planner.label_for_layers`
  and nowhere else. A package carrying the light now says `graybox+art+light+gameplay` of itself.
- **`handoff_layers_text(layers, mode)`:** HANDOFF.md's last paragraph -- what this package is made of, layer by
  layer (the fixtures named in the art, with their `LuxEmit` markers), and that the light is Lux's result, a
  layer apart from the art: carried here and exportable without as `art-unlit`; or exported `art-unlit`, light
  it yourself; or absent.
- **The export's log:** `[export] layers: art, gameplay, light (graybox+art+light+gameplay); the light is Lux's
  result, a layer apart from the art`.
- **README, Output layers:** three independent layers, Art, Light and Gameplay; the run table gains
  `--art --unlit` and `export --mode art-unlit`; a Light bullet says what the layer is, what `--art` includes,
  what `--unlit` and `art-unlit` leave out, and that the fixtures stay in Art as a contract another lighting
  system reads.
- **`docs/RENDER_PASS_SPLIT.md`:** marked built, the other way round from its proposal -- a layer a run
  declines (`--unlit`), not one it adds (`--render`).
- **`tests/unit/test_layers_shown.py`:** one spelling of the label; the HANDOFF paragraph in the three cases;
  the call sites; the README and the design doc. All four fail on 0.212.0.

A doc-and-label change, no geometry: two files of a package move, `output_layers.json` and `HANDOFF.md`, read in
the factory's cold-run record.

**Suite:** exit 0, 2,447 by the progress tally (2,432 passed, 14 skipped, 1 xfail), 447 s: 0.212.0's 2,427 passed, the four new tests, and the sibling-locator guard's case over the new file; the 14 skipped are the real-tool smoke, as before
