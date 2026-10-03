extends SceneTree
## Scratch probe: for every streetlight in a walk copy, is its lamp on, is
## its lens lit, and how many lights does the ground mesh under it have to
## carry? GL Compatibility lights at most 8 per mesh (max_lights_per_object);
## a tile with more drops the rest. Headless. Prints what it measured.

const CAP: int = 8


func _initialize() -> void:
	_run.call_deferred()


func _walk(n: Node, lights: Array, meshes: Array, poles: Array) -> void:
	if n is OmniLight3D or n is SpotLight3D:
		lights.append(n)
	var mi: MeshInstance3D = n as MeshInstance3D
	if mi != null and mi.mesh != null:
		meshes.append(mi)
	if n is LuxStreetlightRig:
		poles.append(n)
	for c in n.get_children():
		_walk(c, lights, meshes, poles)


func _range(l: Light3D) -> float:
	if l is OmniLight3D:
		return (l as OmniLight3D).omni_range
	return (l as SpotLight3D).spot_range


func _touches(l: Light3D, box: AABB) -> bool:
	var r: float = _range(l)
	var p: Vector3 = l.global_position
	var q: Vector3 = Vector3(clampf(p.x, box.position.x, box.end.x), clampf(p.y, box.position.y, box.end.y), clampf(p.z, box.position.z, box.end.z))
	return p.distance_to(q) <= r


func _run() -> void:
	change_scene_to_file("res://mission.tscn")
	for _i in range(90):
		await process_frame
	var lights: Array = []
	var meshes: Array = []
	var poles: Array = []
	_walk(root, lights, meshes, poles)
	print("POLE lights=", lights.size(), " meshes=", meshes.size(), " poles=", poles.size())
	for pole in poles:
		var lamp: Light3D = null
		for c in pole.get_children():
			if c is Light3D:
				lamp = c
		if lamp == null:
			continue
		var lr: LuxLightRig = pole.get("rig")
		var lenses: Array = pole.get("_lenses")
		var lens_e: float = -1.0
		if not lenses.is_empty():
			lens_e = (lenses[0][2] as BaseMaterial3D).emission_energy_multiplier
		# the ground under the lamp: the mesh whose box contains the point 0.1 m up from the lamp's foot
		# the ground under the lamp: the highest thin, wide mesh below the lamp
		# whose footprint holds the lamp's (x, z)
		var lx: float = lamp.global_position.x
		var lz: float = lamp.global_position.z
		var ly: float = lamp.global_position.y
		var ground: MeshInstance3D = null
		var gbox: AABB = AABB()
		for mi in meshes:
			var box: AABB = mi.global_transform * mi.get_aabb()
			if box.size.y < 0.6 and box.size.x * box.size.z > 4.0 and box.end.y < ly 					and lx >= box.position.x and lx <= box.end.x and lz >= box.position.z and lz <= box.end.z:
				if ground == null or box.end.y > gbox.end.y:
					ground = mi
					gbox = box
		var n_lights: int = 0
		var names: Array = []
		if ground != null:
			for l in lights:
				if l.visible and _touches(l, gbox):
					n_lights += 1
					if n_lights <= 12:
						names.append(String(l.get_parent().name))
		# every ground tile this lamp reaches, and how many lights each carries
		var reached: int = 0
		var dropped: int = 0
		var worst: Array = []
		for mi in meshes:
			var box: AABB = mi.global_transform * mi.get_aabb()
			if box.size.y < 0.6 and box.size.x * box.size.z > 4.0 and box.end.y < ly and _touches(lamp, box):
				reached += 1
				var k: int = 0
				for l in lights:
					if l.visible and _touches(l, box):
						k += 1
				if k > CAP:
					dropped += 1
					if worst.size() < 4:
						worst.append("%s:%d" % [String(mi.get_path()).replace("/root/Mission/Site/", ""), k])
		print("POLE %s reaches %d ground tiles, %d of them OVER CAP %s" % [pole.name, reached, dropped, str(worst)])
		print("POLE %s energy=%.2f lens=%.2f failing=%d ground=%s (%.0fx%.0f m) lights_on_ground=%d%s" % [
			pole.name, lamp.light_energy, lens_e, lr.failing_kind if lr != null else -1,
			String(ground.get_path()).replace("/root/Mission/Site/", "") if ground != null else "none",
			gbox.size.x, gbox.size.z, n_lights, "  OVER CAP" if n_lights > CAP else ""])
		if n_lights > CAP:
			print("POLE    ", names)
	# the over-cap OUTDOOR tiles: size, and who is on them
	for mi in meshes:
		var path: String = String(mi.get_path())
		if path.contains("/b0/") or path.contains("/b1/") or path.contains("/b2/"):
			continue
		var box: AABB = mi.global_transform * mi.get_aabb()
		if box.size.y >= 0.6 or box.size.x * box.size.z <= 4.0:
			continue
		var on: Array = []
		for l in lights:
			if l.visible and _touches(l, box):
				on.append("%s(%.0f)" % [String(l.get_parent().name), _range(l)])
		if on.size() > CAP:
			print("TILE %s %.0fx%.0f m at y %.2f carries %d: %s" % [path.replace("/root/Mission/Site/", ""), box.size.x, box.size.z, box.position.y, on.size(), str(on)])
	# every pole lamp's cone: does -Z point down?
	for pole in poles:
		for c in pole.get_children():
			if c is SpotLight3D:
				var sl: SpotLight3D = c
				var down: float = -sl.global_transform.basis.z.y
				print("CONE %s down=%.2f angle=%.0f range=%.1f" % [pole.name, down, sl.spot_angle, sl.spot_range])
	print("POLE done")
	quit(0)
