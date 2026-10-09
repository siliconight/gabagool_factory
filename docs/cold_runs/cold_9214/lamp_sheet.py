"""Cold run 9214's street lamps by day: the shipped frame beside a re-bake with the lamps on.

    python lamp_sheet.py <shots root> <out.png>

<shots root> holds `poles_shipped/` and `poles_lamps_on/`, look_shots' output on
the walk copy as exported (Lux 0.71.0: Heavy Rain is a day preset, so every
street pole and wall pack is dark) and on a re-bake of it with
`street_lamps_lit = true` (tools/lux_rebake.py --set), the way every one shipped
before 0.71.0. Two given cameras: `pole24`, eye (-12.5, 1.6, 22.0) on
site_lamp_24 (-6.5, 5.92, 28.7), baked; `pack002`, eye (16.5, 1.6, 17.5) on
Spawned_wall_pack_002 (16.5, 2.45, 11.3), baked. Godot metres, Y up. One row a
camera, shipped on the left. Writes the sheet and stops.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

SHOTS = ("pole24", "pack002")
COLS = (("poles_shipped", "as shipped: Lux 0.71.0, lamps dark by day"),
        ("poles_lamps_on", "re-baked with the lamps on, as before 0.71.0"))
W, H, BAR = 800, 450, 26


def main():
    root, out = sys.argv[1], sys.argv[2]
    sheet = Image.new("RGB", (W * len(COLS), (H + BAR) * len(SHOTS)), (16, 16, 16))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
    for r, shot in enumerate(SHOTS):
        for c, (folder, label) in enumerate(COLS):
            img = Image.open(os.path.join(root, folder, shot + ".png")).convert("RGB")
            img = img.resize((W, H), Image.LANCZOS)
            x, y = c * W, r * (H + BAR)
            sheet.paste(img, (x, y + BAR))
            d.text((x + 8, y + 4), "%s -- %s" % (shot, label), fill=(235, 235, 235), font=font)
    sheet.save(out)
    print(out, sheet.size)


if __name__ == "__main__":
    main()
