"""Compose a findings frame: the bank's stations on one 1920 x 1080 sheet, 3 x 3 tiles of 640 x 360, each labelled
with its station, in the order frames 17 and 18 used. Reads a `look_shots` output directory; draws no conclusion.

    python docs/findings/bank_interior/sheet.py <shots dir> <prefix> <out.png>

`prefix` is "" for the level's light and "INSPECT_studio_" for the inspection light.
"""
import sys

from PIL import Image, ImageDraw

STATIONS = ("lobby_entry", "lobby_wide", "lobby_west", "lobby_east", "behind_line", "vault", "vault_west",
            "bank_front")
shots, prefix, out = sys.argv[1], sys.argv[2], sys.argv[3]
sheet = Image.new("RGB", (1920, 1080), (0, 0, 0))
draw = ImageDraw.Draw(sheet)
for i, name in enumerate(STATIONS):
    tile = Image.open("%s/%s%s.png" % (shots, prefix, name)).convert("RGB").resize((640, 360), Image.LANCZOS)
    x, y = (i % 3) * 640, (i // 3) * 360
    sheet.paste(tile, (x, y))
    draw.text((x + 8, y + 6), name, fill=(255, 230, 0))
sheet.save(out)
print("wrote", out)
