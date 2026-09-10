"""Add the `sightlines` block to deli_counter/agent_contract.json.

Records the height at which a solid stops BOTH sides of a firefight seeing
each other, derived rather than chosen, plus the four disagreeing sight
heights it was derived from.

Asserts its anchor and refuses to write on a miss. CRLF preserved; the file
is 2-space-indented CRLF JSON and stays that way.

    before  5720 bytes (CRLF working tree)
    after   8148 bytes (CRLF) == 8088 with LF endings

deli_counter has core.autocrlf=input, so git stores LF and does not
convert back on checkout: the file this ran against happened to be
CRLF on disk and normalised to LF the next time git touched it. Both
figures are recorded because a reconstruction that measures the wrong
one is short by exactly the line count, which reads as corruption.
"""
import io
import json
import os
import sys

PATH = os.path.join("deli_counter", "agent_contract.json")
ANCHOR = 'themselves."\r\n  },\r\n  "qa": {'

BLOCK = (
    'themselves."\r\n  },\r\n'
    '  "sightlines": {\r\n'
    '    "crew_sight_height_m": 1.4,\r\n'
    '    "enemy_sight_height_m": 1.5,\r\n'
    '    "aim_height_m": 1.0,\r\n'
    '    "cover_break_height_m": 1.2222,\r\n'
    '    "derivation": "A sightline is TWO lines, not one: each side sights '
    'from its own eye at the other\'s chest, so one descends while the other '
    'climbs and a solid tall enough to break one can sit under the other. '
    'Half a broken sightline is not half a fix -- either side seeing the '
    'other is a shot, and the clock starts on the first shot by EITHER side. '
    'The shortest solid that breaks both is where the two lines cross: with '
    'sight heights a and b and a shared aim height c, '
    'h = a - (a - c)^2 / (a + b - 2c) = 1.4 - 0.16 / 0.9 = 1.2222. When both '
    'sides sight from the same height this reduces to (a + c) / 2, which is '
    'what lot/site_cover.MIN_COVER_HEIGHT derives (1.2) from the crew\'s '
    'numbers alone. BELOW THIS HEIGHT A SOLID IS SCENERY, NOT COVER: one '
    'side keeps a free shot and nothing about the engagement changed.",\r\n'
    '    "measured_from": "Laser Tag 0.19.0, read 2026-09-10. Crew: '
    'LT_BotPlayerController._find_visible_enemy casts from '
    'body.global_position + UP * 1.4. Enemy: LT_EnemyPill.tscn Marker3D_Eye '
    'at y = 1.5, handed to LT_LineOfSightTester as the ray origin. Aim: '
    'LT_LineOfSightTester.CHEST_OFFSET = UP * 1.0, used by both sides.",\r\n'
    '    "unreconciled": "FOUR heights describe one firefight and no two of '
    'them agree. characters.player.eye_height_m is 1.6 and '
    'LT_PlayerPill.tscn puts the Camera3D there, so the crew SHOOTS from '
    '1.55 (Marker3D_Muzzle, camera - 0.05) and decides what it can SEE from '
    '1.4 -- a body whose own muzzle sits 0.15 m above its visibility probe. '
    'The enemy sees from 1.5 and shoots from 1.3. Which of these moves is '
    'Laser Tag\'s call and not this file\'s; it is recorded here because a '
    'cover height derived from one of them is derived from a quarter of the '
    'geometry. Level Factory\'s packages.validation.lasertag_contract carries '
    'the engagement RANGES and does not read these at all, so the drift '
    'check lot/site_cover.py names in its own docstring does not cover the '
    'two constants that docstring is about.",\r\n'
    '    "re_derive_when": "any of the four heights above moves, or a '
    'controller learns to crouch. Nothing in this toolchain crouches -- '
    'characters.player.crouch_height_m has no consumer in Laser Tag or Lot '
    '-- so a solid below this height is life rather than shelter, and that '
    'is a statement about the evaluator, not about the shipped game."\r\n'
    '  },\r\n'
    '  "qa": {'
)


def main():
    with io.open(PATH, "r", encoding="utf-8", newline="") as f:
        text = f.read()
    before = len(text.encode("utf-8"))
    if '"sightlines"' in text:
        print("already present; nothing to do")
        return 0
    hits = text.count(ANCHOR)
    if hits != 1:
        print("ANCHOR MISS (%d occurrences) -- refusing to write" % hits,
              file=sys.stderr)
        return 1
    out = text.replace(ANCHOR, BLOCK)
    json.loads(out)                     # refuse to write invalid JSON
    with io.open(PATH, "w", encoding="utf-8", newline="") as f:
        f.write(out)
    after = len(out.encode("utf-8"))
    print("wrote %s: %d -> %d bytes (+%d)" % (PATH, before, after,
                                              after - before))
    return 0


if __name__ == "__main__":
    sys.exit(main())
