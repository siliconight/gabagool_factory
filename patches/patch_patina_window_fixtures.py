"""Patina 0.26.0: an Empty's window fixtures -- bars and air conditioners --
ordered from the fields Deli Counter (>= 0.181.0) writes on each sealed window.
See `patina_window_fixtures/CHANGELOG_0.26.0.md`.

Anchored edits (every anchor once; refuses on a miss):
  patina/slots.py     Slot carries glazing, pane, ac, bars; parse reads them
  patina/framing.py   window_fixture_orders
  patina/openings.py  EXEMPT names window_bars and ac_unit beside frame; the
                      proudest-cover comment says it counts judged covers
  patina/gameplay.py  the same comment on its mirror of that constant
  patina/cli.py       --dressing with a slots.json orders them
  patina/version.py   0.26.0
Copies the test; CHANGELOG and VERSION.

    python patch_patina_window_fixtures.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
PA = HERE.parent / "patina"
SRC = HERE / "patina_window_fixtures"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


FIELDS_OLD = '''    openings: list = field(default_factory=list)

    def size(self) -> tuple:
'''
FIELDS_NEW = '''    openings: list = field(default_factory=list)
    # An Empty's window (Deli Counter >= 0.179.0 / 0.181.0): `glazing:
    # "facade"` marks an opening with nothing behind it, `pane` its painted
    # state, `ac` / `bars` what hangs in it -- read by
    # `framing.window_fixture_orders` (0.26.0).
    glazing: Optional[str] = None
    pane: Optional[str] = None
    ac: bool = False
    bars: bool = False

    def size(self) -> tuple:
'''

PARSE_OLD = '''            openings=list(fit.get("openings", [])),
        ))
'''
PARSE_NEW = '''            openings=list(fit.get("openings", [])),
            glazing=r.get("glazing"),
            pane=r.get("pane"),
            ac=bool(r.get("ac", False)),
            bars=bool(r.get("bars", False)),
        ))
'''

FRAMING_ANCHOR = '''def roofline_slots(manifest: SlotManifest) -> list:
'''
FRAMING_NEW = '''def window_fixture_orders(manifest: SlotManifest, regions: list, *,
                          seed: int) -> list[dict]:
    """AN EMPTY'S WINDOW FIXTURES (0.26.0), as Zoo (>= 1.69.0) builds them.

    * ``window_bars`` -- one per opening of a barred window, at the opening's
      centre on the wall face, sized to it (``size2``);
    * ``ac_unit`` -- one per opening of a window with an air conditioner, at
      its SILL on the wall face: Zoo stands the unit there and reaches it back
      to the pane, and ``size2`` tells it how wide the opening is to close.

    ONLY ON A FACADE WINDOW. Deli Counter (>= 0.181.0) writes `bars` and `ac`
    only on an Empty's sealed windows; a real window is a firing line, and
    bars a bullet passes through would lie about it, so a slot without
    `glazing: "facade"` orders nothing whatever it carries. THE SLOT IS THE
    OPT-IN, so there is no flag. Exempt from the opening keep-out, as a frame
    is (`openings.EXEMPT`).
    """
    uv = _uv(regions, "frame")
    orders = []
    center = footprint_center(manifest)
    thick_m = modal_thickness(manifest)
    for s in manifest.slots:
        if (s.role != "window" or s.glazing != "facade" or not s.dims
                or not (s.ac or s.bars)):
            continue
        frame = wall_frame(s, center, thick_m)
        base_z = _base_z(s)
        for k, op in enumerate(s.openings):
            ow = float(op.get("width", 0.0))
            oh = float(op.get("height", 0.0))
            if ow <= 0.0 or oh <= 0.0:
                continue
            sill = float(op.get("sill", 0.0))
            fixtures = []
            if s.bars:
                fixtures.append(("window_bars", base_z + sill + oh / 2.0))
            if s.ac:
                fixtures.append(("ac_unit", base_z + sill))
            for cover, z in fixtures:
                pos, n = _face(s, 0.0, z, frame)
                rng = rng_for(seed, cover, s.slot_id, str(k))
                orders.append({
                    "anchor_kind": "window_fixture",
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

EXEMPT_OLD = '''#: Covers exempt from the rule. Exactly one, and it is listed rather than
#: inferred so that adding a second is a visible decision.
EXEMPT = ("frame",)
'''
EXEMPT_NEW = '''#: Covers exempt from the rule, listed rather than inferred so that adding one
#: is a visible decision. A `frame` rings its opening. An Empty's window
#: fixtures (0.26.0) -- `window_bars` over the opening, an `ac_unit` standing
#: in it -- are the opening's own, and are ordered only on a facade window:
#: Deli Counter seals an Empty and records no gameplay openings on it, so no
#: body or shot uses the hole they stand in.
EXEMPT = ("frame", "window_bars", "ac_unit")
'''

CLI_OLD = '''            if args.panel_fields and slot_manifest is not None \\
                    and not args.anchor_patina_space:
                panels += paneling.panel_orders(
                    slot_manifest, regions, seed=args.seed,
                    panel=args.panel_size, gap=args.panel_gap)
'''
CLI_NEW = '''            if args.panel_fields and slot_manifest is not None \\
                    and not args.anchor_patina_space:
                panels += paneling.panel_orders(
                    slot_manifest, regions, seed=args.seed,
                    panel=args.panel_size, gap=args.panel_gap)
            # 0.26.0: an Empty's window fixtures -- the bars and air
            # conditioners Deli Counter (>= 0.181.0) chose per window. The
            # slot is the opt-in, so they need no flag.
            if slot_manifest is not None and not args.anchor_patina_space:
                panels += framing.window_fixture_orders(
                    slot_manifest, regions, seed=args.seed)
'''

PROUD_OLD = '''#: Deepest any cover stands proud of its wall -- `gutter_run` in Zoo's _COVER.
_PROUDEST_COVER = 0.10
'''
PROUD_NEW = '''#: Deepest any cover the rule JUDGES stands proud of its wall -- `gutter_run`
#: in Zoo's _COVER. An `ac_unit` stands 0.30 out (Zoo >= 1.69.0), but it is in
#: `EXEMPT` and ordered only on a sealed window, so no lane is sized for it.
_PROUDEST_COVER = 0.10
'''

GP_PROUD_OLD = '''#: Deepest any cover stands proud of its wall -- ``gutter_run`` in Zoo's
#: ``_COVER``. Also mirrored from :mod:`patina.openings`.
_PROUDEST_COVER = 0.10
'''
GP_PROUD_NEW = '''#: Deepest any cover the keep-out JUDGES stands proud of its wall --
#: ``gutter_run`` in Zoo's ``_COVER``. Also mirrored from
#: :mod:`patina.openings`, and like it leaves out the exempt covers: an
#: ``ac_unit`` stands 0.30 out (Zoo >= 1.69.0), only on an Empty's sealed
#: window, which carries no gameplay marker.
_PROUDEST_COVER = 0.10
'''

TEST_OLD = '''def test_frame_is_the_sole_exemption():
    """Surrounding an opening is the entire point of a frame."""
    boxes = _boxes()
    f = _order("frame", (0.0, 10.0, 1.05), size2=[1.2, 2.1])
    assert openings.hits(f, boxes) == []
    kept, rep = openings.apply([f], boxes)
    assert kept == [f] and not rep["dropped"]
    assert openings.EXEMPT == ("frame",), "adding a second must be deliberate"
'''
TEST_NEW = '''def test_the_exemptions_are_the_listed_three():
    """Surrounding an opening is the entire point of a frame. An Empty's
    window fixtures (0.26.0) stand IN their sealed opening -- the second and
    third exemptions, added deliberately, which is what this pin is for."""
    boxes = _boxes()
    f = _order("frame", (0.0, 10.0, 1.05), size2=[1.2, 2.1])
    assert openings.hits(f, boxes) == []
    kept, rep = openings.apply([f], boxes)
    assert kept == [f] and not rep["dropped"]
    assert openings.EXEMPT == ("frame", "window_bars", "ac_unit"), \\
        "adding another must be deliberate"
'''

VER_OLD = '__version__ = "0.25.1"\n'
VER_NEW = '__version__ = "0.26.0"\n'


def main():
    assert (PA / "VERSION").read_text(encoding="utf-8").strip() == "Patina 0.25.1"
    _edit(PA / "patina" / "slots.py", [(FIELDS_OLD, FIELDS_NEW), (PARSE_OLD, PARSE_NEW)])
    _edit(PA / "patina" / "framing.py", [(FRAMING_ANCHOR, FRAMING_NEW)])
    _edit(PA / "patina" / "openings.py", [(EXEMPT_OLD, EXEMPT_NEW), (PROUD_OLD, PROUD_NEW)])
    _edit(PA / "patina" / "gameplay.py", [(GP_PROUD_OLD, GP_PROUD_NEW)])
    _edit(PA / "patina" / "cli.py", [(CLI_OLD, CLI_NEW)])
    _edit(PA / "patina" / "version.py", [(VER_OLD, VER_NEW)])
    _edit(PA / "tests" / "test_openings.py", [(TEST_OLD, TEST_NEW)])
    shutil.copyfile(SRC / "test_window_fixtures.py", PA / "tests" / "test_window_fixtures.py")
    ch = PA / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    head = "## [0.25.1]"
    assert s.count(head) == 1
    ch.write_text(s.replace(head, (SRC / "CHANGELOG_0.26.0.md").read_text(encoding="utf-8").rstrip("\n")
                            + "\n\n" + head), encoding="utf-8", newline="\n")
    (PA / "VERSION").write_text("Patina 0.26.0", encoding="utf-8", newline="\n")
    print("applied Patina 0.26.0")


if __name__ == "__main__":
    main()
