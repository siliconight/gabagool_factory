# Cold run 9240 -- the container roof on 9226's yard: the run was clean, and the slab was never a roof

**What it tested:** Zoo 1.99.0, which gives a cargo container's roof the
walls' valley shade, the darkest face of the box. Its premise was cold run
9226's "pale slab": from look_shots' elevated west camera, a bright flat
rectangle above the storefront's roofline, which 9226 read as a container's
top face in the backdrop's near band. On 9226's brief (warehouse_yard_001,
industrial surroundings, heavy rain at night), on the current set, and
framed against 9226's package at the same four elevated stations.

**Result: 0 interventions, 0 stops.** Three candidates, seed_9105 picked
on the walktest and Laser Tag's route findings. The bake: 330 models and
120 primitive meshes lightmapped, 51 steady rigs baked and 8 failing left
live. Findings 80 -> 112, every one of the 32 new ones `S_TARGETS`, the
rule Lot 0.112.0 added after 9226 ran.

## Seen: nothing moved (`roof.png`, `roof_frames.sh`)

9226 left and 9240 right, the four elevated views. Every frame matches its
partner by eye, and the slab measures the same in both: mean (192, 199,
202) over the whole 220 x 40 px box at frame (70..290, 176..216) of
`elev_W`, every pixel of it above 450 in summed RGB, in each package.

A change that moves nothing is evidence about the wiring before it is
evidence about the theory, so the object under the slab was measured.

## Measured: the slab is a lit window 91 m away (`slab_ray.py`, `slab_ray.txt`)

- **The camera cannot see a roof.** 9240's shots report records `elev_W`
  as ORTHOGRAPHIC and horizontal: eye (-7.45, 3.758, 4.53), target (24.0,
  3.758, 4.53), an 8.1 m tall frame. A horizontal orthographic camera sees
  every horizontal face edge-on. The slab is a vertical face.
- **The mapping is checked** against the plate's own props: the bus
  shelter's slot lands at frame x 187, the mailbox at 643 and the payphone
  at 1287, where the frame shows each.
- **The rays meet no container.** Through the slab's left, middle and right,
  the only backdrop box in front of the eye is `backdrop_117`, a
  `backdrop_warehouse` 32 x 16 x 8 m centred at (92.0, 3.533, 4.0), turned
  270 degrees, its painted front facing the plate, its face at x = 84:
  91 m from the eye.
- **On that face, the rays land in one window.** Facade metres 17.58 to
  19.38 across and 5.90 to 6.19 up: Zoo's third high window of six,
  (17.67..19.47) x (5.40..6.20) m, which the module's stem paints LIT,
  cool white, in the emission map. Its top at 6.20 m is the slab's top edge
  at 6.22 m; its bottom is behind the storefront's roofline.
- 9226's own control agrees: with the backdrop scene off, the slab is gone.

So the slab is a backdrop warehouse's lit high window, drawn at its full
1.8 m width because the camera is orthographic. From a person's eye in a
perspective view it is a few pixels at 91 m, through rain. It is the
warehouse doing what Zoo 1.96.0 built it to do.

## What it means for Zoo 1.99.0

- 9226's reading is **retracted** in its own record: the slab was neither
  a top face nor a container. Zoo 1.99.0 answered a question about the
  wrong object, and nothing in this run shows its effect, because no
  look_shots camera looks down on a container.
- **The shade stays, as a look, not a fix.** It costs no draw and no
  triangle, a yard box's top is where its weather sits, and taking it out
  would be another release for no evidence either way. Nobody should cite
  1.99.0 as having fixed anything that was seen.
- The rule this breaks is CLAUDE.md's first verification rule, in its
  plainest form: a frame was read as evidence of an object before anything
  said which object drew it. The pick is cheap now that `slab_ray.py`
  exists, and the slot manifest plus the shots report are all it needs.

## What is evidence of what

- 0 interventions and the bake's figures: this run, on the current set.
- The slab's identity: `slab_ray.py` on this run's picked candidate's slot
  manifest (`warehouse_yard_001.lot_assemble.candidate.seed_9105`) and this
  run's shots report; the lit pattern is Zoo's own function on the stem
  the backdrop's MultiMesh names.
- Not shown anywhere: what 1.99.0's roof looks like. A perspective camera
  above a container would show it; none was shot.

## Instruments

- `roof_frames.sh`: the four elevated views in 9226's and this run's
  packages, the sheet `roof.png`.
- `slab_ray.py`: the elevated camera's pixel rays through the backdrop's
  slot boxes and into the warehouse's facade windows; its output in
  `slab_ray.txt`. Its first version counted boxes behind the camera, which
  an orthographic camera does not draw, and named a warehouse at x -144;
  it keeps only boxes in front of the eye.
