"""Roadmap item 31, the light-bake probe, step 3: the baked site back in the
renderer packages ship on.

    python prepare_compat.py <bake dir> <out dir> [--raw]

Copies the baked Forward+ copy (keeping its import cache) and undoes what
step 2 needed to bake: the renderer back to GL Compatibility, the
`bake_probe` plugin removed, and the mission entry made to instance
`res://bake.tscn` (the applied site plus its LightmapGI and baked data) in
place of `res://presentation/lux.applied.tscn`. With ``--raw`` the walk
files are removed and the main scene is `mission.tscn` again, which is the
shape the fixed-station harness measures (`docs/COMMANDS.md`).

Prints what it changed.
"""
import os
import re
import shutil
import sys

WALK_FILES = ("_walk.tscn", "_walk_flashlight.gd", "_walk_flashlight.gd.uid", "_walk_ladders.gd",
              "_walk_ladders.gd.uid", "_walk_player.gd", "_walk_player.gd.uid", "debug_overlay.gd",
              "debug_overlay.gd.uid")


def main():
    src, dst = sys.argv[1], sys.argv[2]
    raw = "--raw" in sys.argv[3:]
    if not os.path.exists(os.path.join(src, "bake.lmbake")):
        raise SystemExit(f"{src} has no bake.lmbake: step 2 has not baked")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    shutil.rmtree(os.path.join(dst, "addons", "bake_probe"), ignore_errors=True)
    pg = os.path.join(dst, "project.godot")
    t = open(pg, encoding="utf-8").read()
    # The editor rewrites project.godot on save and DROPS a setting at its
    # default, and Forward+ is the default: after the bake there may be no
    # renderer line at all. Remove any, then write Compatibility explicitly.
    t = re.sub(r'^renderer/rendering_method=.*\n', '', t, flags=re.M)
    t, k = re.subn(r'^\[rendering\]\n', '[rendering]\n\nrenderer/rendering_method="gl_compatibility"\n',
                   t, flags=re.M)
    assert k == 1, "no [rendering] section"
    t = re.sub(r'\n\[editor_plugins\]\n\nenabled=PackedStringArray\("res://addons/bake_probe/plugin.cfg"\)\n', "\n", t)
    assert "bake_probe" not in t
    if raw:
        t, k = re.subn(r'^run/main_scene="res://_walk.tscn"$', 'run/main_scene="res://mission.tscn"', t, flags=re.M)
        assert k == 1
        for f in WALK_FILES:
            p = os.path.join(dst, f)
            if os.path.exists(p):
                os.remove(p)
    open(pg, "w", encoding="utf-8", newline="\n").write(t)
    ms = os.path.join(dst, "mission.tscn")
    m = open(ms, encoding="utf-8").read()
    old = "load('res://presentation/lux.applied.tscn')"
    assert m.count(old) == 1
    open(ms, "w", encoding="utf-8", newline="\n").write(m.replace(old, "load('res://bake.tscn')"))
    for f in ("bake_result.json", "bake_editor.log"):
        p = os.path.join(dst, f)
        if os.path.exists(p):
            os.remove(p)
    print("COMPAT", dst, "renderer gl_compatibility; mission instances bake.tscn", "(raw)" if raw else "(walk)")


if __name__ == "__main__":
    main()
