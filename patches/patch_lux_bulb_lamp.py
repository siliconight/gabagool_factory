"""Lux 0.67.0: a bare bulb's lamp hangs under its glass, not inside it.

    python patch_lux_bulb_lamp.py

Zoo's `pendant_fixture` reaches 0.15 of the bulb's radius BELOW its anchor,
and Lux hung the bulb's lamp AT the anchor (`mount_height = 0.0`), so every
steady bare bulb and counter accent sat inside closed glass. Real time draws
an unshadowed lamp through it; the lightmapper ray-traces, and each one
baked to nothing. `docs/findings/night_interiors/` has the measurements.

Anchored on `addons/lux/runtime/lux_light_loader.gd` as read 2026-10-07
(87,085 bytes, LF, 1,696 lines). Every anchor must match once; nothing is
written on a miss.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOADER = ROOT / "lux" / "addons" / "lux" / "runtime" / "lux_light_loader.gd"

CONST_OLD = "const FLUORESCENT_MOUNT := -0.25\n"
CONST_NEW = (
    "const FLUORESCENT_MOUNT := -0.25\n"
    "\n"
    "## A BARE BULB'S LAMP HANGS UNDER ITS GLASS (0.67.0). A pendant's anchor is\n"
    "## the BULB point, and Zoo's `pendant_fixture` mounts 'above' it: the bulb is\n"
    "## an ellipsoid whose centre sits one radius over the anchor, stretched 1.15x\n"
    "## upright, so its glass reaches 0.15 of a radius BELOW the anchor -- 6 to\n"
    "## 12 mm over the genome's 0.08-0.16 m bulbs. The lamp hung AT the anchor\n"
    "## sat inside that closed glass. Real time draws an unshadowed lamp straight\n"
    "## through it, so nobody saw; the lightmapper ray-traces, and every steady\n"
    "## bulb baked to nothing -- the pole's disease (0.65.0), one fixture down.\n"
    "## A counter accent wears the same hardware and had the same lamp.\n"
    "##\n"
    "## Measured on cold run 9190's restaurant row, re-baked by Level Factory's\n"
    "## own bake with only the 33 bulb lamps moved, one station a room\n"
    "## (`docs/findings/night_interiors/`): the eight bulb-lit rooms' mean luma\n"
    "## 3.8 -> 9.6 of 255, cold storage 0.8 -> 15.1, the deli counter room\n"
    "## 6.6 -> 12.4. The sixteen fluorescent rooms 15.5 -> 15.7, all of it the\n"
    "## customer floor (12.8 -> 15.1), whose register has the counter accent.\n"
    "##\n"
    "## DERIVED: the widest bulb's reach under its anchor, 0.15 x 0.08 = 0.012,\n"
    "## plus the centimetre the pole's lamp keeps under its lens\n"
    "## (`LuxStreetlightRig.POLE_LAMP_DROP_M`). Zoo owns the first number: a\n"
    "## wider bulb or a longer stretch moves it.\n"
    "const BULB_LAMP_DROP_M := 0.022\n"
)

PENDANT_OLD = ("\t\t\trb.mount_height = 0.0\n"
               "\t\t\t# steady (0.62.0): one bulb an anchor wavers, by the spawner's choice\n")
PENDANT_NEW = ("\t\t\t# under the glass, not inside it (0.67.0): see BULB_LAMP_DROP_M\n"
               "\t\t\trb.mount_height = -BULB_LAMP_DROP_M\n"
               "\t\t\t# steady (0.62.0): one bulb an anchor wavers, by the spawner's choice\n")

ACCENT_OLD = "\t\t\trca.mount_height = 0.0\n"
ACCENT_NEW = ("\t\t\t# the pendant's hardware, so the pendant's clearance (0.67.0)\n"
              "\t\t\trca.mount_height = -BULB_LAMP_DROP_M\n")


def main():
    data = LOADER.read_bytes()
    assert len(data) == 87085, "loader is %d bytes, read at 87,085" % len(data)
    assert b"\r\n" not in data, "loader has CRLF; it was LF"
    text = data.decode("utf-8")
    for old in (CONST_OLD, PENDANT_OLD, ACCENT_OLD):
        assert text.count(old) == 1, "anchor found %d times: %r" % (text.count(old), old[:60])
    text = text.replace(CONST_OLD, CONST_NEW).replace(PENDANT_OLD, PENDANT_NEW).replace(ACCENT_OLD, ACCENT_NEW)
    LOADER.write_bytes(text.encode("utf-8"))
    print("lux_light_loader.gd: %d -> %d bytes" % (len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
