"""Level Factory 0.164.0: the sky is in the bake. The walker, 2026-10-09: "yes
bake the sky in".

`light_bake.BAKE_TSCN`'s `LightmapGI` takes `environment_mode = 1` (the
scene's environment, LuxRoot's WorldEnvironment) in place of 0.131.0's `0`
(none). Measured first by re-baking cold run 9214's level at four slots
(`docs/findings/lighting_spec_vs_lux/`).

Anchored edits, every anchor once, nothing written until all matched:
- `packages/exporting/light_bake.py`: the comment above `BAKE_TSCN` and its
  `environment_mode` line;
- `tests/unit/test_light_bake.py`: `test_the_bake_takes_the_sky`, after the
  bake scene's own test.
CHANGELOG and VERSION from `lf_bake_sky/CHANGELOG_0.164.0.md`.

    python patch_lf_bake_sky.py
    LF_ROOT=<copy> python patch_lf_bake_sky.py [--draft]
"""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_bake_sky"
DRAFT = "--draft" in sys.argv

BAKE_OLD = (
    "BAKE_TSCN = \"\"\"[gd_scene load_steps=2 format=3]\n"
)
BAKE_NEW = (
    "#: THE SKY IS IN THE BAKE (0.164.0), the walker's call on 2026-10-09: \"yes\n"
    "#: bake the sky in\". `environment_mode = 1` gathers the scene's environment\n"
    "#: -- the WorldEnvironment LuxRoot builds, in the editor too, since it is\n"
    "#: `@tool` -- wherever the sky can reach. 0.131.0 shipped `0`, no sky, with\n"
    "#: no reason recorded, and a lightmapped surface takes no ambient at run\n"
    "#: time, so no baked surface had ever received sky light. Measured by\n"
    "#: re-baking cold run 9214's level slot by slot\n"
    "#: (`docs/findings/lighting_spec_vs_lux/` at the factory root): a clear\n"
    "#: afternoon's street cameras +15.1 and +21.4, shade from near black to\n"
    "#: daylight; Heavy Rain +0.3 to +2.3 and Blue Hour +0.5 to +3.7 outside;\n"
    "#: Delco Night two outer facades +3.3 and +4.4, the rest 0.2 or less; every\n"
    "#: room 1.2 or less at every slot, so a sealed room takes none. The bake\n"
    "#: time did not move, and at run time it costs nothing: the light lives in\n"
    "#: the lightmap. The root's `tools/lux_rebake.py --bake-environment none`\n"
    "#: bakes as before, and reads this line, so it stays one literal line.\n"
    + BAKE_OLD
)
ENV_OLD = (
    "max_texture_size = {max_texture}\n"
    "environment_mode = 0\n"
    "\"\"\"\n"
)
ENV_NEW = (
    "max_texture_size = {max_texture}\n"
    "environment_mode = 1\n"
    "\"\"\"\n"
)
TEST_OLD = (
    "def test_the_bake_scene_holds_the_presentation_and_one_lightmap():\n"
    "    t = LB.bake_scene_text()\n"
    "    assert 'path=\"res://presentation/lux.applied.tscn\"' in t\n"
    "    assert t.count('type=\"LightmapGI\"') == 1 and \"quality = 0\" in t and \"bounces = 2\" in t\n"
)
TEST_NEW = (
    TEST_OLD
    + "\n"
    "\n"
    "def test_the_bake_takes_the_sky():\n"
    "    \"\"\"FAILS ON 0.163.1. The walker, 2026-10-09: \"yes bake the sky in\". 0.131.0\n"
    "    to 0.163.1 baked with `environment_mode = 0`, no sky, and a lightmapped\n"
    "    surface takes no ambient at run time, so shade on a clear afternoon came\n"
    "    out near black (`docs/findings/lighting_spec_vs_lux/` at the factory\n"
    "    root). 1 is the scene's environment. One literal line: the root's\n"
    "    `tools/lux_rebake.py --bake-environment` rewrites it by pattern.\"\"\"\n"
    "    t = LB.bake_scene_text()\n"
    "    assert t.count(\"environment_mode = \") == 1, t\n"
    "    assert \"environment_mode = 1\\n\" in t, t\n"
)

EDITS = {
    "packages/exporting/light_bake.py": [(BAKE_OLD, BAKE_NEW), (ENV_OLD, ENV_NEW)],
    "tests/unit/test_light_bake.py": [(TEST_OLD, TEST_NEW)],
}


def main():
    if DRAFT and not os.environ.get("LF_ROOT"):
        raise SystemExit("--draft writes a copy: set LF_ROOT")
    v = (LF / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "0.163.1", v
    entry = (SRC / "CHANGELOG_0.164.0.md").read_text(encoding="utf-8")
    assert DRAFT or "RESULT_" not in entry, "the changelog still carries an unfilled result"
    staged = {}
    for rel, pairs in EDITS.items():
        p = LF / rel
        d = p.read_bytes()
        assert b"\r\n" not in d, (rel, "has CRLF; this patch writes LF files")
        t = d.decode("utf-8")
        assert "THE SKY IS IN THE BAKE" not in t and "test_the_bake_takes_the_sky" not in t, \
            (rel, "already applied")
        for old, new in pairs:
            n = t.count(old)
            assert n == 1, (rel, n, old[:70])
            t = t.replace(old, new)
        staged[p] = t.encode("utf-8")
    cl = LF / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## [0.164.0]" not in d
    assert d.startswith(b"## [0.163.1]")
    for p, raw in staged.items():
        p.write_bytes(raw)
    cl.write_bytes(entry.encode("utf-8").replace(b"\r\n", b"\n") + b"\n" + d)
    (LF / "VERSION").write_bytes(b"0.164.0")
    print("Level Factory 0.163.1 -> 0.164.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
