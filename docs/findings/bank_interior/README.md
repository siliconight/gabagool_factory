# A bank interior that reads as the walker's comps (roadmap 321, the bank first)

The walker, 2026-10-27: "we need to prioritize a great looking bank interior next", with twelve comps read in
`docs/reference/BANK_INTERIOR_COMPS.md`.

## The baseline: MEASURED, 2026-10-27

`bank_block_001` at seed 9082, the level cold runs 9364-9366 made. It was made fresh on the day's tools
(`workspaces/bank-look-1027-ws`, `batch.json` here; `level_factory make`, not a cold run): Level Factory 0.261.0,
Deli Counter 0.279.0, Zoo 1.134.0, Lux 0.80.0, Pixelcoat 0.63.0. Its bank is `bank_branch_a02`, building b0 at Godot
(-60, 0, 6.97), unrotated, so plan (x, y) -> Godot (-60 + x, h, 6.97 - y). `shoot.sh` walks it and shoots six stations
twice: in the level's own light (`frames/01_*`) and under `look_shots --inspect studio` (`frames/02_*`).

| station | the level's light, mean / p50 | inspection light |
|---|---|---|
| lobby_entry (the door, facing the teller line) | 37.2 / 33 | 76.1 / 67 |
| lobby_wide | 33.7 / 27 | 59.7 / 54 |
| behind_line (staff side, facing out) | 46.4 / 42 | 80.0 / 70 |
| manager_office | 80.5 / 76 | 117.0 / 105 |
| vault (storey -1) | 39.9 / 39 | 108.3 / 118 |
| vault_west (storey -1) | 29.9 / 30 | 87.8 / 75 |

For scale, the supermarket's aisles read 87.8 and 91.1 the same day, after roadmap 319.

What the frames show, against the comps:

- **The lobby is dark and bare.**
  - It has 10 lamps over 390 m2, one per 39 m2 (`build/bank_branch_a02.lights.json`). The ceiling grid reads dark grey
    and the walls are raw concrete.
  - On the floor: a few stanchions, a low bench, two bins.
  - No check desk, no planters, no poster stands, no date clock. The recipe stands vending and a cigarette fixture
    there (`level_design._RECIPES["lobby"]`).
- **The lobby floor is maroon carpet** (inspection frame). `floors.FLOOR_BY_ROLE["public_entry"]` is carpet, and
  0.271.0's note keeps it on purpose: "right for a lobby, a banking hall or a parlour". The comps say otherwise for a
  bank: terrazzo or pale tile in public in 1, 2, 4, 6 and 7, carpet only behind the line (3, 5).
- **The teller line reads.** A wood front, glass windows at pitch, an enclosed staff side
  (`enclose_teller_lines`, the walker's ask on cold run 9048). It is the room's strongest shape, as in the comps,
  standing in the dark.
- **The manager's office** is bright and plain: concrete walls, bare desks and cabinets.
- **The vault floor** has count tables with cash, safes, a cage wall and a round vault door: the bones are right.
  - It is lit by bare-bulb pendants (`lights.py`'s moody rule): 6 lamps over 330 m2, one per 55 m2, a mean of 30-40.
  - The comps light money rooms with bare tubes on steel (10, 11), and show safe-deposit boxes (12) and cash carts and
    hampers (10, 11). The vault floor has none of them.

## Step 1 shipped: Deli Counter 0.280.0 (fef9d2f9), light and floor

A bank's public room is lit at a selling room's density with the bake-only reach, and floored in tile. Its rooms below
grade and over the take are lit by tubes, not moody bulbs. A split row's one-lamp runs keep the row's `bake_reach`.

The same mission and seed, made on 0.280.0 with every other tool the same (`workspaces/bank-look-0280-ws`,
`after_0280.sh`), shot at the same stations (`frames/03_*`, `frames/04_*`):

| station | before, mean / p50 | 0.280.0 | inspection light, before -> after |
|---|---|---|---|
| lobby_entry | 37.2 / 33 | 101.1 / 98 | 76.1 -> 159.0 |
| lobby_wide | 33.7 / 27 | 94.2 / 96 | 59.7 -> 138.1 |
| behind_line | 46.4 / 42 | 62.0 / 54 | 80.0 -> 94.3 |
| manager_office | 80.5 / 76 | 80.8 / 76 | unchanged (the control: no rule names it) |
| vault | 39.9 / 39 | 72.2 / 70 | 108.3 -> 129.9 |
| vault_west | 29.9 / 30 | 49.0 / 47 | 87.8 -> 103.2 |

**Priced** (`price.py`, `compare.py`, `compare.out.txt`; control twice and the subject, one session, nothing else
running), 53 headings at the package's own stations:

- **Draws:** subject minus the controls' mean, median +0, largest +34. The controls agree to the draw.
- **p95:** median +0.151 ms. The controls' own a - b is median -0.173 and largest 0.662, so the median is inside the
  instrument's floor.
- **ONE HEADING PAST THE FLOOR, UNEXPLAINED:** `attacker_spawn_2` at yaw 270 reads 8.77 ms against 7.40 and 7.47
  (+1.33), with +10 draws. It is outside the bank, and nothing here says why it moved. Not re-measured.

What the frames show now: a bright, even lobby on a pale tile floor, the teller line reading across it, the vault lit by
tubes. And what they show is still missing:

- an EMPTY lobby (a bench, two bins and stanchions on the floor);
- raw concrete walls in every room;
- the manager's office and the staff side on concrete.

Steps 2 to 4 follow.

## Steps 2 and 3 shipped: Zoo 1.135.0 (7c8489c) and Deli Counter 0.281.0 (cc301ed1), the lobby's furniture and the carts

- **Zoo 1.135.0** draws `check_desk` (a standing-height island, a dark top, brass slip pockets, comp 1's date block)
  and `cash_cart` (a steel cage cart on casters, its load the variant).
- **Deli Counter 0.281.0** furnishes a bank's public room as `bank_lobby`: the check desk its anchor, waiting chairs,
  an ATM, a queue, and none of the general lobby's vending, cigarettes, payphone or sofa. A bank's vault is
  `bank_vault`, with a cash cart beside its count table.

The same level on both (`workspaces/bank-look-0281-ws`, `after_0281.sh`; `frames/05_*`, `frames/06_*`): the check
desk stands mid-floor before the teller line, the vending and cigarettes are gone, and carts stand in the vaults. Light
moved only where a piece now stands (lobby_entry 101.1 -> 101.8, vault_west 49.0 -> 51.9).

**Priced** against the 0.280.0 package (`price_0281.py`, `compare.py perf_0281_`, `compare_0281.out.txt`), 53
headings:

- **Draws:** median +0, from -27 to +5. The lobby's dropped pieces outweigh the desk and the carts.
- **p95:** median +0.011 ms, inside the controls' own floor of 0.850.

**0.280.0'S OUTLIER DID NOT REPRODUCE.** `attacker_spawn_2` yaw 270 read 8.77 ms on the 0.280.0 package in the first
session. The same package reads 7.21 and 7.16 there in this one: session drift (roadmap 271), not the change.

**Two first applies stopped in their gates**, both before any commit, and are kept here:

- **Zoo's:** the species were unreachable by prompt (underscored keywords; the spaced names added).
- **Deli Counter's:** five tests pinned the old bank lobby, and only the furnish tests had been run on the clone.
- The first build of 0.281.0 also put a cash cart in every `vault`-kind room, 44 specs including a deli's back safe.
  `bank_vault` scopes it to banks.

Left: the cart reads brown, the theme's `metal` skin; and every wall is raw concrete -- step 4.

## The plan, each step priced and shown

1. **Light and floor** (Deli Counter): a bank's public rooms take a selling room's lamp density and the bake-only
   reach (roadmap 319's `room_caps` and `bake_reach`), and a hard floor. The money rooms take fluorescent rows, not
   pendants.
2. **The lobby's furniture** (Deli Counter recipe, Zoo species): a check desk island, planters, poster stands, a date
   clock; no vending or cigarettes in a bank.
3. **The money rooms** (Zoo species): a bank of safe-deposit boxes, some drawn open; cash carts and canvas hampers.
4. **Surfaces** (Pixelcoat and the theme): terrazzo underfoot in public (`profiles/materials/terrazzo.json` exists,
   used by the rockay and casino themes), painted walls and wood panelling for the concrete.
