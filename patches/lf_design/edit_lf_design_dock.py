"""Level Factory 0.245.0 on a clone, the dock's half: the panel gets a Setup tab (what 0.244.0 showed) and a Level
tab (`level_panel.gd`). Run after `edit_lf_design.py`. Anchored; refuses on a miss.

    python edit_lf_design_dock.py <clone>
"""
import pathlib
import shutil
import sys

C = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).resolve().parent
ADDON = "apps/godot/addons/gabagool_factory"

dst = C / ADDON / "level_panel.gd"
assert not dst.exists()
shutil.copyfile(HERE / "src" / ADDON / "level_panel.gd", dst)
print("wrote level_panel.gd")

p = C / ADDON / "factory_dock.gd"
t = p.read_bytes().decode("utf-8")
assert "\r\n" not in t and "LevelPanel" not in t


def once(old, new):
    global t
    assert t.count(old) == 1, old[:80]
    t = t.replace(old, new)


once('''## The Gabagool Factory panel: increment 1 of the no-AI authoring loop (`docs/AUTHORING_LOOP.md` at the factory root;
## roadmap 311). It finds the factory, checks whether Blender, Godot and the tools are ready, and records the
## executables the user picks -- every action a service operation (`service_client.gd`), never a terminal.
''', '''## The Gabagool Factory panel (`docs/AUTHORING_LOOP.md` at the factory root). The Setup tab finds the factory, checks
## whether Blender, Godot and the tools are ready, and records the executables the user picks (roadmap 311); the
## Level tab starts and opens levels (`level_panel.gd`, roadmap 312 and 313). Every action is a service operation
## (`service_client.gd`), never a terminal.
''')
once('''const ServiceClient := preload("res://addons/gabagool_factory/service_client.gd")
''', '''const ServiceClient := preload("res://addons/gabagool_factory/service_client.gd")
const LevelPanel := preload("res://addons/gabagool_factory/level_panel.gd")
''')
once('''var client: Node
''', '''var client: Node
## The Level tab; it has its own client, so a level's work and a setup check do not queue behind each other.
var level_panel: Control
var _tabs: TabContainer
var _setup: VBoxContainer
''')

# `_build` lays the Setup tab: every control it adds goes into `_setup`, not the dock
start = t.index("func _build() -> void:\n")
end = t.index("\n\n\n", start)
body = t[start:end]
assert body.count("\tadd_child(") >= 6, body.count("\tadd_child(")
body = body.replace("\tadd_child(", "\t_setup.add_child(")
body = body.replace("func _build() -> void:\n", '''func _build() -> void:
	_tabs = TabContainer.new()
	_tabs.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(_tabs)
	_setup = VBoxContainer.new()
	_setup.name = "Setup"
	_tabs.add_child(_setup)
	level_panel = LevelPanel.new()
	_tabs.add_child(level_panel)

''', 1)
t = t[:start] + body + t[end:]

once('''func _set_root(root: String) -> void:
	client.factory_root = root
''', '''func _set_root(root: String) -> void:
	client.factory_root = root
	level_panel.set_factory_root(root)
''')
p.write_bytes(t.encode("utf-8"))
print("edited factory_dock.gd")

test = C / "apps" / "godot" / "tests" / "test_level_panel.gd"
assert not test.exists()
shutil.copyfile(HERE / "src" / "apps" / "godot" / "tests" / "test_level_panel.gd", test)
print("wrote test_level_panel.gd")
