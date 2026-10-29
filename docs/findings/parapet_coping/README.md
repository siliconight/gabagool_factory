# A parapet has a coping (roadmap 324, the shape step's edges)

The walker, 2026-10-29, on the window frames (`docs/findings/window_frames/`): "keep the aluminium, keep going on the
edges".

**What capped a parapet, grounded.** Not a Zoo module: a parapet tile is a Deli Counter wall slot (`parapet_<side>_*`,
`deli_counter.py` `_record_parapet_slot`) built as the ordinary wall module. Its top was Patina's roofline
`edge_strip`, from the anchor pass (`anchors._generate_zup`): one anchor every 2.5 m with +-0.375 m jitter at the top
of every wall plane, on the plane's outer face line, each built by Zoo (`core.dressing._COVER`) as a 2 m strip 10 cm
tall and 6 cm across, centred on that line. On seed 9082's `bank_branch_a02`, 64 of them: a dashed stick half off a
20 cm wall.

**What shipped.**

- Patina 0.33.0 (`patches/patch_patina_coping.py`): `framing.coping_orders`, one `coping` a parapet run, the slot
  tiles joined into runs, over the whole wall and 5 cm past both faces. N and S run 5 cm past the corners and E and W
  stop at their roof-side overhang, so the ring is capped once with no overlap (`tests/test_copings.py` measures the
  union's area). On an Empty a face with no opening is a party wall, as for gutters: nothing overhangs it and nothing
  runs past it. `framing.drop_capped_edge_strips` drops the strips under a coping, within 0.15 m of its top; the
  manifest counts them (`superseded`). `coping` joins the opening keep-out's exemptions.
- Zoo 1.146.0 (`patches/patch_zoo_coping.py`): the `coping` cover, a 10 cm box on the parapet's top sunk 5 mm into
  it, in the covers' own material (concrete).

**Measured** on seed 9082 (`_scratch/bank_look_input/batch.json`), control `workspaces/frame-9082-ws` (Zoo 1.145.0,
Patina 0.32.1) against `workspaces/coping-9082-ws` (the same batch and seed with Zoo and Patina pointed at the
changes' clones through its `tools.local.json`; the shoot `shoot.py`, the chain `_scratch/coping_chain.sh`):

- **The manifests:** every building with parapet slots got 4 copings, one a side -- the bank, the freight terminal
  and all 12 rowhomes. Strips superseded: the bank 42 of 64, the freight terminal 64 of 64, each rowhome 14 (one 22).
  `twin_a01`, which has no parapet, kept its 44. **Every surviving strip was attributed:** the bank's 22 stand at
  z 6.9 on the plane y 11.15 (and its three siblings), the rowhomes' at z 9.0 on x +-3.15 -- the tops of the STOREY
  walls, not the parapet (below).
- **The package:** the bank's dressing GLB kept 8 meshes (4 sides x concrete and painted metal); its concrete covers'
  top rose from 8.35 to 8.395 m (the parapet top plus 9.5 cm) and each side's widened from 0.21 to 0.43 m.
- **The frames** (`sheet_inspect.png`, `sheet_level.png`, `crops_inspect.png`; before left, after right): from the
  roof the parapet's top reads as one continuous cap where it read as a broken line; at the corner the cap closes
  round both faces. **From the street the silhouette barely moves** -- a 10 cm cap overhanging 5 cm is near what the
  strips drew from below. A pixel difference of the frames measures the rain, which differs between runs (28,892 to
  90,965 px over 0x24 on every shot, the whole frame its bounding box); the crops are read by eye.
- **The price** (`tools/price_batch.py`, A / subject / A, `perf_coping_*`): **PASS over 53 headings, draws median
  +0, largest +2 (floor 0); p95 median -0.032 ms, largest +0.136 ms against a floor of 0.222 ms.** The coping replaces
  strips in the same material on the same side, so it merges where they did.

**The finding this turned up, not fixed here: a parapet stands 15 cm behind its facade.** On `bank_branch_a02` the
storey walls are 0.30 m thick and centred on the footprint line (`ext_1_N_seg*` at y 11.0, outer face 11.15, top
6.9); the roof slab (`roof_footprint`, 30 x 22 m) and the parapet (0.20 m, outer face 11.0) stop at that line. So the
top of every such building is a recessed band at the slab edge with the parapet set back above it, and the strips
that survive are capping that step. `deli_counter.py`'s comment says a parapet "IS THE WALL BELOW IT, CARRIED PAST
THE ROOF"; the coordinates say it is 15 cm behind it. The rowhomes measure the same (walls at +-3.0, 0.3 thick;
parapets' faces at +-3.0). That step, not the cap, is what reads at the top of the bank from the street, and it is
Deli Counter's: the coping follows the parapet slots, so it moves with them if the parapet is brought flush.

**Unproven.** The walker's verdict. The freight terminal and rowhomes were not shot. Whether a 10 cm cap is the right
size at Xbox 360-era distance: the step above suggests the edge that reads is the facade's, so the size was not
tuned against these frames.

**Next in the shape work:** the parapet flush with its facade (Deli Counter); then nosings and corner bevels,
junctions (baseboards, crown), then the box props.
