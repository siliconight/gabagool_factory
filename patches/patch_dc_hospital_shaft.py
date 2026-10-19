"""Deli Counter 0.232.0: every hole in a stacked shaft is declared, and its drop lands where a body would (roadmap 173).

FOUND BY THE BREADTH SWEEP OF 2026-10-19. Cold run 9329 (county_hospital_001, its first run since 9230, before Level
Factory 0.216.0's drop-edge gate existed) STOPPED at the export with 0 interventions: `UNDECLARED_DROP_INDOORS: 20
unguarded edge(s) a body reaches, indoors, on a floor, that nothing declares`. All 20 are one rim: the storey-2 slab
round the hospital's elevator shaft, dropping 7.2 m to the ground floor (`drop_edges_scan.json`: on
`GreyboxBase/slab_col_2`, to `slab_col_0`, x -7..-5, z -13.25..-10.75). The generated shell
`lf_county_hospital_001_9208` cuts the shaft as `presets.hospital` writes it -- "an elevator shaft as a vertical
horde-spawn channel (floor holes stacked)", a hole on every storey from 1 to the top -- and declares ONE of them, a
`floor_hole` on storey 1. A three-storey build's storey-2 hole goes undeclared; the gate keys a declared rim on its
storey as well as its rect, so the storey-1 link does not cover it, and it is right not to.

THE FIX, in the generator, two parts:
  * `presets.hospital` declares a `floor_hole` for every hole it stacks, storey 1 to the top.
  * A declared drop lands where a body would. `ladder.drop_nav_link` ended every link on "the floor below"; over a
    stacked shaft that floor has a hole of its own, and the storey-2 link would end in mid-air over storey 1's cut.
    `ladder.drop_landing(story, x, y, holes)` walks down through every storey whose slab is cut under the drop and
    returns the first that is not; `_vertical_links` passes it (`land_story=`) to `drop_nav_link`. A drop over an
    uncut floor lands on the floor below, as before.

The census beside it (read off every spec on disk): 46 slab holes in 37 specs; undeclared, the generated hospitals'
upper shaft holes and, in the library, three atriums (bank, cbp_town_finale_midbalanced_schemafixed, final_stand) --
large guarded voids, not this shaft, left to the gate's guarded class and not changed here.

What it changes (anchored; each file pinned by hash; nothing written on a miss; LF-safe):
  * presets.py -- the hospital's `vertical_links`, one `floor_hole` a stacked hole.
  * ladder.py -- `drop_landing`; `drop_nav_link(land_story=None)`.
  * deli_counter.py -- `_vertical_links` lands each declared drop.
  * test_hospital_shaft.py (new, 5; all fail on 0.231.1): every stacked hole declared, at three and four floors; the
    landing through stacked cuts; a single cut lands on the floor below; the link ends where it lands.
  * VERSION 0.231.1 -> 0.232.0, CHANGELOG.

AFTER APPLYING: `python build.py --all` (presets.py, ladder.py and deli_counter.py are geometry sources; no library
spec carries the hospital shaft, so no shell should change but its build time), the suite, the commit, and
county_hospital_001 cold.

    python patches/patch_dc_hospital_shaft.py --tests   # the test file only (prove it fails first)
    python patches/patch_dc_hospital_shaft.py           # everything; the test again when it is this patch's
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DC = ROOT / "deli_counter"
PINS = {
    "presets.py": "e2f98163c9979741",
    "ladder.py": "57262560f62d3ac7",
    "deli_counter.py": "5a45fed9dfc11df2",
}

PRESET_OLD = '''    spec["vertical_links"] = [
        {"kind": "stair", "from_story": 0, "to_story": top, "role": "main_route"},
        {"kind": "stair", "from_story": 0, "to_story": top, "role": "emergency_route"},
        {"kind": "floor_hole", "story": 1, "x": 0.0, "y": 12.0, "size_x": 2.6, "size_y": 2.6, "role": "elevator_shaft_horde_channel"},
    ]
'''
PRESET_NEW = '''    spec["vertical_links"] = [
        {"kind": "stair", "from_story": 0, "to_story": top, "role": "main_route"},
        {"kind": "stair", "from_story": 0, "to_story": top, "role": "emergency_route"},
    ] + [
        # EVERY HOLE IN THE SHAFT DECLARED (0.232.0, the factory's roadmap
        # 173): only storey 1's was, and a three-storey build's storey-2 rim
        # fell 7.2 m with nothing declaring it -- cold run 9329's export
        # refused it. One `floor_hole` a stacked hole, each landing through
        # the cuts below it (`ladder.drop_landing`).
        {"kind": "floor_hole", "story": st, "x": 0.0, "y": 12.0, "size_x": 2.6, "size_y": 2.6,
         "role": "elevator_shaft_horde_channel"}
        for st in range(1, floors)
    ]
'''

LADDER_OLD = '''def drop_nav_link(lid, story, x, y, size_x, size_y, story_height):
'''
LADDER_NEW = '''def drop_landing(story, x, y, holes):
    """The storey a body dropped through a cut in storey ``story``'s floor at
    (``x``, ``y``) lands on (0.232.0, the factory's roadmap 173): the floor
    below, unless that floor is cut under the same point too, in which case it
    falls on through -- a stacked shaft lands on the first floor below it that
    is not cut there, the ground floor's slab never being. ``holes`` are the
    building's slab cuts, each with ``story``, ``x``, ``y``, ``size_x`` and
    ``size_y`` (a `SlabHole` or a dict)."""
    def _get(h, k, default=None):
        return h.get(k, default) if isinstance(h, dict) else getattr(h, k, default)

    land = int(story) - 1
    while land > 0 and any(
            int(_get(h, "story", -1)) == land
            and abs(float(_get(h, "x", 1e9)) - float(x)) < float(_get(h, "size_x", 0.0) or 0.0) / 2.0
            and abs(float(_get(h, "y", 1e9)) - float(y)) < float(_get(h, "size_y", 0.0) or 0.0) / 2.0
            for h in holes or ()):
        land -= 1
    return max(0, land)


def drop_nav_link(lid, story, x, y, size_x, size_y, story_height, land_story=None):
'''
LADDER_DOC_OLD = '''    a gate that asks which rim a body may walk off: the declared set and the
    AI's set are then one list.
    """
    sx = float(size_x or 1.5)
    sy = float(size_y or 1.5)
    z_top = float(story) * float(story_height)
    z_bottom = (float(story) - 1.0) * float(story_height)
'''
LADDER_DOC_NEW = '''    a gate that asks which rim a body may walk off: the declared set and the
    AI's set are then one list.

    ``land_story`` (0.232.0): where the body lands, `drop_landing`'s answer.
    Over a stacked shaft the floor below is cut too, and a link ending there
    ends in mid-air. Absent, the floor below, as before.
    """
    sx = float(size_x or 1.5)
    sy = float(size_y or 1.5)
    z_top = float(story) * float(story_height)
    land = (float(story) - 1.0) if land_story is None else float(land_story)
    z_bottom = land * float(story_height)
'''

DC_OLD = '''                rec["nav_link"] = _ladder.drop_nav_link(
                    lid, v.story, v.x, v.y, v.size_x, v.size_y,
                    self.s.story_height)
'''
DC_NEW = '''                # landing through every storey cut under the drop (0.232.0):
                # a stacked shaft's upper link ended in mid-air over the cut
                # below it (`ladder.drop_landing`)
                rec["nav_link"] = _ladder.drop_nav_link(
                    lid, v.story, v.x, v.y, v.size_x, v.size_y,
                    self.s.story_height,
                    land_story=_ladder.drop_landing(v.story, v.x, v.y,
                                                    self.s.slab_holes))
'''

TEST = r'''"""Every hole in a stacked shaft is declared, and its drop lands where a body would (0.232.0, the factory's
roadmap 173).

Cold run 9329's export refused county_hospital_001: the generated hospital stacks an elevator shaft's holes on every
storey and declared only storey 1's, so the storey-2 rim fell 7.2 m with nothing declaring it. And a declared drop
ended on "the floor below", which over a stacked shaft is cut too.

Run: python -m pytest -q test_hospital_shaft.py
"""
import ladder
import presets


def _shaft(spec):
    holes = {(h["story"], h["x"], h["y"]) for h in spec.get("slab_holes") or []}
    declared = {(v["story"], v["x"], v["y"]) for v in spec.get("vertical_links") or []
                if v.get("kind") == "floor_hole"}
    return holes, declared


def test_every_stacked_hole_is_declared_at_three_floors():
    holes, declared = _shaft(presets.hospital(floors=3))
    assert len(holes) == 2 and holes <= declared, (holes, declared)


def test_every_stacked_hole_is_declared_at_four_floors():
    holes, declared = _shaft(presets.hospital(floors=4))
    assert len(holes) == 3 and holes <= declared, (holes, declared)


def test_a_drop_falls_through_the_cuts_below_it():
    shaft = [{"story": s, "x": 0.0, "y": 12.0, "size_x": 2.6, "size_y": 2.6} for s in (1, 2, 3)]
    assert ladder.drop_landing(3, 0.0, 12.0, shaft) == 0
    assert ladder.drop_landing(2, 0.0, 12.0, shaft) == 0
    assert ladder.drop_landing(1, 0.0, 12.0, shaft) == 0
    # beside the shaft, the floor below holds
    assert ladder.drop_landing(3, 5.0, 12.0, shaft) == 2


def test_a_single_cut_lands_on_the_floor_below():
    one = [{"story": 2, "x": 0.0, "y": 0.0, "size_x": 2.0, "size_y": 2.0}]
    assert ladder.drop_landing(2, 0.0, 0.0, one) == 1


def test_the_link_ends_where_it_lands():
    link = ladder.drop_nav_link("h", 2, 0.0, 12.0, 2.6, 2.6, 3.6, land_story=0)
    assert link["start_position"][2] == 7.2 and link["end_position"][2] == 0.0
    plain = ladder.drop_nav_link("h", 2, 0.0, 12.0, 2.6, 2.6, 3.6)
    assert plain["end_position"][2] == 3.6
'''

CHANGELOG = '''## [0.232.0] - every hole in a stacked shaft is declared, and its drop lands where a body would

**Found by the factory's breadth sweep of 2026-10-19 (roadmap 173).** Cold run 9329, county_hospital_001's first run
since Level Factory's drop-edge gate shipped, stopped at the export with 0 interventions: `UNDECLARED_DROP_INDOORS:
20 unguarded edge(s)`. All 20 are one rim, the storey-2 slab round the hospital's elevator shaft, 7.2 m above the
ground floor. `presets.hospital` stacks the shaft's holes on every storey from 1 to the top -- "a vertical
horde-spawn channel" -- and declared only storey 1's. The gate keys a declared rim on its storey as well as its
rect, so the storey-1 link did not cover storey 2, rightly.

### Fixed
- `presets.hospital` declares a `floor_hole` for every hole it stacks.
- A declared drop lands where a body would. `drop_nav_link` ended every link on the floor below, which over a stacked
  shaft is cut too: the upper link ended in mid-air. `ladder.drop_landing(story, x, y, holes)` falls through every
  storey cut under the drop to the first that is not, and `_vertical_links` passes it as `land_story`. A drop over an
  uncut floor lands on the floor below, as before.

### Added
- `test_hospital_shaft.py` (5, all fail on 0.231.1).

### Not changed
- Three library atriums cut holes no link declares -- bank, cbp_town_finale_midbalanced_schemafixed, final_stand --
  large guarded voids, not a shaft; the gate's guarded class is theirs.

'''


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(name):
    p = DC / name
    raw = p.read_bytes()
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == PINS[name], (f"{name} is not the file this patch read", got)
    assert b"\r\n" not in raw, f"{name} is LF"
    return p, raw.decode("utf-8")


def _test_plan():
    p = DC / "test_hospital_shaft.py"
    if p.exists():
        assert p.read_bytes() == TEST.encode("utf-8"), f"{p.name} exists and is not this patch's"
    return p


def write_tests(p=None):
    p = p or _test_plan()
    p.write_text(TEST, encoding="utf-8", newline="\n")
    print("wrote deli_counter/test_hospital_shaft.py")


def main(argv):
    if "--tests" in argv:
        write_tests()
        return 0
    pp, pt = _read("presets.py")
    assert "drop_landing" not in pt and "EVERY HOLE IN THE SHAFT DECLARED" not in pt, "already applied"
    pt = _once(pt, PRESET_OLD, PRESET_NEW, "the hospital's vertical links")
    lp, lt = _read("ladder.py")
    lt = _once(lt, LADDER_OLD, LADDER_NEW, "drop_nav_link's signature")
    lt = _once(lt, LADDER_DOC_OLD, LADDER_DOC_NEW, "drop_nav_link's landing")
    dp, dt = _read("deli_counter.py")
    dt = _once(dt, DC_OLD, DC_NEW, "_vertical_links' drop link")
    v = DC / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "Deli Counter 0.231.1", v.read_text(encoding="utf-8")
    cl = DC / "CHANGELOG.md"
    rawc = cl.read_bytes()
    eol = "\r\n" if rawc.count(b"\r\n") else "\n"
    ctext = rawc.decode("utf-8")
    assert ctext.startswith("## [0.231.1]"), ctext[:40]
    plan = _test_plan()
    pp.write_bytes(pt.encode("utf-8"))
    lp.write_bytes(lt.encode("utf-8"))
    dp.write_bytes(dt.encode("utf-8"))
    v.write_text("Deli Counter 0.232.0", encoding="utf-8")
    cl.write_bytes((CHANGELOG.replace("\n", eol) + ctext).encode("utf-8"))
    write_tests(plan)
    print("Deli Counter 0.232.0 applied: the hospital's shaft declared, drop_landing, tests, VERSION, CHANGELOG -- "
          "now build.py --all")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
