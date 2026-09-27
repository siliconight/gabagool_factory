# Night readability: the layer `Delco Night` is missing

The walker supplied *Making Night Scenes Readable in Godot* on 2026-09-26 with
"not sure if any of this helps us?". It does, and the most useful thing in it
diagnoses a decision this repo made two runs ago and reported as a success.

## The rule it states

> Use ambient light to preserve basic readability. Use moonlight to shape the
> scene. Use local lights to direct attention. Keep the sky dark enough to sell
> the time of day.

Four layers. `Delco Night` (Lux 0.44.0) has three of them.

## What it says about the one we skipped

> **Moonlight:** Add a `DirectionalLight3D` with low energy and a subtle cool
> tint. Rotate it to create a direction for shadows and highlights. Treat it as
> gentle shaping light, not daylight painted blue.

`Delco Night` sets `sun_enabled = false`. There is no directional light in the
package at all — cold run 9084's first falsification check was literally
"DirectionalLight3D nodes in the applied scene: 0", and that was recorded as
the check PASSING.

It was the right fix for the wrong problem. `Blue Hour`'s sun at 4 degrees and
0.9 energy was daylight painted blue, exactly what the doc warns against, and
removing it was correct. Replacing it with nothing was not: the layer that
gives every surface in a scene a direction went with it.

## And the measurement already said so

`tools/pool_exposure.gd` on cold run 9084's package:

    station            mean   clipped    black      p50      p99
    forecourt        0.1513      0.9%    73.8%   0.0039   0.9037
    under_canopy     0.2435      1.5%    46.6%   0.0479   0.9446
    street_pool      0.1267      1.1%    84.1%   0.0000   0.8900

The doc's own words for that shape:

> If shadows collapse into featureless black, raise the ambient fill slightly
> or add a motivated light near the area that needs to read.

74–84% black with a median pixel at zero is the collapse. Part of it was the
unit error in the outdoor levels (Lux 0.45.0), and the blown discs were that.
The black was the missing moon.

## Two more things it corrects

**Exposure is the wrong lever, and `Delco Night` reaches for it.**

> Avoid fixing every problem by raising camera exposure: that brightens the
> whole image and can flatten the scene.

The preset carries `exposure = 1.15`, raised from `Blue Hour`'s 1.05 while it
was being written. That was a guess made in the same edit as everything else
and it should come back down; the fill belongs in ambient and the moon.

**One layer at a time, which is not how any of this was done.**

> Tune in the running game, one lighting layer at a time.

Cold run 9084 changed the preset, built ~80 streetlights that had never
existed, and derived their energy — three layers in one run. When it came back
wrong there was no way to attribute the wrongness, and the next run had to
unpick it. The runs since have been one variable each, which is why 9085 is
worth reading.

## What it validates

> Emission makes a surface look bright; use actual lights or GI when it also
> needs to illuminate nearby geometry.

That is exactly the canopy: an emissive lamp grid that costs no light, plus a
few real washes that do the illuminating. The split was made on the 8-light
budget and this is an independent reason for it.

## The change, when the clock stops

Cold run 9085 is in flight and a tool repo cannot be touched while it is. When
it ends:

* give `Delco Night` a moon — a low-energy, cool, shadow-casting
  `DirectionalLight3D`, angled, as SHAPING light;
* drop `exposure` back to 1.05 and let the moon and ambient carry the fill;
* change those two together and nothing else, so `pool_exposure.gd`'s black
  fraction and p50 attribute to them.

The numbers to beat are 9084's above, and the target is not a number anybody
here can name yet — which is the doc's last word and the honest position:

> There is no universal energy value for a "good night".
