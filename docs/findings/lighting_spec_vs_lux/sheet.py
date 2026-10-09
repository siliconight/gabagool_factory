"""Frames of one level side by side: a row a camera, a column a variant.

    python sheet.py <out.png> <shot,shot,...> "<label>=<folder>" "<label>=<folder>" [...]

Each <folder> holds look_shots' PNGs by camera name (a light check's `own/`, or
a look_shots `--out`). Every frame is scaled to 800 x 450 under a label bar.
Refuses a camera missing from any folder. Writes the sheet and stops.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H, BAR = 800, 450, 26


def main(argv):
    out, shots, cols = argv[0], argv[1].split(","), []
    for a in argv[2:]:
        label, sep, folder = a.partition("=")
        if not sep:
            raise SystemExit("want LABEL=FOLDER, got %r" % a)
        cols.append((label, folder))
    for shot in shots:
        for label, folder in cols:
            if not os.path.isfile(os.path.join(folder, shot + ".png")):
                raise SystemExit("%s has no %s.png" % (folder, shot))
    sheet = Image.new("RGB", (W * len(cols), (H + BAR) * len(shots)), (16, 16, 16))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
    for r, shot in enumerate(shots):
        for c, (label, folder) in enumerate(cols):
            img = Image.open(os.path.join(folder, shot + ".png")).convert("RGB").resize((W, H), Image.LANCZOS)
            x, y = c * W, r * (H + BAR)
            sheet.paste(img, (x, y + BAR))
            d.text((x + 8, y + 4), "%s -- %s" % (shot, label), fill=(235, 235, 235), font=font)
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1:])
