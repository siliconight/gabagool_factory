# cold run: cold_9002

begun 2026-09-06 14:57:37
2408 source files hashed across 10 tools

| when | kind | what |
|---|---|---|
| 2026-09-06 14:57:39 | intervention | INTERVENTION 1 (before this journal opened, recorded here): brief archetype hospital -> office. All 3 candidates failed deli_generate with 'TACTICAL-ERROR: heist level has no extraction zone', objectives 0, exit 1, and Deli Counter's own message 'This is a preset bug -- please report it'. Probed all 17 presets: hospital is the ONLY one yielding 0 objectives (others 1-3; police_station, which built in cold run 5, has 2). Editing a brief is explicitly the failure mode item 17 is named for, so it counts. |
| 2026-09-06 14:57:42 | observation | urban_bank raises KeyError from presets.make(seed=...) -- a preset three existing briefs ask for. Not touched, not part of this run. |
