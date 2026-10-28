"""Lot: a bank's drive-up lane (`site_driveup`), planned before the parking fields, paved as a field is, its
driveway a kerb cut, its canopy and station Zoo 1.138.0's. Run in a Lot clone's root, after edit_lot_bank_sign.py.
Every anchor is asserted to occur exactly once; nothing is written on a miss.
"""
import pathlib

HERE = pathlib.Path(__file__).parent
R = pathlib.Path.cwd()


def edit(rel, pairs):
    p = R / rel
    t = p.read_bytes().decode("utf-8")
    crlf = "\r\n" in t
    t = t.replace("\r\n", "\n")
    for a, b in pairs:
        assert t.count(a) == 1, (rel, t.count(a), a[:80])
        t = t.replace(a, b)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print(p, "edited")


for name, rel in (("site_driveup.py", "site_driveup.py"), ("test_site_driveup.py", "tests/test_site_driveup.py")):
    dst = R / rel
    assert not dst.exists(), dst
    dst.write_bytes((HERE / name).read_bytes())
    print(dst, "written")

edit("lot.py", [
('''def field_slabs(site_spec):
    """One slab per parking field (`site_fields`, 0.94.0), `field_<i>`, top
    at FIELD_THICK, turned to its road: local x runs along the road."""
    out = []
    for i, f in enumerate(site_spec.get("fields", []) or []):
        cx, cy = f["at"]
        sx, sy = f["size"]
        out.append(_surface_slab(f"field_{i}", "parking",
                                 (sx, FIELD_THICK + GROUND_SINK, sy),
                                 (cx, (FIELD_THICK - GROUND_SINK) / 2, -cy),
                                 f["yaw_deg"], FIELD_THICK))
    return out''',
 '''def field_slabs(site_spec):
    """One slab per parking field (`site_fields`, 0.94.0), `field_<i>`, top
    at FIELD_THICK, turned to its road: local x runs along the road. And one
    per bank's drive-up (`site_driveup`), `driveup_<i>`: the same asphalt at
    the same height, so every reader of the drawn surfaces sees it."""
    out = []
    for i, f in enumerate(site_spec.get("fields", []) or []):
        cx, cy = f["at"]
        sx, sy = f["size"]
        out.append(_surface_slab(f"field_{i}", "parking",
                                 (sx, FIELD_THICK + GROUND_SINK, sy),
                                 (cx, (FIELD_THICK - GROUND_SINK) / 2, -cy),
                                 f["yaw_deg"], FIELD_THICK))
    for i, d in enumerate(site_spec.get("driveups", []) or []):
        cx, cy = d["at"]
        sx, sy = d["size"]
        out.append(_surface_slab(f"driveup_{i}", "parking",
                                 (sx, FIELD_THICK + GROUND_SINK, sy),
                                 (cx, (FIELD_THICK - GROUND_SINK) / 2, -cy),
                                 d["yaw_deg"], FIELD_THICK))
    return out'''),
('''    fields = site_fields.plan_fields(site_spec, _fs.roads(site_spec),''',
 '''    # A BANK'S DRIVE-UP (site_driveup, Zoo 1.138.0), BEFORE the fields: a
    # bank's own lane claims its side before a gap is offered to parking, and
    # the fields keep off it as they keep off what stands
    import site_driveup
    import site_furniture as _sf_bank
    _banks_du = bank_fronts(site_spec, base_dir)
    driveups, driveup_pieces = site_driveup.plan_driveups(
        _banks_du, _fs.roads(site_spec), _fsurf.tops(site_spec, ground=extent), _rects_f,
        standing=_standing_f, ground=extent.rect, markers=list(cover_points.values()),
        variants={bid: _sf_bank.bank_sign_variant(bus) for bid, _at, bus in _banks_du})
    site_spec["driveups"] = driveups
    _standing_f = _standing_f + [tuple(d["rect"]) for d in driveups]
    for _d in driveups:
        print(f"[lot] LOT_DRIVEUP_PLACED: {_d['name']} on road {_d['road']} kerb {_d['side']}, "
              f"served lane runs {_d['served_travel']} the road")
    fields = site_fields.plan_fields(site_spec, _fs.roads(site_spec),'''),
('''    site_spec["driveways"] = [f["driveway"] for f in fields]''',
 '''    site_spec["driveways"] = [f["driveway"] for f in fields] + [d["driveway"] for d in driveups]'''),
('''    _field_rects = [tuple(f["rect"]) for f in fields]''',
 '''    # the drive-up's canopy and station stand as pieces; its block is kept off as a field's is
    site_spec["cover"].extend(driveup_pieces)
    _field_rects = [tuple(f["rect"]) for f in fields] + [tuple(d["rect"]) for d in driveups]'''),
])
