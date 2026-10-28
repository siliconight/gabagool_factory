"""Lot 0.135.0: the drive-up as the research drew it, and the bank's outside pieces on their own surfaces. Run in a Lot
clone's root (on 0.134.0). Every anchor is asserted to occur exactly once; nothing is written on a miss.
"""
import pathlib

HERE = pathlib.Path(__file__).parent
R = pathlib.Path.cwd()


def edit(rel, pairs):
    p = R / rel
    t = p.read_bytes().decode("utf-8")
    crlf = "\r\n" in t
    t = t.replace("\r\n", "\n")
    for a, b in pairs:
        assert t.count(a) == 1, (rel, t.count(a), a[:80])
        t = t.replace(a, b)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print(p, "edited")


# site_driveup grows its lane pieces and its paint
p = R / "site_driveup.py"
t = p.read_bytes().decode("utf-8")
assert "def lane_pieces(" not in t and "\r\n" not in t
p.write_bytes((t.rstrip("\n") + "\n" + (HERE / "site_driveup_look.py").read_bytes().decode("utf-8")).encode("utf-8"))
print(p, "appended")

edit("lot.py", [
('''                   "drive_up_canopy": "metal", "drive_up_tube": "metal",
                   "night_drop": "metal",''',
 '''                   "drive_up_canopy": "metal_painted", "drive_up_tube": "metal_painted",
                   "night_drop": "metal_bare",
                   # ...on their own surfaces (0.135.0, Zoo 1.139.0): delco_1997's `metal` is
                   # `metal_rusted_street`, and the canopy's navy fascia read near black on it;
                   # and the lane's clearance bar and the bollards at its station
                   "clearance_bar": "metal_painted", "bollard": "metal_painted",'''),
('''    site_spec["cover"].extend(driveup_pieces)''',
 '''    # ...and each lane's clearance bar and the station's bollards (0.135.0)
    _du_roads = {r.index: r for r in _fs.roads(site_spec)}
    for _d in driveups:
        driveup_pieces += site_driveup.lane_pieces(_d, _du_roads[_d["road"]])
    site_spec["cover"].extend(driveup_pieces)'''),
('''    marks += list(_site_fields.markings(site_spec.get("fields") or [], street_roads))''',
 '''    marks += list(_site_fields.markings(site_spec.get("fields") or [], street_roads))
    # ...and a drive-up's: its island in safety yellow, an arrow on each lane (0.135.0)
    import site_driveup as _site_driveup
    marks += list(_site_driveup.markings(site_spec.get("driveups") or [], street_roads))'''),
])

edit("site_streets.py", [
('''        "markings": markings(rl) + _field_markings(site_spec, rl),''',
 '''        "markings": markings(rl) + _field_markings(site_spec, rl) + _driveup_markings(site_spec, rl),'''),
('''def manifest(site_spec, roads_list=None, findings=None) -> dict:''',
 '''def _driveup_markings(site_spec, rl):
    import site_driveup
    return site_driveup.markings(site_spec.get("driveups") or [], rl)


def manifest(site_spec, roads_list=None, findings=None) -> dict:'''),
])

edit("tests/test_bank_outside_materials.py", [
('''SPECIES = ("drive_up_canopy", "drive_up_tube", "night_drop", "price_pylon")''',
 '''SPECIES = ("drive_up_canopy", "drive_up_tube", "night_drop", "price_pylon", "clearance_bar", "bollard")'''),
])

dst = R / "tests" / "test_driveup_lane.py"
assert not dst.exists(), dst
dst.write_bytes((HERE / "test_driveup_lane.py").read_bytes())
print(dst, "written")
