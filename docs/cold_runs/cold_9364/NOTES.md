# Cold run 9364 -- 0 interventions; bank_block_001, seed 9082: the freight terminal's containers as cargo containers

**What it was for.** Roadmap 267's last named word: Deli Counter 0.245.0 routes `container` to Zoo's `cargo_container`
behind `prop_species.DEPTH_LONG`, which records a species long in depth short side first, so freight_terminal_a01's
four containers -- plain metal boxes before -- build as the species. Seed 9082 draws bank_branch_a02,
freight_terminal_a01 and twin_a01 (`docs/findings/crowd_barrier_267/find_arena_seed.py` over bank_block_001's brief:
15 of seeds 9000 to 9999 draw the terminal; warehouse_yard_001 draws it at none of them). Staged from 9363 with the
batch's `seed_base` set to 9082, so the shell built the candidate the drive names.

**Tools** (`before.json`, every repo clean at `--begin`): Deli Counter 0.245.0 (147111ee) and Level Factory 0.228.0
(e71ea71), its first cold run -- `approve candidate_selected` asked the plan and took seed 9082, one of its batch's
three; the rest as 9363 -- Zoo 1.119.0, Lot 0.126.0, Lux 0.79.0, Dispatch 0.5.3, Patina 0.32.0, Laser Tag 0.32.0,
Pipeline 0.6.0, Pixelcoat 0.62.0.

**Every leg ran, `INTERVENTIONS: 0`** (journal 0, unattributed files 0, retries 0), read after `cold_run.py --end`;
7.4 min (02:38:19 to 02:45:40). Shell 0 blockers of 79 findings; art 0 of 110. The export: 0 surfaces on a greybox
material; closure ok, 0 issues over 83 resources; its bake 138 models and 97 primitive meshes lightmapped, 104 steady
rigs, 2,213 users.

**Findings 99 -> 110 compare two lots, not one change:** 9363's candidates were seeds 9281, 9382 and 9483, these are
9082, 9183 and 9284. None of the 110 names the freight terminal or a container. The three majors: two
`LT_MAP_NO_REACTION_TIME` (Laser Tag's survival, 5.1 s on the selected seed_9082 and 4.6 s on seed_9284) and one
`LOT_DESTINATION_ABOVE_FLOOR` on seed_9284, which the drive did not select. On seed_9082 the one moderate presentation
finding is twin_a01's porch deck and stoop 0.2 m into its doorways, recorded before as a gate with no notion of a
piece being walked on (`docs/findings/presentation_gates/README.md`).

**The containers, read from the package** (`docs/findings/cargo_container_267/README.md` has every figure):
`zoo_kit_build.freight_terminal_a01` built `prop_cargo_container_delco_1997_06_w240_d600_h260.glb` (10 visual meshes on
10 materials, 3,372 triangles); the composed scene before the merge instances it as `container_0` to `_3`, each turned
90 about the vertical, its 6 m along the building's x, the door ends west; the package's `site_base.glb` keeps the four
greybox colliders, 6.0 x 2.6 x 2.4 each. Merged, they are 40 of freight_terminal_a01's 188 meshes -- each of the 10
materials in exactly the 4 cells the containers stand in, worn by no other merged piece -- where the four boxes added
at most four: +36 to +40 submissions with all four in view.

**The frames** (`containers_before_after_inspect.jpg` and `_lit.jpg` in that folder): six stations in the terminal's
own frame, this run's walk copy beside `_runs/walk_export_precinct_yard_001`, the newest package on this machine that
places the terminal (precinct_yard_001 at seed 9708 on Deli Counter 0.222.0 -- another level and an older toolchain,
so the before shows what the containers were and nothing else). Four rust-brown boxes become four blue ISO containers:
corrugated sides, the carrier's name down each, the door end's locking bars and owner code at the west. All four are
one module -- one blue, one carrier, one owner code -- which is the walker's call (roadmap 267).
