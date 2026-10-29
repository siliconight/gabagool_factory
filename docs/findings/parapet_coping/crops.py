"""Full-resolution crops of the bank's top edge, before (left) and after (right), under the studio light: the corner
from corner_oblique, the parapet from the roof (roof_along), the corner from below (corner_low), the front (bank_front).

    python docs/findings/parapet_coping/crops.py

Writes crops_inspect.png beside it. Draws pictures; measures nothing. The rain differs between runs, so a pixel
difference of these frames measures the rain; the crops are read by eye.
"""
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CROPS = [("corner_oblique", (500, 250, 1300, 550)), ("roof_along", (0, 250, 800, 550)),
         ("corner_low", (100, 150, 900, 450)), ("bank_front", (300, 280, 1100, 580))]
out = Image.new("RGB", (1610, 300 * len(CROPS)), (40, 40, 40))
for i, (name, box) in enumerate(CROPS):
    for j, arm in enumerate(("before", "after")):
        im = Image.open(os.path.join(HERE, "frames", arm + "_inspect", "INSPECT_studio_%s.png" % name))
        out.paste(im.convert("RGB").crop(box), (j * 810, i * 300))
out.save(os.path.join(HERE, "crops_inspect.png"))
print("wrote crops_inspect.png", out.size)
