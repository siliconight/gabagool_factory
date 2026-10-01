"""Region luminance of the forecourt frames: the pump faces and the lane.

    python forecourt_regions.py <shots_dir>
"""
import sys
from PIL import Image

REGIONS = {
    "04_pump_face": (690, 355, 910, 610),     # the inner-lane face, square on
    "05_pump_back": (690, 355, 910, 600),     # the outer-lane face, square on
    "03_lane": (400, 560, 1200, 900),         # the lane's tarmac toward the store
}


def lum(px):
    r, g, b = px
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


for name, (x0, y0, x1, y1) in REGIONS.items():
    im = Image.open(f"{sys.argv[1]}/{name}.png").convert("RGB")
    v = sorted(lum(im.getpixel((x, y))) for y in range(y0, y1, 2) for x in range(x0, x1, 2))
    n = len(v)
    print(f"{name:14} mean {sum(v)/n:6.1f}  p50 {v[n//2]:6.1f}  p90 {v[int(n*0.9)]:6.1f}")
