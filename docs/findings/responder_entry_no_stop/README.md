# The getaway van's mirrors close a responder lane (cold run 9204, roadmap 212)

**Question.** Cold run 9204's validation carries `LOT_RESPONDER_ENTRY_NO_STOP`
twice. Which road ends found no stop, and why?

**One road end, counted twice.** Both issues name road 0's east end at
(92.5, -22.8) on seed_9181, the picked candidate.
- **The first** comes from the candidate's `lot_assemble`.
- **The second** comes from `themed_site_assemble`, which assembles the same
  site again.
- *As first written* in `docs/cold_runs/cold_9204/NOTES.md`: "two road ends
  on this mission found no stop". Wrong: it is one road end.

## The replay

`probe_9204.py` replays Lot's own planner (`site_responders.plan`) on the
job's inputs; `probe_9204.txt` is its output.
- **The inputs:** the job's `site.json`, with the getaway van appended to
  `cover` as `lot.py` has it at that line. The crew's positions come from
  the job's `site_walk.tscn`.
- **It reproduces the job's record:** the same two stops, (40.6, -12.0) and
  (64.0, -25.55), and the same one finding.
- **Then it names every refusal** at every station of the east end's lane.

Plan coordinates in metres, site frame (x east, y north).

## What closes the lane

**Not the other arrivals.** With no other arrival reserved, road 0's east end
still has no stop: plan()'s first pass gives it none (`free stop none`).

**The getaway van, and nothing else.** Every station is refused by the van:

| stations (stop centre x) | refused by |
|---|---|
| 79 to 77 | within 12 m of the crew (C), and the stop on the van (Sv) |
| 76 to 63 | C, and the lane to the stop crosses the van (LSv) |
| 62 to -89 | LSv, and a junction or the other arrivals besides (J, T, LT) |

No lane refusal names anything but the van.

**Across the road at the van, plan y:**

| band | from | to |
|---|---|---|
| the westbound driving half | -24.15 (the centre line) | -21.35 |
| the parking lane (`LANE_DEPTH` 2.2) | -21.35 | -19.15 (the kerb) |
| the van's slot (2.60 m, mirror to mirror) | -21.80 | -19.20 |
| the responder lane box (a 2.0 m cruiser, `LANE_MARGIN` 0.5 each side) | -24.25 | -21.25 |

- **The van stands out of its bay.** Its slot runs 0.45 m past the parking
  lane into the driving half.
- **The lane box overlaps it by 0.55 m.**
- **The cruiser alone overlaps it too.** At the lane centre, with no
  margin, it spans -23.75 to -21.75 and overlaps the van by 0.05 m.

**Why it is the van and nothing parked.** At this line of `lot.py`, the van
is the only cover. `site_getaway` places it before the responders are
planned; the parked cars and `site_cover`'s pieces come after and keep out of
the lanes.

## What it means

**The planner's lane is a rigid corridor.** It runs at the lane's centre,
3.0 m wide, in a driving half 2.8 m wide. A driver would steer round a
parked van's mirrors; the planner cannot.
- **So the van shuts every lane** that has to pass it on its own kerb's
  side.
- **And the stops before the van** are within `CAMP_RADIUS` of the crew,
  who start and finish at the van.

**This is roadmap 206's van meeting roadmap 212's lanes**, not this site's
roads. It will recur wherever an open road end's inbound lane runs along
the van's kerb toward it.

**On 9204** it cost one arrival of three. Two arrived, and Lot's nav QA
walked both.
- **The evidence:** the job's `site_navqa.tscn` lists five bot spawns, two
  of them the responder stops, Godot (40.6, 0, 12) and (64, 0, 25.55).
- **The result:** `site_navqa.walktest.json` reports every walker `ok`.

**The van is meant to overhang.** `site_getaway` stands the body
`KERB_GAP` (0.20 m) off the kerb, and the body is the slot less two
`MIRROR_OUT` (0.15 m), so 2.30 m. Its road side is 2.50 m from the kerb in a
2.2 m parking lane: the body overhangs 0.30 m, and the mirrors 0.45 m. A
step van is wider than a parking lane, and Lot builds it so.

**Not decided here: the fix.** Two candidates:
- **Let the lane steer.** It would shift across the carriageway around
  standing ground, as a driver does round a parked van, keeping its margin
  and keeping clear of whatever is planned after it.
- **Keep the van inside its lane.** That needs a narrower van or a wider
  parking lane: a change to the look and to the street, for one planner's
  sake.

The first is a Lot change, with a test that fails on this site's spec.
