## [0.210.0] - a rowhome Empty's roof is tar

**The walker's call of 2026-10-12** ("tar now, coating later"; factory roadmap 240's roofscape,
`docs/reference/ROWHOUSE_ROOFS.md` in the factory). The twelve rowhome Empties
(`presets.EMPTY_ROWHOMES`) were roofed in `concrete` under a comment calling the roof "flat tar,
silver-coated"; neither had a source, and in the delco themes `concrete` skinned them in
`concrete_delco` (under `street`, `cinderblock_delco`: a block wall with mortar lines, on a roof). A
rowhouse roof is a membrane over a wood deck, built-up or modified bitumen -- the skin kind `tar`, and
what Zoo's roof already wears in the delco themes, so a row's Empties now match its other roofs.
"Silver" is the colour of an aluminum roof coating over that membrane; how many 1990s Philadelphia
roofs carried one has no source yet, and the walker held it until one is found.

- **`empty_rowhome`**: `roof_material` "concrete" -> "tar", the comment saying why. The twelve
  `specs/gs_empty_rowhome_*.json` carry it (`test_empties` holds each to the preset's own output).
- **`material_kind.KIND_BY_MATERIAL`**: a `tar` row. Until now only `asphalt`, a forecourt's pad, named
  the kind, and a spec saying `tar` reached the slot manifest with a printed "unmapped" warning.
- **`test_material_kind._spec_material_ids`** reads `roof_material`: it read none, so a misspelt roof
  material reached the build unchecked (found tracing the roof slot's name through Zoo and Pixelcoat).
- **`test_empty_roof`** asks for `tar`; it fails on 0.209.1.

**Rebuilt:** The twelve rebuilt, then the library (`build.py --all`, 146 shells in 434 s; the freshness rule marks every shell older than `presets.py`): each Empty's roof slot reads `tar`, 12 of 12, and the tracked manifests moved only their build time (146) and the twelve's spec hash. A roof slot's style moved 4 -> 1: a style is the material's place in the palette, `tar` is in none, and the number names a module family and shapes nothing -- Zoo's recipes read none. `build_freshness.py` up to date

**Suite:** 1,398 passed, 2 skipped, before and after the rebuild; `test_empty_roof` fails on 0.209.1, on the roof slot's material
