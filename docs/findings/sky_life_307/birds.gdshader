// Roadmap 307's flock: one MultiMesh of bird quads, every bird's place, heading and wing beat from its instance id
// and the clock -- no script, no per-bird CPU, one draw for the flock. A crossing every PERIOD_S: the flock comes in
// over a chord RADIUS_M from CENTRE, at ALT_M, for CROSS_FRAC of the period, and is collapsed to a point (nothing
// rasterised) for the rest. Which chord comes from the crossing's index and SEED, so a level replays the same.
// PIN_PHASE >= 0 holds the clock (proof frames only); PIN_ANGLE_DEG >= -360 holds the chord's bearing.
// 80 m up, 120 m out: 33 degrees from a street eye -- rowhouses 20 m off hide the sky below about 25.
shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled, world_vertex_coords, shadows_disabled;

uniform vec3 centre = vec3(0.0);
uniform float seed = 0.0;
uniform float period_s = 150.0;
uniform float cross_frac = 0.35;
uniform float radius_m = 120.0;
uniform float span_m = 300.0;
uniform float alt_m = 80.0;
uniform float flock_m = 14.0;
uniform float pin_phase = -1.0;
uniform float pin_angle_deg = -999.0;
uniform vec3 tint : source_color = vec3(0.07, 0.07, 0.08);

float h(float n) {
	return fract(sin(n * 12.9898 + seed * 78.233) * 43758.5453);
}

void vertex() {
	float id = float(INSTANCE_ID);
	float cyc = floor(TIME / period_s + h(1.0));
	float ph = pin_phase >= 0.0 ? pin_phase : fract(TIME / period_s + h(1.0));
	if (ph > cross_frac) {
		VERTEX = vec3(0.0, -500.0, 0.0);
	} else {
		float a = pin_angle_deg > -360.0 ? radians(pin_angle_deg) : 6.2831853 * h(cyc + 3.0);
		vec3 out_dir = vec3(cos(a), 0.0, sin(a));
		vec3 fwd = vec3(-out_dir.z, 0.0, out_dir.x);
		float u = ph / cross_frac;
		// each bird's station in the flock, loosely strung out behind the leader
		vec3 off = vec3((h(id + 11.0) - 0.5) * flock_m, (h(id + 23.0) - 0.5) * flock_m * 0.3,
				-h(id + 37.0) * flock_m);
		float t = TIME + h(id + 5.0) * 10.0;
		off += vec3(sin(t * 0.7), sin(t * 0.9) * 0.4, cos(t * 0.6)) * 0.8;
		vec3 base = centre + out_dir * radius_m + vec3(0.0, alt_m, 0.0) + fwd * mix(-0.5, 0.5, u) * span_m;
		// beat: a few strokes, then a glide, per bird
		float beat = sin(t * (14.0 + 6.0 * h(id + 41.0)));
		float glide = step(0.55, fract(t * 0.25 + h(id + 43.0)));
		vec3 v = VERTEX;
		v.y += abs(v.x) * mix(0.55 * beat, 0.12, glide);
		vec3 side = vec3(fwd.z, 0.0, -fwd.x);
		vec3 wp = side * v.x + vec3(0.0, 1.0, 0.0) * v.y + fwd * v.z;
		VERTEX = base + side * off.x + vec3(0.0, off.y, 0.0) + fwd * off.z + wp;
	}
}

void fragment() {
	ALBEDO = tint;
}
