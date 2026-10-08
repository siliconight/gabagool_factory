## 0.99.0 - where responders arrive, and the room they need to

**Roadmap 212, phase 1.** The walker, 2026-10-08, on what makes the walk back
to the getaway van dangerous: "have responders show up after the job, on the
way back (and this would be on the gameplay layer, but we can make thee
assets and ensure there is clearance and routes for their arrival)".

Lot spawns nobody and times nothing. That is the gameplay layer's. What Lot
now does is make sure a heist level can receive responders, and say where.

### `site_responders`: an arrival per open road end

An arrival has four parts:
- **The entry:** an open road end, one that does not lie on another road.
  The plate is walled on four sides with no opening, so a vehicle can only
  appear inside it.
- **The lane:** the inbound driving lane from the entry to the stop. It is
  the half of the carriageway a keep-right driver keeps to, less the parking
  lane, as wide as the vehicle plus `LANE_MARGIN` either side.
- **The stop:** where a cruiser pulls up in that lane, with `DOOR_ROOM` to
  open its doors on both sides.
- **The way back it serves:** the segment from the objective to the
  extraction, which with the van is the walk back to it.

**Where it stops.** The stop is the station along the lane nearest the way
back, nearer the entry on a tie. Four kinds of station are refused:
- one within `CAMP_RADIUS` (12 m) of the crew's spawn or extraction. That
  is `site_audit.CAMP_RADIUS` itself, so the planner and the rule that
  judges it cannot drift apart;
- one that leaves less than `ENTRY_RUN` of lane behind it, so the vehicle
  is seen to drive in;
- one in a junction;
- one in, or one whose lane runs through, anything already standing or
  another arrival's stop. A cruiser standing with its doors open across the
  centre line is in the oncoming lane.

**How many.** One arrival per entry, up to `MAX_ARRIVALS` (3), kept spread by
bearing from the objective when a site has more entries than that.

**The numbers, and which are chosen:**
- `VEHICLE` 2.0 x 5.4 x 1.5 m is **stated**: a 1990s Crown Victoria Police
  Interceptor or Caprice 9C1, 1.99-2.0 m wide and 5.39-5.44 m long. Zoo has
  no cruiser species yet.
- `DOOR_ROOM` 1.0 m is a 1.1 m front door opened to 60 degrees.
- `LANE_MARGIN` 0.5 m and `ENTRY_RUN` (twice the vehicle's length, 10.8 m)
  are **chosen**.

### What `assemble` does with them

- **Planned** after the enemies, before anything is parked or stood in the
  street.
- **Written** as `responder_spawn` site markers at the stops (`source:
  responder_arrival`, the rest under `arrival`), in both the drawn spec and
  the gameplay file.
  - Lot's audit judges them, so `S_RESPONDER_ARC` and `S_RESPONDER_CAMP` run
    for the first time on a generated site.
  - Lot's nav QA already spawns a bot at every `responder_spawn` and walks
    it to the crew's points (`_navqa_anchors`), so the route from each stop
    is walked on the baked navmesh.
- **Reserved:** the stops and lanes reach `plan_parking` as standing ground,
  so a bay beside a stop holds no car to block a door. They reach
  `plan_cover` as the new `keep_out`: rects a piece may not stand in, which
  occlude nothing, because an empty lane hides nobody.
- **Read back** after every planner has run: `LOT_RESPONDER_BLOCKED`
  (major) names any piece standing in a stop or lane. The plan and its
  findings travel as `responder_plan` in the gameplay file.
- **No entry, or no stop:** `LOT_RESPONDERS_NONE` (moderate) when no road
  has an open end; `LOT_RESPONDER_ENTRY_NO_STOP` (minor) when an entry's
  whole lane is refused.

**One test for a road's end** (`site_streets.end_lies_on`). `_ends_on` and
`_slab` each spelled the same arithmetic, and the arrivals would have been a
third copy. All three now ask one function.

### Measured

**The kerb probe** (one road, both ends open, the van on the north kerb).
Two arrivals stop where the crew's way back crosses the road:

| from | stop | off the way back | from the van's door | run in |
|---|---|---|---|---|
| the west end, eastbound | (-51.5, -1.4) | 0.1 m | 14.3 m | 58.5 m |
| the east end, westbound | (-45.5, 1.4) | 5.6 m | 18.8 m | 155.5 m |

The audit says `S_RESPONDER_ARC`: both arrive from a 5 degree arc. On one
road it cannot say anything else.

**Cold run 9198's seed_9256** (cover cut back to the van, which is what
stood when the arrivals were planned). Three open ends -- road 1's other end
is a T on road 0 -- and three arrivals:

| from | stop | off the way back |
|---|---|---|
| road 1's north end | (23.6, 10.0) | 12.7 m |
| road 0's east end | (14.0, -22.75) | 21.5 m |
| road 0's west end | (8.0, -25.55) | 25.2 m |

- **They converge on the van.** The bank stands well back from every road
  here, so the way back comes nearest the roads at the van's end.
- **The road 1 stop sits at 12.7 m** from the van's door, just outside the
  audit's camping line.
- **`S_RESPONDER_ARC` fires.** Every point on this site's roads bears 215 to
  18 degrees from the objective, so no choice of stops could pass it. That
  finding is about the roads.

**The reservation does something real.** Cold run 9198 planned seed_9256
with no reservation, and parked a car in bay L6 on road 1, at (21.112,
14.85) -- in what is now that site's road 1 stop. Given the reservation,
`plan_parking` keeps every car out of every stop and lane.

### Tests

`tests/test_site_responders.py`, 8 tests:
- **The probe, assembled:** an arrival at each open end, keep-right, in a
  driving lane; nothing in any stop or lane; no stop camping the van.
- **seed_9256's site:** the T is not an entry; three arrivals clear of each
  other and of the van.
- **Source:** one test for a road's end.
- **Two controls,** so the clearance tests can fail:
  - 9198's car parks in the stop again without the reservation, and not
    with it;
  - a cover piece refused a kept-out spot stands elsewhere on its line,
    which stays broken, so the kept-out rect hid nothing.

**Results without the change:**
- On 0.98.2 the file cannot import (`site_responders` does not exist).
- With `lot.py` and `site_cover.py` reverted to 0.98.2, 4 fail: the three
  assembled tests and the keep-out test.

**Suite:** 695 passed (687 + 8), `python -m pytest -q`.

### Not yet

- **The package.** The package does not carry the markers yet; the van's
  never reached it either (roadmap 204).
- **The responder vehicle.** Zoo has no cruiser yet; the walker's comps come
  first.
- **The cold run** that proves this in a level.
