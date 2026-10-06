"""Zoo 1.78.0: VERSION and the CHANGELOG entry for `patch_zoo_fabric_blends.py`.

    python patch_zoo_fabric_release.py
"""
import pathlib

ZOO = pathlib.Path(__file__).resolve().parent.parent / "zoo"

ENTRY = '''## [1.78.0] - a pack can blend its texture's alpha: the fence's far fabric

**The chain-link fabric vanished at distance** (cold run 9183, roadmap 188).
It is about a quarter wire, and an alpha TEST at 0.5 keeps nothing once a mip
averages wire and gap.

**Four fixes, rendered on cold run 9184's walk copy** from an alley 20 m away
and along a 16.8 m run:
- cut at 0.2: the far fabric turns into a solid dark wall;
- alpha hash: the whole run goes solid dark under GL Compatibility;
- a second, distant card: the far end of a run seen along its length still
  goes bare, because a visibility range switches a whole node and one run is
  one node;
- **the same texture, BLENDED:** the same crisp wire near, and a faint
  screen far, because its mips average to the fabric's real coverage. It
  costs no extra draw.

**`skins.blends_its_texture(pack)`** reads Pixelcoat 0.60.0's
`alpha_mode: "blend_texture"`. `materials._textured` then:
- wires the albedo's alpha straight to the shader's;
- renders BLENDED, so the exporter writes alphaMode BLEND and Godot imports
  the material as alpha;
- draws both sides.

`is_see_through`, glass's one opacity across a surface, is unchanged.

**Built:** the default 9 m fence, against a library carrying the new pack,
exports `M_Skin_chain_link_delco_1997` as alphaMode `BLEND`, double-sided. The
steel stays `OPAQUE`. Up close the frame is the same crisp chain link.

**Tests** (`tests/test_chain_link_fence.py`):
- `test_a_fabric_that_blends_its_texture_is_not_glass_and_not_a_cutout`;
- `test_the_material_code_acts_on_the_texture_blend`, which reads the
  Blender-bound branch as source and requires it before the glass test.
- Both fail on 1.77.0.

**Suite:** 3,340 passed, 382 skipped, 1 xfailed: 1.77.0's 3,338 and these 2.

'''


def main():
    version = ZOO / "VERSION"
    changelog = ZOO / "CHANGELOG.md"
    v = version.read_bytes()
    assert v == b"1.77.0", v
    c = changelog.read_bytes()
    assert b"\r\n" not in c
    assert c.startswith(b"## [1.77.0] - "), c[:60]
    version.write_bytes(b"1.78.0")
    changelog.write_bytes(ENTRY.encode("utf-8") + c)
    print("Zoo 1.78.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
