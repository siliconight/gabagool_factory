# A parapet stands on the wall below it (roadmap 324)

The walker, 2026-10-29: "keep going on the edges", then "make the parapets flush". `docs/findings/parapet_coping/`
had found every parapet standing 15 cm behind its facade.

**Grounded.** `deli_counter.py` `_exterior` centres every storey wall on the slab's extent (the footprint line) and
stops it under the slab above (`_cap_thick`); `_parapets` ringed the roof on that same extent as its OUTER face. On
`bank_branch_a02`: storey walls 0.30 m thick, face at y 11.15, top at 6.9; roof slab 6.9..7.2 to y 11.0; parapet
0.20 m, face at 11.0, 7.2..8.3. So the top of the building was a recess at the slab's edge with the parapet set back
above it -- the comment over `_record_parapet_slot` says "the wall below it carried past the roof", which the
coordinates did not do. The rowhomes measured the same.

**What shipped.** Deli Counter 0.292.0 (`patches/patch_dc_parapet_flush.py`): the ring takes the walls' outer faces
(the slab's extent plus half `wall_thick`) and each tile starts at the top of the wall below, so it covers the slab's
edge; its top is unchanged; the corners still belong to N and S; `polybudget` mirrors the runs. The bank's N parapet:
y 10.95..11.15, z 6.9..8.3, a slot 1.4 m tall where it was 1.1.

**Found on the way, and shipped first: one plane split into two segments.** The first rebuild (`*_flush1*`) left 24
edge strips across the bank's flat N and S faces at z 6.9. `bucket_probe.py` printed Patina's wall-segment buckets:
the facade's faces at y 11.149998664855957 and the flush parapet's at 11.15000057220459 -- one plane in float32,
rounded by `round(_, 1)` to 11.1 and 11.2, so the facade stood as a segment of its own topping out at 6.9 and got a
roofline. It was already in the library: `plane_census.py` dressed Deli Counter 0.291.0's 158 shells with Patina
0.33.0 and with the fix; 76 change, 82 do not, and `overlap_probe.py` shows every change removing a duplicate --
`airport_terminal_a01` 35 -> 3 overlapping base courses and 25 -> 0 curbs, `bank_branch_a02` 10 -> 0 and 11 -> 0
(`plane_census_live.txt`, `overlap_live.txt`; `merge_probe.py` lists the clusters merged). Patina 0.33.1
(`patches/patch_patina_plane_buckets.py`) clusters planes within 1 mm before rounding.

**Measured** on seed 9082 (`_scratch/flush_input`, its `lot_library` the Deli Counter clone's `build/`), control
`workspaces/coping-9082-ws` (Deli Counter 0.291.0, Patina 0.33.0, Zoo 1.146.0):

- `workspaces/flush-9082-ws` (Deli Counter clone, Patina 0.33.0): **PASS, draws median +0, largest +2; p95 median
  -0.016 ms, largest +0.323 ms, floor 0.841 ms** (`perf_flush1_*`). The 24 strips across the bank's faces
  (`sheet_*_flush1.png`, `crops_inspect_flush1.png`).
- `workspaces/flush2-9082-ws` (Deli Counter clone, Patina 0.33.1): **PASS, draws median +0, largest +1; p95 median
  +0.062 ms, largest +0.684 ms, floor 0.940 ms** (`perf_flush_*`). This price carries both changes: the flush
  parapet and Patina's duplicate covers gone. Every Empty's 14 step strips are gone, the bank's 42 roofline strips
  superseded by its copings and none left on its faces; the copings follow the slots onto the facade line.
- **The frames** (`sheet_inspect.png`, `sheet_level.png`, `crops_inspect.png`): from the street the change barely
  moves the silhouette. The white line still crossing the bank's facade 1.4 m below its top is **not** the parapet:
  it is Patina's gutters, hung at the top storey's wall top under the parapet -- found here, fixed next
  (`docs/findings/slice_look/`, the scupper).

**Unproven.** Walking the roofs: the parapet's collider moved 15 cm outward and down to the wall top; the walk bot did
not run on these builds (`make` builds the walk copy, it does not walk it).
