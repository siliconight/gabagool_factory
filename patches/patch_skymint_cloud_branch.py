"""SkyMint: skip the cloud work when there are no clouds.

Text-anchored on the shader; refuses on any miss. Takes ONE argument: the
path of a `skymint_sky.gdshader` -- the one in a package copy for the A/B,
or `lux/addons/skymint/skymint_sky.gdshader` to ship it. Never run against
Lux while a cold run is in flight.

WHAT WAS MEASURED FIRST (cold run 9090, sky provider on/off, same package,
same harness back to back): about 1.3 ms GPU and 0.2-1.7 ms p95 at every
station, on identical draw counts. A per-pixel cost.

WHAT THE SHADER DOES WITH CLOUDS OFF. `cloud_density = 1.0` is how the
Delco Night preset turns clouds off, and the mask it produces is exactly
zero: `smoothstep(1.0, 1.16, noise)` with noise in [0, 1]. But the five
noise fetches, the `pow`, and every line of cloud lighting and colour run
before that mask is applied, and `mix(sky, cloud_color, 0.0)` throws the
result away. Clouds off is a look, not a saving.

THE ONE THING THAT CHANGES. `thickness` -- smoothstep of the cloud noise --
feeds `glow_occlusion`, which dims the sun's glow where cloud would be
thick, even when the mask is zero. With the block skipped, thickness is 0
and the glow is unoccluded: brighter by up to 85% in the texels where the
(invisible) noise was densest. That is a change to the moon's halo at
night and it is for the walker to judge; it is not hidden here.

The branch is on a uniform, so every pixel takes the same side and there is
no divergence cost.
"""
import pathlib
import sys

SHADER = pathlib.Path(sys.argv[1])

OLD_NOISE_TO_MASK = """    // ---- NOISE ----
    float base_noise = texture(cloud_noise_texture, cloud_uv + macro_shift).r;
    float secondary_noise = texture(cloud_noise_texture,
        cloud_uv * 0.55 + vec2(0.23, 0.37) + evolution_offset * 0.4).r;
    float detail_noise = texture(cloud_noise_texture,
        cloud_uv * 2.4 + evolution_offset).r;

    float noise = base_noise + secondary_noise * 0.5 - detail_noise * detail_strength;

    // ---- EDGE TURBULENCE ----
    float edge_noise = texture(cloud_noise_texture,
        cloud_uv * edge_warp_scale + evolution_offset * 1.7).r;
    edge_noise = (edge_noise - 0.5) * edge_warp_strength;
    noise += edge_noise * (1.0 - abs(noise - 0.5) * 2.0);

    noise = clamp(noise, 0.0, 1.0);
    noise = pow(noise, cloud_contrast);

    // ---- CLOUD MASK ----
    float clouds = smoothstep(cloud_density, cloud_density + cloud_softness, noise);
    float overhead_mask = pow(max(dir.y, 0.0), 0.35);
    clouds *= mix(horizon_fade, zenith_density, overhead_mask);
"""
NEW_NOISE_TO_MASK = """    // NO CLOUDS, NO CLOUD WORK. cloud_density 1.0 is "clouds off" and gives
    // a mask of exactly zero -- but the five fetches, the pow and the cloud
    // lighting below all ran anyway and were thrown away by the final mix.
    // Measured on cold run 9090 at about 1.3 ms GPU a frame. The branch is
    // on a uniform, so it costs no divergence. `thickness` is what the sun
    // glow's occlusion reads; with the block skipped it is 0 and the glow
    // is unoccluded, which is the one visible difference.
    bool cloud_work = cloud_density < 1.0;
    float noise = 0.0;
    float clouds = 0.0;
    if (cloud_work) {
        // ---- NOISE ----
        float base_noise = texture(cloud_noise_texture, cloud_uv + macro_shift).r;
        float secondary_noise = texture(cloud_noise_texture,
            cloud_uv * 0.55 + vec2(0.23, 0.37) + evolution_offset * 0.4).r;
        float detail_noise = texture(cloud_noise_texture,
            cloud_uv * 2.4 + evolution_offset).r;

        noise = base_noise + secondary_noise * 0.5 - detail_noise * detail_strength;

        // ---- EDGE TURBULENCE ----
        float edge_noise = texture(cloud_noise_texture,
            cloud_uv * edge_warp_scale + evolution_offset * 1.7).r;
        edge_noise = (edge_noise - 0.5) * edge_warp_strength;
        noise += edge_noise * (1.0 - abs(noise - 0.5) * 2.0);

        noise = clamp(noise, 0.0, 1.0);
        noise = pow(noise, cloud_contrast);

        // ---- CLOUD MASK ----
        clouds = smoothstep(cloud_density, cloud_density + cloud_softness, noise);
        float overhead_mask = pow(max(dir.y, 0.0), 0.35);
        clouds *= mix(horizon_fade, zenith_density, overhead_mask);
    }
"""

OLD_LIGHTING_TO_HORIZON = """    // ---- CLOUD LIGHTING ----
    float sun_height = light_dir.y;
    float day_factor = clamp(sun_height * 3.0, 0.0, 1.0);   // 1 = day, 0 = sunset/night

    float top_light = max(dir.y, 0.0);
    float bottom_light = pow(1.0 - max(dir.y, 0.0), 1.5);
    float vertical_light = mix(bottom_light, top_light, day_factor);

    float sun_wrap = pow(clamp(dot(dir, light_dir) * 0.5 + 0.5, 0.0, 1.0), 1.5);
    float edge_light = pow(1.0 - thickness, 2.2) * vertical_light * sun_wrap;
    float body_shadow = thickness * mix(0.45, 0.75, day_factor);

    // ---- RANDOM LIGHT SCATTERING ----
    float random_light = texture(cloud_noise_texture,
        cloud_uv * random_light_scale + evolution_offset * 0.2).r;
    random_light = smoothstep(0.6, 0.92, random_light);

    // ---- FINAL LIGHTING ----
    float lighting = edge_light * 1.3 + random_light * random_light_strength
        - body_shadow - thickness * 0.15;
    lighting = clamp(lighting, 0.0, 1.0);

    // ---- CLOUD COLOR ----
    vec3 cloud_color = mix(cloud_dark_color, cloud_mid_color, lighting);
    cloud_color = mix(cloud_color, cloud_bright_color, edge_light);

    // ---- ATMOSPHERIC BLENDING ----
    float atmosphere_factor = mix(atmosphere_horizon_strength,
        atmosphere_zenith_strength, max(dir.y, 0.0));
    atmosphere_factor *= atmosphere_blend;
    cloud_color = mix(cloud_color, base_sky, atmosphere_factor);
    cloud_color *= cloud_brightness;

    // ---- HORIZON ATMOSPHERE ----
    float horizon_amount = pow(1.0 - max(dir.y, 0.0), 2.5);
    cloud_color = mix(cloud_color, base_sky, horizon_amount * horizon_blend);
"""
NEW_LIGHTING_TO_HORIZON = """    vec3 cloud_color = base_sky;
    if (cloud_work) {
        // ---- CLOUD LIGHTING ----
        float sun_height = light_dir.y;
        float day_factor = clamp(sun_height * 3.0, 0.0, 1.0);   // 1 = day, 0 = sunset/night

        float top_light = max(dir.y, 0.0);
        float bottom_light = pow(1.0 - max(dir.y, 0.0), 1.5);
        float vertical_light = mix(bottom_light, top_light, day_factor);

        float sun_wrap = pow(clamp(dot(dir, light_dir) * 0.5 + 0.5, 0.0, 1.0), 1.5);
        float edge_light = pow(1.0 - thickness, 2.2) * vertical_light * sun_wrap;
        float body_shadow = thickness * mix(0.45, 0.75, day_factor);

        // ---- RANDOM LIGHT SCATTERING ----
        float random_light = texture(cloud_noise_texture,
            cloud_uv * random_light_scale + evolution_offset * 0.2).r;
        random_light = smoothstep(0.6, 0.92, random_light);

        // ---- FINAL LIGHTING ----
        float lighting = edge_light * 1.3 + random_light * random_light_strength
            - body_shadow - thickness * 0.15;
        lighting = clamp(lighting, 0.0, 1.0);

        // ---- CLOUD COLOR ----
        cloud_color = mix(cloud_dark_color, cloud_mid_color, lighting);
        cloud_color = mix(cloud_color, cloud_bright_color, edge_light);

        // ---- ATMOSPHERIC BLENDING ----
        float atmosphere_factor = mix(atmosphere_horizon_strength,
            atmosphere_zenith_strength, max(dir.y, 0.0));
        atmosphere_factor *= atmosphere_blend;
        cloud_color = mix(cloud_color, base_sky, atmosphere_factor);
        cloud_color *= cloud_brightness;

        // ---- HORIZON ATMOSPHERE ----
        float horizon_amount = pow(1.0 - max(dir.y, 0.0), 2.5);
        cloud_color = mix(cloud_color, base_sky, horizon_amount * horizon_blend);
    }
"""


def main() -> int:
    raw = SHADER.read_bytes()
    if raw.count(b"\r\n") not in (0, raw.count(b"\n")):
        raise SystemExit("REFUSED: mixed endings")
    eol = "\r\n" if raw.count(b"\r\n") else "\n"
    t = raw.decode("utf-8").replace("\r\n", "\n")
    if "cloud_work" in t:
        raise SystemExit("REFUSED: already patched")
    for label, old, new in (("noise..mask", OLD_NOISE_TO_MASK, NEW_NOISE_TO_MASK),
                            ("lighting..horizon", OLD_LIGHTING_TO_HORIZON, NEW_LIGHTING_TO_HORIZON)):
        if t.count(old) != 1:
            raise SystemExit("REFUSED: %s matched %d" % (label, t.count(old)))
        t = t.replace(old, new, 1)
    SHADER.write_bytes(t.replace("\n", eol).encode("utf-8"))
    print("[patch] %s: cloud work branched on cloud_density < 1.0" % SHADER)
    return 0


if __name__ == "__main__":
    sys.exit(main())
