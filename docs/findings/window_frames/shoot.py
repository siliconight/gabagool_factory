"""Shoot seed 9082's bank before (Zoo 1.144.0, a window is a hole and a pane) and after (the clone with framed,
silled windows), at the same stations, in the level's light and under the studio inspection light. Prints each
shot's mean and median brightness; the frames are the evidence.

    python docs/findings/window_frames/shoot.py
"""
import sys

sys.path.insert(0, "tools")
import look_shots  # noqa: E402

# bank_branch_a02 is building b0 at Godot (-60, 0, 6.97), unrotated (docs/findings/bank_interior/). Its upper
# windows (window_delco_1997_01_w160_iplaster) stand at local (+-7.5, 5.246, +-11), so the south pair at world
# (-67.5, 5.25, 17.97) and (-52.5, 5.25, 17.97). The ground floor's glazing is a glass wall, unchanged.
ST = ["bank_front:-60.0,1.7,36.0,-60.0,3.5,8.0",
      "window_oblique:-62.0,4.0,23.0,-67.5,5.0,18.0",
      "window_near:-55.0,5.2,21.5,-52.5,5.0,18.0",
      "window_low:-50.0,1.7,24.0,-52.5,5.0,18.0"]
ARMS = (("before", "workspaces/linear-9082-ws"), ("after", "workspaces/frame-9082-ws"))
for arm, ws in ARMS:
    walk = ws + "/.level_factory/preview/bank_block_001_walk"
    for tag, extra in (("level", {}), ("inspect", {"inspect": "studio"})):
        got = look_shots.shoot(walk, "docs/findings/window_frames/frames/%s_%s" % (arm, tag), stations=ST,
                               timeout=900, **extra)
        for s in got.get("shots", []):
            if s["name"] in [x.split(":")[0] for x in ST]:
                print(arm, tag, s["name"], round(s["mean"], 1), s["p50"])
