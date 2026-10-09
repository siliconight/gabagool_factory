"""Frames of the payphone before and after Zoo 1.88.0, for the walker and for
the modern low-poly standard's comparison (roadmap 210).

    python render_frames.py <zoo before> <zoo after> <out dir>

Every frame is the Zoo tree's own `tools/preview_specimen.py` on its kit path
(`--species payphone --dims 0.75 0.5 2.3`, theme delco_1997, style 1): Cycles
CPU, 40 samples, the tool's sun and world. Two cameras: the tool's own
three-quarter view, and a caller's -- 1.1 m out, eye 1.6 m, aimed at the
instrument (1.25 m), from slightly right of the front.

Writes each render, then `before_after.png` (1.87.0's booth beside 1.88.0's),
`forms.png` (1.88.0's booth, pedestal and wall side by side) and
`close_before_after.png` (the caller's view of each). Prints what it ran and
stops.
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw

BLENDER = r"C:\blender\blender.exe"
BEFORE, AFTER, OUT = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3])
os.makedirs(OUT, exist_ok=True)
CLOSE = ["--azimuth", "-75", "--eye", "1.6", "--dist", "1.1", "--target-z", "1.25"]


def render(zoo, name, form=None, camera=()):
    png = os.path.join(OUT, name + ".png")
    cmd = [BLENDER, "-b", "--factory-startup", "--python", os.path.join(zoo, "tools", "preview_specimen.py"),
           "--", "--species", "payphone", "--dims", "0.75", "0.5", "2.3", "--theme", "delco_1997",
           "--style", "1", "--out", os.path.join(OUT, "_build"), "--render", png, *camera]
    if form:
        cmd += ["--form", form]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if res.returncode != 0 or not os.path.exists(png):
        raise SystemExit(f"{name}: render failed\n" + res.stdout[-1500:] + res.stderr[-800:])
    for line in res.stdout.splitlines():
        if line.startswith("[preview]") and "module=" in line:
            print(f"[frames] {name}: {line}")
    return png


def strip(pngs, labels, out_name, scale=0.5):
    ims = [Image.open(p).convert("RGB") for p in pngs]
    ims = [im.resize((int(im.width * scale), int(im.height * scale))) for im in ims]
    w, h = ims[0].size
    out = Image.new("RGB", (w * len(ims) + 8 * (len(ims) - 1), h + 24), (255, 255, 255))
    d = ImageDraw.Draw(out)
    for k, (im, label) in enumerate(zip(ims, labels)):
        x = k * (w + 8)
        out.paste(im, (x, 24))
        d.text((x + 6, 6), label, fill=(0, 0, 0))
    out.save(os.path.join(OUT, out_name))
    print(f"[frames] wrote {out_name}")


old = render(BEFORE, "before_booth")
new = {f: render(AFTER, f"after_{f}", form=f) for f in ("booth", "pedestal", "wall")}
old_close = render(BEFORE, "before_close", camera=CLOSE)
new_close = render(AFTER, "after_close", form="booth", camera=CLOSE)
strip([old, new["booth"]], ["Zoo 1.87.0", "Zoo 1.88.0, booth (the default)"], "before_after.png")
strip([new["booth"], new["pedestal"], new["wall"]], ["booth", "pedestal", "wall"], "forms.png")
strip([old_close, new_close], ["Zoo 1.87.0, a caller's view", "Zoo 1.88.0, a caller's view"],
      "close_before_after.png", scale=0.6)
