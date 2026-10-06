"""Zoo 1.78.0: a pack can ask for its texture's alpha to be BLENDED.

The chain-link fence's far fabric vanished (cold run 9183, item 188). The
fabric is about 25 % wire, and an alpha TEST at 0.5 keeps nothing once a
mip averages its wires and gaps. Rendered on cold run 9184's walk copy
(scratchpad probe, `fabric_variants.gd`), the candidates were:
- cut at 0.2: the far fabric turns into a solid dark wall;
- alpha hash: the whole run goes solid dark under GL Compatibility;
- a second, distant card: it cannot fix a long run seen along its length.
  Visibility ranges switch a whole node, and one run is one node, so its far
  end never hands over.
- THE SAME TEXTURE BLENDED: near, it is the same crisp wire; far, its mips
  average to the fabric's real coverage, a faint screen. It also fixes the
  run seen along its length, at no extra draw.

`skins.blends_its_texture(pack)` reads Pixelcoat's new hint, `alpha_mode:
"blend_texture"` (Pixelcoat 0.60.0). `materials._textured` then wires the
albedo's alpha straight to the shader's, renders BLENDED (the glTF exporter
writes alphaMode BLEND; Godot imports TRANSPARENCY_ALPHA) and draws both
sides. `is_see_through` is unchanged: that is glass, one opacity for the
whole surface.

    python patch_zoo_fabric_blends.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ZOO = ROOT / "zoo"

EDITS = {
    ZOO / "zoo_keeper/core/skins.py": [
        ('''def is_see_through(pack: dict | None) -> bool:
''',
         '''def blends_its_texture(pack: dict | None) -> bool:
    """True when a resolved pack asks for its ALBEDO's alpha to be blended,
    not tested (``import_hints.transparency.alpha_mode == "blend_texture"``,
    Pixelcoat 0.60.0). Glass blends one opacity across a surface
    (`is_see_through`); a cutout tests its alpha at 0.5 (`scissor`). A
    fabric too fine for a test -- chain link is about 25 % wire, so its mips
    fall under any cutoff that keeps it crisp near -- blends its own alpha
    instead (1.78.0). Pure, like `is_see_through`, so the material code and
    its tests read the hint one way."""
    trans = (pack or {}).get("transparency") or {}
    return trans.get("alpha_mode") == "blend_texture"


def is_see_through(pack: dict | None) -> bool:
'''),
    ],
    ZOO / "zoo_keeper/bpylayer/materials.py": [
        ('''        try:
            mat.use_backface_culling = False       # a card reads from both sides
        except Exception:
            pass
    elif skins.is_see_through(pack):
''',
         '''        try:
            mat.use_backface_culling = False       # a card reads from both sides
        except Exception:
            pass
    elif skins.blends_its_texture(pack):
        # THE TEXTURE'S OWN ALPHA, BLENDED (1.78.0, the chain-link fabric).
        # Linked straight to the shader, so the exporter writes alphaMode
        # BLEND with the albedo's alpha, and Godot draws it as alpha.
        try:
            tree.links.new(albedo.outputs["Alpha"], bsdf.inputs["Alpha"])
        except Exception:
            pass
        for _attr, _val in (("blend_method", "BLEND"),
                            ("surface_render_method", "BLENDED")):
            try:
                setattr(mat, _attr, _val)
            except Exception:
                pass
        try:
            mat.use_backface_culling = False       # a card reads from both sides
        except Exception:
            pass
    elif skins.is_see_through(pack):
'''),
    ],
    ZOO / "tests/test_chain_link_fence.py": [
        ('''def test_the_fabric_is_a_kind_the_skin_library_resolves():
''',
         '''def test_a_fabric_that_blends_its_texture_is_not_glass_and_not_a_cutout():
    """1.78.0: the far fabric vanished under an alpha test (cold run 9183);
    blended, its mips keep the fabric's coverage."""
    hint = lambda mode, opacity=1.0: {"transparency": {"alpha_mode": mode, "opacity": opacity}}
    assert skins.blends_its_texture(hint("blend_texture"))
    assert not skins.is_see_through(hint("blend_texture"))
    assert not skins.blends_its_texture(hint("scissor"))
    assert not skins.blends_its_texture(hint("blend", 0.6))
    assert skins.is_see_through(hint("blend", 0.6))
    assert not skins.blends_its_texture(None)


def test_the_material_code_acts_on_the_texture_blend():
    """The branch is Blender-bound, so read it as source, as
    `test_car_forms` does: it must ask `blends_its_texture` before the glass
    test, or a blended fabric would fall through to an opaque surface."""
    import os
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "zoo_keeper", "bpylayer", "materials.py"), encoding="utf-8").read()
    i_blend = src.index("elif skins.blends_its_texture(pack):")
    i_glass = src.index("elif skins.is_see_through(pack):")
    assert i_blend < i_glass
    assert '"surface_render_method", "BLENDED"' in src[i_blend:i_glass]


def test_the_fabric_is_a_kind_the_skin_library_resolves():
'''),
    ],
}


def main():
    staged = {}
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        crlf = data.count(b"\r\n")
        assert crlf in (0, data.count(b"\n")), f"{path}: mixed line endings"
        eol = "\r\n" if crlf else "\n"
        text = data.decode("utf-8")
        for old, new in pairs:
            old, new = old.replace("\n", eol), new.replace("\n", eol)
            n = text.count(old)
            assert n == 1, f"{path}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        staged[path] = text
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
