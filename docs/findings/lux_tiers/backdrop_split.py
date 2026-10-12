"""Split the difference between 9264's live sun and 9265's baked one into the backdrop's pixels and the
level's (roadmap 243, 2026-10-12; `backdrop_split.sh` and `spec_arm.sh` make the frames).

    python docs/findings/lux_tiers/backdrop_split.py

The backdrop's pixels are where hiding it changes 9265's frame by more than THRESHOLD levels of luma
(9265 against 9265 with `site_backdrop.tscn` hidden): what the backdrop draws, or the sky it covers.
For each station: the backdrop's share of the frame; the mean luma, on the backdrop's pixels and on the
rest, of 9264 (live), the arm (9264's live sun, the backdrop casting no shadow), the arm with the sun's
specular 0 when `spec_arm.sh` has shot it, and 9265 (baked); and 9264's mean absolute difference from
9265 split into the two -- the parts add to the whole. A missing frame or a size that differs stops it.
It measures and prints.
"""
import pathlib
import sys

from PIL import Image, ImageChops

F = pathlib.Path(__file__).resolve().parents[3]
FR = F / "_scratch" / "frames_sun_occl"
LIVE = F / "_scratch" / "frames_9265" / "shots_control"
BAKED = F / "_scratch" / "frames_9265" / "shots_subject"
HIDDEN = FR / "shots_9265_nobackdrop"
COLUMNS = [("live", LIVE), ("arm", FR / "shots_arm"), ("no spec", FR / "shots_arm_nospec"), ("baked", BAKED)]
SHOTS = ("line", "corner", "up", "spawn", "objective", "elev_N")
THRESHOLD = 8


def _px(im):
    return list(im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata())


def _mean(values):
    return sum(values) / len(values) if values else float("nan")


def main():
    cols = [(name, d) for name, d in COLUMNS if name != "no spec" or (d / "line.png").is_file()]
    for d in [d for _, d in cols] + [HIDDEN]:
        for s in SHOTS:
            if not (d / (s + ".png")).is_file():
                sys.exit("MISSING FRAME: %s" % (d / (s + ".png")))
    names = " / ".join(name for name, _ in cols)
    print("backdrop pixels: 9265's frame moves more than %d levels when the backdrop is hidden" % THRESHOLD)
    print("luma 0-255 as %s; |live - baked| split, adding to the whole" % names)
    print("  live: 9264 as shipped; arm: 9264, the backdrop casting no shadow;"
          + (" no spec: the arm, the sun's specular 0;" if len(cols) == 4 else "") + " baked: 9265")
    width = 8 * len(cols) + 2
    print("%-10s %9s  %-*s %-*s %8s %9s %8s" % ("station", "backdrop", width, "on the backdrop", width,
                                                "on the level", "|diff|", "backdrop", "level"))
    for shot in SHOTS:
        ims = [Image.open(d / (shot + ".png")).convert("L") for _, d in cols]
        hidden = Image.open(HIDDEN / (shot + ".png")).convert("L")
        if len({im.size for im in ims + [hidden]}) != 1:
            sys.exit("SIZES DIFFER at %s" % shot)
        mask = [v > THRESHOLD for v in _px(ImageChops.difference(ims[-1], hidden))]
        px = [_px(im) for im in ims]
        n = len(mask)
        on = [i for i in range(n) if mask[i]]
        off = [i for i in range(n) if not mask[i]]
        cells = [" / ".join("%5.1f" % _mean([p[i] for i in idx]) for p in px) for idx in (on, off)]
        live, baked = px[0], px[-1]
        d_on = sum(abs(live[i] - baked[i]) for i in on) / n
        d_off = sum(abs(live[i] - baked[i]) for i in off) / n
        print("%-10s %8.1f%%  %-*s %-*s %8.1f %9.1f %8.1f" % (shot, 100.0 * len(on) / n, width, cells[0], width,
                                                             cells[1], d_on + d_off, d_on, d_off))


if __name__ == "__main__":
    main()
