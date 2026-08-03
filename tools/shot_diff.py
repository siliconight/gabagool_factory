"""Did the level CHANGE, and did it get worse? Two shot runs, side by side.

WHAT THIS IS FOR. Every visual defect found in this pipeline so far was found
by a human walking the level and saying "that looks wrong" -- curbs 4.3 m under
the street, 60 conduits at third-storey height, gutters above the roofline,
strips pointing at world +X on half the building, 1374 panels sampling one
patch of concrete. Through all of it the pipeline reported *structural checks
passed, 0 blockers*. Nothing in it looks at the result.

`look_shots.gd` already renders fixed camera angles and writes per-shot
luminance statistics. It had no counterpart: nothing compared one run to the
next, so a render was something you looked at once and forgot. This is that
counterpart.

    python tools\\shot_diff.py <before.json> <after.json> [--images] [--gate]

WHAT IT COMPARES.

  * STATISTICS, always. mean / p05 / p50 / p95 and the clipped, near-clipped
    and crushed percentages, for the full frame and for the centre region.
    Cheap, needs no image decoding, and catches "the level went dark" or "the
    sky blew out" immediately.

  * PIXELS, with --images. Fraction of pixels that changed at all, and the
    largest single-channel delta. This is the half that catches GEOMETRY: 86
    pieces of dressing disappearing from doorways barely moves a mean, and
    lights up a pixel diff.

WHAT COUNTS AS A REGRESSION, and why only these. Rising `clipped_pct` (detail
burned out of highlights), rising `crushed_pct` (detail lost in shadow), and a
frame going uniform (a shot that renders nothing, or renders a wall). Those are
losses in every art direction. Everything else -- brighter, darker, different --
is reported as CHANGE and judged by a human, because a tool that decides a
level looks worse is a tool that will be wrong and ignored.

WHAT IT REFUSES. Comparing runs from different GPUs, renderers or viewport
sizes. A pixel diff across two adapters measures the driver, not the level, and
`shots_*.json` records adapter / rendering_method / viewport precisely so this
can be checked. Same shape as the provenance guard in `stage_census.py`, for
the same reason: a comparison whose frame silently shifted is worse than no
comparison.

WHAT A NONZERO EXIT MEANS. With --gate: a regression fired, or the runs were
not comparable. Without it: only a hard error. Findings never set the exit code
unless you ask for the gate, so this is a lens by default and a gate on demand.
"""
import argparse
import json
import os
import sys

#: Fields compared verbatim between runs. Anything differing here means the two
#: renders are not measuring the same thing.
PROVENANCE = ("adapter", "adapter_api", "adapter_vendor", "engine",
              "rendering_method", "viewport")

#: Percentage-point rise that counts as a regression rather than a change.
TOL_PCT = 0.5
#: A frame whose p95 and p05 are this close is showing one flat surface.
UNIFORM_SPREAD = 2.0


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def comparable(a, b):
    """(ok, differences). Refusing beats measuring the driver."""
    diffs = []
    for k in PROVENANCE:
        if a.get(k) != b.get(k):
            diffs.append("%s: %r -> %r" % (k, a.get(k), b.get(k)))
    return (not diffs), diffs


def _stat(shot, key, centre=False):
    src = shot.get("centre", {}) if centre else shot
    v = src.get(key)
    return float(v) if isinstance(v, (int, float)) else None


def pixel_delta(before_png, after_png):
    """(changed_fraction, max_channel_delta) or (None, reason)."""
    try:
        from PIL import Image
    except ImportError:
        return None, "Pillow not installed"
    for p in (before_png, after_png):
        if not p or not os.path.exists(p):
            return None, "missing %s" % (os.path.basename(p or "?"))
    a = Image.open(before_png).convert("RGB")
    b = Image.open(after_png).convert("RGB")
    if a.size != b.size:
        return None, "size %s vs %s" % (a.size, b.size)
    ap, bp = a.getdata(), b.getdata()
    changed = 0
    worst = 0
    n = 0
    for pa, pb in zip(ap, bp):
        n += 1
        d = max(abs(pa[0] - pb[0]), abs(pa[1] - pb[1]), abs(pa[2] - pb[2]))
        if d:
            changed += 1
            if d > worst:
                worst = d
    return (changed / n if n else 0.0), worst


def regressions(before, after):
    """Only losses that are losses under any art direction. See the docstring."""
    out = []
    for key, label in (("clipped_pct", "highlights blown"),
                       ("crushed_pct", "shadows crushed")):
        b, a = _stat(before, key), _stat(after, key)
        if b is not None and a is not None and a - b > TOL_PCT:
            out.append("%s: %s %.2f%% -> %.2f%%" % (label, key, b, a))
    p05, p95 = _stat(after, "p05"), _stat(after, "p95")
    if p05 is not None and p95 is not None and (p95 - p05) < UNIFORM_SPREAD:
        out.append("frame is uniform (p05 %.0f, p95 %.0f): renders nothing, "
                   "or renders one wall" % (p05, p95))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--images", action="store_true",
                    help="also diff the PNGs (catches geometry; slower)")
    ap.add_argument("--gate", action="store_true",
                    help="exit nonzero on a regression or an incomparable pair")
    ap.add_argument("--allow-mixed", action="store_true",
                    help="compare across differing render provenance anyway")
    args = ap.parse_args(argv)

    try:
        before, after = load(args.before), load(args.after)
    except (OSError, ValueError) as exc:
        sys.stderr.write("unreadable: %s\n" % exc)
        return 2

    ok, diffs = comparable(before, after)
    if not ok:
        print("REFUSED: these runs are not comparable")
        for d in diffs:
            print("   " + d)
        print("A pixel diff across two adapters measures the driver, not the "
              "level.")
        if not args.allow_mixed:
            return 2 if args.gate else 0
        print("--allow-mixed: comparing anyway; every number below is suspect")

    bs = {s.get("name"): s for s in before.get("shots", [])}
    as_ = {s.get("name"): s for s in after.get("shots", [])}
    gone = sorted(set(bs) - set(as_))
    new = sorted(set(as_) - set(bs))

    print("shots: %d before, %d after" % (len(bs), len(as_)))
    for n in gone:
        print("  REMOVED  %s" % n)
    for n in new:
        print("  ADDED    %s" % n)

    print()
    hdr = "%-14s %9s %9s %9s %9s" % ("shot", "d_mean", "d_p50", "d_clip%",
                                     "d_crush%")
    if args.images:
        hdr += " %10s %7s" % ("px_changed", "max_d")
    print(hdr)

    any_regression = False
    unchanged = []
    for name in sorted(set(bs) & set(as_)):
        b, a = bs[name], as_[name]
        row = [name]
        for key in ("mean", "p50", "clipped_pct", "crushed_pct"):
            vb, va = _stat(b, key), _stat(a, key)
            row.append("%+9.2f" % (va - vb) if (vb is not None and va is not None)
                       else "%9s" % "n/a")
        line = "%-14s %s" % (row[0], " ".join(row[1:]))
        moved = any(f.strip() not in ("+0.00", "n/a") for f in row[1:])
        if args.images:
            frac, worst = pixel_delta(b.get("png"), a.get("png"))
            if frac is None:
                line += " %10s %7s" % ("--", str(worst)[:7])
            else:
                line += " %9.2f%% %7d" % (frac * 100.0, worst)
                moved = moved or frac > 0
        print(line)
        if not moved:
            unchanged.append(name)
        for r in regressions(b, a):
            any_regression = True
            print("      REGRESSION  %s" % r)

    print()
    if unchanged:
        # Saying so matters: an unchanged shot after a change you EXPECTED to
        # see is the same finding as a changed shot you did not.
        print("unchanged: %s" % ", ".join(unchanged))
    else:
        print("every shot moved")
    if not any_regression:
        print("no regressions (clipping, crushing, uniform frames)")

    if args.gate and (any_regression or (not ok and not args.allow_mixed)):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
