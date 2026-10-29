"""Shoot the vertical slice from the street, where a player stands: two views down the avenue and a front and an
oblique of each building, in the level's light and under the studio inspection light. Prints each shot's mean and
median brightness; the frames are the evidence.

    python docs/findings/slice_look/shoot_street.py <workspace> <tag>

Stations are given, not derived, from slice 1's picked candidate (seed 9104): its site.markings.json puts the
avenue along X at spec y -30.565 -- Godot z +30.6 (Godot z = -spec y), 10 m wide with a 3 m sidewalk -- and the
frontages of the bank (b1, x -30..0), the card shop (b2, x 15..35) and the train yard (b3, x 66..118) at Godot z
20.4..22.6, facing it; the gas station (b0) stands at x -86 with its forecourt to the avenue. The first version of
this file put every camera at z 0 -- behind the buildings -- and is RETRACTED: its frames were the backs. A later
slice that draws other buildings needs these re-derived.
"""
import sys

sys.path.insert(0, "tools")
import look_shots  # noqa: E402

ws, tag = sys.argv[1], sys.argv[2]
ST = ["ave_east:-120.0,1.7,30.6,60.0,4.0,30.6",
      "ave_west:110.0,1.7,30.6,-90.0,4.0,30.6",
      "sidewalk_east:-45.0,1.7,25.5,40.0,2.0,23.5",
      "gas_front:-86.0,1.7,33.0,-86.0,3.0,0.0",
      "gas_oblique:-60.0,1.7,33.0,-90.0,3.0,5.0",
      "bank_front:-15.0,1.7,31.0,-15.0,4.5,18.0",
      "bank_oblique:8.0,1.7,32.0,-18.0,5.0,18.0",
      "card_front:25.0,1.7,31.0,25.0,3.5,18.0",
      "yard_front:92.0,1.7,31.0,92.0,3.0,18.0"]
walk = ws + "/.level_factory/preview/delco_ave_slice_001_walk"
for light, extra in (("level", {}), ("inspect", {"inspect": "studio"})):
    got = look_shots.shoot(walk, "_scratch/slice_frames/%s_street_%s" % (tag, light), stations=ST,
                           timeout=1200, **extra)
    for s in got.get("shots", []):
        if s["name"] in [x.split(":")[0] for x in ST]:
            print(tag, light, s["name"], round(s["mean"], 1), s["p50"])
