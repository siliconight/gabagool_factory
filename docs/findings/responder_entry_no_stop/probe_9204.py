"""Why cold run 9204's road 0 east end found no responder stop: Lot's own
planner, replayed on the job's inputs, every station's refusal named.

    python probe_9204.py [--out probe_9204.txt]

REPRODUCE FIRST. `site_responders.plan` runs inside `lot.py`'s assemble on
a `site_spec` nobody saved. This rebuilds it the way assemble had it at that
line (`lot.py` ~3350): the job's input `site.json`, plus the getaway van
appended to `cover` (`site_getaway.plan` does that a few lines above). The
crew's positions come from the job's own `site_walk.tscn` -- `spawn_pos`,
`objective_pos`, `extraction_pos`, Godot (x, y up, z) turned to site
(x, -z). If the replayed arrivals and findings are not the ones the job
wrote into `site.site.gameplay.json`'s `responder_plan`, this stops: a
reconstruction that does not reproduce the record explains nothing.

THEN NAME EVERY REFUSAL. For the entry with no stop, each station
`_best_stop` tries, with the stops and lanes of the arrivals planned before
it (`plan`'s own order), and every test it fails -- not only the first:
- J  the stop is in a junction;
- C  the stop's centre is within `site_audit.CAMP_RADIUS` of the crew's
     spawn or extraction;
- S  the stop box overlaps standing ground (buildings, blockers, cover);
- T  the stop box overlaps another arrival's stop or lane;
- LS the lane from the entry to the stop overlaps standing ground;
- LT the lane overlaps another arrival's stop.
S and LS are written Sv and LSv when what they hit is the getaway van and
nothing else, So and LSo when anything else is hit. And the same entry
again with no other arrival reserved, to say whether the other arrivals are
what took its stop. Last, the van's slot and the lane's box across the road,
beside the road's own bands, so an overlap has a size.

Plan coordinates, metres, x east and y north (the site frame). Prints what it
measured and stops.
"""
import argparse
import json
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
LOT = ROOT / "lot"
WS = ROOT / "workspaces" / "cold-9204-ws" / ".level_factory"
SPEC = WS / "temp" / "club_block_014" / "candidate_seed_9181" / "site.json"
JOB = WS / "jobs" / "club_block_014.lot_assemble.candidate.seed_9181" / "1" / "out"

sys.path.insert(0, str(LOT))
import site_audit        # noqa: E402
import site_responders as sr   # noqa: E402
import site_spawns       # noqa: E402
import site_streets      # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=str(pathlib.Path(__file__).with_suffix(".txt")))
args = ap.parse_args()
lines = []


def say(s=""):
    print(s)
    lines.append(s)


spec = json.loads(SPEC.read_text(encoding="utf-8"))
record = json.loads((JOB / "site.site.gameplay.json").read_text(encoding="utf-8"))
van = record["getaway_plan"]["placed"]["van"]
spec.setdefault("cover", []).append(van)

walk = (JOB / "site_walk.tscn").read_text(encoding="utf-8")
pos = {}
for key, name in (("spawn", "spawn_pos"), ("objective", "objective_pos"),
                  ("extraction", "extraction_pos")):
    m = re.search(r"^%s = Vector3\(([^,]+), ([^,]+), ([^)]+)\)$" % name, walk, flags=re.M)
    if m is None:
        raise SystemExit(f"{name} not in {JOB / 'site_walk.tscn'}")
    gx, _gy, gz = (float(v) for v in m.groups())
    pos[key] = (gx, -gz, 0.0)
say(f"inputs: {SPEC}")
say(f"        {JOB}")
say(f"crew, site frame: spawn {pos['spawn'][:2]}  objective {pos['objective'][:2]}  "
    f"extraction {pos['extraction'][:2]}")

findings = []
arrivals = sr.plan(spec, pos, findings=findings)
want = record["responder_plan"]
got_stops = [a["stop"] for a in arrivals]
want_stops = [a["stop"] for a in want["arrivals"]]
same = (got_stops == want_stops
        and [f["message"] for f in findings] == [f["message"] for f in want["findings"]])
say(f"replayed arrivals' stops {got_stops}")
say(f"recorded arrivals' stops {want_stops}")
say(f"replayed findings {len(findings)}, recorded {len(want['findings'])}")
if not same:
    raise SystemExit("the replay does not reproduce the job's responder_plan; it explains nothing")
say("REPRODUCED: the replay writes the job's arrivals and findings.")

roads = site_streets.roads(spec)
ends = sr.entries(roads)
spawn, extraction, objective = (tuple(pos[k][:2]) for k in ("spawn", "extraction", "objective"))
way_back = (objective, extraction)
anchors = [spawn, extraction]
standing = site_spawns.solid_rects(spec, margin=0.0) + site_spawns.cover_rects(spec, margin=0.0)
# the van is the one cover piece at this line (`spec` brought none of its own)
cover_now = site_spawns.cover_rects(spec, margin=0.0)
if len(cover_now) != 1:
    raise SystemExit(f"expected the van as the only cover at plan time, found {len(cover_now)} pieces")
van_rect = cover_now[0]
last_lane = None

# plan()'s own order: by the free stop's distance to the way back, then road
# index, then entry station.
order = []
for road, t_entry, travel in ends:
    free = sr._best_stop(road, t_entry, travel, way_back, anchors, standing)
    order.append(((free[5] if free else math.inf), road.index, t_entry, road, travel, free))
order.sort(key=lambda o: o[:3])
say()
say("plan()'s order (free stop's distance to the way back, m):")
for dist, index, t_entry, road, travel, free in order:
    where = road.point(t_entry, sr.lane_offset(road, travel))
    say(f"  road {index} entry ({where[0]:.1f}, {where[1]:.1f}) travel {travel:+d}: "
        f"free stop {'none' if free is None else '(%.1f, %.1f)' % tuple(free[2])} "
        f"at {dist:.3f}")

_name, w, d, _h = sr.VEHICLE
stops, lanes_taken = [], []
for dist, index, t_entry, road, travel, free in order:
    best = sr._best_stop(road, t_entry, travel, way_back, anchors, standing, stops, lanes_taken)
    if best is not None:
        stops.append(best[3])
        lanes_taken.append(best[4])
        continue
    entry = road.point(t_entry, sr.lane_offset(road, travel))
    say()
    say(f"NO STOP: road {index}'s entry at ({entry[0]:.1f}, {entry[1]:.1f}), travel {travel:+d}, "
        f"with {len(stops)} arrival(s) planned before it")
    off = sr.lane_offset(road, travel)
    lo, hi = road.slab
    junctions = sr._junctions(road)
    t = t_entry + travel * (sr.ENTRY_RUN + d / 2.0)
    runs = []
    while lo + d / 2.0 - 1e-9 <= t <= hi - d / 2.0 + 1e-9:
        rear, front = t - d / 2.0, t + d / 2.0
        stop = sr._box(road, t, off, d, w + 2.0 * sr.DOOR_ROOM)
        centre = road.point(t, off)
        why = []
        if any(not (front <= j0 or rear >= j1) for j0, j1 in junctions):
            why.append("J")
        if not all(math.dist(centre, a) >= site_audit.CAMP_RADIUS for a in anchors):
            why.append("C")
        if any(sr._overlaps(stop, r) for r in standing):
            why.append("Sv" if [r for r in standing if sr._overlaps(stop, r)] == [van_rect] else "So")
        if any(sr._overlaps(stop, r) for r in stops + lanes_taken):
            why.append("T")
        t_lane = t - travel * d / 2.0
        lane = sr._box(road, (t_entry + t_lane) / 2.0, off, abs(t_lane - t_entry),
                       w + 2.0 * sr.LANE_MARGIN)
        if any(sr._overlaps(lane, r) for r in standing):
            why.append("LSv" if [r for r in standing if sr._overlaps(lane, r)] == [van_rect] else "LSo")
            last_lane = lane
        if any(sr._overlaps(lane, r) for r in stops):
            why.append("LT")
        key = "+".join(why) or "FEASIBLE"
        if runs and runs[-1][0] == key:
            runs[-1][2] = centre
            runs[-1][3] += 1
        else:
            runs.append([key, centre, centre, 1])
        t += travel * sr.STATION_STEP
    say("  stations along its lane, in the order tried (stop centre x, y):")
    for key, c0, c1, n in runs:
        say(f"    {key:10s} {n:3d} station(s)  ({c0[0]:6.1f}, {c0[1]:6.1f}) .. ({c1[0]:6.1f}, {c1[1]:6.1f})")
    alone = sr._best_stop(road, t_entry, travel, way_back, anchors, standing)
    say(f"  with no other arrival reserved: "
        f"{'no stop either' if alone is None else 'stop at (%.1f, %.1f), %.3f m from the way back' % (alone[2][0], alone[2][1], alone[5])}")

    # ACROSS THE ROAD at the van, in plan y for a road along x. This road's
    # bands from `site_streets`: the centre line, each driving half out to
    # its parking lane, the kerb line.
    if abs(road.along[1]) > 1e-9:
        say("  (road not along x: the across-the-road table is written for one that is)")
        continue
    # every across-the-road figure from road.point, so the sign of the
    # road's perp is the road's and not an assumption
    sign = 1.0 if off > 0 else -1.0
    park = site_streets.LANE_DEPTH if site_streets.has_parking(road) else 0.0
    cy = road.point(0.0)[1]
    kerb = road.point(0.0, sign * road.width / 2.0)[1]
    lane_edge = road.point(0.0, sign * (road.width / 2.0 - park))[1]
    lane_y = road.point(0.0, off)[1]
    side = 1.0 if kerb > cy else -1.0
    say("  across the road at the van, plan y (m):")
    say(f"    centre line {cy:.3f}; this lane's driving half runs to {lane_edge:.3f}; "
        f"parking lane {lane_edge:.3f} to the kerb {kerb:.3f} (LANE_DEPTH {park:g})")
    say(f"    the van's slot {van_rect[1]:.3f} .. {van_rect[3]:.3f} ({van_rect[3] - van_rect[1]:.2f} m, "
        f"x {van_rect[0]:.2f} .. {van_rect[2]:.2f})")
    if last_lane is not None:
        say(f"    the lane box   {last_lane[1]:.3f} .. {last_lane[3]:.3f} "
            f"({last_lane[3] - last_lane[1]:.2f} m: the cruiser's {w:g} m and LANE_MARGIN {sr.LANE_MARGIN:g} each side)")
        ov = min(last_lane[3], van_rect[3]) - max(last_lane[1], van_rect[1])
        say(f"    overlap of the lane box and the van's slot across the road: {ov:.3f} m")
        body = (lane_y - w / 2.0, lane_y + w / 2.0)
        ovb = min(body[1], van_rect[3]) - max(body[0], van_rect[1])
        say(f"    the cruiser alone at the lane centre, {body[0]:.3f} .. {body[1]:.3f}: "
            f"overlap {ovb:.3f} m")
    van_in = (van_rect[1] if side > 0 else van_rect[3])
    say(f"    the van's slot past the parking lane into the driving half: "
        f"{side * (lane_edge - van_in):.3f} m")

pathlib.Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
