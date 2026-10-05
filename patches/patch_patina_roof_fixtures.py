"""Patina 0.29.0: an Empty's TV antenna and satellite dish, ordered on its roof
from the `antenna` / `dish` / `front` Deli Counter (>= 0.185.0) writes on the
roof slot, for Zoo (>= 1.74.0) to build. See
`patina_roof_fixtures/CHANGELOG_0.29.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  patina/slots.py     Slot carries antenna, dish, front; parse reads them
  patina/framing.py   roof_fixture_orders and its placement constants
  patina/openings.py  EXEMPT names tv_antenna and sat_dish
  patina/cli.py       --dressing with a slots.json orders them
  patina/version.py   0.29.0
  tests/test_openings.py  the exemption pin moves with the decision
Copies the test; CHANGELOG and VERSION.

    python patch_patina_roof_fixtures.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
PA = HERE.parent / "patina"
SRC = HERE / "patina_roof_fixtures"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


FIELD_OLD = '''    # and an Empty front door's iron security door (Deli Counter >= 0.182.0),
    # read by `framing.door_fixture_orders` (0.28.0)
    security_door: bool = False
'''
FIELD_NEW = '''    # and an Empty front door's iron security door (Deli Counter >= 0.182.0),
    # read by `framing.door_fixture_orders` (0.28.0)
    security_door: bool = False
    # and an Empty roof's TV antenna and satellite dish, with the facing of
    # the front they are set back from (Deli Counter >= 0.185.0), read by
    # `framing.roof_fixture_orders` (0.29.0)
    antenna: bool = False
    dish: bool = False
    front: Optional[str] = None
'''

PARSE_OLD = '''            security_door=bool(r.get("security_door", False)),
        ))
'''
PARSE_NEW = '''            security_door=bool(r.get("security_door", False)),
            antenna=bool(r.get("antenna", False)),
            dish=bool(r.get("dish", False)),
            front=r.get("front"),
        ))
'''

FRAMING_ANCHOR = '''

def roofline_slots(manifest: SlotManifest) -> list:
'''
FRAMING_NEW = '''

#: AN EMPTY'S ROOF FIXTURES (0.29.0): where they stand, measured back into the
#: roof from the inner face of the front parapet. From across the road -- an
#: eye at 1.6 m some 14 m from the facade -- anything less than about 0.6 m
#: over the parapet per metre behind it is hidden, so both stand near the
#: front. The antenna 1.0 to 1.6 m back, within 15 % of the roof's width of
#: its centreline, its mast and boom drawn per house; the dish 0.25 m back
#: and 18 to 32 % out on the other half, so the two never share a footing,
#: its bowl's centre `DISH_ABOVE_PARAPET` over the parapet's top.
ANTENNA_SETBACK = (1.0, 1.6)
ANTENNA_ACROSS = 0.15
ANTENNA_MAST = (2.6, 3.4)
ANTENNA_BOOM = (1.6, 2.6)
DISH_SETBACK = 0.25
DISH_ACROSS = (0.18, 0.32)
DISH_ABOVE_PARAPET = 0.6
DISH_WIDTH = 0.5
#: Bearings in the building's own frame -- Deli Counter's facings, N = +y and
#: E = +x -- as compass degrees. Philadelphia's TV transmitters stand in
#: Roxborough, north-west of South Philly, so a rowhouse antenna points about
#: 325; the DSS satellites sit at 101 W, so a Philadelphia dish looks about
#: 211, SSW (and up 41 degrees, Zoo's `DISH_TILT`). A building turned at
#: placement turns its fixtures with it; Level Factory's terrace turns every
#: house of a row the same way, so a row's antennas point one way, which is
#: what a street shows.
ANTENNA_BEARING = 325.0
DISH_BEARING = 211.0
_FACING = {"N": (0.0, 1.0), "E": (1.0, 0.0), "S": (0.0, -1.0), "W": (-1.0, 0.0)}


def _bearing(deg: float) -> list:
    r = math.radians(deg)
    return [round(math.sin(r), 4), round(math.cos(r), 4), 0.0]


def _parapet(manifest: SlotManifest, front: str) -> tuple:
    """``(thickness, height)`` of the front's parapet -- Deli Counter (>= 0.177.0)
    names its tiles `parapet_<facing>_...` -- or ``(0.0, 0.0)`` with none."""
    for s in manifest.slots:
        if str(s.slot_id).startswith(f"parapet_{front}_") and s.dims:
            w, d, h = s.size()
            return min(w, d), h
    return 0.0, 0.0


def roof_fixture_orders(manifest: SlotManifest, regions: list, *,
                        seed: int) -> list[dict]:
    """AN EMPTY'S TV ANTENNA AND SATELLITE DISH (0.29.0), as Zoo (>= 1.74.0)
    builds them: a ``tv_antenna`` and a ``sat_dish`` on the roof's top
    surface, up-facing, each with the bearing it looks along as its
    ``tangent``.

    Deli Counter (>= 0.185.0) writes `antenna` / `dish` on an Empty's roof
    slot with `front`, the facing of the wall that holds its front door. THE
    SLOT IS THE OPT-IN, as a window's fixtures are; one with no `front` orders
    nothing, since there is no parapet to set them back from. Exempt from the
    opening keep-out (`openings.EXEMPT`): nothing walks or shoots across an
    Empty's roof.

    Each house draws its own antenna, its place and the dish's side from
    ``(seed, kind, building, slot)``: every Empty's roof slot is
    `roof_footprint`, so keyed by the slot alone the street would draw one.
    """
    uv = _uv(regions, "frame")
    orders = []
    for s in manifest.slots:
        if s.role != "roof" or not s.dims or not (s.antenna or s.dish):
            continue
        f = _FACING.get(str(s.front or ""))
        if f is None:
            continue
        w, d, _h = s.size()
        rad = math.radians(float(s.rot_y))
        a = (math.cos(rad), math.sin(rad))            # the slot's local x
        b = (-math.sin(rad), math.cos(rad))           # and its local y
        p = (-f[1], f[0])                             # across the house
        half = (abs(f[0] * a[0] + f[1] * a[1]) * w + abs(f[0] * b[0] + f[1] * b[1]) * d) / 2.0
        across = abs(p[0] * a[0] + p[1] * a[1]) * w + abs(p[0] * b[0] + p[1] * b[1]) * d
        thick, par_h = _parapet(manifest, str(s.front))
        inner = half - thick
        top = s.base_z() + s.size()[2]
        cx, cy = float(s.translation[0]), float(s.translation[1])

        def at(back, off):
            return [round(cx + f[0] * (inner - back) + p[0] * off, 3),
                    round(cy + f[1] * (inner - back) + p[1] * off, 3), round(top, 3)]

        side = 1.0
        if s.antenna:
            rng = rng_for(seed, "tv_antenna", manifest.building_id, s.slot_id)
            back = float(rng.uniform(*ANTENNA_SETBACK))
            off = float(rng.uniform(-ANTENNA_ACROSS, ANTENNA_ACROSS)) * across
            mast = round(float(rng.uniform(*ANTENNA_MAST)), 3)
            boom = round(float(rng.uniform(*ANTENNA_BOOM)), 3)
            side = -1.0 if off >= 0.0 else 1.0
            orders.append({
                "anchor_kind": "roof_fixture", "cover": "tv_antenna", "collision": "none",
                "trim_piece": "frame", "uv_region": uv, "slot_id": s.slot_id,
                "pos": at(back, off), "normal": [0.0, 0.0, 1.0],
                "tangent": _bearing(ANTENNA_BEARING),
                "size": boom, "size2": [boom, mast],
                "seed_offset": int(rng.integers(0, 1_000_000)),
            })
        if s.dish:
            rng = rng_for(seed, "sat_dish", manifest.building_id, s.slot_id)
            if not s.antenna:
                side = 1.0 if rng.uniform() < 0.5 else -1.0
            off = side * float(rng.uniform(*DISH_ACROSS)) * across
            orders.append({
                "anchor_kind": "roof_fixture", "cover": "sat_dish", "collision": "none",
                "trim_piece": "frame", "uv_region": uv, "slot_id": s.slot_id,
                "pos": at(DISH_SETBACK, off), "normal": [0.0, 0.0, 1.0],
                "tangent": _bearing(DISH_BEARING),
                "size": DISH_WIDTH,
                "size2": [DISH_WIDTH, round(par_h + DISH_ABOVE_PARAPET, 3)],
                "seed_offset": int(rng.integers(0, 1_000_000)),
            })
    return orders


def roofline_slots(manifest: SlotManifest) -> list:
'''

EXEMPT_OLD = '''#: inside its margin, and are exempt for the same reason. So is the iron
#: `security_door` (0.28.0) hung in a sealed front door's reveal.
EXEMPT = ("frame", "window_bars", "ac_unit", "lintel", "window_sill", "security_door")
'''
EXEMPT_NEW = '''#: inside its margin, and are exempt for the same reason. So is the iron
#: `security_door` (0.28.0) hung in a sealed front door's reveal, and the
#: roof's `tv_antenna` and `sat_dish` (0.29.0): nothing walks or shoots
#: across an Empty's roof.
EXEMPT = ("frame", "window_bars", "ac_unit", "lintel", "window_sill", "security_door",
          "tv_antenna", "sat_dish")
'''

CLI_OLD = '''                # 0.28.0: and a secured front door's iron security door
                panels += framing.door_fixture_orders(
                    slot_manifest, regions, seed=args.seed)
'''
CLI_NEW = '''                # 0.28.0: and a secured front door's iron security door
                panels += framing.door_fixture_orders(
                    slot_manifest, regions, seed=args.seed)
                # 0.29.0: and the TV antenna and satellite dish on its roof
                panels += framing.roof_fixture_orders(
                    slot_manifest, regions, seed=args.seed)
'''

TEST_OLD = '''def test_the_exemptions_are_the_listed_six():
    """Surrounding an opening is the entire point of a frame. An Empty's
    window fixtures (0.26.0) stand IN their sealed opening, its stone lintel
    and sill (0.27.0) on that opening's head and sill, and its iron security
    door (0.28.0) in a sealed doorway's reveal -- each added deliberately,
    which is what this pin is for."""
'''
TEST_NEW = '''def test_the_exemptions_are_the_listed_eight():
    """Surrounding an opening is the entire point of a frame. An Empty's
    window fixtures (0.26.0) stand IN their sealed opening, its stone lintel
    and sill (0.27.0) on that opening's head and sill, its iron security door
    (0.28.0) in a sealed doorway's reveal, and its TV antenna and dish
    (0.29.0) on a roof nothing crosses -- each added deliberately, which is
    what this pin is for."""
'''
TEST_PIN_OLD = '''    assert openings.EXEMPT == ("frame", "window_bars", "ac_unit", "lintel", "window_sill",
                               "security_door"), \\
'''
TEST_PIN_NEW = '''    assert openings.EXEMPT == ("frame", "window_bars", "ac_unit", "lintel", "window_sill",
                               "security_door", "tv_antenna", "sat_dish"), \\
'''

VER_OLD = '__version__ = "0.28.0"\n'
VER_NEW = '__version__ = "0.29.0"\n'


def main():
    assert (PA / "VERSION").read_text(encoding="utf-8").strip() == "Patina 0.28.0"
    _edit(PA / "patina" / "slots.py", [(FIELD_OLD, FIELD_NEW), (PARSE_OLD, PARSE_NEW)])
    _edit(PA / "patina" / "framing.py", [(FRAMING_ANCHOR, FRAMING_NEW)])
    _edit(PA / "patina" / "openings.py", [(EXEMPT_OLD, EXEMPT_NEW)])
    _edit(PA / "patina" / "cli.py", [(CLI_OLD, CLI_NEW)])
    _edit(PA / "patina" / "version.py", [(VER_OLD, VER_NEW)])
    _edit(PA / "tests" / "test_openings.py", [(TEST_OLD, TEST_NEW), (TEST_PIN_OLD, TEST_PIN_NEW)])
    shutil.copyfile(SRC / "test_roof_fixtures.py", PA / "tests" / "test_roof_fixtures.py")
    ch = PA / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    head = "## [0.28.0]"
    assert s.count(head) == 1
    ch.write_text(s.replace(head, (SRC / "CHANGELOG_0.29.0.md").read_text(encoding="utf-8").rstrip("\n")
                            + "\n\n" + head), encoding="utf-8", newline="\n")
    (PA / "VERSION").write_text("Patina 0.29.0", encoding="utf-8", newline="\n")
    print("applied Patina 0.29.0")


if __name__ == "__main__":
    main()
