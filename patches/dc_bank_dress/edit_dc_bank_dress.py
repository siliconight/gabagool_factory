"""Edit a Deli Counter clone for 0.283.0: a bank's lobby keeps potted plants and a wall clock -- Zoo 1.136.0's `planter`
and `wall_clock`. Run from the clone's root, on 0.282.0. Asserts every anchor once; refuses on a miss."""
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
('''    _piece("security_camera", ((0.18, 0.38, 0.2),), "wall", front=True, most=2, most_big=(300.0, 4),
           under=_CAMERA_AIR, collision="none"),''',
'''    _piece("security_camera", ((0.18, 0.38, 0.2),), "wall", front=True, most=2, most_big=(300.0, 4),
           under=_CAMERA_AIR, collision="none"),
    # A LOBBY'S PLANTS AND ITS CLOCK (0.283.0, Zoo 1.136.0's `planter` and
    # `wall_clock`; the factory's roadmap 321). The comps keep a plant in a
    # planter by the windows and the counters, and a clock over the line
    # (docs/reference/BANK_INTERIOR_COMPS.md); the walker, shown a 390 m2 lobby
    # standing a dozen pieces: "fix it before we rush to the release". A
    # `potted_plant`, not a `planter`: that word is the library's long planter
    # BOXES (1.4 x 0.7 m and 2.4 x 1.4 m, fifteen in seven specs), which stay
    # boxes. Against a wall, its variant the plant; the clock hung at 2.3 m.
    _piece("potted_plant", ((0.6, 0.6, 1.5), (0.5, 0.5, 1.2), (0.7, 0.7, 1.8)), "wall", variants=True, most=4),
    _piece("wall_clock", ((0.36, 0.06, 0.36),), "wall", front=True, most=1, lift=2.3, collision="none"),'''),
('''    "bank_lobby": {"anchors": ("check_desk",),
                   "wall": ("chair_waiting", "chair_waiting", "atm"),''',
'''    # THE ATM IS AN ANCHOR (0.282.0): placed before any wall piece, so a lobby
    # keeps it -- with three plants in the wall pool, bank_branch_a03's took
    # the wall its ATM and chairs had stood on (`test_ticket_queue`)
    "bank_lobby": {"anchors": ("check_desk", "atm"),
                   "all_anchors": True,
                   "wall": ("chair_waiting", "chair_waiting", "potted_plant", "potted_plant"),'''),
('''                   "clusters": ((("stanchion",), 3, 4), (("litter_bin",), 1, 1)),
                   "fixtures": ("security_camera",)},''',
'''                   "clusters": ((("stanchion",), 3, 4), (("litter_bin",), 1, 1)),
                   "fixtures": ("security_camera", "wall_clock")},'''),
])

edit("prop_species.py", [
('''    (("security_camera",), "security_camera"),''',
'''    (("security_camera",), "security_camera"),
    # A LOBBY'S PLANT AND CLOCK (0.283.0, Zoo 1.136.0). `potted_plant`, ahead of
    # the box row whose `planter` is the library's long planter boxes
    (("potted_plant",), "planter"),
    (("wall_clock",), "wall_clock"),'''),
])

edit("tests/test_furnish.py", [
('''    "check_desk": ((1.0, 3.2), (0.6, 1.2), (1.0, 1.2)),''',
'''    "check_desk": ((1.0, 3.2), (0.6, 1.2), (1.0, 1.2)),
    "planter": ((0.4, 0.9), (0.4, 0.9), (0.8, 2.0)),
    "wall_clock": ((0.25, 0.5), (0.04, 0.1), (0.25, 0.5)),'''),
])
