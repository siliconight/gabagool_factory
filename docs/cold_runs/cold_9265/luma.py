"""Cold run 9265's frames against 9264's, and against the arms of `docs/findings/lux_tiers/`.

    python docs/cold_runs/cold_9265/luma.py

Mean luma (0-255) a station, and the mean absolute difference of 9265's frame from each other frame,
for: 9264 as shipped (Lux 0.75.0, the sun live), 9265 (Lux 0.76.0, the sun baked), and two frames
kept from the findings on 9264's package -- B2 (the sun baked by an edited copy and re-baked by
`tools/lux_rebake.py`, the arm 0.76.0 was written from) and the re-bake control (nothing changed, the
noise floor of a re-bake: 1.6 to 2.4 levels). A frame that is missing stops the run. It measures and
prints.
"""
import pathlib
import sys

from PIL import Image, ImageChops, ImageStat

F = pathlib.Path(__file__).resolve().parents[3]
FRAMES = [("9264 live", F / "_scratch" / "frames_9265" / "shots_control"),
          ("9265 baked", F / "_scratch" / "frames_9265" / "shots_subject"),
          ("B2", F / "_scratch" / "frames_sun_variants" / "shots_B2"),
          ("rebake ctl", F / "_scratch" / "frames_sun_variants" / "shots_control")]
SHOTS = ("line", "corner", "up", "spawn", "objective", "elev_N")


def main():
    missing = [str(d / (s + ".png")) for _, d in FRAMES for s in SHOTS if not (d / (s + ".png")).is_file()]
    if missing:
        sys.exit("MISSING FRAMES: " + ", ".join(missing))
    print("mean luma 0-255; in brackets the mean absolute difference from 9265's frame")
    print("%-10s" % "station" + "".join("%18s" % name for name, _ in FRAMES))
    for shot in SHOTS:
        ims = [Image.open(d / (shot + ".png")).convert("L") for _, d in FRAMES]
        if len({im.size for im in ims}) != 1:
            sys.exit("SIZES DIFFER at %s: %s" % (shot, [im.size for im in ims]))
        cells = []
        for im in ims:
            luma = ImageStat.Stat(im).mean[0]
            diff = ImageStat.Stat(ImageChops.difference(im, ims[1])).mean[0]
            cells.append("%8.1f (%5.1f)" % (luma, diff))
        print("%-10s" % shot + "".join("%18s" % c for c in cells))


if __name__ == "__main__":
    main()
