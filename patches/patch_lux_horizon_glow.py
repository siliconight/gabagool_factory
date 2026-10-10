"""Lux 0.73.0: the glow at the horizon, a town's light over dark land (roadmap 228, step A).
See `lux_horizon_glow/CHANGELOG_0.73.0.md`.

Anchored edits, each asserted to match exactly once, nothing written until all of them did:
  addons/lux/resources/lux_preset.gd    four `horizon_glow_*` fields after `sky_energy`
  addons/lux/runtime/lux_root.gd        `_glow`; built after the environment; freed with the
                                        modules; tuned on every apply; its fields in `_lerp_preset`
  addons/lux/presets/*.tres             each preset's glow, by its character
  new  addons/lux/runtime/lux_horizon_glow.gd
  new  tools/horizon_glow_selftest.gd
CHANGELOG and VERSION from `CHANGELOG_0.73.0.md`. The `.uid` sidecars Godot writes for the two new
scripts on the next import are added by hand afterwards, as every Lux script's is.

    python patch_lux_horizon_glow.py --results-pending   apply, the results unfilled
    python patch_lux_horizon_glow.py --fill               fill them from result_seen.txt, result_selftest.txt
    LUX_ROOT=<copy> python patch_lux_horizon_glow.py --draft
"""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LUX = pathlib.Path(os.environ.get("LUX_ROOT") or HERE.parent / "lux")
SRC = HERE / "lux_horizon_glow"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SEEN": "result_seen.txt", "RESULT_SELFTEST": "result_selftest.txt",
           "RESULT_PRICE": "result_price.txt"}
VERSION_WAS, VERSION = b"Lux 0.72.0", b"Lux 0.73.0"
CHANGELOG_HEAD = "## [0.72.0] - a den is lit at its walls, and in its own colour\n"

PRESET_GD = "addons/lux/resources/lux_preset.gd"
P_ANCHOR = "@export_range(0.0, 2.0) var sky_energy: float = 1.0\n"
P_FIELDS = (
    "## THE GLOW AT THE HORIZON (0.73.0, roadmap 228): a town's light over dark\n"
    "## land, past the plate's edge, drawn by LuxHorizonGlow as one unshaded ring\n"
    "## around the LuxRoot. Energy 0 draws nothing. The top is where the glow has\n"
    "## faded out, in degrees above a standing eye's horizon: a town's climbs 10\n"
    "## to 20, and from 26 m a 3 m wall hides the first 3, so 4 showed in no frame.\n"
    "@export var horizon_glow_color: Color = Color(0.78, 0.47, 0.26)\n"
    "@export_range(0.0, 2.0) var horizon_glow_energy: float = 0.0\n"
    "@export_range(1.0, 45.0) var horizon_glow_top_deg: float = 20.0\n"
    "@export_range(50.0, 2000.0) var horizon_glow_radius_m: float = 380.0\n"
)

ROOT_GD = "addons/lux/runtime/lux_root.gd"
R_VAR_ANCHOR = "var _env: LuxEnvironment\n"
R_VAR = "## The glow at the horizon (0.73.0); hidden when the preset's energy is 0.\nvar _glow: LuxHorizonGlow = null\n"
R_FREE_OLD = "\t\t\t\tor child is LuxRain or child is LuxSkyProvider \\\n"
R_FREE_NEW = "\t\t\t\tor child is LuxRain or child is LuxSkyProvider or child is LuxHorizonGlow \\\n"
R_NULL_ANCHOR = "\t_sky_provider = null\n\t_sky_provider_node = null\n"
R_NULL = "\t_glow = null\n"
R_BUILD_ANCHOR = "\t_env.ensure_world_environment(self)\n"
R_BUILD = (
    "\t# THE GLOW AT THE HORIZON (0.73.0) hangs from this node, so the ring is\n"
    "\t# centred where the level is; `apply` tunes it, and energy 0 hides it.\n"
    "\t_glow = LuxHorizonGlow.new()\n"
    "\tadd_child(_glow)\n"
)
R_APPLY_ANCHOR = "\t\t_lighting.apply(preset, _quality)\n"
R_APPLY = "\tif _glow != null:\n\t\t_glow.apply(preset)\n"
R_LERP_ANCHOR = "\tp.sky_energy = lerpf(a.sky_energy, b.sky_energy, k)\n"
R_LERP = (
    "\tp.horizon_glow_color = a.horizon_glow_color.lerp(b.horizon_glow_color, k)\n"
    "\tp.horizon_glow_energy = lerpf(a.horizon_glow_energy, b.horizon_glow_energy, k)\n"
    "\tp.horizon_glow_top_deg = lerpf(a.horizon_glow_top_deg, b.horizon_glow_top_deg, k)\n"
    "\tp.horizon_glow_radius_m = lerpf(a.horizon_glow_radius_m, b.horizon_glow_radius_m, k)\n"
)

#: Each preset's glow, by its character: (colour, energy, top degrees). The radius stays the
#: script's 380 m everywhere.
SODIUM = (0.78, 0.47, 0.26)
DUSK = (0.85, 0.6, 0.4)
RAIN = (0.6, 0.62, 0.66)
DAY = (0.9, 0.88, 0.82)
PRESETS = {
    "delco_night": (SODIUM, 1.0, 20.0),
    "gothic_street_night": (SODIUM, 0.8, 20.0),
    "gas_station_fluorescent": (SODIUM, 0.8, 20.0),
    "mission_goes_hot": (SODIUM, 0.8, 20.0),
    "ps1_storm_night": (SODIUM, 0.5, 20.0),
    "blue_hour": (DUSK, 0.6, 14.0),
    "heavy_rain": (RAIN, 0.5, 15.0),
    "delco_summer_afternoon": (DAY, 0.35, 10.0),
    "delco_arcade": (DAY, 0.35, 10.0),
    "sof_pc2000": (DAY, 0.35, 10.0),
}
NEW = {
    "addons/lux/runtime/lux_horizon_glow.gd": "lux_horizon_glow.gd",
    "tools/horizon_glow_selftest.gd": "horizon_glow_selftest.gd",
}


def _eol(raw, rel):
    """The file's own line ending. A file with both refuses: there is no one ending to restore."""
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _text(rel):
    raw = (LUX / rel).read_bytes()
    return raw.decode("utf-8").replace("\r\n", "\n"), _eol(raw, rel)


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _preset_lines(color, energy, top):
    r, g, b = color
    return ("sky_energy = {sky}\n"
            f"horizon_glow_color = Color({r}, {g}, {b}, 1)\n"
            f"horizon_glow_energy = {energy}\n"
            f"horizon_glow_top_deg = {top}\n")


def fill():
    assert (LUX / "VERSION").read_bytes().strip() == VERSION, (LUX / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value, (name, value)
        results[key] = value
    writes = {}
    for path, rel in ((LUX / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.73.0.md", "the entry")):
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Lux 0.73.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LUX_ROOT"):
        sys.exit("refusing: --draft is for a LUX_ROOT copy, never the repo")
    assert (LUX / "VERSION").read_bytes().strip() == VERSION_WAS, (LUX / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.73.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.73.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    text, eol = _text(PRESET_GD)
    assert "horizon_glow" not in text, "already patched"
    text = _once(text, P_ANCHOR, P_ANCHOR + P_FIELDS, "the preset's sky_energy")
    writes[LUX / PRESET_GD] = text.encode("utf-8").replace(b"\n", eol)
    text, eol = _text(ROOT_GD)
    assert "LuxHorizonGlow" not in text, "already patched"
    text = _once(text, R_VAR_ANCHOR, R_VAR_ANCHOR + R_VAR, "the _env var")
    text = _once(text, R_FREE_OLD, R_FREE_NEW, "the modules freed")
    text = _once(text, R_NULL_ANCHOR, R_NULL_ANCHOR + R_NULL, "the provider nulled")
    text = _once(text, R_BUILD_ANCHOR, R_BUILD_ANCHOR + R_BUILD, "the environment built")
    text = _once(text, R_APPLY_ANCHOR, R_APPLY_ANCHOR + R_APPLY, "the lighting applied")
    text = _once(text, R_LERP_ANCHOR, R_LERP_ANCHOR + R_LERP, "the sky_energy lerp")
    writes[LUX / ROOT_GD] = text.encode("utf-8").replace(b"\n", eol)
    for name, (color, energy, top) in PRESETS.items():
        rel = f"addons/lux/presets/{name}.tres"
        text, eol = _text(rel)
        assert "horizon_glow" not in text, (rel, "already patched")
        lines = [ln for ln in text.split("\n") if ln.startswith("sky_energy = ")]
        assert len(lines) == 1, (rel, lines)
        sky = lines[0][len("sky_energy = "):]
        text = _once(text, lines[0] + "\n", _preset_lines(color, energy, top).format(sky=sky), rel)
        writes[LUX / rel] = text.encode("utf-8").replace(b"\n", eol)
    for rel, name in NEW.items():
        assert not (LUX / rel).exists(), (rel, "already exists")
        writes[LUX / rel] = (SRC / name).read_bytes().replace(b"\r\n", b"\n")
    cl_text, cl_eol = _text("CHANGELOG.md")
    assert cl_text.startswith("# Changelog\n\n" + CHANGELOG_HEAD), cl_text[:120]
    assert cl_text.count(CHANGELOG_HEAD) == 1
    # every anchor matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    (LUX / "CHANGELOG.md").write_bytes(
        ("# Changelog\n\n" + entry.rstrip("\n") + "\n\n" + cl_text[len("# Changelog\n\n"):])
        .encode("utf-8").replace(b"\n", cl_eol))
    (LUX / "VERSION").write_bytes(VERSION)
    print("Lux 0.72.0 -> 0.73.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
