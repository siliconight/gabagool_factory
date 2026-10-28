"""Zoo 1.139.0, part one: the bank's pieces on the surfaces they are made of. Run in a Zoo clone's root.

delco_1997 maps the `metal` kind to `metal_rusted_street` (pixelcoat/profiles/themes/delco_1997.json), and a minted
species takes `metal` and the generic options (concrete, metal, wood, plaster): the drive-up's canopy and station were
built on rust, the cash cart, camera and clock on wood. Each now defaults to its own surface and offers only what it
could be made of, so a slot asking for something else falls back (Deli Counter 0.284.0) rather than building it.
"""
import json
import pathlib

R = pathlib.Path.cwd()

#: species -> (default, options, why)
TABLE = {
    "drive_up_canopy": ("metal_painted", ["metal_painted"], "a painted steel canopy, its fascia the bank's colour"),
    "drive_up_tube": ("metal_painted", ["metal_painted"], "a painted steel pedestal"),
    "night_drop": ("metal_bare", ["metal_bare"], "a polished stainless plate (UL 771 depositories are stainless)"),
    "cash_cart": ("metal_bare", ["metal_bare"], "a steel cage cart"),
    "wall_clock": ("plastic", ["plastic", "metal_painted"], "a moulded office clock"),
    "planter": ("plaster", ["plaster", "concrete", "plastic"], "a commercial planter: cast, concrete or moulded"),
}


#: recipes whose every colour is in the `Wear` vertex colour (`geometry.tint_wear`)
VERTEX_COLOURED = ("drive_up_canopy", "drive_up_tube", "night_drop")


def set_materials(species, default, options, why):
    g = R / "zoo_keeper" / "genome" / "species" / (species + ".json")
    raw = g.read_bytes()
    crlf = b"\r\n" in raw
    d = json.loads(raw)
    text = raw.replace(b"\r\n", b"\n")
    indent = next(i for i in (2, 1) if (json.dumps(d, indent=i) + "\n").encode() == text)
    d["materials"] = {"default": default, "options": list(options)}
    # every style on the species' own kind; a recipe whose colours ride the vertex colour takes a near-white base,
    # the price pylon's rule (`KIND_BASE` 1.0), so a tinted pack cannot darken them (a tintable pack takes the base
    # colour as its tint; how much of the canopy's near-black fascia that was, against the rust, is not measured)
    for s in (d.get("styles") or {}).values():
        s["material"] = default
        if species in VERTEX_COLOURED:
            s["color"] = [0.92, 0.92, 0.92]
    d["license"]["notes"] += f" 1.139.0: material {default} ({why}), options {', '.join(options)}."
    out = (json.dumps(d, indent=indent) + "\n").encode()
    g.write_bytes(out.replace(b"\n", b"\r\n") if crlf else out)
    print(g, "->", default, options)


for sp, (default, options, why) in TABLE.items():
    set_materials(sp, default, options, why)

# a teller counter of wood is a bank's own (the walker's comps 1-5): offered, the slot's `wood` builds it
g = R / "zoo_keeper" / "genome" / "species" / "teller_line.json"
raw = g.read_bytes()
crlf = b"\r\n" in raw
d = json.loads(raw)
text = raw.replace(b"\r\n", b"\n")
indent = next(i for i in (2, 1) if (json.dumps(d, indent=i) + "\n").encode() == text)
assert "wood" not in d["materials"]["options"]
d["materials"]["options"].append("wood")
d["license"]["notes"] += " 1.139.0: wood offered -- the comps' wood teller counter, which every library line asks for."
out = (json.dumps(d, indent=indent) + "\n").encode()
g.write_bytes(out.replace(b"\n", b"\r\n") if crlf else out)
print(g, "options + wood")
