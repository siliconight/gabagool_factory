"""Roadmap 220: the bar on the door sign found and fixed (Patina 0.29.2); item 221 filed.

220's status line is replaced whole: the one line that starts with its unique opening, asserted
to be exactly one. Its body keeps every claim it made, and the one that was half wrong gets its
correction beside it; the finding is appended after its last line, asserted to end the file.
Item 221 is appended after it, its status directly above its heading, refused if a 221 exists.
Then:

    python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib

ROADMAP = pathlib.Path(__file__).resolve().parent.parent / "PIPELINE_ROADMAP.md"

START = "*STATUS: OPEN 2026-10-09 -- found in cold run 9217's frames and older than them:"
NEW = (
    "*STATUS: NARROWED 2026-10-09 -- cause found and fixed, not yet run cold. The bar is Patina's "
    "conduit run to the sign: a 0.05 x 0.04 x 0.27 m box on the sign's face plane, from the door "
    "head (2.28 m) to the face's middle (2.55 m). `anchors.conduit_targets` took Deli Counter's "
    "sign anchor -- the face itself, `_SIGN_OUT` 0.2 m proud of the wall -- as a fixture to run "
    "conduit to, and `openings.apply` started the run above the door the sign hangs over. Found by "
    "hiding, one at a time in the walked level, each of the 19 meshes within 2 m of the bar: "
    "`b0/Dressing/CoverN_concrete` alone took it from luma 243 to 90, against the face's 122. All "
    "three signed buildings of 9217 ordered one. Patina 0.29.2 stops running conduit to a sign "
    "(`docs/findings/sign_bar/`). Owed: a cold run framing those doors. Item 221 filed on the "
    "way.*"
)

BODY_END = (
    "Next: frame `sign_box` alone, in a probe the drape's way (`docs/findings/den_drapes/probe.gd`). A "
    "bar there is Zoo's; none there is the level's -- the bake, or the rig standing 0.29 m off the "
    "face.\n"
)
FOUND = (
    "\n"
    "**Found, 2026-10-09** (`docs/findings/sign_bar/`). The probe above was not needed.\n"
    "- **`light_breakdown` with the bake switched off left the bar standing,** dark against the "
    "emissive face. So it was a lit object, not the face's texture or emission.\n"
    "- **`hide_and_seek.gd` hid each drawn thing within 2 m of the bar,** in the walked level, and "
    "measured the bar's strip of screen against the face beside it:\n"
    "  - one of 19 moved it, `b0/Dressing/CoverN_concrete_delco_1997`: 243 to 90, against the face's "
    "122;\n"
    "  - hiding the sign's own face left the bar standing (242.3).\n"
    "- **That merged mesh holds a box** at building-local x -5.025..-4.975, y 2.28..2.55, z "
    "12.33..12.37. The face is the plane z = 12.35, centred at x = -5.0.\n"
    "- **The box is Patina's order** `conduit_run` at spec (-5.0, -12.35, 2.415), size 0.27, "
    "`clipped_by` `ext_0_S_open0`. The sign's anchor stands at (-5.0, -12.35, 2.55).\n"
    "- **airport_terminal_a02 and funeral_home_a03 ordered the same stub.** Deli Counter's "
    "`_storefront_sign` hangs every sign it derives over a door.\n"
    "\n"
    "Corrections to the list above, kept beside it:\n"
    "- **\"Geometry standing off the face\"** read the parallax right: the bar keeps its place "
    "between the letters. But it straddles the face plane, 2 cm either way. So it is geometry ON the "
    "plane, not the face's own.\n"
    "- **An AABB census of the sign's surroundings DID list the mesh:** `CoverN_concrete`'s box "
    "reached z 14.37, in front of the face at 14.35. It was set aside because a merged mesh's box "
    "spans its building, and its name says north while the sign faces south. A census can say a "
    "merged mesh reaches a point; it cannot say which part does.\n"
    "\n"
    "**The fix is Patina 0.29.2.** `conduit_targets` runs conduit to wall packs only. A cabinet "
    "sign is fed through the wall behind it. Its test fails on 0.29.1, and a kept instrument test "
    "rebuilds 0.29.1's order through the opening pass: the 0.27 m stub on the face plane.\n"
)

ITEM_221 = (
    "\n"
    "*STATUS: OPEN 2026-10-09 -- found while tracing 220: Patina's anchor-derived wall covers face "
    "INTO the building, so Zoo merges base courses and conduits with the opposite face's covers. On "
    "9217's strip_club_a01 each concrete merge group spans two faces (CoverN 2,544 north-face "
    "vertices and 480 south-face), and the painted-metal groups do not. 22 of the club's 51 base "
    "courses stand on a wall's centre line, buried. Not priced; cause not verified.*\n"
    "\n"
    "**221. Patina's wall covers face into the building.** Found in cold run 9217's orders for "
    "strip_club_a01 while tracing 220 (`docs/findings/sign_bar/README.md`). In the spec frame:\n"
    "- **The anchor-derived covers face in.** The south door's conduit carries normal +y, and "
    "all 51 base courses carry inward normals, for example +x on the west face.\n"
    "- **The slot-derived ones face out,** as they should: the gutters and downspouts from "
    "`framing.py`.\n"
    "\n"
    "**What it costs: the per-side merge stops culling by side.** Zoo's `dressing.cover_side` puts "
    "a wall-facing cover on the side its normal leaves, so base courses and conduits join the "
    "opposite face's group. Roadmap 180 merged covers per side because a side enters and leaves "
    "view together. The club's dressing GLB, vertices by the face they lie on:\n"
    "\n"
    "| mesh | its own face | the opposite face |\n"
    "|---|---|---|\n"
    "| CoverN_concrete | N 2,544 | S 480 |\n"
    "| CoverS_concrete | S 1,344 | N 1,008 |\n"
    "| CoverE_concrete | E 912 | W 672 |\n"
    "| CoverW_concrete | W 1,008 | E 432 |\n"
    "\n"
    "The four painted-metal meshes each lie on their own face only. Not priced: what a building in "
    "view pays for its back's concrete has not been measured.\n"
    "\n"
    "**Two smaller things in the same orders:**\n"
    "- **22 of the 51 base courses stand on a wall's centre line,** buried in a 0.3 m wall: 9 on the "
    "south face at y -12.000, 7 west, 6 north. The other 29 stand on the outer face.\n"
    "- **The wall packs' conduits stand at the pack,** 0.15 m proud of the wall (Deli Counter's "
    "`_WALL_PACK_OUT`). Each is a 0.17 m stub from the door head to the pack's housing, off the "
    "wall. 220's rule was the same, for the sign.\n"
    "\n"
    "**The likely cause, NOT verified.** For a Y-up shell, `anchors._up_to_z` permutes positions "
    "(x, y, z) to (x, z, y). That swap is a reflection. `_exterior_wall_faces` takes each "
    "triangle's normal from a cross product of the permuted positions, so the mirrored winding "
    "would invert every normal it derives. The slot path never takes a cross product. Next:\n"
    "1. print one segment's normal against its wall's known facing, before believing this;\n"
    "2. then fix the normal once, where it is derived, and put the wall packs' conduits on the "
    "wall;\n"
    "3. then price the merge before and after, at stations that face one side of a building.\n"
)


def main():
    data = ROADMAP.read_bytes()
    assert b"\r\n" not in data, "the roadmap is LF; found CRLF"
    text = data.decode("utf-8")
    assert "**221." not in text, "item 221 exists"
    lines = text.split("\n")
    hits = [i for i, ln in enumerate(lines) if ln.startswith(START)]
    assert len(hits) == 1, len(hits)
    lines[hits[0]] = NEW
    text = "\n".join(lines)
    assert text.endswith(BODY_END) and text.count(BODY_END) == 1, "220's body does not end the file"
    ROADMAP.write_bytes((text + FOUND + ITEM_221).encode("utf-8"))
    print("roadmap 220: narrowed, fixed in Patina 0.29.2; 221 filed")


if __name__ == "__main__":
    main()
