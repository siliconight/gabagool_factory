extends SceneTree
## Texture memory, read from the engine (roadmap 237's open check, the walker 2026-10-11:
## "texture memory and compression, worth measuring on a package"). Opens a window -- a headless
## run draws nothing and allocates no texture -- loads the package's scene, waits for the frames
## the engine needs to upload what the scene references, prints Godot's own monitors and quits.
## It never stops on a dialog: a scene that fails to load prints the failure and quits.
##
##     godot --path <imported package copy> --script docs/findings/texture_memory/texture_mem_probe.gd
##
## What the monitors are (Performance): RENDER_TEXTURE_MEM_USED is the bytes of texture memory the
## rendering server holds; RENDER_BUFFER_MEM_USED the vertex/index/uniform buffers; RENDER_VIDEO_MEM_USED
## the two together. Numbers are the renderer's accounting, not a driver query, and compressed
## formats count at their compressed size. The scene is SCENE; FRAMES frames are waited.

const SCENE := "res://mission.tscn"
const FRAMES := 90
var _frames := 0
var _root_node: Node = null


func _initialize() -> void:
	var packed: PackedScene = load(SCENE)
	if packed == null:
		print("[texture_mem] FAILED to load %s" % SCENE)
		quit(2)
		return
	_root_node = packed.instantiate()
	root.add_child(_root_node)
	print("[texture_mem] scene %s loaded; renderer %s; waiting %d frames" % [
		SCENE, RenderingServer.get_rendering_device().get_device_name() if RenderingServer.get_rendering_device() != null else "gl_compatibility", FRAMES])


func _process(_delta: float) -> bool:
	_frames += 1
	if _frames < FRAMES:
		return false
	var tex := Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED)
	var buf := Performance.get_monitor(Performance.RENDER_BUFFER_MEM_USED)
	var vid := Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)
	var objs := Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)
	var prims := Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)
	var draws := Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
	print("[texture_mem] after %d frames: texture %.1f MiB, buffers %.1f MiB, video %.1f MiB; objects %d, primitives %d, draw calls %d" % [
		_frames, tex / 1048576.0, buf / 1048576.0, vid / 1048576.0, objs, prims, draws])
	quit(0)
	return true
