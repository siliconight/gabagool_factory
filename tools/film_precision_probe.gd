extends Node
## Measures the precision of the render target the Lux post pass reads from
## (roadmap item 61, film emulsion TDD section 20).
##
## Driven by tools/film_precision_probe.py -- see that file for invocation.
## Registered as an autoload by godot_probe.add_autoload, so it starts before
## the main scene and does not modify the project under test.
##
## WHY THIS EXISTS. The film emulsion TDD forbids converting scene color to
## RGB8 before the film math runs. Whether Lux already does that is not a
## property of any Lux source file -- it is decided by the viewport's render
## target format, which is set by `rendering/viewport/hdr_2d` and defaults off.
## The class reference is not authority enough for a decision that costs
## 7.5 MiB at 1080p, and the reference consulted was for a different engine
## version than the one this project runs. Godot itself is the authority.
##
## WHY IT COVERS THE SCREEN. The question is what the render TARGET can hold,
## not what the scene happens to contain. A full-rect ColorRect on a high
## CanvasLayer writes a known shallow ramp over everything -- including Lux's
## own post pass at layer -1 -- so the value read back is the value written,
## and any levels missing from it were lost by the target and nothing else.
##
## TWO MEASUREMENTS, DELIBERATELY REDUNDANT. `Image.get_format()` answers
## directly. The distinct-level count answers empirically. They are reported
## separately and the driver compares them: a format that says 16-bit while
## the ramp survives in 256 steps is a finding, not a rounding error.
##
## THIS PROBE NEEDS A DISPLAY. `--headless` disables rendering outright, so
## there is nothing to read back. The driver runs it with a real driver.

const BEGIN := "<<<FILM_PRECISION_JSON"
const END := "FILM_PRECISION_JSON>>>"

## A deliberately shallow ramp. Over a 1920 px row a 0.0 -> 1.0 ramp would be
## resolvable by an 8-bit target too (256 codes, 1920 samples); a 0.10-wide one
## can carry at most 26 distinct 8-bit codes, so 8-bit and 16-bit answers differ
## by an order of magnitude instead of by a fraction.
const RAMP_LOW := 0.20
const RAMP_HIGH := 0.30

const RAMP_SHADER := """
shader_type canvas_item;
uniform float ramp_low = 0.2;
uniform float ramp_high = 0.3;
void fragment() {
	float v = mix(ramp_low, ramp_high, UV.x);
	COLOR = vec4(vec3(v), 1.0);
}
"""

var _done: bool = false


func _ready() -> void:
	call_deferred("_run")


func _fail(why: String) -> void:
	# No fence. godot_probe treats a missing fence as "nothing was measured",
	# which is the correct reading -- never as a pass.
	push_error("[film_precision_probe] " + why)
	print("[film_precision_probe] FAILED TO MEASURE: " + why)
	get_tree().quit(2)


func _run() -> void:
	if _done:
		return
	_done = true

	var vp := get_viewport()
	if vp == null:
		_fail("no viewport")
		return

	# --- what the project asked for, before anything is drawn ---
	var setting_present: bool = ProjectSettings.has_setting("rendering/viewport/hdr_2d")
	var setting_value: Variant = (
		ProjectSettings.get_setting("rendering/viewport/hdr_2d")
		if setting_present else null
	)
	var vp_hdr_2d: bool = false
	if "use_hdr_2d" in vp:
		vp_hdr_2d = bool(vp.get("use_hdr_2d"))

	# --- write a known ramp over the whole target ---
	var layer := CanvasLayer.new()
	layer.layer = 128  # above Lux's post pass at -1 and any UI
	add_child(layer)

	var rect := ColorRect.new()
	rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sh := Shader.new()
	sh.code = RAMP_SHADER
	var mat := ShaderMaterial.new()
	mat.shader = sh
	mat.set_shader_parameter("ramp_low", RAMP_LOW)
	mat.set_shader_parameter("ramp_high", RAMP_HIGH)
	rect.material = mat
	layer.add_child(rect)

	# Two frames: one to lay the rect out at full size, one to draw it.
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw

	var tex := vp.get_texture()
	if tex == null:
		_fail("viewport has no texture -- was this run with --headless?")
		return
	var img: Image = tex.get_image()
	if img == null or img.get_width() < 8:
		_fail("viewport image came back empty (%s) -- rendering is disabled"
			% ("null" if img == null else str(img.get_width())))
		return

	var w: int = img.get_width()
	var h: int = img.get_height()
	var fmt: int = img.get_format()

	# --- count distinct levels along the middle scanline ---
	var y: int = h / 2
	var seen: Dictionary = {}
	var first := Color(0, 0, 0, 0)
	var last := Color(0, 0, 0, 0)
	for x in range(w):
		var c: Color = img.get_pixel(x, y)
		if x == 0:
			first = c
		if x == w - 1:
			last = c
		# Key on the red channel: the ramp is neutral, so R carries the signal.
		# Quantized to 1e-7 so float noise in a 16F readback does not inflate
		# the count -- 1e-7 is finer than 16F can represent at these values.
		seen[snappedf(c.r, 0.0000001)] = true

	var payload := {
		"ramp_low": RAMP_LOW,
		"ramp_high": RAMP_HIGH,
		"width": w,
		"height": h,
		"image_format": fmt,
		"image_format_name": _format_name(fmt),
		"hdr_2d_setting_present": setting_present,
		"hdr_2d_setting_value": setting_value,
		"viewport_use_hdr_2d": vp_hdr_2d,
		"distinct_levels": seen.size(),
		# The count an 8-bit target could carry over this ramp, for comparison.
		"levels_if_rgba8": int(round((RAMP_HIGH - RAMP_LOW) * 255.0)) + 1,
		"first_pixel_r": first.r,
		"last_pixel_r": last.r,
		"godot_version": Engine.get_version_info().get("string", "?"),
		"rendering_method": str(ProjectSettings.get_setting(
			"rendering/renderer/rendering_method", "?")),
		"rendering_driver": str(RenderingServer.get_video_adapter_api_version()),
		"adapter": str(RenderingServer.get_video_adapter_name()),
	}

	print(BEGIN)
	print(JSON.stringify(payload, "  "))
	print(END)
	get_tree().quit(0)


func _format_name(f: int) -> String:
	# Named from the engine's own constants, never from a table on the Python
	# side. There was such a table in film_render_probe.py and it was wrong --
	# 11 as RGBH, when 11 is RGBAF and 14 is RGBH -- which misreported a
	# measured format in three documents. Anything unrecognised is reported by
	# number rather than guessed at.
	match f:
		Image.FORMAT_RGBA8:
			return "RGBA8"
		Image.FORMAT_RGB8:
			return "RGB8"
		Image.FORMAT_RGBAH:
			return "RGBAH (16-bit float)"
		Image.FORMAT_RGBF:
			return "RGBF (32-bit float)"
		Image.FORMAT_RGBH:
			return "RGBH (16-bit float)"
		Image.FORMAT_RGBAF:
			return "RGBAF (32-bit float)"
		Image.FORMAT_RGBE9995:
			return "RGBE9995"
		_:
			return "format id %d" % f
