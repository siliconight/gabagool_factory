"""Lux 0.67.0's release: VERSION and the CHANGELOG entry.

    python patch_lux_0670_release.py

Anchored on VERSION (b'Lux 0.66.0', no newline) and on CHANGELOG.md's head
(241,787 bytes, LF) as read 2026-10-07.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LUX = ROOT / "lux"

HEAD = "# Changelog\n\n## [0.66.0]"
ENTRY = """# Changelog

## [0.67.0] - a bare bulb's lamp hangs under its glass, not inside it

The walker, 2026-10-07: "a lot of our interiors are quite dark when the sun
isn't up". Measured on cold run 9190's restaurant row, one camera a room, 24
rooms (`docs/findings/night_interiors/` at the factory root): the baked level
against the same level lit live, mean luma of 255,

    rooms                 baked    live
    16 fluorescent rows    15.5    24.3
     8 bulb-lit rooms       3.8    17.5     (basements and objective rooms)

and the floor straight under the deli counter's centre bulb, 0.9 baked
against 40.4 live.

THE CAUSE IS THE POLE'S (0.65.0), ONE FIXTURE DOWN. A pendant's anchor is the
BULB point, and Zoo's `pendant_fixture` mounts 'above' it: an ellipsoid
centred one radius over the anchor and stretched 1.15x upright, so the glass
reaches 0.15 of a radius BELOW the anchor -- 6 to 12 mm across the genome's
0.08-0.16 m bulbs. The lamp hung AT the anchor (`mount_height = 0.0`), inside
closed glass. Real time draws an unshadowed lamp through it, so nothing
looked wrong until the light bake (Level Factory 0.131.0, on by default since
0.144.0) ray-traced every steady bulb to nothing. A counter accent wears the
same hardware and hung the same way.

A bulb's lamp and a counter accent's now hang `BULB_LAMP_DROP_M` (0.022 m)
under the anchor: the widest bulb's 0.012 m reach plus the centimetre the
pole's lamp keeps under its lens. Re-baked by Level Factory's own bake with
the 33 bulb lamps moved 0.020 m (the experiment's figure; the shipped 0.022
is derived, and both clear 0.012), against a plain re-bake as the control,
which reproduced the shipped level room for room:

    rooms                 control    bulbs clear
    8 bulb-lit rooms         3.8        9.6     (median room 3.0 -> 12.4)
      cold storage           0.8       15.1
      deli counter           6.6       12.4
    16 fluorescent rows     15.5       15.7     (all of it the customer
                                                 floor's counter accent)
    floor under the bulb     0.9       20.3     (live: 40.4)

The rest of the gap to live is not this release's: the room probes' ambient
floor (0.38.0) does not reach a lightmapped surface at all -- raising it
five-fold moved no wall -- and the lightmapper keeps about 0.8 of a lamp's
live luma even over a bare floor with nothing in the way.

NOT PRICED, AND WHY: no node, light, mesh or material is added; 33 lamps move
22 mm. What it invalidates: every bulb-lit room in every baked level since
Level Factory 0.144.0 was darker than its fixtures say, and any frame of one
judged the bulbs, not the bake.

`tools/bulb_lamp_selftest.gd` (headless, 9 checks) holds the pendant and the
counter accent under Zoo's widest bulb on the manifest path and through a
marker, with a fluorescent row and a wall pack as controls. On 0.66.0 it
fails 4. Not checked: the other lamps that hang AT their anchor -- a club's
neon, back bar and stage light, a canopy wash, a sign -- whose hardware is
built elsewhere.

## [0.66.0]"""


def main():
    v = (LUX / "VERSION").read_bytes()
    assert v == b"Lux 0.66.0", repr(v)
    c = (LUX / "CHANGELOG.md").read_bytes()
    assert b"\r\n" not in c
    text = c.decode("utf-8")
    assert text.count(HEAD) == 1, text.count(HEAD)
    (LUX / "VERSION").write_bytes(b"Lux 0.67.0")
    (LUX / "CHANGELOG.md").write_bytes(text.replace(HEAD, ENTRY, 1).encode("utf-8"))
    print("Lux 0.67.0: VERSION and CHANGELOG written")


if __name__ == "__main__":
    main()
