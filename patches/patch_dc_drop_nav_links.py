"""Deli Counter 0.226.0: a declared drop carries its own off-mesh nav link (factory roadmap 173, step 3).

A `floor_hole` or `hatch` vertical link is the spec saying "a body goes down here" (`spec_types.VerticalLink`:
"describe a vertical angle or drop point"). The builder cut the slab and recorded the link, and nothing
downstream could tell that hole from one nobody meant: the package's `navigation_hints.json` carried a ladder's
off-mesh link (0.172.0, `ladder._nav_link`) and no drop's, so the AI had no edge through a hole a player drops
through, and a drop-edge gate had no declared set to read. Now `ladder.drop_nav_link` files one on the record,
the same shape as a ladder's (Dispatch carries it verbatim, Lot moves its positions into site space), one-way,
`required_capability` "drop", with the cut's rect under `hole` for a gate that asks which rim is declared.

What it changes (anchored; refuses on a miss; CRLF-safe):
  * ladder.py: DROP_COST and drop_nav_link(lid, story, x, y, size_x, size_y, story_height).
  * deli_counter.py _vertical_links: the record gains "nav_link" for floor_hole / hatch links with a storey and a
    position (a local `import ladder`, as `_ladder_semantics` does).
  * test_drop_nav_link.py, VERSION 0.226.0, CHANGELOG.

    python patches/patch_dc_drop_nav_links.py --tests   # the test file only (prove it fails first)
    python patches/patch_dc_drop_nav_links.py           # everything
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DC = ROOT / "deli_counter"


def _apply(path, old, new, count=1):
    raw = path.read_bytes()
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    assert crlf == 0 or lf == 0, f"{path.name}: mixed endings ({crlf} CRLF, {lf} LF)"
    eol = "\r\n" if crlf else "\n"
    text = raw.decode("utf-8")
    o, n = old.replace("\n", eol), new.replace("\n", eol)
    assert text.count(o) == count, f"{path.name}: anchor found {text.count(o)} times, wanted {count}: {old[:70]!r}"
    path.write_bytes(text.replace(o, n).encode("utf-8"))


COST_OLD = '''_AI_COST = {"fixed_vertical": 3.0, "ship": 2.0, "alternating_tread": 2.5,
            "caged": 3.5, "safety_rail": 3.2}
'''
COST_NEW = '''_AI_COST = {"fixed_vertical": 3.0, "ship": 2.0, "alternating_tread": 2.5,
            "caged": 3.5, "safety_rail": 3.2}
#: A declared drop's cost to a planner: dearer than any ladder, because it is
#: one-way and the body takes a storey's fall -- a route of last resort, not a
#: shortcut the AI prefers to a stair.
DROP_COST = 4.0
'''

HELPER_ANCHOR = '''    }


def _authority_split(ld):
'''
HELPER_NEW = '''    }


def drop_nav_link(lid, story, x, y, size_x, size_y, story_height):
    """s17.2 for a DECLARED DROP: the one-way off-mesh link a `floor_hole` or
    `hatch` vertical link files on itself (0.226.0, factory roadmap 173).

    The link starts over the cut on the storey whose floor it opens (`story`:
    the slab whose TOP face is that storey's floor, the same key the builder's
    slab holes use) and ends on the floor below, the same two-point shape as
    `_nav_link` so Dispatch carries it as it carries a ladder's and Lot moves
    both points into site space. One-way, `required_capability` "drop": a
    planner that cannot fall does not route through it, and one that can pays
    `DROP_COST`. `hole` is the cut's rect on the upper floor, two corners, for
    a gate that asks which rim a body may walk off: the declared set and the
    AI's set are then one list.
    """
    sx = float(size_x or 1.5)
    sy = float(size_y or 1.5)
    z_top = float(story) * float(story_height)
    z_bottom = (float(story) - 1.0) * float(story_height)
    return {
        "id": f"{lid}_navlink",
        "start_position": [x, y, z_top],
        "end_position": [x, y, z_bottom],
        "bidirectional": False,
        "cost": DROP_COST,
        "agent_types": ["player", "ai_humanoid"],
        "required_capability": "drop",
        "access_state": "open",
        "reservation_state": "free",
        "hole": [[x - sx / 2.0, y - sy / 2.0], [x + sx / 2.0, y + sy / 2.0]],
    }


def _authority_split(ld):
'''

BUILDER_OLD = '''        for v in self.s.vertical_links:
            self.gameplay["vertical_links"].append({
                "kind": v.kind, "role": v.role,
                "from_story": v.from_story, "to_story": v.to_story,
                "story": v.story, "x": v.x, "y": v.y,
                "breachable": v.breachable,
            })
'''
BUILDER_NEW = '''        import ladder as _ladder
        for v in self.s.vertical_links:
            rec = {
                "kind": v.kind, "role": v.role,
                "from_story": v.from_story, "to_story": v.to_story,
                "story": v.story, "x": v.x, "y": v.y,
                "breachable": v.breachable,
            }
            # A DECLARED DROP CARRIES ITS OWN OFF-MESH LINK (0.226.0, factory
            # roadmap 173). The package carried a ladder's link and no drop's,
            # so nothing downstream could tell this hole from one nobody
            # meant: the AI had no edge through it and a drop-edge gate had no
            # declared set to read. The same shape as a ladder's, one-way,
            # capability "drop", with the cut's rect (`ladder.drop_nav_link`).
            if (v.kind in ("floor_hole", "hatch") and v.story is not None
                    and v.x is not None and v.y is not None):
                lid = "%s_%s_%d_%d_%d" % (self.s.name, v.kind, v.story,
                                          round(v.x), round(v.y))
                rec["nav_link"] = _ladder.drop_nav_link(
                    lid, v.story, v.x, v.y, v.size_x, v.size_y,
                    self.s.story_height)
            self.gameplay["vertical_links"].append(rec)
'''

TEST = '''"""A declared drop carries its own off-mesh nav link (0.226.0, factory roadmap 173).

Run: pytest -q test_drop_nav_link.py
"""
import ladder as L


def test_drop_link_shape():
    nl = L.drop_nav_link("deli_a01_floor_hole_1_8_-4", 1, 8.0, -4.0, None, None, 3.3)
    assert nl["id"] == "deli_a01_floor_hole_1_8_-4_navlink"
    assert nl["start_position"] == [8.0, -4.0, 3.3]          # over the cut, on the storey whose floor it opens
    assert nl["end_position"] == [8.0, -4.0, 0.0]            # on the floor below
    assert nl["bidirectional"] is False                       # a fall is one-way
    assert nl["required_capability"] == "drop"
    assert nl["cost"] == L.DROP_COST and nl["cost"] > max(L._AI_COST.values())
    assert nl["agent_types"] == ["player", "ai_humanoid"]
    assert nl["access_state"] == "open" and nl["reservation_state"] == "free"


def test_the_hole_is_the_cut_the_builder_makes():
    nl = L.drop_nav_link("x", 2, 13.0, -9.0, None, None, 3.6)
    assert nl["hole"] == [[12.25, -9.75], [13.75, -8.25]]      # 1.5 m square by default, as `_vertical_links` cuts
    nl = L.drop_nav_link("x", 2, 0.0, 0.0, 1.0, 1.2, 3.6)
    assert nl["hole"] == [[-0.5, -0.6], [0.5, 0.6]]


def test_a_roof_hatch_drops_into_the_top_storey():
    nl = L.drop_nav_link("x", 2, 0.0, 0.0, None, None, 3.6)   # story 2 of a two-storey building: the roof slab
    assert nl["start_position"][2] == 7.2 and nl["end_position"][2] == 3.6


def test_a_ladder_link_is_untouched():
    """The shape is shared with `_nav_link`; the capability and direction are what differ."""
    keys = set(L.drop_nav_link("x", 1, 0.0, 0.0, None, None, 3.0)) - {"hole"}
    lad = L._nav_link(type("Ld", (), {"x": 0.0, "y": 0.0})(), "l", 0.0, 3.0)
    assert keys == set(lad)
    assert lad["required_capability"] == "climb" and lad["bidirectional"] is True
'''

CHANGELOG_ENTRY = '''## [0.226.0] - a declared drop carries its own off-mesh nav link

**Factory roadmap 173 ("a drop is either guarded or declared, and today nothing declares one"), step 3.** A
`floor_hole` or `hatch` vertical link is the spec saying "a body goes down here"; the builder cut the slab and
recorded the link, and nothing downstream could tell that hole from one nobody meant. The package's
`navigation_hints.json` carried a ladder's off-mesh link (0.172.0) and no drop's: measured on cold run 9317's
package, 2 links, both ladders, while deli_a01 declares a floor hole and a hatch. So the AI had no edge through
a hole a player drops through, and the drop-edge instrument that found the office's unguarded stair pit (0.225.0)
had no declared set to read off the package -- it reads Deli Counter's build records instead, which a consumer
of the package does not have.

### Added
- **`ladder.drop_nav_link(lid, story, x, y, size_x, size_y, story_height)`**: the one-way off-mesh link of a
  declared drop, the same two-point shape as a ladder's `_nav_link` (so Dispatch carries it verbatim and Lot
  moves its points into site space), starting over the cut on the storey whose floor it opens and ending on the
  floor below, `bidirectional` false, `required_capability` "drop", `cost` `DROP_COST` (4.0, dearer than any
  ladder: a route of last resort), and `hole`, the cut's rect as two corners, for a gate that asks which rim is
  declared.
- **`_vertical_links` files it on the record** as `nav_link`, for `floor_hole` / `hatch` links with a storey and
  a position; a `stair` link, which is descriptive, carries none. The id is
  `<spec>_<kind>_<story>_<x>_<y>_navlink`.
- `test_drop_nav_link.py`.

### Downstream
Lot 0.125.0 moves the link's points into site space with the vertical link; Dispatch 0.5.3 reads it from both
importers into `navigation_hints.json` `links[]`. The factory's `tools/walkable_edge.gd` sort can then take the
declared set from the package rather than from this repo's build records.

'''


def write_tests():
    (DC / "test_drop_nav_link.py").write_text(TEST, encoding="utf-8")
    print("wrote deli_counter/test_drop_nav_link.py")


def main(argv):
    if "--tests" in argv:
        write_tests()
        return 0
    lad = DC / "ladder.py"
    _apply(lad, COST_OLD, COST_NEW)
    _apply(lad, HELPER_ANCHOR, HELPER_NEW)
    _apply(DC / "deli_counter.py", BUILDER_OLD, BUILDER_NEW)
    v = DC / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "Deli Counter 0.225.0", v.read_text(encoding="utf-8")
    v.write_text("Deli Counter 0.226.0", encoding="utf-8")
    cl = DC / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = "\r\n" if raw.count(b"\r\n") else "\n"
    text = raw.decode("utf-8")
    assert text.startswith("## [0.225.0]"), text[:40]
    cl.write_bytes((CHANGELOG_ENTRY.replace("\n", eol) + text).encode("utf-8"))
    write_tests()
    print("Deli Counter 0.226.0 applied: drop_nav_link on every floor_hole / hatch record, test, VERSION, CHANGELOG")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
