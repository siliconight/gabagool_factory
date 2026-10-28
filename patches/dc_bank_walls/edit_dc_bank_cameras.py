"""Edit a Deli Counter clone for 0.282.0 (with `edit_dc_bank_walls.py`): a bank's lobby and vault hang CCTV cameras --
Zoo's `security_camera`, which no building placed. Run from the clone's root, after the walls edit. Asserts every
anchor once; refuses on a miss."""
from pathlib import Path


def edit(path, pairs):
    p = Path(path)
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    for old, new in pairs:
        assert t.count(old) == 1, (path, old[:70], t.count(old))
        t = t.replace(old, new)
    if crlf:
        t = t.replace("\n", "\r\n")
    p.write_bytes(t.encode("utf-8"))
    print(path, "edited", len(pairs), "anchors", "CRLF" if crlf else "LF")


edit("level_design.py", [
('''    _piece("check_desk", ((1.6, 0.9, 1.1), (2.4, 1.0, 1.1)), "island", front=True, most=2),''',
'''    _piece("check_desk", ((1.6, 0.9, 1.1), (2.4, 1.0, 1.1)), "island", front=True, most=2),
    # A BANK'S CAMERAS (0.282.0, Zoo's `security_camera`; the factory's
    # roadmap 321). The walker: "were there cctv cameras in the 90s?" -- yes:
    # the Bank Protection Act of 1968 asks for devices that identify a robber,
    # and most banks met it with interior cameras on brackets aimed at the
    # floor and the teller line, recorded on time-lapse VCRs
    # (docs/reference/BANK_INTERIOR_COMPS.md, "researched"). No building placed
    # the species. Hung under the ceiling (`under`) on a wall facing the room,
    # out of reach, so no collision; two a room, four in a room of 300 m2 or
    # more -- a lobby and each vault alike.
    _piece("security_camera", ((0.18, 0.38, 0.2),), "wall", front=True, most=2, most_big=(300.0, 4),
           under=_CAMERA_AIR, collision="none"),'''),
('''    "bank_lobby": {"anchors": ("check_desk",),
                   "wall": ("chair_waiting", "chair_waiting", "atm"),
                   "floor": (),
                   "clusters": ((("stanchion",), 3, 4), (("litter_bin",), 1, 1))},''',
'''    "bank_lobby": {"anchors": ("check_desk",),
                   "wall": ("chair_waiting", "chair_waiting", "atm"),
                   "floor": (),
                   "clusters": ((("stanchion",), 3, 4), (("litter_bin",), 1, 1)),
                   "fixtures": ("security_camera",)},'''),
('''    "bank_vault": {"anchors": ("safe_floor",),
                   "wall": ("shelf_run", "cabinet_locker", "safe_floor"),
                   "floor": ("table_count", "cash_cart"),
                   "clusters": ((("cartons",), 2, 3),)},''',
'''    "bank_vault": {"anchors": ("safe_floor",),
                   "wall": ("shelf_run", "cabinet_locker", "safe_floor"),
                   "floor": ("table_count", "cash_cart"),
                   "clusters": ((("cartons",), 2, 3),),
                   "fixtures": ("security_camera",)},'''),
('''def _piece(name, sizes, where, front=False, stock=None, variants=False,''',
'''#: A camera's top this far under the ceiling plane (0.282.0): on its bracket,
#: clear of the grid's lip, over every head.
_CAMERA_AIR = 0.25


def _piece(name, sizes, where, front=False, stock=None, variants=False,'''),
])

edit("prop_species.py", [
('''    (("check_desk",), "check_desk"),''',
'''    (("check_desk",), "check_desk"),
    # A BANK'S CAMERAS (0.282.0): Zoo's `security_camera`, a CCTV camera on its
    # wall bracket
    (("security_camera",), "security_camera"),'''),
('''DEPTH_LONG = frozenset({"cargo_container"})''',
'''DEPTH_LONG = frozenset({"cargo_container", "security_camera"})'''),
])


edit("tests/test_furnish.py", [
('''    "check_desk": ((1.0, 3.2), (0.6, 1.2), (1.0, 1.2)),''',
'''    "check_desk": ((1.0, 3.2), (0.6, 1.2), (1.0, 1.2)),
    "security_camera": ((0.12, 0.24), (0.28, 0.46), (0.14, 0.26)),'''),
('''        for label, v, (lo, hi) in zip(("width", "depth", "height"),
                                      (max(w, d), min(w, d), h), rng):''',
'''        # a species long in DEPTH is recorded short side first (0.282.0,
        # `prop_species.long_axis_first`): its width is the short side
        wd = (min(w, d), max(w, d)) if sp in prop_species.DEPTH_LONG else (max(w, d), min(w, d))
        for label, v, (lo, hi) in zip(("width", "depth", "height"),
                                      (wd[0], wd[1], h), rng):'''),
])
