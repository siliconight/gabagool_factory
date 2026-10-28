"""Lot: a bank's time-and-temperature sign at its frontage -- Zoo 1.138.0's `price_pylon` form `bank`, placed by the
gas pylon's own planner. Run in a Lot clone's root. Every anchor is asserted to occur exactly once; nothing is written
on a miss.
"""
import pathlib

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


edit("site_furniture.py", [
('''import math
''', '''import math
import re
import zlib
'''),
('''def _piece(name, species, road, kerb, t, offset, yaw_extra=0.0, breaks="",
           blade=None):
    w, d, h = SPECIES[species]
    fw, fd = FOOTPRINT.get(species, (w, d))''',
 '''def _piece(name, species, road, kerb, t, offset, yaw_extra=0.0, breaks="",
           blade=None, dims=None):
    w, d, h = dims or SPECIES[species]
    # a piece sized by its caller (a bank's sign, `plan_pylons`) is its own footprint
    fw, fd = (w, d) if dims else FOOTPRINT.get(species, (w, d))'''),
('''def plan_pylons(roads_list, forecourts, markers=(), standing=(), keep_out=(), findings=None):
    """One `price_pylon` per forecourt: ``forecourts`` is ``[(building id,
    (x, y) canopy centre)]``. Returns the pieces placed; a forecourt with no
    road band, or no clear station, is said into ``findings``."""
    placed = []
    w, d, _h = SPECIES[PYLON_SPECIES]
    for bid, (cx, cy) in forecourts:''',
 '''#: A BANK'S TIME-AND-TEMPERATURE SIGN (Zoo 1.138.0, `price_pylon` form
#: `bank`): the walker's bank list, outside. The gas pylon's frame, smaller --
#: a branch's street sign, not a highway's -- placed by this same planner at
#: the bank's frontage, the door sign standing for the canopy. Its variant is
#: the door sign's (`bank_sign_variant`).
BANK_PYLON_DIMS = (2.4, 0.6, 6.5)
#: Its stations reach past the building's ends: a branch sits close behind its sidewalk (bank_branch_a02 2.2 m, under
#: the 2.4 m face), so no station across its own frontage is clear, and a bank's sign stands at the corner of its lot.
BANK_PYLON_STEPS = tuple([0.0] + [s * k for k in range(2, 26, 2) for s in (1.0, -1.0)])
#: The words Zoo's `storefront_names` reads a bank's door from, and its four
#: names in the pylon's four colourways: the variant mirror Deli Counter keeps
#: (`level_design.bank_teller_variant`), since neither reads Zoo.
BANK_SIGN_WORDS = ("bank", "credit", "savings")
_BANK_NAMES = 4
_SIGN_COLOURWAYS = 4


def is_bank_business(business):
    words = set(w for w in re.split(r"[^a-z]+", str(business or "").lower()) if w)
    return bool(words & set(BANK_SIGN_WORDS))


def bank_sign_variant(business):
    """The `price_pylon` form `bank` variant naming the bank its door sign
    does: ``names[k % 4]`` in ``COLOURWAYS[(k // 7) % 4]``, ``k`` the crc32 of
    the sign's `business` (Zoo's `teller_line_forms.variant_for`)."""
    k = zlib.crc32(str(business or "").encode("utf-8")) & 0xFFFFFFFF
    return k % _BANK_NAMES + _BANK_NAMES * ((k // 7) % _SIGN_COLOURWAYS)


def plan_pylons(roads_list, forecourts, markers=(), standing=(), keep_out=(), findings=None,
                dims=None, dress=None, label="forecourt", steps=PYLON_STEPS):
    """One `price_pylon` per forecourt: ``forecourts`` is ``[(building id,
    (x, y) canopy centre)]``. Returns the pieces placed; a forecourt with no
    road band, or no clear station, is said into ``findings``. ``dims``,
    ``dress`` (building id -> the piece's `form` and `variant`) and ``label``
    are a bank's sign's (`BANK_PYLON_DIMS`): a frontage is a forecourt."""
    placed = []
    w, d, _h = dims or SPECIES[PYLON_SPECIES]
    for bid, (cx, cy) in forecourts:'''),
('''            _say(findings, f"LOT_PYLON_NO_FRONTAGE: no road with a sidewalk for {bid}'s forecourt")''',
 '''            _say(findings, f"LOT_PYLON_NO_FRONTAGE: no road with a sidewalk for {bid}'s {label}")'''),
('''            cand = _piece(f"Pylon_{bid}", PYLON_SPECIES, road, kerb, s, offset, 90.0,
                          breaks=f"forecourt {bid}")''',
 '''            cand = _piece(f"Pylon_{bid}", PYLON_SPECIES, road, kerb, s, offset, 90.0,
                          breaks=f"{label} {bid}", dims=dims)
            for k, v in ((dress or {}).get(bid) or {}).items():
                if v:
                    cand[k] = v'''),
('''            _say(findings, f"LOT_PYLON_NO_ROOM: no clear station for {bid}'s pylon within "
                           f"{max(PYLON_STEPS):.0f} m of its forecourt on road {road.index}")''',
 '''            _say(findings, f"LOT_PYLON_NO_ROOM: no clear station for {bid}'s pylon within "
                           f"{max(steps):.0f} m of its {label} on road {road.index}")'''),
('''        for dt in PYLON_STEPS:''', '''        for dt in steps:'''),
])

edit("lot.py", [
('''#: Every POINT a light anchor carries, each moved into site space with its''',
 '''def bank_fronts(site_spec, base_dir):
    """``[(building id, (x, y), business)]``: every building whose door sign
    reads as a bank's (`site_furniture.is_bank_business`, the words Zoo's
    sign reads one from), with that sign's anchor in site space -- where its
    time-and-temperature sign looks for frontage, as a gas station's pylon
    looks from its canopy (`forecourts`)."""
    import site_furniture
    out = []
    for b in site_spec.get("buildings") or []:
        ref = _lights_ref_for(b)
        if not ref:
            continue
        lp = os.path.join(base_dir, ref)
        if not os.path.exists(lp):
            continue
        with open(lp, encoding="utf-8") as f:
            lm = json.load(f)
        placement = {"at": b["at"], "rot": b.get("rot", 0)}
        for a in lm.get("anchors", []):
            if a.get("type") == "sign" and site_furniture.is_bank_business(a.get("business")):
                x, y, z = a.get("pos", [0.0, 0.0, 0.0])
                wx, wy, _wz = _place_point(x, y, z, placement)
                out.append((b["id"], (round(wx, 4), round(wy, 4)), str(a["business"])))
                break
    return out


#: Every POINT a light anchor carries, each moved into site space with its'''),
('''    site_spec["cover"].extend(pylons)
    furniture = furniture + pylons''',
 '''    # ...AND A BANK'S TIME-AND-TEMPERATURE SIGN (Zoo 1.138.0): the same
    # planner at the bank's frontage, after the gas pylons so it yields to
    # them, dressed in the door sign's name and colours
    _banks = bank_fronts(site_spec, base_dir)
    pylons = pylons + site_furniture.plan_pylons(
        site_streets.roads(site_spec), [(bid, at) for bid, at, _b in _banks],
        list(cover_points.values()), standing=_standing0 + [site_furniture._piece_rect(_p) for _p in pylons],
        keep_out=site_furniture.path_corridors(site_spec) + _site_spawns.footprints(site_spec, margin=0.5)
        + _field_rects,
        findings=furniture_findings, dims=site_furniture.BANK_PYLON_DIMS, steps=site_furniture.BANK_PYLON_STEPS,
        dress={bid: {"form": "bank", "variant": site_furniture.bank_sign_variant(bus)} for bid, _at, bus in _banks},
        label="frontage")
    site_spec["cover"].extend(pylons)
    furniture = furniture + pylons'''),
])

src, dst = pathlib.Path(__file__).parent / "test_bank_sign.py", R / "tests" / "test_bank_sign.py"
assert not dst.exists(), dst
dst.write_bytes(src.read_bytes())
print(dst, "written")
