"""Roadmap 305's far-band PROTOTYPE, applied to a COPY of a walk copy (never a tool repo, never a shipped walk copy):
SkyMint's sky shader composites a horizon strip over the sky, and SkyMint loads it. Anchored; refuses on a miss.

    python proto_apply.py <walk copy> <dir holding horizon_day.png and horizon_night.png>

The strip is equirectangular in azimuth (its u is the panorama's, SKY_COORDS.x) and spans elevation
`horizon_bottom_deg` to `horizon_top_deg`; outside it the sky is untouched. Day and night blend by the panorama's own
`base_sky_blend`, so the strip follows the time of day. Composited last, over the clouds and the sun: the far band
stands in front of the sky. Two texture reads a sky pixel; no geometry.
"""
import pathlib
import shutil
import sys

W = pathlib.Path(sys.argv[1])
A = pathlib.Path(sys.argv[2])
assert "_scratch" in str(W.resolve()), "the prototype goes on a scratch copy only"


def edit(rel, pairs):
    p = W / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:60])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


edit("runtime/skymint/skymint_sky.gdshader", [
    ("""uniform float random_light_strength : hint_range(0.0, 2.0) = 0.4;""",
     """// ---- HORIZON STRIP (roadmap 305 prototype) ----
uniform bool use_horizon = false;
uniform sampler2D horizon_day : source_color, filter_linear, repeat_enable;
uniform sampler2D horizon_night : source_color, filter_linear, repeat_enable;
uniform float horizon_bottom_deg = -1.0;
uniform float horizon_top_deg = 8.0;

uniform float random_light_strength : hint_range(0.0, 2.0) = 0.4;"""),
    ("""    COLOR = final_color;""",
     """    if (use_horizon) {
        float elev = degrees(asin(clamp(dir.y, -1.0, 1.0)));
        float t = (elev - horizon_bottom_deg) / (horizon_top_deg - horizon_bottom_deg);
        if (t >= 0.0 && t <= 1.0) {
            vec2 huv = vec2(SKY_COORDS.x, 1.0 - t);
            vec4 hd = texture(horizon_day, huv);
            vec4 hn = texture(horizon_night, huv);
            vec4 h = mix(hd, hn, base_sky_blend);
            final_color = mix(final_color, h.rgb * mix(sky_exposure, 1.0, base_sky_blend), h.a);
        }
    }
    COLOR = final_color;"""),
])

edit("runtime/skymint/skymint.gd", [
    ("""		_mat.set_shader_parameter("use_cube", false)
	_textures_dirty = false""",
     """		_mat.set_shader_parameter("use_cube", false)
	_textures_dirty = false
	# roadmap 305 prototype, after both branches (cube faces or panorama): a horizon strip beside the project, when there is one
	if ResourceLoader.exists("res://vista/horizon_day.png") and ResourceLoader.exists("res://vista/horizon_night.png"):
		_mat.set_shader_parameter("horizon_day", load("res://vista/horizon_day.png"))
		_mat.set_shader_parameter("horizon_night", load("res://vista/horizon_night.png"))
		_mat.set_shader_parameter("use_horizon", true)"""),
])
(W / "vista").mkdir(exist_ok=True)
for n in ("horizon_day.png", "horizon_night.png"):
    shutil.copy2(A / n, W / "vista" / n)
print("prototype applied to %s" % W)
