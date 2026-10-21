"""A GLB's meshes, primitives (one draw each, unbatched), materials and triangles, read from its JSON chunk."""
import json, struct, sys
for p in sys.argv[1:]:
    raw = open(p, "rb").read()
    assert raw[:4] == b"glTF", p
    n = struct.unpack_from("<I", raw, 12)[0]
    g = json.loads(raw[20:20 + n])
    prims = [(m.get("name"), pr) for m in g.get("meshes", []) for pr in m["primitives"]]
    tris = 0
    for _name, pr in prims:
        acc = g["accessors"][pr["indices"]] if "indices" in pr else g["accessors"][pr["attributes"]["POSITION"]]
        tris += acc["count"] // 3
    nodes = [nd.get("name") for nd in g.get("nodes", []) if "mesh" in nd]
    print(p.split("/")[-1], "| meshes", len(g.get("meshes", [])), "| primitives", len(prims),
          "| materials", len(g.get("materials", [])), "| tris", tris)
    for nd in nodes:
        print("   node", nd)
    for m in g.get("materials", []):
        print("   material", m.get("name"))
