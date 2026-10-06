"""A static sky that is never touched: SkyMint applies its uniforms only when
something changed, and Lux's sky provider writes only when the material's
value differs from what it wants.

Takes ONE argument: a package copy root (for the A/B) or the factory root
(to ship: it then patches lux/addons/skymint/skymint.gd and
lux/addons/lux/runtime/lux_sky_provider.gd). Text-anchored; refuses on a
miss. Never run against Lux while a cold run is in flight.

WHY. `Sky.PROCESS_MODE_QUALITY` re-renders the radiance cubemap when the
sky material changes. SkyMint's `_process` calls `_apply()` every frame,
paused or not, and `_apply` writes about fifteen shader parameters every
time -- so the material is dirty every frame and QUALITY behaves like
REALTIME. The provider adds three more writes a frame for the same reason
(its own docstring: "the provider writes these same parameters from its own
profile every frame, so writing them earlier would be overwritten").

WHAT CHANGES.
  * SkyMint: `_apply()` runs when the clock is advancing, when a property
    setter marked `_dirty`, or when a network time is being chased. A paused
    sky with nothing set applies once (the flag starts true) and never
    again.
  * Provider: before each write, read the parameter back and skip the write
    when it already holds the value. So it still wins the frame SkyMint
    re-applies -- the read differs, it writes -- and on every other frame
    it touches nothing. `process_priority = 100` keeps it after SkyMint.

The look is unchanged by construction: every uniform holds the value it
held before; it is just not re-set. That is checked by the harness's frames
being the same frames, and by a walk.
"""
import pathlib
import sys

ROOT = pathlib.Path(sys.argv[1])
if (ROOT / "lux" / "addons" / "skymint" / "skymint.gd").exists():
    SKYMINT = ROOT / "lux" / "addons" / "skymint" / "skymint.gd"
    PROVIDER = ROOT / "lux" / "addons" / "lux" / "runtime" / "lux_sky_provider.gd"
else:
    SKYMINT = ROOT / "runtime" / "skymint" / "skymint.gd"
    PROVIDER = ROOT / "runtime" / "lux" / "runtime" / "lux_sky_provider.gd"


def edit(path, pairs, label):
    raw = path.read_bytes()
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: %s has mixed endings" % path)
    eol = "\r\n" if crlf else "\n"
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for i, (old, new) in enumerate(pairs):
        if t.count(old) != 1:
            raise SystemExit("REFUSED: %s anchor %d matched %d times"
                             % (label, i, t.count(old)))
        t = t.replace(old, new, 1)
    path.write_bytes((t.replace("\n", eol) if eol == "\r\n" else t).encode("utf-8"))
    print("[patch] %s: %d blocks" % (path, len(pairs)))


SKY_OLD = """	if _net_target >= 0.0:
		time_of_day = _ring_lerp(time_of_day, _net_target, clamp(delta * 1.5, 0.0, 1.0))
		if absf(_ring_diff(time_of_day, _net_target)) < 0.01:
			_net_target = -1.0

	_apply()
"""
SKY_NEW = """	var chasing := _net_target >= 0.0
	if chasing:
		time_of_day = _ring_lerp(time_of_day, _net_target, clamp(delta * 1.5, 0.0, 1.0))
		if absf(_ring_diff(time_of_day, _net_target)) < 0.01:
			_net_target = -1.0

	# ONLY WHEN SOMETHING CHANGED. Every write here dirties the sky material,
	# and a dirty material re-renders the radiance cubemap whatever
	# process_mode says -- so a paused sky re-applied every frame was paying
	# for an animation it was not doing. `_dirty` starts true and every
	# property setter raises it.
	if advancing or chasing or _dirty:
		_apply()
"""

PROV_OLD = """	if _has_direction and sun != null and sun.is_inside_tree():
		# a DirectionalLight3D casts along -basis.z, so the body it stands
		# for lies along +basis.z from the viewer
		mat.set_shader_parameter(P_DIRECTION,
			sun.global_transform.basis.z.normalized())
	if disc_intensity > 0.0:
		if _has_intensity:
			mat.set_shader_parameter(P_INTENSITY, disc_intensity)
		if _has_size:
			mat.set_shader_parameter(P_SIZE, disc_size)
"""
PROV_NEW = """	# WRITE ONLY WHAT DIFFERS. A write dirties the material and a dirty sky
	# material re-renders its radiance cubemap, so three unconditional writes
	# a frame kept a static sky permanently animated. Reading back first
	# costs nothing on the GPU; and on the frame the provider re-applies its
	# own profile the read differs, so this still lands last, as before.
	if _has_direction and sun != null and sun.is_inside_tree():
		# a DirectionalLight3D casts along -basis.z, so the body it stands
		# for lies along +basis.z from the viewer
		_set_if_changed(mat, P_DIRECTION, sun.global_transform.basis.z.normalized())
	if disc_intensity > 0.0:
		if _has_intensity:
			_set_if_changed(mat, P_INTENSITY, disc_intensity)
		if _has_size:
			_set_if_changed(mat, P_SIZE, disc_size)


func _set_if_changed(mat: ShaderMaterial, name: String, value: Variant) -> void:
	var cur: Variant = mat.get_shader_parameter(name)
	if typeof(cur) == typeof(value) and cur == value:
		return
	mat.set_shader_parameter(name, value)
"""


def main() -> int:
    edit(SKYMINT, [(SKY_OLD, SKY_NEW)], "skymint.gd")
    edit(PROVIDER, [(PROV_OLD, PROV_NEW)], "lux_sky_provider.gd")
    return 0


if __name__ == "__main__":
    sys.exit(main())
