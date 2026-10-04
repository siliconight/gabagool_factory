## [0.175.2] - An Empty's walls run the full storey

0.175.0 left an Empty only its roof slab, and `_cap_thick` kept stopping
every wall 0.3 m short of each storey line, to sit under a floor slab that
was no longer emitted. Measured on 0.175.1's `gs_empty_rowhome_f.slots.json`:
storey 0's walls end at z 2.80 and storey 1's begin at 3.10; 5.90 to 6.20
the same. Nothing filled either band, so every Empty had a slot through it
at every storey line. In cold run 9147's frames it is a dark band across
each house. This was introduced by 0.175.0 and caught by looking at the
frames, not by a check.

`_cap_thick` answers 0 on an Empty below its roof: the wall runs the full
storey. Under the roof it still stops, and the roof slab closes it. Of
`_cap_thick`'s five callers only `_exterior` runs on an Empty, so nothing
enterable moves.

`test_empty_walls.py`:
- an Empty leaves no slot at any storey line (fails on 0.175.1: 0.3 m at
  two lines);
- the control: an enterable building still stops under each floor slab.
