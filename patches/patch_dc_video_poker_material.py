"""Deli Counter 0.168.1: a video-poker cabinet's slot names its own kind.

Cold run 9127 built every cabinet as `prop_video_poker_..._mwood`: the
cabinets fell through `_PROP_MATERIALS` to the default `wood`, which is not
the species' own kind (Zoo 1.39.0's `metal_painted`), so Zoo tagged the stem.
The recipe draws from its atlas and ignores the material, so nothing LOOKED
wrong -- the stem said a thing that was not so. The cabinets join the painted
sheet row, the species' own kind, and the stem carries no `_m` (the
dartboard's reason, 0.136.0).
"""
import pathlib

P = pathlib.Path(__file__).resolve().parents[1] / "deli_counter" / "level_design.py"
OLD = '''    (("neon", "tv", "cigarette"), "metal_painted"),'''
NEW = '''    # ...and a video-poker cabinet, in its species' own kind so Zoo's stem
    # carries no `_m` (0.168.1; cold run 9127 built every one `_mwood`)
    (("neon", "tv", "cigarette", "video_poker"), "metal_painted"),'''


def main():
    raw = P.read_bytes()
    assert b"\r\n" not in raw
    s = raw.decode("utf-8")
    assert s.count(OLD) == 1
    P.write_bytes(s.replace(OLD, NEW).encode("utf-8"))
    print("patched level_design.py")


if __name__ == "__main__":
    main()
