"""The light check looks down every opening, from where a player stands to use it.

    python test_light_check_openings.py            # standalone
    python -m pytest test_light_check_openings.py  # or collected

The walker, cold run 9383, of a stair opening onto deli_a03's basement: "this shouldn't look pitch black" -- "you
should be able to see into holes to know you can go forward into them". `light_check.py` had one station a room, the
eye inside it, and passed the basement's cold storage at p50 10 while the walker saw black from above
(`docs/findings/walk_2026-10-23_deli/`). `openings()` adds a station per opening's landing (Deli Counter's
`lights.opening_landings`). This builds a walk copy of one deli_a03 at the site's origin and reads the stations it
derives, against the real Deli Counter; `judge` holds them to the OPENING floor.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import light_check  # noqa: E402

DC = HERE.parent / "deli_counter"
SITE = """[gd_scene load_steps=2 format=3]

[ext_resource type="PackedScene" path="res://lot/deli_a03/site.tscn" id="b1"]

[node name="site" type="Node3D"]

[node name="b0" parent="." instance=ExtResource("b1")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0)
"""


class OpeningStations(unittest.TestCase):
    def setUp(self):
        self.walk = Path(tempfile.mkdtemp(prefix="lc_open_"))
        (self.walk / "site.tscn").write_text(SITE, encoding="utf-8")
        (self.walk / "buildings.json").write_text(json.dumps({"buildings": [
            {"node": "b0", "id": "deli_a03", "kind": "building", "spec": "deli_a03"}]}), encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.walk, ignore_errors=True)

    def test_every_opening_of_deli_a03_is_looked_down_into(self):
        sys.path.insert(0, str(DC))
        import lights
        import spec_loader
        if not hasattr(lights, "opening_landings"):
            self.skipTest("Deli Counter before 0.261.0")
        spec = spec_loader.load_spec(str(DC / "specs" / "deli_a03.json"))
        ops, note = light_check.openings(str(self.walk), str(DC))
        self.assertIsNone(note)
        self.assertEqual(len(ops), len(lights.opening_landings(spec)))
        # THE WALKER'S OPENING: the basement stair, from its upper end on the ground floor, down to its foot. Spec
        # (x, y, z) is the site's (x, z, -y) here: the building stands at the origin, unturned.
        down = [o for o in ops if o["kind"] == "stair" and o["story"] == -1]
        self.assertEqual(len(down), 1)
        ex, ey, ez, tx, ty, tz = (float(v) for v in down[0]["spec"].split(","))
        self.assertAlmostEqual(ey, 0 * 3.3 + light_check.EYE, places=3)          # y is up in the site
        self.assertAlmostEqual(ty, -3.3 + light_check.OPENING_LOOK_Z, places=3)
        self.assertAlmostEqual(tx, -15.8, places=3)
        self.assertAlmostEqual(-tz, 11.6, places=3)
        self.assertGreater(ey, ty, "the eye stands above what it looks at")

    def test_an_opening_is_judged_through_its_rim_not_by_its_frame(self):
        """Cold run 9384: deli_a03's ground-floor ladder hole, black inside its rim, in a frame of lit floor at p50
        42; its broken-floor hole showing a lit kitchen in a frame at p50 9. The frame's p50 passed the first and
        failed the second; the rim's p95 does the reverse."""
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
        """A frame drawn by hand: grey floor, and a black square exactly where `project` puts a rim the camera
        looks straight into. Inside it reads black and the frame reads grey -- and a rim one metre aside does not."""
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

    def test_no_buildings_json_says_so(self):
        (self.walk / "buildings.json").unlink()
        ops, note = light_check.openings(str(self.walk), str(DC))
        self.assertEqual(ops, [])
        self.assertIn("buildings.json", note)


if __name__ == "__main__":
    unittest.main()
