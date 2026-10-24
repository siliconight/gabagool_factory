"""Zoo 1.121.0 on a CLONE (<repo>): a traffic signal for the driver's right (the walker's walk of cold run 9386,
finding 12: "where are the traffic lights for this side of the road?"). Anchored; refuses on a miss.

    python edit_zoo_signal_hand.py <repo>
"""
import json
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


edit("zoo_keeper/recipes/traffic_signal.py", [
    ('''Extents are exactly (w, d, h). Collision is the POLE only -- a body walks
under an arm.
"""''',
     '''Extents are exactly (w, d, h). Collision is the POLE only -- a body walks
under an arm.

TWO HANDS (1.121.0). The heads face -y off an arm along +x: seen from above,
the face is the arm turned clockwise, which is a pole on the driver's LEFT
reaching right over the lanes. The `right` form turns both heads round to
face +y -- the arm turned counter-clockwise -- for the pole a US junction
stands on the approach's far RIGHT corner, its arm back over the lanes and
its heads facing the driver (MUTCD 4D.14: two faces at least 8 ft apart, one
at least 40 ft beyond the stop line; the arm's head and the pole's are 4.3 m
apart). The walker, walking cold run 9386: "where are the traffic lights for
this side of the road?" -- Lot stood a signal only on a junction's yielding
leg, its heads facing across it. Same geometry, materials and collision
either way; only the heads, their lenses and visors change side.
"""'''),
    ('''def _head(bm, lens_bms, centre):
    """A three-lens head hung with its top at ``centre``, facing -y.
    ``lens_bms`` holds one bmesh per lens row -- red, amber, green -- so each
    row can wear its own colour."""
    cx, cy, cz = centre
    geometry.add_box(bm, (cx, cy, cz - HEAD_H / 2.0), (HEAD_W, HEAD_D, HEAD_H))
    for i in range(3):
        lz = cz - HEAD_H * (0.19 + 0.31 * i)
        y = cy - (HEAD_D / 2.0 + 0.012)
        geometry.add_cylinder(lens_bms[i], (cx, y, lz), LENS_R, 0.02,
                              segments=8, axis="Y")
        geometry.add_box(bm, (cx, y - 0.055, lz + LENS_R * 0.8),
                         (HEAD_W * 0.92, 0.11, 0.03))          # the visor''',
     '''def _head(bm, lens_bms, centre, face=-1):
    """A three-lens head hung with its top at ``centre``, facing -y (``face``
    -1) or +y (+1, the `right` form). ``lens_bms`` holds one bmesh per lens
    row -- red, amber, green -- so each row can wear its own colour."""
    cx, cy, cz = centre
    geometry.add_box(bm, (cx, cy, cz - HEAD_H / 2.0), (HEAD_W, HEAD_D, HEAD_H))
    for i in range(3):
        lz = cz - HEAD_H * (0.19 + 0.31 * i)
        y = cy + face * (HEAD_D / 2.0 + 0.012)
        geometry.add_cylinder(lens_bms[i], (cx, y, lz), LENS_R, 0.02,
                              segments=8, axis="Y")
        geometry.add_box(bm, (cx, y + face * 0.055, lz + LENS_R * 0.8),
                         (HEAD_W * 0.92, 0.11, 0.03))          # the visor'''),
    ('''    mast = w * 0.62                      # the signal arm, over the road''',
     '''    # which way the heads face: -y, or +y on the `right` form (TWO HANDS)
    face = 1 if (plan.get("params") or {}).get("form") == "right" else -1
    mast = w * 0.62                      # the signal arm, over the road'''),
    ('''    _head(bm, lens_bms, (mast * 0.92, 0.0, arm_z - 0.08))      # over the road
    _head(bm, lens_bms, (POLE_D * 1.4, 0.0, arm_z - 0.60))     # the near head''',
     '''    _head(bm, lens_bms, (mast * 0.92, 0.0, arm_z - 0.08), face)      # over the road
    _head(bm, lens_bms, (POLE_D * 1.4, 0.0, arm_z - 0.60), face)     # the near head'''),
])

# the genome lists the form, so `kit.honour_dressing` keeps it and the stem says it
gp = R / "zoo_keeper" / "genome" / "species" / "traffic_signal.json"
raw = gp.read_bytes()
crlf = b"\r\n" in raw
text = raw.decode("utf-8").replace("\r\n", "\n")
g = json.loads(text)
assert g["params"] == {}, g["params"]
old = '  "params": {},\n'
assert text.count(old) == 1
text = text.replace(old, '  "params": {\n    "form": [\n      "auto",\n      "right"\n    ]\n  },\n')
assert json.loads(text)["params"] == {"form": ["auto", "right"]}
gp.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
print("traffic_signal: the right form; genome params.form")
