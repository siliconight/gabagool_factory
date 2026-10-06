# Two names on one building

**Status, 2026-10-06: option D shipped.**
- Level Factory 0.147.0, "a band names a shop": 68 of the 148 library shells
  are dealt a band, where all 148 were.
- Zoo 1.76.0: a retail strip is not a strip club.
- Named shops still carry two names. A or B is the walker's call.

Found 2026-10-06, during the walker's request that the detail in the strip
club and the Flappahs store live "in the logic that is called when a level
calls for a Gas Station, Convient Store, or a strip club". The strip club's
open audit item read: "the fascia pool holds only CLUB VELVET, which never
matches the neon name". Measuring it showed the club is one case of a
library-wide problem.

## What was measured

A building can carry two lit name signs, and each comes from its own table.

| Sign | Who draws it | Name from |
|---|---|---|
| The **band**: a lit cabinet centred on the street-facing facade, 3.6 m up | Lot (`sign_placement`, `SIGN_Z`) | Level Factory `_signs_for`: `sign_family(archetype)`, then a hash into Pixelcoat's `profiles/signs/<theme>.json` pool for that family |
| The **door box**: a lit cabinet over the storefront door | Deli Counter derives the anchor; Zoo `sign_box` paints it | Zoo `storefront_names.sign_for(business)`: a kind from the words of the business string, then a crc32 into that kind's names. A club's neon uses the same rule, so its neon and door agree. |

`two_names.py` (here, with its output in `two_names.txt`) takes all 95
library shells whose `<shell>.lights.json` carries a door anchor. For each it
compares what the door says against every name the band could be dealt
(`delco_1997`, names only, as Level Factory 0.146.0 deals).

**The door's name is in the band's pool for 6 of 95.** Those 6 are the
FLAPPAHS stores, aligned earlier the same day (Pixelcoat 0.58.0). The rest
disagree by construction: the two tables share no names.

The pairings that read worst:

| Building | Door box | Band dealt from |
|---|---|---|
| police station, courthouse, rail station, clinic | POLICE, COURT HOUSE, RAIL STATION, URGENT-ISH CARE | STATE WINE + SPIRITS, KEYSTONE SAVINGS |
| museum, arena, stadium, airport, funeral home | MUSEUM, ARENA, ... STIFF & SONS FUNERAL HOME | GOOSE MART, HOAGIE HUT, BEER WORLD ... |
| casino, country club | THE BROKE BANK CASINO, PIKE HILLS COUNTRY CLUB | CLUB VELVET |
| strip club | its neon's name, e.g. MOM THINKS I'M AT BINGO | CLUB VELVET |
| `strip_retail_a01` (a retail strip) | THE WOODER HOLE, a strip club's name | retail |
| `gs_corner_station`, `fuel_stop_heist` | FLAPPAHS | civic; default |

**In shipped levels** (the `shop sign(s)` line of each cold run's log):
- `county_hospital_001`'s hospital (9171, 9173) wore CORNER TAP, a bar.
- `precinct_yard_001` (9172, seed 9001) dealt CORNER TAP to `train_yard_a02`.
- `restaurant_row_001` (9179, seed 9104) dealt CLUB VELVET to `casino_a02`,
  whose door says it is a casino.

## Two causes, both measured

1. **Two tables name the same building.** Pixelcoat 0.33.0 wrote business
   names for bands. Zoo 1.37.0 then filled the door box, which 9120's walk
   had found blank, from a table of its own. Neither reads the other.
2. **`civic` means two things.**
   - Pixelcoat's `civic` family is state-run commerce: the Pennsylvania
     state liquor store, and a savings bank.
   - Level Factory's `SIGN_FAMILIES` sends police, courthouse, station,
     library, clinic and hospital to `civic`.
   - So a police station is dealt a liquor store. Separately, `station` is a
     substring of `gs_corner_station` and `fuel_station`.

## What this does not measure

Whether both signs are visible on one facade. The band hangs on the facade
nearest a road; the door box hangs over the storefront door, wherever that
is. A close frame of a storefront would answer it. None was taken here,
because cold run 9181 was running and a Godot render would have shared its
machine.

## Options

- **A. The band says the door's name.**
  - One name table, read by every sign. Zoo's door names are the ones
    written to the walker's Delco-slang rule, MACDADE MOVIES among them.
  - Pixelcoat renders a band from whatever text it is given.
  - Most coherent. Needs the table moved to one file that Level Factory,
    Pixelcoat and Zoo all read.
- **B. The door says the band's name.**
  - Level Factory deals the band as now, and passes each building's band
    text to Zoo's door box.
  - Clubs take no band, and keep the neon's rule.
  - Keeps Pixelcoat's plainer names; less Delco.
- **C. One sign each.** Where the door box names the building, no band.
  - Level Factory only.
  - Most named shops lose their big street sign, and streets get plainer.
- **D. Stop the absurd pairings now, Level Factory and Zoo only.**
  - Civic institutions, landmarks, clubs, casinos and country clubs are
    dealt no band; their door box or neon already names them.
  - Gas stations by name (`gs_corner_station`, `fuel_stop_heist`) are dealt
    the gas family.
  - `strip_retail` stops reading as a strip club at its door.
  - Named shops (bank, deli, market, pawn ...) keep two names until A or B.

**Recommended:** D first, because each band it removes is a wrong one and it
pre-empts nothing. Then A, because the names it keeps are the walker's
register.

The walker's call: whether to do D, and whether A or B.
