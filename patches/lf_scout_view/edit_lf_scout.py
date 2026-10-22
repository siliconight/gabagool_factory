"""Level Factory 0.233.0, applied to a CLONE (<repo>): `buildings.json` names each building's scout view (Deli Counter
0.258.0's `drawings/scout.svg`; the factory's roadmap 296). Anchored; refuses on a miss; keeps line endings."""
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
     """THE SCOUT VIEW (0.233.0). The walker judged the axonometric too busy to scout from -- "simpler but carry all of the
signals needed" -- and Deli Counter 0.258.0 draws each building a second way, with only what a body finds its way
by, as `drawings/scout.svg`. Each entry names it under `scout`; a package composed before 0.258.0 has none, and the
entry says null there rather than guessing a path.

THE PATHS ARE res:// ON PURPOSE."""),
    ("""                 "spec": None, "axonometric": None, "plans": []}""",
     """                 "spec": None, "axonometric": None, "scout": None, "plans": []}"""),
    ("""            if rec.get("axonometric"):
                entry["axonometric"] = base + rec["axonometric"]
""",
     """            if rec.get("axonometric"):
                entry["axonometric"] = base + rec["axonometric"]
            if rec.get("scout"):
                entry["scout"] = base + rec["scout"]
"""),
])

edit("tests/unit/test_buildings_index.py", [
    ("""    for f in ("axonometric.svg", "floorB1.svg", "floor0.svg"):
        (d / f).write_text("<svg/>", encoding="utf-8")
    (d / "drawings.json").write_text(json.dumps({
        "schema": "deli_counter.drawings.v1", "spec": "deli_a03", "axonometric": "axonometric.svg",
        "plans": [{"storey": -1, "file": "floorB1.svg"}, {"storey": 0, "file": "floor0.svg"}]}), encoding="utf-8")""",
     """    for f in ("axonometric.svg", "scout.svg", "floorB1.svg", "floor0.svg"):
        (d / f).write_text("<svg/>", encoding="utf-8")
    # deli_a03 composed by Deli Counter 0.258.0, with a scout view; office (below) by 0.257.0, without
    (d / "drawings.json").write_text(json.dumps({
        "schema": "deli_counter.drawings.v1", "spec": "deli_a03", "axonometric": "axonometric.svg",
        "scout": "scout.svg",
        "plans": [{"storey": -1, "file": "floorB1.svg"}, {"storey": 0, "file": "floor0.svg"}]}), encoding="utf-8")"""),
])
p = R / "tests" / "unit" / "test_buildings_index.py"
t = p.read_bytes().decode("utf-8")
nl = "\r\n" if "\r\n" in t else "\n"
t = t.rstrip("\r\n") + nl + nl + nl + nl.join('''def test_the_scout_view_is_named_where_a_package_carries_one(tmp_path):
    """0.233.0, the factory's roadmap 296: a building whose package carries Deli Counter 0.258.0's scout view is named
    with it, res://; one composed before has none and says null; a facade has none; and the closure verdict proves the
    path -- take the file away and it names the index's reference to it."""
    root = _package(tmp_path)
    by_node = {e["node"]: e for e in BI.write(root)["buildings"]}
    assert by_node["b0"]["scout"] == "res://lot/deli_a03/drawings/scout.svg"
    assert by_node["b1"]["scout"] is None and by_node["b1"]["axonometric"] == "res://lot/office/drawings/axonometric.svg"
    assert by_node["blocker_0"]["scout"] is None
    assert not [i for i in scan_closure(root).issues if i.startswith(BI.INDEX_NAME)]
    (root / "lot" / "deli_a03" / "drawings" / "scout.svg").unlink()
    issues = [i for i in scan_closure(root).issues if i.startswith(BI.INDEX_NAME)]
    assert issues == ["%s: unresolved res://lot/deli_a03/drawings/scout.svg" % BI.INDEX_NAME], issues'''.split("\n")) + nl
p.write_bytes(t.encode("utf-8"))

v = R / "VERSION"
assert v.read_bytes() == b"0.232.1", v.read_bytes()
v.write_bytes(b"0.233.0")
print("edited", R)
