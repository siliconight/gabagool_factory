"""Shoot seed 9082's bank before (Deli Counter 0.291.0, the parapet half a wall behind the facade) and after (the clone
with the parapet on the walls' outer faces), at the same stations, in the level's light and under the studio inspection light.
Prints each shot's mean and median brightness; the frames are the evidence.

    python docs/findings/parapet_flush/shoot.py
"""
import sys

sys.path.insert(0, "tools")
import look_shots  # noqa: E402

# bank_branch_a02 is building b0 at Godot (-60, 0, 6.97), unrotated (docs/findings/bank_interior/), a 30 x 22 m
# footprint: its parapet's outer faces at world x -75 and -45 and z -4.03 and 17.97, its top at y 8.3 and its roof
# at y 7.2 (slots.json: parapet tiles centred 7.75, 1.1 tall).
ST = ["bank_front:-60.0,1.7,36.0,-60.0,3.5,8.0",
      "roofline_far:-60.0,1.7,48.0,-60.0,8.0,18.0",
      "corner_low:-40.0,1.7,26.0,-45.0,8.3,18.0",
      "corner_oblique:-35.0,4.0,30.0,-45.0,8.3,18.0",
      "roof_along:-50.0,8.9,14.0,-70.0,8.3,17.9",
      "top_band:-58.0,1.7,25.0,-60.0,7.0,18.0"]
ARMS = (("before", "workspaces/coping-9082-ws"), ("after", "workspaces/flush2-9082-ws"))
for arm, ws in ARMS:
    walk = ws + "/.level_factory/preview/bank_block_001_walk"
    for tag, extra in (("level", {}), ("inspect", {"inspect": "studio"})):
        got = look_shots.shoot(walk, "docs/findings/parapet_flush/frames/%s_%s" % (arm, tag), stations=ST,
                               timeout=900, **extra)
        for s in got.get("shots", []):
            if s["name"] in [x.split(":")[0] for x in ST]:
                print(arm, tag, s["name"], round(s["mean"], 1), s["p50"])
