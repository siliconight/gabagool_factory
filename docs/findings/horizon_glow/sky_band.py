"""Lux 0.73.0's horizon glow, seen: the sky just above the horizon, with and without it.

    python docs/findings/horizon_glow/sky_band.py <control shots dir> <glow shots dir> [--sheet OUT.png]

For each station frame both folders hold (1600 x 900, `look_shots`), the band of rows from
BAND_TOP to BAND_BOTTOM of the frame's height: the sky from a little above the horizon up. Each
station is pitched 0.5 m up over its look distance, so the horizon sits a few rows under the
centre, and the band stops short of it. Per frame: the band's mean luma, and its warmth, the mean
of R - B over the band (a sodium glow is orange, a night sky is blue). Printed as control, glow and
the difference, per station. A frame of another size is an error, and a station in one folder
only is said and skipped. `--sheet` lays the pairs out, control left and glow right, one station
a row, captioned. It prints what it measured and stops.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

FRAME = (1600, 900)
BAND_TOP, BAND_BOTTOM = 0.20, 0.46


def band(path):
    im = Image.open(path).convert("RGB")
    if im.size != FRAME:
        raise SystemExit("%s: %s, not the %d x %d frame" % ((path, im.size) + FRAME))
    y0, y1 = int(FRAME[1] * BAND_TOP), int(FRAME[1] * BAND_BOTTOM)
    px = list(im.crop((0, y0, FRAME[0], y1)).getdata())
    n = len(px)
    luma = sum(0.299 * r + 0.587 * g + 0.114 * b for r, g, b in px) / n
    warmth = sum(r - b for r, g, b in px) / n
    return luma, warmth


def main(argv):
    sheet = argv[argv.index("--sheet") + 1] if "--sheet" in argv else None
    a, b = Path(argv[0]), Path(argv[1])
    names = sorted(p.name for p in a.glob("*.png"))
    rows = []
    print("%-12s %8s %8s %8s | %8s %8s %8s" % ("station", "luma ctl", "luma glo", "diff", "warm ctl", "warm glo", "diff"))
    for name in names:
        if not (b / name).exists():
            print("%-12s only in %s: skipped" % (name, a))
            continue
        la, wa = band(a / name)
        lb, wb = band(b / name)
        rows.append((name, la, lb, wa, wb))
        print("%-12s %8.2f %8.2f %+8.2f | %8.2f %8.2f %+8.2f" % (name[:-4], la, lb, lb - la, wa, wb, wb - wa))
    if not rows:
        raise SystemExit("no station frame in both folders")
    if sheet:
        w, h = 800, 450
        out = Image.new("RGB", (w * 2, h * len(rows)), (0, 0, 0))
        d = ImageDraw.Draw(out)
        for i, (name, la, lb, wa, wb) in enumerate(rows):
            for j, (folder, luma, warm) in enumerate(((a, la, wa), (b, lb, wb))):
                im = Image.open(folder / name).convert("RGB").resize((w, h), Image.BILINEAR)
                out.paste(im, (j * w, i * h))
                d.text((j * w + 8, i * h + 6), "%s  %s  band luma %.1f  warmth %+.1f" % (
                    name[:-4], "control" if j == 0 else "glow", luma, warm), fill=(255, 255, 0))
        out.save(sheet)
        print("wrote %s: %d stations" % (sheet, len(rows)))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    main(sys.argv[1:])
