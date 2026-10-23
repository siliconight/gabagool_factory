"""The light check judges an opening by what is seen through its rim, not by its frame (the walker's walk of cold run
9383, finding 1). `tools/light_check.py` held an opening's station to the whole frame's p50, and a frame looking down
an opening is mostly the floor round it: on cold run 9384 it PASSED deli_a03's ground-floor ladder hole at p50 42
while the hole itself was black -- luma p50 0, p95 12 through its rim, Level Factory 0.211.0's backdrop ground lying
across it -- and FAILED the broken-floor hole (frame p50 9, through its rim p95 158) and the roof hatch (frame p50 0,
the lit landing at the shaft's foot, through-p95 129), where what each leads to reads
(`docs/findings/walk_2026-10-23_deli/`, `through_9383.out.txt` and `through_9384.out.txt`).

Each opening station now carries its rim -- the slab cut it is looked down through, in the site frame -- and the check
projects it into the frame the way Godot's default camera draws it (75 degrees vertical, `look_at` with Y up:
look_shots never sets a field of view) and reads Rec.709 luma inside it from the shot's PNG. Held to p95 through the
rim >= OPENING_FLOOR (20), PROVISIONAL: the brightest twentieth, the facade rule's statistic; lidded, the ladder hole
read 12 and 9, and every opening whose landing reads, 40 or more. A rim the camera cannot see is REPORTED, not judged.
Anchored; refuses on a miss; a second run refuses.

    python patches/patch_light_check_through_rim.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LC = ROOT / "tools" / "light_check.py"
TEST = ROOT / "tools" / "test_light_check_openings.py"

EDITS = [
    # the target table's row
    ("""| opening | any | p50 >= 20, PROVISIONAL | the walker, 2026-10-23: "you should be able to see into holes to know you can go forward into them" -- a stair opening onto deli_a03's basement read black from above at the landing's own p50 10, so twice the ROW floor |""",
     """| opening | any | p95 THROUGH ITS RIM >= 20, PROVISIONAL | the walker, 2026-10-23: "you should be able to see into holes to know you can go forward into them" -- a stair opening onto deli_a03's basement read black from above at the landing's own p50 10, so twice the ROW floor; the pixels inside the opening's rim, not the frame (`through_rim`) |"""),
    ("""OPENING_LOOK_Z = 0.2
""",
     """OPENING_LOOK_Z = 0.2
#: AN OPENING IS JUDGED THROUGH ITS RIM (2026-10-23). A frame looking down an opening is mostly the floor round it,
#: and its p50 is that floor's: on cold run 9384 it passed a ladder hole black inside its rim at 42 and failed a
#: broken-floor hole that showed a lit kitchen. The brightest twentieth through the rim, the facade rule's statistic:
#: measured, a lidded hole 12 and 9, every opening whose landing reads 40 or over
#: (`docs/findings/walk_2026-10-23_deli/through_*.out.txt`).
OPENING_THROUGH_PCT = 95
#: The camera look_shots draws with: Godot's Camera3D default, 75 degrees vertical (it never sets `fov`), aimed by
#: `look_at(target, Vector3.UP)`.
CAMERA_FOV_V = 75.0
"""),
    ("""    try:
        import axonometric
        import lights
        import spec_loader
        import stairwell
    except ImportError as e:""",
     """    try:
        import axonometric
        import ladder_geom
        import lights
        import spec_loader
        import stairwell
    except ImportError as e:"""),
    ("""            s, lx, ly = g["story"], g["x"], g["y"]
            eye = None
""",
     """            s, lx, ly = g["story"], g["x"], g["y"]
            eye = None
            rim = None   # the slab cut the opening is looked down through: (x0, y0, x1, y1), the slab's top
"""),
    ("""                        top = max(st.from_story, st.to_story)
                        eye = (up[0]["point"][0], up[0]["point"][1], top * sh + EYE)
                        break""",
     """                        top = max(st.from_story, st.to_story)
                        eye = (up[0]["point"][0], up[0]["point"][1], top * sh + EYE)
                        rim = (stairwell.footprint_rect(st), top * sh)
                        break"""),
    ("""                        eye = (ex, ey, (s + 1) * sh + EYE)
                        break""",
     """                        eye = (ex, ey, (s + 1) * sh + EYE)
                        rim = (r, (s + 1) * sh)
                        break"""),
    ("""                        eye = (lx + dx * d * 0.7071, ly + dy * d * 0.7071, top * sh + EYE)
                        break""",
     """                        eye = (lx + dx * d * 0.7071, ly + dy * d * 0.7071, top * sh + EYE)
                        hx, hy, hsx, hsy = ladder_geom.through_hole(ld.x, ld.y, ld.width, ld.facing)
                        rim = ((hx - hsx / 2.0, hy - hsy / 2.0, hx + hsx / 2.0, hy + hsy / 2.0), top * sh)
                        break"""),
    ("""            out.append({"name": "%s__open_%s_%d" % (e.get("id", spec_name), g["kind"], k), "building": e.get("id"),
                        "node": node, "kind": g["kind"], "story": s,
                        "spec": ",".join("%.3f" % c for c in e3 + t3)})
    return out, None
""",
     """            (rx0, ry0, rx1, ry1), rz = rim
            out.append({"name": "%s__open_%s_%d" % (e.get("id", spec_name), g["kind"], k), "building": e.get("id"),
                        "node": node, "kind": g["kind"], "story": s,
                        "spec": ",".join("%.3f" % c for c in e3 + t3),
                        "rim": [list(to_site(place, (x, y, rz))) for x, y in
                                ((rx0, ry0), (rx1, ry0), (rx1, ry1), (rx0, ry1))]})
    return out, None


def project(eye, target, pts, width, height, fov_v=CAMERA_FOV_V):
    \"\"\"Site points -> frame pixels ``[(u, v)]`` for a camera at `eye` aimed at `target` with Y up, as Godot's
    `look_at` aims it and its perspective projection draws it (keep-height, `fov_v` degrees vertical); None when a
    point is behind the camera.\"\"\"
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
    \"\"\"Luma 0-255 of the frame's pixels inside an opening's rim: ``{p50, p95, mean, frame_pct, pixels}``, or None
    when the shot has no PNG, the rim is behind the camera or covers no pixel. Rec.709, as look_shots measures.\"\"\"
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
"""),
    ("""    if region == "opening":
        if p50 < OPENING_FLOOR:
            return "FAIL", "p50 %d under the OPENING floor %d: what it leads to does not read" % (p50, OPENING_FLOOR)
        return "PASS", "p50 %d at or over %d" % (p50, OPENING_FLOOR)""",
     """    if region == "opening":
        # through its rim (`through_rim`), not the frame: the frame is mostly the floor round the opening
        th = shot.get("through")
        if not th:
            return "REPORT", "the rim is not in the frame: not judged (frame p50 %d)" % p50
        if th["p95"] < OPENING_FLOOR:
            return "FAIL", "through its rim p95 %d under the OPENING floor %d: what it leads to does not read" % (
                th["p95"], OPENING_FLOOR)
        return "PASS", "through its rim p95 %d at or over %d" % (th["p95"], OPENING_FLOOR)"""),
    ("""            verdict, rule = judge(region, kind, shot, day, street_median)""",
     """            if region == "opening":
                shot = dict(shot, through=through_rim(shot, by_name[name].get("rim")))
            verdict, rule = judge(region, kind, shot, day, street_median)"""),
    ("""                         "crushed_pct": round(shot["crushed_pct"], 1), "png": shot.get("png")})""",
     """                         "crushed_pct": round(shot["crushed_pct"], 1), "png": shot.get("png"),
                         "through": shot.get("through")})"""),
]

TEST_EDITS = [
    ("""    def test_an_opening_is_judged_by_its_own_floor(self):
        dark = {"p50": 10, "near_clipped_pct": 0.0, "mean": 12.0, "p95": 30}
        lit = dict(dark, p50=light_check.OPENING_FLOOR)
        self.assertEqual(light_check.judge("opening", "stair", dark, False, None)[0], "FAIL")
        self.assertEqual(light_check.judge("opening", "stair", lit, False, None)[0], "PASS")
        # the room the walker looked into passed as a room at the same p50: the reason this region exists
        self.assertEqual(light_check.judge("interior", "MOODY", dark, False, None)[0], "PASS")
""",
     """    def test_an_opening_is_judged_through_its_rim_not_by_its_frame(self):
        \"\"\"Cold run 9384: deli_a03's ground-floor ladder hole, black inside its rim, in a frame of lit floor at p50
        42; its broken-floor hole showing a lit kitchen in a frame at p50 9. The frame's p50 passed the first and
        failed the second; the rim's p95 does the reverse.\"\"\"
        lidded = {"p50": 42, "near_clipped_pct": 0.0, "mean": 45.3, "through": {"p50": 0.0, "p95": 12.0}}
        kitchen = {"p50": 9, "near_clipped_pct": 0.0, "mean": 24.7, "through": {"p50": 87.0, "p95": 158.2}}
        self.assertEqual(light_check.judge("opening", "ladder", lidded, False, None)[0], "FAIL")
        self.assertEqual(light_check.judge("opening", "hole", kitchen, False, None)[0], "PASS")
        self.assertEqual(light_check.judge("opening", "hole", dict(kitchen, through=None), False, None)[0], "REPORT")
        # the room the walker looked into passed as a room at a p50 of 10: the reason this region exists
        self.assertEqual(light_check.judge("interior", "MOODY", dict(lidded, p50=10), False, None)[0], "PASS")

    def test_every_opening_station_carries_its_rim_round_its_landing(self):
        ops, _note = light_check.openings(str(self.walk), str(DC))
        self.assertTrue(ops)
        for o in ops:
            rim = o["rim"]
            self.assertEqual(len(rim), 4, o["name"])
            ex, ey, ez, tx, ty, tz = (float(v) for v in o["spec"].split(","))
            xs, zs = [p[0] for p in rim], [p[2] for p in rim]
            self.assertTrue(min(xs) <= tx <= max(xs) and min(zs) <= tz <= max(zs) or o["kind"] == "stair",
                            (o["name"], rim, (tx, tz)))
            self.assertTrue(ty < rim[0][1] <= ey, (o["name"], "the rim is between the eye and the landing"))

    def test_the_rim_is_measured_where_godot_draws_it(self):
        \"\"\"A frame drawn by hand: grey floor, and a black square exactly where `project` puts a rim the camera
        looks straight into. Inside it reads black and the frame reads grey -- and a rim one metre aside does not.\"\"\"
        from PIL import Image, ImageDraw
        eye, target = [0.3, 4.0, 0.2], [0.0, 0.0, 0.0]
        rim = [[-0.5, 0.0, -0.5], [0.5, 0.0, -0.5], [0.5, 0.0, 0.5], [-0.5, 0.0, 0.5]]
        uv = light_check.project(eye, target, rim, 320, 180)
        img = Image.new("RGB", (320, 180), (120, 120, 120))
        ImageDraw.Draw(img).polygon(uv, fill=(0, 0, 0))
        png = os.path.join(str(self.walk), "frame.png")
        img.save(png)
        shot = {"png": png, "eye": eye, "target": target}
        th = light_check.through_rim(shot, rim)
        self.assertLess(th["p95"], 5)
        aside = [[x + 1.0, y, z] for x, y, z in rim]
        self.assertGreater(light_check.through_rim(shot, aside)["p50"], 100)
        self.assertIsNone(light_check.project(eye, target, [[0.0, 9.0, 0.0]], 320, 180))
"""),
]


def apply(path, edits):
    raw = path.read_bytes()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in edits:
        if text.count(old) != 1:
            raise SystemExit("REFUSED: %s: an anchor is there %d times; nothing written: %r"
                             % (path.name, text.count(old), old[:80]))
        text = text.replace(old, new)
    return (text.replace("\n", "\r\n") if crlf else text).encode("utf-8")


def main():
    if "def through_rim" in LC.read_text(encoding="utf-8"):
        raise SystemExit("REFUSED: already applied; nothing written")
    out = {LC: apply(LC, EDITS), TEST: apply(TEST, TEST_EDITS)}
    for p, b in out.items():
        p.write_bytes(b)
    print("tools/light_check.py judges an opening through its rim; its test, three cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
