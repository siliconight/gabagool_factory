"""Deli Counter 0.202.0: a piece keeps off an authored hole in its own floor.

    python patch_dc_hole_clear.py

`level_design._seed_clear`, anchored on its stair reservation as read
2026-10-07. Run AFTER `patch_dc_wall_backing.py`; asserts the file carries
that patch's `_held` and nothing of this one.

MEASURED FIRST (a dry refurnish of the library under the wall rule, then
under both): the rule moves 7 specs -- apartment_walkup_a01's and
rowhouse_raid's dining sets off their 2 x 2 m drop holes, cbp_town_finale's
and final_stand's furnished pieces out of atrium holes of 28 x 22 and 10 x 8 m
that nothing fills, and 4 pieces in each of corner_deli_heist_01, cr_deli and
night_deli off the 0.3 m margin round the upper floor's 2.2 x 2.2 m hole.

ITS OWN STOREY ONLY. A hole in storey 1's floor is a ceiling over storey 0;
the room below stands under it, not on it. Clearing every storey, as the stair
reserve does, would empty the floor under every drop hole. A hung piece
(`above`) hangs over the floor and is not asked.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LD = ROOT / "deli_counter" / "level_design.py"

OLD = (
    "    for rect in _stair_reserved_rects(spec):\n"
    "        if px + half > rect[0] - 0.3 and px - half < rect[2] + 0.3 and \\\n"
    "                py + half > rect[1] - 0.3 and py - half < rect[3] + 0.3:\n"
    "            return False\n"
    "    for l in spec.get(\"ladders\", []):\n"
)
NEW = (
    "    for rect in _stair_reserved_rects(spec):\n"
    "        if px + half > rect[0] - 0.3 and px - half < rect[2] + 0.3 and \\\n"
    "                py + half > rect[1] - 0.3 and py - half < rect[3] + 0.3:\n"
    "            return False\n"
    "    # AN AUTHORED HOLE IN THIS STOREY'S FLOOR (0.202.0), kept off by the stair\n"
    "    # reserve's own 0.3 m. Furnish cleared the stairs and never an authored\n"
    "    # `slab_holes` opening (layout_lint L23's \"UNSEEN\"): apartment_walkup_a01's\n"
    "    # dining set stood over its drop hole, and cbp_town_finale's and\n"
    "    # final_stand's furniture inside atrium holes nothing fills. Its own\n"
    "    # storey only -- the storey below stands under a hole, not on it -- and a\n"
    "    # hung piece hangs over the floor and is not asked.\n"
    "    if above is None:\n"
    "        for h in spec.get(\"slab_holes\", []) or []:\n"
    "            if int(h.get(\"story\", 0) or 0) != story:\n"
    "                continue\n"
    "            hx0, hx1 = h[\"x\"] - h[\"size_x\"] / 2.0, h[\"x\"] + h[\"size_x\"] / 2.0\n"
    "            hy0, hy1 = h[\"y\"] - h[\"size_y\"] / 2.0, h[\"y\"] + h[\"size_y\"] / 2.0\n"
    "            if px + half > hx0 - 0.3 and px - half < hx1 + 0.3 and \\\n"
    "                    py + half > hy0 - 0.3 and py - half < hy1 + 0.3:\n"
    "                return False\n"
    "    for l in spec.get(\"ladders\", []):\n"
)


def main():
    data = LD.read_bytes()
    assert b"\r\n" not in data, "CRLF in level_design.py; refusing"
    text = data.decode("utf-8")
    assert "def _held(" in text, "patch_dc_wall_backing.py has not run; refusing"
    assert "AN AUTHORED HOLE IN THIS STOREY'S FLOOR" not in text, "already applied; refusing"
    n = text.count(OLD)
    assert n == 1, "the stair reserve found %d times, not once" % n
    LD.write_bytes(text.replace(OLD, NEW).encode("utf-8"))
    print("level_design.py: %d -> %d bytes" % (len(data), len(LD.read_bytes())))


if __name__ == "__main__":
    main()
