extends SceneTree
## Every visible MeshInstance3D with triangles lying wholly inside a world box, per node: how many, their world bounds,
## the surface materials, whether a CollisionObject3D sits above it. Godot world metres, Y up. Measurements only.
## Box: over the office's flight 0 ahead of the walker's finding-4 eye (world 54.6, 2.2, 1.6; b2 placed at 54, 0,
## -0.49), where the frame puts the rod: x 53.6..56.0 (the flight is local x 0..1.6), y 2.6..3.9, z -2.6..1.0.

const BOX_MIN := Vector3(53.6, 2.6, -2.6)
const BOX_MAX := Vector3(56.0, 3.9, 1.0)

var _frame := 0


func _initialize() -> void:
	var ps: PackedScene = load("res://_walk.tscn")
	root.add_child(ps.instantiate())


func _collides(n: Node) -> bool:
	var p: Node = n
	while p != null:
		if p is CollisionObject3D:
			return true
		p = p.get_parent()
	return false


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _process(_d: float) -> bool:
	_frame += 1
	if _frame < 3:
		return false
	var box := AABB(BOX_MIN, BOX_MAX - BOX_MIN)
	for n in root.find_children("*", "MeshInstance3D", true, false):
		var mi: MeshInstance3D = n
		if not mi.is_visible_in_tree() or mi.mesh == null:
			continue
		var wb: AABB = mi.global_transform * mi.get_aabb()
		if not box.intersects(wb):
			continue
		var faces: PackedVector3Array = mi.mesh.get_faces()
		var xf: Transform3D = mi.global_transform
		var count := 0
		var lo := Vector3(INF, INF, INF)
		var hi := Vector3(-INF, -INF, -INF)
		for i in range(0, faces.size(), 3):
			var a: Vector3 = xf * faces[i]
			var b: Vector3 = xf * faces[i + 1]
			var c: Vector3 = xf * faces[i + 2]
			if box.has_point(a) and box.has_point(b) and box.has_point(c):
				count += 1
				lo = lo.min(a).min(b).min(c)
				hi = hi.max(a).max(b).max(c)
		if count == 0:
			continue
		var mats := []
		for s in mi.mesh.get_surface_count():
			var m: Material = mi.get_active_material(s)
			mats.append(m.resource_name if m != null else "null")
		print("FACES %d %s lo %s hi %s collides=%s mats=%s" % [count, mi.get_path(), lo, hi, _collides(mi), mats])
	_exit(0)
	return true
