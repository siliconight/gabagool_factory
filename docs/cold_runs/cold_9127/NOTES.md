# Cold run 9127 -- the video-poker cabinets

Zoo 1.39.0 (the 1997 tavern video-poker cabinet) and Deli Counter 0.168.0
(cabinets with a stool in stores, bars and clubs). Same brief, same seed, same
lot as 9126. Zero interventions, one observation.

The art leg before export: 0 blockers, 63 findings -- identical to 9126's by
code. Export closure clean (package 1,366 -> 1,394 files).

## The cabinets (`video_poker_variants.png`, Blender; `video_poker_in_level.png`, night)

The four brands -- JAWN JACKPOT, PIKE DRAW, LUCKY HOAGIE, DOWN THE SHORE DRAW
-- each FOR AMUSEMENT ONLY, a dealt hand on the CRT, the pay table on the belly
glass. On club_block_014: six in the strip club, three in each of its two
large rooms (stations 01-03), two on the gas station's sales floor (04, 05).
Every one with its stool in front, facing it. In the club the cabinets' bodies
are near black and their marquees and screens carry them, as the neon does;
in the store they read whole.

Calls left to the walker:
  * one of the gas station's cabinets stands against the storefront glass by
    the door (station 04). The sale posters are kept off the glass
    (`off_glass`); the cabinets are not;
  * six stores lose a poster run to the cabinets (Deli Counter 0.168.0's
    entry has the list; strip_retail_a02 loses both of its runs);
  * the count: 2 a store, 2 a bar or club room, 3 past 80 m2.

A wart, no visible effect: the cabinets' slots carry Deli Counter's default
prop material, `wood`, so their stems are `_mwood`. The recipe draws from its
atlas and ignores the material; the slot should say `metal`, as the ATM's
does. Follow-up.

## The price (`perf_9127.json`, against 9126's)

    total draws, 53 headings   61,201 -> 61,627  (+426, +0.7%; 30 headings)
    largest single change      +67  (extraction_3, yaw 270)
    worst heading on the map   2,626 -> 2,648  (objective_4, yaw 90, +22)
    meshes                     4,455 -> 4,498; over the 8-light cap 44 -> 44

Eight cabinets of two draws and eight stools are fewer submissions than some
headings gained; a shadowed light drawing them again is a candidate and is
not established. The worst heading was already over the provisional 2,000
budget and is 22 further over.
