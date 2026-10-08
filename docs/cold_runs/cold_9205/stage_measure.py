"""The club's main stage in cold run 9205's package, against 9204's frames.

    python stage_measure.py

THE QUESTION. Lux 0.69.0 raised the stage lamps to `CLUB_STAGE_LEVEL` 24
and Level Factory 0.160.0 stopped baking a rig that cycles. Does the package
the pipeline built read as the hand-made copy the decision was taken from
(`docs/findings/club_stage_live_price/stage_live_x8.png`, 9204's package
with the stage rigs set live at eight times Lux's energy)?

THE FRAMES. Every frame is `tools/look_shots.py`'s `main_stage_close`
station: eye (-55.5, 2.4, 7.0), target (-63.5, 0.6, 7.0), Godot metres,
1600x900, GL Compatibility, the RTX 2060. 9204's five are in
`docs/findings/club_stage_live_price/`; 9205's is `stage_9205.png` here.

WHAT IT READS, in 8-bit sRGB codes as they reached the swap chain:
- **stage top:** the mean of a 200 x 34 px box on the stage's pool;
- **pole:** the mean of a 7 x 150 px strip down the pole;
- **housings:** the brightest pixel near each of the two lamp housings
  above the stage, left and right.
Luminance is Rec.709 on those codes. Prints what it measured and stops.
"""
import pathlib

from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
LIVE = HERE.parents[1] / "findings" / "club_stage_live_price"
FRAMES = (
    ("9204 as shipped (baked, 1x)", LIVE / "stage_as_shipped.png"),
    ("9204 hand copy, live 1x", LIVE / "stage_live_x1.png"),
    ("9204 hand copy, live 4x", LIVE / "stage_live_x4.png"),
    ("9204 hand copy, live 8x", LIVE / "stage_live_x8.png"),
    ("9204 hand copy, live 10x", LIVE / "stage_live_x10.png"),
    ("9205 as shipped (live, level 24)", HERE / "stage_9205.png"),
)
MEANS = {"stage top": (700, 418, 900, 452), "pole": (796, 250, 803, 400)}
HOUSINGS = {"left": (640, 80, 720, 160), "right": (890, 80, 960, 160)}


def lum(p):
    return 0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]


def main():
    for name, path in FRAMES:
        im = Image.open(path).convert("RGB")
        if im.size != (1600, 900):
            raise SystemExit(f"{path.name} is {im.size}, not the 1600x900 these boxes are in")
        cells = []
        for label, (x0, y0, x1, y1) in MEANS.items():
            px = [im.getpixel((x, y)) for x in range(x0, x1) for y in range(y0, y1)]
            rgb = tuple(sum(p[c] for p in px) / len(px) for c in range(3))
            cells.append("%s (%5.1f %5.1f %5.1f) lum %5.1f"
                         % (label, *rgb, sum(lum(p) for p in px) / len(px)))
        for label, (x0, y0, x1, y1) in HOUSINGS.items():
            best = max((sum(im.getpixel((x, y))), im.getpixel((x, y)))
                       for x in range(x0, x1) for y in range(y0, y1))
            cells.append("%s housing max %3d %s" % (label, best[0], best[1]))
        print("%-33s | %s" % (name, " | ".join(cells)))


if __name__ == "__main__":
    main()
