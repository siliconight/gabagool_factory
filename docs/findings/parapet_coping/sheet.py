"""Before/after sheets for the parapet coping: Zoo 1.145.0 / Patina 0.32.1 (left) against the coping (right), seed
9082's bank, the same stations, at full frame and at a 2x crop of each frame's centre.

    python docs/findings/parapet_coping/sheet.py

Writes sheet_<tag>.png beside it. Draws pictures; measures nothing.
"""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
FR = os.path.join(HERE, "frames")
NAMES = ["corner_low", "corner_oblique", "roofline_far", "roof_along", "bank_front"]
SHOTS = {"inspect": ["INSPECT_studio_" + n for n in NAMES], "level": NAMES}
W = 800                       # each half, px


def _crop(im):
    w, h = im.size
    box = (w // 2 - w // 4, h // 2 - h // 4, w // 2 + w // 4, h // 2 + h // 4)
    return im.crop(box).resize((W, int(W * 9 / 16)), Image.LANCZOS)


for tag, names in SHOTS.items():
    rows = []
    for name in names:
        a = Image.open(os.path.join(FR, "before_" + tag, name + ".png")).convert("RGB")
        b = Image.open(os.path.join(FR, "after_" + tag, name + ".png")).convert("RGB")
        for im_a, im_b in ((a.resize((W, int(W * 9 / 16))), b.resize((W, int(W * 9 / 16)))), (_crop(a), _crop(b))):
            row = Image.new("RGB", (2 * W + 8, im_a.size[1]), (40, 40, 40))
            row.paste(im_a, (0, 0))
            row.paste(im_b, (W + 8, 0))
            ImageDraw.Draw(row).text((8, 6), "%s  before (edge strips)" % name, fill=(255, 255, 0))
            ImageDraw.Draw(row).text((W + 16, 6), "after (coping)", fill=(255, 255, 0))
            rows.append(row)
    sheet = Image.new("RGB", (2 * W + 8, sum(r.size[1] + 8 for r in rows)), (40, 40, 40))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.size[1] + 8
    sheet.save(os.path.join(HERE, "sheet_%s.png" % tag))
    print("wrote sheet_%s.png" % tag, sheet.size)
