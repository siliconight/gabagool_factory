"""Before/after sheets of the slice's street stations: tag A (left) against tag B (right), the same stations, at full
frame and at a 2x crop of each frame's centre, in the level's light or under the studio light.

    python docs/findings/slice_look/sheet.py <tag A> <tag B> <level|inspect> [station ...]

Reads _scratch/slice_frames/<tag>_street_<light>/ and writes sheet_<A>_<B>_<light>.png beside it. Draws pictures;
measures nothing.
"""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
FR = os.path.join(HERE, "..", "..", "..", "_scratch", "slice_frames")
a, b, light = sys.argv[1:4]
names = sys.argv[4:] or ["ave_east", "ave_west", "sidewalk_east", "gas_front", "bank_front", "card_front"]
pre = "INSPECT_studio_" if light == "inspect" else ""
W = 800


def _crop(im):
    w, h = im.size
    return im.crop((w // 4, h // 4, 3 * w // 4, 3 * h // 4)).resize((W, int(W * 9 / 16)), Image.LANCZOS)


rows = []
for name in names:
    ia = Image.open(os.path.join(FR, "%s_street_%s" % (a, light), pre + name + ".png")).convert("RGB")
    ib = Image.open(os.path.join(FR, "%s_street_%s" % (b, light), pre + name + ".png")).convert("RGB")
    for x, y in ((ia.resize((W, int(W * 9 / 16))), ib.resize((W, int(W * 9 / 16)))), (_crop(ia), _crop(ib))):
        row = Image.new("RGB", (2 * W + 8, x.size[1]), (40, 40, 40))
        row.paste(x, (0, 0))
        row.paste(y, (W + 8, 0))
        ImageDraw.Draw(row).text((8, 6), "%s  %s" % (name, a), fill=(255, 255, 0))
        ImageDraw.Draw(row).text((W + 16, 6), b, fill=(255, 255, 0))
        rows.append(row)
sheet = Image.new("RGB", (2 * W + 8, sum(r.size[1] + 8 for r in rows)), (40, 40, 40))
y = 0
for r in rows:
    sheet.paste(r, (0, y))
    y += r.size[1] + 8
out = os.path.join(HERE, "sheet_%s_%s_%s.png" % (a, b, light))
sheet.save(out)
print("wrote", os.path.basename(out), sheet.size)
