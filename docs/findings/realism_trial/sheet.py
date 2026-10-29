"""Before/after sheets for the realism trial's first step: nearest sampling (left) against linear (right), seed 9082's
bank, the same stations, at full frame and at a 2x crop of each frame's centre, where a texel's step shows.

    python docs/findings/realism_trial/sheet.py

Writes sheet_<tag>.png beside it. Draws pictures; measures nothing.
"""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
FR = os.path.join(HERE, "frames")
SHOTS = {"inspect": ["INSPECT_studio_vault_wall_close", "INSPECT_studio_vault", "INSPECT_studio_lobby_floor_close",
                     "INSPECT_studio_spawn"],
         "level": ["vault_wall_close", "vault", "lobby_floor_close", "lobby_east"]}
W = 800                       # each half, px


def _pair(tag, name):
    a = Image.open(os.path.join(FR, "nearest_" + tag, name + ".png")).convert("RGB")
    b = Image.open(os.path.join(FR, "linear_" + tag, name + ".png")).convert("RGB")
    return a, b


def _crop(im):
    w, h = im.size
    box = (w // 2 - w // 6, h // 2 - h // 6, w // 2 + w // 6, h // 2 + h // 6)
    return im.crop(box).resize((W, int(W * 9 / 16)), Image.NEAREST)


for tag, names in SHOTS.items():
    rows = []
    for name in names:
        a, b = _pair(tag, name)
        for im_a, im_b in ((a.resize((W, int(W * 9 / 16))), b.resize((W, int(W * 9 / 16)))), (_crop(a), _crop(b))):
            row = Image.new("RGB", (2 * W + 8, im_a.size[1]), (40, 40, 40))
            row.paste(im_a, (0, 0))
            row.paste(im_b, (W + 8, 0))
            ImageDraw.Draw(row).text((8, 6), "%s  nearest" % name, fill=(255, 255, 0))
            ImageDraw.Draw(row).text((W + 16, 6), "linear", fill=(255, 255, 0))
            rows.append(row)
    sheet = Image.new("RGB", (2 * W + 8, sum(r.size[1] + 8 for r in rows)), (40, 40, 40))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.size[1] + 8
    sheet.save(os.path.join(HERE, "sheet_%s.png" % tag))
    print("wrote sheet_%s.png" % tag, sheet.size)
