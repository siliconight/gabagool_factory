"""Lux 0.68.1's test, written first: the fills are owned by the scene.

    python patch_lux_bake_fill_owned_tests.py

0.68.0's selftest held the opposite -- "the container has no owner, so a save
cannot keep it" -- and that was the defect. Godot's LightmapGI skips a child
with no owner when it collects lights ("maybe a helper"), so Level Factory
0.151.0's bake laid 267 unowned fills on cold run 9190's level and the
lightmap came out identical to the control's (16 fluorescent rooms 15.5, 8
bulb-lit 3.8). The check is replaced, and the refutation kept in its label.

Anchored on `lux/tools/bake_fill_selftest.gd` as 0.68.0 wrote it (7,653
bytes, LF). On 0.68.0 it must FAIL.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST = ROOT / "lux" / "tools" / "bake_fill_selftest.gd"

OLD = '\t_check("the container has no owner, so a save cannot keep it", fills.owner == null, true)\n'
NEW = ('\t# OWNED (0.68.1). 0.68.0 held the opposite -- "no owner, so a save cannot\n'
       '\t# keep it" -- and LightmapGI skips an unowned child as a helper: a real\n'
       '\t# bake laid 267 unowned fills and baked none of them.\n'
       '\tvar owned := fills.owner == level\n'
       '\tfor c in fills.get_children():\n'
       '\t\towned = owned and c.owner == level\n'
       '\t_check("the fills are owned by the scene, so the lightmapper takes them", owned, true)\n')

HEADER_OLD = "## gets BAKE_FILL_BULB_SHARE of the energy; every fill reaches\n## BAKE_FILL_REACH_CELLS cells, flat; the container has no owner, so a save\n## cannot keep it; a second call replaces it; and with no energy given it\n"
HEADER_NEW = "## gets BAKE_FILL_BULB_SHARE of the energy; every fill reaches\n## BAKE_FILL_REACH_CELLS cells, flat; every node is owned by the scene, which\n## the lightmapper needs (0.68.1); a second call replaces it; and with no energy given it\n"


def main():
    data = TEST.read_bytes()
    assert len(data) == 7653, "selftest is %d bytes, read at 7,653" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    for old in (OLD, HEADER_OLD):
        assert text.count(old) == 1, "anchor found %d times: %r" % (text.count(old), old[:60])
    text = text.replace(OLD, NEW).replace(HEADER_OLD, HEADER_NEW)
    TEST.write_bytes(text.encode("utf-8"))
    print("bake_fill_selftest.gd: %d -> %d bytes" % (len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
