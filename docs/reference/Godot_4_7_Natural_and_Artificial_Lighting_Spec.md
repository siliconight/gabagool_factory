---
document_id: godot47_natural_artificial_lighting
title: "Natural and Artificial Lighting in Godot 4.7"
document_version: "1.0.0"
schema_version: "1.0.0"
created_date: "2026-10-09"
language: en-US
format: markdown_with_yaml_records
target_engine: Godot
target_engine_version: "4.7"
audience: [game_designer, lighting_artist, gameplay_engineer, rendering_engineer, procedural_generator]
scope: [real_world_light_behavior, interiors, exteriors, day_night_transitions, exposure, implementation, acceptance_tests]
status: implementation_specification
verification:
  api_documentation_checked: true
  machine_records_validated: true
  engine_scene_executed: false
  performance_measured: false
  numeric_presets_production_calibrated: false
---

# Natural and Artificial Lighting in Godot 4.7

Artificial lights normally retain their output as the sun changes. Their prominence changes because the amount of other light reaching each surface changes, and because the camera adapts its exposure. A lamp can be inconspicuous on a sunny street and dominant in a nearby windowless room at the same time.

This document specifies that relationship for human implementation and machine-assisted scene creation. It is a design and engineering specification, not a tested Godot project or a photometric certification.

## 1. Machine-reading contract

Parse the YAML front matter first, then each fenced `yaml` block independently. Each block has a unique `block_id`; assemble a dictionary keyed by that value. Markdown explains the records but does not silently override them. The records are application data, not native Godot resources or settings files.

```yaml
block_id: reading_contract
schema_version: "1.0.0"
identifier_policy:
  rules: "R-NNN"
  tests: "T-NNN"
  sources: "S-NN"
  uniqueness: document_wide_within_identifier_type
requirement_levels:
  MUST: required_for_conformance
  MUST_NOT: prohibited_for_conformance
  SHOULD: recommended_unless_a_reason_is_recorded
  MAY: optional
evidence_classes:
  physical_principle: ordinary_lighting_model
  documented_engine_behavior: supported_by_named_source
  project_policy: authored_requirement_for_this_specification
  illustrative_example: explanatory_value_not_a_calibrated_preset
value_policy:
  null: unresolved_not_zero
  booleans: [true, false]
  numeric_units: explicit_in_field_name_or_unit_field
  enums: case_sensitive_strings
  source_ids: resolve_in_source_register
  test_ids: resolve_in_acceptance_tests
  mandatory_unresolved_values: block_production_profile_signoff
  conflicts: report_and_resolve_do_not_silently_guess
```

Requirements here describe the intended result. Document any deliberate artistic departure, its affected rooms or fixtures, and the acceptance test used to review it. Do not describe an artistic adjustment as a measured physical fact.

## 2. Physical model and terminology

Light contributions add. A source does not become weaker merely because another source is present. The illumination received at a point depends on source output, distance, direction, obstruction, and reflections. A shadow blocks the contribution of its source; another source can still illuminate that location. [S-01]

The camera then maps scene radiance into a displayable image. Exposure is separate from light transport. It changes the image of the entire scene, not the physical output of individual lamps. Godot provides exposure control through camera attributes. [S-03]

| Quantity | Unit | Meaning | Do not confuse with |
| --- | --- | --- | --- |
| Luminous flux | lumen, lm | Total visible output of a source | Illumination at a particular floor point |
| Illuminance | lux, lx | Visible light arriving per square meter | Brightness of a visible bulb or sky pixel |
| Luminance | cd/m², also called nit | Light leaving a surface in a viewing direction | Total fixture output |
| Color temperature | kelvin, K | Warm/cool chromaticity description for suitable sources | Brightness or a complete spectral description |
| Exposure multiplier | dimensionless | Scale applied to the captured/rendered image | An additional light source |
| Distance | meter, m | Spatial separation in this project's scale convention | A light node's transform scale |

The Godot bindings for physical units are listed in Section 6. [S-02, S-04, S-05, S-09]

### 2.1 Equations and assumptions

```yaml
block_id: analytic_model
evidence_class: physical_principle
source_ids: [S-01, S-18, S-19]
equations:
  surface_illuminance:
    expression: "E_total_lux = E_sun_direct_lux + E_sky_direct_lux + E_bounce_lux + E_artificial_direct_lux"
    assumptions:
      - Each term contains only light that actually reaches the same surface point.
      - Bounce includes reflected contributions from all source types; do not count it twice.
      - Direct sky excludes the direct solar term already counted separately.
  artificial_share:
    expression: "share = E_artificial_lux / (E_other_lux + E_artificial_lux)"
    domain: "E_other_lux >= 0; E_artificial_lux >= 0; denominator > 0"
    note: "For source attribution, E_artificial_lux may include its bounce; exclude that bounce from E_other_lux."
  relative_addition:
    expression: "increase_percent = 100 * E_artificial_lux / E_other_lux"
    domain: "E_other_lux > 0"
    zero_baseline_behavior: undefined
  point_source_distance_ratio:
    expression: "E_at_r2 / E_at_r1 = (r1 / r2)^2"
    assumptions:
      - Small source approximated as a point.
      - Same incidence angle and source direction.
      - No changed obstruction, absorption, or engine range attenuation.
      - Distances are outside the immediate near field of the emitter.
interpretation_limits:
  - Illuminance ratios are not perceived-brightness ratios.
  - These equations are not the complete material-shading or camera pipeline.
  - A screenshot pixel value is not a lux measurement.
  - Godot does not supply a universal local-lux field merely by enabling physical units.
```

Surface orientation matters: grazing light spreads its energy across more area. At room scale, the sun is modeled as a directional source rather than a nearby point source. [S-01, S-07]

### 2.2 One unchanged lamp under different surroundings

These synthetic examples fix the lamp's contribution at one surface point to 100 lx. They are calculations, not fixture specifications or universal measurements of these locations. The large daylight value is consistent with Godot's approximate direct-sun reference. [S-02]

```yaml
block_id: contrast_examples
evidence_class: illustrative_example
lamp_contribution_lux: 100.0
rows:
  - {id: example_very_bright, other_lux: 100000.0, total_lux: 100100.0, increase_percent: 0.1}
  - {id: example_bright, other_lux: 10000.0, total_lux: 10100.0, increase_percent: 1.0}
  - {id: example_moderate, other_lux: 1000.0, total_lux: 1100.0, increase_percent: 10.0}
  - {id: example_equal, other_lux: 100.0, total_lux: 200.0, increase_percent: 100.0}
  - {id: example_dim, other_lux: 10.0, total_lux: 110.0, increase_percent: 1000.0}
  - {id: example_very_dark, other_lux: 0.1, total_lux: 100.1, increase_percent: 100000.0}
```

### 2.3 Streetlamps, fireworks, and visible emitters

A streetlamp has at least two observable components: its luminous surface and the illumination it adds to other surfaces. Its bulb can remain visible in daylight while the added pavement illumination becomes difficult to distinguish.

A firework is usually observed against the sky. Its visibility depends on the luminance contrast of the sparks against that background, their angular size, duration, and viewing conditions. Ground illuminance alone does not determine this contrast. Daylight does not switch the sparks off.

Represent a firework's sparks with emissive visual effects and, where warranted, separate short-lived light nodes for environmental illumination. Glow can spread a bright image region but does not provide world illumination or shadows. Emissive contributions through GI depend on the selected technique. [S-09, S-10, S-13]

## 3. Required behavior

```yaml
block_id: requirements
rules:
  - id: R-001
    level: MUST
    evidence_class: physical_principle
    statement: "Combine contributing light sources additively before display mapping."
    source_ids: [S-01]
    test_ids: [T-001, T-003]
  - id: R-002
    level: MUST
    evidence_class: project_policy
    statement: "Keep an operating fixture's output independent of sun brightness unless its explicit dimmer, sensor, schedule, or artistic override changes it."
    source_ids: [S-01]
    test_ids: [T-001]
  - id: R-003
    level: MUST
    evidence_class: project_policy
    statement: "Determine daylight access per location through geometry, openings, shadows, and the indirect-light strategy."
    source_ids: [S-07, S-10]
    test_ids: [T-004]
  - id: R-004
    level: MUST_NOT
    evidence_class: project_policy
    statement: "Use camera exposure as the sole repair for daylight incorrectly reaching an enclosed room."
    source_ids: [S-03]
    test_ids: [T-004, T-007]
  - id: R-005
    level: MUST
    evidence_class: project_policy
    statement: "Treat source emission, world illumination, and image glow as separate responsibilities."
    source_ids: [S-09, S-13]
    test_ids: [T-009]
  - id: R-006
    level: MUST
    evidence_class: project_policy
    statement: "Coordinate direct sun, sky, indirect light, reflections, and camera response through day/night changes."
    source_ids: [S-05, S-10]
    test_ids: [T-006, T-008]
  - id: R-007
    level: SHOULD
    evidence_class: documented_engine_behavior
    statement: "Start omni and spot distance attenuation at 2.0 when targeting inverse-square falloff."
    source_ids: [S-06, S-08]
    test_ids: [T-002]
  - id: R-008
    level: MUST
    evidence_class: project_policy
    statement: "Validate light range and distance culling at night as well as in daylight."
    source_ids: [S-04, S-06, S-08]
    test_ids: [T-005]
  - id: R-009
    level: MUST
    evidence_class: project_policy
    statement: "Keep indirect-light changes consistent with the chosen GI technique and its update limitations."
    source_ids: [S-10, S-11, S-12]
    test_ids: [T-006, T-010]
  - id: R-010
    level: MUST_NOT
    evidence_class: documented_engine_behavior
    statement: "Assume baked daylight in LightmapGI updates when the live sun changes or disappears."
    source_ids: [S-12]
    test_ids: [T-006]
  - id: R-011
    level: MUST_NOT
    evidence_class: documented_engine_behavior
    statement: "Assume moving a door updates SDFGI obstruction immediately."
    source_ids: [S-11]
    test_ids: [T-010]
  - id: R-012
    level: MUST
    evidence_class: project_policy
    statement: "Bound and smooth exposure changes to preserve intended darkness and avoid distracting adaptation."
    source_ids: [S-03, S-14]
    test_ids: [T-007]
  - id: R-013
    level: MUST
    evidence_class: project_policy
    statement: "Select features supported by the project's actual renderer and target hardware."
    source_ids: [S-03, S-10, S-11]
    test_ids: [T-011]
  - id: R-014
    level: MUST
    evidence_class: project_policy
    statement: "Keep measurements, illustrative values, and artistic overrides explicitly distinguishable."
    source_ids: []
    test_ids: [T-012]
  - id: R-015
    level: SHOULD
    evidence_class: project_policy
    statement: "Allow lighting colors to mix through material shading rather than manually averaging source color temperatures."
    source_ids: [S-19, S-07]
    test_ids: [T-003]
  - id: R-016
    level: MUST
    evidence_class: project_policy
    statement: "Profile lighting under the densest intended visible-light and shadow configuration; do not infer FPS from a universal light count."
    source_ids: [S-07]
    test_ids: [T-011]
```

## 4. Spatial and temporal gradients

The gradient is a changing mixture of contributions, not a global rule that weakens all lamps during the day. Evaluate fixtures from gameplay camera positions using the actual room envelope and material palette.

```yaml
block_id: expected_contexts
evidence_class: project_policy
contexts:
  - id: sunlit_street
    natural_input: direct_sun_plus_sky_and_bounce
    expected_result: "Ordinary lamps add relatively little to sunlit pavement; visible bulbs may remain bright."
  - id: covered_exterior
    natural_input: reduced_direct_sun_with_partial_sky_and_bounce
    expected_result: "An unchanged lamp gains prominence compared with an equivalent exposed location."
  - id: window_zone
    natural_input: daylight_through_apertures_plus_bounce
    expected_result: "Daylight and fixture light mix; a direct sun patch may strongly dominate locally."
  - id: deep_interior
    natural_input: limited_aperture_light_and_bounce
    expected_result: "Fixtures can dominate at noon; brightness follows actual daylight access."
  - id: twilight_exterior
    natural_input: diminishing_sky_after_direct_sun_is_lost
    expected_result: "Existing artificial pools, colors, reflections, and shadows become more prominent."
  - id: night_exterior
    natural_input: sky_moon_and_other_environment_sources_as_authored
    expected_result: "Fixtures define local lighting; unlit areas retain the intended darkness."
  - id: sealed_room
    natural_input: none_in_the_ideal_control_scene
    expected_result: "Changing the outdoor sun has negligible influence on the room with exposure locked."
```

Warm artificial light can appear subtle in daylight and strongly warm at night without changing its temperature. Its contribution has become a larger part of the local mixture. A lamp can also fill a sunlight shadow; sunlight can make a lamp's own shadows difficult to distinguish. The material's reflectance and roughness affect the result, so a colored wall or polished surface will not respond like a neutral matte test surface. These are applications of additive light transport through materials. [S-19]

The apparent reach of a lamp may grow at night because its weak outer contribution becomes visible. Its actual distance function remains unchanged. Godot's finite range still truncates that function. [S-06, S-08]

## 5. Scene responsibilities and ownership

Use one authoritative lighting controller for the selected world state. Keep fixture operation separate from the controller that sets natural light. These are project roles, not required node names.

```yaml
block_id: component_contract
components:
  - {id: natural_light_controller, owns: [sun_orientation, sun_output, sky_state, optional_moon_output, world_reflection_refresh]}
  - {id: fixture_controller, owns: [power_state, dimmer, flicker, operating_schedule, emitter_appearance]}
  - {id: room_lighting_model, owns: [apertures, opaque_envelope, gi_strategy, authored_fill, local_probe_coverage]}
  - {id: camera_response_controller, owns: [exposure_mode, adaptation, exposure_bounds]}
  - {id: presentation_profile, owns: [tonemapper, glow, artistic_overrides]}
  - {id: performance_profile, owns: [shadow_quality, distance_fades, gi_quality, probe_update_budget]}
coordinate_policy:
  meters_per_world_unit: 1.0
  classification: project_convention
material_policy:
  calibration_material: neutral_matte_lit_material
  gameplay_materials: consistent_albedo_roughness_and_metallic_workflow
  unshaded_materials: reserve_for_intentional_exceptions
resource_policy:
  - "Avoid unintentionally sharing mutable Environment or material resources across independent states."
  - "A gameplay camera's attributes can override WorldEnvironment camera attributes; test the active camera."
source_ids: [S-14, S-16]
```

For procedural generation, store room openings and opaque boundaries as explicit scene data. A room's `indoor` label is insufficient: a greenhouse, garage with an open door, and sealed basement have different daylight access. Author any substitute bounce lights from openings or reflective surfaces and constrain their influence to the intended space.

## 6. Godot property bindings

Enable physical units in **Project Settings → Rendering → Lights And Shadows → Use Physical Light Units**, restart the editor, and configure camera attributes for the editor/world and gameplay camera. Physical light units and photographic camera controls are separate choices. `CameraAttributesPractical` is suitable when exposure is needed without photographic framing controls. [S-02, S-14]

The table is a binding reference, not a complete preset. `light_energy` multiplies physical intensity, so avoid accidentally authoring the same brightness adjustment in both places. Physical output and material emission use different quantities. [S-04, S-09]

| Object | Exact property or setting | Meaning / policy | Source |
| --- | --- | --- | --- |
| `ProjectSettings` | `rendering/lights_and_shadows/use_physical_light_units` | `true` for the physical-units profile | S-02 |
| `DirectionalLight3D` | `light_intensity_lux` | Direct sun or moon illumination parameter | S-04 |
| `OmniLight3D`, `SpotLight3D` | `light_intensity_lumens` | Fixture output parameter | S-04 |
| `Light3D` | `light_energy` | Dimensionless output multiplier | S-04 |
| `Light3D` | `light_temperature` | Kelvin when physical units are enabled | S-02 |
| `Light3D` | `light_color` | Additional tint; do not unintentionally double-tint temperature | S-02 |
| `Light3D` | `shadow_enabled` | Enable where structural obstruction is required | S-07 |
| `Light3D` | `light_bake_mode` | Select according to the GI method and required updates | S-04, S-11, S-12 |
| `OmniLight3D` | `omni_attenuation`, `omni_range` | Distance exponent and finite reach | S-06 |
| `SpotLight3D` | `spot_attenuation`, `spot_range` | Distance exponent and finite reach | S-08 |
| `SpotLight3D` | `spot_angle` | Angular radius, not full cone width | S-08 |
| `Environment` | `sky`, `background_mode` | Sky resource and background selection | S-05 |
| `Environment` | `background_intensity` | Background luminance parameter in nits with physical units | S-05 |
| `Environment` | `background_energy_multiplier` | Additional background scaling | S-05 |
| `Environment` | `ambient_light_source`, `reflected_light_source` | Select ambient and reflection sources deliberately | S-05 |
| `Environment` | `sdfgi_enabled`, `sdfgi_use_occlusion` | Enable SDFGI; optionally trade cost/artifacts for reduced leaking | S-05, S-11 |
| `CameraAttributes` | `auto_exposure_enabled`, `auto_exposure_speed` | Native adaptation and its response speed | S-03 |
| `CameraAttributes` | `exposure_multiplier` | Global exposure scale | S-03 |
| `CameraAttributesPractical` | `auto_exposure_min_sensitivity`, `auto_exposure_max_sensitivity` | Native bounds; calibrate in the actual scene | S-14 |
| `Environment` | `tonemap_mode` | Selected display mapping, such as AgX or ACES | S-13 |
| `BaseMaterial3D` | `emission_enabled`, `emission_intensity` | Visible emission, with intensity in nits in physical mode | S-09 |
| `BaseMaterial3D` | `emission_energy_multiplier` | Additional emission scaling | S-09 |
| `Environment` | `glow_enabled`, `glow_intensity` | Optional image glow | S-13 |
| `Light3D` | `distance_fade_enabled`, `distance_fade_begin`, `distance_fade_length`, `distance_fade_shadow` | View-distance optimization, not physical falloff | S-04 |
| `ReflectionProbe` | `interior`, `update_mode` | Interior reflection behavior and capture update policy | S-15 |

`ReflectionProbe.interior` removes sky contribution from its reflections; it is not a switch that makes all room illumination physically correct. Probe captures also need an update policy when the scene changes. [S-15]

The sky resource's own output, the environment background multiplier, and physical background intensity all participate in the result. Calibrate the chosen combination; a nits value alone does not normalize every HDR image or procedural sky.

### 6.1 Illustrative fixture record

This is application data for a generator or importer. The sample is intentionally an omni lamp, so a directional fixture's beam distribution is not implied. The 800 lm, 3000 K, and 8 m range are starting examples, not defaults for every lamp or historical fixture type.

```yaml
block_id: fixture_example
evidence_class: illustrative_example
fixture:
  id: calibration_warm_omni
  node_class: OmniLight3D
  output_lumens: 800.0
  temperature_kelvin: 3000.0
  energy_multiplier: 1.0
  distance_attenuation_exponent: 2.0
  range_meters: 8.0
  shadows_enabled: true
  power_state: "on"
  dimmer_fraction: 1.0
  operating_mode: always_on
  daylight_output_coupling: none
  emissive_surface:
    enabled: true
    luminance_nits: null
    calibration_required: true
  artistic_override: null
```

## 7. Indirect lighting and interior strategy

Direct-light shadows do not automatically solve sky ambient occlusion. Excessive global ambient can illuminate a closed room regardless of its windows. Evaluate room darkness before adding exposure adaptation. SSAO is useful for contact detail but is not a complete room-scale daylight solution. [S-13]

| Situation | Candidate strategy | Implementation consequence |
| --- | --- | --- |
| Fixed lighting and geometry prepared in advance | `LightmapGI` | Efficient baked indirect result; changing the source does not update baked light. |
| Changing daylight over mostly static structures in Forward+ | `SDFGI` | Supports changing lights; budget its GPU cost and test leaks and update delay. |
| Bounded scenes needing more dynamic GI participation | `VoxelGI` | Requires volume setup and initial baking; assess coverage and cost. |
| Runtime-generated levels with a constrained GPU budget | Authored fill lights and local probe ambient/reflections | Approximation requires placement and transition rules. |
| Mobile or Compatibility renderer | Supported baked/probe/manual approach | Do not depend on SDFGI or native auto-exposure. |

Technique selection and procedural-generation limitations are documented by Godot. [S-10, S-11, S-12, S-17]

For SDFGI, changing sunlight or long-lived changing fixtures generally requires `Light3D.BAKE_DYNAMIC`. Its dynamic-light support does not mean dynamic doors update obstruction correctly. Thin structures, voxel resolution, and bias can also produce leaks. Test a closed room, a narrow wall, and a moving door before committing to this technique. [S-11]

With LightmapGI, `Dynamic` bake mode still stores the source's indirect contribution in the bake. Direct lighting can change while the old bounce remains. Exclude changing sources from the bake and supply another indirect strategy, use separately authored lighting states with an explicit transition system, or keep the baked lighting condition fixed. Do not promise an automatic day/night lightmap blend. [S-12]

An approximation must retain causal placement: window fill should track the daylight available at that window, while a permanently lit interior fixture should remain independent. Record authored fill lights separately from physical fixtures to prevent double counting when enabling another GI system. [S-17]

## 8. Day/night and exposure implementation

### 8.1 State contract

The following fields are mandatory in a production profile. `null` values are unresolved implementation choices, not instructions to set a property to zero. Choose either physical or artistic units consistently; this specification recommends physical units for the baseline calibration.

```yaml
block_id: project_profile_template
production_ready: false
profile:
  engine_patch_version: null
  renderer: null
  target_hardware: null
  output_resolution_pixels: null
  target_frame_time_ms: null
  physical_light_units_enabled: true
  meters_per_world_unit: 1.0
  gi_strategy: null
  moving_door_indirect_strategy: null
  reflection_update_policy: null
  camera_attributes_class: CameraAttributesPractical
  exposure_mode: null
  exposure_bounds_calibrated: false
  exposure_adaptation_reviewed: false
  tonemapper: null
  daylight_keyframes: null
  shadow_quality_profile: null
  lighting_gpu_budget_ms: null
  approved_reference_captures: []
allowed_values:
  renderer: [forward_plus, mobile, compatibility]
  gi_strategy: [lightmapgi, sdfgi, voxelgi, authored_approximation, documented_hybrid]
  exposure_mode: [fixed, native_auto, scripted_bounded]
  tonemapper: [agx, aces, filmic, reinhard, linear_with_documented_reason]
capability_constraints:
  - "native_auto requires forward_plus."
  - "sdfgi requires forward_plus."
  - "Runtime-generated layouts require a GI preparation/update strategy suitable for runtime generation."
```

### 8.2 Natural-light keyframes

Author at least midday, low sun, twilight, and night. A clock time alone does not establish solar elevation; location, season, weather, and the intended fiction affect it. Suggested values must be calibrated with the actual sky and materials.

```yaml
block_id: daylight_keyframe_contract
required_fields: [id, phase, sun_altitude_degrees, sun_azimuth_degrees, direct_sun_lux, sun_temperature_kelvin, sky_profile_id, sky_background_nits]
optional_fields: [moon_profile_id, weather_profile_id, exposure_profile_id, fog_profile_id]
phase_enum: [midday, low_sun, twilight, night]
constraints:
  - "Direct sun is removed when the authored horizon/occlusion model says it cannot reach the scene."
  - "Twilight may retain substantial skylight after direct sun is gone."
  - "Changing sun direction also changes incidence angles and shadows."
  - "Sky intensity, sky color, and direct-sun intensity need independent curves."
  - "Night skylight, moonlight, and artificial sources are separate contributions."
  - "Do not brighten all lamps automatically as the sun dims."
  - "Do not darken all indoor lamps automatically as the sun brightens."
interpolation:
  intensity: authored_curve
  optional_log_interpolation: positive_values_only
  zero_handling: explicit_transition_to_or_from_zero
  note: "Smooth controls in a perceptually useful domain; do not sum light logarithmically."
```

A sunrise/sunset sensor may legitimately switch a streetlamp. That changes the lamp's operation, not the physical interaction between its light and daylight. Any optimization that disables negligible daytime lights must account for shade and indoor locations instead of using sun height alone.

### 8.3 Controller sequence

This is implementation pseudocode, not directly executable GDScript. No step assumes that Godot automatically calculates a local lux sensor or refreshes every probe.

```text
1. Sample the authored time, weather, and natural-light profile.
2. Apply sun direction, direct intensity, and color.
3. Apply sky state and the calibrated background scaling.
4. Apply optional moon and fog state.
5. Evaluate each fixture's own switch, schedule, dimmer, and flicker.
6. Apply fixture output and its separately calibrated visible emission.
7. Update the selected indirect-light approximation or dynamic GI inputs.
8. Schedule reflection updates according to the project's refresh budget.
9. Update camera exposure using the selected bounded response policy.
10. Render with the approved tone mapping and optional glow.
```

### 8.4 Exposure calibration

First lock exposure within each diagnostic comparison. Adjust source relationships and room obstruction. Then enable the intended adaptation and walk between interior and exterior viewpoints. Native auto-exposure is available only in Forward+; scripted bounded transitions are an alternative where needed. [S-03]

Use an exposure policy that keeps night recognizably dark and avoids strong pumping when a bulb or bright window enters the view. Separate brightening and darkening response times may be implemented in a custom controller; do not assume the single native speed property supplies that distinction. Numerical adaptation times are project choices, not a complete model of human dark adaptation.

AgX and ACES are candidate tonemappers for highlight handling. Pick one before final calibration. Adjust glow after the underlying light balance works; a luminous halo cannot repair absent illumination. [S-13]

## 9. Acceptance tests

These are proposed tests to run in the target project. None are claimed to have been executed in Godot for this document. Keep geometry, materials, camera pose, and exposure fixed within each A/B pair. Compare linear pre-tonemap values only when the project has a validated capture path; ordinary screenshots are visual evidence, not photometric measurements.

Build a compact test scene containing a sunlit patch, an awning, a windowed room, a sealed room, a moving door, matte neutral surfaces, and a roughness reference. Duplicate one fixture with identical settings across these spaces. Capture each required time state with fixture operation forced on, then separately test its schedule.

```yaml
block_id: acceptance_tests
default_execution_status: not_run
tests:
  - id: T-001
    name: fixture_output_invariance
    method: parameter_log
    action: "Sweep midday through night with the same fixture forced on and its dimmer fixed."
    pass: "Output, energy multiplier, temperature, attenuation, range, and authored emitter luminance remain unchanged."
    evidence: [fixture_parameter_log, time_state_log]
  - id: T-002
    name: point_light_falloff
    method: analytic_and_optional_linear_render_comparison
    action: "Check identical normal-incidence targets at r and 2r, well inside the configured range; isolate direct lamp light."
    pass: "The analytic model gives 0.25; a rendered comparison is consistent within an explicitly recorded engine/capture tolerance."
    evidence: [calculation, attenuation_setting, range_setting, optional_linear_capture]
  - id: T-003
    name: additive_and_color_behavior
    method: controlled_visual_comparison
    action: "Capture sources separately and together with exposure fixed; include a warm lamp in a cooler daylight region."
    pass: "The lamp adds illumination and its color becomes more prominent as competing illumination falls."
    evidence: [source_isolation_captures, combined_capture]
  - id: T-004
    name: local_daylight_access
    method: controlled_visual_comparison
    action: "Compare the exposed, awning, windowed, and sealed positions; disable artificial sources for the leak check."
    pass: "Daylight follows available paths; the sealed room does not track outdoor brightness through an unexplained ambient contribution."
    evidence: [room_envelope_capture, fixed_exposure_captures]
  - id: T-005
    name: nighttime_range_and_culling
    method: gameplay_walkthrough
    action: "Walk across lamp range and camera distance-fade boundaries at night and in daylight."
    pass: "No distracting cutoff, light popping, or fixture-illumination mismatch in intended play space."
    evidence: [video, range_and_fade_settings]
  - id: T-006
    name: indirect_light_state_consistency
    method: source_toggle_and_time_sweep
    action: "Remove direct sun and change the sky; inspect formerly sunlit walls and reflected bounce."
    pass: "No unexplained baked daytime illumination remains; any authored approximation matches the selected state."
    evidence: [gi_strategy_record, day_and_night_captures]
  - id: T-007
    name: exposure_transition
    method: gameplay_walkthrough
    action: "Move indoors/outdoors and look between a dark room, bright window, and visible bulb."
    pass: "Adaptation stays within the calibrated bounds without distracting pumping or erasing intended night darkness."
    evidence: [video, exposure_profile]
  - id: T-008
    name: reflection_state_consistency
    method: visual_comparison
    action: "Inspect reflective surfaces after a time change and after entering an interior."
    pass: "Reflections do not retain an inappropriate daytime sky or obsolete lighting beyond the approved refresh behavior."
    evidence: [reflection_captures, probe_update_policy]
  - id: T-009
    name: emission_light_and_glow_separation
    method: controlled_toggle
    action: "Toggle glow, the fixture light node, and material emission independently."
    pass: "Glow changes image spread; the light node changes world illumination; emission changes source appearance and only supported GI contributions."
    evidence: [toggle_captures, emission_gi_configuration]
  - id: T-010
    name: moving_door_lighting
    method: geometry_change
    action: "Open and close the test door while observing direct and indirect light separately."
    pass: "Direct obstruction is correct; the selected indirect strategy's limitations or approximations are acceptable and recorded."
    evidence: [video, moving_door_indirect_strategy]
  - id: T-011
    name: renderer_and_performance
    method: target_hardware_profile
    action: "Run the densest visible light/shadow scene and interior/exterior transition on the selected renderer."
    pass: "Required features operate and measured frame times meet the project's declared budgets."
    evidence: [hardware_record, renderer_record, cpu_gpu_timings, quality_settings]
  - id: T-012
    name: profile_completeness
    method: configuration_review
    action: "Resolve production profile nulls and trace source IDs, overrides, and test evidence."
    pass: "No required field remains unresolved; illustrative values are not mislabeled as measured calibration."
    evidence: [completed_project_profile, exception_register, test_results]
```

For T-002, a finite light range modifies ideal inverse-square behavior near its edge. GI, specular response, exposure, tone mapping, and display encoding can also invalidate a naive screenshot-ratio test. A failed pixel comparison is not automatically evidence that source falloff is wrong. The isolated point-source model is explained in S-18.

Use this result format when the engineering team executes the tests:

```yaml
block_id: test_result_template
result:
  test_id: T-001
  status: not_run
  engine_patch_version: null
  renderer: null
  hardware: null
  scene_revision: null
  lighting_profile_id: null
  evidence_paths: []
  measured_values: {}
  deviations: []
  reviewer: null
status_enum: [not_run, pass, fail, blocked, accepted_deviation]
```

## 10. Troubleshooting and performance

| Symptom | Check first | Corrective direction |
| --- | --- | --- |
| Lamps are invisible in a closed room at noon | Global ambient, sky contribution, geometry leaks, active camera exposure | Repair local light access, then recalibrate exposure. |
| Night remains bright after disabling the sun | Sky/background, baked bounce, fill lights, exposure, reflection captures | Remove stale daytime contributions and bound adaptation. |
| Every lamp looks like a floodlight during the day | Output units, double multipliers, attenuation, material emission | Calibrate source relationships before adding glow. |
| A lit bulb does not light the floor | Only emission/glow exists; light masks or range exclude the floor | Supply the intended light node or supported GI contribution. |
| Lamp light crosses a solid wall | Shadows disabled, missing/thin geometry, shadow bias, GI leakage | Fix the responsible direct or indirect path. |
| Door motion changes direct light but not bounce | SDFGI or baked-light limitations | Implement the declared door/indirect approximation. |
| Image brightens and darkens while aiming | Auto-exposure metering and limits | Revisit bounds, response, and camera framing behavior. |
| Lights pop as the camera moves | Renderer light limits, range, visibility, distance fades | Reduce active overlap or use a supported approximation. |
| Night surfaces reflect a noon sky | Stale sky/probe content | Implement and budget reflection refresh. |

Prioritize structural shadows, then optional decorative shadows. Use distance fades and carefully bounded light ranges, and review their appearance at night. Probe refreshes, GI, and shadowed lights can be substantial costs; measure their contribution on the target hardware. Keep the light-source relationship intact when lowering quality. [S-07, S-15]

For a performance-oriented stylized game, the baseline can use a directional sun, restrained environment light, selected real-time fixtures, local probes, and authored bounce approximations. Full dynamic GI is a choice, not a requirement for communicating the intended day/interior/night relationship. [S-17]

## 11. Source register

All links are primary technical references. Godot links are pinned to the 4.7 documentation. Property and feature descriptions were checked on 2026-10-09; validate the exact engine patch and rendering method in the production project. Project policies, example records, and acceptance tests are authored recommendations derived from these mechanisms, not requirements imposed by Godot.

```yaml
block_id: source_register
checked_date: "2026-10-09"
sources:
  - id: S-01
    title: "Physically Based Rendering, 4th edition: Radiometry"
    url: "https://pbr-book.org/4ed/Radiometry,_Spectra,_and_Color/Radiometry"
    supports: [additivity, distance_falloff, incidence_angle, radiometric_quantities]
  - id: S-02
    title: "Godot 4.7: Physical light and camera units"
    url: "https://docs.godotengine.org/en/4.7/tutorials/3d/physical_light_and_camera_units.html"
    supports: [physical_units_setup, unit_distinctions, approximate_daylight_reference]
  - id: S-03
    title: "Godot 4.7: CameraAttributes"
    url: "https://docs.godotengine.org/en/4.7/classes/class_cameraattributes.html"
    supports: [exposure, native_auto_exposure_renderer_support]
  - id: S-04
    title: "Godot 4.7: Light3D"
    url: "https://docs.godotengine.org/en/4.7/classes/class_light3d.html"
    supports: [light_properties, energy_multiplier, bake_modes, distance_fade]
  - id: S-05
    title: "Godot 4.7: Environment"
    url: "https://docs.godotengine.org/en/4.7/classes/class_environment.html"
    supports: [background_intensity, ambient_and_reflection_sources, sdfgi_properties]
  - id: S-06
    title: "Godot 4.7: OmniLight3D"
    url: "https://docs.godotengine.org/en/4.7/classes/class_omnilight3d.html"
    supports: [omni_attenuation, finite_range]
  - id: S-07
    title: "Godot 4.7: 3D lights and shadows"
    url: "https://docs.godotengine.org/en/4.7/tutorials/3d/lights_and_shadows.html"
    supports: [light_types, shadows, renderer_limits, performance_tradeoffs]
  - id: S-08
    title: "Godot 4.7: SpotLight3D"
    url: "https://docs.godotengine.org/en/4.7/classes/class_spotlight3d.html"
    supports: [spot_attenuation, finite_range, angular_radius]
  - id: S-09
    title: "Godot 4.7: BaseMaterial3D"
    url: "https://docs.godotengine.org/en/4.7/classes/class_basematerial3d.html"
    supports: [emission_properties, emission_luminance_units]
  - id: S-10
    title: "Godot 4.7: Introduction to global illumination"
    url: "https://docs.godotengine.org/en/4.7/tutorials/3d/global_illumination/introduction_to_global_illumination.html"
    supports: [gi_selection, renderer_support, procedural_generation_tradeoffs]
  - id: S-11
    title: "Godot 4.7: Signed distance field global illumination"
    url: "https://docs.godotengine.org/en/4.7/tutorials/3d/global_illumination/using_sdfgi.html"
    supports: [dynamic_lights, dynamic_occluder_limitations, update_delay, performance]
  - id: S-12
    title: "Godot 4.7: Using Lightmap global illumination"
    url: "https://docs.godotengine.org/en/4.7/tutorials/3d/global_illumination/using_lightmap_gi.html"
    supports: [baked_indirect_lighting, light_bake_modes, static_lighting_limitations]
  - id: S-13
    title: "Godot 4.7: Environment and post-processing"
    url: "https://docs.godotengine.org/en/4.7/tutorials/3d/environment_and_post_processing.html"
    supports: [ambient_lighting, tone_mapping, glow, ssao_scope]
  - id: S-14
    title: "Godot 4.7: CameraAttributesPractical"
    url: "https://docs.godotengine.org/en/4.7/classes/class_cameraattributespractical.html"
    supports: [camera_attribute_precedence, native_exposure_bounds]
  - id: S-15
    title: "Godot 4.7: ReflectionProbe"
    url: "https://docs.godotengine.org/en/4.7/classes/class_reflectionprobe.html"
    supports: [interior_reflections, probe_update_modes]
  - id: S-16
    title: "Godot 4.7: Camera3D"
    url: "https://docs.godotengine.org/en/4.7/classes/class_camera3d.html"
    supports: [active_camera_configuration]
  - id: S-17
    title: "Godot 4.7: Faking global illumination"
    url: "https://docs.godotengine.org/en/4.7/tutorials/3d/global_illumination/faking_global_illumination.html"
    supports: [authored_indirect_lighting_approximations]
  - id: S-18
    title: "Physically Based Rendering, 4th edition: Point Lights"
    url: "https://pbr-book.org/4ed/Light_Sources/Point_Lights"
    supports: [point_source_model, inverse_square_distance_dependence]
  - id: S-19
    title: "Physically Based Rendering, 4th edition: The Light Transport Equation"
    url: "https://pbr-book.org/4ed/Light_Transport_I_Surface_Reflection/The_Light_Transport_Equation"
    supports: [emitted_and_reflected_light, material_dependent_light_transport]
```

## 12. Handoff requirements

The designer owns the intended readability, mood, and reference captures. The engineer owns source control, room-lighting behavior, renderer compatibility, and measured performance. Review the same test scene together before rolling the configuration across a level or procedural asset set.

The completed implementation handoff must contain a resolved project profile, fixture records, daylight keyframes, an indirect-light strategy, exposure settings, reflection refresh policy, and evidence for T-001 through T-012. Preserve explicit exceptions so later tools do not mistake them for universal lighting rules.
