"""Lux 0.76.0: the sun is baked while the lightmap shows (factory roadmap 243; the walker's call of
2026-10-12 after `docs/findings/lux_tiers/`).

Anchored edits, each asserted once, nothing written until all of them matched:
  addons/lux/runtime/lux_lighting.gd   `_sun_shadows_wanted`; `apply` records what the preset and the
                                       tier want and calls `_apply_sun_mode`; `_sync_lightmaps` calls
                                       it too; `_apply_sun_mode` before `fixtures_powered`
  tools/sun_bake_selftest.gd           NEW (`lux_sun_baked/sun_bake_selftest.gd.txt`)
CHANGELOG and VERSION from `lux_sun_baked/CHANGELOG_0.76.0.md`; `--results-pending` leaves the RESULT_
keys to `--fill`. (The street-light shadow fade drafted as 0.76.0 earlier the same day was refuted and
never applied; `patches/patch_lux_street_shadow_fade.py` refuses to run.)

Read before it was written: `apply` (the sun's shadow from `preset.sun_shadows and
quality.allow_sun_shadows`), `ensure_sun` (a DirectionalLight3D at the engine's default bake mode),
`bind_lightmaps` (deferred from LuxRoot's ready, after the first apply), `_sync_lightmaps` (the power cut
and the baked-lighting switch hide the lightmap through it) and `set_baked_lighting` (a bake-mode change
at run time needs the light hidden and shown to pair again).

    python patches/patch_lux_sun_baked.py --results-pending
    godot --headless --path lux -s res://tools/sun_bake_selftest.gd
    python patches/patch_lux_sun_baked.py --fill
    LUX_ROOT=<copy> python patches/patch_lux_sun_baked.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LUX = pathlib.Path(os.environ.get("LUX_ROOT") or HERE.parent / "lux")
SRC = HERE / "lux_sun_baked"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SELFTEST": "result_selftest.txt", "RESULT_OTHERS": "result_others.txt"}
VERSION_WAS, VERSION = b"Lux 0.75.0", b"Lux 0.76.0"
CHANGELOG_HEAD = "# Changelog\n\n## [0.75.0] - a home's dome lights its room\n"
LIGHTING = "addons/lux/runtime/lux_lighting.gd"
TEST = "tools/sun_bake_selftest.gd"
SHA = {LIGHTING: "5649a821e0ed9855"}

VAR_OLD = "var sun: DirectionalLight3D\n"
VAR_NEW = ("var sun: DirectionalLight3D\n"
           "## What the preset and the tier want of the sun's shadow; `_apply_sun_mode`\n"
           "## decides whether it is drawn live (0.76.0).\n"
           "var _sun_shadows_wanted: bool = false\n")

APPLY_OLD = "\tsun.shadow_enabled = preset.sun_shadows and quality.allow_sun_shadows\n"
APPLY_NEW = ("\t# THE SUN IS BAKED WHILE THE LIGHTMAP SHOWS (0.76.0): `_apply_sun_mode`\n"
             "\t_sun_shadows_wanted = preset.sun_shadows and quality.allow_sun_shadows\n"
             "\t_apply_sun_mode()\n")

SYNC_OLD = ("func _sync_lightmaps() -> void:\n"
            "\tvar show: bool = _baked_on and _fixtures_powered\n"
            "\tfor pair in _lightmaps:\n"
            "\t\tvar lm: LightmapGI = pair[0]\n"
            "\t\tif is_instance_valid(lm):\n"
            "\t\t\tlm.light_data = pair[1] if show else null\n")
SYNC_NEW = (SYNC_OLD +
            "\t_apply_sun_mode()\n"
            "\n"
            "\n"
            "## THE SUN IS BAKED WHILE THE LIGHTMAP SHOWS (0.76.0, factory roadmap 243).\n"
            "## The sun was a dynamic light: the lightmap held only its bounce, and its\n"
            "## light and shadows were drawn live every frame. Measured in the factory\n"
            "## (`docs/findings/lux_tiers/`, Level Factory's 53 station headings, GL\n"
            "## Compatibility): its live shadows were 1,854 of a heading's 2,642 draws and\n"
            "## 3.56 ms of an 8.0 ms median p95. Baked with its shadows and drawn without\n"
            "## them, 788 draws and 4.42 ms, the look kept but for what moves -- it casts\n"
            "## and takes no sun shadow -- and shadows as soft as the lightmap's texels.\n"
            "## So: in the editor, where Level Factory bakes, the sun is STATIC with the\n"
            "## preset's shadows, so the bake traces them (a static sun baked unshadowed\n"
            "## bakes flat); at run time it is static and unshadowed while a lightmap\n"
            "## shows, and dynamic with the preset's shadows whenever none does -- no\n"
            "## lightmap, the power cut (daylight must not go out with the lamps), or\n"
            "## baked lighting switched off.\n"
            "func _apply_sun_mode() -> void:\n"
            "\tif sun == null or not is_instance_valid(sun):\n"
            "\t\treturn\n"
            "\tvar editor: bool = Engine.is_editor_hint()\n"
            "\tvar shown: bool = _baked_on and _fixtures_powered and not _lightmaps.is_empty()\n"
            "\tvar mode: Light3D.BakeMode = Light3D.BAKE_STATIC if editor or shown else Light3D.BAKE_DYNAMIC\n"
            "\tvar changed: bool = sun.light_bake_mode != mode\n"
            "\tsun.light_bake_mode = mode\n"
            "\tsun.shadow_enabled = _sun_shadows_wanted and (editor or not shown)\n"
            "\t# a bake mode changed at run time pairs again with the geometry only once\n"
            "\t# the light is hidden and shown (`set_baked_lighting`'s finding)\n"
            "\tif changed and not editor and sun.visible:\n"
            "\t\tsun.visible = false\n"
            "\t\tsun.visible = true\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def fill():
    assert (LUX / "VERSION").read_bytes().strip() == VERSION, (LUX / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LUX / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.76.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Lux 0.76.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LUX_ROOT"):
        sys.exit("refusing: --draft is for a LUX_ROOT copy, never the repo")
    assert (LUX / "VERSION").read_bytes().strip() == VERSION_WAS, (LUX / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.76.0.md")
    assert entry.startswith("## [0.76.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        for key in RESULTS if PENDING else ():
            left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    assert not (LUX / TEST).exists(), "already applied"
    p = LUX / LIGHTING
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[LIGHTING], (LIGHTING, "is not the file this patch read", got)
    eol = _eol(raw, LIGHTING)
    text = raw.decode("utf-8").replace("\r\n", "\n")
    text = _once(text, VAR_OLD, VAR_NEW, "the sun's variable")
    text = _once(text, APPLY_OLD, APPLY_NEW, "apply's sun shadow")
    text = _once(text, SYNC_OLD, SYNC_NEW, "_sync_lightmaps")
    test = _src("sun_bake_selftest.gd.txt")
    cl = LUX / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:160]
    cl_new = "# Changelog\n\n" + entry.rstrip("\n") + "\n\n" + cl_text[len("# Changelog\n\n"):]
    # every anchor matched: now write
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    (LUX / TEST).write_bytes(test.encode("utf-8"))
    cl.write_bytes(cl_new.replace("\n", cl_eol.decode()).encode("utf-8"))
    (LUX / "VERSION").write_bytes(VERSION)
    print("Lux 0.75.0 -> 0.76.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
