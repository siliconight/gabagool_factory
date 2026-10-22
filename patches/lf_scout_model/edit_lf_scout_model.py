"""Level Factory 0.234.0, applied to a CLONE (<repo>): `buildings.json` names each building's scout model (Deli
Counter 0.259.0's `drawings/scout.glb`; the factory's roadmap 295). Anchored; refuses on a miss; keeps endings."""
import pathlib
import sys

R = pathlib.Path(sys.argv[1])


def edit(rel, pairs):
    p = R / rel
    b = p.read_bytes()
    crlf = b"\r\n" in b
    t = b.decode("utf-8").replace("\r\n", "\n")
    for o, n in pairs:
        assert t.count(o) == 1, (rel, o[:70])
        t = t.replace(o, n)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


edit("packages/exporting/buildings_index.py", [
    ("""THE PATHS ARE res:// ON PURPOSE.""",
     """THE SCOUT MODEL (0.234.0). The walker wants the scout view as something players turn all the way round -- "They
can scout out the buildings and rotate the schemas in a 360 degree way" (roadmap 295) -- and Deli Counter 0.259.0
builds it, `drawings/scout.glb`, one mesh a storey, kept as the file it is so a game loads it with `GLTFDocument`
when its screen opens. Each entry names it under `scout_model`, null where a package has none.

THE PATHS ARE res:// ON PURPOSE."""),
    ("""                 "spec": None, "axonometric": None, "scout": None, "plans": []}""",
     """                 "spec": None, "axonometric": None, "scout": None, "scout_model": None, "plans": []}"""),
    ("""            if rec.get("scout"):
                entry["scout"] = base + rec["scout"]
""",
     """            if rec.get("scout"):
                entry["scout"] = base + rec["scout"]
            if rec.get("scout_model"):
                entry["scout_model"] = base + rec["scout_model"]
"""),
])

edit("tests/unit/test_buildings_index.py", [
    ("""    for f in ("axonometric.svg", "scout.svg", "floorB1.svg", "floor0.svg"):
        (d / f).write_text("<svg/>", encoding="utf-8")""",
     """    for f in ("axonometric.svg", "scout.svg", "floorB1.svg", "floor0.svg"):
        (d / f).write_text("<svg/>", encoding="utf-8")
    (d / "scout.glb").write_bytes(b"glTF")"""),
    ("""        "scout": "scout.svg",
""",
     """        "scout": "scout.svg", "scout_model": "scout.glb",
"""),
])
p = R / "tests" / "unit" / "test_buildings_index.py"
t = p.read_bytes().decode("utf-8")
nl = "\r\n" if "\r\n" in t else "\n"
t = t.rstrip("\r\n") + nl + nl + nl + nl.join('''def test_the_scout_model_is_named_where_a_package_carries_one(tmp_path):
    """0.234.0, the factory's roadmap 295: a building whose package carries Deli Counter 0.259.0's scout model is named
    with it, res://; one composed before has none and says null; a facade has none; and the closure verdict proves the
    path -- take the model away and it names the index's reference to it."""
    root = _package(tmp_path)
    by_node = {e["node"]: e for e in BI.write(root)["buildings"]}
    assert by_node["b0"]["scout_model"] == "res://lot/deli_a03/drawings/scout.glb"
    assert by_node["b1"]["scout_model"] is None and by_node["blocker_0"]["scout_model"] is None
    assert not [i for i in scan_closure(root).issues if i.startswith(BI.INDEX_NAME)]
    (root / "lot" / "deli_a03" / "drawings" / "scout.glb").unlink()
    issues = [i for i in scan_closure(root).issues if i.startswith(BI.INDEX_NAME)]
    assert issues == ["%s: unresolved res://lot/deli_a03/drawings/scout.glb" % BI.INDEX_NAME], issues'''.split("\n")) + nl
p.write_bytes(t.encode("utf-8"))

v = R / "VERSION"
assert v.read_bytes() == b"0.233.0", v.read_bytes()
v.write_bytes(b"0.234.0")
print("edited", R)
