## 0.105.0 - a shop sign's pack manifest travels beside its maps

**Roadmap 223.** Pixelcoat 0.62.0 letters a business's sign smooth, in Blue
Highway Condensed, and its pack asks for `linear` sampling and a mip chain.
A pixel pack asks for `nearest` and neither. This copied a dealt pack's
albedo and emissive to `signs/` beside its scene, but not its manifest, so
the maps alone could not say which kind they were. Level Factory 0.166.0's
export reads the manifest there and pins each map's import to match.

**Now.**
- `building_signs` records the pack's manifest, and `_sign_ext_lines` copies
  it beside the maps.
- No scene names it: it is a sibling for the export, not a resource.
- **The band's comment is true at last.** `SIGN_ASPECT = 6.0` said "width :
  height, matching the pack" while Pixelcoat drew a 4:1 cabinet, so every
  band's letters stood 1.5x too wide. Pixelcoat 0.62.0 draws 6:1. The
  number does not change.
- A `linear` pack's band material was already left at Godot's filtered
  default: only a `nearest` pack sets `texture_filter`. That is now
  asserted.

**Tests.** `tests/test_sign_manifest_travels.py`:
- the manifest is copied beside the maps;
- no scene names it;
- a smooth pack is not forced nearest.

On 0.104.0 the first fails. The other two pass on both: they assert what
was already so.

Suite: 732 passed (729 on 0.104.0).
