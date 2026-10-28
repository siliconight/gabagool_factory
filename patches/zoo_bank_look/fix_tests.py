"""Zoo 1.139.0, part three: the tests and genomes follow the new pieces. Run in a Zoo clone's root, after the other two
edits and after `tools/new_species.py new clearance_bar` (shaped by hand)."""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
R = pathlib.Path.cwd()


def edit(rel, pairs):
    p = R / rel
    t = p.read_bytes().decode("utf-8")
    for a, b in pairs:
        assert t.count(a) == 1, (rel, t.count(a), a[:80])
        t = t.replace(a, b)
    p.write_bytes(t.encode("utf-8"))
    print(p, "edited")


def parts(species, new):
    g = R / "zoo_keeper" / "genome" / "species" / (species + ".json")
    raw = g.read_bytes()
    d = json.loads(raw)
    assert (json.dumps(d, indent=2) + "\n").encode() == raw
    d["parts"] = new
    g.write_bytes((json.dumps(d, indent=2) + "\n").encode())
    print(g, new)


# the clearance bar in the minted registry, as `tools/new_species.py new clearance_bar` wrote it (a sorted list)
mj = R / "zoo_keeper" / "genome" / "minted.json"
raw = mj.read_bytes()
names = json.loads(raw)
assert (json.dumps(names, indent=2) + "\n").encode() == raw and "clearance_bar" not in names
mj.write_bytes((json.dumps(sorted(names + ["clearance_bar"]), indent=2) + "\n").encode())
print(mj, "+ clearance_bar")

parts("drive_up_canopy", ["DriveUpCanopy_Deck", "DriveUpCanopy_Soffit", "DriveUpCanopy_Footing", "DriveUpCanopy_Column",
                          "DriveUpCanopy_Chase", "DriveUpCanopy_Board"])
parts("drive_up_tube", ["DriveUp_Island", "DriveUp_Cabinet", "DriveUp_Mouth", "DriveUp_Hood", "DriveUp_Screen",
                        "DriveUp_Grille", "DriveUp_Button", "DriveUp_Collar", "DriveUp_Tube"])

edit("tests/test_drive_up_canopy.py", [
('''    tube = [parts["DriveUpCanopy_Tube"].matrix_world @ v.co for v in parts["DriveUpCanopy_Tube"].data.vertices]
    assert (min(p.z for p in tube) + max(p.z for p in tube)) / 2.0 - lo[2] == pytest.approx(C.run_z(dims[2]), abs=1e-3)
    # the run reaches the wall at -X
    assert min(p.x for p in tube) == pytest.approx(lo[0], abs=1e-3)''',
 '''    # the run in its chase (1.139.0): the chase's underside half its section under the run's centre, where the
    # station's tube rises to; the chase reaches the wall at -X
    chase = [parts["DriveUpCanopy_Chase"].matrix_world @ v.co for v in parts["DriveUpCanopy_Chase"].data.vertices]
    assert min(p.z for p in chase) - lo[2] == pytest.approx(C.run_z(dims[2]) - C.CHASE / 2.0, abs=1e-3)
    assert min(p.x for p in chase) == pytest.approx(lo[0], abs=1e-3)
    # DRIVE-UP on both ends, the boards' fronts the module's ends
    art = [o for o in meshes if o.name.startswith("DriveUpCanopy_Board")]
    assert art, sorted(parts)
    ys = [(o.matrix_world @ v.co).y for o in art for v in o.data.vertices]
    assert min(ys) == pytest.approx(lo[1], abs=1e-3) and max(ys) == pytest.approx(lo[1] + dims[1], abs=1e-3)'''),
('''    assert len({s.material.name for o in meshes for s in o.material_slots}) == 1''',
 '''    # the steel on one material, the boards' lettering on one atlas
    assert len({s.material.name for o in meshes for s in o.material_slots}) == 2'''),
])

t = (R / "tests" / "test_coincident_faces.py").read_bytes().decode()
a = "CENSUS_BUILDS = 444"
assert t.count(a) == 1
t = t.replace(a, '''#: 1.139.0: `clearance_bar` (the drive-up's research), three builds more, same tool: 0 pairs at every corner, 84 tris;
#: the canopy's chase and DRIVE-UP boards and the station's screen re-measured, 0 pairs, 104 and 216 tris; the
#: night drop, cash cart, clock and planter on their own materials, 0 pairs. The first build of the bar measured the
#: module 0.225 deep in a 0.25 slot (posts a section short of the depth) and validation failed it.
CENSUS_BUILDS = 447''')
(R / "tests" / "test_coincident_faces.py").write_bytes(t.encode())
print("census 447")

edit("tests/test_material_options_closed.py", [
('''           # a drop safe is painted steel, its dial and handle bare steel as
           # a constant in the recipe (1.125.0)
           "drop_safe")''',
 '''           # a drop safe is painted steel, its dial and handle bare steel as
           # a constant in the recipe (1.125.0)
           "drop_safe",
           # the bank's outside (1.139.0): a drive-up canopy, its tube station
           # and a lane's clearance bar are painted steel, their colours in the
           # vertex; a wall clock's rim may be enamelled steel. delco_1997's
           # `metal` is street rust, and the canopy's fascia read black on it
           "drive_up_canopy", "drive_up_tube", "clearance_bar", "wall_clock")'''),
('''        # a crowd barricade is hot-dip galvanised tube (1.118.0)
        "crowd_barrier")''',
 '''        # a crowd barricade is hot-dip galvanised tube (1.118.0)
        "crowd_barrier",
        # a night depository is polished stainless (UL 771), a cash cart a
        # steel cage (1.139.0)
        "night_drop", "cash_cart")'''),
])

for name in ("test_clearance_bar.py", "test_bank_materials.py"):
    (R / "tests" / name).write_bytes((HERE / name).read_bytes())
    print("tests/" + name, "written")
