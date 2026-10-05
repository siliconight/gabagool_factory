"""Zoo 1.64.0: an Empty's window is painted -- lit, dark, curtained, barred.

Cold run 9150: at night the Empties read as a black mass outside the
streetlight pools, every window an unlit opaque pane. The walker's Bloodlines
comp asks for mixed windows with lights on to show life
(`docs/reference/EMPTIES_COMPS.md`, "LIT WINDOWS AT NIGHT"). Deli Counter
(>= 0.179.0) writes a `pane` state on each facade window slot; here the pane
is UV-mapped to that state's cell of one painted atlas, one `_Face` material,
glow from a separate emission image. See
`zoo_window_panes/CHANGELOG_1.64.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  zoo_keeper/core/window_panes.py   NEW: the atlas, its cells, its UVs
  zoo_keeper/bpylayer/materials.py  `make_pane_material`
  zoo_keeper/recipes/_arch.py       a facade window with a pane state wears it
  zoo_keeper/core/kit.py            `pane` in the name, the key and the module
  zoo_keeper/core/dna.py            `pane` onto the plan
Copies the test; CHANGELOG and VERSION.

    python patch_zoo_window_panes.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
ZOO = HERE.parent / "zoo"
SRC = HERE / "zoo_window_panes"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


MAT_ANCHOR = '''def _load_image(path, non_color=False):
'''
MAT_NEW = '''def make_pane_material(name, albedo, emission, strength, albedo_factor,
                       roughness=0.2):
    """A painted window (1.64.0): ``albedo`` is the pane as seen, dimmed by
    ``albedo_factor``; ``emission`` -- a SEPARATE image, black wherever no
    room light shows -- glows at ``strength``. One image could not do both:
    glow taken from the albedo lights boarded plywood and curtain fabric.

    Name it ``_Face`` (Lux's emissive binder matches the suffix) so the power
    cut darkens every lit window. Nearest filter, clamped: an atlas cell never
    bleeds into its neighbour. A strength of 0 links no emission at all, for
    the reason `make_backlit_material` gives."""
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Roughness"].default_value = float(roughness)
    bsdf.inputs["Metallic"].default_value = 0.0

    def tex(image):
        node = tree.nodes.new("ShaderNodeTexImage")
        node.image = image
        node.interpolation = "Closest"
        node.extension = "EXTEND"
        return node

    base = tex(albedo)
    f = float(albedo_factor)
    tree.links.new(_tint_multiply(tree, base.outputs["Color"], (f, f, f), name),
                   bsdf.inputs["Base Color"])
    if float(strength) > 0.0:
        glow = tex(emission)
        sock = "Emission Color" if "Emission Color" in bsdf.inputs else "Emission"
        tree.links.new(glow.outputs["Color"], bsdf.inputs[sock])
        bsdf.inputs["Emission Strength"].default_value = float(strength)
    return mat


def _load_image(path, non_color=False):
'''

ARCH_IMPORT_OLD = '''from ..core import arch, partnames
'''
ARCH_IMPORT_NEW = '''from ..core import arch, partnames, window_panes
'''

PANE_OLD = '''        bm = geometry.new_bm()
        geometry.add_box(bm, (cx, 0.0, cz),
                         (pane_w * 0.98, d * 0.15, pane_h * 0.98))
        pane = geometry.bm_to_object(
            bm, f"{root}_Glass", collection, bevel=0.0, texel=1.0,
            rng=rng, wear=wear * 0.25)
        # Enterable windows glaze see-through "glass"; facade-shell windows
        # (hollow building) glaze opaque "glass_facade" via plan.glazing_kind.
        glazing_kind = plan.get("glazing_kind", "glass")
        glass = materials.make_material(
            f"M_Window_{glazing_kind}",
            plan.get("glass_color", [0.55, 0.66, 0.72]), glazing_kind)
        materials.assign([pane], glass)
        objs.append(pane)
'''
PANE_NEW = '''        bm = geometry.new_bm()
        geometry.add_box(bm, (cx, 0.0, cz),
                         (pane_w * 0.98, d * 0.15, pane_h * 0.98))
        glazing_kind = plan.get("glazing_kind", "glass")
        state = plan.get("pane")
        if glazing_kind == "glass_facade" and state in window_panes.STATES:
            # A PAINTED PANE (1.64.0): the street face (+Y, outdoors) shows
            # its state's cell of the shared atlas; every other face takes a
            # point of the frame paint. Own UVs, so `finish=False` -- the
            # cube projection would overwrite them -- and a white COLOR_0,
            # which Level Factory's import multiplies by.
            u0, v0, u1, v1 = window_panes.uv_rect(state)
            frame = window_panes.uv_rect("lit")[0] * 0.25
            uv = bm.loops.layers.uv.new("UVMap")
            hx, hz = pane_w * 0.49, pane_h * 0.49
            bm.normal_update()
            for face in bm.faces:
                for loop in face.loops:
                    if face.normal.y > 0.9:
                        co = loop.vert.co
                        # seen from +Y looking at -Y, +X is the viewer's
                        # LEFT: u runs from the +X edge, or the cell mirrors
                        loop[uv].uv = (u0 + (u1 - u0) * ((cx + hx) - co.x) / (2 * hx),
                                       v0 + (v1 - v0) * (co.z - (cz - hz)) / (2 * hz))
                    else:
                        loop[uv].uv = (frame, frame)
            geometry.wear_colors(bm, streams.stream("pane"), 0.0)
            pane = geometry.bm_to_object(bm, f"{root}_Glass", collection,
                                         finish=False, bevel=0.0)
            albedo, emission = window_panes.atlas()
            pane.data.materials.append(materials.make_pane_material(
                "M_Window_pane_Face",
                materials.image_from_png("window_pane_albedo", albedo.png()),
                materials.image_from_png("window_pane_emission", emission.png()),
                window_panes.EMISSION, window_panes.ALBEDO))
            objs.append(pane)
        else:
            pane = geometry.bm_to_object(
                bm, f"{root}_Glass", collection, bevel=0.0, texel=1.0,
                rng=rng, wear=wear * 0.25)
            # Enterable windows glaze see-through "glass"; facade-shell windows
            # (hollow building) glaze opaque "glass_facade" via plan.glazing_kind.
            glass = materials.make_material(
                f"M_Window_{glazing_kind}",
                plan.get("glass_color", [0.55, 0.66, 0.72]), glazing_kind)
            materials.assign([pane], glass)
            objs.append(pane)
'''

SIG_OLD = '''                material_in: str = None) -> str:
    """The exact filename stem Deli Counter's resolver looks for:'''
SIG_NEW = '''                material_in: str = None, pane: str = None) -> str:
    """The exact filename stem Deli Counter's resolver looks for:'''

STEM_OLD = '''    if material_in:
        base += f"_i{material_in}"
'''
STEM_NEW = '''    if material_in:
        base += f"_i{material_in}"
    # A PAINTED PANE'S STATE (1.64.0): `_p<state>`, after the room face. Two
    # facade windows of one size in different states are different modules.
    # Deli Counter's `themed_tscn.module_stem` is the mirror.
    if pane:
        base += f"_p{pane}"
'''

INNER_OLD = '''        inner = (str(s["material_in"]) if typ in INNER_FACE_ROLES and s.get("material_in")
                 in skins.KNOWN_KINDS else None)
'''
INNER_NEW = '''        inner = (str(s["material_in"]) if typ in INNER_FACE_ROLES and s.get("material_in")
                 in skins.KNOWN_KINDS else None)
        # A FACADE WINDOW'S PAINTED STATE (1.64.0, Deli Counter >= 0.179.0)
        from zoo_keeper.core import window_panes as _panes
        pane = (str(s["pane"]) if typ == "window" and s.get("glazing") == "facade"
                and s.get("pane") in _panes.STATES else None)
'''

CALL_OLD = '''                               budget_tiles=budget, material_in=inner, **dress)
            if is_deferred:'''
CALL_NEW = '''                               budget_tiles=budget, material_in=inner, pane=pane,
                               **dress)
            if is_deferred:'''

KEY_OLD = '''                   _opening_key(fit.get("openings")), budget, inner)
'''
KEY_NEW = '''                   _opening_key(fit.get("openings")), budget, inner, pane)
'''

MOD_OLD = '''                    "material_in": inner,
                    "count": 0,
'''
MOD_NEW = '''                    "material_in": inner,
                    "pane": pane,
                    "count": 0,
'''

DNA_OLD = '''    if module.get("material_in"):
        plan["material_in"] = str(module["material_in"])
'''
DNA_NEW = '''    if module.get("material_in"):
        plan["material_in"] = str(module["material_in"])
    # A facade window's painted state (1.64.0): `_arch.build_slab` maps the
    # pane to its cell of `window_panes`' atlas
    if module.get("pane"):
        plan["pane"] = str(module["pane"])
'''


def main():
    assert (ZOO / "VERSION").read_text(encoding="utf-8").strip() == "1.63.0"
    core = ZOO / "zoo_keeper" / "core"
    assert not (core / "window_panes.py").exists()
    shutil.copyfile(SRC / "window_panes.py", core / "window_panes.py")
    _edit(ZOO / "zoo_keeper" / "bpylayer" / "materials.py", [(MAT_ANCHOR, MAT_NEW)])
    _edit(ZOO / "zoo_keeper" / "recipes" / "_arch.py",
          [(ARCH_IMPORT_OLD, ARCH_IMPORT_NEW), (PANE_OLD, PANE_NEW)])
    _edit(core / "kit.py", [(SIG_OLD, SIG_NEW), (STEM_OLD, STEM_NEW), (INNER_OLD, INNER_NEW),
                            (CALL_OLD, CALL_NEW), (KEY_OLD, KEY_NEW), (MOD_OLD, MOD_NEW)])
    _edit(core / "dna.py", [(DNA_OLD, DNA_NEW)])
    shutil.copyfile(SRC / "test_window_panes.py", ZOO / "tests" / "test_window_panes.py")
    ch = ZOO / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_1.64.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (ZOO / "VERSION").write_text("1.64.0", encoding="utf-8", newline="\n")
    print("applied Zoo 1.64.0")


if __name__ == "__main__":
    main()
