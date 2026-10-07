"""Lux 0.68.2's test, written first: a den of sin is a building, not a room.

    python patch_lux_den_buildings_tests.py

Adds to `lux/tools/bake_fill_selftest.gd` (as 0.68.1 left it, 7,975 bytes,
LF): a club building b5 -- a tinted floor and an untinted back room -- whose
back room must get no fill, and an ordinary building b6 that must. The
prefix-less probes already there stay as they are: a probe that names no
building stands alone, which is 0.68.1's rule, and is the control.
On 0.68.1 it must FAIL (b5's back room is filled).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEST = ROOT / "lux" / "tools" / "bake_fill_selftest.gd"

OLD = ("\tvar again: Node3D = loader.add_bake_fills(level, 0.025)\n")
NEW = ("\t# DENS OF SIN ARE BUILDINGS (0.68.2): Lot ids every anchor `<building>/<id>`\n"
       "\t# and a probe is named for its room with \"/\" made \"_\". A club building's\n"
       "\t# back room keeps no fill; an ordinary building beside it keeps its own.\n"
       "\tvar den_floor := _probe(\"b5_main_floor_ambient\", Vector3(60.0, 1.6, 0.0), Vector3(10.0, 3.2, 10.0),\n"
       "\t\t0.0, Color(1.0, 0.55, 0.08))\n"
       "\tvar den_back := _probe(\"b5_back_rooms_ambient\", Vector3(60.0, 1.6, 12.0), Vector3(10.0, 3.2, 6.0),\n"
       "\t\t0.0, white)\n"
       "\tvar plain := _probe(\"b6_office_ambient\", Vector3(80.0, 1.6, 0.0), Vector3(6.0, 3.2, 6.0), 0.0, white)\n"
       "\tfor p in [den_floor, den_back, plain]:\n"
       "\t\tlevel.add_child(p)\n"
       "\tvar dens: Node3D = loader.add_bake_fills(level, 0.025)\n"
       "\t_check(\"a club building's back room keeps no fill\", _fills_of(dens, \"b5_back_rooms_ambient\").size(), 0)\n"
       "\t_check(\"...nor its tinted floor\", _fills_of(dens, \"b5_main_floor_ambient\").size(), 0)\n"
       "\t_check(\"an ordinary building beside it keeps its own\", _fills_of(dens, \"b6_office_ambient\").size(), 1)\n"
       "\t_check(\"control: a probe naming no building stands alone\", _fills_of(dens, \"shop_floor\").size(), 4)\n"
       "\tfor p in [den_floor, den_back, plain]:\n"
       "\t\tp.free()\n"
       "\n"
       "\tvar again: Node3D = loader.add_bake_fills(level, 0.025)\n")


def main():
    data = TEST.read_bytes()
    assert len(data) == 7975, "selftest is %d bytes, read at 7,975" % len(data)
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.count(OLD) == 1, text.count(OLD)
    TEST.write_bytes(text.replace(OLD, NEW).encode("utf-8"))
    print("bake_fill_selftest.gd: %d -> %d bytes" % (len(data), len(text.replace(OLD, NEW).encode("utf-8"))))


if __name__ == "__main__":
    main()
