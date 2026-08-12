"""The themed roof must carry the slab's holes -- the ladder into solid roof.

    python patch_dc_roof_voids.py --check      # verify targets, write nothing
    python patch_dc_roof_voids.py              # apply
    python patch_dc_roof_voids.py --revert     # restore from the .pre_roofvoid sidecars

Measured on `bank_branch_a04`, from the 2026-08-09 run's own walkbot.json:

    "blocker": "Roof", "blocker_rel_y": 3.9, "aperture_z": [],
    "climb": false, "climb_height_reached": 2.1

The ladder runs storey 1 -> 2 in a 4.2 m storey, so its base is world y 4.2 and
the top slab spans 8.10..8.40. `blocker_rel_y 3.9` is world 8.10 -- the slab
underside, exact. `blocker` was present, so that figure was measured, not the
probe's `rel.y + 1.0` fallback.

DELI COUNTER CUT THE HOLE. `slab_col_2-colonly` in the shipped `site_base.glb`
carries 76 vertices (a box has 8) with corners at x 15.45 / 16.55 and z -10.90 --
exactly `ladder_geom.through_hole(16, 12, 0.5, "S")`. And no node named `Roof`
exists among that file's 762. The collider the bot hit is the art pass's
`roof_rockay_01_w4000.glb`, instanced as `roof_footprint`: a 40 m plate with
`collision: trimesh` and no void, laid over a correctly cut slab.

TWO CAUSES, BOTH FIXED HERE:

  1. `roofs._slot` had no `voids` key at all -- only `"openings": []`, which is
     the WALL contract and the wrong shape. A roof slot could not express a
     hole. `floors._slot` has carried `voids` since the floor/ceiling skins were
     given theirs; the roof never was.
  2. `_record_roof_slots` was called from `_slabs()` -- build step ONE. `_ladders`
     does not append a hole until step five and `_slab_holes_cut` runs at step
     eleven, so `spec.slab_holes` was empty by construction when the roof slot
     was derived. It now sits beside `_record_slab_slots`, after the cut, whose
     comment has said exactly why since it was written.

Simulated with the real functions in the real order, no Blender:

    OLD ORDER (_slabs -> roof slot, then _ladders):  voids = []
    NEW ORDER (_ladders -> cut -> roof slot):
        voids = [{x0: 15.45, y0: 10.9, x1: 16.55, y1: 12.2}]

-- which is the hole already measured in the slab, to the centimetre.

WHY FIVE GATES PASSED. L14 checks the hole against the footprint, L15 checks
partitions crossing it, the compose gate counts climb volumes, `test_ladder_geom`
checks the hole's geometry, `nav_gate` bakes the greybox. Every one checks Deli
Counter's own geometry, which was correct. Nothing checked that what is laid ON
the slab preserves the opening. This is greybox-clean and themed-broken, so
"the ladder used to work" is true and nothing regressed.

VERIFYING NEEDS A REBUILD. The pure half is tested here -- 7 new cases in
test_roofs.py, all failing on the pre-patch file with `KeyError: 'voids'`. The
builder half needs Blender, and the level needs a full --art run and a walk.

REFUSES on any target whose bytes are not what this patch was written against --
a whole-file SHA-256, so a drifted file cannot be half-patched, and nothing is
written unless every target verifies.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

SIDECAR = ".pre_roofvoid"
ROOT = Path(__file__).resolve().parent

TARGETS = [
    {
        "rel": 'deli_counter/roofs.py',
        "pre_sha": '21aff6af024d4ab0407bf8433cf6a2d9df3beef1049d5ae6652bb5823a9a6cd5',
        "post_sha": 'dc11dfa559936fd5ca2c5717f1ca1a4b65e90dadb9164ac51d3370f05bd1cc48',
        "pre_bytes": 2823, "post_bytes": 5200,
        "hunks": [
            ('\nTransforms are raw spec/Blender Z-up coords, same as the wall slots; rot_y is\ndegrees about up. A roof slot is a wall slot laid flat: facing "up", rot_y 0,\ncenter pivot, unit scale (themed art is exact-fit, never stretched).\n"""\n\nROOF_SLOT_ROLE = "roof"\nGREYBOX_REF = "roof_greybox_01"\n\n\ndef _slot(sid, story, cx, cy, cz, sx, sy, ft, room=None, style=1,\n          material=None):\n    return {\n        "slot_id": sid, "role": ROOF_SLOT_ROLE, "size_mod": "full",\n        "style": style, "material": material,\n        "current_ref": GREYBOX_REF, "kit_axis": "theme",\n        "wall": None, "story": story, "facing": "up", "room": room,\n        "transform": {"translation": [round(cx, 4), round(cy, 4), round(cz, 4)],\n                      "rot_y": 0, "scale": [1.0, 1.0, 1.0]},\n        "fit": {"dims": [round(sx, 4), round(sy, 4), round(ft, 4)],\n                "pivot": "center", "openings": [], "collision": "trimesh"},\n    }\n\n\ndef roof_slots(spec, story, cz, ft):\n    """Return the roof swap-slots for the top story.\n\n    spec  -- a LevelSpec (reads footprint_x/y, roof_mode, rooms).\n    story -- top story index (roof level).\n    cz    -- slab center Z (raw Blender coords).\n    ft    -- roof thickness.\n\n    "footprint" -> one slot over the whole plan.\n    "per_room"  -> one slot per top-story room with room.roofed (open-air rooms\n                   opt out).\n    """\n    # roof skin style follows the spec\'s default material (skin_style.py) --\n    # same axis every other slot varies on.\n    import skin_style\n    mat = getattr(spec, "default_material", None)\n    mapping = skin_style.material_styles(\n        [m.id for m in getattr(spec, "materials", [])])\n    style = skin_style.style_for(mat, mapping, mat)\n    if getattr(spec, "roof_mode", "footprint") == "per_room":\n        out = []\n        for r in spec.rooms:\n            if r.story == story and getattr(r, "roofed", True):\n                b = r.bounds\n                out.append(_slot(f"roof_{r.id}", story,\n                                 (b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0, cz,\n                                 b[2] - b[0], b[3] - b[1], ft, room=r.id,\n                                 style=style, material=mat))\n        return out\n    return [_slot("roof_footprint", story, 0.0, 0.0, cz,\n                  spec.footprint_x, spec.footprint_y, ft,\n                  style=style, material=mat)]\n',
             '\nTransforms are raw spec/Blender Z-up coords, same as the wall slots; rot_y is\ndegrees about up. A roof slot is a wall slot laid flat: facing "up", rot_y 0,\ncenter pivot, unit scale (themed art is exact-fit, never stretched).\n\nTHE ROOF CARRIES THE SLAB\'S HOLES, and until 2026-08-09 it did not. A roof slot\nis not a skin: its `fit.dims` is the slab\'s real thickness and its collision is\n`trimesh`, so the themed module IS a collider spanning the whole plan. A floor\nor ceiling skin that forgot a void is a cosmetic fault; a roof that forgets one\nis a wall. Measured on `bank_branch_a04`: Deli Counter cut the roof-slab hole\nexactly where `ladder_geom.through_hole` says (verified in `slab_col_2-colonly`,\ncorners 15.45/16.55/-10.90), the art pass laid `roof_rockay_01_w4000.glb` over\nit with no void, and the walk bot\'s ladder stalled against a collider named\n`Roof` at the slab underside -- a ladder rising a full storey into solid roof.\nEvery gate passed, because every gate checks the slab and none checks what is\nlaid on it.\n"""\n\nROOF_SLOT_ROLE = "roof"\nGREYBOX_REF = "roof_greybox_01"\n\n\ndef _slot(sid, story, cx, cy, cz, sx, sy, ft, room=None, style=1,\n          material=None, voids=None):\n    return {\n        "slot_id": sid, "role": ROOF_SLOT_ROLE, "size_mod": "full",\n        "style": style, "material": material,\n        "current_ref": GREYBOX_REF, "kit_axis": "theme",\n        "wall": None, "story": story, "facing": "up", "room": room,\n        "transform": {"translation": [round(cx, 4), round(cy, 4), round(cz, 4)],\n                      "rot_y": 0, "scale": [1.0, 1.0, 1.0]},\n        "fit": {"dims": [round(sx, 4), round(sy, 4), round(ft, 4)],\n                "pivot": "center", "openings": [], "collision": "trimesh",\n                # Rectangular holes in the PLATE\'s own x/y, cut by\n                # core.arch.plate_parts -- the same key and the same shape\n                # `floors._slot` emits, and named `voids` for the reason stated\n                # there: `openings` is the WALL contract, a hole in a standing\n                # slab\'s x/z, and the two are not the same shape.\n                "voids": list(voids or ())},\n    }\n\n\ndef roof_slots(spec, story, cz, ft):\n    """Return the roof swap-slots for the top story.\n\n    spec  -- a LevelSpec (reads footprint_x/y, roof_mode, rooms, slab_holes).\n    story -- top story index (roof level).\n    cz    -- slab center Z (raw Blender coords).\n    ft    -- roof thickness.\n\n    "footprint" -> one slot over the whole plan.\n    "per_room"  -> one slot per top-story room with room.roofed (open-air rooms\n                   opt out).\n\n    ORDER OF CALL IS PART OF THE CONTRACT. `spec.slab_holes` is appended DURING\n    the build by `_stairs`, `_ladders`, `_ramps` and `_vertical_links`, so this\n    must be called after them -- `Builder._record_roof_slots` sits beside\n    `_record_slab_slots`, after `_slab_holes_cut`, for exactly that reason. It\n    used to be called from `_slabs()`, the first build step, where\n    `slab_holes` is always empty and a roof could not have carried a hole even\n    if it had asked for one.\n    """\n    # roof skin style follows the spec\'s default material (skin_style.py) --\n    # same axis every other slot varies on.\n    import skin_style\n    # The clip is floors\' -- one definition of "which holes land on this rect",\n    # imported rather than restated, the same rule `ladder_geom` states for the\n    # hole itself. `room_voids` clips to the rect it is handed and never reads\n    # its `room` argument, so it is already the general function this needs.\n    from floors import room_voids\n    mat = getattr(spec, "default_material", None)\n    mapping = skin_style.material_styles(\n        [m.id for m in getattr(spec, "materials", [])])\n    style = skin_style.style_for(mat, mapping, mat)\n    if getattr(spec, "roof_mode", "footprint") == "per_room":\n        out = []\n        for r in spec.rooms:\n            if r.story == story and getattr(r, "roofed", True):\n                b = r.bounds\n                cx, cy = (b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0\n                sx, sy = b[2] - b[0], b[3] - b[1]\n                out.append(_slot(f"roof_{r.id}", story, cx, cy, cz,\n                                 sx, sy, ft, room=r.id,\n                                 style=style, material=mat,\n                                 voids=room_voids(spec, r, story,\n                                                  cx, cy, sx, sy)))\n        return out\n    return [_slot("roof_footprint", story, 0.0, 0.0, cz,\n                  spec.footprint_x, spec.footprint_y, ft,\n                  style=style, material=mat,\n                  voids=room_voids(spec, None, story, 0.0, 0.0,\n                                   spec.footprint_x, spec.footprint_y))]\n'),
        ],
    },
    {
        "rel": 'deli_counter/deli_counter.py',
        "pre_sha": '3ec50a0b9c4c21b1cc094d3787399fc88997e98ed1a200506c9f2398a8bec6df',
        "post_sha": 'f4b797e4fc2e364adf2b48ee9eeaad6272ce163e2d973bfac13aa9d067d4478e',
        "pre_bytes": 125456, "post_bytes": 127164,
        "hunks": [
            ('        self._slab_holes_cut()\n        # Immediately after the cut, and for the same reason: by here every\n        # stairwell, ramp and hatch has appended its hole, so a floor or\n        # ceiling skin can be given the same openings the slab just got.\n        if self._modular_on():\n            self._record_slab_slots()\n        self._volumes()\n        self._placements()\n        self._parapets()\n',
             "        self._slab_holes_cut()\n        # Immediately after the cut, and for the same reason: by here every\n        # stairwell, ramp and hatch has appended its hole, so a floor or\n        # ceiling skin can be given the same openings the slab just got.\n        #\n        # THE ROOF IS HERE TOO NOW, and it is the one that mattered. A floor or\n        # ceiling skin is `collision: none` -- a forgotten void there is a thing\n        # you see through and walk through. The roof slot is the slab's real\n        # thickness with `collision: trimesh`, so a forgotten void there is a\n        # wall. Roof first, so the slot order inside this block still reads\n        # roof, then floors and ceilings, as it did when `_slabs` emitted it.\n        if self._modular_on():\n            self._record_roof_slots()\n            self._record_slab_slots()\n        self._volumes()\n        self._placements()\n        self._parapets()\n"),
            ('            # the hole. The roof keeps collision even when its visual is hidden.\n            self._col_box(f"slab_col_{s}", (0, 0, z - ft / 2),\n                          (self.s.footprint_x, self.s.footprint_y, ft),\n                          mode="trimesh")\n            # ALWAYS emit the roof as an art-pass swap-slot (when modular) so\n            # Zoo can dress it -- present even in "open" mode, since the slot is\n            # the always-there hook that lets a roof be added after the fun test.\n            if is_roof and self._modular_on():\n                self._record_roof_slots(top, z - ft / 2, ft)\n\n    def _record_slab_slots(self):\n        """Emit the per-room floor and ceiling swap-slots (floors.slab_slots --\n        pure & tested), so Zoo can skin what a player stands on and looks up at.\n',
             '            # the hole. The roof keeps collision even when its visual is hidden.\n            self._col_box(f"slab_col_{s}", (0, 0, z - ft / 2),\n                          (self.s.footprint_x, self.s.footprint_y, ft),\n                          mode="trimesh")\n            # The roof swap-slot is NOT emitted here any more -- see\n            # `_record_roof_slots`, now called next to `_record_slab_slots`\n            # after the holes are cut. Emitting it from this loop meant it was\n            # derived in build step ONE, before `_ladders` had appended a\n            # single hole, so a roof could never carry one.\n\n    def _record_slab_slots(self):\n        """Emit the per-room floor and ceiling swap-slots (floors.slab_slots --\n        pure & tested), so Zoo can skin what a player stands on and looks up at.\n'),
            ('        """\n        _base, top = self._story_range()\n        self.slots.extend(floors.slab_slots(self.s, top))\n\n    def _record_roof_slots(self, story, cz, ft):\n        """Emit the roof swap-slots (see roofs.roof_slots -- pure & tested) so\n        Zoo can dress the roof. footprint = one slot; per_room = one per\n        top-story room honoring Room.roofed."""\n        self.slots.extend(roofs.roof_slots(self.s, story, cz, ft))\n\n    def _cap_thick(self, story, top):\n        """Thickness of the slab that caps `story` -- the one whose top face is\n        the floor of story+1, so the wall below must stop at its underside.\n',
             '        """\n        _base, top = self._story_range()\n        self.slots.extend(floors.slab_slots(self.s, top))\n\n    def _record_roof_slots(self):\n        """Emit the roof swap-slots (see roofs.roof_slots -- pure & tested) so\n        Zoo can dress the roof. footprint = one slot; per_room = one per\n        top-story room honoring Room.roofed.\n\n        CALLED FROM THE BUILD SEQUENCE, AFTER `_slab_holes_cut`, for the same\n        reason `_record_slab_slots` is -- and it was not, which is the defect.\n        It ran inside `_slabs()`, build step one, where `self.s.slab_holes` is\n        empty by construction; `_ladders` does not append until step five. So\n        the roof slot was derived before any hole existed, Zoo built a solid\n        plate for it, and the plate has `collision: trimesh` over the whole\n        plan. Measured on `bank_branch_a04`: the roof slab itself was cut\n        correctly and the themed roof laid over it was not, so a ladder climbed\n        a full storey into a collider named `Roof`.\n\n        Takes its own geometry rather than the loop\'s, so the call site does not\n        have to sit where the slabs are built. `roof == "none"` emits nothing --\n        there is no roof to dress -- while `"open"` still does, because the slot\n        is the always-there hook that lets a roof be added after the fun test.\n        """\n        if self.s.roof == "none":\n            return\n        _base, top = self._story_range()\n        ft = self.s.roof_thick or self.s.floor_thick\n        self.slots.extend(roofs.roof_slots(\n            self.s, top, top * self.s.story_height - ft / 2, ft))\n\n    def _cap_thick(self, story, top):\n        """Thickness of the slab that caps `story` -- the one whose top face is\n        the floor of story+1, so the wall below must stop at its underside.\n'),
        ],
    },
    {
        "rel": 'deli_counter/test_roofs.py',
        "pre_sha": '87e1a5d30e9ace94bf8ff57218409ccbc1e7cf6ead5e1dff02e4cd4a78471951',
        "post_sha": '93a717d3df4af78a7bb4a3933fb1ad40c3bcc6276f6fffaae316e89480ae15c6',
        "pre_bytes": 2216, "post_bytes": 7382,
        "hunks": [
            ('    b = roofs.roof_slots(sp, 1, 4.35, 0.2)\n    assert a == b and a[0]["slot_id"] == "roof_vault"\n\n\nif __name__ == "__main__":\n    _run(test_footprint_single_slot)\n    _run(test_per_room_and_roofed_optout)\n    _run(test_per_room_all_open_is_empty)\n    _run(test_stable_slot_ids)\n    print("\\nall roof tests passed")\n',
             '    b = roofs.roof_slots(sp, 1, 4.35, 0.2)\n    assert a == b and a[0]["slot_id"] == "roof_vault"\n\n\n\n\n# --------------------------------------------------------------------------- #\n# The roof carries the slab\'s holes (2026-08-09)\n#\n# A roof slot is NOT a skin. `fit.dims` is the slab\'s real thickness and\n# `collision` is `trimesh`, so the themed module is a collider spanning the\n# whole plan. A floor or ceiling skin that forgets a void looks wrong; a roof\n# that forgets one IS a wall -- which is what a ladder in `bank_branch_a04` rose\n# a full storey into.\n# --------------------------------------------------------------------------- #\n\nclass _Hole:\n    """Same stand-in `test_floors` uses -- spec_types.SlabHole\'s four fields."""\n\n    def __init__(self, story, x, y, sx, sy):\n        self.story, self.x, self.y = story, x, y\n        self.size_x, self.size_y = sx, sy\n\n\ndef test_a_roof_over_nothing_has_no_voids():\n    """THE CLEAN CASE, asserted on purpose. "It cut the hole for the broken\n    building" cannot tell you it would not also punch one in a solid roof, and\n    only the clean report has any value -- the lesson `module_extents --kit`\n    paid for with a Z-up fixture that agreed with a Y-up reader."""\n    sp = LevelSpec(name="s", footprint_x=32, footprint_y=22,\n                   roof_mode="footprint")\n    slots = roofs.roof_slots(sp, story=1, cz=4.35, ft=0.2)\n    assert slots[0]["fit"]["voids"] == []\n\n\ndef test_a_slab_hole_at_the_roof_storey_reaches_the_roof_slot():\n    sp = LevelSpec(name="s", footprint_x=40, footprint_y=30,\n                   roof_mode="footprint")\n    sp.slab_holes = [_Hole(2, 16.0, 11.55, 1.1, 1.3)]\n    slots = roofs.roof_slots(sp, story=2, cz=8.25, ft=0.3)\n    assert slots[0]["fit"]["voids"] == [\n        {"x0": 15.45, "y0": 10.9, "x1": 16.55, "y1": 12.2}]\n\n\ndef test_a_hole_through_a_lower_slab_is_not_the_roofs():\n    """`slab_holes` carries every storey\'s openings. A stairwell through\n    storey 1 must not punch the roof."""\n    sp = LevelSpec(name="s", footprint_x=40, footprint_y=30,\n                   roof_mode="footprint")\n    sp.slab_holes = [_Hole(1, 4.0, -6.0, 3.0, 4.0)]\n    slots = roofs.roof_slots(sp, story=2, cz=8.25, ft=0.3)\n    assert slots[0]["fit"]["voids"] == []\n\n\nclass _BareSpec:\n    """A spec object with no `slab_holes` attribute at all -- the stand-in\n    `test_floors` uses for the same guarantee. `LevelSpec` defaults the field to\n    a list, so it cannot express this case and the `getattr` guard would go\n    untested against it."""\n\n    roof_mode = "footprint"\n    footprint_x, footprint_y = 32.0, 22.0\n    rooms, materials = (), ()\n    default_material = None\n\n\ndef test_a_spec_with_no_slab_holes_attribute_still_slots():\n    sp = _BareSpec()\n    assert not hasattr(sp, "slab_holes")\n    assert roofs.roof_slots(sp, story=1, cz=4.35, ft=0.2)[0]["fit"]["voids"] == []\n\n\ndef test_per_room_roofs_each_take_only_their_own_holes():\n    sp = LevelSpec(name="s", roof_mode="per_room", rooms=[\n        Room(id="west", story=2, bounds=[-16, -11, 0, 11]),\n        Room(id="east", story=2, bounds=[0, -11, 16, 11]),\n    ])\n    sp.slab_holes = [_Hole(2, 8.0, 0.0, 2.0, 2.0)]      # inside `east` only\n    slots = {s["slot_id"]: s for s in roofs.roof_slots(sp, 2, 8.25, 0.3)}\n    assert slots["roof_west"]["fit"]["voids"] == []\n    assert len(slots["roof_east"]["fit"]["voids"]) == 1\n\n\ndef test_a_hole_outside_every_roofed_room_is_dropped_not_clamped():\n    sp = LevelSpec(name="s", roof_mode="per_room",\n                   rooms=[Room(id="hall", story=2, bounds=[-5, -5, 5, 5])])\n    sp.slab_holes = [_Hole(2, 100.0, 100.0, 2.0, 2.0)]\n    assert roofs.roof_slots(sp, 2, 8.25, 0.3)[0]["fit"]["voids"] == []\n\n\ndef test_the_bank_branch_ladder_gets_out_onto_the_roof():\n    """THE REGRESSION, with the numbers off the shipped building.\n\n    `bank_branch_a04`: 40 x 30 footprint, storey 4.2, roof at storey 2, one\n    ladder at spec (16, 12) width 0.5 facing S climbing storey 1 -> 2. The walk\n    bot stalled against a collider named `Roof` at ladder-local 3.90 -- world\n    8.10, the exact underside of a slab spanning 8.10..8.40 -- with\n    `aperture_z: []`, no opening anywhere across the sweep.\n\n    The hole itself was never in doubt: `slab_col_2-colonly` carries it, corners\n    15.45/16.55/-10.90, exactly where `ladder_geom.through_hole` puts it. So\n    this asserts the OTHER half -- that the roof slot laid over that slab asks\n    for the same rectangle, and that the rectangle admits the climbing capsule.\n    """\n    import ladder_geom\n    hx, hy, hsx, hsy = ladder_geom.through_hole(16.0, 12.0, 0.5, "S")\n    sp = LevelSpec(name="bank_branch_a04", footprint_x=40, footprint_y=30,\n                   n_stories=2, story_height=4.2, roof_mode="footprint")\n    sp.slab_holes = [_Hole(2, hx, hy, hsx, hsy)]\n    void = roofs.roof_slots(sp, story=2, cz=8.25, ft=0.3)[0]["fit"]["voids"][0]\n\n    # the climb column the capsule needs: CLIMB_STANDOFF +/- capsule radius,\n    # measured from the ladder face along the APPROACH direction (facing S =\n    # -y), and the ladder\'s own width across it.\n    standoff, capsule_r = ladder_geom.CLIMB_STANDOFF, 0.35\n    assert void["y0"] <= 12.0 - (standoff + capsule_r)\n    assert void["y1"] >= 12.0 - (standoff - capsule_r)\n    assert void["x0"] <= 16.0 - 0.25 and void["x1"] >= 16.0 + 0.25\n\n\n\nif __name__ == "__main__":\n    for _name, _fn in sorted(globals().items()):\n        if _name.startswith("test_"):\n            _run(_fn)\n    print("\\nall roof tests passed")\n'),
        ],
    },
]

NEW_FILES = {}


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _write(p: Path, text: str) -> None:
    p.write_text(text, encoding="utf-8", newline="")


def check(verbose: bool = True):
    """(ok, todo) -- every target read and hashed, nothing written."""
    ok, todo = True, []
    for t in TARGETS:
        p = ROOT / t["rel"]
        if not p.is_file():
            print(f"  MISSING   {t['rel']}")
            ok = False
            continue
        cur = _read(p)
        got = _sha(cur)
        if got == t["post_sha"]:
            print(f"  already   {t['rel']}")
            continue
        if got != t["pre_sha"]:
            print(f"  DRIFTED   {t['rel']}")
            print(f"            expected {t['pre_bytes']} bytes "
                  f"sha {t['pre_sha'][:16]}")
            print(f"            found    {len(cur.encode('utf-8'))} bytes "
                  f"sha {got[:16]}")
            ok = False
            continue
        todo.append((p, t, cur))
        if verbose:
            print(f"  ready     {t['rel']}  ({len(t['hunks'])} hunk(s), "
                  f"{t['pre_bytes']} -> {t['post_bytes']} bytes)")
    for rel in NEW_FILES:
        p = ROOT / rel
        state = "exists (will not overwrite)" if p.is_file() else "will create"
        print(f"  new file  {rel}  -- {state}")
    return ok, todo


def apply() -> int:
    print("checking every target before writing anything")
    ok, todo = check()
    if not ok:
        print("\nREFUSED. At least one target is not the file this patch was "
              "written against; nothing has been written.")
        return 1
    for p, t, cur in todo:
        side = p.with_name(p.name + SIDECAR)
        if not side.exists():
            _write(side, cur)
        out = cur
        for old, new in t["hunks"]:
            if out.count(old) != 1:
                print(f"REFUSED mid-file on {t['rel']} -- anchor not unique. "
                      f"Restore from {side.name} and re-read.")
                return 1
            out = out.replace(old, new, 1)
        if _sha(out) != t["post_sha"]:
            print(f"REFUSED on {t['rel']} -- result does not match the "
                  f"expected post-image. Nothing further written.")
            return 1
        _write(p, out)
        print(f"  patched   {t['rel']}  ({side.name} written)")
    for rel, body in NEW_FILES.items():
        p = ROOT / rel
        if p.is_file():
            print(f"  kept      {rel} (already present, not overwritten)")
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        _write(p, body)
        print(f"  created   {rel}")
    print("\nNow run, from deli_counter/:  python test_roofs.py")
    print("Expected: all pure suites green; test_roofs.py gains 7 cases.")
    return 0


def revert() -> int:
    n = 0
    for t in TARGETS:
        p = ROOT / t["rel"]
        side = p.with_name(p.name + SIDECAR)
        if not side.is_file():
            continue
        body = _read(side)
        if _sha(body) != t["pre_sha"]:
            print(f"  REFUSED   {t['rel']} -- {side.name} is not the "
                  f"pre-image this patch recorded")
            continue
        _write(p, body)
        side.unlink()
        n += 1
        print(f"  reverted  {t['rel']}")
    for rel in NEW_FILES:
        p = ROOT / rel
        if p.is_file() and _sha(_read(p)) == _sha(NEW_FILES[rel]):
            p.unlink()
            print(f"  removed   {rel}")
    print(f"\n{n} file(s) restored.")
    return 0


def main(argv):
    if "--check" in argv:
        ok, _ = check()
        print("\nOK to apply." if ok else "\nNOT ok to apply.")
        return 0 if ok else 1
    if "--revert" in argv:
        return revert()
    return apply()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
