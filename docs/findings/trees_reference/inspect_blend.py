"""What a reference .blend holds, read without running anything in it.

Run inside Blender, background, with the file on the command line and
auto-exec OFF, so no script the file carries can run:

    C:\\blender\\blender.exe -b --factory-startup --disable-autoexec <file.blend> --python inspect_blend.py -- <out.json>

Prints, and writes as JSON:
- the Blender version the file was saved by, and the scenes and collections;
- every object: type, parent, collection, location, dimensions, modifiers
  (type and the settings that decide geometry), particle systems (count,
  render type, what they instance), and triangles, both its own mesh's and
  EVALUATED (modifiers and instancing applied, through the depsgraph);
- every material: its render method, alpha handling (blend method, alpha
  clip, backface culling), and the image each texture node reads;
- every image: size, source file, packed or not, colour space;
- every text block, by name and line count only. Its contents are NOT run
  and NOT printed: it is the file's code, and this is a reading of the file.

Prints what it measured and stops.
"""
import json
import sys

import bpy

OUT = sys.argv[sys.argv.index("--") + 1]


def tris_of(me):
    me.calc_loop_triangles()
    return len(me.loop_triangles)


def evaluated_tris(obj, depsgraph):
    ev = obj.evaluated_get(depsgraph)
    try:
        me = ev.to_mesh()
    except RuntimeError:
        return None
    if me is None:
        return None
    n = tris_of(me)
    ev.to_mesh_clear()
    return n


def modifier_row(m):
    row = {"name": m.name, "type": m.type, "show_render": m.show_render}
    for key in ("levels", "render_levels", "ratio", "iterations", "count",
                "use_smooth_shade", "branch_smoothing", "node_group"):
        if hasattr(m, key):
            v = getattr(m, key)
            row[key] = v.name if hasattr(v, "name") else v
    return row


def particle_rows(obj):
    rows = []
    for ps in getattr(obj, "particle_systems", []):
        s = ps.settings
        rows.append({
            "name": ps.name, "type": s.type, "count": s.count,
            "render_type": s.render_type,
            "instance_object": s.instance_object.name if s.instance_object else None,
            "instance_collection": (s.instance_collection.name
                                    if s.instance_collection else None),
            "hair_length": getattr(s, "hair_length", None),
        })
    return rows


def material_row(mat):
    row = {"name": mat.name, "users": mat.users}
    for key in ("blend_method", "surface_render_method", "alpha_threshold",
                "use_backface_culling", "shadow_method"):
        if hasattr(mat, key):
            row[key] = getattr(mat, key)
    images, alpha_linked = [], False
    if mat.use_nodes and mat.node_tree:
        for n in mat.node_tree.nodes:
            if n.type == "TEX_IMAGE" and n.image:
                images.append(n.image.name)
            if n.type == "BSDF_PRINCIPLED":
                a = n.inputs.get("Alpha")
                alpha_linked = alpha_linked or bool(a and a.is_linked)
        row["shaders"] = sorted({n.type for n in mat.node_tree.nodes
                                 if n.type.startswith("BSDF") or n.type in
                                 ("MIX_SHADER", "EMISSION", "BSDF_TRANSPARENT")})
    row["images"] = images
    row["alpha_linked"] = alpha_linked
    return row


def main():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    doc = {"saved_by": ".".join(str(v) for v in bpy.data.version),
           "blender": bpy.app.version_string,
           "scenes": [s.name for s in bpy.data.scenes],
           "collections": [{"name": c.name, "objects": len(c.objects),
                            "children": [k.name for k in c.children]}
                           for c in bpy.data.collections],
           "objects": [], "materials": [], "images": [], "texts": []}
    for obj in bpy.data.objects:
        row = {"name": obj.name, "type": obj.type,
               "parent": obj.parent.name if obj.parent else None,
               "collections": [c.name for c in obj.users_collection],
               "location": [round(v, 3) for v in obj.location],
               "dimensions": [round(v, 3) for v in obj.dimensions],
               "hide_render": obj.hide_render,
               "instance_type": obj.instance_type,
               "modifiers": [modifier_row(m) for m in obj.modifiers],
               "particles": particle_rows(obj),
               "materials": [s.material.name for s in obj.material_slots if s.material]}
        if obj.type == "MESH":
            row["verts"] = len(obj.data.vertices)
            row["tris"] = tris_of(obj.data)
            row["uv_layers"] = [u.name for u in obj.data.uv_layers]
            row["color_attributes"] = [a.name for a in obj.data.color_attributes]
        if obj.type in ("MESH", "CURVE"):
            row["tris_evaluated"] = evaluated_tris(obj, depsgraph)
        doc["objects"].append(row)
    doc["materials"] = [material_row(m) for m in bpy.data.materials]
    for im in bpy.data.images:
        doc["images"].append({"name": im.name, "size": list(im.size),
                              "filepath": im.filepath, "packed": bool(im.packed_file),
                              "colorspace": im.colorspace_settings.name,
                              "alpha_mode": im.alpha_mode, "source": im.source})
    for t in bpy.data.texts:
        doc["texts"].append({"name": t.name, "lines": len(t.lines),
                             "use_module": getattr(t, "use_module", None)})
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
    print("[blend] saved by", doc["saved_by"], "read by", doc["blender"])
    print("[blend] scenes", doc["scenes"])
    for c in doc["collections"]:
        print("[blend] collection", c["name"], "objects", c["objects"], "children", c["children"])
    for o in doc["objects"]:
        print("[blend] object %-28s %-8s tris %-7s eval %-8s dims %s mods %s particles %s mats %s"
              % (o["name"][:28], o["type"], o.get("tris"), o.get("tris_evaluated"),
                 o["dimensions"], [m["type"] for m in o["modifiers"]],
                 [(p["count"], p["render_type"], p["instance_object"] or p["instance_collection"])
                  for p in o["particles"]], o["materials"]))
    for m in doc["materials"]:
        print("[blend] material", m)
    for im in doc["images"]:
        print("[blend] image", im)
    for t in doc["texts"]:
        print("[blend] text block (not run, not printed):", t)


main()
