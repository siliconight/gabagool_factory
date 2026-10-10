# Roadmap 202: does a Godot executable deliver a headless script's output to a pipe? Run under each:
#     <godot exe> --headless -s docs/findings/stranger_install/godot_pipe.gd > out.txt 2> err.txt
# stdout should carry PIPE_OK 42 and stderr PIPE_ERR. It prints and quits; it judges nothing.
extends SceneTree

func _initialize() -> void:
	print("PIPE_OK %d" % 42)
	push_error("PIPE_ERR")
	quit(0)
