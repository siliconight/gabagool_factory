"""Shoot the vertical slice (docs/vertical_slice/, Delco Ave) from look_shots' derived cameras -- the site's own
stations, nothing typed in -- plus interiors, in the level's light and under the studio inspection light. Prints each
shot's mean and median brightness; the frames are the evidence.

    python docs/findings/slice_look/shoot.py <workspace> <tag>

Writes _scratch/slice_frames/<tag>_level/ and <tag>_inspect/ (raw frames are scratch; the sheets are kept here).
"""
import sys

sys.path.insert(0, "tools")
import look_shots  # noqa: E402

ws, tag = sys.argv[1], sys.argv[2]
walk = ws + "/.level_factory/preview/delco_ave_slice_001_walk"
for light, extra in (("level", {}), ("inspect", {"inspect": "studio"})):
    got = look_shots.shoot(walk, "_scratch/slice_frames/%s_%s" % (tag, light), interiors=6, timeout=1200,
                           **extra)
    for s in got.get("shots", []):
        print(tag, light, s["name"], round(s["mean"], 1), s["p50"])
