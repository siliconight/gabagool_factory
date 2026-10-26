extends SceneTree
# Loads a walk copy's _walk.tscn headless and prints what the sky-life nodes carry: class, custom AABB, the
# multimesh's instance count and buffer length, the material's shader path. Measurements only.

func _init() -> void:
	var ps: PackedScene = load("res://_walk.tscn")
	var root: Node = ps.instantiate()
	for n in ["SkyBirds", "SkyPlane"]:
		var g: Node = root.get_node_or_null(n)
		if g == null:
			print("%s: absent" % n)
			continue
		var mmi := g as MultiMeshInstance3D
		var mm: MultiMesh = mmi.multimesh
		var mat: ShaderMaterial = mmi.material_override
		print("%s: %s custom_aabb %s aabb %s count %d buffer %d custom %s shader %s" % [
			n, g.get_class(), str(mmi.custom_aabb), str(mmi.get_aabb()), mm.instance_count,
			mm.buffer.size(), str(mm.use_custom_data), mat.shader.resource_path])
	root.free()
	quit()
