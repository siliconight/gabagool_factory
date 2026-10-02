"""Lux 0.62.0: light that isn't perfectly steady -- one failing fixture a room.

The walker, 2026-10-02, on levels whose every fluorescent row already
"flickered" at 12 % and 9 Hz: the lights feel frozen. Three reasons, all in
the code: the flicker was a sum of two sines (a smooth hum of at most 6 %,
which the eye ignores), the fixture's own lens stayed constant while its
lamp wavered (a light moving without its source reads as nothing), and every
fixture did it in unison (uniform irregularity, the authorship guide's
symptom). Design shown to the walker; their calls: one failing fixture a
room, and cycling streetlights.

WHAT THIS DOES:

  * `runtime/lux_failing.gd` (new): the model. STUTTER (a fluorescent with a
    tired ballast: steady for its own 4-15 s, then a burst of 2-4 drops to
    60-75 % a few frames long), CYCLING (a sodium streetlight: over 40-70 s it
    dims, cuts out, sits dark, restrikes and warms up), WAVER (a filament's
    slow 3-5 % sway). Pure functions of (kind, seed, t).
  * `LuxLightRig` gains `failing_kind` and `failing_seed`.
  * `LuxFluorescentRig` and `LuxStreetlightRig`: a failing rig drives its
    lamps' energy AND its lens -- the nearest lit face to each lamp, found
    once at ready, given its own material override so no other fixture
    moves with it. A powered-off level (the heist's cut) is left alone.
  * `LuxFixtureSpawner`: ONE fixture an anchor (a ceiling row is a room's)
    fails, chosen by the anchor id's hash: a fluorescent stutters, a pendant
    wavers. Every other fixture is steady.
  * `LuxLightLoader`: the fluorescent and pendant rows' always-on wobble is
    0; the every-third streetlight that buzzed now CYCLES.

COST: a script tick a FAILING fixture (a handful a level) where every rig
ticked before. No draws: a lens surface is one draw whatever material it
wears, so its override adds none -- measured on run 9137's package, 53
views, draw counts identical to the view (see the 0.62.0 changelog).

    python patch_lux_failing_fixtures.py
    LUX_ROOT=<copy> python patch_lux_failing_fixtures.py

Every edit asserts its anchor once and refuses to write on a miss. The new
files (`runtime/lux_failing.gd`, `tools/failing_fixtures_selftest.gd`) are
copied from `lux_failing/` beside this script.
"""
from __future__ import annotations

import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LUX = pathlib.Path(os.environ.get("LUX_ROOT") or HERE.parent / "lux")


def _edit(rel, pairs):
    p = LUX / rel
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    s = raw.replace(b"\r\n", b"\n").decode("utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, f"{rel}: anchor found {n} times: {old[:70]!r}"
        s = s.replace(old, new)
    out = s.encode("utf-8")
    p.write_bytes(out.replace(b"\n", b"\r\n") if crlf else out)
    print("edited", rel)


RIG_RES = [
    ('''@export_group("Flicker")
## Subtle instability for fluorescents / failing bulbs. 0 = steady.
@export_range(0.0, 1.0) var flicker_amount: float = 0.0
@export_range(0.1, 30.0) var flicker_speed: float = 8.0
''', '''@export_group("Flicker")
## Subtle instability for fluorescents / failing bulbs. 0 = steady. The
## sum-of-sines hum every rig carried before 0.62.0; the loader sets it to 0
## now and a FAILING fixture uses `failing_kind` instead. Kept for scenes
## that tuned it by hand.
@export_range(0.0, 1.0) var flicker_amount: float = 0.0
@export_range(0.1, 30.0) var flicker_speed: float = 8.0

@export_group("Failing")
## How this fixture fails (0.62.0, `LuxFailing`): 0 steady, 1 a fluorescent's
## stutter, 2 a sodium lamp's cycling, 3 a filament's waver. A failing rig
## moves its lamps AND the lit face nearest each lamp. One fixture a room
## fails; the spawner and the loader choose which.
@export_enum("Steady", "Stutter", "Cycling", "Waver") var failing_kind: int = 0
## Its own clock: two failing tubes in one building never stutter together.
@export var failing_seed: int = 0
''')]

FLUORO = [
    ('''var _lights: Array[Light3D] = []
var _flicker_phase: float = 0.0
''', '''var _lights: Array[Light3D] = []
var _flicker_phase: float = 0.0
## A failing fixture's clock and its lenses (0.62.0): one
## ``[MeshInstance3D, surface, material, base emission]`` a lamp, each its
## own override so no other fixture dims with it.
var _fail_t: float = 0.0
var _lenses: Array = []
'''),
    ('''	var root := _find_lux_root()
	if root != null:
		for l in _lights:
			root.register_lux_light(l)
	set_process(rig != null and rig.flicker_amount > 0.0 and rig.bake_mode != 1)
''', '''	var root := _find_lux_root()
	if root != null:
		for l in _lights:
			root.register_lux_light(l)
	# DEFERRED, not now: the spawner places a rig AFTER add_child, so at
	# ready its lamps still sit at the container's origin and the nearest
	# lens is nowhere (measured: 0 of 9 tubes bound on the first probe)
	_bind_lenses.call_deferred()
	set_process(rig != null and rig.bake_mode != 1
		and (rig.flicker_amount > 0.0 or rig.failing_kind != LuxFailing.NONE))


## A failing fixture dims the lit face nearest each of its lamps (0.62.0).
## The lamp sits inside its own hardware, so the nearest lens within a metre
## and a half is its own. The face gets a material of its own, so the rest of
## the row -- which shares the lens material -- stays steady. Once, at ready.
func _bind_lenses() -> void:
	_lenses.clear()
	if rig == null or rig.failing_kind == LuxFailing.NONE or rig.bake_mode == 1:
		return
	var scene: Node = owner if owner != null else get_tree().current_scene
	if scene == null:
		scene = get_tree().root
	for l in _lights:
		var hit: Array = LuxFailing.find_lens(scene, l.global_position, 1.5)
		if hit.is_empty():
			continue
		var mi: MeshInstance3D = hit[0]
		var s: int = hit[1]
		var mat: BaseMaterial3D = mi.get_active_material(s) as BaseMaterial3D
		if mat == null:
			continue
		var own: BaseMaterial3D = mat.duplicate() as BaseMaterial3D
		own.resource_name = mat.resource_name
		mi.set_surface_override_material(s, own)
		_lenses.append([mi, s, own, own.emission_energy_multiplier])
'''),
    ('''func _process(delta: float) -> void:
	var r := rig if rig != null else null
	if r == null or r.flicker_amount <= 0.0 or r.bake_mode == 1:
		return
	_flicker_phase += delta * r.flicker_speed
''', '''func _process(delta: float) -> void:
	var r := rig if rig != null else null
	if r == null or r.bake_mode == 1:
		return
	if r.failing_kind != LuxFailing.NONE:
		_fail_t += delta
		var lvl := LuxFailing.level(r.failing_kind, r.failing_seed, _fail_t)
		for l in _lights:
			if is_instance_valid(l):
				l.light_energy = r.energy * energy_scale * lvl
		# the lens follows the lamp -- unless the level's power is cut, when
		# the binder has zeroed it and it stays zeroed
		var root := _find_lux_root()
		if root == null or root.fixtures_powered():
			for e in _lenses:
				(e[2] as BaseMaterial3D).emission_energy_multiplier = float(e[3]) * lvl
		return
	if r.flicker_amount <= 0.0:
		return
	_flicker_phase += delta * r.flicker_speed
'''),
]

STREET = [
    ('''var _lights: Array[SpotLight3D] = []
var _cones: Array[MeshInstance3D] = []
var _flicker_phase: float = 0.0
''', '''var _lights: Array[SpotLight3D] = []
var _cones: Array[MeshInstance3D] = []
var _flicker_phase: float = 0.0
## A failing pole's clock and its lenses (0.62.0): see LuxFluorescentRig.
var _fail_t: float = 0.0
var _lenses: Array = []
'''),
    ('''	var root := _find_lux_root()
	if root != null:
		for l in _lights:
			root.register_lux_light(l)


func _rebuild() -> void:
	# Sweep every built child by TYPE, not just what this instance's arrays
''', '''	var root := _find_lux_root()
	if root != null:
		for l in _lights:
			root.register_lux_light(l)
	_bind_lenses.call_deferred()        # after the spawner has placed the rig
	if rig != null and rig.failing_kind != LuxFailing.NONE and rig.bake_mode != 1:
		set_process(true)


## A cycling pole dims its own lens with its lamp (0.62.0): the nearest lit
## face to each lamp within a metre and a half, given a material of its own.
func _bind_lenses() -> void:
	_lenses.clear()
	if rig == null or rig.failing_kind == LuxFailing.NONE or rig.bake_mode == 1:
		return
	var scene: Node = owner if owner != null else get_tree().current_scene
	if scene == null:
		scene = get_tree().root
	for l in _lights:
		var hit: Array = LuxFailing.find_lens(scene, l.global_position, 1.5)
		if hit.is_empty():
			continue
		var mi: MeshInstance3D = hit[0]
		var s: int = hit[1]
		var mat: BaseMaterial3D = mi.get_active_material(s) as BaseMaterial3D
		if mat == null:
			continue
		var own: BaseMaterial3D = mat.duplicate() as BaseMaterial3D
		own.resource_name = mat.resource_name
		mi.set_surface_override_material(s, own)
		_lenses.append([mi, s, own, own.emission_energy_multiplier])


func _rebuild() -> void:
	# Sweep every built child by TYPE, not just what this instance's arrays
'''),
    ('''	var fr := rig if rig != null else null
	if fr != null and fr.flicker_amount > 0.0 and fr.bake_mode != 1:
		_flicker_phase += _delta * fr.flicker_speed
''', '''	var fr := rig if rig != null else null
	if fr != null and fr.failing_kind != LuxFailing.NONE and fr.bake_mode != 1:
		# a sodium lamp at the end of its life: dims, cuts out, restrikes
		_fail_t += _delta
		var lvl := LuxFailing.level(fr.failing_kind, fr.failing_seed, _fail_t)
		for fl in _lights:
			if is_instance_valid(fl):
				fl.light_energy = fr.energy * lvl
		var root := _find_lux_root()
		if root == null or root.fixtures_powered():
			for e in _lenses:
				(e[2] as BaseMaterial3D).emission_energy_multiplier = float(e[3]) * lvl
	elif fr != null and fr.flicker_amount > 0.0 and fr.bake_mode != 1:
		_flicker_phase += _delta * fr.flicker_speed
'''),
]

LOADER = [
    ('''			r.mount_height = FLUORESCENT_MOUNT
			r.flicker_amount = 0.12
			r.flicker_speed = 9.0
			_make_downlight(r)
''', '''			r.mount_height = FLUORESCENT_MOUNT
			# STEADY (0.62.0). Every row hummed at 12 % and 9 Hz and the walker
			# called the lights frozen: a smooth hum is invisible and a whole
			# building in step is uniform. ONE tube a room fails instead --
			# `LuxFixtureSpawner` chooses it and sets `failing_kind`.
			r.flicker_amount = 0.0
			_make_downlight(r)
'''),
    ('''			rb.mount_height = 0.0
			rb.flicker_amount = 0.06
			rb.flicker_speed = 2.5
			_make_downlight(rb)
''', '''			rb.mount_height = 0.0
			# steady (0.62.0): one bulb an anchor wavers, by the spawner's choice
			rb.flicker_amount = 0.0
			_make_downlight(rb)
'''),
    ('''			if String(a.get("id", "")).hash() % 3 == 0:
				rs.flicker_amount = 0.22
				rs.flicker_speed = 7.0
''', '''			if String(a.get("id", "")).hash() % 3 == 0:
				# 0.62.0: it CYCLES rather than buzzes -- dims, cuts out, sits
				# dark, restrikes -- and its lens goes with it (the walker's
				# call, 2026-10-02: "go with cycling streetlights")
				rs.failing_kind = LuxFailing.CYCLING
				rs.failing_seed = int(String(a.get("id", "")).hash() & 0x7fffffff)
'''),
]

SPAWNER = [
    ('''	var made := 0
	var skipped: Array = []
	for m in markers:
		var mk := m as Node3D
		var t := marker_type(mk)
''', '''	# ONE FAILING FIXTURE AN ANCHOR (0.62.0). A ceiling row is a room's
	# anchor; its markers are its lamps. The hash of the anchor id picks one
	# lamp of each fluorescent row to stutter and one pendant of each run
	# to waver, so the same tube fails in every build of a seed. Everything
	# else is steady, which is what makes the failing one read.
	var failing: Dictionary = choose_failing(markers)

	var made := 0
	var skipped: Array = []
	for m in markers:
		var mk := m as Node3D
		var t := marker_type(mk)
'''),
    ('''		if rig is LuxAreaLightRig:
			# The hardware IS the panel. Zoo's sign cabinet carries its own
''', '''		if failing.has(mk) and rig.get("rig") is LuxLightRig:
			var res: LuxLightRig = rig.get("rig")
			res.failing_kind = int(failing[mk][0])
			res.failing_seed = int(failing[mk][1])
			res.flicker_amount = 0.0
		if rig is LuxAreaLightRig:
			# The hardware IS the panel. Zoo's sign cabinet carries its own
'''),
    ('''## `base`, or `base_dup<k>` for the first k from 2 that no child of
''', '''## Which markers fail, and how: ``{marker: [kind, seed]}``. One a
## `lux_anchor_id` among the fluorescent and pendant markers, chosen by the
## anchor id's hash -- deterministic, and an authored rename is the only
## thing that moves it. Markers with no anchor id are grouped by their type.
static func choose_failing(markers: Array) -> Dictionary:
	var groups: Dictionary = {}
	for m in markers:
		var mk := m as Node3D
		var t := marker_type(mk)
		var kind := LuxFailing.NONE
		if t == "fluorescent":
			kind = LuxFailing.STUTTER
		elif t == "pendant":
			kind = LuxFailing.WAVER
		else:
			continue
		var anchor := String(marker_payload(mk, "lux_anchor_id", t))
		if not groups.has(anchor):
			groups[anchor] = [kind, []]
		(groups[anchor][1] as Array).append(mk)
	var out: Dictionary = {}
	for anchor in groups:
		var kind: int = groups[anchor][0]
		var lamps: Array = groups[anchor][1]
		var seed: int = int(String(anchor).hash() & 0x7fffffff)
		out[lamps[seed % lamps.size()]] = [kind, seed]
	return out


## `base`, or `base_dup<k>` for the first k from 2 that no child of
'''),
]

ROOT = [
    ('func set_fixtures_powered(on: bool) -> void:\n\tif _lighting != null:\n\t\t_lighting.set_fixtures_powered(on)\n', 'func set_fixtures_powered(on: bool) -> void:\n\tif _lighting != null:\n\t\t_lighting.set_fixtures_powered(on)\n\n\n## Whether the fixtures are powered (0.62.0): a failing rig asks before it\n## writes its lens, so a cut level stays dark.\nfunc fixtures_powered() -> bool:\n\treturn _lighting == null or _lighting.fixtures_powered()\n'),
]


def main():
    v = (LUX / "VERSION").read_text(encoding="utf-8").strip()
    assert v == "Lux 0.61.0", v
    _edit("addons/lux/resources/lux_light_rig.gd", RIG_RES)
    _edit("addons/lux/runtime/rigs/lux_fluorescent_rig.gd", FLUORO)
    _edit("addons/lux/runtime/rigs/lux_streetlight_rig.gd", STREET)
    _edit("addons/lux/runtime/lux_light_loader.gd", LOADER)
    _edit("addons/lux/runtime/lux_fixture_spawner.gd", SPAWNER)
    _edit("addons/lux/runtime/lux_root.gd", ROOT)
    for src, dst in (("lux_failing.gd", "addons/lux/runtime/lux_failing.gd"),
                     ("failing_fixtures_selftest.gd", "tools/failing_fixtures_selftest.gd")):
        (LUX / dst).write_bytes((HERE / "lux_failing" / src).read_bytes())
    (LUX / "VERSION").write_bytes(b"Lux 0.62.0")
    print("0.61.0 -> 0.62.0 (changelog is written separately)")


if __name__ == "__main__":
    main()
