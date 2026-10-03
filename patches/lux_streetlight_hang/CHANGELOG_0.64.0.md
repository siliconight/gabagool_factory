## [0.64.0] - the poles' shadow was their own shaft

The walker, 2026-10-03, walking the gas station lot at night: "we still have
quite a few street lamps that aren't putting their light down", and later,
"this one far away is working but the one closer isn't". A survey over every
pole of cold run 9139's lot (every other light off, the ground's luminance
9 m from the foot, the pole's own lamp against a fresh unshadowed spot on its
transform) read 0.001 on 12 of 17 poles against 0.25-0.33 for the copy; the
other five read within 7% of theirs. The twelve were exactly the lights
`apply_shadow_policy` had given shadow maps: the High tier's 12, drawn from
the rank-0 class by the tie-break's string sort of paths (`site_lamp_1, 11,
15, ..., 27, 3, 30, 32`), which is why the lit poles made no spatial
pattern and the one across the lot worked while the near one did not.

Why a shadowed pole was dark. The rig's lamp sat at the mount, and for a Lot
pole the mount is the lens point 0.175 m under the module's top -- in Zoo's
recipe, 5 mm above the shaft's top cap. A spot's shadow map is a perspective
camera at the light's origin; a disc of radius r at depth d in front of it
subtends atan(r / d), so the 0.06 m cap 5 mm under the lamp subtends 85
degrees, the whole 55-degree cone, and every pixel under the pole compares
as shadowed. The dials, each alone on a fresh shadowed spot on the pole's
transform: tilt, cone angle, range, atlas size and depth, cull mask -- no
change (0.000-0.002); shadow casting off (`shadow_caster_mask` 0) or a large
bias -- lit (0.53); the pole's merged body mesh hidden -- lit (0.284); the
lens alone hidden -- no change; the lamp 0.02 m lower -- 0.282, 0.05 --
0.239, 0.10 -- 0.282, against 0.286 with no shadow at all; the lamp raised
0.02 or 0.05 -- still 0.000. The first reading of this was the shaft's SIDES
filling the frustum from a camera on the axis, and a clean cylinder in the
Lux project with the lamp on its cap lit the ground fully (0.742) and
refuted it; the same shapes with the lamp 5 mm over the cap read 0.002
whatever the body's cull mode, 0.745 with the shaft hidden, and no change
with the head or the lens hidden. The cap is the caster.

`LuxStreetlightRig.LAMP_HANG_M` (0.10): the lamp hangs that far below the
mount, which puts the shaft behind the shadow camera; the derivation and
the table sit on the constant. The loader solves the pole's energy for
where the lamp now is. A wall pack is the same rig and hangs the same.

`tools/streetlight_shadow_selftest.gd` holds it with a window: Zoo's pole
geometry, a shadowed rig, the ground read hung (the shipped placement), with
no shadow, and on the cap (the control: the shaft blacks the pool, which
proves the instrument can see a shadow at all).

`tools/self_shadow_census.gd` is the general instrument this came out of:
run on a walk copy, every rig light is read with its shadow off and on from
a camera beside its target, and the summary names the ones that lose more
than half their light to their own shadow map. On 9139's lot before this
fix, one wall pack read 0.50 and every readable sign, pendant, bulb,
fluorescent and spill read 0.89-1.09; the poles were unreadable from the
first cut's camera (a downlight's target was put below the floor), which
the ray-cast target fixes. Rerun on the rebuilt lot: the 17 poles at
0.97-1.00 but one, two lights flagged and not chased (a fluorescent and a
pole whose pool the camera most likely saw through a wall -- the tool
cannot yet tell a self-shadow from a shadow map stopping a leak; a camera
in the light's own room would). `docs/findings/streetlight_shadow/NOTES.md`.

After the fix, the same survey on the rebuilt lot: 17 of 17 poles light
their foot, each shadowed lamp at 0.85-0.94 of a fresh unshadowed copy.

Priced on the fixed-station harness (raw packages, one session, the old
export twice as the control): median ms after minus before -0.13 against a
control of -0.09; GPU -0.02 against -0.03; draws +0.02; lights 94 both.
Inside the control, as it should be: the twelve shadow maps were already
being rendered for lights that drew nothing.

What was wrong before this and is kept: `docs/findings/light_cap/NOTES.md`
blamed the per-mesh light cap and indoor light leaking onto the lot tiles,
and priced a cap of 16 (+2 ms GPU, refused). The cap finding was real on
the tiles it measured and not the cause of the dark poles: a fresh spot lit
tiles the pole's own could not, with every other light off.

Open, noted and not changed here: the shadow policy's tie-break sorts
paths as strings, so which 12 of 17 poles carry a shadow is an accident of
their ids; a natural sort, or distance from the site's centre, would make
the shadowed set deliberate.

