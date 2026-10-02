# Cold run 9136 -- the store's counter in one look

gas_block_001, 9135's brief and seed (9080), on Zoo 1.48.0 and Level Factory
0.128.0. Zero interventions (journal 0, unattributed files 0), no
observations. The same three buildings as 9135: bank_tower_a02,
freight_terminal_a01, gas_station_a03.

Since 9135: Zoo 1.47.0 (the lottery dispensers, built to a brief and painted
into the till's image), Zoo 1.48.0 (the cigarette rack and machine
repainted; the rack stocked in blocks), Level Factory 0.128.0 (a filtered
texture ships VRAM-compressed; the register's flicker removed).

## Seen in the level (`frames/`)

The probe from 9135, taught two things: the till's mesh now holds the
dispensers too, so its middle no longer says which side its display is on
(the rack over the clerk's side does); and to find the rack.

* `till0_counter`, `till0_customer`, `till0_clerk`, `till0_lottery` -- the
  tills with three ticket dispensers beside each, a different game in each.
* `rack_full`, `rack_close` -- the rack over the counter: smooth lettering,
  packs in blocks of a brand.
* `atm*`, `poker0_*` -- as 9135.

What a frame shows and nothing measured: the counter's own candy tiers and
checker trim, the coolers behind it and the frozen-drink machine are still
the pixel look. `rack_close` has a hot spot where a ceiling fixture meets
the rack's face; the display's roughness (0.4) is what it always was.

## Priced (`perf_9136.json`, `perf_9136_again.json`)

The fixed-station harness twice on a fresh copy, idle machine, against B
from `docs/findings/real_look_trial/AB_IN_LEVEL.md` -- the same lot on Zoo
1.46.0 and the same Level Factory.

| package | mean p95 ms | mean draws | views over 11 ms |
|---|---|---|---|
| B (Zoo 1.46.0) | 5.16 | 1079.4 | 2 |
| 9136 | 5.32 | 1079.2 | 3 |
| 9136 again | 5.44 | 1079.2 | 2 |

**Draws**: 9 of 53 views differ from B by one draw, -7 in total; the two
passes of this package are identical. 1079.2 is also what the lot read on
Zoo 1.45.0, before any of the real look: the painted tills cost a draw
(1.46.0) and painting the dispensers into the same image gave it back.

**Frame time**: +0.16 ms a view against B, where this package against
itself is 0.23 ms. Nothing above the instrument's floor.

**Texture memory**, the renderer's figure with `mission.tscn` loaded and the
warm-up finished:

| package | texture memory | shared textures compressed |
|---|---|---|
| 9135 as exported (Level Factory 0.127.0) | 344,910,446 B | 0 of 157 |
| 9135 with 0.128.0's pin applied to a copy | 336,561,431 B | 8 of 157 |
| 9136 | 333,443,842 B | 11 of 157 |

11.5 MB under 9135 with three more props in the new look than it had.

## Findings

51, and the same count under every finding code as 9135.

## Open

* The rest of the store: candy tiers and checker trim, the coolers' stock,
  the frozen-drink machine, the sandwich case.
* The owner pass on type (Pixelcoat's three new faces): everything painted
  so far is Blue Highway, whoever it belongs to.
* The other 97 % of the level's 333 MB of textures has not been attributed.
