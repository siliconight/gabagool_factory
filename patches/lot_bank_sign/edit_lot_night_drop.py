"""Lot: a bank's night depository beside its door (`site_night_drop`), a hung piece as a poster run is. Run in a Lot
clone's root, after edit_lot_driveup.py. Every anchor is asserted to occur exactly once; nothing is written on a miss.
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


for name, rel in (("site_night_drop.py", "site_night_drop.py"), ("test_site_night_drop.py", "tests/test_site_night_drop.py")):
    dst = R / rel
    assert not dst.exists(), dst
    dst.write_bytes((HERE / name).read_bytes())
    print(dst, "written")

edit("lot.py", [
('''    merged["poster_plan"] = {"placed": site_spec["hung"]}
    for f_ in poster_findings:
        print(f"[lot] {f_}")''',
 '''    merged["poster_plan"] = {"placed": site_spec["hung"]}
    for f_ in poster_findings:
        print(f"[lot] {f_}")
    # A BANK'S NIGHT DEPOSITORY (site_night_drop, Zoo 1.138.0): beside the
    # door its sign is over, clear of the facade's openings; hung, as a
    # poster run is, so never cover
    import site_night_drop
    _nd_findings = []
    site_spec["hung"] += site_night_drop.plan(site_spec, merged, _banks_du, _rects_f, _nd_findings)
    for f_ in _nd_findings:
        print(f"[lot] {f_}")'''),
])
