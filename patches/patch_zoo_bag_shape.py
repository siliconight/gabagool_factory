"""Zoo 1.42.0: a bag is pinched flat at its seals and puffed between them.

The walker, 2026-10-02, sent two tutorials on making a chip bag in Blender:
a flat sheet with its top and bottom rows PINNED, inflated by a cloth
simulation's pressure, the pinned rows staying flat as the crimped seals.
That is the shape: thin at the top and the bottom, fat in the middle, front
and back alike.

Until now a bag was `prims.pillow` stood on its back: a box with a crowned
front, as deep at its top and bottom edges as at its middle. It read as a
padded box.

`bag()` now builds four rings up the bag's height -- the bottom seal's edge
(thin, full width), the belly's foot and head (the full depth, a little
narrower: a filled bag draws in), the top seal's edge (thin, full width) --
and lofts them: 14 planar quads, 28 triangles where the pillow was 22. The
front is the three quads toward -Y, and the print maps onto them by x and z
as it did.

NOT the simulation, and that is the performance rule: a simulated sheet
dense enough to wrinkle is thousands of triangles a bag and a gondola
stands two hundred. What the cheap shape gives up is stated in the
changelog.

Every edit asserts its anchor once and refuses to write on a miss.
"""
from __future__ import annotations

import pathlib

ZOO = pathlib.Path(__file__).resolve().parents[1] / "zoo"


def _load(rel):
    p = ZOO / rel
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    if crlf:
        assert raw.count(b"\r\n") == raw.count(b"\n"), f"{rel}: mixed line endings"
    return p, raw.replace(b"\r\n", b"\n").decode("utf-8"), crlf


def _save(p, s, crlf):
    b = s.encode("utf-8")
    p.write_bytes(b.replace(b"\n", b"\r\n") if crlf else b)
    print("patched", p.relative_to(ZOO))


def _once(rel, s, old, new):
    n = s.count(old)
    assert n == 1, f"{rel}: anchor found {n} times: {old[:60]!r}"
    return s.replace(old, new)


DOC1_OLD = '''  * CHIP BAGS on every shelf, faced out: each a real bag -- a puffed front,
    flat sides (`prims.pillow` stood on its back) -- its front printed from'''
DOC1_NEW = '''  * CHIP BAGS on every shelf, faced out: each a real bag -- pinched flat at
    its top and bottom seals and puffed between them (`bag`) -- its front
    printed from'''
DOC2_OLD = '''on a flat panel. It costs 22 triangles a bag.'''
DOC2_NEW = '''on a flat panel. It costs 28 triangles a bag (1.42.0; the pillow it
replaced was 22).'''

CONST_OLD = '''BAG_CROWN = 0.03          # the puff of a bag's front
'''
CONST_NEW = '''BAG_CROWN = 0.03          # the puff of a bag's front
#: A BAG'S SHAPE (1.42.0), from the walker's tutorials: the top and bottom
#: rows of the sheet are pinned and stay flat -- the seals -- and pressure
#: fills what is between. The seal's edge is this thick; the belly runs
#: between these fractions of the bag's height, at this fraction of its
#: width (a filled bag draws in at the waist).
SEAL_T = 0.008
BELLY = (0.30, 0.70)
BELLY_W = 0.94
'''

BAG_START = '''def bag(x, y_front, z0, bw, bh, brand, depth=BAG_D, crown=BAG_CROWN):'''
BAG_END = '''def carton(x, y_front, z0, bw, bh, bd, brand):'''
BAG_NEW = '''def bag(x, y_front, z0, bw, bh, brand, depth=BAG_D, crown=BAG_CROWN):
    """One bag, its front toward -Y at ``y_front``, standing on ``z0``
    (buried `BURY`), centred on ``x``; ``depth + crown`` is its thickness at
    the belly.

    FOUR RINGS UP ITS HEIGHT, lofted: the bottom seal's edge (`SEAL_T`
    thick, full width), the belly's foot and head (full thickness,
    `BELLY_W` of the width), the top seal's edge. Pinched at the seals and
    fat between, front and back alike -- the walker's tutorials, without
    the simulation. Fourteen planar quads: the bottom cap, three toward -Y
    (``front``: shoulder, belly, shoulder), three to each other side, the
    top cap. ``uvs`` put the front on the brand's tile by x and z and every
    other face on the brand's colour block."""
    thick = depth + crown
    yc = y_front + thick / 2.0
    zb = z0 - BURY
    rings = ((0.0, 1.0, SEAL_T), (BELLY[0], BELLY_W, thick), (BELLY[1], BELLY_W, thick),
             (1.0, 1.0, SEAL_T))
    verts = []
    for f, wk, t in rings:
        hw = bw * wk / 2.0
        z = zb + bh * f
        verts += [(x - hw, yc - t / 2.0, z), (x + hw, yc - t / 2.0, z),
                  (x + hw, yc + t / 2.0, z), (x - hw, yc + t / 2.0, z)]
    faces = [(0, 3, 2, 1)]                                    # the bottom cap
    spans = [(4 * i, 4 * i + 4) for i in range(len(rings) - 1)]
    faces += [(a, a + 1, b + 1, b) for a, b in spans]         # the front, -Y
    faces += [(a + 1, a + 2, b + 2, b + 1) for a, b in spans]     # +X
    faces += [(a + 2, a + 3, b + 3, b + 2) for a, b in spans]     # the back, +Y
    faces += [(a + 3, a, b, b + 3) for a, b in spans]             # -X
    top = 4 * (len(rings) - 1)
    faces.append((top, top + 1, top + 2, top + 3))            # the top cap
    p = P.mesh("Snack_Bag", "bag", verts, faces)
    front = tuple(range(1, 1 + len(spans)))
    x0, x1 = x - bw / 2.0, x + bw / 2.0
    uvs = []
    for k, f in enumerate(p["faces"]):
        if k in front:
            # clamped: a ring's own corner is the tile's edge to a rounding
            uvs.append(tuple(("tile_" + brand,
                              min(1.0, max(0.0, (p["verts"][i][0] - x0) / (x1 - x0))),
                              min(1.0, max(0.0, (p["verts"][i][2] - zb) / bh))) for i in f))
        else:
            uvs.append(tuple(("solid_" + brand,) for _ in f))
    p["uvs"] = uvs
    p["front"] = front
    return p


'''

T_OLD = '''def test_every_bag_face_maps_into_the_art():'''
T_NEW = '''def test_a_bag_is_pinched_at_its_seals_and_fat_between():
    """1.42.0, the walker's tutorials: the sheet's top and bottom rows are
    pinned flat -- the seals -- and the bag fills between them. Thin at the
    foot and the head, the full thickness across the belly, front and back
    alike; every face planar and wound outward; 28 triangles."""
    for bw, bh, d, crown in ((S.BAG_W, 0.30, S.BAG_D, S.BAG_CROWN), (0.125, 0.17, 0.05, S.CANDY_CROWN)):
        p = S.bag(0.0, 0.0, 0.0, bw, bh, SB.IDS[0], d, crown)
        ys = lambda lo, hi: [v[1] for v in p["verts"] if lo <= (v[2] + S.BURY) / bh <= hi]   # noqa: E731
        foot, belly, head = ys(-0.01, 0.01), ys(S.BELLY[0] - 0.01, S.BELLY[1] + 0.01), ys(0.99, 1.01)
        assert abs((max(foot) - min(foot)) - S.SEAL_T) < 1e-9
        assert abs((max(head) - min(head)) - S.SEAL_T) < 1e-9
        assert abs((max(belly) - min(belly)) - (d + crown)) < 1e-9
        # front and back alike: the seals sit on the belly's mid-plane
        mid = (max(belly) + min(belly)) / 2.0
        assert abs((max(foot) + min(foot)) / 2.0 - mid) < 1e-9
        assert abs(min(belly) - 0.0) < 1e-9                      # the belly reaches y_front
        xs = [v[0] for v in p["verts"]]
        assert abs(max(xs) - bw / 2.0) < 1e-9 and abs(min(xs) + bw / 2.0) < 1e-9
        assert S.signed_volume(p) > 0
        assert P.tri_count([p]) == 28
        for f in p["faces"]:                                    # planar
            a, b, c, e = (p["verts"][i] for i in f)
            u = [b[k] - a[k] for k in range(3)]
            v = [c[k] - a[k] for k in range(3)]
            n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
            assert abs(sum(n[k] * (e[k] - a[k]) for k in range(3))) < 1e-12
        # the three front faces look toward -Y
        for k in p["front"]:
            a, b, c = (p["verts"][i] for i in p["faces"][k][:3])
            u = [b[j] - a[j] for j in range(3)]
            v = [c[j] - a[j] for j in range(3)]
            assert u[2] * v[0] - u[0] * v[2] < 0, k


def test_every_bag_face_maps_into_the_art():'''


def main():
    rel = "zoo_keeper/core/snack_gondola_forms.py"
    p, s, crlf = _load(rel)
    assert "SEAL_T" not in s, "already applied"
    s = _once(rel, s, DOC1_OLD, DOC1_NEW)
    s = _once(rel, s, DOC2_OLD, DOC2_NEW)
    s = _once(rel, s, CONST_OLD, CONST_NEW)
    assert s.count(BAG_START) == 1 and s.count(BAG_END) == 1
    a, b = s.index(BAG_START), s.index(BAG_END)
    assert a < b
    s = s[:a] + BAG_NEW + s[b:]
    _save(p, s, crlf)

    rel = "tests/test_snack_gondola.py"
    p, s, crlf = _load(rel)
    s = _once(rel, s, T_OLD, T_NEW)
    _save(p, s, crlf)

    # THE BUDGET IS A REGRESSION DETECTOR (CLAUDE.md), and this is a known
    # step: 6 triangles a bag. The genome's largest gondola (14 x 1.5 x 2.2)
    # is 20,676 where it was 18,528 against 20,000.
    rel = "zoo_keeper/genome/species/snack_gondola.json"
    p, s, crlf = _load(rel)
    s = _once(rel, s, '"tris_lod0": 20000', '"tris_lod0": 22000')
    _save(p, s, crlf)


if __name__ == "__main__":
    main()
