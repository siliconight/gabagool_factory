"""Lux 0.68.0's release: VERSION and the CHANGELOG entry.

    python patch_lux_0680_release.py

Anchored on VERSION (b'Lux 0.67.0', no newline) and on CHANGELOG.md's head,
as Lux 0.67.0 left them (LF).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LUX = ROOT / "lux"

HEAD = "# Changelog\n\n## [0.67.0]"
ENTRY = """# Changelog

## [0.68.0] - the rooms' floor, put back in the bake

THE BAKE TOOK IT AWAY. Lux 0.38.0 gave every room a ReflectionProbe whose
flat ambient (`ROOM_AMBIENT_DERIVED_ENERGY`, 0.04) is "a floor under the
fixtures so an unlit corner is dark grey rather than a hole". A lightmapped
surface takes its light from the lightmap alone, so once Level Factory baked
(0.131.0, on by default since 0.144.0) that floor reached no wall and no
floor. Raised five-fold on all 24 probes of cold run 9190's baked level, it
moved no surface: the customer floor 12.7 -> 13.1, every other room within
0.1. The bake is baked with the environment off, which is right for a sealed
room and leaves it nothing. Measured against the same level lit live
(`docs/findings/night_interiors/` at the factory root), mean luma of 255:

    rooms                  baked    live
    16 fluorescent rows     15.5    24.3
     8 bulb-lit rooms        3.8    17.5

`LuxLightLoader.add_bake_fills(scene_root, energy = -1)` puts the floor back
as light that exists only while the lightmapper runs. It lays static omnis
over every UNTINTED room probe: a tinted probe is a club room, dark by
design, the walker's dens of sin. The rules:
- one fill per `BAKE_FILL_CELL_M` (6 m) cell, at `BAKE_FILL_HEIGHT_M`
  (1.7 m) over the room's floor, in the probe's own frame, so a turned
  building's fills stand in its rooms;
- each at the preset's `bake_room_fill` (0.025), reaching
  `BAKE_FILL_REACH_CELLS` (1.5) cells, flat inside it;
- a room a Bare Bulb rig hangs in takes `BAKE_FILL_BULB_SHARE` (0.5),
  "keep pendants moody".

The container has no owner, so a save that forgot to free it cannot keep it.
A bake lays it before it bakes and frees it before it saves. Level Factory
0.151.0's bake does. A level carries no fill at runtime.

FOUR LAYOUTS, BAKED ON THAT LEVEL with the bulbs clear (0.67.0) and Level
Factory's own bake. The first three are refuted and kept in the loader:

    fluorescent / bulb-lit rooms, bake time in the editor
    no floor                                       15.7   9.6    85 s
    1 fill a room, centre, 2.3 m, 0.08             32.9  19.4    86 s
    6 m cells, 1.7 m, 0.08 a room split            32.0  28.1   172 s
    8 m cells, as above, bulb rooms half           32.0  18.7   132 s
    6 m cells, 1.7 m, 0.025 each, 9 m, half        39.1  22.8    94 s

- **The centre fill** hung at 2.3 m, where a bare bulb hangs, in the room's
  centre, where a row's middle bulb hangs. deli_a01's deli counter fill
  stood on its centre bulb's anchor, inside the glass, and four rooms did not
  move.
- **A room's energy split between its cells** left a big room dark. A floor
  point is lit by the fills near it, so the split falls as 1/size.
- **A fixed energy a fill with a local reach** lights a floor the same
  whatever the room's size.

The exterior barely moves: the overview is unchanged, the elevations move
+0 to +5.6, and the difference image is all interior.

NOT PRICED, AND WHY: nothing ships. The fills are in the lightmap, which keeps
its size, and gone from the scene, so draws, lights and frame time are the
unfilled level's by construction. The bake costs about 9 s more in the editor.
The energy was chosen by eye from the frames, not derived. The level's
darkest fluorescent rooms are the office lobby (13.4) and the rail concourse
(16.5). In the lobby the fill lifted the ceiling 16 codes and the dark red
carpet 2.4, so what is left there is the carpet's albedo, not light.

`tools/bake_fill_selftest.gd` (headless, 26 checks) holds the rules above, the
club room's exemption, the turned room, the replace-not-add, the unowned
container and the preset's dial. On 0.67.0 it fails 6. Per time of day is
next: a level is set at one of five times (the walker, 2026-10-07), and its
preset is where each one's floor and window light belong.

## [0.67.0]"""


def main():
    v = (LUX / "VERSION").read_bytes()
    assert v == b"Lux 0.67.0", repr(v)
    c = (LUX / "CHANGELOG.md").read_bytes()
    assert b"\r\n" not in c
    text = c.decode("utf-8")
    assert text.count(HEAD) == 1, text.count(HEAD)
    (LUX / "VERSION").write_bytes(b"Lux 0.68.0")
    (LUX / "CHANGELOG.md").write_bytes(text.replace(HEAD, ENTRY, 1).encode("utf-8"))
    print("Lux 0.68.0: VERSION and CHANGELOG written")


if __name__ == "__main__":
    main()
