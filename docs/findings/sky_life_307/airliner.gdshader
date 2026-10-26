// Roadmap 307's airliner: one MultiMesh of unit boxes (fuselage, wing, tailplane, fin, three lights), each scaled
// and placed by its instance transform around the origin, the whole flown down an approach track by the clock.
// One draw for the aircraft and its lights. A pass every PERIOD_S; the track lies OFFSET_M out from CENTRE on a
// bearing from the pass's index and SEED, descending from ALT_M + DESCENT_M to ALT_M over its length. INSTANCE_CUSTOM:
// rgb a colour, a the kind (1 body, 2 red nav, 3 green nav, 4 white strobe). Lights read from NIGHT (0 day .. 1
// night), a body is plain. PIN_PHASE >= 0 holds the clock, PIN_ANGLE_DEG >= -360 the bearing (proof frames only).
shader_type spatial;
render_mode unshaded, cull_back, fog_disabled, world_vertex_coords, shadows_disabled;

uniform vec3 centre = vec3(0.0);
uniform float seed = 0.0;
uniform float period_s = 180.0;
uniform float speed_mps = 75.0;
uniform float track_m = 5000.0;
uniform float offset_m = 1500.0;
uniform float alt_m = 1000.0;
uniform float descent_m = 250.0;
uniform float night = 0.5;
uniform float pin_phase = -1.0;
uniform float pin_angle_deg = -999.0;

varying vec4 kind;

float h(float n) {
	return fract(sin(n * 12.9898 + seed * 78.233) * 43758.5453);
}

void vertex() {
	kind = INSTANCE_CUSTOM;
	float fly = track_m / speed_mps;
	float cyc = floor(TIME / period_s + h(2.0));
	float s = pin_phase >= 0.0 ? pin_phase * period_s : fract(TIME / period_s + h(2.0)) * period_s;
	if (s > fly) {
		VERTEX = vec3(0.0, -500.0, 0.0);
	} else {
		float a = pin_angle_deg > -360.0 ? radians(pin_angle_deg) : 6.2831853 * h(cyc + 7.0);
		vec3 out_dir = vec3(cos(a), 0.0, sin(a));
		vec3 fwd = vec3(-out_dir.z, 0.0, out_dir.x);
		float u = s / fly;
		vec3 base = centre + out_dir * offset_m + fwd * (u - 0.5) * track_m
				+ vec3(0.0, alt_m + descent_m * (1.0 - u), 0.0);
		// local -z is the nose: (-side, up, -fwd) keeps the basis a rotation
		vec3 side = vec3(-fwd.z, 0.0, fwd.x);
		vec3 v = VERTEX;
		VERTEX = base + side * v.x + vec3(0.0, v.y, 0.0) + fwd * -v.z;
	}
}

void fragment() {
	vec3 c = kind.rgb;
	if (kind.a > 1.5) {
		float on = kind.a > 3.5 ? step(0.92, fract(TIME * 0.8)) : 1.0;
		c = mix(vec3(0.72, 0.73, 0.75), c * 4.0 * on, night);
	}
	ALBEDO = c;
}
