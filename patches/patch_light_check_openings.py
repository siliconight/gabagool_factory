"""The light check looks down every opening (the walker's walk of cold run 9383, finding 1). The walker, of a stair
opening onto deli_a03's basement: "this shouldn't look pitch black" -- "you should be able to see into holes to know
you can go forward into them". `tools/light_check.py` had one station a room, the eye inside the room, so it judged the
basement's cold storage a PASS at luma p50 10 by the MOODY floor while the walker, looking down into it from the
stairwell, saw black. This adds an OPENING station for every place an opening lands (Deli Counter's
`lights.opening_landings`, the rule its landing lights are placed by, 0.261.0): the eye where a player stands to use the
opening -- a stair's upper end, past a hole's edge, beside a ladder's top -- looking down at the landing, held to its
own floor. Adds `tools/test_light_check_openings.py`. Anchored; refuses on a miss.

    python patches/patch_light_check_openings.py && python tools/test_light_check_openings.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LC = ROOT / "tools" / "light_check.py"
TEST = ROOT / "tools" / "test_light_check_openings.py"

EDITS = [
    ("""| interior DEN | any | exempt, reported | dark by design (Lux 0.68.2) |""",
     """| interior DEN | any | exempt, reported | dark by design (Lux 0.68.2) |
| opening | any | p50 >= 20, PROVISIONAL | the walker, 2026-10-23: "you should be able to see into holes to know you can go forward into them" -- a stair opening onto deli_a03's basement read black from above at the landing's own p50 10, so twice the ROW floor |"""),
    ("""- **Outside: look_shots' own derived cameras.**""",
     """- **Openings: one a landing (2026-10-23).** Every place an opening comes
  down -- Deli Counter's `lights.opening_landings`, the rule its landing lights
  are placed by -- seen from where a player stands to use it: a stair's upper
  end, 0.8 m past a hole's edge, 0.9 m beside a ladder's top, at eye height on
  the storey above, looking at the landing 0.2 m over its floor. Buildings and
  their specs come from the walk copy's `buildings.json`. A Deli Counter older
  than 0.261.0 has no `opening_landings`, and the check says so rather than
  judging none.
- **Outside: look_shots' own derived cameras.**"""),
    ("""ROW_FLOOR = 10
MOODY_FLOOR = 5""",
     """ROW_FLOOR = 10
MOODY_FLOOR = 5
OPENING_FLOOR = 20
#: Where the eye stands beside an opening, metres past a hole's edge and beside a ladder's top.
OPENING_STAND_OFF_HOLE = 0.8
OPENING_STAND_OFF_LADDER = 0.9
OPENING_LOOK_Z = 0.2"""),
    ("""def judge(region, kind, shot, day, street_median):
    \"\"\"(verdict, rule) for one station's frame.\"\"\"
    p50, near, mean = shot["p50"], shot["near_clipped_pct"], shot["mean"]""",
     """def openings(walk, dc):
    \"\"\"One station an opening's landing: ``([{name, building, node, kind, story, spec}], note)``, the eye where a
    player stands to use the opening, looking down at where it lands -- in the site frame. ``note`` says why there
    are none when there are none for a reason (no buildings.json, a Deli Counter without `opening_landings`).\"\"\"
    path = os.path.join(walk, "buildings.json")
    if not os.path.isfile(path):
        return [], "no buildings.json in the walk copy: openings not judged"
    if dc not in sys.path:
        sys.path.insert(0, dc)
    try:
        import axonometric
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
            if g["kind"] == "stair":
                for st in getattr(spec, "stairs", []) or []:
                    ends = stairwell.stair_endpoints(st)
                    low = [x for x in ends if x["end"] == "lower"]
                    up = [x for x in ends if x["end"] == "upper"]
                    if low and up and min(st.from_story, st.to_story) == s \\
                            and abs(low[0]["point"][0] - lx) < 0.01 and abs(low[0]["point"][1] - ly) < 0.01:
                        top = max(st.from_story, st.to_story)
                        eye = (up[0]["point"][0], up[0]["point"][1], top * sh + EYE)
                        break
            elif g["kind"] == "hole":
                for r, kind in holes.get(s + 1, []):
                    if kind != "stair" and r[0] <= lx <= r[2] and r[1] <= ly <= r[3]:
                        # past the edge nearest the building's middle, on the storey above
                        sides = [(r[0] - OPENING_STAND_OFF_HOLE, ly), (r[2] + OPENING_STAND_OFF_HOLE, ly),
                                 (lx, r[1] - OPENING_STAND_OFF_HOLE), (lx, r[3] + OPENING_STAND_OFF_HOLE)]
                        ex, ey = min(sides, key=lambda p: (p[0] - bx) ** 2 + (p[1] - by) ** 2)
                        eye = (ex, ey, (s + 1) * sh + EYE)
                        break
            elif g["kind"] == "ladder":
                for ld in getattr(spec, "ladders", []) or []:
                    if abs(ld.x - lx) < 0.01 and abs(ld.y - ly) < 0.01:
                        top = max(ld.from_story, ld.to_story)
                        d = OPENING_STAND_OFF_LADDER
                        dx, dy = (-1.0 if lx > bx else 1.0), (-1.0 if ly > by else 1.0)
                        eye = (lx + dx * d * 0.7071, ly + dy * d * 0.7071, top * sh + EYE)
                        break
            if eye is None:
                continue
            place = places[node]
            e3, t3 = to_site(place, eye), to_site(place, (lx, ly, s * sh + OPENING_LOOK_Z))
            out.append({"name": "%s__open_%s_%d" % (e.get("id", spec_name), g["kind"], k), "building": e.get("id"),
                        "node": node, "kind": g["kind"], "story": s,
                        "spec": ",".join("%.3f" % c for c in e3 + t3)})
    return out, None


def judge(region, kind, shot, day, street_median):
    \"\"\"(verdict, rule) for one station's frame.\"\"\"
    p50, near, mean = shot["p50"], shot["near_clipped_pct"], shot["mean"]
    if region == "opening":
        if p50 < OPENING_FLOOR:
            return "FAIL", "p50 %d under the OPENING floor %d: what it leads to does not read" % (p50, OPENING_FLOOR)
        return "PASS", "p50 %d at or over %d" % (p50, OPENING_FLOOR)"""),
    ("""    rs, skipped, den_buildings = rooms(a.project, a.dc)
    stations = ["%s:%s" % (r["name"], r["spec"]) for r in rs]
    by_name = {r["name"]: r for r in rs}""",
     """    rs, skipped, den_buildings = rooms(a.project, a.dc)
    ops, ops_note = openings(a.project, a.dc)
    stations = ["%s:%s" % (r["name"], r["spec"]) for r in rs] + ["%s:%s" % (o["name"], o["spec"]) for o in ops]
    by_name = {r["name"]: r for r in rs}
    by_name.update({o["name"]: dict(o, region="opening") for o in ops})"""),
    ("""    lines = ["light check: %s" % os.path.abspath(a.project),
             "own preset %s; %d rooms; dens of sin: %s; no room list (not judged): %s"
             % (own, len(rs), ", ".join(den_buildings) or "none", ", ".join(skipped) or "none")]""",
     """    lines = ["light check: %s" % os.path.abspath(a.project),
             "own preset %s; %d rooms; dens of sin: %s; no room list (not judged): %s"
             % (own, len(rs), ", ".join(den_buildings) or "none", ", ".join(skipped) or "none"),
             "openings: %d station(s)%s" % (len(ops), "; " + ops_note if ops_note else "")]
    report["openings"] = len(ops)
    report["openings_note"] = ops_note"""),
    ("""            if name in by_name:
                region, kind = "interior", by_name[name]["kind"]""",
     """            if name in by_name:
                # a room's station is interior; an opening's carries its own region, held to its own floor
                region, kind = by_name[name].get("region", "interior"), by_name[name]["kind"]"""),
    ("""        order = {"interior": 0, "street": 1, "facade": 2, "context": 3}""",
     """        order = {"interior": 0, "opening": 1, "street": 2, "facade": 3, "context": 4}"""),
]


def main():
    raw = LC.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if "def openings(walk, dc)" in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    for old, new in EDITS:
        if text.count(old) != 1:
            raise SystemExit("REFUSED: an anchor in tools/light_check.py is there %d times; nothing written"
                             % text.count(old))
        text = text.replace(old, new)
    compile(text, str(LC), "exec")
    if TEST.exists():
        raise SystemExit("REFUSED: tools/test_light_check_openings.py exists; nothing written")
    src = pathlib.Path(__file__).resolve().parent / "light_check_openings" / "test_light_check_openings.py"
    LC.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    TEST.write_bytes(src.read_bytes())
    print("tools/light_check.py looks down every opening; tools/test_light_check_openings.py written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
