"""Before/after frames of Zoo 1.87.0's weighted normals, with a control.

    python render_pairs.py <zoo root> <out dir> <species> [...]

Each species is rendered by the Zoo tree's own `tools/preview_specimen.py`
on its kit path (`--species S --dims W D H`, the genome's default corner,
theme delco_1997, style 1): Cycles CPU, 40 samples, the tool's sun and world,
the tool's own camera. Twice: as built (`<s>_on.png`) and with
`--no-weighted-normals` (`<s>_off.png`), which is 1.86.0's shading. The FIRST
species is rendered OFF a second time (`<s>_off2.png`): the control, which
shows what two renders of one build differ by.

Then `<s>_pair.png`, OFF left and ON right, and per species: the mean absolute
difference of the two frames in 8-bit codes, and the share of pixels whose
largest channel moved more than 8 codes -- printed beside the control's.
Prints what it measured and stops.
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageChops, ImageDraw

BLENDER = r"C:\blender\blender.exe"
ZOO, OUT, SPECIES = sys.argv[1], os.path.abspath(sys.argv[2]), sys.argv[3:]
os.makedirs(OUT, exist_ok=True)


def dims_of(sp):
    with open(os.path.join(ZOO, "zoo_keeper", "genome", "species", sp + ".json"),
              encoding="utf-8") as f:
        d = json.load(f)["dimensions"]
    return [str(d[k]["default"]) for k in ("width", "depth", "height")]


def render(sp, state, png):
    cmd = [BLENDER, "-b", "--factory-startup", "--python",
           os.path.join(ZOO, "tools", "preview_specimen.py"), "--",
           "--species", sp, "--dims", *dims_of(sp), "--theme", "delco_1997",
           "--style", "1", "--out", os.path.join(OUT, "_build"), "--render", png]
    if state != "on":
        cmd.append("--no-weighted-normals")
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    lines = [l for l in res.stdout.splitlines() if l.startswith("[preview]")]
    if res.returncode != 0 or not os.path.exists(png):
        raise SystemExit(f"{sp} {state}: render failed\n" + res.stdout[-1500:] + res.stderr[-800:])
    return lines


def diff(a, b):
    ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    d = ImageChops.difference(ia, ib)
    px = list(d.getdata())
    mean = sum(sum(p) for p in px) / (3.0 * len(px))
    moved = sum(max(p) > 8 for p in px) / len(px)
    return mean, moved


def pair(sp):
    a = Image.open(os.path.join(OUT, f"{sp}_off.png")).convert("RGB")
    b = Image.open(os.path.join(OUT, f"{sp}_on.png")).convert("RGB")
    w, h = a.size
    out = Image.new("RGB", (w * 2 + 8, h + 28), (255, 255, 255))
    out.paste(a, (0, 28))
    out.paste(b, (w + 8, 28))
    dr = ImageDraw.Draw(out)
    dr.text((8, 8), f"{sp} -- default normals (Zoo 1.86.0)", fill=(0, 0, 0))
    dr.text((w + 16, 8), f"{sp} -- weighted normals (Zoo 1.87.0)", fill=(0, 0, 0))
    out.save(os.path.join(OUT, f"{sp}_pair.png"))


rows = []
for i, sp in enumerate(SPECIES):
    for state in (("on", "off", "off2") if i == 0 else ("on", "off")):
        for line in render(sp, state, os.path.join(OUT, f"{sp}_{state}.png")):
            if "module=" in line:
                print(f"[pairs] {sp} {state}: {line}")
    pair(sp)
    rows.append((sp, diff(os.path.join(OUT, f"{sp}_off.png"), os.path.join(OUT, f"{sp}_on.png"))))
ctl = diff(os.path.join(OUT, f"{SPECIES[0]}_off.png"), os.path.join(OUT, f"{SPECIES[0]}_off2.png"))
print(f"[pairs] control, {SPECIES[0]} OFF against OFF: mean {ctl[0]:.3f} codes, "
      f"{ctl[1] * 100:.2f}% of pixels over 8")
for sp, (mean, moved) in rows:
    print(f"[pairs] {sp:20} OFF against ON: mean {mean:.3f} codes, {moved * 100:.2f}% of pixels over 8")
