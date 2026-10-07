"""Deli Counter 0.198.0: the z-fight gate judges a pair by the side its faces face.

    python patch_dc_zfight_facing.py

Anchored on zfight_gate.py as read 2026-10-06 (12,965 bytes, LF); every
anchor must match exactly once or nothing is written.

MEASURED FIRST (`zfight_hidden_census.py`, 9189's composed buildings, the
gate's own raw pairs): deli_a01 198 visible by the gate's rule, office 121,
rail_station_a02 117; judged by the side the faces face, with a 2-D joint
cover to the gate's tolerance, 2, 2 and 1 -- the same at a 5.5 mm gap and at
5 cm. Refuted on the way, kept: the census's first 2-D cover had no
tolerance, and called every float32 seam between two slab tiles (2.4e-7 m) a
hole.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ZF = ROOT / "deli_counter" / "zfight_gate.py"

EDITS = []

EDITS.append((
    '''Abutting faces (max-vs-min: a wall top meeting the ceiling above) are
never flagged.
''',
    '''Abutting faces (max-vs-min: a wall top meeting the ceiling above) are
never flagged.

A pair can be seen only from the side its two faces FACE, so it is judged
there (0.198.0, `visible_fights`). When solid matter within OUTWARD_GAP of
the plane on that side covers the shared rectangle -- one solid, or several
together in 2-D -- no camera can reach either face, and the pair is reported
buried, not visible. Before 0.198.0 a pair was buried only inside a solid
with matter on BOTH sides of the plane, so a chair and the floor module it
stands in, both bottoms on the slab and facing down into it, read as
flicker: cold run 9189's deli_a01, office and rail_station_a02 reported 198,
121 and 117 pairs, and judged by what their faces face, 2, 2 and 1.
'''))

EDITS.append((
    "OCCLUDE_MARGIN = 0.003   # solid cover needed on BOTH sides of a buried plane\n",
    '''OCCLUDE_MARGIN = 0.003   # how far past the plane a covering solid must reach
# The composer sinks wall-family modules this far (themed_tscn.SLAB_CAP_SINK,
# mirrored here so this gate stays free of the scene exporter; a test pins the
# two together), which leaves their caps 4 mm under the slab above them.
SLAB_CAP_SINK = 0.004
# How close to the plane, on the side the faces face, matter must start to
# shut them (0.198.0): the composer's own sink plus this gate's tolerance. A
# slot that thin holds no camera. Nothing in cold run 9189's buildings needed
# more, and a 5 cm gap read the same.
OUTWARD_GAP = SLAB_CAP_SINK + TOL
'''))

OLD_VISIBLE = '''def visible_fights(named_boxes, tol=TOL, area_min=AREA_MIN, pen_min=PEN_MIN,
                   margin=OCCLUDE_MARGIN):
    """coplanar_fights minus pairs whose shared face region is ENTOMBED: fully
    inside a third opaque solid with at least `margin` of matter on both sides
    of the plane. A face no camera can reach cannot flicker -- end-faces of a
    wall run buried in the perpendicular wall's band, or co-sunk junction caps
    inside a slab, are geometry meeting the way DC intends, not defects.

    Returns (visible, suppressed) -- both lists of finding dicts."""
    raw = coplanar_fights(named_boxes, tol, area_min, pen_min)
    visible, suppressed = [], []
    for f in raw:
        ax, plane, rlo, rhi = f.pop("_rect")
        i, j = f.pop("_ij")
        o = [k for k in range(3) if k != ax]
        # covers: solids (other than the pair) with solid matter on both
        # sides of the plane. One may bury the region alone, or several may
        # bury it TOGETHER -- adjacent wall segments split exactly where a
        # partition lands, so joint coverage is the common case, not the edge.
        cands = []
        for k, (nm, (slo, shi)) in enumerate(named_boxes):
            if k in (i, j):
                continue
            if slo[ax] <= plane - margin and shi[ax] >= plane + margin:
                cands.append((nm, slo, shi))
        buried_in = None
        for nm, slo, shi in cands:
            if all(slo[q] <= rlo[q] + tol and shi[q] >= rhi[q] - tol
                   for q in o):
                buried_in = nm
                break
        if buried_in is None:
            for u, v in ((o[0], o[1]), (o[1], o[0])):
                ivs = [(slo[u], shi[u]) for nm, slo, shi in cands
                       if slo[v] <= rlo[v] + tol and shi[v] >= rhi[v] - tol]
                if _union_covers(ivs, rlo[u], rhi[u], tol):
                    buried_in = "(joint cover)"
                    break
        if buried_in is not None:
            f["buried_in"] = buried_in
            suppressed.append(f)
        else:
            visible.append(f)
    return visible, suppressed
'''

NEW_VISIBLE = '''def visible_fights(named_boxes, tol=TOL, area_min=AREA_MIN, pen_min=PEN_MIN,
                   margin=OCCLUDE_MARGIN, gap=OUTWARD_GAP):
    """coplanar_fights minus pairs whose shared face region is SHUT on the side
    the two faces face: solid matter starting within `gap` of the plane on
    that side and reaching at least `margin` past it, covering the region
    alone or together. A face no camera can reach cannot flicker -- end-faces
    of a wall run buried in the perpendicular wall's band, co-sunk junction
    caps under a slab, the bottoms of a piece and the floor module it stands
    in, pressed on the slab -- geometry meeting the way DC intends.

    THE FACING SIDE, not both sides (0.198.0). A min face looks down its axis
    and a max face up it, and both faces of a pair look the same way. Until
    0.198.0 a cover needed matter on BOTH sides of the plane, which buried a
    face inside a wall band and nothing pressed against a slab: on cold run
    9189's deli_a01, 198 visible pairs, of which 2 have an open side.
    Matter on both sides is matter on the facing side, so every pair the old
    rule buried, this one buries too.

    Returns (visible, suppressed) -- both lists of finding dicts."""
    raw = coplanar_fights(named_boxes, tol, area_min, pen_min)
    visible, suppressed = [], []
    for f in raw:
        ax, plane, rlo, rhi = f.pop("_rect")
        i, j = f.pop("_ij")
        o = [k for k in range(3) if k != ax]
        # covers: solids (other than the pair) on the side the faces face,
        # from within `gap` of the plane to at least `margin` past it. One may
        # shut the region alone, or several TOGETHER -- adjacent wall segments
        # split exactly where a partition lands, slab tiles meet under a desk
        # in a 2 x 2 corner -- so joint coverage is the common case.
        cands = []
        for k, (nm, (slo, shi)) in enumerate(named_boxes):
            if k in (i, j):
                continue
            if f["side"] == "min":
                if slo[ax] <= plane - margin and shi[ax] >= plane - gap:
                    cands.append((nm, slo, shi))
            elif shi[ax] >= plane + margin and slo[ax] <= plane + gap:
                cands.append((nm, slo, shi))
        buried_in = None
        for nm, slo, shi in cands:
            if all(slo[q] <= rlo[q] + tol and shi[q] >= rhi[q] - tol
                   for q in o):
                buried_in = nm
                break
        if buried_in is None and _rect_covered(
                [(slo, shi) for _nm, slo, shi in cands], rlo, rhi, o, tol):
            buried_in = "(joint cover)"
        if buried_in is not None:
            f["buried_in"] = buried_in
            suppressed.append(f)
        else:
            visible.append(f)
    return visible, suppressed
'''

EDITS.append((OLD_VISIBLE, NEW_VISIBLE))

EDITS.append((
    '''def _union_covers(intervals, lo, hi, tol):
    """True if the union of 1-D intervals covers [lo, hi] within tol."""
    cur = lo + tol
    for a, b in sorted(intervals):
        if a > cur + tol:
            return False
        cur = max(cur, b)
        if cur >= hi - tol:
            return True
    return cur >= hi - tol
''',
    '''def _rect_covered(boxes, rlo, rhi, o, tol):
    """True if the union of `boxes` covers the rectangle rlo..rhi on the two
    axes `o`, to `tol`. The rectangle is cut on every box edge inside it, and
    every cell's centre must lie in some box.

    2-D, not 1-D (0.198.0). The 1-D union it replaces needed one box to span
    the whole rectangle across, so four slab tiles meeting in a corner under
    a desk covered it and read as uncovered. And `tol` is not optional: 9189's
    slab tiles meet at -9.333000183 and -9.332999944, a float32 seam of
    2.4e-7 m, and a first version without it called every seam a hole."""
    cuts = []
    for q in o:
        c = {rlo[q], rhi[q]}
        for lo, hi in boxes:
            for v in (lo[q], hi[q]):
                if rlo[q] < v < rhi[q]:
                    c.add(v)
        cuts.append(sorted(c))
    for a0, a1 in zip(cuts[0], cuts[0][1:]):
        for b0, b1 in zip(cuts[1], cuts[1][1:]):
            ma, mb = (a0 + a1) / 2.0, (b0 + b1) / 2.0
            if not any(lo[o[0]] - tol <= ma <= hi[o[0]] + tol
                       and lo[o[1]] - tol <= mb <= hi[o[1]] + tol
                       for lo, hi in boxes):
                return False
    return True
'''))


def main():
    data = ZF.read_bytes()
    assert len(data) == 12965, "zfight_gate.py is %d bytes, not the 12,965 read; refusing" % len(data)
    assert b"\r\n" not in data, "CRLF in zfight_gate.py; refusing"
    text = data.decode("utf-8")
    for old, _new in EDITS:
        n = text.count(old)
        assert n == 1, "anchor found %d times, not once: %r" % (n, old[:70])
    for old, new in EDITS:
        text = text.replace(old, new)
    assert "_union_covers" not in text, "a caller of _union_covers remains"
    ZF.write_bytes(text.encode("utf-8"))
    print("zfight_gate.py: %d edits; %d -> %d bytes" % (len(EDITS), len(data), len(text.encode("utf-8"))))


if __name__ == "__main__":
    main()
