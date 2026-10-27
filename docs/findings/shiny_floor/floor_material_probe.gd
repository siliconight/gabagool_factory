extends SceneTree
## What a floor point is made of, and which reflection probes reach it. Prints and stops.
##
##     godot --headless --path <walk copy> --script res://floor_material_probe.gd -- <scene> <x> <y> <z>
##
## (x, y, z) is a point in the scene's Godot frame (y up), a few cm above the floor. For every MeshInstance3D whose
## world AABB holds the point it prints each surface's material: class, resource name, roughness, its roughness
## texture's path, metallic and specular. For every ReflectionProbe whose box holds it: size, intensity, interior,
## box projection, update mode and ambient mode.


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _walk(n: Node, out: Array) -> void:
	out.append(n)
	for c in n.get_children():
		_walk(c, out)


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	if args.size() < 4:
		print("usage: <scene> <x> <y> <z>")
		_exit(2)
		return
	var packed: PackedScene = load(args[0]) as PackedScene
	if packed == null:
		print("cannot load ", args[0])
		_exit(1)
		return
	var scene: Node = packed.instantiate()
	root.add_child(scene)
	await process_frame
	var at := Vector3(float(args[1]), float(args[2]), float(args[3]))
	var nodes: Array = []
	_walk(scene, nodes)
	var meshes: int = 0
	for n in nodes:
		var mi: MeshInstance3D = n as MeshInstance3D
		if mi != null and mi.mesh != null and mi.is_visible_in_tree():
			var box: AABB = mi.global_transform * mi.get_aabb()
			if not box.grow(0.05).has_point(at):
				continue
			meshes += 1
			print("MESH %s  aabb %s" % [String(scene.get_path_to(mi)), str(box)])
			for s in range(mi.mesh.get_surface_count()):
				var m: Material = mi.get_active_material(s)
				var bm: BaseMaterial3D = m as BaseMaterial3D
				if bm == null:
					print("  surface %d: %s %s" % [s, (m.get_class() if m != null else "<none>"),
						(m.resource_name if m != null else "")])
					continue
				var rt: String = bm.roughness_texture.resource_path if bm.roughness_texture != null else "-"
				print("  surface %d: %s '%s' roughness %.3f roughness_texture %s metallic %.3f specular %.3f"
					% [s, bm.get_class(), bm.resource_name, bm.roughness, rt, bm.metallic, bm.metallic_specular])
		var rp: ReflectionProbe = n as ReflectionProbe
		if rp != null:
			var half: Vector3 = rp.size * 0.5
			var local: Vector3 = rp.global_transform.affine_inverse() * at
			if absf(local.x) <= half.x and absf(local.y) <= half.y and absf(local.z) <= half.z:
				print("PROBE %s  size %s intensity %.3f interior %s box_projection %s update %d ambient_mode %d"
					% [String(scene.get_path_to(rp)), str(rp.size), rp.intensity, str(rp.interior),
						str(rp.box_projection), rp.update_mode, rp.ambient_mode])
	print("meshes holding the point: %d" % meshes)
	_exit(0)
