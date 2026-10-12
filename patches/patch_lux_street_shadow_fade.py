"""REFUTED, NOT APPLIED (2026-10-12). Kept as the record of what was tried; `main` refuses to run.

Its own self-test failed it on the renderer packages ship on. Drafted on a copy of Lux and run
windowed on GL Compatibility (Godot 4.7, RTX 2060), the pole lamp carried the fade, a wall pack did
not, and every control held -- but a slab's shadow seen from 44 m, past the fade and its length,
stayed fully black (0.000 against 0.499 unshadowed). The order probe
(`docs/findings/pole_line/fade_order_probe.gd`) says why: read far FIRST, the pool is lit (0.499);
read far after a near look, it is black (0.000). On GL Compatibility `distance_fade_shadow` stops
re-drawing a light's shadow map past the distance -- which is where the 154 draws a heading went --
but the light keeps sampling its last map, so a far shadow FREEZES as it was last drawn, and a
light never seen up close casts none. In a level that is a stale or missing shadow on anything
that moves through a far pool, and a failing (live) light first seen from afar washing through the
walls beside it. Not a free saving; the levers go to the walker (`docs/findings/pole_line/`).
What follows is the original docstring.

Lux 0.76.0: a street light's shadow stops 30 m from the camera (factory roadmap 240, the pole
line's price -- docs/findings/pole_line/).

Anchored edits, each asserted once, nothing written until all of them matched:
  addons/lux/runtime/rigs/lux_streetlight_rig.gd   `shadow_fade_m`, `SHADOW_FADE_LENGTH_M`,
                                                  `LIGHT_FADE_NEVER_M`, `STREET_SHADOW_FADE_M` after
                                                  `lamp_shadow_bias`; `_rebuild()` gives each lamp
                                                  Godot's distance fade when `shadow_fade_m` > 0
  addons/lux/runtime/lux_light_loader.gd           the `streetlight` branch sets STREET_SHADOW_FADE_M
  tools/street_shadow_fade_selftest.gd             NEW (`lux_street_shadow_fade/*.gd.txt`)
CHANGELOG and VERSION from `lux_street_shadow_fade/CHANGELOG_0.76.0.md`; `--results-pending` leaves
the RESULT_ keys to `--fill`.

Read before it was written: the rig's `_rebuild()` (it frees every saved SpotLight3D and builds its
lamps at runtime, so a scene edit to a lamp is never read -- measured: exactly 0 draws), the
loader's `streetlight`, `wall_pack` and `canopy_wash` branches (all three build this rig), and
`tools/streetlight_shadow_selftest.gd` (the self-test's shape).

    python patches/patch_lux_street_shadow_fade.py --results-pending
    godot --rendering-method gl_compatibility --path lux -s res://tools/street_shadow_fade_selftest.gd
    python patches/patch_lux_street_shadow_fade.py --fill
    LUX_ROOT=<copy> python patches/patch_lux_street_shadow_fade.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LUX = pathlib.Path(os.environ.get("LUX_ROOT") or HERE.parent / "lux")
SRC = HERE / "lux_street_shadow_fade"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SELFTEST": "result_selftest.txt", "RESULT_OTHERS": "result_others.txt"}
VERSION_WAS, VERSION = b"Lux 0.75.0", b"Lux 0.76.0"
CHANGELOG_HEAD = "# Changelog\n\n## [0.75.0] - a home's dome lights its room\n"
RIG = "addons/lux/runtime/rigs/lux_streetlight_rig.gd"
LOADER = "addons/lux/runtime/lux_light_loader.gd"
TEST = "tools/street_shadow_fade_selftest.gd"
SHA = {RIG: "4ae293611810165f", LOADER: "8ae0ca046f84d841"}

EXPORT_OLD = ("## Each lamp's shadow bias; negative leaves the engine's. The loader's\n"
              "## `streetlight` branch sets `POLE_SHADOW_BIAS`.\n"
              "@export var lamp_shadow_bias: float = -1.0\n")
EXPORT_NEW = (EXPORT_OLD +
              "\n"
              "## A STREET LIGHT'S SHADOW STOPS AT A DISTANCE (0.76.0). The shadow budget\n"
              "## (roadmap 60) gives its maps to street lights first, and every shadowed one\n"
              "## in view draws its shadow pass whether the player stands under it or 80 m\n"
              "## down the street. A pole line hangs its lamps at 7.50 m where a steel lamp\n"
              "## hung at 5.92, so each pass takes in more of the street: priced at Level\n"
              "## Factory's stations on cold run 9262's package (the factory's\n"
              "## `docs/findings/pole_line/`, 53 headings, GL Compatibility), its twelve\n"
              "## shadowed street lights cost 300.1 draws a heading against 133.4 for 9261's\n"
              "## lamps. A steady street light is baked, so its map at runtime shades only\n"
              "## what moves through its pool; a failing one is live and shades the street\n"
              "## too. Past `shadow_fade_m` from the camera a lamp's shadow fades out over\n"
              "## `SHADOW_FADE_LENGTH_M` by Godot's own `distance_fade_shadow`; the light\n"
              "## itself never fades (`LIGHT_FADE_NEVER_M`). 0 leaves a rig as before. The\n"
              "## loader's `streetlight` branch sets STREET_SHADOW_FADE_M; a wall pack and a\n"
              "## canopy wash keep 0 -- their shadows stop light washing through their own\n"
              "## wall, which matters from inside at any distance. It lives here and not\n"
              "## on a scene's lamps because `_rebuild()` frees those and builds its own.\n"
              "@export var shadow_fade_m: float = 0.0:\n"
              "\tset(value):\n"
              "\t\tshadow_fade_m = value\n"
              "\t\tif is_inside_tree():\n"
              "\t\t\t_rebuild()\n"
              "const SHADOW_FADE_LENGTH_M := 5.0\n"
              "const LIGHT_FADE_NEVER_M := 4096.0\n"
              "## 30 m: one span of a pole line -- Lot's poles stand at most 36 m apart, and\n"
              "## 31.2 to 33.2 on 9262's main road -- so the player keeps the shadow of the\n"
              "## light overhead, and of both when between two. Measured with these four\n"
              "## properties set in the rig vendored into a copy of 9262's package: -154.0\n"
              "## draws a heading (median -46, at most -740), 16.2 over 9261's lamps. A line\n"
              "## spaced otherwise would want it derived again.\n"
              "const STREET_SHADOW_FADE_M := 30.0\n")

BUILD_OLD = ("\t\tlamp.shadow_enabled = r.shadows_enabled\n"
             "\t\tif lamp_shadow_bias >= 0.0:\n"
             "\t\t\tlamp.shadow_bias = lamp_shadow_bias\n")
BUILD_NEW = (BUILD_OLD +
             "\t\tif shadow_fade_m > 0.0:\n"
             "\t\t\t# the shadow ends shadow_fade_m from the camera, the light never (0.76.0)\n"
             "\t\t\tlamp.distance_fade_enabled = true\n"
             "\t\t\tlamp.distance_fade_begin = LIGHT_FADE_NEVER_M\n"
             "\t\t\tlamp.distance_fade_shadow = shadow_fade_m\n"
             "\t\t\tlamp.distance_fade_length = SHADOW_FADE_LENGTH_M\n")

LOADER_OLD = ("\t\t\ts.lamp_shadow_bias = LuxStreetlightRig.POLE_SHADOW_BIAS\n"
              "\t\t\tvar rs := LuxLightRig.new()\n"
              "\t\t\trs.rig_name = &\"Streetlight (baked)\"\n")
LOADER_NEW = ("\t\t\ts.lamp_shadow_bias = LuxStreetlightRig.POLE_SHADOW_BIAS\n"
              "\t\t\t# its shadow stops one span of a pole line from the camera (0.76.0)\n"
              "\t\t\ts.shadow_fade_m = LuxStreetlightRig.STREET_SHADOW_FADE_M\n"
              "\t\t\tvar rs := LuxLightRig.new()\n"
              "\t\t\trs.rig_name = &\"Streetlight (baked)\"\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _read(rel):
    p = LUX / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


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
    sys.exit("refused: this patch is REFUTED (its docstring says why) and must not be applied")
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LUX_ROOT"):
        sys.exit("refusing: --draft is for a LUX_ROOT copy, never the repo")
    assert (LUX / "VERSION").read_bytes().strip() == VERSION_WAS, (LUX / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.76.0.md")
    assert entry.startswith("## [0.76.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    assert not (LUX / TEST).exists(), "already applied"
    rp, r_eol, rig = _read(RIG)
    rig = _once(rig, EXPORT_OLD, EXPORT_NEW, "the rig's lamp_shadow_bias export")
    rig = _once(rig, BUILD_OLD, BUILD_NEW, "the rig's lamp build")
    lp, l_eol, loader = _read(LOADER)
    loader = _once(loader, LOADER_OLD, LOADER_NEW, "the loader's streetlight branch")
    test = _src("street_shadow_fade_selftest.gd.txt")
    cl = LUX / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:160]
    cl_new = "# Changelog\n\n" + entry.rstrip("\n") + "\n\n" + cl_text[len("# Changelog\n\n"):]
    # every anchor matched: now write
    rp.write_bytes(rig.replace("\n", r_eol.decode()).encode("utf-8"))
    lp.write_bytes(loader.replace("\n", l_eol.decode()).encode("utf-8"))
    (LUX / TEST).write_bytes(test.encode("utf-8"))
    cl.write_bytes(cl_new.replace("\n", cl_eol.decode()).encode("utf-8"))
    (LUX / "VERSION").write_bytes(VERSION)
    print("Lux 0.75.0 -> 0.76.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
