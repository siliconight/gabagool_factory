"""Level Factory 0.130.0: the wind -- a street tree's crown sways. Step 3a of
`docs/proposals/WIND_DESIGN.md`. The walker, 2026-10-03: "start with the
crowns".

WHAT THIS DOES (every edit anchored once; refuses on a miss):

  * `zoo_worldskin.gd`, the project writer, the export and the preview
    (`lf_wind/worldskin_and_project_edits.py`): `_sway_crowns` replaces a
    crown's skin -- the `StreetTree_Crown` node whose mesh carries a second
    UV set (Zoo 1.56.0) -- with a shader that reproduces the skin's own
    numbers and leans the vertices with `lf_wind`, the one global the shipped
    project.godot declares from the brief's weather
    (`godot_project.wind_for_weather`, `shader_globals_block`); the export
    profile carries `weather`; the preview's project text declares the calm.
  * `cmd_export` hands the brief's weather to the profile.
  * `tests/unit/test_worldskin_sway.py` (new, from `lf_wind/`);
    `test_project_godot_agreement.py` compares `[shader_globals]` too and
    holds the weather table; `test_worldskin_crt_motion.py` admits
    `_sway_crowns` to the material replacers.
  * CHANGELOG and VERSION, from `lf_wind/CHANGELOG_0.130.0.md`.

    python patch_lf_wind.py
    LF_ROOT=<copy> python patch_lf_wind.py
"""
import os
import pathlib
import runpy

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")


def _edit(rel, pairs):
    p = LF / rel
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        assert s.count(old) == 1, (rel, old[:60], s.count(old))
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8", newline="\n")


def main():
    v = (LF / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "0.129.0", v
    gd = LF / "assets" / "godot" / "zoo_worldskin.gd"
    assert "_sway_crowns" not in gd.read_text(encoding="utf-8"), "already applied"
    os.environ["LF_ROOT"] = str(LF)
    runpy.run_path(str(HERE / "lf_wind" / "worldskin_and_project_edits.py"), run_name="__main__")
    # the export command hands the brief's weather to the profile
    _edit("apps/cli/commands/__init__.py", [(
        '''    profile = ExportProfile(mode=args.mode,
                            include_walk=bool(getattr(args, "include_walk", False)))
''',
        '''    # THE BRIEF'S WEATHER GOES INTO THE PACKAGE (0.130.0): the shipped
    # project.godot declares the wind the sway shaders read from it. A
    # workspace with no brief for the mission ships the calm.
    weather = "clear"
    try:
        _, _brief = _find_mission(ws, mission_id)
        weather = str(getattr(_brief_model(_brief), "weather", "") or "clear")
    except Exception:          # no brief in hand: the export still ships
        pass
    profile = ExportProfile(mode=args.mode,
                            include_walk=bool(getattr(args, "include_walk", False)),
                            weather=weather)
''')])
    # the tests
    t = LF / "tests" / "unit" / "test_worldskin_sway.py"
    t.write_bytes((HERE / "lf_wind" / "test_worldskin_sway.py").read_bytes())
    _edit("tests/unit/test_project_godot_agreement.py", [
        ('@pytest.mark.parametrize("section", ["rendering", "debug"])\n',
         '@pytest.mark.parametrize("section", ["rendering", "shader_globals", "debug"])\n'),
        ('''def test_the_sections_being_compared_are_not_empty(tmp_path):
    t = _exported(tmp_path, 0)
    assert _settings(t, "rendering"), "no [rendering] settings parsed"
    assert _settings(t, "debug"), "no [debug] settings parsed"
''',
         '''def test_the_sections_being_compared_are_not_empty(tmp_path):
    t = _exported(tmp_path, 0)
    assert _settings(t, "rendering"), "no [rendering] settings parsed"
    assert _settings(t, "shader_globals"), "no [shader_globals] settings parsed"
    assert _settings(t, "debug"), "no [debug] settings parsed"


def test_the_wind_global_follows_the_profile_s_weather(tmp_path):
    """0.130.0: the export declares `lf_wind` from the weather it was given;
    the preview's text carries the calm, which is what a default profile
    exports, so the agreement above holds for the default and this holds
    the rest of the table."""
    _package(tmp_path, 0)
    _write_project_godot(tmp_path, "mission.tscn", "m", "4.7", weather="storm")
    t = (tmp_path / "project.godot").read_text(encoding="utf-8")
    assert _settings(t, "shader_globals")["lf_wind"] == '{"type": "vec3", "value": Vector3(9, 0, 0)}'
''')])
    _edit("tests/unit/test_worldskin_crt_motion.py", [(
        'MATERIAL_REPLACERS = {"_assign_stairs", "_assign_slabs", "_shutters", "_turning_parts"}\n',
        '#: 0.130.0: a CROWN\'s skin is replaced by the sway shader, which carries the\n'
        '#: skin\'s own numbers and refuses a skin outside its set (`test_worldskin_sway.py`).\n'
        'MATERIAL_REPLACERS = {"_assign_stairs", "_assign_slabs", "_shutters", "_turning_parts", "_sway_crowns"}\n')])
    # the changelog and the version
    entry = (HERE / "lf_wind" / "CHANGELOG_0.130.0.md").read_text(encoding="utf-8")
    cl = LF / "CHANGELOG.md"
    d = cl.read_bytes()
    assert d.startswith(b"## [0.129.0]") and b"## [0.130.0]" not in d
    cl.write_bytes(entry.replace("\r\n", "\n").encode("utf-8") + d)
    (LF / "VERSION").write_bytes(b"0.130.0")
    print("0.129.0 -> 0.130.0")


if __name__ == "__main__":
    main()
