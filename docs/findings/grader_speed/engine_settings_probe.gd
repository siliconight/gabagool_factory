extends SceneTree
## Prints the engine settings a staged evaluation actually runs with -- the physics engine, the
## worker pool, the processor count -- and quits. Headless; nothing is loaded or simulated.
##
##     godot --headless --path <staged project> -s <this script>

func _initialize() -> void:
	for key in ["physics/3d/physics_engine", "physics/3d/run_on_separate_thread",
			"threading/worker_pool/max_threads", "threading/worker_pool/low_priority_thread_ratio",
			"physics/common/physics_ticks_per_second", "physics/common/max_physics_steps_per_frame",
			"physics/common/physics_jitter_fix", "navigation/world/map_use_async_iterations",
			"navigation/world/region_use_async_iterations"]:
		var value: Variant = ProjectSettings.get_setting(key, "<unset>")
		print("[settings] %s = %s" % [key, str(value)])
	print("[settings] processor count %d; physics server 3d class %s" % [
		OS.get_processor_count(), PhysicsServer3D.get_class()])
	quit(0)
