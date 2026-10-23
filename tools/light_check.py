"""Judge whether a level reads inside and out at the times of day asked for: one station a room and the mission's exterior cameras, each held to a named target.

    python tools/light_check.py <walk project> [--slots own,night,afternoon] [--out DIR] [--dc DIR]

THE ASK. The walker, 2026-10-09: "a tool that can make sure levels look good
in both interiors and exteriors for both day and night lighting".

WHAT IT CAN JUDGE, AND WHAT IT CANNOT. A histogram cannot say a level looks
designed rather than generated (roadmap 18), and nothing here claims to. This
holds the floor under "looks good" that a number CAN hold:
- a room a person can read;
- a street that has not collapsed to black;
- a frame that has not blown to white;
- by day, the street outshining the shop.
Every target names its source. A target nobody has set yet is PROVISIONAL and
says so, so the walker's eye can move it.

THE SLOTS. A level is set at one time of day and baked for it
(`docs/LEVEL_STANDARD.md` section 17).
- `own` is the level as shipped.
- Any other slot is the level re-baked under that slot's Lux preset by
  `tools/lux_rebake.py`: Level Factory's own bake, which reproduces a shipped
  bake exactly (`docs/findings/light_breakdown/`).
- The slots and their presets, as Level Factory's `_preset_for` picks them:

  | slot | preset |
  |---|---|
  | `night` | Delco Night |
  | `evening` | Blue Hour |
  | `afternoon` | Delco Summer Afternoon |

  `day` means `afternoon`, the one built daylight preset. Morning and noon
  have none, section 17's gap, and asking for either refuses.
- A slot whose preset is the level's own is the shipped bake, not a re-bake.

THE STATIONS.
- **Inside: one a room.** Rooms come from Deli Counter's room list,
  `build/<building>.gameplay.json`, placed through the walk copy's
  `site.tscn`. This is `docs/findings/night_interiors/
  night_interior_census.py`'s derivation: a person's eye 1.6 m over the
  room's floor, 20% along its long axis, looking 80% along it at 1.0 m.
- **The room's kind:**
  - ROW: a fluorescent row;
  - MOODY: below grade, or an objective room that is not a public entrance.
    Bare bulbs, by Deli Counter's `lights.py` rule;
  - DEN: a room in a building with a tinted room probe, a den of sin, dark
    by design (Lux 0.68.2 reads a building the same way).
- **Openings: one a landing (2026-10-23).** Every place an opening comes
  down -- Deli Counter's `lights.opening_landings`, the rule its landing lights
  are placed by -- seen from where a player stands to use it: a stair's upper
  end, 0.8 m past a hole's edge, 0.9 m beside a ladder's top, at eye height on
  the storey above, looking at the landing 0.2 m over its floor. Buildings and
  their specs come from the walk copy's `buildings.json`. A Deli Counter older
  than 0.261.0 has no `opening_landings`, and the check says so rather than
  judging none.
- **Outside: look_shots' own derived cameras.**
  - the spawn and the extraction, on the mission's spine at eye height:
    "street";
  - the objective: "street", or "interior" when it stands inside a room;
  - the four elevations: "facade";
  - the overview: "context", reported and not judged.

THE TARGETS. Luma, 0 to 255, after the grade, as look_shots measures it.

| region | slot | target | source |
|---|---|---|---|
| interior ROW | any | p50 >= 10 | the night census and `LEVEL_STANDARD`'s scorecard, "rooms under 10" |
| interior MOODY | any | p50 >= 5, PROVISIONAL | half the ROW floor: moody rooms take half the fill (`BAKE_FILL_BULB_SHARE`) |
| interior DEN | any | exempt, reported | dark by design (Lux 0.68.2) |
| opening | any | p95 THROUGH ITS RIM >= 20, PROVISIONAL | the walker, 2026-10-23: "you should be able to see into holes to know you can go forward into them" -- a stair opening onto deli_a03's basement read black from above at the landing's own p50 10, so twice the ROW floor; the pixels inside the opening's rim, not the frame (`through_rim`) |
| street | any | p50 >= 2 | `NIGHT_READABILITY`: the collapse is "a median pixel at zero" |
| street | any | near-clip <= 5%, PROVISIONAL | look_shots: 18.6% within 3 codes of white was blown; 1.1 to 3.2% read |
| facade | any | WARN when p95 < 10, or near-clip over 5% | nothing on the facade reaches the ROW floor, or it is blown. An elevation is not a player's view. |
| interior ROW / MOODY | day | WARN when its mean is over the street's median, PROVISIONAL | by day the street outshines the shop (`INTERIOR_EXTERIOR_BALANCE`) |

A day's interior floor is the night's 10: "where that floor sits is a look
call and nobody here has named it" (`INTERIOR_EXTERIOR_BALANCE`). PROVISIONAL
too.

**RETRACTED, kept: a facade judged by its frame's centre p50.** An elevation
frames the whole street orthographically, with the buildings along the
bottom, so its centre third is sky. On cold run 9213 at midnight all four
elevations read centre p95 3, and the moonlit south and west facades (frame
p95 92 and 85) warned with the black north one (3). The whole frame's p95
tells them apart: the brightest twentieth of the frame, against the floor a
person reads a room by.

Writes under --out:
- each slot's shots and look_shots manifest (`<slot>/`, `<slot>.json`);
- `sheets/<slot>.png`: every station's frame, labelled with its verdict;
- `light_check.json` and `light_check.txt`.

Prints the verdicts and stops. Exit 1 when any station FAILs, else 0.
Nothing gates on it yet. The re-bake copies are deleted once shot.
"""
import argparse
import json
import os
import re
import shutil
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import look_shots                                    # noqa: E402
import lux_rebake                                    # noqa: E402
from godot_probe import ProbeFailed, require_godot   # noqa: E402

FACTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#: slot -> the Lux preset Level Factory's `_preset_for` gives it.
SLOT_PRESETS = {"night": "delco_night", "evening": "blue_hour", "afternoon": "delco_summer_afternoon"}
SLOT_ALIASES = {"day": "afternoon", "midnight": "night"}
GAP_SLOTS = ("morning", "noon", "high_noon")
#: preset -> slot class: day (the street outshines the shop) or not.
DAY_PRESETS = {"delco_summer_afternoon", "gas_station_fluorescent", "heavy_rain"}
EYE = 1.6
LOOK_Z = 1.0
ROW_FLOOR = 10
MOODY_FLOOR = 5
OPENING_FLOOR = 20
#: Where the eye stands beside an opening, metres past a hole's edge and beside a ladder's top.
OPENING_STAND_OFF_HOLE = 0.8
OPENING_STAND_OFF_LADDER = 0.9
OPENING_LOOK_Z = 0.2
#: AN OPENING IS JUDGED THROUGH ITS RIM (2026-10-23). A frame looking down an opening is mostly the floor round it,
#: and its p50 is that floor's: on cold run 9384 it passed a ladder hole black inside its rim at 42 and failed a
#: broken-floor hole that showed a lit kitchen. The brightest twentieth through the rim, the facade rule's statistic:
#: measured, a lidded hole 12 and 9, every opening whose landing reads 40 or over
#: (`docs/findings/walk_2026-10-23_deli/through_*.out.txt`).
OPENING_THROUGH_PCT = 95
#: The camera look_shots draws with: Godot's Camera3D default, 75 degrees vertical (it never sets `fov`), aimed by
#: `look_at(target, Vector3.UP)`.
CAMERA_FOV_V = 75.0
BLACK_P50 = 1
NEAR_CLIP_PCT = 5.0
STREET = ("spawn", "extraction", "objective")
FACADE = ("elev_N", "elev_S", "elev_E", "elev_W")


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def placements(walk):
    """``{node name: (archetype, basis rows, origin)}`` for every building the
    walk copy's site.tscn instances from `lot/<archetype>/site.tscn`."""
    t = _read(os.path.join(walk, "site.tscn"))
    res = {i: a for a, i in re.findall(
        r'\[ext_resource type="PackedScene" path="(?:res://)?lot/([^/"]+)/site\.tscn" id="([^"]+)"\]', t)}
    out = {}
    for name, rid, tr in re.findall(
            r'\[node name="([^"]+)"[^\]]*instance=ExtResource\("([^"]+)"\)\]\ntransform = Transform3D\(([^)]*)\)', t):
        if rid not in res:
            continue
        v = [float(x) for x in tr.split(",")]
        # the written numbers ARE the rows (`tools/godot_transform.py`); until
        # 2026-10-19 this built the transpose, turning a quarter-turned
        # building's points the other way about its origin (roadmap 177)
        basis = ((v[0], v[1], v[2]), (v[3], v[4], v[5]), (v[6], v[7], v[8]))
        out[name] = (res[rid], basis, (v[9], v[10], v[11]))
    return out


def to_site(place, p):
    """Deli Counter's spec frame (x, y, z up) -> Godot building-local
    (x, z, -y) -> the site, by the building's node transform."""
    _arch, basis, origin = place
    local = (p[0], p[2], -p[1])
    return tuple(sum(basis[r][c] * local[c] for c in range(3)) + origin[r] for r in range(3))


def dens(walk, places):
    """Node names of buildings with a tinted interior room probe. A probe is
    named `<node>_<room>_ambient` (Lux's room probes, Lot's building ids)."""
    t = _read(os.path.join(walk, "presentation", "lux.applied.tscn"))
    out = set()
    for m in re.finditer(r'^\[node name="([^"]+)" type="ReflectionProbe" parent="[^"]+"[^\]]*\]\n((?:[^\[\n].*\n|\n)*)',
                         t, re.M):
        kv = dict(re.findall(r"^(\w+) = (.+)$", m.group(2), re.M))
        if kv.get("interior") != "true":
            continue
        col = re.search(r"Color\(([^)]*)\)", kv.get("ambient_color", "Color(1, 1, 1, 1)"))
        rgb = [float(c) for c in col.group(1).split(",")[:3]]
        if any(abs(c - 1.0) > 1e-6 for c in rgb):
            node = m.group(1).split("_", 1)[0]
            if node in places:
                out.add(node)
    return out


def rooms(walk, dc):
    """One station a room, and each room's box in the site frame."""
    places = placements(walk)
    den = dens(walk, places)
    out, skipped = [], []
    for node, place in sorted(places.items()):
        arch = place[0]
        g = os.path.join(dc, "build", arch + ".gameplay.json")
        if not os.path.exists(g):
            skipped.append(arch)
            continue
        with open(g, encoding="utf-8") as fh:
            rs = json.load(fh).get("rooms") or []
        for r in rs:
            x0, y0, x1, y1 = r["bounds"]
            fz = float((r.get("center") or [0, 0, 0])[2])
            story = int(r.get("story", 0) or 0)
            if node in den:
                kind = "DEN"
            elif story < 0 or (bool(r.get("objective")) and r.get("role") != "public_entry"):
                kind = "MOODY"
            else:
                kind = "ROW"
            if (x1 - x0) >= (y1 - y0):
                cy = (y0 + y1) / 2.0
                eye, tgt = (x0 + 0.2 * (x1 - x0), cy, fz + EYE), (x0 + 0.8 * (x1 - x0), cy, fz + LOOK_Z)
            else:
                cx = (x0 + x1) / 2.0
                eye, tgt = (cx, y0 + 0.2 * (y1 - y0), fz + EYE), (cx, y0 + 0.8 * (y1 - y0), fz + LOOK_Z)
            e, t = to_site(place, eye), to_site(place, tgt)
            corners = [to_site(place, (x, y, z)) for x in (x0, x1) for y in (y0, y1) for z in (fz, fz + 3.0)]
            box = tuple(min(c[k] for c in corners) for k in range(3)) + tuple(max(c[k] for c in corners) for k in range(3))
            out.append({"name": "%s__%s" % (arch, r["id"]), "building": arch, "node": node, "room": r["id"],
                        "story": story, "kind": kind, "box": box,
                        "spec": ",".join("%.3f" % c for c in e + t)})
    return out, skipped, sorted(places[n][0] for n in den)


def openings(walk, dc):
    """One station an opening's landing: ``([{name, building, node, kind, story, spec}], note)``, the eye where a
    player stands to use the opening, looking down at where it lands -- in the site frame. ``note`` says why there
    are none when there are none for a reason (no buildings.json, a Deli Counter without `opening_landings`)."""
    path = os.path.join(walk, "buildings.json")
    if not os.path.isfile(path):
        return [], "no buildings.json in the walk copy: openings not judged"
    if dc not in sys.path:
        sys.path.insert(0, dc)
    try:
        import axonometric
        import ladder_geom
        import lights
        import spec_loader
        import stairwell
    except ImportError as e:
        return [], "Deli Counter not importable (%s): openings not judged" % e
    if not hasattr(lights, "opening_landings"):
        return [], "Deli Counter has no lights.opening_landings (before 0.261.0): openings not judged"
    places = placements(walk)
    with open(path, encoding="utf-8") as fh:
        entries = json.load(fh).get("buildings") or []
    out, done = [], set()
    for e in entries:
        node, spec_name = e.get("node"), e.get("spec")
        if e.get("kind") != "building" or not spec_name or node not in places or node in done:
            continue
        done.add(node)
        spec_path = os.path.join(dc, "specs", spec_name + ".json")
        if not os.path.isfile(spec_path):
            continue
        spec = spec_loader.load_spec(spec_path)
        sh = float(spec.story_height)
        holes = axonometric._slab_holes(spec)
        bx, by = 0.0, 0.0
        for k, g in enumerate(lights.opening_landings(spec)):
            s, lx, ly = g["story"], g["x"], g["y"]
            eye = None
            rim = None   # the slab cut the opening is looked down through: (x0, y0, x1, y1), the slab's top
            if g["kind"] == "stair":
                for st in getattr(spec, "stairs", []) or []:
                    ends = stairwell.stair_endpoints(st)
                    low = [x for x in ends if x["end"] == "lower"]
                    up = [x for x in ends if x["end"] == "upper"]
                    if low and up and min(st.from_story, st.to_story) == s \
                            and abs(low[0]["point"][0] - lx) < 0.01 and abs(low[0]["point"][1] - ly) < 0.01:
                        top = max(st.from_story, st.to_story)
                        eye = (up[0]["point"][0], up[0]["point"][1], top * sh + EYE)
                        rim = (stairwell.footprint_rect(st), top * sh)
                        break
            elif g["kind"] == "hole":
                for r, kind in holes.get(s + 1, []):
                    if kind != "stair" and r[0] <= lx <= r[2] and r[1] <= ly <= r[3]:
                        # past the edge nearest the building's middle, on the storey above
                        sides = [(r[0] - OPENING_STAND_OFF_HOLE, ly), (r[2] + OPENING_STAND_OFF_HOLE, ly),
                                 (lx, r[1] - OPENING_STAND_OFF_HOLE), (lx, r[3] + OPENING_STAND_OFF_HOLE)]
                        ex, ey = min(sides, key=lambda p: (p[0] - bx) ** 2 + (p[1] - by) ** 2)
                        eye = (ex, ey, (s + 1) * sh + EYE)
                        rim = (r, (s + 1) * sh)
                        break
            elif g["kind"] == "ladder":
                for ld in getattr(spec, "ladders", []) or []:
                    if abs(ld.x - lx) < 0.01 and abs(ld.y - ly) < 0.01:
                        top = max(ld.from_story, ld.to_story)
                        d = OPENING_STAND_OFF_LADDER
                        dx, dy = (-1.0 if lx > bx else 1.0), (-1.0 if ly > by else 1.0)
                        eye = (lx + dx * d * 0.7071, ly + dy * d * 0.7071, top * sh + EYE)
                        hx, hy, hsx, hsy = ladder_geom.through_hole(ld.x, ld.y, ld.width, ld.facing)
                        rim = ((hx - hsx / 2.0, hy - hsy / 2.0, hx + hsx / 2.0, hy + hsy / 2.0), top * sh)
                        break
            if eye is None:
                continue
            place = places[node]
            e3, t3 = to_site(place, eye), to_site(place, (lx, ly, s * sh + OPENING_LOOK_Z))
            (rx0, ry0, rx1, ry1), rz = rim
            out.append({"name": "%s__open_%s_%d" % (e.get("id", spec_name), g["kind"], k), "building": e.get("id"),
                        "node": node, "kind": g["kind"], "story": s,
                        "spec": ",".join("%.3f" % c for c in e3 + t3),
                        "rim": [list(to_site(place, (x, y, rz))) for x, y in
                                ((rx0, ry0), (rx1, ry0), (rx1, ry1), (rx0, ry1))]})
    return out, None


def project(eye, target, pts, width, height, fov_v=CAMERA_FOV_V):
    """Site points -> frame pixels ``[(u, v)]`` for a camera at `eye` aimed at `target` with Y up, as Godot's
    `look_at` aims it and its perspective projection draws it (keep-height, `fov_v` degrees vertical); None when a
    point is behind the camera."""
    import math
    sub = [eye[i] - target[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in sub))
    z = [c / n for c in sub]
    x = [z[2], 0.0, -z[0]]                                    # Y x z
    n = math.sqrt(sum(c * c for c in x))
    x = [c / n for c in x]
    y = [z[1] * x[2] - z[2] * x[1], z[2] * x[0] - z[0] * x[2], z[0] * x[1] - z[1] * x[0]]
    f = 1.0 / math.tan(math.radians(fov_v) / 2.0)
    out = []
    for p in pts:
        d = [p[i] - eye[i] for i in range(3)]
        cx, cy, cz = (sum(d[i] * a[i] for i in range(3)) for a in (x, y, z))
        if cz >= 0:
            return None
        out.append(((f * cx / -cz / (width / height) + 1.0) / 2.0 * width, (1.0 - f * cy / -cz) / 2.0 * height))
    return out


def through_rim(shot, rim):
    """Luma 0-255 of the frame's pixels inside an opening's rim: ``{p50, p95, mean, frame_pct, pixels}``, or None
    when the shot has no PNG, the rim is behind the camera or covers no pixel. Rec.709, as look_shots measures."""
    png = shot.get("png")
    if not rim or not png or not os.path.isfile(png) or not shot.get("eye") or not shot.get("target"):
        return None
    from PIL import Image, ImageDraw
    img = Image.open(png).convert("RGB")
    w, h = img.size
    uv = project(shot["eye"], shot["target"], rim, w, h)
    if uv is None:
        return None
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon([(float(u), float(v)) for u, v in uv], fill=255)
    rgb, inside = img.tobytes(), mask.tobytes()
    lum = sorted(0.2126 * rgb[3 * i] + 0.7152 * rgb[3 * i + 1] + 0.0722 * rgb[3 * i + 2]
                 for i in range(w * h) if inside[i])
    if not lum:
        return None

    def pct(q):
        return lum[min(len(lum) - 1, int(q / 100.0 * len(lum)))]
    return {"p50": round(pct(50), 1), "p95": round(pct(OPENING_THROUGH_PCT), 1),
            "mean": round(sum(lum) / len(lum), 1), "frame_pct": round(100.0 * len(lum) / (w * h), 1),
            "pixels": len(lum)}


def judge(region, kind, shot, day, street_median):
    """(verdict, rule) for one station's frame."""
    p50, near, mean = shot["p50"], shot["near_clipped_pct"], shot["mean"]
    if region == "opening":
        # through its rim (`through_rim`), not the frame: the frame is mostly the floor round the opening
        th = shot.get("through")
        if not th:
            return "REPORT", "the rim is not in the frame: not judged (frame p50 %d)" % p50
        if th["p95"] < OPENING_FLOOR:
            return "FAIL", "through its rim p95 %d under the OPENING floor %d: what it leads to does not read" % (
                th["p95"], OPENING_FLOOR)
        return "PASS", "through its rim p95 %d at or over %d" % (th["p95"], OPENING_FLOOR)
    if region == "interior":
        if kind == "DEN":
            return "EXEMPT", "a den of sin, dark by design"
        floor = ROW_FLOOR if kind == "ROW" else MOODY_FLOOR
        if p50 < floor:
            return "FAIL", "p50 %d under the %s floor %d" % (p50, kind, floor)
        if day and street_median is not None and mean > street_median:
            return "WARN", "by day it is brighter than the street (%.1f over %.1f)" % (mean, street_median)
        return "PASS", "p50 %d at or over %d" % (p50, floor)
    if region == "street":
        if p50 <= BLACK_P50:
            return "FAIL", "collapsed to black: p50 %d" % p50
        if near > NEAR_CLIP_PCT:
            return "FAIL", "blown: %.1f%% within 3 codes of white" % near
        return "PASS", "p50 %d, near-clip %.1f%%" % (p50, near)
    if region == "facade":
        p95 = shot["p95"]
        if p95 < ROW_FLOOR:
            return "WARN", "nothing on it reaches the floor %d: p95 %d" % (ROW_FLOOR, p95)
        if near > NEAR_CLIP_PCT:
            return "WARN", "blown: %.1f%% within 3 codes of white" % near
        return "PASS", "p95 %d" % p95
    return "REPORT", "context"


def slot_list(asked, own):
    out = []
    for s in [x.strip() for x in asked.split(",") if x.strip()]:
        s = SLOT_ALIASES.get(s, s)
        if s in GAP_SLOTS:
            raise SystemExit("no Lux preset for %s: LEVEL_STANDARD section 17's gap" % s)
        if s == "own":
            name = os.path.splitext(os.path.basename(own))[0]
            out.append(("own", name, None))
        elif s in SLOT_PRESETS:
            preset = SLOT_PRESETS[s]
            same = preset == os.path.splitext(os.path.basename(own))[0]
            out.append((s, preset, None if same else preset))
        else:
            raise SystemExit("no slot %s; the slots are own, %s, and day for afternoon"
                             % (s, ", ".join(SLOT_PRESETS)))
    return out


def sheet(path, entries):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return False
    tw, th, per = 320, 180, 5
    rows = (len(entries) + per - 1) // per
    img = Image.new("RGB", (tw * per, (th + 30) * rows), (0, 0, 0))
    d = ImageDraw.Draw(img)
    colour = {"PASS": (120, 220, 120), "WARN": (240, 200, 80), "FAIL": (250, 90, 90),
              "EXEMPT": (170, 170, 170), "REPORT": (170, 170, 170)}
    for i, (name, verdict, shot) in enumerate(entries):
        x, y = (i % per) * tw, (i // per) * (th + 30)
        if os.path.isfile(shot.get("png", "")):
            img.paste(Image.open(shot["png"]).convert("RGB").resize((tw, th)), (x, y + 30))
        d.text((x + 4, y + 2), name[:44], fill=(255, 255, 255))
        d.text((x + 4, y + 15), "%s  p50 %d  mean %.1f" % (verdict, shot["p50"], shot["mean"]),
               fill=colour.get(verdict, (255, 255, 255)))
    img.save(path)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("project", help="the walk project to judge")
    ap.add_argument("--slots", default="own,night,afternoon",
                    help="own, night, evening, afternoon (day); default own,night,afternoon")
    ap.add_argument("--out", default="light_check")
    ap.add_argument("--dc", default=os.path.join(FACTORY, "deli_counter"),
                    help="Deli Counter, for its room lists")
    ap.add_argument("--timeout", type=int, default=1800)
    a = ap.parse_args(argv)
    out = os.path.abspath(a.out)
    os.makedirs(os.path.join(out, "sheets"), exist_ok=True)
    own = lux_rebake.active_preset(a.project)
    slots = slot_list(a.slots, own)
    rs, skipped, den_buildings = rooms(a.project, a.dc)
    ops, ops_note = openings(a.project, a.dc)
    stations = ["%s:%s" % (r["name"], r["spec"]) for r in rs] + ["%s:%s" % (o["name"], o["spec"]) for o in ops]
    by_name = {r["name"]: r for r in rs}
    by_name.update({o["name"]: dict(o, region="opening") for o in ops})
    godot = None
    report = {"project": os.path.abspath(a.project), "own_preset": own, "rooms": len(rs),
              "skipped_no_room_list": skipped, "dens": den_buildings, "slots": {}}
    lines = ["light check: %s" % os.path.abspath(a.project),
             "own preset %s; %d rooms; dens of sin: %s; no room list (not judged): %s"
             % (own, len(rs), ", ".join(den_buildings) or "none", ", ".join(skipped) or "none"),
             "openings: %d station(s)%s" % (len(ops), "; " + ops_note if ops_note else "")]
    report["openings"] = len(ops)
    report["openings_note"] = ops_note
    failed = 0
    seen = {}
    for slot, preset, rebake_preset in slots:
        key = preset
        if key in seen:
            continue
        seen[key] = slot
        proj = a.project
        rebake_note = None
        if rebake_preset:
            if godot is None:
                godot = require_godot()
            proj = os.path.join(out, slot + "_project")
            print("[light_check] %s: re-baking a copy under %s" % (slot, rebake_preset), flush=True)
            rep = lux_rebake.rebake(a.project, proj, godot, preset=rebake_preset,
                                    log=lambda s: print("    " + s))
            rebake_note = {k: rep.get(k) for k in ("ok", "reason", "editor_s", "room_fills", "rebake")}
            if not rep.get("ok"):
                lines.append("")
                lines.append("SLOT %s (%s): NOT JUDGED, the re-bake failed: %s" % (slot, preset, rep.get("reason")))
                report["slots"][slot] = {"preset": preset, "rebake": rebake_note, "error": "re-bake failed"}
                failed += 1
                shutil.rmtree(proj, ignore_errors=True)
                continue
        print("[light_check] %s: shooting %d rooms and the exterior under %s" % (slot, len(rs), preset), flush=True)
        try:
            r = look_shots.shoot(proj, os.path.join(out, slot), stations=stations, timeout=a.timeout)
        except ProbeFailed as e:
            r = {"error": "NOT MEASURED: " + str(e)}
        with open(os.path.join(out, slot + ".json"), "w", encoding="utf-8") as fh:
            json.dump(r, fh, indent=1)
        if rebake_preset:
            shutil.rmtree(proj, ignore_errors=True)
        if "error" in r:
            lines += ["", "SLOT %s (%s): NOT JUDGED: %s" % (slot, preset, r["error"])]
            report["slots"][slot] = {"preset": preset, "rebake": rebake_note, "error": r["error"]}
            failed += 1
            continue
        shots = {s["name"]: s for s in r.get("shots", []) if s.get("pixels")}
        day = preset in DAY_PRESETS
        street = [shots[n]["mean"] for n in ("spawn", "extraction") if n in shots]
        street_median = statistics.median(street) if street else None
        rows = []
        for name, shot in shots.items():
            if name in by_name:
                # a room's station is interior; an opening's carries its own region, held to its own floor
                region, kind = by_name[name].get("region", "interior"), by_name[name]["kind"]
            elif name == "objective":
                eye = shot.get("eye") or [0, 0, 0]
                inside = next((rm for rm in rs if all(rm["box"][k] <= eye[k] <= rm["box"][k + 3] for k in range(3))),
                              None)
                region, kind = ("interior", inside["kind"]) if inside else ("street", "-")
            elif name in STREET:
                region, kind = "street", "-"
            elif name in FACADE:
                region, kind = "facade", "-"
            else:
                region, kind = "context", "-"
            if region == "opening":
                shot = dict(shot, through=through_rim(shot, by_name[name].get("rim")))
            verdict, rule = judge(region, kind, shot, day, street_median)
            rows.append({"station": name, "region": region, "kind": kind, "verdict": verdict, "rule": rule,
                         "mean": round(shot["mean"], 1), "p50": shot["p50"],
                         "near_clip_pct": round(shot["near_clipped_pct"], 2),
                         "crushed_pct": round(shot["crushed_pct"], 1), "png": shot.get("png"),
                         "through": shot.get("through")})
        order = {"interior": 0, "opening": 1, "street": 2, "facade": 3, "context": 4}
        rows.sort(key=lambda x: (order[x["region"]], x["station"]))
        counts = {}
        for x in rows:
            counts[x["verdict"]] = counts.get(x["verdict"], 0) + 1
        failed += counts.get("FAIL", 0)
        lines += ["", "SLOT %s: %s%s, %s; the street's median %s"
                  % (slot, preset, " (re-baked)" if rebake_preset else " (as shipped)",
                     "day" if day else "not day",
                     "%.1f" % street_median if street_median is not None else "-"),
                  "  " + "  ".join("%s %d" % (k, v) for k, v in sorted(counts.items())),
                  "  %-46s %-8s %-6s %6s %4s %6s  %-6s %s" % ("station", "region", "kind", "mean", "p50",
                                                             "near%", "", "rule")]
        for x in rows:
            lines.append("  %-46s %-8s %-6s %6.1f %4d %6.2f  %-6s %s"
                         % (x["station"][:46], x["region"], x["kind"], x["mean"], x["p50"], x["near_clip_pct"],
                            x["verdict"], x["rule"]))
        sheet(os.path.join(out, "sheets", slot + ".png"),
              [(x["station"], x["verdict"], shots[x["station"]]) for x in rows])
        report["slots"][slot] = {"preset": preset, "day": day, "rebake": rebake_note,
                                 "street_median": street_median, "counts": counts, "stations": rows}
    text = "\n".join(lines)
    print(text)
    with open(os.path.join(out, "light_check.txt"), "w", encoding="utf-8") as fh:
        fh.write(text + "\n")
    with open(os.path.join(out, "light_check.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
