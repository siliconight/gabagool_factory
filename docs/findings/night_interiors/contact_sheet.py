"""Lay the census's frames out as one sheet: a row per room, a column per stage.

    python contact_sheet.py <out.jpg> <room,room,...> <label=shots_dir> [<label=shots_dir> ...]

Each cell is the room's census frame scaled to 400 x 225, captioned with the
stage's label and the frame's mean luma (from `<shots_dir>.json`).
"""
import json
import sys

from PIL import Image, ImageDraw

W, H, PAD, CAP = 400, 225, 6, 18


def main(argv):
    out, rooms = argv[0], argv[1].split(",")
    stages = [a.split("=", 1) for a in argv[2:]]
    means = {}
    for label, d in stages:
        m = json.load(open(d.rstrip("/\\") + ".json", encoding="utf-8"))
        means[label] = {s["name"]: s["mean"] for s in m["shots"]}
    sheet = Image.new("RGB", (len(stages) * (W + PAD) + PAD, len(rooms) * (H + CAP + PAD) + PAD), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    for r, room in enumerate(rooms):
        for c, (label, d) in enumerate(stages):
            x, y = PAD + c * (W + PAD), PAD + r * (H + CAP + PAD)
            im = Image.open("%s/%s.png" % (d, room)).convert("RGB").resize((W, H))
            sheet.paste(im, (x, y + CAP))
            draw.text((x + 2, y + 2), "%s | %s | mean %.1f" % (room.replace("__", " "), label,
                                                                  means[label].get(room, -1)), fill=(230, 230, 230))
    sheet.save(out, quality=88)
    print("wrote", out, sheet.size)


if __name__ == "__main__":
    main(sys.argv[1:])
