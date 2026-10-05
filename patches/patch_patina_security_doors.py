"""Patina 0.28.0: an Empty's iron security door, ordered from the
`security_door` Deli Counter (>= 0.182.0) writes on a facade front door's slot,
for Zoo (>= 1.72.0) to build. See `patina_security_doors/CHANGELOG_0.28.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  patina/slots.py     Slot carries security_door; parse reads it
  patina/framing.py   door_fixture_orders
  patina/openings.py  EXEMPT names security_door
  patina/cli.py       --dressing with a slots.json orders it
  patina/version.py   0.28.0
  tests/test_openings.py  the exemption pin moves with the decision
Copies the test; CHANGELOG and VERSION.

    python patch_patina_security_doors.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
PA = HERE.parent / "patina"
SRC = HERE / "patina_security_doors"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


FIELD_OLD = '''    ac: bool = False
    bars: bool = False
'''
FIELD_NEW = '''    ac: bool = False
    bars: bool = False
    # and an Empty front door's iron security door (Deli Counter >= 0.182.0),
    # read by `framing.door_fixture_orders` (0.28.0)
    security_door: bool = False
'''

PARSE_OLD = '''            bars=bool(r.get("bars", False)),
'''
PARSE_NEW = '''            bars=bool(r.get("bars", False)),
            security_door=bool(r.get("security_door", False)),
'''

FRAMING_ANCHOR = '''def opening_trim_orders(manifest: SlotManifest, regions: list, *,
                        seed: int) -> list[dict]:
'''
FRAMING_NEW = '''def door_fixture_orders(manifest: SlotManifest, regions: list, *,
                        seed: int) -> list[dict]:
    """AN EMPTY'S IRON SECURITY DOOR (0.28.0), as Zoo (>= 1.72.0) builds it:
    one ``security_door`` per opening of a facade doorway whose slot carries
    `security_door` (Deli Counter >= 0.182.0 writes it on the front door of a
    house that has one), at the opening's centre on the wall face, sized to
    it. Zoo hangs it in the reveal, in front of the leaf.

    ONLY ON A FACADE DOORWAY, as the window fixtures are: a real door is a way
    in. The slot is the opt-in, and the cover is exempt from the opening
    keep-out (`openings.EXEMPT`)."""
    uv = _uv(regions, "frame")
    orders = []
    center = footprint_center(manifest)
    thick_m = modal_thickness(manifest)
    for s in manifest.slots:
        if (s.role != "doorway" or s.glazing != "facade" or not s.dims
                or not s.security_door):
            continue
        frame = wall_frame(s, center, thick_m)
        base_z = _base_z(s)
        for k, op in enumerate(s.openings):
            ow = float(op.get("width", 0.0))
            oh = float(op.get("height", 0.0))
            if ow <= 0.0 or oh <= 0.0:
                continue
            sill = float(op.get("sill", 0.0))
            pos, n = _face(s, 0.0, base_z + sill + oh / 2.0, frame)
            rng = rng_for(seed, "security_door", s.slot_id, str(k))
            orders.append({
                "anchor_kind": "door_fixture",
                "cover": "security_door",
                "collision": "none",
                "trim_piece": "frame",
                "uv_region": uv,
                "slot_id": s.slot_id,
                "pos": pos, "normal": n,
                "size": round(ow, 3),
                "size2": [round(ow, 3), round(oh, 3)],
                "seed_offset": int(rng.integers(0, 1_000_000)),
            })
    return orders


def opening_trim_orders(manifest: SlotManifest, regions: list, *,
                        seed: int) -> list[dict]:
'''

EXEMPT_OLD = '''#: `window_sill` (0.27.0) sit on the same sealed opening's head and sill,
#: inside its margin, and are exempt for the same reason.
EXEMPT = ("frame", "window_bars", "ac_unit", "lintel", "window_sill")
'''
EXEMPT_NEW = '''#: `window_sill` (0.27.0) sit on the same sealed opening's head and sill,
#: inside its margin, and are exempt for the same reason. So is the iron
#: `security_door` (0.28.0) hung in a sealed front door's reveal.
EXEMPT = ("frame", "window_bars", "ac_unit", "lintel", "window_sill", "security_door")
'''

CLI_OLD = '''                panels += framing.opening_trim_orders(
                    slot_manifest, regions, seed=args.seed)
'''
CLI_NEW = '''                panels += framing.opening_trim_orders(
                    slot_manifest, regions, seed=args.seed)
                # 0.28.0: and a secured front door's iron security door
                panels += framing.door_fixture_orders(
                    slot_manifest, regions, seed=args.seed)
'''

TEST_OLD = '''def test_the_exemptions_are_the_listed_five():
    """Surrounding an opening is the entire point of a frame. An Empty's
    window fixtures (0.26.0) stand IN their sealed opening, and its stone
    lintel and sill (0.27.0) on that opening's head and sill -- each added
    deliberately, which is what this pin is for."""
'''
TEST_NEW = '''def test_the_exemptions_are_the_listed_six():
    """Surrounding an opening is the entire point of a frame. An Empty's
    window fixtures (0.26.0) stand IN their sealed opening, its stone lintel
    and sill (0.27.0) on that opening's head and sill, and its iron security
    door (0.28.0) in a sealed doorway's reveal -- each added deliberately,
    which is what this pin is for."""
'''
TEST_PIN_OLD = '''    assert openings.EXEMPT == ("frame", "window_bars", "ac_unit", "lintel", "window_sill"), \\
'''
TEST_PIN_NEW = '''    assert openings.EXEMPT == ("frame", "window_bars", "ac_unit", "lintel", "window_sill",
                               "security_door"), \\
'''

VER_OLD = '__version__ = "0.27.0"\n'
VER_NEW = '__version__ = "0.28.0"\n'


def main():
    assert (PA / "VERSION").read_text(encoding="utf-8").strip() == "Patina 0.27.0"
    _edit(PA / "patina" / "slots.py", [(FIELD_OLD, FIELD_NEW), (PARSE_OLD, PARSE_NEW)])
    _edit(PA / "patina" / "framing.py", [(FRAMING_ANCHOR, FRAMING_NEW)])
    _edit(PA / "patina" / "openings.py", [(EXEMPT_OLD, EXEMPT_NEW)])
    _edit(PA / "patina" / "cli.py", [(CLI_OLD, CLI_NEW)])
    _edit(PA / "patina" / "version.py", [(VER_OLD, VER_NEW)])
    _edit(PA / "tests" / "test_openings.py", [(TEST_OLD, TEST_NEW), (TEST_PIN_OLD, TEST_PIN_NEW)])
    shutil.copyfile(SRC / "test_security_doors.py", PA / "tests" / "test_security_doors.py")
    ch = PA / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    head = "## [0.27.0]"
    assert s.count(head) == 1
    ch.write_text(s.replace(head, (SRC / "CHANGELOG_0.28.0.md").read_text(encoding="utf-8").rstrip("\n")
                            + "\n\n" + head), encoding="utf-8", newline="\n")
    (PA / "VERSION").write_text("Patina 0.28.0", encoding="utf-8", newline="\n")
    print("applied Patina 0.28.0")


if __name__ == "__main__":
    main()
