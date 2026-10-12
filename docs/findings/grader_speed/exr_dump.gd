extends SceneTree
## Writes lightmap EXRs out as raw half-float RGBA texels, so another tool can compare two of them
## texel by texel. Prints each image's size and the format Godot read it in, then quits. Run by
## lightmap_compare.py; by hand:
##   godot --headless --script exr_dump.gd -- <in.exr> <out.rgbah> [<in.exr> <out.rgbah> ...]


func _init() -> void:
	var args: PackedStringArray = OS.get_cmdline_user_args()
	var i: int = 0
	while i + 1 < args.size():
		var img: Image = Image.load_from_file(args[i])
		if img == null or img.is_empty():
			print("EXR_DUMP unreadable ", args[i])
		else:
			var fmt: int = img.get_format()
			img.convert(Image.FORMAT_RGBAH)
			var f: FileAccess = FileAccess.open(args[i + 1], FileAccess.WRITE)
			f.store_buffer(img.get_data())
			f.close()
			print("EXR_DUMP ", args[i], " ", img.get_width(), " ", img.get_height(), " ", fmt)
		i += 2
	quit()
