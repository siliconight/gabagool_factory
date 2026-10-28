

# --- 0.135.0: the lane as the research drew it ------------------------------------------------------------------------
#
# The walker, 2026-10-27, of the drive-up's first frames: "do some more research, make it look better". A bank
# drive-up plan details a clearance bar at the lane's entry ('PROPOSED NEW CLEARANCE "HEADACHE BAR"', Albuquerque,
# 2022); a traffic review asks a bank's drive-up for a pavement arrow at its exit and its lanes kept apart from the
# lot's other traffic (Albuquerque; Madison). The first frames read as a canopy standing in a parking lot: the lanes
# were the lot's own asphalt, unmarked.

CLEARANCE_SPECIES = "clearance_bar"
#: across the served lane, its posts 3 cm in from the wall and the island (a post on the wall's plane would z-fight
#: it); the genome's least width is 3.91
CLEARANCE_W = round(LANE - 0.06, 3)
CLEARANCE_D = 0.25
CLEARANCE_H = 3.6
CLEARANCE_POST = 0.20                    # Zoo's `recipes/clearance_bar.py` POST
#: how far into the lane from the block's entry end
CLEARANCE_IN = 1.0
BOLLARD_SPECIES = "bollard"
BOLLARD = (0.22, 0.22, 1.05)             # Zoo's genome default
#: the bollards on the island line, this far either side of the station along the lane
BOLLARD_OFF = 1.0
#: the paint: white arrows, a safety-yellow island
WHITE = (0.90, 0.90, 0.88)
YELLOW = (0.93, 0.74, 0.12)
STRIPE = 0.15
ARROW_SHAFT = 2.4
ARROW_HEAD = 0.9
ARROW_HEAD_DEG = 30.0
#: an arrow's tip this far from the lane's end it points to
ARROW_IN = 2.0


def _lane_frame(d, road):
    """``(sgn, near, far, travel_served)``: the block's side of the road, its near (sidewalk) and far ends across the
    road, and +1 when the served lane runs away from the road."""
    sgn = 1 if d["side"] == "L" else -1
    near = road.width / 2.0 + road.sidewalk
    far = near + d["size"][1]
    return sgn, near, far, (1 if d["served_travel"] == "away" else -1)


def lane_pieces(d, road):
    """The clearance bar at the served lane's entry and two bollards guarding the station, as cover records. A
    clearance bar's record is a post, a pole's rule (`module_at`), so no box stands across the lane in greybox or in
    the sightline count."""
    import site_parking
    sgn, near, far, travel = _lane_frame(d, road)
    lanes = d["lanes"]
    served_t, island_t = lanes["served"], lanes["island"]
    # the entry end, and the direction a car comes from
    o_entry = sgn * (near if travel > 0 else far)
    o_bar = o_entry + sgn * travel * (CLEARANCE_IN)
    away = (road.perp[0] * sgn, road.perp[1] * sgn)
    travel_vec = (away[0] * travel, away[1] * travel)
    yaw = site_parking.yaw_facing(-travel_vec[0], -travel_vec[1])
    mx, my = road.point(served_t, o_bar)
    # the post on the island's side of the served lane
    side = 1.0 if island_t > served_t else -1.0
    px, py = road.point(served_t + side * (CLEARANCE_W / 2.0 - CLEARANCE_POST / 2.0), o_bar)
    bar = _piece(f"ClearanceBar_{d['building']}", CLEARANCE_SPECIES, (px, py), (CLEARANCE_W, CLEARANCE_D, CLEARANCE_H),
                 yaw, f"drive-up {d['building']}")
    bar["size"] = [CLEARANCE_POST, CLEARANCE_H, CLEARANCE_D]
    bar["module_at"] = [round(mx, 3), round(my, 3)]
    out = [bar]
    o_mid = sgn * (near + far) / 2.0
    for k, off in enumerate((-BOLLARD_OFF, BOLLARD_OFF)):
        bx, by = road.point(island_t, o_mid + off)
        out.append(_piece(f"Bollard_{d['building']}_{k}", BOLLARD_SPECIES, (bx, by), BOLLARD, 0.0,
                          f"drive-up {d['building']}"))
    return out


def markings(driveups, roads_list):
    """The lanes' paint, in `site_streets._marking`'s record: the island in safety yellow, and an arrow on each lane,
    the served lane's the way it runs, the passing lane's the other."""
    by_index = {r.index: r for r in roads_list}
    out = []
    for d in driveups or []:
        road = by_index.get(d["road"])
        if road is None:
            continue
        sgn, near, far, travel = _lane_frame(d, road)
        lanes = d["lanes"]
        # the island, its length the block's less a metre each end
        ix, iy = road.point(lanes["island"], sgn * (near + far) / 2.0)
        out.append({"kind": "driveup_island", "road": road.index, "at": [round(ix, 4), round(iy, 4)],
                    "yaw": round(road.angle_deg + 90.0, 4), "size": [round(far - near - 2.0, 4), ISLAND - 0.2],
                    "color": list(YELLOW), "driveup": d["name"]})
        for lane, direction in (("served", travel), ("passing", -travel)):
            out += _arrow(road, lanes[lane], sgn, near, far, direction, d["name"])
    return out


def _arrow(road, t, sgn, near, far, direction, name):
    """Three strokes: a shaft along the lane and two heads back from its tip, `ARROW_HEAD_DEG` off it."""
    tip_o = sgn * ((far - ARROW_IN) if direction > 0 else (near + ARROW_IN))
    ang = math.degrees(math.atan2(road.perp[1] * sgn * direction, road.perp[0] * sgn * direction))
    ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    tx, ty = road.point(t, tip_o)
    out = []
    sx, sy = tx - ux * ARROW_SHAFT / 2.0, ty - uy * ARROW_SHAFT / 2.0
    out.append({"kind": "driveup_arrow", "road": road.index, "at": [round(sx, 4), round(sy, 4)],
                "yaw": round(ang, 4), "size": [ARROW_SHAFT, STRIPE], "color": list(WHITE), "driveup": name})
    for s in (1.0, -1.0):
        a = ang + 180.0 + s * ARROW_HEAD_DEG
        hx = tx + math.cos(math.radians(a)) * ARROW_HEAD / 2.0
        hy = ty + math.sin(math.radians(a)) * ARROW_HEAD / 2.0
        out.append({"kind": "driveup_arrow", "road": road.index, "at": [round(hx, 4), round(hy, 4)],
                    "yaw": round(a % 360.0, 4), "size": [ARROW_HEAD, STRIPE], "color": list(WHITE), "driveup": name})
    return out
