extends SceneTree
## Where a package's texture memory goes, by LEAVING ONE PART OUT in a fresh process (roadmap 238).
##
## `texture_resident_probe.gd` freed parts of a loaded level and read the engine's monitor after each, and
## the monitor did not come down with them: 314.7 MiB loaded, 266.9 MiB with the whole scene freed and not
## one of the package's 602 image files left in the resource cache. Whatever holds that, a free is not a
## measurement here. So each arm is its own process: the mission built as its entry script builds it
## (`mission.tscn`'s `_ready` loads each `res://*.tscn` it names, in order, beside its Occluders and its
## Warmup), with one part left out BEFORE it enters the tree, and the monitor read once:
##
##   mission     the package's own `mission.tscn`, loaded as it is: THE CONTROL for `full`
##   full        everything, rebuilt as the entry script builds it
##   -<part>     one of the scenes the entry loads left out (its name without `res://` and `.tscn`)
##   -lightmap   everything, the LightmapGI nodes taken out of the bake scene before it enters the tree
##   -warmup     everything but the Warmup sweep
##   -patlas     everything, the window's positional shadow atlas 0 before anything renders
##   -datlas     everything, the directional shadow atlas 256 before anything renders
##   -shadows    both
##   empty       nothing at all: the window's floor
##
## The read waits for the Warmup's `warmup_finished` and then SETTLE frames (the sweep draws the whole
## level from every station with the culler off; read mid-sweep, a monitor is the sweep's), or MAX_FRAMES
## when there is no Warmup. Prints what it measured and quits; a part that does not load prints so and
## quits, so no run stops on a dialog.
##
##     godot --path <imported package copy> -s res://texture_split_probe.gd -- <arm>

const SETTLE := 60
const MAX_FRAMES := 1800
const NO_WARMUP_FRAMES := 300

var _arm := "full"
var _frames := 0
var _settle := -1
var _warm := false


func _parts() -> PackedStringArray:
	var out: PackedStringArray = []
	var f := FileAccess.open("res://mission.tscn", FileAccess.READ)
	if f == null:
		return out
	var re := RegEx.new()
	re.compile("load\\('(res://[^']+\\.tscn)'\\)")
	for m in re.search_all(f.get_as_text()):
		out.append(m.get_string(1))
	return out


func _on_warmed(_total: int, _ms: float) -> void:
	_settle = 0


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() > 0:
		_arm = args[0]
	var parts := _parts()
	var names: PackedStringArray = []
	for p in parts:
		names.append(p.trim_prefix("res://").trim_suffix(".tscn"))
	print("[split] arm %s; the entry's parts: %s" % [_arm, ", ".join(names)])
	if _arm == "empty":
		return
	# THE SHADOW MAPS, before anything renders: `-patlas` gives the window no positional shadow atlas,
	# `-datlas` a 256 directional one, `-shadows` both; each otherwise `full`
	if _arm == "-patlas" or _arm == "-shadows":
		root.positional_shadow_atlas_size = 0
	if _arm == "-datlas" or _arm == "-shadows":
		RenderingServer.directional_shadow_atlas_set_size(256, true)
	if _arm == "mission":
		# THE CONTROL: the package's own scene, as it runs -- `full` must read what this reads, or the
		# rebuild is not the mission and no arm below means anything
		var ms := load("res://mission.tscn") as PackedScene
		if ms == null:
			print("[split] FAILED to load res://mission.tscn")
			quit(2)
			return
		var m := ms.instantiate()
		root.add_child(m)
		var wu := m.get_node_or_null("Warmup")
		if wu != null and wu.has_signal("warmup_finished"):
			wu.connect("warmup_finished", _on_warmed)
			_warm = true
		return
	var top := Node3D.new()
	root.add_child(top)
	var occ := load("res://occluders.tscn") as PackedScene
	if occ != null:
		top.add_child(occ.instantiate())
	for p in parts:
		var name := p.trim_prefix("res://").trim_suffix(".tscn")
		if _arm == "-" + name:
			continue
		var packed := load(p) as PackedScene
		if packed == null:
			print("[split] FAILED to load %s" % p)
			quit(2)
			return
		var inst := packed.instantiate()
		if _arm == "-lightmap":
			for n in inst.find_children("*", "LightmapGI", true, false):
				n.get_parent().remove_child(n)
				n.free()
		top.add_child(inst)
	if _arm != "-warmup":
		var w := Node3D.new()
		w.name = "Warmup"
		w.set_script(load("res://warmup.gd"))
		top.add_child(w)
		if w.has_signal("warmup_finished"):
			w.connect("warmup_finished", _on_warmed)
			_warm = true


func _process(_delta: float) -> bool:
	_frames += 1
	if _settle >= 0:
		_settle += 1
	var ready := false
	if _arm == "empty" or not _warm:
		ready = _frames >= NO_WARMUP_FRAMES
	else:
		ready = _settle >= SETTLE or _frames >= MAX_FRAMES
	if not ready:
		return false
	var tex := Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED)
	var buf := Performance.get_monitor(Performance.RENDER_BUFFER_MEM_USED)
	var draws := Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
	var how := "after the warm-up"
	if _arm == "empty" or not _warm:
		how = "no warm-up"
	elif _settle < SETTLE:
		how = "WARM-UP NOT FINISHED"
	var fmt := "[split] %-12s texture %.1f MiB, buffers %.1f MiB, draws %d, frame %d (%s)"
	print(fmt % [_arm, tex / 1048576.0, buf / 1048576.0, draws, _frames, how])
	# the reflection probes in the tree at the read, by update mode: each one the atlas must hold
	var modes := {}
	var n_probes := 0
	for n in root.find_children("*", "ReflectionProbe", true, false):
		var rp := n as ReflectionProbe
		if rp == null:
			continue
		n_probes += 1
		modes[rp.update_mode] = int(modes.get(rp.update_mode, 0)) + 1
	var pfmt := "[split] %-12s reflection probes %d (by update_mode %s); atlas setting %s x %s"
	print(pfmt % [_arm, n_probes, str(modes),
		str(ProjectSettings.get_setting("rendering/reflections/reflection_atlas/reflection_count", "?")),
		str(ProjectSettings.get_setting("rendering/reflections/reflection_atlas/reflection_size", "?"))])
	quit(0)
	return true
