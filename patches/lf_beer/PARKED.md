# Level Factory 0.276.0, a beer distributor on Delco Avenue -- PARKED (2026-10-31)

`patch_lf_beer.py` is written and proven (dry runs held; `fails_on_old.out.txt`; the clone's suite passed,
`suite_clone.out.txt`) and NOT applied: its cluster asks for the `beer_distributor` family, which the library has only
once Deli Counter 0.297.0 ships (`patches/dc_beerdist/PARKED.md`). Apply it right after that: `ship_change.py apply
level_factory lf_beer --message <file>`. Zoo 1.157.0 (the door's beer kind) and Pixelcoat 0.71.0 (the beer family)
are shipped.
