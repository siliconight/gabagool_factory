extends SceneTree
## Which 3D physics engine a Godot 4.7 project runs (2026-10-12, roadmap 242).
##
## Godot 4.7 carries two 3D physics engines, Godot Physics and Jolt Physics, picked by one project
## setting, `physics/3d/physics_engine`. A factory package names none, and neither does Laser Tag's
## staged evaluation project. This prints the setting as the project holds it and the class of the
## physics server the engine actually started, so a project's engine is read, not assumed. Run it in
## a project with the setting absent and in one with it set to "Jolt Physics":
##
##     godot --headless --path <project> -s res://engine_probe.gd
##
## It measures and stops (`engine_probe.out.txt` beside it is its output on both).
##
## REFUTED, KEPT: the first version printed `PhysicsServer3D.get_class()`, which read
## "PhysicsServer3D" under every setting -- the singleton's own class, not the engine behind it, a
## number that cannot move. The engine is told by its own error path instead: asking the server for a
## body that does not exist raises an error that names the module's source file
## (`modules/godot_physics_3d/...` or `modules/jolt_physics/...`), the same line that showed Godot
## Physics in Laser Tag's job log. The caller reads that line off stderr.


func _initialize() -> void:
	var setting: Variant = ProjectSettings.get_setting("physics/3d/physics_engine", "<absent>")
	print("ENGINE setting=%s version=%s" % [str(setting), Engine.get_version_info().get("string", "?")])
	# no such body: the server's error names the file it was raised in
	PhysicsServer3D.body_get_param(RID(), PhysicsServer3D.BODY_PARAM_MASS)
	quit(0)
