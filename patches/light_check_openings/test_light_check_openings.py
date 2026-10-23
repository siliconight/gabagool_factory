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

    def test_an_opening_is_judged_by_its_own_floor(self):
        dark = {"p50": 10, "near_clipped_pct": 0.0, "mean": 12.0, "p95": 30}
        lit = dict(dark, p50=light_check.OPENING_FLOOR)
        self.assertEqual(light_check.judge("opening", "stair", dark, False, None)[0], "FAIL")
        self.assertEqual(light_check.judge("opening", "stair", lit, False, None)[0], "PASS")
        # the room the walker looked into passed as a room at the same p50: the reason this region exists
        self.assertEqual(light_check.judge("interior", "MOODY", dark, False, None)[0], "PASS")

    def test_no_buildings_json_says_so(self):
        (self.walk / "buildings.json").unlink()
        ops, note = light_check.openings(str(self.walk), str(DC))
        self.assertEqual(ops, [])
        self.assertIn("buildings.json", note)


if __name__ == "__main__":
    unittest.main()
