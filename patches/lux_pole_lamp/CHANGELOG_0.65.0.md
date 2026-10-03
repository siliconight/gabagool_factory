## [0.65.0] - the pole's lamp sits beside the pole, not inside it

0.64.0's fix for the dark streetlights was wrong in a way real-time
rendering could not show. It hung the pole's lamp 0.10 m below the mount to
clear the shaft's cap from its shadow map; the mount is 5 mm above that cap,
so the lamp sat 9.5 cm inside the steel shaft. A shadow map culls the
shaft's inside faces, the pool came back, and the walker confirmed it. The
light-bake probe (roadmap item 31, `docs/findings/light_bake/NOTES.md`)
ray-traces, and on the baked gas station lot every steady pole's pool was
gone: a lamp sealed in a tube lights nothing.

Measured on one closed 6 m pole and one static spot with the streetlight
rig's own numbers, baked by Godot 4.7's lightmapper at quality Low:

    lamp inside the shaft (0.64.0)             0 lit texels   max 0.005
    on the axis at the lens point (to 0.63.0)  2,815          max 0.039
    0.2 m along the head, 1 cm under the lens  5,581          max 20.9
    no pole at all                             5,605          max 3.0

The pole's lamp now sits `POLE_LAMP_ALONG_M` (0.2 m) along the head from
the pole's axis and `POLE_LAMP_DROP_M` (0.01 m) under the lens: in the air
beside the shaft, under the lens at the genome's narrowest head. The rig
turns with its pole (Lot writes the pole's yaw on the anchor), so the rig's
local x is the head's length. The pole shadows a 33-degree wedge of its own
pool on its far side, which a real pole does.

THE POLE'S SHADOW BIAS IS 0.1 (`POLE_SHADOW_BIAS`). With the lamp beside
the pole, one shadowed pole on the lot -- the side street's -- went dark
again after about 30 frames: the renderer moves a light to a smaller slot
of the 16-bit positional atlas, and at the engine's default bias of 0.03 the
ground shadowed itself. Settled, every other light off, the ground under it
read 0.085 against 0.201 unshadowed; bias 0.1 read 0.183, as did a 24-bit
atlas. The pole survey read each pole 8 frames in and could miss it; a
90-frame settle found 1 steady pole of 17 dark at the default and none at
0.1 (`patches/lux_pole_lamp/pole_survey_settled.gd`). The bias is a
rig-node property too, `lamp_shadow_bias`, which a wall pack leaves at the
engine's.

The offset is a rig-node property, `lamp_offset`, defaulting to 0.64.0's
(0, -`LAMP_HANG_M`, 0): a wall pack is the same rig on its own hardware and
does not move. The loader's `streetlight` branch sets the pole's, and solves
the pole's energy for the lamp's new height. The fake-volumetric cone
follows the lamp's offset.

`tools/streetlight_shadow_selftest.gd` now builds the pole through the
loader's own streetlight branch: the lamp's place; clear of the shaft by
0.1 m or more and under the narrowest lens; the shadowed pool at 0.8 or more
of its unshadowed self; the two controls (a slab, and the lamp on the axis
at the lens point, each black the pool); a wall pack's placement unchanged.
What it cannot hold is the bake, which needs the editor; the probe's pole
control holds that, and its figures are on the constant.

