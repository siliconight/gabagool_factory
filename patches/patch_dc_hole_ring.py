"""Deli Counter 0.236.1: a hole's greybox is a ring round it, never a box over it (the factory's roadmap 265).

Found by cold run 9340 (restaurant_row_001 on 0.236.0, 0 interventions): 8 new WALKTEST_WALKER_STUCK, all four walkers
on both of deli_a03's candidates sent to a target inside the deli's drop and stuck in its corner on the slab's cut.
0.236.0 drew a hole_edge's and a floor hatch's greybox as one box over the hole, and Lot bakes the walk test's navmesh
from the greybox lot's visual meshes too, so the bake took the box for floor. Measured over the library with
docs/findings/hole_causes_265/greybox_over_holes.py: 16 holes covered, 56.76 m2, on 0.236.0; none now.

What it changes (anchored; each file pinned by hash; nothing written on a miss; every file LF):
  * hole_causes.py -- `_ring`: the edge's and the hatch's greybox, four boxes outside the hole; `hole_slots` returns
    (slot, entry, boxes).
  * deli_counter.py -- `_vertical_links` draws each slot's boxes.
  * test_hole_causes.py -- `test_nothing_of_a_holes_greybox_stands_over_the_hole`; the file reads the new shape.
  * VERSION 0.236.0 -> 0.236.1, CHANGELOG.

AFTER APPLYING, in deli_counter/: the suite, build.py --all (hole_causes.py is a geometry source), check.py.

    python patches/patch_dc_hole_ring.py
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DC = ROOT / "deli_counter"
PINS = {'hole_causes.py': '6efe8e52035b4353', 'deli_counter.py': '0c069f3bc404e1a5', 'test_hole_causes.py': '4123e8264cb4cd8a'}
EDITS = {'hole_causes.py': [('lines 449-448', '\ndef hole_slots(spec, style_for):\n', '\ndef _ring(sid, hole, z, band, height):\n    """The greybox of a slot that stands ROUND a hole: four boxes `band` wide outside the hole\'s rect, named\n    ``<sid>_n`` / ``_s`` / ``_e`` / ``_w`` so each is the slot\'s own node (`themed_tscn.owns_node`) -- their union is\n    the slot\'s footprint, which the placement gate and the composer\'s fit read, and nothing is drawn over the hole.\n\n    A GREYBOX IS A DRAWING OF THE SPACE, and the walk test reads it: Lot bakes its walk navmeshes from visual meshes\n    too (`geometry_parsed_geometry_type = 2`), on the candidate\'s greybox lot. Cold run 9340 (restaurant_row_001,\n    Deli Counter 0.236.0) drew the edge as one box over the hole, its top 12 mm above the floor; the bake took it\n    for floor, and all four walkers on both of deli_a03\'s candidates were sent to a target inside the hole and\n    stuck in its corner against the slab\'s cut (WALKTEST_WALKER_STUCK 0 -> 8)."""\n    sx, sy = hole[2] - hole[0], hole[3] - hole[1]\n    x, y = (hole[0] + hole[2]) / 2.0, (hole[1] + hole[3]) / 2.0\n    return [("%s_n" % sid, (x, hole[3] + band / 2.0, z), (sx + 2.0 * band, band, height)),\n            ("%s_s" % sid, (x, hole[1] - band / 2.0, z), (sx + 2.0 * band, band, height)),\n            ("%s_e" % sid, (hole[2] + band / 2.0, y, z), (band, sy, height)),\n            ("%s_w" % sid, (hole[0] - band / 2.0, y, z), (band, sy, height))]\n\n\ndef hole_slots(spec, style_for):\n'), ('lines 452-453', "    ``slots`` is ``[(slot, gameplay_interactive or None, box_center, box_size)]``, as\n    `roof_hatch.roof_hatches` returns: the box is the greybox's, world-axis aligned.\n", "    ``slots`` is ``[(slot, gameplay_interactive or None, boxes)]``, ``boxes`` the greybox's\n    ``[(node name, center, size)]``, world-axis aligned: the spoil's and the kit's one box, the\n    edge's and the floor hatch's a ring round the hole (`_ring`), so nothing is drawn over it.\n"), ('lines 493-493', '            slots.append((slot, entry, center, (world[0], world[1], HATCH_FRAME)))\n', '            slots.append((slot, entry, _ring(sid, hole, center[2], HATCH_CURB, HATCH_FRAME)))\n'), ('lines 503-503', '                          None, center, (w, d, h_edge)))\n', '                          None, _ring(sid, hole, center[2], BAND, h_edge)))\n'), ('lines 520-520', '                          None, center, (w, d, SPOIL_H)))\n', '                          None, [(sid, center, (w, d, SPOIL_H))]))\n'), ('lines 533-533', '                      None, center, (box[2] - box[0], box[3] - box[1], KIT[2])))\n', '                      None, [(sid, center, (box[2] - box[0], box[3] - box[1], KIT[2]))]))\n')], 'deli_counter.py': [('lines 3003-3002', "        # collision, so the slab's cut stays the collider and the drop's route.\n        hole_slots, notes = hole_causes.hole_slots(\n", "        # collision, so the slab's cut stays the collider and the drop's route.\n        # The edge's and the hatch's greybox is a ring round the hole (0.236.1):\n        # the walk test bakes its navmesh from visual meshes too.\n        hole_slots, notes = hole_causes.hole_slots(\n"), ('lines 3006-3007', '        for slot, entry, c, size in hole_slots:\n            self._box(slot["slot_id"], c, size, self.VISUAL, role="prop")\n', '        for slot, entry, boxes in hole_slots:\n            for name, c, size in boxes:\n                self._box(name, c, size, self.VISUAL, role="prop")\n')], 'test_hole_causes.py': [('lines 60-59', 'def _slots(spec):\n    slots, notes = HC.hole_slots(spec, lambda material: 1)\n', 'def _slots(spec):\n    """{species: (slot, gameplay entry, greybox box center, greybox footprint)}, the greybox\'s union of boxes."""\n    slots, notes = HC.hole_slots(spec, lambda material: 1)\n'), ('lines 61-61', '    return {s["species"]: (s, e, c, size) for s, e, c, size in slots}, notes\n', '    out = {}\n    for s, e, boxes in slots:\n        lo = [min(c[i] - z[i] / 2.0 for _n, c, z in boxes) for i in range(3)]\n        hi = [max(c[i] + z[i] / 2.0 for _n, c, z in boxes) for i in range(3)]\n        out[s["species"]] = (s, e, tuple((a + b) / 2.0 for a, b in zip(lo, hi)),\n                             tuple(b - a for a, b in zip(lo, hi)))\n    return out, notes\n'), ('lines 216-215', '\ndef test_a_slots_variant_is_its_names_and_its_stem_is_zoos():\n', '\ndef test_nothing_of_a_holes_greybox_stands_over_the_hole():\n    """Cold run 9340: the walk test bakes its navmesh from the greybox lot\'s visual meshes, and 0.236.0 drew the\n    edge as one box over the hole -- the bake took it for floor and every walker on both of deli_a03\'s candidates was\n    sent into the hole (WALKTEST_WALKER_STUCK 0 -> 8). The edge and the floor hatch now draw a ring round it."""\n    for spec in (_house(), _house(link={"kind": "hatch", "story": 1, "x": -5.0, "y": 0.0}),\n                 json.load(open(os.path.join(HERE, "specs", "deli_a03.json"), encoding="utf-8"))):\n        slots, _n = HC.hole_slots(spec, lambda material: 1)\n        sh = float(spec.get("story_height") or SH)\n        thick = float(spec.get("floor_thick") or 0.3)\n        # each hole\'s rect, and the heights of the slab it is cut in, skins and all\n        holes = [(HC._rect(v), int(v["story"]) * sh - thick - HC.SKIN, int(v["story"]) * sh + HC.SKIN + 0.05)\n                 for v in HC.drop_links(spec)]\n        assert slots\n        for slot, _e, boxes in slots:\n            for name, c, z in boxes:\n                assert name == slot["slot_id"] or name.startswith(slot["slot_id"] + "_")\n                box = (c[0] - z[0] / 2.0, c[1] - z[1] / 2.0, c[0] + z[0] / 2.0, c[1] + z[1] / 2.0)\n                for h, z0, z1 in holes:\n                    if c[2] + z[2] / 2.0 < z0 or c[2] - z[2] / 2.0 > z1:\n                        continue                       # a spoil on the floor below is not over the hole\n                    inside = (min(box[2], h[2]) - max(box[0], h[0]), min(box[3], h[3]) - max(box[1], h[1]))\n                    assert inside[0] < 1e-6 or inside[1] < 1e-6, (slot["slot_id"], name, box, h)\n    edge, _e, center, size = _slots(_house())[0]["hole_edge"]\n    # the ring\'s union is still the slot\'s footprint, which the placement gate and the composer\'s fit read\n    assert size == pytest.approx(tuple(edge["fit"]["dims"]))\n    assert center == pytest.approx(tuple(edge["transform"]["translation"]))\n    (_slot, _e, boxes), = [x for x in HC.hole_slots(_house(), lambda m: 1)[0] if x[0]["species"] == "hole_edge"]\n    assert sorted(n[len("hole_edge_1_-50_0"):] for n, _c, _z in boxes) == ["_e", "_n", "_s", "_w"]\n\n\ndef test_a_slots_variant_is_its_names_and_its_stem_is_zoos():\n'), ('lines 256-256', '    assert [s["species"] for s, _e, _c, _z in HC.hole_slots(deli, lambda m: 1)[0]] == [\n', '    assert [s["species"] for s, _e, _b in HC.hole_slots(deli, lambda m: 1)[0]] == [\n'), ('lines 281-281', '            got[os.path.basename(p)[:-5]] = sorted((s["species"], s["form"], s["stock"]) for s, _e, _c, _z in slots)\n', '            got[os.path.basename(p)[:-5]] = sorted((s["species"], s["form"], s["stock"]) for s, _e, _b in slots)\n')]}
NEW_FILES = {}
CHANGELOG = "## [0.236.1] - a hole's greybox is a ring round it, never a box over it\n\n**The factory's roadmap 265, its first cold run.** Cold run 9340 (restaurant_row_001 on 0.236.0 and Zoo 1.114.0, 0\ninterventions) read 8 new findings, every one WALKTEST_WALKER_STUCK: all four walkers on both of deli_a03's candidates\nwere sent to a target inside the deli's drop and stuck in its corner, pressing on the slab's cut faces. 0.236.0 drew\nthe greybox of a `hole_edge` -- and of a floor hatch -- as one box over the hole, its top 12 mm above the floor; Lot\nbakes the walk test's navmesh from the candidate's greybox lot with visual meshes in it (`geometry_parsed_geometry_type\n= 2`), so the bake took the box for floor and laid a path and a target across the hole that no collider holds up.\n\n### Fixed\n- `hole_causes._ring`: an edge's and a floor hatch's greybox are four boxes outside the hole's rect -- `BAND` and\n  `HATCH_CURB` wide -- named `<slot_id>_n` / `_s` / `_e` / `_w`, so each is the slot's own node: their union is the\n  slot's footprint, which the placement gate and the composer's fit read, and nothing stands over the hole. The spoil\n  and the kit keep their one box each. `hole_slots` returns `(slot, entry, boxes)`; `_vertical_links` draws them.\n- Measured over the library (the factory's `docs/findings/hole_causes_265/greybox_over_holes.py`): on 0.236.0 all 16\n  dressed holes had greybox over their whole area, 56.76 m2 in all; now none.\n\n### Tests\n- test_hole_causes.py: `test_nothing_of_a_holes_greybox_stands_over_the_hole` (18 in the file). On 0.236.0 the file\n  fails 13: the new test, and 12 that read `hole_slots`' new shape.\n\n"
OLD_VERSION, NEW_VERSION = 'Deli Counter 0.236.0', 'Deli Counter 0.236.1'


def _sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def _read(name):
    raw = (DC / name).read_bytes()
    if _sha(raw) != PINS[name]:
        raise SystemExit("REFUSED: deli_counter/%s is %s, not the %s this patch was written against; nothing written"
                         % (name, _sha(raw), PINS[name]))
    if b"\r\n" in raw:
        raise SystemExit("REFUSED: deli_counter/%s has CRLF endings; these edits are LF" % name)
    return raw.decode("utf-8")


def main(argv):
    # every file worked out and checked before any is written
    out = {}
    for name, edits in EDITS.items():
        text = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: deli_counter/%s: the anchor at %s is there %d times; nothing written"
                                 % (name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text
    for name in NEW_FILES:
        p = DC / name
        if p.exists():
            raise SystemExit("REFUSED: deli_counter/%s exists already; nothing written" % name)
    v = DC / "VERSION"
    if v.read_bytes().decode("utf-8") != OLD_VERSION:
        raise SystemExit("REFUSED: VERSION reads %r, not %s; nothing written" % (v.read_text(), OLD_VERSION))
    cl = DC / "CHANGELOG.md"
    ctext = cl.read_bytes().decode("utf-8")
    if not ctext.startswith("## [0.236.0]"):
        raise SystemExit("REFUSED: CHANGELOG.md does not open on 0.236.0; nothing written")
    for name, text in out.items():
        (DC / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (DC / name).write_bytes(text.encode("utf-8"))
    v.write_bytes(NEW_VERSION.encode("utf-8"))
    cl.write_bytes((CHANGELOG + ctext).encode("utf-8"))
    print("%s applied: %d files edited, %d written, VERSION, CHANGELOG. Now, in deli_counter/: the suite, "
          "build.py --all, check.py" % (NEW_VERSION, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
