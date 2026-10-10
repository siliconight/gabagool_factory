"""Roadmap 224, step 2: the box truck's blotches against the bake's texel density and its denoiser.

    python docs/findings/bake_texel/bake_texel.py run <walk copy> <out dir> NAME=OPTIONS ...
    python docs/findings/bake_texel/bake_texel.py read <out dir> [--sheet SHEET.png]

`run`: for each variant, `tools/lux_rebake.py <walk copy> <out>/copy_NAME OPTIONS` (Level
Factory's own bake with the variant's dials; its report, with the lightmap's price, kept as
rebake_NAME.json), then `tools/look_shots.py` at step 1's truck side station (shots_NAME/), then
the copy is deleted: 290 MB a copy, and the report and the frame are what is kept. OPTIONS are
lux_rebake's own, comma-joined: `t1=` is Level Factory's bake unchanged, the control;
`t2=--texel-scale,2`; `dn0=--denoiser,off`; `day_t2=--preset,delco_summer_afternoon,--texel-scale,2`.

`read`: per variant, the face and the price, side by side.
- **The face:** luma over the box's face, the rectangle cold run 9219's notes measured (x 640..950,
  y 385..515 of the 1600 x 900 frame), after an 8 px Gaussian blur. Printed as p5, p50 and p95
  of 255 and their spread, as step 1's `blotch.py` printed them, and as the mean and standard
  deviation. Those two are not rounded to whole levels, which matters at midnight, where the face
  reads 1 to 6.
- **The price:** the editor's seconds, the lightmap's layers and their size, `bake.exr`'s MB (what
  the package carries) and the imported texture array's MB (what it takes in video memory).
- **The sheet,** with `--sheet`: the rectangle from each frame, stacked in the order the variants
  ran. Each crop is scaled so its p95 reads 200, so a night face and a day face can both be seen,
  and the gain is printed on the crop. A scaled crop shows where the blotches are, not how a player
  sees them.

A report that is not a successful rebake, a frame of another size, or a price the rebake could not
read is an error, not a blank. It prints what it measured and stops.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

FACTORY = Path(__file__).resolve().parents[3]
STATION = "truck_side:-31.9,1.7,-4.5,-39.9,1.7,-4.5"
SHOT = "truck_side.png"
BOX = (640, 385, 950, 515)
FRAME = (1600, 900)
ORDER = "order.txt"


def run(src, out, variants):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for v in variants:
        name, sep, opts = v.partition("=")
        if not sep or not name.isidentifier():
            raise SystemExit("a variant is NAME=OPTIONS, got %r" % v)
        args = [a for a in opts.split(",") if a]
        dest = out / ("copy_" + name)
        with open(out / ("rebake_%s.json" % name), "w", encoding="utf-8") as fo, \
                open(out / ("rebake_%s.err" % name), "w", encoding="utf-8") as fe:
            code = subprocess.call([sys.executable, str(FACTORY / "tools" / "lux_rebake.py"), src,
                                    str(dest)] + args, stdout=fo, stderr=fe,
                                   stdin=subprocess.DEVNULL, cwd=str(FACTORY))
        print("%s rebake exit %d" % (name, code), flush=True)
        if code == 0:
            with open(out / ("shots_%s.json" % name), "w", encoding="utf-8") as fo, \
                    open(out / ("shots_%s.err" % name), "w", encoding="utf-8") as fe:
                code = subprocess.call([sys.executable, str(FACTORY / "tools" / "look_shots.py"),
                                        str(dest), "--out", str(out / ("shots_" + name)), "--json",
                                        "--station", STATION], stdout=fo, stderr=fe,
                                       stdin=subprocess.DEVNULL, cwd=str(FACTORY))
            print("%s shots exit %d" % (name, code), flush=True)
        if dest.exists():
            shutil.rmtree(dest)
        with open(out / ORDER, "a", encoding="utf-8") as fo:
            fo.write("%s %s\n" % (name, " ".join(args)))


def _report(path):
    """lux_rebake prints the bake's log before its report: the report is the JSON from the last
    line that is a bare "{" to the end."""
    lines = path.read_text(encoding="utf-8").splitlines()
    starts = [i for i, ln in enumerate(lines) if ln == "{"]
    if not starts:
        raise SystemExit("%s: no report in it" % path)
    r = json.loads("\n".join(lines[starts[-1]:]))
    if not r.get("ok") or "editor_s" not in r or "lightmap" not in r:
        raise SystemExit("%s: not a successful rebake report with its lightmap: %s" % (path, sorted(r)))
    lm = r["lightmap"]
    if lm.get("unread"):
        raise SystemExit("%s: the lightmap's price was not read: %s" % (path, lm["unread"]))
    return r


def _face(shot):
    from PIL import Image, ImageFilter
    im = Image.open(shot)
    if im.size != FRAME:
        raise SystemExit("%s: %s, not the %d x %d frame the box was measured on" % ((shot, im.size) + FRAME))
    px = sorted(im.convert("L").crop(BOX).filter(ImageFilter.GaussianBlur(8)).getdata())
    n = len(px)
    mean = sum(px) / n
    sd = (sum((p - mean) ** 2 for p in px) / n) ** 0.5
    return {"p5": px[n * 5 // 100], "p50": px[n // 2], "p95": px[n * 95 // 100], "mean": mean, "sd": sd}


def read(out, sheet=None):
    out = Path(out)
    names = []
    for ln in (out / ORDER).read_text(encoding="utf-8").splitlines():
        name = ln.split(" ", 1)[0]
        if name and name not in names:
            names.append(name)
    rows = []
    print("%-8s %8s %6s %10s %8s %8s | %4s %4s %4s %6s %6s %5s  %s" % (
        "variant", "editor s", "layers", "layer", "exr MB", "vram MB", "p5", "p50", "p95", "spread",
        "mean", "sd", "options"))
    opts = {ln.split(" ", 1)[0]: (ln.split(" ", 1) + [""])[1]
            for ln in (out / ORDER).read_text(encoding="utf-8").splitlines() if ln}
    for name in names:
        shot = out / ("shots_" + name) / SHOT
        rep = out / ("rebake_%s.json" % name)
        if not shot.exists() or not rep.exists():
            print("%-8s not measured: %s" % (name, "no frame" if rep.exists() else "no report"))
            continue
        r = _report(rep)
        lm = r["lightmap"]
        f = _face(shot)
        rows.append((name, shot, f))
        print("%-8s %8.1f %6d %10s %8.1f %8.1f | %4d %4d %4d %6d %6.2f %5.2f  %s" % (
            name, float(r["editor_s"]), lm["layers"], "%dx%d" % (lm["layer_w"], lm["layer_h"]),
            lm["exr_bytes"] / 1e6, lm["imported_bytes"] / 1e6, f["p5"], f["p50"], f["p95"],
            f["p95"] - f["p5"], f["mean"], f["sd"], opts.get(name, "")))
    if sheet and rows:
        from PIL import Image, ImageDraw
        crops = []
        for name, shot, f in rows:
            gain = max(1.0, min(60.0, 200.0 / max(1, f["p95"])))
            c = Image.open(shot).convert("RGB").crop(BOX).point(lambda v, g=gain: min(255, int(v * g)))
            c = c.resize((c.width * 2, c.height * 2), Image.NEAREST)
            ImageDraw.Draw(c).text((6, 4), "%s  x%.1f" % (name, gain), fill=(255, 255, 0))
            crops.append(c)
        w, h = crops[0].size
        im = Image.new("RGB", (w, h * len(crops)), (0, 0, 0))
        for i, c in enumerate(crops):
            im.paste(c, (0, i * h))
        im.save(sheet)
        print("wrote %s: %d crops, %d x %d each" % (sheet, len(crops), w, h))


def main(argv):
    if len(argv) >= 4 and argv[0] == "run":
        return run(argv[1], argv[2], argv[3:])
    if len(argv) >= 2 and argv[0] == "read":
        sheet = argv[argv.index("--sheet") + 1] if "--sheet" in argv else None
        return read(argv[1], sheet)
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
