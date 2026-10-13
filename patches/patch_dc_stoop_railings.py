"""Deli Counter 0.212.0: a stoop's iron railings, one each side (factory roadmap 240; the walker's calls of
2026-10-13, "3 risers, concrete, railings both sides -- build the railings"; Zoo 1.105.0's `stoop_railing`).

Anchored edits, each asserted exactly once and every file's sha16 pinned, nothing written until all of
them matched:
  stoop.py                   the railings in the docstring; RAIL_H, RAIL_D, RAIL_INSET, RAIL_POST,
                             RAIL_BACK, RAIL_ROT_Y; `plan` -> `rails` (slot boxes, module dims,
                             colliders)
  deli_counter.py            `_stoop` records the railing slots, draws their greybox, writes their
                             colliders
  presets.py                 `empty_rowhome` declares `metal_painted` beside the stoop's concrete
  test_stoop.py              the railings' tests, appended
  test_stoop_circulation.py  the stoop's slots now include its railings
  specs/gs_empty_rowhome_*.json   regenerated from the patched presets (`json.dumps(indent=2)`, no
                             trailing newline), after asserting each is the CURRENT presets' output
CHANGELOG and VERSION from `dc_stoop_railings/CHANGELOG_0.212.0.md`; `--results-pending` leaves the
RESULT_ keys to `--fill`. The shells are rebuilt after (`build.py --all`).

Read before it was written, in this session: `stoop.py` and `_stoop` as 0.211.1 committed them,
`empty_rowhome`'s stoop block and an existing `metal_painted` palette entry (presets.py:2944),
`test_stoop.py`, `test_stoop_circulation.py`, `themed_tscn._fit_rotation` (the slot's own turn is tried
first, so a tie keeps it) and `tscn_export.godot_basis` (Ry(-t): `rot_y` 90 points a module's +X at
Godot +Z, the street; 270 at -Z, the house -- computed, not assumed), Zoo 1.105.0's
`stoop_railing_forms` (RAIL_H 36 in, the flight's rail RAIL_H over its box's bottom at the post's centre
and at its box's top at +X; the post 1-1/4 in), `agent_contract` (`min_corridor_width_m` 1.1). Read
again after a context reset, before it was applied: all five files at their pinned hashes and every
anchor; `_box`, `_col_box`, `_record_surface` and the volumes' slots (deli_counter.py:2521, the shape
these follow); `circulation.doorway_volume` (the aperture's own width across, 0.6 m out along the
wall's normal: the 1.0 m front door's volume ends 0.16 m short of either railing);
`portable_building.strip_greybox_base` (every collider stays; a visual goes when its name is a slot's
id, or that id and `_`); `zfight_gate.visible_fights` (a module read as its box; a pair under
`AREA_MIN` 0.05 m^2 skipped) -- which moved the railings `RAIL_INSET` in from the stoop's side: flush,
the flight's box and the middle tread's shared a plane facing one way over 0.0497 m^2. Every file LF.

    python patches/patch_dc_stoop_railings.py --results-pending
    (build.py --all; python -m pytest -q in deli_counter)
    python patches/patch_dc_stoop_railings.py --fill
"""
import hashlib
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
DC = pathlib.Path(os.environ.get("DC_ROOT") or HERE.parent / "deli_counter")
SRC = HERE / "dc_stoop_railings"
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_BUILD": "result_build.txt", "RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"Deli Counter 0.211.1", b"Deli Counter 0.212.0"
CHANGELOG_HEAD = "## [0.211.1] - a stoop is circulation, not a prop standing in it"
SHA = {"stoop.py": "4cf9d4ae3514972e", "deli_counter.py": "92a47baf09e82bce",
       "presets.py": "0cf65c4a7286e5af", "test_stoop.py": "1728ddd8559eb9d6",
       "test_stoop_circulation.py": "62fb999aaf6e3efb"}

STOOP_DOC_OLD = ("Frame: the building's -- x along the front, y back into the house, z up, the front wall `S` at\n"
                 "-footprint_y / 2. Pure: no Blender, so every number here is tested without a build.\n")
STOOP_DOC_NEW = (
    "THE RAILINGS (0.212.0, the walker's calls of 2026-10-13: \"railings both sides\"): one a side,\n"
    "`RAIL_INSET` inside the stoop's side, each Zoo's `stoop_railing` (1.105.0) in two slots -- a LEVEL\n"
    "section along the landing, from its front edge to the facade, and a FLIGHT from that edge down to a\n"
    "post on the bottom tread. Zoo draws either from its slot's box alone, its run along X and the high end\n"
    "at +X: a level's rail along the box's top; a flight's from `RAIL_H` over the box's bottom at its post\n"
    "to the box's top at the high end. So the boxes here ARE the railing: the level's bottom is the landing\n"
    "and its top `RAIL_H` over it; the flight's bottom is the bottom tread, its low end the post's outer\n"
    "face, its top `RAIL_H` over the landing at the landing's edge. Their colliders are written here, as\n"
    "the stoop's are: a box along the landing, and a slab whose top face is the flight's rail.\n"
    "\n"
    "Frame: the building's -- x along the front, y back into the house, z up, the front wall `S` at\n"
    "-footprint_y / 2. Pure: no Blender, so every number here is tested without a build.\n")

STOOP_CONST_OLD = ("#: the terrace's frontage a stoop must fit inside (`level_factory/packages/pipeline/empties.py`)\n"
                   "TERRACE_FRONTAGE = 2.0\n")
STOOP_CONST_NEW = (
    "#: the terrace's frontage a stoop must fit inside (`level_factory/packages/pipeline/empties.py`)\n"
    "TERRACE_FRONTAGE = 2.0\n"
    "#: THE RAILINGS (0.212.0). The rail's height over the walking line: IRC R311.7.8.1's 34-38 in, at 36\n"
    "#: -- Zoo's `stoop_railing_forms.RAIL_H`, the same source and the same number\n"
    "RAIL_H = round(36 * IN, 4)           # 0.9144 m\n"
    "#: the railing's depth across: Zoo's top rail, a 1-1/2 in flat bar\n"
    "RAIL_D = 0.038\n"
    "#: and how far inside the stoop's side it stands. Flush, a flight's box shares the middle tread's\n"
    "#: side plane, facing the same way, over a tread by a riser (0.2794 x 0.1778 = 0.0497 m^2); the\n"
    "#: composer's z-fight gate reads a module as its box and skips a pair under 0.05 m^2\n"
    "#: (`zfight_gate.AREA_MIN`), so it passed by 0.3 cm^2 -- one deeper tread from a flag. Inside it,\n"
    "#: no railing face lies on a step's\n"
    "RAIL_INSET = 0.05\n"
    "#: the post Zoo stands at a flight's low end (1-1/4 in square), its centre `RAIL_BACK` behind the\n"
    "#: bottom nosing, so it stands on the bottom tread\n"
    "RAIL_POST = round(1.25 * IN, 4)      # 0.0318 m\n"
    "RAIL_BACK = 0.05\n"
    "#: THE TURN. Zoo draws a railing's run along its X, the high end at +X; the composer turns a module\n"
    "#: by `tscn_export.godot_basis`, Ry(-t), so 270 points +X at Godot -Z -- Blender +Y, the house. 90\n"
    "#: would point every flight's rail down at the street. A thin railing's footprint ties 90 and 270, and\n"
    "#: the composer's fit keeps the slot's own turn on a tie (`themed_tscn._fit_rotation`).\n"
    "RAIL_ROT_Y = 270.0\n")

STOOP_PLAN_OLD = ("    out[\"ramp\"] = ((x, cy, cz), (width, length, RAMP_THICK), pitch)\n"
                  "    return out\n")
STOOP_PLAN_NEW = (
    "    out[\"ramp\"] = ((x, cy, cz), (width, length, RAMP_THICK), pitch)\n"
    "    # THE RAILINGS (0.212.0): `centre` and `size` in the building's frame, `dims` the module's (its\n"
    "    # run, its depth, its height), `collider` Deli Counter's\n"
    "    bottom_top = total - (n - 1) * riser               # the bottom tread's top\n"
    "    post_y = head - (n - 1) * tread + RAIL_BACK        # the flight's post, on the bottom tread\n"
    "    lo_y = post_y - RAIL_POST / 2.0                    # the flight's low end: the post's face\n"
    "    rails = []\n"
    "    for side, sgn in ((\"w\", -1.0), (\"e\", 1.0)):\n"
    "        rx = x + sgn * (width / 2.0 - RAIL_INSET - RAIL_D / 2.0)\n"
    "        run = face - head\n"
    "        centre = (rx, (head + face) / 2.0, total + RAIL_H / 2.0)\n"
    "        size = (RAIL_D, run, RAIL_H)\n"
    "        rails.append({\"name\": \"stoop_rail_%s_level\" % side, \"form\": \"level\",\n"
    "                      \"centre\": centre, \"size\": size, \"dims\": (run, RAIL_D, RAIL_H),\n"
    "                      \"collider\": (\"box\", centre, size)})\n"
    "        run = head - lo_y\n"
    "        z0, z1 = bottom_top, total + RAIL_H\n"
    "        # the rail: RAIL_H over the bottom tread at the post's centre, RAIL_H over the landing at its\n"
    "        # edge; the collider a slab under it, RAIL_H deep measured upright\n"
    "        r_run, r_drop = head - post_y, total - bottom_top\n"
    "        r_pitch = math.atan2(r_drop, r_run)\n"
    "        thick = RAIL_H * math.cos(r_pitch)\n"
    "        ym, zm = (post_y + head) / 2.0, (bottom_top + total) / 2.0 + RAIL_H\n"
    "        rails.append({\"name\": \"stoop_rail_%s_flight\" % side, \"form\": \"flight\",\n"
    "                      \"centre\": (rx, (lo_y + head) / 2.0, (z0 + z1) / 2.0),\n"
    "                      \"size\": (RAIL_D, run, z1 - z0), \"dims\": (run, RAIL_D, z1 - z0),\n"
    "                      \"collider\": (\"slab\", (rx, ym + (thick / 2.0) * math.sin(r_pitch),\n"
    "                                           zm - (thick / 2.0) * math.cos(r_pitch)),\n"
    "                                   (RAIL_D, math.hypot(r_run, r_drop), thick), r_pitch)})\n"
    "    out[\"rails\"] = rails\n"
    "    return out\n")

DC_OLD = ("        # its high end toward the house: local +Y up the flight\n"
          "        ramp.rotation_euler = (pitch, 0.0, 0.0)\n"
          "        self._record_surface(\"stoop_ramp\", mat)\n")
DC_NEW = (
    "        # its high end toward the house: local +Y up the flight\n"
    "        ramp.rotation_euler = (pitch, 0.0, 0.0)\n"
    "        self._record_surface(\"stoop_ramp\", mat)\n"
    "        # ITS RAILINGS (0.212.0): Zoo's `stoop_railing`, two slots a side, dressed\n"
    "        # as volumes are and turned so each flight rises to the house\n"
    "        # (`stoop.RAIL_ROT_Y`); and their colliders, Deli Counter's, so the\n"
    "        # greybox the graders walk has them as the art does\n"
    "        iron = \"metal_painted\"\n"
    "        iron_style = skin_style.style_for(iron, self._mat_style,\n"
    "                                          self.s.default_material)\n"
    "        for r in p[\"rails\"]:\n"
    "            c, size = r[\"centre\"], r[\"size\"]\n"
    "            self._box(r[\"name\"], c, size, self.VISUAL, role=\"prop\")\n"
    "            self.slots.append({\n"
    "                \"slot_id\": r[\"name\"], \"role\": \"prop\", \"size_mod\": \"full\",\n"
    "                \"style\": iron_style, \"material\": iron,\n"
    "                \"species\": \"stoop_railing\", \"stock\": None, \"variant\": 0,\n"
    "                \"form\": r[\"form\"],\n"
    "                \"current_ref\": \"prop_greybox_01\", \"kit_axis\": \"material\",\n"
    "                \"wall\": None, \"story\": None, \"facing\": None,\n"
    "                \"transform\": {\"translation\": [round(c[0], 4),\n"
    "                                              round(c[1], 4),\n"
    "                                              round(c[2], 4)],\n"
    "                              \"rot_y\": stoop.RAIL_ROT_Y,\n"
    "                              \"scale\": [1.0, 1.0, 1.0]},\n"
    "                \"fit\": {\"dims\": [round(v, 4) for v in r[\"dims\"]],\n"
    "                        \"pivot\": \"center\", \"openings\": [],\n"
    "                        \"collision\": \"none\"},\n"
    "            })\n"
    "            col = r[\"collider\"]\n"
    "            if col[0] == \"box\":\n"
    "                self._col_box(r[\"name\"] + \"_col\", col[1], col[2], mode=\"convex\")\n"
    "            else:\n"
    "                slab = self._box(r[\"name\"] + \"_col\" + self.col_suffix[\"convex\"],\n"
    "                                 col[1], col[2], self.COLLISION)\n"
    "                slab.rotation_euler = (col[3], 0.0, 0.0)\n"
    "            self._record_surface(r[\"name\"] + \"_col\", iron)\n")

PRESET_OLD = ("        if not any(m[\"id\"] == \"concrete\" for m in s[\"materials\"]):\n"
              "            s[\"materials\"].append({\"id\": \"concrete\", \"acoustic\": \"Concrete\",\n"
              "                                   \"absorption\": 0.7, \"damping\": 0.6})\n"
              "    return s\n")
PRESET_NEW = ("        if not any(m[\"id\"] == \"concrete\" for m in s[\"materials\"]):\n"
              "            s[\"materials\"].append({\"id\": \"concrete\", \"acoustic\": \"Concrete\",\n"
              "                                   \"absorption\": 0.7, \"damping\": 0.6})\n"
              "        # and its railings' iron (0.212.0)\n"
              "        if not any(m[\"id\"] == \"metal_painted\" for m in s[\"materials\"]):\n"
              "            s[\"materials\"].append({\"id\": \"metal_painted\", \"acoustic\": \"Metal\",\n"
              "                                   \"absorption\": 0.25, \"damping\": 0.2})\n"
              "    return s\n")

TEST_OLD = ("def test_the_stoop_s_concrete_is_declared():\n"
            "    for n in VARIANTS:\n"
            "        s = presets.empty_rowhome(name=n, **presets.EMPTY_ROWHOMES[n])\n"
            "        assert [m for m in s[\"materials\"] if m[\"id\"] == \"concrete\"], n\n")
TEST_NEW = TEST_OLD + '''

# THE RAILINGS (0.212.0): Zoo's stoop_railing, one a side in two sections

def test_every_stoop_has_a_railing_each_side_in_two_sections():
    for n in VARIANTS:
        p = stoop.plan(_spec(n))
        assert [r["name"] for r in p["rails"]] == [
            "stoop_rail_w_level", "stoop_rail_w_flight", "stoop_rail_e_level", "stoop_rail_e_flight"]
        assert [r["form"] for r in p["rails"]] == ["level", "flight"] * 2


def test_a_railing_stands_just_inside_the_stoop_s_side_and_leaves_the_way_up_wide():
    narrowest = agent_contract.contract()["clearances"]["min_corridor_width_m"]
    for n in VARIANTS:
        p = stoop.plan(_spec(n))
        xs = sorted({r["centre"][0] for r in p["rails"]})
        assert len(xs) == 2
        # each outer face RAIL_INSET inside the stoop's side
        assert abs((xs[0] - stoop.RAIL_D / 2) - (p["x"] - p["width"] / 2 + stoop.RAIL_INSET)) < 1e-9
        assert abs((xs[1] + stoop.RAIL_D / 2) - (p["x"] + p["width"] / 2 - stoop.RAIL_INSET)) < 1e-9
        # and the way up between them wider than the contract's narrowest corridor
        assert (xs[1] - xs[0]) - stoop.RAIL_D >= narrowest, (n, xs)


def _as_the_gate_reads_them(p, out=0.0):
    """The stoop's pieces and railings as the composer's z-fight gate reads a module -- its box,
    ``(name, (lo, hi))``. ``out`` moves each railing that far toward the stoop's side."""
    def box(c, s):
        return (tuple(c[i] - s[i] / 2 for i in range(3)), tuple(c[i] + s[i] / 2 for i in range(3)))
    boxes = [("stoop_landing", box(*p["landing"]))]
    boxes += [("stoop_tread_%d" % k, box(*t)) for k, t in enumerate(p["treads"], 1)]
    for r in p["rails"]:
        c = list(r["centre"])
        c[0] += out if c[0] > p["x"] else -out
        boxes.append((r["name"], box(c, r["size"])))
    return boxes


def test_no_railing_meets_a_step_face_to_face():
    """Flush with the stoop's side, a flight's box shared the middle tread's side plane, facing the
    same way, over a tread by a riser -- 0.0497 m^2, under the gate's 0.05 m^2 floor. Asked with no
    floor, the gate finds no railing in a pair a camera can reach; the control, each railing pushed
    flush, finds the two flights against the middle tread."""
    import zfight_gate
    for n in VARIANTS:
        p = stoop.plan(_spec(n))
        seen, _buried = zfight_gate.visible_fights(_as_the_gate_reads_them(p), area_min=0.0)
        assert not [f for f in seen if "rail" in f["a"] + f["b"]], (n, seen)
        flush, _buried = zfight_gate.visible_fights(
            _as_the_gate_reads_them(p, out=stoop.RAIL_INSET), area_min=0.0)
        assert sorted((f["a"], f["b"]) for f in flush) == [
            ("stoop_tread_1", "stoop_rail_e_flight"), ("stoop_tread_1", "stoop_rail_w_flight")], (n, flush)
        for f in flush:
            assert abs(f["area"] - round(p["tread"] * p["riser"], 3)) < 1e-9, f


def test_the_level_section_runs_the_landing_at_rail_height():
    for n in VARIANTS:
        p = stoop.plan(_spec(n))
        for r in (r for r in p["rails"] if r["form"] == "level"):
            (_x, y, z), (sx, sy, sz) = r["centre"], r["size"]
            assert abs((y - sy / 2) - p["head_y"]) < 1e-9 and abs((y + sy / 2) - p["face_y"]) < 1e-9
            assert abs((z - sz / 2) - p["rise"]) < 1e-9 and abs(sz - stoop.RAIL_H) < 1e-9
            # the module's dims: its run along its X
            assert r["dims"] == (sy, sx, sz)


def test_the_flight_runs_from_a_post_on_the_bottom_tread_to_the_landing():
    for n in VARIANTS:
        p = stoop.plan(_spec(n))
        bottom_top = p["rise"] - (p["risers"] - 1) * p["riser"]
        nosing = p["head_y"] - (p["risers"] - 1) * p["tread"]
        for r in (r for r in p["rails"] if r["form"] == "flight"):
            (_x, y, z), (sx, sy, sz) = r["centre"], r["size"]
            lo, hi = y - sy / 2, y + sy / 2
            assert abs(hi - p["head_y"]) < 1e-9
            # the post: its centre RAIL_BACK onto the bottom tread, wholly on it
            post = lo + stoop.RAIL_POST / 2
            assert abs(post - (nosing + stoop.RAIL_BACK)) < 1e-9
            assert nosing < lo and lo + stoop.RAIL_POST < nosing + p["tread"]
            # its foot on that tread, its top RAIL_H over the landing
            assert abs((z - sz / 2) - bottom_top) < 1e-9
            assert abs((z + sz / 2) - (p["rise"] + stoop.RAIL_H)) < 1e-9
            assert r["dims"] == (sy, sx, sz)
            # and it ends inside the stoop's depth, which the frontage holds
            assert p["face_y"] - lo < p["depth"]


def test_a_railing_turns_its_high_end_to_the_house():
    """Zoo draws a railing's run along its X, the high end at +X. The composer turns a module by
    `tscn_export.godot_basis` (Ry(-t)), so RAIL_ROT_Y must take +X to Godot -Z -- Blender +Y, into the
    house; 90 would point each flight's rail down at the street."""
    from tscn_export import godot_basis
    rows = godot_basis(stoop.RAIL_ROT_Y, [1.0, 1.0, 1.0])
    # the nine numbers are the matrix's rows: +X's image is its first column
    image = (rows[0], rows[3], rows[6])
    assert abs(image[0]) < 1e-9 and abs(image[1]) < 1e-9 and image[2] < -0.999, image
    wrong = godot_basis(90.0, [1.0, 1.0, 1.0])
    assert wrong[6] > 0.999


def test_the_flight_s_collider_rides_its_rail():
    for n in VARIANTS:
        p = stoop.plan(_spec(n))
        bottom_top = p["rise"] - (p["risers"] - 1) * p["riser"]
        for r in p["rails"]:
            kind = r["collider"][0]
            if r["form"] == "level":
                assert kind == "box" and r["collider"][1:] == (r["centre"], r["size"])
                continue
            assert kind == "slab"
            _k, (_cx, cy, cz), (sx, _length, thick), pitch = r["collider"]
            # the slab's top face: its centre moved up its normal by half its thickness
            ty, tz = cy - (thick / 2) * math.sin(pitch), cz + (thick / 2) * math.cos(pitch)

            def top_at(y):
                return tz + (y - ty) * math.tan(pitch)
            (_x, y, _z), (_sx, sy, _sz) = r["centre"], r["size"]
            post = y - sy / 2 + stoop.RAIL_POST / 2
            assert abs(top_at(post) - (bottom_top + stoop.RAIL_H)) < 1e-9
            assert abs(top_at(p["head_y"]) - (p["rise"] + stoop.RAIL_H)) < 1e-9
            # RAIL_H deep, measured upright; as thin as the railing
            assert abs(thick / math.cos(pitch) - stoop.RAIL_H) < 1e-9
            assert sx == stoop.RAIL_D


def test_the_rail_height_is_the_code_s():
    # IRC R311.7.8.1: 34 to 38 in, measured upright over the nosings' sloped plane; drawn at 36, as
    # Zoo's stoop_railing_forms draws it
    assert abs(stoop.RAIL_H - 36 * IN) < 1e-4
    for n in VARIANTS:
        p = stoop.plan(_spec(n))
        bottom_top = p["rise"] - (p["risers"] - 1) * p["riser"]
        for r in (r for r in p["rails"] if r["form"] == "flight"):
            (_x, y, _z), (_sx, sy, _sz) = r["centre"], r["size"]
            post = y - sy / 2 + stoop.RAIL_POST / 2
            # the rail runs straight from RAIL_H over the bottom tread at the post to RAIL_H over the
            # landing at its edge; the walked surface under it is the nosing line
            for t in (0.0, 0.25, 0.5, 0.75, 1.0):
                at = post + t * (p["head_y"] - post)
                over = bottom_top + stoop.RAIL_H + t * (p["rise"] - bottom_top) - stoop.surface_z(p, at)
                assert 34 * IN - 1e-9 <= over <= 38 * IN + 1e-9, (n, t, over)
            # lowest at the post, where it stands RAIL_BACK up the bottom tread: 34.75 in
            over = bottom_top + stoop.RAIL_H - stoop.surface_z(p, post)
            assert abs(over / IN - 34.75) < 0.01, (n, over / IN)


def test_the_railing_s_iron_is_declared():
    for n in VARIANTS:
        s = presets.empty_rowhome(name=n, **presets.EMPTY_ROWHOMES[n])
        assert [m for m in s["materials"] if m["id"] == "metal_painted"], n
'''

CIRC_OLD = ("    st = {s[\"slot_id\"]: s for s in slots[\"slots\"] if s[\"slot_id\"].startswith(\"stoop_\")}\n"
            "    assert sorted(st) == sorted(PIECES)\n"
            "    assert all(s[\"role\"] == \"prop\" and s[\"material\"] == \"concrete\" for s in st.values())\n")
CIRC_NEW = ("    st = {s[\"slot_id\"]: s for s in slots[\"slots\"] if s[\"slot_id\"] in PIECES}\n"
            "    assert sorted(st) == sorted(PIECES)\n"
            "    assert all(s[\"role\"] == \"prop\" and s[\"material\"] == \"concrete\" for s in st.values())\n"
            "    # and its railings (0.212.0): Zoo's stoop_railing in iron, two forms a side, props\n"
            "    # the gate reads and finds clear of the doorway\n"
            "    rails = {s[\"slot_id\"]: s for s in slots[\"slots\"] if s[\"slot_id\"].startswith(\"stoop_rail_\")}\n"
            "    assert sorted(rails) == sorted(RAILS)\n"
            "    assert all(s[\"species\"] == \"stoop_railing\" and s[\"material\"] == \"metal_painted\"\n"
            "               and s[\"form\"] in (\"level\", \"flight\") for s in rails.values())\n"
            "    assert all(roles.get(r) == \"prop\" for r in RAILS)\n"
            "    every = {s[\"slot_id\"] for s in slots[\"slots\"] if s[\"slot_id\"].startswith(\"stoop_\")}\n"
            "    assert every == set(PIECES) | set(RAILS)\n")
CIRC_CONST_OLD = "PIECES = (\"stoop_landing\", \"stoop_tread_1\", \"stoop_tread_2\")\n"
CIRC_CONST_NEW = ("PIECES = (\"stoop_landing\", \"stoop_tread_1\", \"stoop_tread_2\")\n"
                  "RAILS = (\"stoop_rail_w_level\", \"stoop_rail_w_flight\",\n"
                  "         \"stoop_rail_e_level\", \"stoop_rail_e_flight\")\n")

EDITS = {
    "stoop.py": [(STOOP_DOC_OLD, STOOP_DOC_NEW), (STOOP_CONST_OLD, STOOP_CONST_NEW),
                 (STOOP_PLAN_OLD, STOOP_PLAN_NEW)],
    "deli_counter.py": [(DC_OLD, DC_NEW)],
    "presets.py": [(PRESET_OLD, PRESET_NEW)],
    "test_stoop.py": [(TEST_OLD, TEST_NEW)],
    "test_stoop_circulation.py": [(CIRC_CONST_OLD, CIRC_CONST_NEW), (CIRC_OLD, CIRC_NEW)],
}

REGEN = (
    "import json, sys\n"
    "sys.path.insert(0, '.')\n"
    "import presets\n"
    "for n, a in sorted(presets.EMPTY_ROWHOMES.items()):\n"
    "    p = 'specs/%s.json' % n\n"
    "    data = json.dumps(presets.empty_rowhome(name=n, **a), indent=2).encode('utf-8')\n"
    "    if sys.argv[1] == 'check':\n"
    "        assert open(p, 'rb').read() == data, ('not the presets output', p)\n"
    "    else:\n"
    "        open(p, 'wb').write(data)\n"
    "print(sys.argv[1], len(presets.EMPTY_ROWHOMES), 'specs')\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def fill():
    assert (DC / "VERSION").read_bytes().strip() == VERSION, (DC / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(DC / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.212.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Deli Counter 0.212.0: results filled")


def main():
    if FILL:
        return fill()
    assert (DC / "VERSION").read_bytes().strip() == VERSION_WAS, (DC / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.212.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.212.0] - "), entry[:40]
    left = entry
    for key in RESULTS if PENDING else ():
        left = left.replace(key, "")
    assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    subprocess.run([sys.executable, "-c", REGEN, "check"], cwd=DC, check=True)
    writes = {}
    for rel, pairs in EDITS.items():
        p = DC / rel
        raw = p.read_bytes()
        got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
        assert got == SHA[rel], (rel, "is not the file this patch read", got)
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            assert text.count(old) == 1, (rel, "anchor", text.count(old), old[:80])
            text = text.replace(old, new)
        writes[p] = text.encode("utf-8").replace(b"\n", eol)
    cl = DC / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:120]
    # every anchor matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).encode("utf-8").replace(b"\n", cl_eol))
    (DC / "VERSION").write_bytes(VERSION)
    subprocess.run([sys.executable, "-c", REGEN, "write"], cwd=DC, check=True)
    print("Deli Counter 0.211.1 -> 0.212.0")


if __name__ == "__main__":
    main()
