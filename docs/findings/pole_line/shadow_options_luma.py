"""Mean luminance of the same regions across `shadow_options.py`'s four arms (2026-10-12).

    python docs/findings/pole_line/shadow_options_luma.py

Reads the frames `shadow_options.py` left under `_scratch/frames_shadow_options/` and prints, per arm,
the mean Rec.709 luma (0-255, the 8-bit sRGB values that reached the swap chain) of: the near body,
the road around it, the far frame's centre crop (the one `shadow_options.png` enlarges) and that crop's
lower half, the far frame whole; then the five 100 x 100 tiles of the far frame whose arms differ most.
It measures and stops; `shadow_options_luma.out.txt` is its output.
"""
import pathlib

from PIL import Image

F = pathlib.Path(__file__).resolve().parents[3]
FR = F / "_scratch" / "frames_shadow_options"
ARMS = ("built", "budget4", "budget0", "fade30")


def _lum(im, box):
    px = im.convert("RGB").crop(box).tobytes()
    n = len(px) // 3
    return sum(0.2126 * px[3 * i] + 0.7152 * px[3 * i + 1] + 0.0722 * px[3 * i + 2] for i in range(n)) / n


def main():
    frames = {(a, s): Image.open(FR / ("shots_" + a) / (s + ".png")) for a in ARMS for s in ("near", "far")}
    w, h = frames[("built", "far")].size
    crop = (w // 2 - 160, h // 2 - 70, w // 2 + 160, h // 2 + 110)
    regions = [("near: the body", "near", (760, 340, 840, 500)),
               ("near: the road around it", "near", (600, 480, 1000, 620)),
               ("far: the centre crop", "far", crop),
               ("far: the crop's lower half", "far", (crop[0], crop[1] + 90, crop[2], crop[3])),
               ("far: the whole frame", "far", (0, 0, w, h))]
    print("%-30s" % "region" + "".join("%9s" % a for a in ARMS))
    for label, shot, box in regions:
        print("%-30s" % label + "".join("%9.2f" % _lum(frames[(a, shot)], box) for a in ARMS))
    tiles = []
    for ty in range(h // 100):
        for tx in range(w // 100):
            box = (tx * 100, ty * 100, tx * 100 + 100, ty * 100 + 100)
            v = [_lum(frames[(a, "far")], box) for a in ARMS]
            tiles.append((max(v) - min(v), box, v))
    tiles.sort(reverse=True)
    print("the far frame's tiles whose arms differ most:")
    for spread, box, v in tiles[:5]:
        print("  %-22s spread %5.2f  " % (str(box), spread) + "  ".join("%s %.2f" % (a, x) for a, x in zip(ARMS, v)))


if __name__ == "__main__":
    main()
