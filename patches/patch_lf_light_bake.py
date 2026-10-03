"""Level Factory 0.131.0: `export --bake-lights` bakes the package's steady
lights into a lightmap (roadmap item 31). The probe and its measurements
are `docs/findings/light_bake/NOTES.md`.

New files copied from `lf_light_bake/`: `packages/exporting/light_bake.py`,
`assets/godot/light_bake_plugin.gd`, `tests/unit/test_light_bake.py`.
Anchored edits (every anchor once; refuses on a miss): `export.py`
(`ExportProfile.bake_lights`, the step after the occluder bake),
`apps/cli/main.py` (`--bake-lights`), `apps/cli/commands/__init__.py`
(the profile reads it). CHANGELOG and VERSION from
`lf_light_bake/CHANGELOG_0.131.0.md`.

    python patch_lf_light_bake.py
    LF_ROOT=<copy> python patch_lf_light_bake.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_light_bake"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


def main():
    v = (LF / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "0.130.1", v
    assert not (LF / "packages" / "exporting" / "light_bake.py").exists(), "already applied"
    for name, dst in (("light_bake.py", LF / "packages" / "exporting" / "light_bake.py"),
                      ("light_bake_plugin.gd", LF / "assets" / "godot" / "light_bake_plugin.gd"),
                      ("test_light_bake.py", LF / "tests" / "unit" / "test_light_bake.py")):
        dst.write_bytes((SRC / name).read_bytes())
    _edit(LF / "packages" / "exporting" / "export.py", [
        ('    weather: str = "clear"\n\n    def as_dict(self) -> dict:\n',
         '    weather: str = "clear"\n'
         '    #: Bake the steady lights into a lightmap (0.131.0, roadmap item 31,\n'
         '    #: `packages/exporting/light_bake.py`). Opt-in: it needs a GPU and a\n'
         '    #: display, and opens the Godot editor for about a minute.\n'
         '    bake_lights: bool = False\n\n    def as_dict(self) -> dict:\n'),
        ('    # Settle the flag against what shipped, then drop the cache the bake\n',
         '    # THE LIGHT BAKE (0.131.0), opt-in. After the occluder bake, which leaves\n'
         '    # the import cache this needs, and before the cache is dropped; it points\n'
         '    # the entry at `bake.tscn` and ships the lightmap, or restores what it\n'
         '    # touched and ships the package unbaked, saying which in light_bake.json.\n'
         '    if profile.bake_lights:\n'
         '        from packages.exporting.light_bake import bake as _bake_lights\n'
         '        _bake_lights(export_dir, godot_executable)\n\n'
         '    # Settle the flag against what shipped, then drop the cache the bake\n'),
    ])
    _edit(LF / "apps" / "cli" / "main.py", [
        ('    sp.add_argument("--include-walk", action="store_true",\n'
         '                    help="localize walk scenes (runtime scripts bundled) instead of stripping them")\n'
         '    sp.set_defaults(func=cmd_export)\n',
         '    sp.add_argument("--include-walk", action="store_true",\n'
         '                    help="localize walk scenes (runtime scripts bundled) instead of stripping them")\n'
         '    sp.add_argument("--bake-lights", action="store_true",\n'
         '                    help="bake the steady lights into a lightmap (needs a GPU and a display; "\n'
         '                         "opens the Godot editor for about a minute)")\n'
         '    sp.set_defaults(func=cmd_export)\n'),
    ])
    _edit(LF / "apps" / "cli" / "commands" / "__init__.py", [
        ('                            include_walk=bool(getattr(args, "include_walk", False)),\n'
         '                            weather=weather)\n',
         '                            include_walk=bool(getattr(args, "include_walk", False)),\n'
         '                            weather=weather,\n'
         '                            bake_lights=bool(getattr(args, "bake_lights", False)))\n'),
    ])
    entry = (SRC / "CHANGELOG_0.131.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    cl = LF / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## [0.131.0]" not in d and d.startswith(b"## [0.130.1]")
    cl.write_bytes(entry.encode("utf-8") + d)
    (LF / "VERSION").write_bytes(b"0.131.0")
    print("0.130.1 -> 0.131.0")


if __name__ == "__main__":
    main()
