"""Roadmap 224: the box truck's shaded side, per bake quality, and what each bake cost.

    python docs/findings/bake_quality/blotch.py <out dir of bake_quality.sh>

For each `shots_qQ/truck_side.png`: luma over the box's face, the rectangle cold run 9219's notes
measured (x 640..950, y 385..515 of the 1600 x 900 frame), after an 8 px Gaussian blur, as p5,
p50 and p95 of 255, and their spread p95 - p5. For each `rebake_qQ.json`: the editor's seconds.
It reads an unknown shape as an error, and prints what it measured and stops.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageFilter

BOX = (640, 385, 950, 515)


def main(out):
    out = Path(out)
    print("%-4s %9s %5s %5s %5s %7s" % ("q", "editor s", "p5", "p50", "p95", "spread"))
    for q in range(4):
        shot = out / f"shots_q{q}" / "truck_side.png"
        rep = out / f"rebake_q{q}.json"
        if not shot.exists() or not rep.exists():
            continue
        # `lux_rebake.py` prints the bake's log to stdout before its report, which is the JSON
        # from the last line that is a bare "{" to the end
        lines = rep.read_text(encoding="utf-8").splitlines()
        starts = [i for i, ln in enumerate(lines) if ln == "{"]
        if not starts:
            raise SystemExit(f"{rep}: no report in it")
        r = json.loads("\n".join(lines[starts[-1]:]))
        if "editor_s" not in r or not r.get("ok"):
            raise SystemExit(f"{rep}: not a successful rebake report: {sorted(r)}")
        im = Image.open(shot).convert("L")
        if im.size != (1600, 900):
            raise SystemExit(f"{shot}: {im.size}, not the 1600 x 900 frame the box was measured on")
        px = sorted(im.crop(BOX).filter(ImageFilter.GaussianBlur(8)).getdata())
        n = len(px)
        p5, p50, p95 = px[n * 5 // 100], px[n // 2], px[n * 95 // 100]
        print("%-4d %9.1f %5d %5d %5d %7d" % (q, float(r["editor_s"]), p5, p50, p95, p95 - p5))


if __name__ == "__main__":
    main(sys.argv[1])
