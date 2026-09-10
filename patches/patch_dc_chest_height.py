"""Give the aim point a body to belong to (roadmap 131's residue).

`sightlines.aim_height_m` was settable and not derived: 1.0 m is where a
1.8 m body's chest is, and no field said so. A studio stating a 2.05 m
character got an eye that followed and an aim point that did not.

Adds `characters.player.chest_height_m` beside the eye, and repoints the
sightline block's prose at it. The value does not move -- 1.0 stays 1.0 --
so nothing measured changes; what changes is that it now follows a body.

Asserts its anchors and refuses to write on a miss. The file is LF on disk
(deli_counter has core.autocrlf=input, so git stores and checks out LF).

    before  8319 bytes
    after   9464 bytes
"""
import io
import json
import os
import sys

PATH = os.path.join("deli_counter", "agent_contract.json")

#: `characters.player` sits two levels deep, so six spaces and not four. The
#: sightline block below is top-level and takes four.
EYE_ANCHOR = '      "eye_height_m": 1.6,\n      "crouch_height_m": 1.2,\n'
EYE_BLOCK = (
    '      "eye_height_m": 1.6,\n'
    '      "chest_height_m": 1.0,\n'
    '      "chest_note": "WHERE A SHOT IS AIMED, and the other half of the '
    'geometry that decides how tall cover must be. Derived: the centre of '
    'mass of a standing adult sits at about 0.55 of stature, so 0.55 * 1.8 = '
    '0.99, ratified at 1.0. THE HARD CONSTRAINT IS NOT ANTHROPOMETRY THOUGH, '
    'it is that the aim point must lie inside the target\'s own collider -- '
    'a line-of-sight ray is cast AT this height and LOS is granted only if it '
    'hits the target body first, so an aim point above the capsule misses and '
    'every sightline on the map reads blocked. Safe band for a capsule of '
    'radius R and height H is R <= chest <= H - R (0.35 to 1.45 here); '
    'outside the cylindrical section the ray grazes a hemisphere, and at the '
    'apex it misses. A 1.0 m character aimed at a fixed 1.0 m is aimed at the '
    'top of its own head.",\n'
    '      "crouch_height_m": 1.2,\n'
)

AIM_ANCHOR = '    "aim_height_m": 1.0,\n'
AIM_BLOCK = (
    '    "aim_height_m": 1.0,\n'
    '    "aim_height_is": "characters.player.chest_height_m. Carried here as '
    'well because this block is read as a unit -- the crossing height below '
    'needs all three numbers in one place -- but the body is where it is '
    'decided, and agent_contract.chest_height() reads the body and checks it '
    'against that body\'s capsule.",\n'
)


def main():
    with io.open(PATH, "r", encoding="utf-8", newline="") as f:
        text = f.read()
    before = len(text.encode("utf-8"))
    if '"chest_height_m"' in text:
        print("already present; nothing to do")
        return 0
    for anchor in (EYE_ANCHOR, AIM_ANCHOR):
        if text.count(anchor) != 1:
            print("ANCHOR MISS (%d occurrences): %r"
                  % (text.count(anchor), anchor[:40]), file=sys.stderr)
            return 1
    out = text.replace(EYE_ANCHOR, EYE_BLOCK).replace(AIM_ANCHOR, AIM_BLOCK)
    data = json.loads(out)                       # refuse to write invalid JSON

    # The constraint the note describes, checked here rather than trusted.
    player = data["characters"]["player"]
    chest = float(player["chest_height_m"])
    radius = float(player["radius_m"])
    height = float(player["height_m"])
    if not (radius <= chest <= height - radius):
        print("chest_height_m %.3f is outside the capsule's cylindrical "
              "section (%.3f to %.3f) -- refusing to write"
              % (chest, radius, height - radius), file=sys.stderr)
        return 1
    if abs(chest - float(data["sightlines"]["aim_height_m"])) > 1e-9:
        print("chest_height_m and sightlines.aim_height_m disagree -- "
              "refusing to write", file=sys.stderr)
        return 1

    with io.open(PATH, "w", encoding="utf-8", newline="") as f:
        f.write(out)
    after = len(out.encode("utf-8"))
    print("wrote %s: %d -> %d bytes (+%d)" % (PATH, before, after, after - before))
    return 0


if __name__ == "__main__":
    sys.exit(main())
