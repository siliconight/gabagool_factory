"""Zoo 1.61.0: an Empty's door is shut.

Deli Counter 0.174.0 made an Empty's doors solid in COLLISION and left the
VISUAL a doorway frame with no leaf, so a player saw an open doorway into a
dark box and walked into an invisible wall (cold runs 9146-9148, the
`empties_one_front_*` frames). Deli Counter 0.178.0 tags an Empty's doorway
`glazing: "facade"`, as it has tagged an Empty's window since 0.80.0; here a
doorway so tagged is filled with a painted panel door set back from the face.
See `zoo_shut_door/CHANGELOG_1.61.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  zoo_keeper/recipes/_arch.py  the leaf, after the window pane
Copies the test; CHANGELOG and VERSION.

    python patch_zoo_shut_door.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
ZOO = HERE.parent / "zoo"
SRC = HERE / "zoo_shut_door"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


CONST_OLD = '''#: The flat colour a room face falls back to with no skin library: a warm
#: off-white wall, the drywall a 1990s store is painted.
INNER_COLOR = (0.82, 0.80, 0.74)
'''
CONST_NEW = '''#: The flat colour a room face falls back to with no skin library: a warm
#: off-white wall, the drywall a 1990s store is painted.
INNER_COLOR = (0.82, 0.80, 0.74)

#: AN EMPTY'S DOOR (1.61.0): a painted panel door, set back from the street
#: face the depth a real frame recesses it, and as thick as a solid-core door.
#: Navy, one of the rowhouse comp's three door colours
#: (`docs/reference/EMPTIES_COMPS.md`); per-house colour is instance data,
#: not a material per colour, when it comes.
FACADE_DOOR_SETBACK = 0.08
FACADE_DOOR_THICK = 0.045
FACADE_DOOR_COLOR = (0.16, 0.20, 0.28)
'''

LEAF_OLD = '''        materials.assign([pane], glass)
        objs.append(pane)

    return {"objects": objs, "collision_boxes": cboxes, "attachments": {}}
'''
LEAF_NEW = '''        materials.assign([pane], glass)
        objs.append(pane)

    # AN EMPTY'S DOOR IS SHUT (1.61.0). A doorway tagged `glazing: "facade"`
    # belongs to a shell with nothing behind it (Deli Counter >= 0.178.0), the
    # same tag that glazes its windows opaque. Its collision has been solid
    # since Deli Counter 0.174.0; drawn as an open frame it was a doorway the
    # player could see into and not walk through. Filled with a leaf, set back
    # from the +Y street face (+Y is outdoors, see THE ROOM FACE above), no
    # collision of its own -- the wall's box already holds. After the room
    # face, like the panes: a door is not structure.
    if species == "doorway" and void and plan.get("glazing_kind") == "glass_facade":
        lw = void["x1"] - void["x0"]
        lh = void["z1"] - void["z0"]
        bm = geometry.new_bm()
        geometry.add_box(bm, ((void["x0"] + void["x1"]) / 2.0,
                              d / 2.0 - FACADE_DOOR_SETBACK - FACADE_DOOR_THICK / 2.0,
                              (void["z0"] + void["z1"]) / 2.0),
                         (lw - 0.004, FACADE_DOOR_THICK, lh - 0.002))
        leaf = geometry.bm_to_object(
            bm, f"{root}_Leaf", collection, bevel=bevel, texel=1.0,
            rng=rng, wear=wear, smooth_angle=_WALL_SMOOTH, butt_planes=butts)
        materials.assign([leaf], materials.make_material(
            "M_Door_wood_panel", plan.get("door_color", FACADE_DOOR_COLOR), "wood_panel"))
        objs.append(leaf)

    return {"objects": objs, "collision_boxes": cboxes, "attachments": {}}
'''


def main():
    assert (ZOO / "VERSION").read_text(encoding="utf-8").strip() == "1.60.0"
    _edit(ZOO / "zoo_keeper" / "recipes" / "_arch.py", [(CONST_OLD, CONST_NEW), (LEAF_OLD, LEAF_NEW)])
    shutil.copyfile(SRC / "test_shut_door.py", ZOO / "tests" / "test_shut_door.py")
    ch = ZOO / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_1.61.0.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (ZOO / "VERSION").write_text("1.61.0", encoding="utf-8", newline="\n")
    print("applied Zoo 1.61.0")


if __name__ == "__main__":
    main()
