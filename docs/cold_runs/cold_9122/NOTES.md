# Cold run 9122 -- the signs over the doors, named

Zoo 1.37.0 (the sign over a door names its business) and Deli Counter
0.165.1 (sign anchors carry the building's identity; a build that raises
fails). Same brief, same seed, same lot as 9121. Zero interventions, one
observation (the look shots).

The art leg before export: 0 blockers, 63 findings -- identical to 9121's by
code. Export closure clean (0 issues over 53 resources).

## The signs (`01`-`03`, night, sky wired)

Given stations, Godot metres, each in front of its sign's face (the site
light manifest's `pos`, Z-up, mapped to Godot as (x, z, -y)):

* `01_club_sign` (-47, 1.7, 2) -> (-56.65, 2.55, 0): strip_club_a01's door,
  MOM THINKS I'M AT BINGO -- the name its neon carries, by the same key.
  Mean 14.6.
* `02_terminal_sign` (10, 1.7, -21) -> (8.5, 2.55, -11.35): the airport
  terminal, TERMINAL A. Mean 11.8.
* `03_gas_sign` (94, 1.7, 13.5) -> (89.35, 2.55, 16): FLAPPHAS over the
  store's door, in the pylon's green. Mean 17.8.

9120's FLAPPHAS walk finding 2 (the blank lit box) is closed on this site.

## New: the sign's own light hot-spots its face

In `02` and `03` the middle of the face is washed white (the I of TERMINAL,
the middle letters of FLAPPHAS). The sign's area light stands 0.29 m in front
of its face (`lux_light_loader.gd`, "A SIGN'S SOURCE STANDS IN FRONT OF ITS
CABINET"), and Zoo 1.37.0's face is a backlit material with a 0.6 diffuse
copy (the pylon's albedo), so the lamp lights its own sign. The pylon has no
lamp in front of it, which is why the same albedo is right there. Not yet
fixed; the candidates are a face that does not take light (albedo near 0,
emission unchanged) or a source below the sign rather than in front of it.

## Still open from the FLAPPHAS walk

3. Stone inside. 4. The forecourt is dark.
