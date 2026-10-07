"""Level Factory 0.151.0: the light bake lays the rooms' floor, bakes it, and
frees it before it saves.

    python patch_lf_room_fill.py

Lux 0.68.0's `LuxLightLoader.add_bake_fills` lays bake-only fills over a
level's room probes. The editor plugin asks for them after the scene opens
and before Bake is pressed, frees them before the scene is saved, and counts
them in its result; `light_bake.bake` carries the count into
`light_bake.json` and the export log. A level whose Lux predates the call
bakes as before and says so (-1).

Anchored on, as read 2026-10-07 (both LF):
  level_factory/assets/godot/light_bake_plugin.gd    4,472 bytes
  level_factory/packages/exporting/light_bake.py    14,655 bytes
Every anchor must match once; nothing is written on a miss.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "level_factory" / "assets" / "godot" / "light_bake_plugin.gd"
BAKE = ROOT / "level_factory" / "packages" / "exporting" / "light_bake.py"

PLUGIN_EDITS = [
    ("var _busy: bool = false\n",
     "var _busy: bool = false\n"
     "## THE ROOMS' FLOOR (0.151.0). Lux >= 0.68.0 lays bake-only fills over the\n"
     "## level's room probes (`LuxLightLoader.add_bake_fills`), because a\n"
     "## lightmapped wall takes no light from a room probe's ambient. The lightmap\n"
     "## must keep their light and the saved scene must not keep them: laid after\n"
     "## the scene opens and before Bake is pressed, freed before the save.\n"
     "## `_fill_count` is -1 when the level's Lux has no such call.\n"
     "var _fill: Node = null\n"
     "var _fill_count: int = -1\n"),
    ("\t\t\t_t0 = Time.get_ticks_msec()\n",
     "\t\t\t_fill = _lay_room_fill(EditorInterface.get_edited_scene_root())\n"
     "\t\t\t_t0 = Time.get_ticks_msec()\n"),
    ("\t\t\t_busy = true\n\t\t\tEditorInterface.save_scene()\n",
     "\t\t\t_free_room_fill()\n\t\t\t_busy = true\n\t\t\tEditorInterface.save_scene()\n"),
    ('\t\t\t_done({"ok": true, "bake_ms": took, "users": d.get_user_count(),\n',
     '\t\t\t_done({"ok": true, "bake_ms": took, "users": d.get_user_count(),\n'
     '\t\t\t\t"room_fills": _fill_count,\n'),
    ("func _process(_delta: float) -> void:\n",
     "## The level's Lux loader sits beside its LuxRoot's script, in a package\n"
     "## (`res://runtime/lux/runtime/`) and in Lux's own repo alike. Its\n"
     "## `add_bake_fills` lays the fill under `root` and returns the container.\n"
     "func _lay_room_fill(root: Node) -> Node:\n"
     "\tif root == null:\n"
     "\t\treturn null\n"
     "\tfor n in root.get_tree().get_nodes_in_group(&\"lux_root\"):\n"
     "\t\tif n != root and not root.is_ancestor_of(n):\n"
     "\t\t\tcontinue\n"
     "\t\tvar s: Script = n.get_script()\n"
     "\t\tif s == null:\n"
     "\t\t\tcontinue\n"
     "\t\tvar path := s.resource_path.get_base_dir().path_join(\"lux_light_loader.gd\")\n"
     "\t\tif not ResourceLoader.exists(path):\n"
     "\t\t\tcontinue\n"
     "\t\tvar loader: Script = load(path)\n"
     "\t\tif loader == null or not loader.has_method(\"add_bake_fills\"):\n"
     "\t\t\treturn null\n"
     "\t\tvar fill: Node = loader.call(\"add_bake_fills\", root)\n"
     "\t\t_fill_count = fill.get_child_count() if fill != null else 0\n"
     "\t\tprint(\"BAKE room fills: \", _fill_count)\n"
     "\t\treturn fill\n"
     "\treturn null\n"
     "\n"
     "\n"
     "func _free_room_fill() -> void:\n"
     "\tif _fill != null and is_instance_valid(_fill):\n"
     "\t\t_fill.free()\n"
     "\t_fill = null\n"
     "\n"
     "\n"
     "func _process(_delta: float) -> void:\n"),
]

BAKE_EDITS = [
    ("WHAT SHIPS. `bake.tscn` at the package root",
     "THE ROOMS' FLOOR (0.151.0). A lightmapped surface takes its light from the\n"
     "lightmap alone, so a room probe's ambient -- the floor Lux puts under a\n"
     "room's fixtures -- stopped reaching any wall or floor when this bake\n"
     "shipped, and a corner no lamp reaches baked to black\n"
     "(`docs/findings/night_interiors/` at the factory root). The plugin asks the\n"
     "level's Lux (>= 0.68.0) to lay bake-only fills over its room probes before\n"
     "Bake is pressed and frees them before the save: the lightmap holds their\n"
     "light and the package carries no fill. `room_fills` in the report counts\n"
     "them; -1 means the level's Lux lays none.\n"
     "\n"
     "WHAT SHIPS. `bake.tscn` at the package root"),
    ('        report["result"] = result\n',
     '        report["result"] = result\n'
     '        report["room_fills"] = (result or {}).get("room_fills")\n'),
    ('        log("[export] light bake: %d model(s) and %d primitive mesh(es) lightmapped, %d kept dynamic; "\n'
     '            "%d steady rig(s) baked, %d failing left live; %d users, %s s in the editor"\n'
     '            % (len(report["imports"]["baked"]), sum(report["primitives"].values()),\n'
     '               len(report["imports"]["dynamic"]), report["rigs"]["static"], report["rigs"]["live"],\n'
     '               result.get("users"), report["editor_s"]))\n',
     '        fills = report["room_fills"]\n'
     '        log("[export] light bake: %d model(s) and %d primitive mesh(es) lightmapped, %d kept dynamic; "\n'
     '            "%d steady rig(s) baked, %d failing left live; %s; %d users, %s s in the editor"\n'
     '            % (len(report["imports"]["baked"]), sum(report["primitives"].values()),\n'
     '               len(report["imports"]["dynamic"]), report["rigs"]["static"], report["rigs"]["live"],\n'
     '               "no room floor (the level\'s Lux lays none)" if fills in (None, -1)\n'
     '               else "%d room fill(s)" % fills,\n'
     '               result.get("users"), report["editor_s"]))\n'),
]


def _stage(path, size, edits):
    data = path.read_bytes()
    assert len(data) == size, "%s is %d bytes, read at %d" % (path.name, len(data), size)
    assert b"\r\n" not in data, "%s has CRLF; it was LF" % path.name
    text = data.decode("utf-8")
    for old, new in edits:
        assert text.count(old) == 1, "%s: anchor found %d times: %r" % (path.name, text.count(old), old[:60])
        text = text.replace(old, new)
    return path, data, text


def main():
    staged = [_stage(PLUGIN, 4472, PLUGIN_EDITS), _stage(BAKE, 14655, BAKE_EDITS)]
    for path, data, text in staged:
        path.write_bytes(text.encode("utf-8"))
        print("%s: %d -> %d bytes" % (path.name, len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
