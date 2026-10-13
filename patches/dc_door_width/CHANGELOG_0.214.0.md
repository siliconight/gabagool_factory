## [0.214.0] - every walkable door is at least the contract's 1.25 m, and the contract says so

**Factory roadmap 197.** `agent_contract.json`'s `clearances.min_door_width_m` is 1.25 m. The library built 200
walkable doors under it in 32 of 132 enterable buildings: 13 at 1.0 m, 74 at 1.1 and 113 at 1.2, 47 of those
width-less and so at this builder's own default, then 1.2. The presets wrote 61 more, at 1.1 and 1.2. Only
a warning in `navigability.check` named them, and nothing read it. The number itself was derived at a
0.15 m cell, which the contract had since left for 0.1; at 0.1 its formula gives 1.00. The census and the
measurements below are in the factory root's `docs/findings/door_widths/`. The walker, 2026-10-13: "If we
change the door widths, that's ok, it should be called out in the agent contract". Asked which way, they
answered "widen the doors and keep 1.25". Then they added: "continue to update the agent contract file so we
can make singular changes when we know the size of characters in the game". So every door width this
builder's code writes now asks the contract, and the contract says what one change to a body moves.

- **The contract** (`agent_contract.json`, `clearances`). No number moves.
  - `derivation` is re-worked at the contract's own cell: the bake needs 1.00 m. 1.25 is written above it
    as a DESIGN MINIMUM, with every door and width built from it.
  - `min_door_width_note`, new, records what was widened and the two doors that were not.
  - `re_derive_when`, new, says what a change to the body or the bake's cell starts. It also says what
    follows on its own, what needs the migration re-run, and the body-sized numbers that do not follow
    yet: `stairwell.LANDING_DEPTH`, a literal 1.2, and the vault door's aperture, 1.3 x 2.1 m, spelt in
    `vault_room.APERTURE`, `spec_types`' vault default and Zoo's `vault_forms.DEFAULT_OPENING`. The vault
    is named by the release's second edit, `patch_dc_door_width_vault_note.py`.
- **The staff door** behind a teller line asks the contract for its width (`level_design._STAFF_DOOR_WIDTH`).
  It was a literal 1.25 beside a comment naming the contract, and `staff_aisle_width` already said the
  staff room asks. The number is the same.
- **A width-less door** resolves to the contract's minimum, not 1.2. `spec_types.Opening.resolved` reads it
  when the door is resolved.
- **The presets** write every walkable door at `presets.DOOR_W`, the contract's minimum: 61 doors in 15
  presets. Those are `auto_shop`, `bank`, `casino_tower`, `compound`, `corner_deli`, `gas_station`,
  `hospital`, `office`, `parking_garage`, `pawn_shop`, `police_station`, `rowhome`, `suburban_safehouse`,
  `twin` and `warehouse`. `empty_rowhome` and `empty_midrise` keep theirs: an Empty's doors are shut and
  nothing walks through them.
- **The library** (`migrate_door_width.py`, one-shot and idempotent, run here) widens 152 authored doors in
  29 specs to 1.25 m, each about its own centre. Two doors are handled by name, from the lint's own numbers:
  - **`final_stand`'s `west_entry` slides 0.10 m along its wall.** A partition ended 0.90 m from its
    centre, where L18 needs more than 0.93.
  - **`primos_pizza`'s `kitchen_stairs` is KEPT at 1.20 m.** At 1.25 it fails L18 where it stands. Slid
    clear, it fails L21, hanging 0.12 m over the basement stair's hole. No place on that wall holds it
    until the stair moves.
- **The library refurnished around its wider doors** (`migrate_furnish_recipes.py`, the release's third
  edit, `patch_dc_door_width_refurnish.py`). The library is held to be a fixed point of the furnishing
  pass, and widening a door moves what furnish puts beside it: the full suite failed both fixed-point
  tests on `cr_gas`. Measured spec by spec (the factory's `docs/findings/door_widths/refurnish_delta.py`),
  the refurnish moves 8 specs, every one a spec whose doors changed:
  - `cr_gas`, `foundry_heist_vertical`, `gas_station`, `gas_street` and `gs_corner_station`: pieces
    move, none lost;
  - `cr_pawn` loses a cartons stack and a floor safe, and `stop_n_go` its back-room cigarette rack;
  - `rowhouse_raid` gains four chair sets.
  The rack stood 0.96 m from `rear_service`, which widened 1.0 -> 1.25 m, so `test_club_fixtures`' pin
  on the library's cigarette machines moves 119 -> 118 with that reason beside it. The 8 shells are
  rebuilt. `migrate_furnish_recipes.py --check`'s own summary is not a measure of this: it reads
  -7,923 / +7,819 on 0.213.0, where the library is a fixed point.
- **Stairs-first's landing door** (`stair_core._PUNCH_DOOR_W`) is the contract's corridor width,
  `min_corridor_width_m`: 1.1 m, the literal it was. It is under the door minimum, and it is commented and
  named in the contract. Of the 20 crossings in `stair_regression`'s 140 variants, 18 are 1.2 m and 2 are
  1.1. At 1.25 none is punched, and the sweep's checks fail 21 times against 2. Of the new failures, 16 are
  `STAIR_EXIT_FACES_SOLID` and 3 are a prop in a stair's reserved volume. Level Factory never builds
  stairs-first.
- **An exact fit is punched.** A crossing exactly the door's width counts as wide enough, within 1e-9. The
  two 1.1 m crossings measured were 1.1000000000000014 and were punched by 1.4e-15. Spelt `6.1 - 5.0`, the
  same crossing is 1.0999999999999996, and it was refused.
- **Stairs-first's doored check** (also `stair_core`). Asking whether a crossing is already doored, it read
  a width-less door at a literal 1.2. It now reads `Opening.resolved()`.
- **The stairs-first changes move no spec.** The 140 variants' specs are byte-identical across all three
  (`stairs_first_doors.py`: sha256 35e2a857... over the 140 variants' specs with 0.213.0's two literals, with the resolved width alone, and with all three changes; at a 1.25 m punched door, the control, it moves to 6c417af7...).
- **`test_door_width.py`**. It fails to import on 0.213.0. It checks:
  - the width-less default, and a stand-in contract with another minimum getting another door;
  - the module-level widths (`presets.DOOR_W`, the staff door, the punched landing door) against the
    contract in force;
  - every library door, and the KEPT door still named and still narrow;
  - every enterable preset made as Level Factory's adapter can make it: three modes, one to four floors,
    a basement or not;
  - the migration's Empties, kept doors and idempotence, and the library as the migration's fixed point;
  - the contract's three texts, and the derivation re-worked at the contract's own bake, so the next
    change to the bake fails here until the text follows;
  - stairs-first's doored check at a width-less door's built width, and the exact-fit crossing;
  - the library's built shells, not every file in `build/`.

**Measured before the change.** These ran on a copy of 0.213.0 with the change and a copy without it:
- `layout_lint --all`: 0 FAIL and 391 WARN both ways, with the same findings.
- Every preset as Level Factory makes it: two modes on eight seeds (304 variants), then three modes at 1 to
  4 floors with and without a basement (432). The FAILs match preset by preset and rule by rule (768 and
  1,044). Doors under 1.25 went from 1,568 to 0, and from 2,148 to 0.

**Built:** `build.py --all` under Blender 5.1.1, 152 shells in 388 s, exit 0, no error in the log; the 8 refurnished specs rebuilt after. 34 manifests move in content -- the shells the doors change -- and 118 only by `built_utc`. `door_fit.py` (the factory's `docs/findings/door_widths/`) over the 132 built enterable shells finds no door under 1.25 m but the KEPT one. Its other findings are two orphan builds of specs no longer in the library (`fuel_stop_heist3`, `fuel_stop_heist4`, untracked) and a breach overlap in `auto_shop_a02` that 0.213.0's tracked build carries too. `layout_lint --all`: 0 FAIL, 391 WARN, as before

**Suite:** 1,480 passed, 2 skipped (the bpy round-trip fixtures, run in their own process), exit 0: 0.213.0's 1,449 and `test_door_width.py`'s 31. Against an export of 0.213.0 with the migration module copied in so the file imports, 26 of the 31 fail; the 5 that pass are the three presets that never wrote a narrow door, the KEPT door's record and the migration's own check
