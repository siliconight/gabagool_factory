"""The door sign as each version paints it, through its own `storefront_names.paint`.

    python sign_sheet.py <zoo_189_root> <zoo_190_root> <out.png>

Each painter runs in a child process (both versions are the package `zoo_keeper`), returns raw
RGB, and the sheet shows 1.89.0 nearest-magnified (as it was sampled) above 1.90.0 smooth-scaled
(as it will be), each 1120 px wide. Prints the sheet's size and what it drew.
"""
import json
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

SIGNS = (("strip_club_a01", 2.8), ("funeral_home_a03", 3.2), ("funeral_home_a03", 2.0),
         ("casino_a03", 3.2), ("deli_a01", 2.0), ("07_police_station", 2.4),
         ("apartment_walkup_a01", 2.2))
SHOW_W = 1120
CHILD = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
from zoo_keeper.core import storefront_names as SN
out = []
for business, w in json.loads(sys.argv[2]):
    said = SN.sign_for(business)
    spec = {"w_m": w, "h_m": 0.6, "text": said["text"], "colours": said["colours"]}
    if hasattr(SN, "voice_for"):
        spec["voice"] = SN.voice_for(said["kind"])
    c = SN.paint(spec)
    out.append({"business": business, "text": said["text"], "w": c.w, "h": c.h,
                "rgb": bytes(c.buf).hex(), "unset": c.unset})
print(json.dumps(out))
"""


def paint(root):
    res = subprocess.run([sys.executable, "-c", CHILD, root, json.dumps(SIGNS)],
                         capture_output=True, text=True, check=True)
    return json.loads(res.stdout)


def main():
    old, new = paint(sys.argv[1]), paint(sys.argv[2])
    rows = []
    for o, n in zip(old, new):
        a = Image.frombytes("RGB", (o["w"], o["h"]), bytes.fromhex(o["rgb"]))
        b = Image.frombytes("RGB", (n["w"], n["h"]), bytes.fromhex(n["rgb"]))
        rows.append((f"1.89.0  {o['business']}  {o['w']}x{o['h']} px, Closest",
                     a.resize((SHOW_W, round(SHOW_W * a.height / a.width)), Image.NEAREST)))
        rows.append((f"1.90.0  {n['business']}  {n['w']}x{n['h']} px, filtered",
                     b.resize((SHOW_W, round(SHOW_W * b.height / b.width)), Image.BILINEAR)))
    bar = 24
    sheet = Image.new("RGB", (SHOW_W, sum(im.height + bar for _, im in rows)), (16, 16, 16))
    d = ImageDraw.Draw(sheet)
    try:
        lf = ImageFont.truetype("arial.ttf", 15)
    except OSError:
        lf = ImageFont.load_default()
    y = 0
    for label, im in rows:
        d.text((8, y + 4), label, fill=(235, 235, 235), font=lf)
        sheet.paste(im, (0, y + bar))
        y += im.height + bar
    sheet.save(sys.argv[3])
    print(sys.argv[3], sheet.size, [(n["business"], n["text"], n["unset"]) for n in new])


if __name__ == "__main__":
    main()
