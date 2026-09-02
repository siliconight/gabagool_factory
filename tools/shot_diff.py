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

THE NULL SHOT, and why a pixel count means nothing without one. `look_shots`
accumulates six frames per shot because TAA and glow need more than one, so two
launches of the SAME project do not converge to the same pixels. Measured
2026-08-29 by shooting `wJ` twice with nothing changed between runs:

    elev_N   mean 2.1185   %px>2 41.977%   max |delta|  9
    elev_W   mean 2.1305   %px>2 41.952%   max |delta|  7
    spawn    mean 2.0852   %px>2 39.223%   max |delta| 15

Forty-two percent of pixels differ between a project and itself. Every
`%px changed` figure below that is noise, and this tool reported several of
them as findings before anyone checked -- a pier five times larger measured
41.916% on one elevation, against a floor of 41.977%.

`max |delta|` is the statistic that separates: floor 7-15, an un-mipmapped
import 51-148, a real geometry change 122-211. Pass `--null <shots.json>` from
a re-shoot of an UNCHANGED project and every shot is judged against its own
floor rather than against zero. The floor is a property of the project and the
frame count, not a constant, so it is measured rather than hard-coded, and a
shot inside it is reported as `~floor` and does not count as moved.

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
#: How far above a measured floor still counts as the floor. One null run is
#: one sample of a distribution; see the note at the verdict below.
MARGIN = 1.5


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


def same_subject(a, b):
    """(verdict, note) -- did these photograph the SAME THING?

    The instrument check above catches a changed camera. It cannot catch a
    changed SUBJECT, and the first real comparison run by this tool comprised a
    Lux-lit export against an unlit walk project: every statistic moved, every
    pixel changed, and the result was a photograph of two different levels
    reported as a difference in one. `project` is recorded from look_shots
    v-next; runs predating it say nothing, and unknown must not read as same.
    """
    # ART FIRST, PATH LAST, and that ordering is the whole correction.
    # This guarded the project PATH, which is the difference an A/B is SUPPOSED
    # to have -- two builds go to two directories. The difference that voids a
    # comparison is the ART, and it was not recorded, so on 2026-08-29 two
    # published readings each moved two variables (a stale `wear: 0.0` baked
    # into the workspace's job outputs, copied into three later builds) while
    # this function reported only "different projects". It fired both times and
    # named the harmless half.
    sa, sb = a.get("subject"), b.get("subject")
    if isinstance(sa, dict) and isinstance(sb, dict):
        da, db = sa.get("art_digest"), sb.get("art_digest")
        ta, tb = sa.get("treatment") or {}, sb.get("treatment") or {}
        moved = sorted(k for k in set(ta) | set(tb) if ta.get(k) != tb.get(k))
        if da and db and da != db:
            note = ("art %s (%s files) vs %s (%s files)"
                    % (da[:12], sa.get("art_files"), db[:12], sb.get("art_files")))
            if moved:
                note += "\n   AND treatment moved: " + ", ".join(
                    "%s %r -> %r" % (k, ta.get(k), tb.get(k)) for k in moved)
            else:
                note += "\n   treatment is identical, so the ART itself changed"
            return "differs", note
        if moved:
            return "same", ("art %s, identical\n   treatment moved (this is "
                            "the experiment): %s" % (da[:12] if da else "?",
                            ", ".join("%s %r -> %r" % (k, ta.get(k), tb.get(k))
                                      for k in moved)))
        return "same", "art %s, treatment identical" % (da[:12] if da else "?")

    pa, pb = a.get("project"), b.get("project")
    if pa is None or pb is None:
        return "unknown", ("one or both runs predate subject recording -- "
                           "cannot verify these photographed the same project")
    if os.path.normcase(os.path.abspath(pa)) != os.path.normcase(os.path.abspath(pb)):
        return "unknown", ("no art digest on either run; paths differ, which "
                           "on its own proves nothing either way:\n   %s\n"
                           "   vs %s" % (pa, pb))
    return "unknown", ("%s -- same path, but no art digest, so a stale "
                       "rebuild would look identical here" % pa)


def _stat(shot, key, centre=False):
    src = shot.get("centre", {}) if centre else shot
    v = src.get(key)
    return float(v) if isinstance(v, (int, float)) else None


def resolve_png(json_path, recorded):
    """Where the PNG IS, not where it was made.

    `shots_*.json` records an absolute path. Copy the pair aside as a baseline
    -- which is exactly what keeping a "before" requires -- and that path still
    points at the LIVE directory, so --images diffs each picture against
    itself and reports 0.00% with total confidence. The first real run of this
    tool did precisely that. A JSON travels with its own directory; the
    recorded path is provenance, not a location.
    """
    if not recorded:
        return None
    base = os.path.basename(str(recorded).replace("\\", "/"))
    d = os.path.dirname(os.path.abspath(json_path))
    stem = os.path.splitext(os.path.basename(json_path))[0]
    for cand in (os.path.join(d, stem, base), os.path.join(d, base), recorded):
        if os.path.exists(cand):
            return cand
    return recorded


def pixel_delta(before_png, after_png, threshold=8):
    """(fraction changed by more than ``threshold``, max delta), or (None, why).

    THRESHOLDED, because counting any nonzero delta reported 100.00% on all
    four shots the first time this ran: a global exposure shift moves every
    pixel by at least one code, and a metric that saturates on every real
    change measures nothing. 8/255 is roughly where a flat-surface difference
    stops being invisible.
    """
    try:
        from PIL import Image
    except ImportError:
        return None, "Pillow not installed"
    for p in (before_png, after_png):
        if not p or not os.path.exists(p):
            return None, "missing %s" % (os.path.basename(p or "?"))
    if os.path.abspath(before_png) == os.path.abspath(after_png):
        return None, "SAME FILE -- the baseline PNGs were not copied aside"
    a = Image.open(before_png).convert("RGB")
    b = Image.open(after_png).convert("RGB")
    if a.size != b.size:
        return None, "size %s vs %s" % (a.size, b.size)
    ab, bb = a.tobytes(), b.tobytes()
    try:
        import numpy as np
    except ImportError:
        changed = worst = 0
        for i in range(0, len(ab), 3):
            d = max(abs(ab[i] - bb[i]), abs(ab[i + 1] - bb[i + 1]),
                    abs(ab[i + 2] - bb[i + 2]))
            if d > threshold:
                changed += 1
                worst = max(worst, d)
        n = len(ab) // 3
        return (changed / n if n else 0.0), worst
    aa = np.frombuffer(ab, np.uint8).reshape(-1, 3).astype(np.int16)
    bv = np.frombuffer(bb, np.uint8).reshape(-1, 3).astype(np.int16)
    d = np.abs(aa - bv).max(axis=1)
    return (float((d > threshold).mean()), int(d.max()))


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
    ap.add_argument("--null", default=None,
                    help="a shots.json from re-shooting one of these runs with "
                         "NOTHING changed. Establishes this project's own "
                         "repeatability so a shot inside it is not reported as "
                         "a finding. Implies --images")
    ap.add_argument("--null-of", choices=("before", "after"), default=None,
                    help="which run the --null set re-shot. Inferred from the "
                         "subject stamps when they differ; REQUIRED when both "
                         "runs photographed the same subject, because then "
                         "nothing in the files can tell them apart")
    ap.add_argument("--threshold", type=int, default=8,
                    help="per-channel delta a pixel must exceed to count as "
                         "changed (default 8; 0 counts any difference and "
                         "saturates on any exposure shift)")
    ap.add_argument("--art-changed", action="store_true",
                    help="the ART is the variable under test -- a genome or "
                         "spec value moved and the level was rebuilt. Accepts "
                         "a differing art digest as the EXPERIMENT rather than "
                         "as contamination, and still refuses when the "
                         "treatment moved as well, because that is two "
                         "variables whichever one you meant")
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

    verdict, note = same_subject(before, after)
    if verdict == "differs":
        # AN ART CHANGE CAN BE THE EXPERIMENT. Changing a genome value and
        # rebuilding is the most ordinary A/B this factory runs, and the first
        # version of this guard had no way to say so -- which would have made
        # `--allow-mixed` the habitual answer, and a guard everyone waves
        # through is not a guard. `--art-changed` says the difference was
        # intended; it still refuses when the treatment moved too, because
        # that is two variables no matter which one was meant.
        treatment_moved = "treatment moved" in note
        if args.art_changed and not treatment_moved:
            print("ART CHANGED, and you said so (--art-changed):")
            print("   " + note)
            print("Numbers below are the effect of the art change.")
        else:
            print("SUBJECT DIFFERS -- the ART is not the same:")
            print("   " + note)
            print("Every number below is a difference between LEVELS, not a "
                  "difference in one level.")
            if args.art_changed and treatment_moved:
                print("--art-changed does NOT cover this: the treatment moved "
                      "as well, so two variables are in flight.")
            if not args.allow_mixed:
                return 2 if args.gate else 0
    elif verdict == "unknown":
        print("subject: UNKNOWN -- " + note)
    else:
        print("subject: " + note)

    bs = {s.get("name"): s for s in before.get("shots", [])}
    as_ = {s.get("name"): s for s in after.get("shots", [])}
    gone = sorted(set(bs) - set(as_))
    new = sorted(set(as_) - set(bs))

    # THE NULL RUN IS A THIRD SET OF PICTURES, not a number. It is loaded here
    # rather than folded into the loop so that a null whose camera or GPU moved
    # is refused on the same terms as a mismatched before/after -- a floor
    # measured through a different instrument is worse than no floor.
    nulls = {}
    if args.null:
        args.images = True
        null_doc = load(args.null)
        null_ok, null_why = comparable(after, null_doc)
        if not null_ok:
            print("REFUSED: the null run is not comparable with `after`")
            for w in null_why:
                print("   %s" % w)
            return 2
        # WHICH RUN IS IT A RE-SHOOT OF. This has to be established, not
        # assumed, and assuming it is how the first version of this feature
        # got the answer exactly backwards: measuring the floor as
        # `after vs null` when the null was a re-shoot of BEFORE folds the
        # real change into the floor, and the shot with a genuine 45-level
        # block came out `~floor` while a pure-noise shot came out MOVED.
        # The subject stamp already knows; ask it.
        m_after = same_subject(after, null_doc)[0] == "same"
        m_before = same_subject(before, null_doc)[0] == "same"
        if args.null_of:
            null_side = args.null_of
        elif m_after and not m_before:
            null_side = "after"
        elif m_before and not m_after:
            null_side = "before"
        elif m_after and m_before:
            # A treatment-only A/B leaves both subjects identical, and then no
            # amount of reading the files can say which one was re-shot. Ask.
            print("REFUSED: `before` and `after` photographed the same "
                  "subject, so the null could be a re-shoot of either.")
            print("   Say which with --null-of before|after.")
            return 2
        else:
            print("REFUSED: the null run photographed neither of these "
                  "subjects, so it cannot measure their floor.")
            print("   vs after:  " + same_subject(after, null_doc)[1])
            print("   vs before: " + same_subject(before, null_doc)[1])
            return 2
        null_ref = args.after if null_side == "after" else args.before
        nulls = {sh["name"]: sh for sh in null_doc.get("shots", [])}
        null_pairs = bs if null_side == "before" else as_
        print("null: %s  -- a re-shoot of `%s`; the floor is measured per shot"
              % (os.path.basename(args.null), null_side))

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
    if nulls:
        hdr += " %7s %8s" % ("floor", "verdict")
    print(hdr)

    any_regression = False
    unchanged = []
    below_floor = []
    marginal = []
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
            frac, worst = pixel_delta(resolve_png(args.before, b.get("png")),
                                      resolve_png(args.after, a.get("png")),
                                      args.threshold)
            if frac is None:
                line += " %10s %7s" % ("--", str(worst)[:7])
            else:
                line += " %9.2f%% %7d" % (frac * 100.0, worst)
                moved = moved or frac > 0
            # JUDGED AGAINST ITSELF. `worst` from the before/after pair means
            # nothing until the same pair of cameras has been asked what it
            # produces with NO change at all.
            if nulls and frac is not None:
                nsh = nulls.get(name)
                fl = None
                ref = null_pairs.get(name)
                if nsh is not None and ref is not None:
                    _f, fl = pixel_delta(
                        resolve_png(null_ref, ref.get("png")),
                        resolve_png(args.null, nsh.get("png")),
                        args.threshold)
                if not isinstance(fl, int):
                    line += " %7s %8s" % ("--", "no-null")
                elif worst <= fl:
                    line += " %7d %8s" % (fl, "~floor")
                    moved = False
                    below_floor.append(name)
                elif worst <= fl * MARGIN:
                    # ONE NULL IS ONE SAMPLE. The floor is a draw from a
                    # distribution, not a constant, so a value a little above
                    # it is another draw and not a finding. Measured on real
                    # runs the gap is not close -- floor 7-15, an un-mipmapped
                    # import 51-148, a real geometry change 122-211 -- so a
                    # generous band costs nothing and stops the tool crying
                    # wolf at 8 against 7.
                    line += " %7d %8s" % (fl, "marginal")
                    moved = False
                    marginal.append(name)
                else:
                    line += " %7d %8s" % (fl, "MOVED")
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
    if below_floor:
        # Not the same sentence as "unchanged". These shots DID differ; the
        # difference was smaller than what this project produces against
        # itself, which is a statement about the ruler, not about the level.
        print("inside the measured floor (no verdict): %s"
              % ", ".join(below_floor))
    if marginal:
        print("within %.2gx the floor, treated as noise: %s"
              % (MARGIN, ", ".join(marginal)))
    if nulls and not below_floor and not marginal:
        print("every shot cleared its own floor")
    if not any_regression:
        print("no regressions (clipping, crushing, uniform frames)")

    if args.gate and (any_regression or (not ok and not args.allow_mixed)):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
