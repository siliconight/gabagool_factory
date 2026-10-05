"""Patina 0.27.0: an Empty's openings get stone lintels and sills -- a lintel
over every window and door, a sill under every window -- for Zoo (>= 1.71.0)
to build. The walker's South Philly photograph: "white stone lintels and sills
over and under every window". See `patina_opening_trim/CHANGELOG_0.27.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  patina/framing.py   opening_trim_orders
  patina/openings.py  EXEMPT names lintel and window_sill
  patina/cli.py       --dressing with a slots.json orders them, beside the
                      window fixtures
  patina/version.py   0.27.0
  tests/test_openings.py  the exemption pin moves with the decision
Copies the test; CHANGELOG and VERSION.

    python patch_patina_opening_trim.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
PA = HERE.parent / "patina"
SRC = HERE / "patina_opening_trim"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


FRAMING_ANCHOR = '''def roofline_slots(manifest: SlotManifest) -> list:
'''
FRAMING_NEW = '''def opening_trim_orders(manifest: SlotManifest, regions: list, *,
                        seed: int) -> list[dict]:
    """AN EMPTY'S STONE LINTELS AND SILLS (0.27.0), as Zoo (>= 1.71.0) builds
    them. The walker's South Philly photograph: "white stone lintels and
    sills over and under every window".

    * ``lintel`` -- one per opening of a facade window or doorway, at the
      opening's HEAD on the wall face; Zoo stands the block on that line.
    * ``window_sill`` -- one per opening of a facade window, at its SILL on
      the wall face; Zoo hangs the block below that line. A door has none:
      its threshold is the sidewalk's.

    ONLY ON A FACADE SLOT (`glazing: "facade"`), as the window fixtures are,
    and for the same reason they are exempt from the opening keep-out
    (`openings.EXEMPT`): they sit on the opening's own head and sill, inside
    its margin, and the opening is sealed. ``size2`` is the opening.
    """
    uv = _uv(regions, "frame")
    orders = []
    center = footprint_center(manifest)
    thick_m = modal_thickness(manifest)
    for s in manifest.slots:
        if s.role not in ("window", "doorway") or s.glazing != "facade" or not s.dims:
            continue
        frame = wall_frame(s, center, thick_m)
        base_z = _base_z(s)
        for k, op in enumerate(s.openings):
            ow = float(op.get("width", 0.0))
            oh = float(op.get("height", 0.0))
            if ow <= 0.0 or oh <= 0.0:
                continue
            sill = float(op.get("sill", 0.0))
            trims = [("lintel", base_z + sill + oh)]
            if s.role == "window":
                trims.append(("window_sill", base_z + sill))
            for cover, z in trims:
                pos, n = _face(s, 0.0, z, frame)
                rng = rng_for(seed, cover, s.slot_id, str(k))
                orders.append({
                    "anchor_kind": "opening_trim",
                    "cover": cover,
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


def roofline_slots(manifest: SlotManifest) -> list:
'''

EXEMPT_OLD = '''#: Deli Counter seals an Empty and records no gameplay openings on it, so no
#: body or shot uses the hole they stand in.
EXEMPT = ("frame", "window_bars", "ac_unit")
'''
EXEMPT_NEW = '''#: Deli Counter seals an Empty and records no gameplay openings on it, so no
#: body or shot uses the hole they stand in. Its stone `lintel` and
#: `window_sill` (0.27.0) sit on the same sealed opening's head and sill,
#: inside its margin, and are exempt for the same reason.
EXEMPT = ("frame", "window_bars", "ac_unit", "lintel", "window_sill")
'''

CLI_OLD = '''            if slot_manifest is not None and not args.anchor_patina_space:
                panels += framing.window_fixture_orders(
                    slot_manifest, regions, seed=args.seed)
'''
CLI_NEW = '''            if slot_manifest is not None and not args.anchor_patina_space:
                panels += framing.window_fixture_orders(
                    slot_manifest, regions, seed=args.seed)
                # 0.27.0: and the stone lintels and sills of the same
                # sealed openings
                panels += framing.opening_trim_orders(
                    slot_manifest, regions, seed=args.seed)
'''

TEST_OLD = '''def test_the_exemptions_are_the_listed_three():
    """Surrounding an opening is the entire point of a frame. An Empty's
    window fixtures (0.26.0) stand IN their sealed opening -- the second and
    third exemptions, added deliberately, which is what this pin is for."""
'''
TEST_NEW = '''def test_the_exemptions_are_the_listed_five():
    """Surrounding an opening is the entire point of a frame. An Empty's
    window fixtures (0.26.0) stand IN their sealed opening, and its stone
    lintel and sill (0.27.0) on that opening's head and sill -- each added
    deliberately, which is what this pin is for."""
'''
TEST_PIN_OLD = '''    assert openings.EXEMPT == ("frame", "window_bars", "ac_unit"), \\
        "adding another must be deliberate"
'''
TEST_PIN_NEW = '''    assert openings.EXEMPT == ("frame", "window_bars", "ac_unit", "lintel", "window_sill"), \\
        "adding another must be deliberate"
'''

VER_OLD = '__version__ = "0.26.0"\n'
VER_NEW = '__version__ = "0.27.0"\n'


def main():
    assert (PA / "VERSION").read_text(encoding="utf-8").strip() == "Patina 0.26.0"
    _edit(PA / "patina" / "framing.py", [(FRAMING_ANCHOR, FRAMING_NEW)])
    _edit(PA / "patina" / "openings.py", [(EXEMPT_OLD, EXEMPT_NEW)])
    _edit(PA / "patina" / "cli.py", [(CLI_OLD, CLI_NEW)])
    _edit(PA / "patina" / "version.py", [(VER_OLD, VER_NEW)])
    _edit(PA / "tests" / "test_openings.py", [(TEST_OLD, TEST_NEW), (TEST_PIN_OLD, TEST_PIN_NEW)])
    shutil.copyfile(SRC / "test_opening_trim.py", PA / "tests" / "test_opening_trim.py")
    ch = PA / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    head = "## [0.26.0]"
    assert s.count(head) == 1
    ch.write_text(s.replace(head, (SRC / "CHANGELOG_0.27.0.md").read_text(encoding="utf-8").rstrip("\n")
                            + "\n\n" + head), encoding="utf-8", newline="\n")
    (PA / "VERSION").write_text("Patina 0.27.0", encoding="utf-8", newline="\n")
    print("applied Patina 0.27.0")


if __name__ == "__main__":
    main()
