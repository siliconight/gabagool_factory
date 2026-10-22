extends SceneTree
# In game: the walk copy's own scene, then F6 pressed as a key, as a player presses it. Saves frames, quits.
# Args after --: <out prefix>

var prefix: String


func _initialize() -> void:
	prefix = OS.get_cmdline_user_args()[0]
	change_scene_to_file("res://_walk.tscn")
	_run.call_deferred()


func _key(code: Key) -> void:
	for pressed in [true, false]:
		var e := InputEventKey.new()
		e.keycode = code
		e.physical_keycode = code
		e.pressed = pressed
		Input.parse_input_event(e)
		await process_frame


func _snap(tag: String, frames: int) -> void:
	for f in range(frames):
		await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("%s_%s.png" % [prefix, tag])
	print("saved ", tag)


func _find_warmup(n: Node) -> Node:
	if n.has_signal("warmup_finished"):
		return n
	for c in n.get_children():
		var hit: Node = _find_warmup(c)
		if hit != null:
			return hit
	return null


func _run() -> void:
	# the level warms its shaders behind a black screen first; photograph after it says it is done
	var started: int = Time.get_ticks_msec()
	var warm: Node = null
	while warm == null and Time.get_ticks_msec() - started < 20000:
		await process_frame
		warm = _find_warmup(root)
	if warm != null:
		var done := [false]
		warm.connect("warmup_finished", func(_f: int, _ms: float) -> void: done[0] = true)
		while not done[0] and Time.get_ticks_msec() - started < 150000:
			await process_frame
		print("warm-up finished after %d ms: %s" % [Time.get_ticks_msec() - started, str(done[0])])
	await _snap("walk", 120)
	await _key(KEY_F6)
	await _snap("f6", 60)
	await _key(KEY_RIGHT)
	await _snap("f6_next", 40)
	await _key(KEY_F6)
	await _snap("closed", 20)
	quit(0)
