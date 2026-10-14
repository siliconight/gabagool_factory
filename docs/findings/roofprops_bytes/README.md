# The roof props' bytes from run to run (roadmap 247)

**The question.** Cold runs 9294, 9295 and 9296 each built
`lot/pharmacy_a01/art/roofprops/pharmacy_a01_roofprops.glb` with the same command, `--seed` included. 9294's and
9296's are byte-identical, and 9295's is not. Roadmap 181 records the scatter as "deterministic per manifest and
seed". What differs?

**Measured** (`glb_order.py`, `glb_order.out.txt`; 9294 against 9295, and 9294 against 9296 as the control):
- **The glTF JSON is identical.** 2,569 of the 61,836 binary bytes differ, and all of them belong to one mesh:
  `SatelliteDish_metal_delco_1997`, the merged satellite dish.
  - Its positions, normals, UVs, colours and indices differ: 180 of 1,071 position values moved, the largest by
    0.75 m.
  - The mesh is the same set of 376 triangles, each with the same winding.
  - The 64 vertices whose positions differ lie between indices 79 and 160 of 357, in eight runs, and that span is
    a permutation of the same positions.
- **The control:** 9294 against 9296 differ in 0 bytes.

**What that says, argued here and not measured:** the dish is the same geometry with its vertices in a different
order, inside one span of the merged mesh rather than a whole part swapped. The merge orders its parts by name
(`zoo_keeper/core/partnames.group_parts`: "Sorted, not hash- or link-ordered"), so the order more likely changes
inside one part's build.

**Not traced:** which step reorders those vertices, and why one run in three.

**Why it matters, recorded and not fixed:** nothing a player sees moves. But a byte that changes without a cause
defeats any comparison of packages by hash: cold run 9296's NOTES had to read both builds to set this one aside.
