"""Deli Counter 0.168.2: a video-poker cabinet stands off the storefront glass.

The walker, 2026-10-01, on cold run 9127's frames: "keep the posters off the
machines, set off_glass on cabinets". One of gas_station_a02's cabinets stood
against the storefront glass by the door. The sale posters were already kept
off the glass (`off_glass`, 0.163.0); the cabinets now are too, both pieces
-- a bar's machine does not stand in its window either. The order is kept:
cabinets before posters, so no poster hangs over a machine.
"""
import pathlib

P = pathlib.Path(__file__).resolve().parents[1] / "deli_counter" / "level_design.py"
PAIRS = [
    ('''    _piece("video_poker_store", ((0.65, 0.65, 1.75),), "wall", front=True, most=2,
           variants=4, seats=("stool", 1, 1),''',
     '''    _piece("video_poker_store", ((0.65, 0.65, 1.75),), "wall", front=True, most=2,
           variants=4, seats=("stool", 1, 1), off_glass=True,'''),
    ('''    _piece("video_poker_bar", ((0.65, 0.65, 1.75),), "wall", front=True, most=2,
           most_big=(80.0, 3), variants=4, seats=("stool", 1, 1),''',
     '''    _piece("video_poker_bar", ((0.65, 0.65, 1.75),), "wall", front=True, most=2,
           most_big=(80.0, 3), variants=4, seats=("stool", 1, 1), off_glass=True,'''),
    ('''    # Each brings ONE stool in front of its face (`seats`, which
    # `_place_fixture` honours since this release). Standing, collision.''',
     '''    # Each brings ONE stool in front of its face (`seats`, which
    # `_place_fixture` honours since this release). Standing, collision.
    # OFF THE GLASS (0.168.2), the walker: "set off_glass on cabinets" -- a
    # store's machine stood against the storefront window by its door.'''),
]


def main():
    raw = P.read_bytes()
    assert b"\r\n" not in raw
    s = raw.decode("utf-8")
    for old, new in PAIRS:
        assert s.count(old) == 1, old[:60]
        s = s.replace(old, new)
    P.write_bytes(s.encode("utf-8"))
    print("patched level_design.py")


if __name__ == "__main__":
    main()
