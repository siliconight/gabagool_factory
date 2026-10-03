"""Lux 0.66.0: a baked level's lightmap is switched with the level's state.

Roadmap item 31's probe (`docs/findings/light_bake/NOTES.md`) baked the gas
station lot's steady lights and priced it on a quiet machine: -0.8 ms
median frame, -0.45 ms GPU, controls 0.04-0.10 ms. Two runtime states keep
it honest, both measured in GL Compatibility on the baked lot:

  * the POWER CUT (`set_fixtures_powered(false)`) hides every rig lamp; a
    baked light's effect on the level does not hide with its lamp, so the
    lightmap goes off with the power and comes back with it. Lightmap off
    and lamps hidden read 0.120 overhead against 0.154 lit;
  * a PRESET other than the one the lightmap was baked under (weather, time
    of day, a mission phase) falls back to real time: lightmap off, every
    static rig light flipped to dynamic and re-added. Measured: 3,253 draws
    and the never-baked build's luminance at three stations (3,252); the
    lightmap back and the lights static again return 2,614 and the baked
    picture. Clearing the lightmap alone, or flipping the mode alone, left
    the static lights excluded (2,614 draws, darker): the re-add is the step.

Anchored edits (every anchor once; refuses on a miss): `lux_lighting.gd`
(the state, `bind_lightmaps`, `set_baked_lighting`, the power cut syncs it),
`lux_root.gd` (bound after ready, the preset rule, the public calls),
`lux_runtime_api.gd` (`baked_lighting`); `tools/lightmap_switch_selftest.gd`
copied from `lux_baked_switch/`; CHANGELOG and VERSION from
`lux_baked_switch/CHANGELOG_0.66.0.md`.

    python patch_lux_baked_switch.py
    LUX_ROOT=<copy> python patch_lux_baked_switch.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LUX = pathlib.Path(os.environ.get("LUX_ROOT") or HERE.parent / "lux")
SRC = HERE / "lux_baked_switch"

LIGHTING_STATE = '''
## THE BAKED LIGHTMAPS (0.66.0). A LightmapGI's data holds the steady lights'
## effect on the level as it was baked; a static light no longer lights the
## lightmapped surfaces in real time. So the lightmap is level STATE, and two
## things change it: the power cut (the lamps hide, so the lightmap goes off
## with them) and a preset other than the baked one (`set_baked_lighting
## (false)`: the lightmap off and every static rig light handed back to real
## time). [[LightmapGI, its LightmapGIData], ...]
var _lightmaps: Array = []
var _baked_on: bool = false
var _flipped: Array[Light3D] = []
'''

LIGHTING_FUNCS = '''

## Find every LightmapGI under `search_root` that carries baked data and hold
## it; baked lighting is on when there is one. Returns how many were bound.
func bind_lightmaps(search_root: Node) -> int:
	_lightmaps.clear()
	if search_root == null:
		return 0
	for n in search_root.find_children("*", "LightmapGI", true, false):
		var lm := n as LightmapGI
		if lm != null and lm.light_data != null:
			_lightmaps.append([lm, lm.light_data])
	_baked_on = not _lightmaps.is_empty()
	_sync_lightmaps()
	return _lightmaps.size()


func has_lightmaps() -> bool:
	return not _lightmaps.is_empty()


func baked_lighting() -> bool:
	return _baked_on


## Baked (the lightmap on, the steady lights static) or real time (the
## lightmap off, every static rig light dynamic). A level with no lightmap
## ignores this.
##
## THE RE-ADD IS THE STEP THAT WORKS. Measured on the baked gas station lot in
## GL Compatibility: clearing the lightmap alone left the static lights
## excluded from the surfaces it had covered (2,614 draws, the level darker),
## and flipping their bake mode alone did too. Hiding and showing each light
## again re-pairs it with the geometry: 3,253 draws against the never-baked
## build's 3,252, the same luminance at three stations.
func set_baked_lighting(on: bool) -> void:
	if _lightmaps.is_empty() or on == _baked_on:
		return
	_baked_on = on
	if on:
		for l in _flipped:
			if is_instance_valid(l):
				l.light_bake_mode = Light3D.BAKE_STATIC
		_flipped.clear()
	else:
		for n in _registered:
			if is_instance_valid(n) and n is Light3D and (n as Light3D).light_bake_mode == Light3D.BAKE_STATIC:
				var l := n as Light3D
				l.light_bake_mode = Light3D.BAKE_DYNAMIC
				_flipped.append(l)
	_sync_lightmaps()
	for n in _registered:
		if is_instance_valid(n) and n is Light3D and (n as Light3D).visible:
			(n as Light3D).visible = false
			(n as Light3D).visible = true


## The lightmap shows while baked lighting is on AND the power is: a cut
## hides the lamps, and their baked light goes with them.
func _sync_lightmaps() -> void:
	var show: bool = _baked_on and _fixtures_powered
	for pair in _lightmaps:
		var lm: LightmapGI = pair[0]
		if is_instance_valid(lm):
			lm.light_data = pair[1] if show else null
'''

ROOT_READY = '''	if bind_emissives_on_ready:
		var bound: Dictionary = bind_fixture_emissives()
		print("[lux] %s (searched %s)" % [String(bound.get("msg", "")),
			String(bound.get("search_root", "?"))])
'''

ROOT_READY_NEW = ROOT_READY + '''	# THE BAKED LIGHTMAPS (0.66.0), deferred: a LightmapGI beside the site in
	# the level's scene is in the tree by now, but a level built in code may
	# add it after this node is ready.
	_bind_lightmaps.call_deferred()
'''

ROOT_FUNCS = '''

## The preset the level's lightmap was baked under, by identity: a weather,
## time-of-day or mission-phase change builds a NEW preset and falls back to
## real time; re-applying the same one (a quality change) does not.
var _baked_preset: LuxPreset = null


func _bind_lightmaps() -> void:
	if _lighting == null:
		return
	var top: Node = self
	while top.get_parent() != null and top.get_parent() != get_tree().root:
		top = top.get_parent()
	var n: int = _lighting.bind_lightmaps(top)
	_baked_preset = _current
	if n > 0:
		print("[lux] baked lighting: %d lightmap(s) bound under %s" % [n, String(top.name)])


## Whether the level is drawing its baked lightmap (0.66.0).
func baked_lighting() -> bool:
	return _lighting != null and _lighting.baked_lighting()


## Switch a baked level between its lightmap and real-time lighting. Off
## costs the frame what the bake saved; on is valid only under the preset it
## was baked with, so turning it on under another one is refused.
func set_baked_lighting(on: bool) -> void:
	if _lighting == null:
		return
	if on and _current != _baked_preset:
		push_warning("Lux: baked lighting not restored: the preset in force is not the one it was baked under.")
		return
	_lighting.set_baked_lighting(on)
'''

ROOT_APPLY = '''	if blend_time <= 0.0:
		_apply_immediate(preset)
	else:
		_start_blend(_current if _current != null else preset, preset, blend_time)
'''

ROOT_APPLY_NEW = '''	# a preset the lightmap was not baked under falls back to real time (0.66.0)
	if preset != _baked_preset and _lighting != null and _lighting.baked_lighting():
		push_warning("Lux: preset changed on a baked level; lighting falls back to real time.")
		_lighting.set_baked_lighting(false)
''' + ROOT_APPLY

API = '''

## Whether a baked level draws its lightmap, and switch it (0.66.0). Off is
## real time for every steady light; on is refused under a preset other
## than the one it was baked with.
static func baked_lighting(tree: SceneTree, on: bool) -> void:
	var r := get_root(tree)
	if r != null:
		r.set_baked_lighting(on)
'''


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


def main():
    v = (LUX / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Lux 0.65.0", v
    rt = LUX / "addons" / "lux" / "runtime"
    _edit(rt / "lux_lighting.gd", [
        ("var _fixtures_powered: bool = true\n", "var _fixtures_powered: bool = true\n" + LIGHTING_STATE),
        ("\tfor m in _emissives:\n\t\tif m != null:\n\t\t\t_apply_emissive_power(m)\n\n\nfunc fixtures_powered() -> bool:\n",
         "\tfor m in _emissives:\n\t\tif m != null:\n\t\t\t_apply_emissive_power(m)\n\t_sync_lightmaps()\n" + LIGHTING_FUNCS
         + "\n\nfunc fixtures_powered() -> bool:\n"),
    ])
    _edit(rt / "lux_root.gd", [
        (ROOT_READY, ROOT_READY_NEW),
        (ROOT_APPLY, ROOT_APPLY_NEW),
        ("\n\n## Whether the fixtures are powered (0.62.0)", ROOT_FUNCS + "\n\n## Whether the fixtures are powered (0.62.0)"),
    ])
    api = rt / "lux_runtime_api.gd"
    s = api.read_text(encoding="utf-8")
    assert "\r" not in s and "baked_lighting" not in s
    api.write_text(s.rstrip("\n") + "\n" + API, encoding="utf-8", newline="\n")
    (LUX / "tools" / "lightmap_switch_selftest.gd").write_bytes((SRC / "lightmap_switch_selftest.gd").read_bytes())
    entry = (SRC / "CHANGELOG_0.66.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    cl = LUX / "CHANGELOG.md"
    d = cl.read_bytes()
    assert b"## [0.66.0]" not in d
    head = b"# Changelog\n\n"
    assert d.startswith(head)
    cl.write_bytes(head + entry.encode("utf-8") + d[len(head):])
    (LUX / "VERSION").write_bytes(b"Lux 0.66.0")
    print("0.65.0 -> 0.66.0")


if __name__ == "__main__":
    main()
