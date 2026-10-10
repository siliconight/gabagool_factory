"""Roadmap 224: the box truck's shaded side at each bake quality, side by side and brightened.

    python docs/findings/bake_quality/sheet.py <out dir of bake_quality.sh> <sheet.png>

Crops `blotch.py`'s rectangle (x 640..950, y 385..515 of the 1600 x 900 frame) out of each
`shots_qQ/truck_side.png`, multiplies it by GAIN so luma 1 to 6 of 255 can be seen at all,
and stacks the crops top to bottom, Low first. A brightened frame shows where the blotches are,
not how a player sees them: at the shipped exposure the face is near black. Labels are drawn in
PIL's default bitmap face. It prints what it wrote and stops.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

BOX = (640, 385, 950, 515)
GAIN = 20
NAMES = {0: "Low (Level Factory's)", 1: "Medium", 2: "High", 3: "Ultra"}


def main(out, sheet):
    crops = []
    for q in range(4):
        shot = Path(out) / f"shots_q{q}" / "truck_side.png"
        if not shot.exists():
            continue
        im = Image.open(shot).convert("RGB")
        if im.size != (1600, 900):
            raise SystemExit(f"{shot}: {im.size}, not the 1600 x 900 frame the box was measured on")
        c = im.crop(BOX).point(lambda v: min(255, v * GAIN))
        c = c.resize((c.width * 2, c.height * 2), Image.NEAREST)
        ImageDraw.Draw(c).text((6, 4), f"q{q} {NAMES[q]}  x{GAIN}", fill=(255, 255, 0))
        crops.append(c)
    if not crops:
        raise SystemExit(f"{out}: no shots_qQ/truck_side.png")
    w, h = crops[0].size
    out_im = Image.new("RGB", (w, h * len(crops)), (0, 0, 0))
    for i, c in enumerate(crops):
        out_im.paste(c, (0, i * h))
    out_im.save(sheet)
    print(f"wrote {sheet}: {len(crops)} crops, {w} x {h} each")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
