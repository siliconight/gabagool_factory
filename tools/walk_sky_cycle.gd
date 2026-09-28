extends Node
## Walk-copy only: cycle the sky provider's skybox while walking.
##
##   N / shift+N   next / previous skybox, named in the console
##   C             procedural clouds on / off (the preset ships them OFF)
##   ] / [         sky brightness up / down (the preset ships 8.0)
##
## Deliberately does nothing else. Lux owns the grade, LuxSkyProvider owns
## the moon disc and its bearing, and the preset owns the defaults; this only
## turns the one dial a person needs to compare skies by eye now that every
## skybox samples its source cube and none of them carries the pole square.

const NAMES := [
	"techno", "apocalypse", "apocalypse_land", "apocalypse_ocean",
	"classic", "classic_land", "clear", "clear_ocean", "dawn", "dusk",
	"dusk_land", "dusk_ocean", "empty_space", "gray", "moody",
	"netherworld", "sinister", "sinister_land", "sinister_ocean",
	"sunshine",
]

var _prov: Node = null
var _idx: int = 0
var _clouds: bool = false
var _bright: float = 8.0


func _ready() -> void:
	await get_tree().process_frame
	await get_tree().process_frame
	_prov = _find(get_tree().current_scene)
	if _prov == null:
		push_warning("[cycle] no sky provider in this scene")
		return
	_idx = int(_prov.get(&"night_sky"))
	_clouds = float(_prov.get(&"cloud_density")) < 0.999
	_bright = float(_prov.get(&"brightness"))
	print("[cycle] N / shift+N cycles the skybox, C toggles clouds, ] [ brightness")
	_say()


## The provider is a WorldEnvironment with a `night_sky` property. Never by
## node name, and never by class -- Lux makes WorldEnvironments too.
func _find(n: Node) -> Node:
	if n == null:
		return null
	if n is WorldEnvironment and "night_sky" in n:
		return n
	for c in n.get_children():
		var r: Node = _find(c)
		if r != null:
			return r
	return null


func _say() -> void:
	print("[cycle] skybox %2d %-16s clouds %-3s brightness %.2f"
		% [_idx, String(NAMES[_idx]), "on" if _clouds else "off", _bright])


func _unhandled_input(e: InputEvent) -> void:
	if _prov == null:
		return
	var k: InputEventKey = e as InputEventKey
	if k == null or not k.pressed or k.echo:
		return
	if k.keycode == KEY_N:
		_idx = wrapi(_idx + (-1 if k.shift_pressed else 1), 0, NAMES.size())
		_prov.set(&"night_sky", _idx)
		_prov.set(&"day_sky", _idx)
	elif k.keycode == KEY_C:
		_clouds = not _clouds
		# density is a threshold: 1.0 resolves the cloud mask to nothing
		_prov.set(&"cloud_density", 0.52 if _clouds else 1.0)
	elif k.keycode == KEY_BRACKETRIGHT or k.keycode == KEY_BRACKETLEFT:
		# NIGHT DIMS EVERYTHING: at time_of_day 0 the profile's sky_exposure
		# is 0.30 with a cool tint, so a dim sky is the night grade working,
		# not a lost skybox. This is the dial to lift one while comparing.
		_bright = clampf(_bright * (1.4 if k.keycode == KEY_BRACKETRIGHT else 1.0 / 1.4), 0.1, 40.0)
		_prov.set(&"brightness", _bright)
	else:
		return
	_say()
