---
name: indoor-fixture-placement
description: "Walker 2026-10-10: indoor light fixtures should not always stand in a perfect line (roadmap 229). SHIPPED: DC 0.206.0/0.206.1 (rows to the work on the ceiling grid, the home rule), 0.207.0 (rows over the aisles, the long hall's trade; seen in 9232), 0.207.1 (a home's room takes a fixture a 7 m bay; the dark hideout fixed by count); left: species (dome, pendant, strip light, sconce, high-bay, exit sign), benches/bar, duct runs; fix by cause, never jitter"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 27f14f8b-7ce5-44c0-a704-178a824035d7
  modified: 2026-10-11T01:08:49.058Z
---

The walker, 2026-10-10: "making indoor light fixtures not always be in a
perfect line, so it looks a little less robotic in the line/lighting
placement", with nine references digested in
`docs/reference/INDOOR_FIXTURE_PLACEMENT_GUIDE.md` (roadmap 229).

**Why:** the census (`docs/findings/fixture_rows/`) read 513 of 513
fluorescent rows on their room's centreline along its longer axis, one
rule lighting every room from its bounds alone.

**What shipped, by cause and never by jitter:**
- DC 0.206.0: rows laid to the WORK PLANE (WOOD's rule), as many across
  the width as it asks, each on the 0.6 m tile or 0.4 m joist pitch; a
  home's room one fixture. Seen and priced in cold run 9229 (+122 draws,
  4 %, no frame time inside the spread).
- DC 0.206.1: the home rule keys on the ROOM's words too.
- DC 0.207.0: rows over the AISLES between shelf runs (lanes at least the
  contract's 1.25 m, each a floor of its own width); the LONG HALL's trade
  where the cap binds; a FIELD of staggered islands keeps the grid (the
  first rebuild without that rule left the gas station's floor 14 m
  dark). Seen in cold run 9232: the deli's market aisles on the lanes'
  centres by construction.
- DC 0.207.1 (2026-10-11): a home's room takes a fixture a 7 m BAY
  (`_HOME_SPACING`; the guide lights a home a room at a time), one bay
  keeping its one fixture at its centre byte for byte, a bigger room a
  grid of bays at the bays' centres, never snapped; the deli's 21 x 16 m
  hideout (dark at both ends under one troffer in 9232's frames) takes
  two rows of three. Library: 1,071 rows / 4,102 lamps (0.207.0: 1,048 /
  3,933); 39 rooms changed, all residence buildings and residence-like
  rooms. Not yet seen in a level: a residence-heavy brief
  (apartment_walkup, twin) would show it.

**How to apply next:**
- Show the walker the frames (9229's rows, 9232's aisles and hideout);
  their eye decides density; the fixture in a home is still a TROFFER --
  a dome or pendant is the species step.
- Left on 229: the species (dome, pendant, strip light, sconce, high-bay,
  exit sign: Zoo + Lux + DC); the layout by use beyond aisles (benches,
  the bar's pendants, the counter's work side); structural causes beyond
  the grid and the aisles (a duct run); daylight switching the window row.
- Every new rule: a pure test, THEN the library diff over the furnished
  specs (`docs/findings/fixture_rows/aisle_rows_diff.py`, examples read),
  THEN the rebuild. The draws are the price to watch: every fixture is
  hardware.

See [[open-work-2026-10-09]], [[authorship-guide]].
