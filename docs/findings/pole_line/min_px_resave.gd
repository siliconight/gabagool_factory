extends SceneTree
## Does a wire material's `min_px` survive a re-save? (2026-10-12)
##
## Cold run 9264's package carried `shader_parameter/min_px = null` in Lux's re-saved scene
## (`presentation/lux.applied.tscn`) where Lot 0.119.1 wrote `shader_parameter/min_px = 1` in
## `site.tscn`; the colour beside it survived. At runtime a null parameter falls back to the shader's
## default, 1.0 -- the value meant -- so the wires drew right, but a WIRE_MIN_PX other than 1 would be
## lost: a knob with no effect. This writes the same Shader and ShaderMaterial into two scenes, one with
## the integer literal Lot wrote and one with a float literal, loads each and saves it again the way a
## re-save does, headless, and prints the line each saved scene carries. It measures and stops.
##
##     godot --headless --path <an empty project> -s res://min_px_resave.gd
##
## (`min_px_resave.out.txt` beside this file is its output.)

const SHADER := """shader_type spatial;
render_mode unshaded, cull_back;
uniform vec4 colour : source_color = vec4(0.07, 0.07, 0.07, 1.0);
uniform float min_px = 1.0;
void fragment() {
    ALBEDO = colour.rgb;
}
"""


func _initialize() -> void:
	_main.call_deferred()


func _exit(code: int) -> void:
	quit(code)
	await process_frame
	await process_frame
	OS.kill(OS.get_process_id())


func _scene(literal: String) -> String:
	return ("[gd_scene load_steps=3 format=3]\n\n"
		+ "[sub_resource type=\"Shader\" id=\"Shader_site_wires\"]\n"
		+ "code = \"" + SHADER + "\"\n\n"
		+ "[sub_resource type=\"ShaderMaterial\" id=\"Mat_site_wires\"]\n"
		+ "shader = SubResource(\"Shader_site_wires\")\n"
		+ "shader_parameter/colour = Color(0.07, 0.07, 0.07, 1)\n"
		+ "shader_parameter/min_px = " + literal + "\n\n"
		+ "[node name=\"Site\" type=\"Node3D\"]\n\n"
		+ "[node name=\"wire\" type=\"MeshInstance3D\" parent=\".\"]\n"
		+ "material_override = SubResource(\"Mat_site_wires\")\n")


func _main() -> void:
	var failed := 0
	for literal in ["1", "1.0", "2", "2.0"]:
		var src := "res://written_%s.tscn" % literal.replace(".", "_")
		var dst := "res://resaved_%s.tscn" % literal.replace(".", "_")
		var f := FileAccess.open(src, FileAccess.WRITE)
		f.store_string(_scene(literal))
		f.close()
		var packed: PackedScene = load(src)
		if packed == null:
			print("  %-4s could not load" % literal)
			failed += 1
			continue
		var err := ResourceSaver.save(packed, dst)
		var text := FileAccess.get_file_as_string(dst)
		var got := ""
		for line in text.split("\n"):
			if line.begins_with("shader_parameter/min_px"):
				got = line
		var node: Node = packed.instantiate()
		var mat: ShaderMaterial = (node.get_node("wire") as MeshInstance3D).material_override
		print("  written min_px = %-4s  saved again (err %d): %-34s  reads back %s" % [
			literal, err, got if got != "" else "(no min_px line)", str(mat.get_shader_parameter("min_px"))])
		node.free()
	_exit(1 if failed else 0)
