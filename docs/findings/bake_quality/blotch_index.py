"""How blotchy a wall reads in a frame: the bake's low-frequency variation with the plaster's grain blurred away.

    python blotch_index.py <frame.png> [<frame.png> ...]

Over a fixed band of the `shelf` station's frame (1600 x 900; the back-room's north wall between the bookshelf's top and
the ceiling, columns 200..1500, rows 350..500 -- a first band, rows 300..470, took the ceiling in), the luminance (Rec.709 on the 8-bit values) is blurred by a Gaussian of
GRAIN_PX -- wider than the plaster's grain, narrower than a blotch -- and the band's standard deviation over its mean is
printed with the band's mean and its p5/p95. A bake with fewer blotches reads a lower index at a like mean. The band is
the frame's, not the wall's: the frames must come from one station. Measurements only.
"""
import statistics
import sys

from PIL import Image, ImageFilter

BAND = (200, 350, 1500, 500)
GRAIN_PX = 12

for path in sys.argv[1:]:
    im = Image.open(path).convert("RGB")
    assert im.size == (1600, 900), "%s is %s, not the station's 1600 x 900" % (path, im.size)
    r, g, b = im.split()
    lum = Image.merge("RGB", (r, g, b)).convert("L")
    crop = lum.crop(BAND).filter(ImageFilter.GaussianBlur(GRAIN_PX))
    vals = list(crop.get_flattened_data())
    m = statistics.mean(vals)
    sd = statistics.pstdev(vals)
    s = sorted(vals)
    print("%-60s mean %6.1f  sd %5.2f  index %.4f  p5 %3d p95 %3d" % (
        path[-60:], m, sd, sd / m if m else float("nan"), s[len(s) // 20], s[len(s) * 19 // 20]))
