"""Lux 0.71.0: street lamps are dark by day. The walker, 2026-10-09: "street
lamps aren't usually on during the day".

A street pole and a wall pack -- on a home, its porch light -- switch on a
photocell in the world. A preset now says whether its sky lights them
(`LuxPreset.street_lamps_lit`; the four day presets say no), the loader marks
those two rows `dusk_to_dawn` (`LuxLightRig`), and applying a preset hides
every such rig and darkens its lens (`LuxStreetlightRig.set_lamps_lit`, called
by `LuxLighting` on apply and on registration). LuxRoot applies its preset in
the editor too, so the export, the editor's bake and a re-bake under another
slot all see it: a day level bakes no street lamp.

Anchored edits, every anchor once, nothing written until all matched:
- `resources/lux_preset.gd`: `street_lamps_lit` after `bake_room_fill`;
- `resources/lux_light_rig.gd`: `dusk_to_dawn` after `preset_scaled`;
- `runtime/lux_light_loader.gd`: the `streetlight` and `wall_pack` rows set it;
- `runtime/rigs/lux_streetlight_rig.gd`: the switch (`lux_dusk_to_dawn/
  rig_funcs.gd.txt`), and a dark pole binds no failing lens;
- `runtime/lux_lighting.gd`: the preset's value, handed to each rig;
- `runtime/lux_root.gd`: `_lerp_preset` snaps it at a blend's middle (the
  function is exhaustive by contract);
- presets `delco_summer_afternoon`, `delco_arcade`, `sof_pc2000`,
  `heavy_rain` (an overcast DAY): `street_lamps_lit = false`.
New: `tools/street_lamps_selftest.gd`. CHANGELOG and VERSION from
`lux_dusk_to_dawn/CHANGELOG_0.71.0.md`.

    python patch_lux_dusk_to_dawn.py
    LUX_ROOT=<copy> python patch_lux_dusk_to_dawn.py [--draft]
"""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LUX = pathlib.Path(os.environ.get("LUX_ROOT") or HERE.parent / "lux")
SRC = HERE / "lux_dusk_to_dawn"
DRAFT = "--draft" in sys.argv
A = "addons/lux/"

PRESET_FIELD = (
    "\n"
    "## THE DUSK-TO-DAWN FIXTURES (0.71.0). The walker, 2026-10-09: \"street lamps\n"
    "## aren't usually on during the day\". A street pole and a wall pack -- on a\n"
    "## home, its porch light -- switch on a photocell in the world: when the sky\n"
    "## goes dark the lamp comes on. A DAY preset sets this false, and both stand\n"
    "## dark with their lens (`LuxStreetlightRig.set_lamps_lit`); dusk and night\n"
    "## leave it true. Everything else a level lights keeps its light by day: a\n"
    "## fuel canopy, a lit sign, a store's glass, a payphone, every room. A level\n"
    "## never changes its time of day (LEVEL_STANDARD section 17), and this is\n"
    "## read wherever a preset is applied -- the export, the editor's bake, a\n"
    "## re-bake under another slot -- so a day level bakes no street lamp.\n"
    "@export var street_lamps_lit: bool = true\n"
)
RIG_FIELD = (
    "## A DUSK-TO-DAWN FIXTURE (0.71.0): it lights only while the preset in force\n"
    "## has `street_lamps_lit` (LuxPreset). The loader's `streetlight` and\n"
    "## `wall_pack` rows set it; a rig that is not one ignores the switch.\n"
    "@export var dusk_to_dawn: bool = false\n"
)
RIG_VARS = (
    "\n"
    "## THE DUSK-TO-DAWN SWITCH (0.71.0). A rig whose resource is `dusk_to_dawn`\n"
    "## goes dark under a preset with `street_lamps_lit` false: the rig hidden, so\n"
    "## its lamps neither draw nor bake, and the lens nearest each lamp given a\n"
    "## dark copy of its material, so a dark lamp does not glow. LuxLighting calls\n"
    "## `set_lamps_lit` when a preset is applied and when a lamp registers.\n"
    "var _lamps_lit: bool = true\n"
    "## [mesh, surface, the override it had]\n"
    "var _dark_lenses: Array = []\n"
)
LIGHTING_FUNC = (
    "\n\n"
    "## The preset's `street_lamps_lit` (0.71.0), handed to the lamp's rig. Duck\n"
    "## typed: a rig class without the switch is left alone, and the rig itself\n"
    "## decides by its resource whether it is a dusk-to-dawn fixture.\n"
    "func _switch_dusk_to_dawn(light: Node) -> void:\n"
    "\tif not is_instance_valid(light):\n"
    "\t\treturn\n"
    "\tvar rig_node := light.get_parent()\n"
    "\tif rig_node != null and rig_node.has_method(&\"set_lamps_lit\"):\n"
    "\t\trig_node.call(&\"set_lamps_lit\", _street_lamps_lit)\n"
)


def edits():
    rig_funcs = (SRC / "rig_funcs.gd.txt").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert rig_funcs.startswith("## Light or darken a dusk-to-dawn rig (0.71.0)")
    return {
        A + "resources/lux_preset.gd": [
            ("@export_range(0.0, 0.2, 0.005) var bake_room_fill: float = 0.025\n",
             "@export_range(0.0, 0.2, 0.005) var bake_room_fill: float = 0.025\n" + PRESET_FIELD),
        ],
        A + "resources/lux_light_rig.gd": [
            ("@export var preset_scaled: bool = false\n",
             "@export var preset_scaled: bool = false\n" + RIG_FIELD),
        ],
        A + "runtime/lux_light_loader.gd": [
            ('\t\t\trs.rig_name = &"Streetlight (baked)"\n',
             '\t\t\trs.rig_name = &"Streetlight (baked)"\n'
             "\t\t\t# a photocell's lamp: dark under a day preset (0.71.0)\n"
             "\t\t\trs.dusk_to_dawn = true\n"),
            ('\t\t\trw.rig_name = &"Wall Pack (baked)"\n',
             '\t\t\trw.rig_name = &"Wall Pack (baked)"\n'
             "\t\t\t# a photocell's lamp -- on a home, the porch light: dark by day (0.71.0)\n"
             "\t\t\trw.dusk_to_dawn = true\n"),
        ],
        A + "runtime/rigs/lux_streetlight_rig.gd": [
            ("var _lenses: Array = []\n", "var _lenses: Array = []\n" + RIG_VARS),
            ("func _bind_lenses() -> void:\n"
             "\t_lenses.clear()\n"
             "\tif rig == null or rig.failing_kind == LuxFailing.NONE or rig.bake_mode == 1:\n"
             "\t\treturn\n",
             "func _bind_lenses() -> void:\n"
             "\t_lenses.clear()\n"
             "\tif rig == null or rig.failing_kind == LuxFailing.NONE or rig.bake_mode == 1:\n"
             "\t\treturn\n"
             "\t# a dark dusk-to-dawn pole binds no failing lens; it binds when it relights\n"
             "\tif not _lamps_lit:\n"
             "\t\treturn\n"),
            ("func _rebuild() -> void:\n", rig_funcs + "func _rebuild() -> void:\n"),
        ],
        A + "runtime/lux_lighting.gd": [
            ("\tif preset != null:\n"
             "\t\t_fluorescent_scale = preset.fluorescent_energy_scale\n"
             "\t\tfor n in _registered:\n"
             "\t\t\t_scale_practical(n)\n",
             "\tif preset != null:\n"
             "\t\t_fluorescent_scale = preset.fluorescent_energy_scale\n"
             "\t\t_street_lamps_lit = preset.street_lamps_lit\n"
             "\t\tfor n in _registered:\n"
             "\t\t\t_scale_practical(n)\n"
             "\t\t\t_switch_dusk_to_dawn(n)\n"),
            ("var _fluorescent_scale: float = 1.0\n",
             "var _fluorescent_scale: float = 1.0\n"
             "## The preset's `street_lamps_lit` (0.71.0); true until a preset says.\n"
             "var _street_lamps_lit: bool = true\n"),
            ("\tif rig_node is LuxFluorescentRig:\n"
             "\t\t(rig_node as LuxFluorescentRig).set_energy_scale(_fluorescent_scale)\n",
             "\tif rig_node is LuxFluorescentRig:\n"
             "\t\t(rig_node as LuxFluorescentRig).set_energy_scale(_fluorescent_scale)\n"
             + LIGHTING_FUNC),
            ("\t\t_registered.append(light)\n"
             "\t\t_scale_practical(light)\n",
             "\t\t_registered.append(light)\n"
             "\t\t_scale_practical(light)\n"
             "\t\t_switch_dusk_to_dawn(light)\n"),
        ],
        A + "runtime/lux_root.gd": [
            ("\tp.fluorescent_energy_scale = lerpf(a.fluorescent_energy_scale, b.fluorescent_energy_scale, k)\n",
             "\tp.fluorescent_energy_scale = lerpf(a.fluorescent_energy_scale, b.fluorescent_energy_scale, k)\n"
             "\t# a lamp on a photocell snaps with the preset it blends toward (0.71.0)\n"
             "\tp.street_lamps_lit = b.street_lamps_lit if k >= 0.5 else a.street_lamps_lit\n"),
        ],
        **{A + "presets/%s.tres" % p: [
            ('[resource]\nscript = ExtResource("1_preset")\n',
             '[resource]\nscript = ExtResource("1_preset")\nstreet_lamps_lit = false\n'),
        ] for p in ("delco_summer_afternoon", "delco_arcade", "sof_pc2000", "heavy_rain")},
    }


def main():
    if DRAFT and not os.environ.get("LUX_ROOT"):
        sys.exit("refusing: --draft is for a LUX_ROOT copy, never the repo")
    v = (LUX / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Lux 0.70.0", v
    entry = (SRC / "CHANGELOG_0.71.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert DRAFT or "RESULT_" not in entry, "the changelog still carries an unfilled result"
    staged = {}
    for rel, pairs in edits().items():
        p = LUX / rel
        d = p.read_bytes()
        assert b"\r\n" not in d, (rel, "has CRLF; this patch writes LF files")
        t = d.decode("utf-8")
        assert "street_lamps_lit" not in t and "dusk_to_dawn" not in t, (rel, "already applied")
        for old, new in pairs:
            n = t.count(old)
            assert n == 1, (rel, n, old[:70])
            t = t.replace(old, new)
        staged[p] = t.encode("utf-8")
    test = LUX / "tools" / "street_lamps_selftest.gd"
    assert not test.exists(), test
    cl = LUX / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## [0.71.0]" not in d
    head = b"# Changelog\n\n"
    assert d.startswith(head)
    # every anchor matched: now write
    for p, raw in staged.items():
        p.write_bytes(raw)
    test.write_bytes((SRC / "street_lamps_selftest.gd").read_bytes().replace(b"\r\n", b"\n"))
    cl.write_bytes(head + entry.encode("utf-8") + d[len(head):])
    (LUX / "VERSION").write_bytes(b"Lux 0.71.0")
    print("Lux 0.70.0 -> 0.71.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
