"""Compose cold run 9355's phone frames against 9351's: a row a payphone; from 4 m, 9351 then 9355; from 1.5 m, 9351
then 9355. Each frame is look_shots' own, scaled to a quarter of the sheet's width and labelled.

    python docs/cold_runs/cold_9355/compose_phones.py <review dir> <out.jpg> [<crop: close frames' middle share>]
"""
import pathlib
import sys

from PIL import Image, ImageDraw

R, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
PHONES = ("payphone_0L3", "payphone_1L3", "payphone_2R3")
COLS = (("phones_far_9351", "9351, 4 m"), ("phones_far_9355", "9355, 4 m"),
        ("phones_close_9351", "9351, 1.5 m"), ("phones_close_9355", "9355, 1.5 m"))
W = 640
cells = []
for phone in PHONES:
    row = []
    for d, label in COLS:
        im = Image.open(R / d / (phone + ".png")).convert("RGB")
        im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
        ImageDraw.Draw(im).text((8, 6), "%s  %s" % (phone, label), fill=(255, 255, 255))
        row.append(im)
    cells.append(row)
h = max(c.height for row in cells for c in row)
sheet = Image.new("RGB", (W * len(COLS) + 6 * (len(COLS) - 1), h * len(PHONES) + 6 * (len(PHONES) - 1)), (20, 20, 20))
for r, row in enumerate(cells):
    for c, im in enumerate(row):
        sheet.paste(im, (c * (W + 6), r * (h + 6)))
sheet.save(out, quality=90)
print(out, sheet.size)
