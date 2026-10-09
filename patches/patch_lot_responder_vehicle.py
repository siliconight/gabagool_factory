"""Lot 0.101.0: the responders' car is built and shipped, and stood nowhere
(roadmap 212).

`assemble` writes each arrival's car as `site_spec["responders"]`,
`write_site_slots` gives each a slot so Zoo's site kit builds the cruiser,
and the themed assembly copies the module into `cover/` beside its scene
(with the textures it names) without declaring it in the scene, then names
it in `responders.json`. Level Factory 0.162.0 ships the name.

Anchored edits (every anchor once; refuses on a miss; nothing is written
until every anchor in every file matched):
- `site_responders.py`: `vehicle_record`.
- `lot.py`: `assemble` (the list), `write_site_slots` (the slots and their
  coverage), `COVER_MATERIALS` (`cruiser`), the themed scene's resolution
  and `write_responder_vehicles` with `RESPONDERS_NAME`.
- `tests/test_site_responders.py`: four tests and the GLB fixture import.
CHANGELOG and VERSION from `lot_responder_vehicle/CHANGELOG_0.101.0.md`.

    python patch_lot_responder_vehicle.py
    LOT_ROOT=<copy> python patch_lot_responder_vehicle.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_responder_vehicle"

RESPONDERS = [
    ("""def marker(arrival) -> dict:
""",
     """def vehicle_record(arrival) -> dict:
    \"\"\"The car an arrival brings (0.101.0), as a record the site kit builds
    from: the species, its slot ([plan x, plan y, height] before the turn, as
    every cover record's `dims`), and where it stands at its stop, facing
    the way it drove in. Built, never stood: the gameplay layer spawns it.\"\"\"
    name, w, d, h = VEHICLE
    return {"species": name, "dims": [w, d, h], "at": list(arrival["stop"]),
            "yaw": arrival["yaw"], "source": "responder_arrival"}


def marker(arrival) -> dict:
"""),
]

LOT_PY = [
    # assemble: the cars, a list of their own
    ("""    responder_keep_out = site_responders.keep_out(arrivals)
""",
     """    responder_keep_out = site_responders.keep_out(arrivals)
    # THE CAR THEY ARRIVE IN (0.101.0): one record a stop, in a list of its
    # own -- not cover, so no planner stands round it and the scene stands
    # nothing for it. `write_site_slots` gives each a slot, so Zoo's site
    # kit builds the car; the themed assembly copies the module beside its
    # scene and names it in `responders.json` (`write_responder_vehicles`),
    # which the package reads.
    site_spec["responders"] = [site_responders.vehicle_record(a) for a in arrivals]
"""),
    # write_site_slots: a slot a car
    ("""    coverage = {"prop/site_cover": n_cover}
    if len(slots) > n_cover:
        coverage["prop/site_hung"] = len(slots) - n_cover
""",
     """    n_hung = len(slots) - n_cover
    # THE RESPONDERS' CAR (0.101.0): a slot an arrival, so the site kit
    # builds it. Nothing stands it -- the gameplay layer spawns responders --
    # so the slot's transform says where the car would stop, and only
    # `write_responder_vehicles` reads what Zoo built.
    for i, rv in enumerate(site_spec.get("responders", []) or []):
        sp, dims = rv.get("species"), rv.get("dims")
        if not sp or not dims or len(dims) < 3:
            continue
        cx, cy = rv["at"][:2]
        slots.append({
            "slot_id": f"responder_{i}", "role": "prop", "size_mod": "full",
            "style": int(rv.get("style") or 1),
            "material": COVER_MATERIALS.get(sp, "metal_painted"),
            "current_ref": "prop_greybox_01", "kit_axis": "theme",
            "species": sp,
            "transform": {"translation": [round(cx, 4), round(cy, 4),
                                          round(float(dims[2]) / 2.0, 4)],
                          "rot_y": float(rv.get("yaw") or 0.0),
                          "scale": [1.0, 1.0, 1.0]},
            "fit": {"dims": [float(dims[0]), float(dims[1]), float(dims[2])],
                    "pivot": "center", "openings": [], "collision": "convex"},
        })
    coverage = {"prop/site_cover": n_cover}
    if n_hung:
        coverage["prop/site_hung"] = n_hung
    if len(slots) > n_cover + n_hung:
        coverage["prop/site_responders"] = len(slots) - n_cover - n_hung
"""),
    # the cruiser's material, as its genome names it
    ("""                   "step_van": "paint_matte",
                   "simple_car": "metal_painted",
""",
     """                   "step_van": "paint_matte",
                   "simple_car": "metal_painted",
                   # the responders' car (0.101.0), Zoo 1.86.0's one option
                   "cruiser": "metal_painted",
"""),
    # the themed scene: copy the car, stand nothing, name it
    ("""    # a module both lists use is declared once
    res_lines += [ln for ln in hung_ext if ln not in res_lines]
""",
     """    # a module both lists use is declared once
    res_lines += [ln for ln in hung_ext if ln not in res_lines]
    # THE RESPONDERS' CAR (0.101.0): resolved and copied beside the scene the
    # way a cover piece is -- the module and the textures beside it -- but
    # declared nowhere in it: a resource the scene names, it would load.
    # `responders.json` names the file for the package.
    resp_refs, _resp_ext, resp_findings = cover_module_refs(
        site_spec, prefix, os.path.dirname(os.path.abspath(out_path)), key="responders")
    for code, msg in resp_findings:
        print(f"[lot] {code}: {msg}")
    write_responder_vehicles(site_spec, resp_refs, os.path.dirname(os.path.abspath(out_path)))
"""),
    # the writer
    ("""def _blocker_source(bk):
""",
     """#: What `write_responder_vehicles` writes beside a themed site scene.
RESPONDERS_NAME = "responders.json"


def write_responder_vehicles(site_spec, refs, scene_dir):
    \"\"\"`responders.json` beside the scene (0.101.0, roadmap 212): for each
    arrival's car, the module Zoo built and `cover_module_refs` copied --
    its path relative to the scene -- with the stop and the slot it was
    built for. The gameplay layer spawns responders; the package names the
    car it spawns (Level Factory's `responder_arrivals.json`). A car with no
    module is listed under `missing`, not dropped. Returns the document, or
    None, writing nothing, on a site with no arrivals.\"\"\"
    cars = site_spec.get("responders") or []
    if not cars:
        return None
    vehicles, missing = [], []
    for i, rv in enumerate(cars):
        ref = refs.get(i)
        if ref is None:
            missing.append(i)
            continue
        assert ref.startswith("cover_"), ref        # `cover_module_refs`' own ids
        vehicles.append({"arrival": i, "species": rv["species"],
                         "scene": f"{COVER_DIR}/{ref[len('cover_'):]}.glb",
                         "stop": list(rv["at"]), "yaw": rv.get("yaw"),
                         "dims": list(rv["dims"])})
    doc = {"schema": "lot.responder_vehicles.v1",
           "what": ("The car each responder arrival brings: built by Zoo's site kit, "
                    "copied beside this scene, stood nowhere. Spawning it is the "
                    "gameplay layer's."),
           "vehicles": vehicles, "missing": missing}
    with open(os.path.join(scene_dir, RESPONDERS_NAME), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=2)
    return doc


def _blocker_source(bk):
"""),
]

ANCHOR = """def test_cover_keeps_out_of_a_lane_and_the_lane_hides_nobody():
"""
NEW = """# --------------------------------------------------------------------------- #
# 0.101.0: the car they arrive in -- built, shipped, stood nowhere
# --------------------------------------------------------------------------- #

def _cruiser_stem():
    _name, w, d, h = site_responders.VEHICLE
    return lot.cover_module_stem("cruiser", "delco_1997", 1, [w, d, h])


def test_each_arrival_gets_a_kit_slot_for_its_car(tmp_path):
    \"\"\"`write_site_slots` gives every arrival's car a slot, so Zoo's site kit
    builds it: the cruiser at `VEHICLE`'s size, at the stop, facing the way
    it drove in, with collision for when the game spawns it.\"\"\"
    drawn, _gameplay = _assembled(tmp_path)
    arrivals = [m["arrival"] for m in _arrivals(drawn["site_markers"])]
    doc = json.loads(next(tmp_path.glob("*.slots.json")).read_text(encoding="utf-8"))
    cars = [s for s in doc["slots"] if s["slot_id"].startswith("responder_")]
    assert len(cars) == len(arrivals) == 2
    assert doc["coverage"]["prop/site_responders"] == 2
    _name, w, d, h = site_responders.VEHICLE
    for slot, a in zip(cars, arrivals):
        assert slot["species"] == "cruiser" and slot["fit"]["dims"] == [w, d, h]
        assert slot["fit"]["collision"] == "convex"
        assert slot["transform"]["translation"] == [round(a["stop"][0], 4), round(a["stop"][1], 4),
                                                    round(h / 2.0, 4)]
        assert slot["transform"]["rot_y"] == a["yaw"]


def test_the_car_is_copied_with_what_it_names_and_named_for_the_package(tmp_path):
    \"\"\"The module and the texture beside it go where a cover module's go,
    and `responders.json` names the file, with the stop and the slot.\"\"\"
    stem = _cruiser_stem()
    write_glb(tmp_path / (stem + ".glb"), "cruiser", images=["_tex/livery_c1930467.png"])
    spec = {"responders": [site_responders.vehicle_record({"stop": [62.637, -22.75], "yaw": 270.0})],
            "cover_modules": {"dir": str(tmp_path), "theme": "delco_1997", "style": 1},
            "buildings": []}
    out = tmp_path / "out"
    out.mkdir()
    refs, _ext, findings = lot.cover_module_refs(spec, "", str(out), key="responders")
    assert findings == [] and refs == {0: "cover_" + stem}
    doc = lot.write_responder_vehicles(spec, refs, str(out))
    _name, w, d, h = site_responders.VEHICLE
    assert doc["vehicles"] == [{"arrival": 0, "species": "cruiser", "scene": f"cover/{stem}.glb",
                                "stop": [62.637, -22.75], "yaw": 270.0, "dims": [w, d, h]}]
    assert doc["missing"] == []
    assert (out / "cover" / (stem + ".glb")).is_file()
    assert (out / "cover" / "_tex" / "livery_c1930467.png").is_file()
    assert json.loads((out / lot.RESPONDERS_NAME).read_text(encoding="utf-8")) == doc


def test_the_assembled_scene_stands_no_car(tmp_path):
    \"\"\"The probe assembled against a kit holding the cruiser: the car is
    copied beside the scene and named for both arrivals, and the scene
    declares and instances nothing of it -- a resource a scene names, it
    loads, and responders are the gameplay layer's to spawn.\"\"\"
    stem = _cruiser_stem()
    kit = tmp_path / "kit"
    write_glb(kit / (stem + ".glb"), "cruiser", images=["_tex/livery_c1930467.png"])
    spec = json.load(open(PROBE, encoding="utf-8"))
    spec["cover_modules"] = {"dir": str(kit), "theme": "delco_1997", "style": 1}
    probe = tmp_path / "coldrun_kerb_probe.json"
    probe.write_text(json.dumps(spec), encoding="utf-8")
    out = tmp_path / "out"
    lot.assemble(str(probe), str(out))
    scene = next(out.glob("*.tscn")).read_text(encoding="utf-8")
    assert stem not in scene
    doc = json.loads((out / lot.RESPONDERS_NAME).read_text(encoding="utf-8"))
    assert [v["scene"] for v in doc["vehicles"]] == [f"cover/{stem}.glb"] * 2 and doc["missing"] == []
    assert (out / "cover" / (stem + ".glb")).is_file()


def test_with_no_kit_every_car_is_missing_not_dropped(tmp_path):
    \"\"\"The candidate's greybox assembly has no kit yet: `responders.json`
    lists each car as missing, so a package that ships none says so.\"\"\"
    _assembled(tmp_path)
    doc = json.loads((tmp_path / lot.RESPONDERS_NAME).read_text(encoding="utf-8"))
    assert doc["vehicles"] == [] and doc["missing"] == [0, 1]


""" + ANCHOR


def _stage(root, edits):
    """{path: bytes}: every file's new content, every anchor matched once,
    endings kept; raises before anything is written."""
    staged = {}
    for rel, pairs in edits.items():
        p = root / rel
        d = p.read_bytes()
        crlf, lf = d.count(b"\r\n"), d.count(b"\n")
        assert crlf in (0, lf), (rel, "mixed endings")
        t = d.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            n = t.count(old)
            assert n == 1, (rel, n, old[:70])
            t = t.replace(old, new)
        staged[p] = (t.replace("\n", "\r\n") if crlf else t).encode("utf-8")
    return staged


IMPORT_OLD = "import site_streets     # noqa: E402\n"
IMPORT_NEW = IMPORT_OLD + "from tests.glb_fixture import write_glb  # noqa: E402\n"

EDITS = {
    "site_responders.py": RESPONDERS,
    "lot.py": LOT_PY,
    str(pathlib.Path("tests") / "test_site_responders.py"): [(ANCHOR, NEW), (IMPORT_OLD, IMPORT_NEW)],
}


def main():
    v = LOT / "VERSION"
    assert v.read_bytes() == b"Lot 0.100.1", v.read_bytes()
    staged = _stage(LOT, EDITS)
    entry = (SRC / "CHANGELOG_0.101.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    cl = LOT / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## 0.100.1 - the responder planner checks the boxes it records"), text[:60]
    # Every anchor matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    cl.write_bytes((entry + text).encode("utf-8"))
    v.write_bytes(b"Lot 0.101.0")
    print("Lot 0.100.1 -> 0.101.0")


if __name__ == "__main__":
    main()
