"""Hash every mesh simple_car builds, per street style and size, from ONE zoo
tree -- run once against the shipped Zoo and once against the changed copy,
and compare the two JSONs. The plan is resolved the way `build_module`
resolves it (`dna.resolve_module_plan`), its ``body_style`` set, and the
recipe called with the same seeded streams.

    blender -b --python car_hashes.py -- <zoo repo> <out.json>

Frame: the recipe's own build frame (z 0 .. H, before re-centring); vertex
positions rounded to 1e-6 m before hashing.
"""
import hashlib
import json
import sys

argv = sys.argv[sys.argv.index("--") + 1:]
repo, out = argv[0], argv[1]
sys.path.insert(0, repo)
import bpy  # noqa: E402
from zoo_keeper.bpylayer import build as build_mod  # noqa: E402
from zoo_keeper.core import dna, genome as genome_mod, kit, seeding  # noqa: E402
from zoo_keeper.recipes import simple_car  # noqa: E402

genome = genome_mod.load_species("simple_car")
rows = {}
for style in ("sedan", "coupe", "hatchback", "suv"):
    for dims in ((1.75, 4.30, 1.40), (1.85, 4.90, 1.50), (2.00, 5.20, 1.80)):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        slot = {"slot_id": "car_0", "role": "prop", "size_mod": "full", "style": 1,
                "species": "simple_car", "fit": {"dims": list(dims), "pivot": "center"}}
        mod = kit.plan_kit({"building_id": "car_hashes", "slots": [slot]}, theme="delco_1997", style=1)["modules"][0]
        plan = dna.resolve_module_plan(mod, genome, "delco_1997", 1, build_mod.TOOL_VERSION)
        plan["params"] = dict(plan.get("params") or {}, body_style=style)
        stem = plan["module"]["stem"]
        streams = seeding.RNGStreams(seeding.root_key(stem, "simple_car", 0, build_mod.SEED_EPOCH))
        coll = bpy.data.collections.new(stem)
        bpy.context.scene.collection.children.link(coll)
        res = simple_car.build(plan, streams, coll)
        objs = {}
        for o in sorted(res["objects"], key=lambda o: o.name):
            m = o.data
            h = hashlib.sha1()
            for v in m.vertices:
                h.update(("%.6f,%.6f,%.6f;" % tuple(v.co)).encode())
            for p in m.polygons:
                h.update((",".join(str(i) for i in p.vertices) + ";").encode())
            mat = o.active_material.name if o.active_material else ""
            objs[o.name] = {"verts": len(m.vertices), "faces": len(m.polygons), "sha1": h.hexdigest(),
                            "material": mat}
        key = "%s %s" % (style, "x".join("%.2f" % d for d in dims))
        rows[key] = {"form": {k: res["form"].get(k) for k in ("style", "doors", "paint_name", "wheel_kind")},
                     "objects": objs, "attachments": {k: [round(c, 6) for c in v]
                                                     for k, v in res["attachments"].items()}}
        print("[hash] %s: %d objects, %d verts" % (key, len(objs), sum(o["verts"] for o in objs.values())))
json.dump(rows, open(out, "w", encoding="utf-8"), indent=1, sort_keys=True)
print("[hash] wrote %s" % out)
