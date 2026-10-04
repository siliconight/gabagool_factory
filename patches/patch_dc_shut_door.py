"""Deli Counter 0.178.0: an Empty's doorway is tagged so Zoo shuts it.

0.174.0 made an Empty's doors solid in collision and left the visual an open
frame: a doorway a player could see into and not walk through. Its windows
have carried `glazing: "facade"` since 0.80.0 so Zoo glazes them opaque; its
doorways now carry it too, and Zoo (>= 1.61.0) fills them with a shut panel
door. See `dc_shut_door/CHANGELOG_0.178.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  deli_counter.py         the tag on a facade doorway
  test_facade_glazing.py  the test that pinned the opposite, retracted in place
CHANGELOG and VERSION. `python build.py --all` follows.

    python patch_dc_shut_door.py
"""
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
DC = HERE.parent / "deli_counter"
SRC = HERE / "dc_shut_door"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


TAG_OLD = '''        if role == "window" and getattr(self.s, "facade", False):
            slot["glazing"] = "facade"
'''
TAG_NEW = '''        #
        # AND ITS DOORWAY (0.178.0). Since 0.174.0 an Empty's door is solid in
        # collision and was drawn as an open frame -- a doorway into a dark
        # box that a player walks into as a wall. The same tag says "nothing
        # behind this opening" to Zoo (>= 1.61.0), which shuts it with a leaf.
        if role in ("window", "doorway") and getattr(self.s, "facade", False):
            slot["glazing"] = "facade"
'''

TEST_OLD = '''def test_a_facade_door_carries_no_glazing(dc):
    slots = _opening_slots(dc, _with_openings(presets.facade_storefront()))
    for s in _by_role(slots, "doorway"):
        assert "glazing" not in s, s["slot_id"]
'''
TEST_NEW = '''# RETRACTED 0.178.0, kept above what replaced it: "a facade door carries no
# glazing". True while no facade had a door anyone could see into. Since
# 0.174.0 an Empty's door is solid in collision, and untagged it was drawn as
# an open frame -- cold run 9148's `empties_one_front_*`. Tagged, Zoo
# (>= 1.61.0) shuts it.
def test_a_facade_door_carries_facade_glazing_so_zoo_shuts_it(dc):
    slots = _opening_slots(dc, _with_openings(presets.facade_storefront()))
    for s in _by_role(slots, "doorway"):
        assert s.get("glazing") == "facade", s["slot_id"]
'''


def main():
    assert (DC / "VERSION").read_text(encoding="utf-8").strip() == "Deli Counter 0.177.0"
    _edit(DC / "deli_counter.py", [(TAG_OLD, TAG_NEW)])
    _edit(DC / "test_facade_glazing.py", [(TEST_OLD, TEST_NEW)])
    ch = DC / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.178.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (DC / "VERSION").write_text("Deli Counter 0.178.0", encoding="utf-8", newline="\n")
    print("applied Deli Counter 0.178.0")


if __name__ == "__main__":
    main()
