"""Measure the precision of the render target the Lux post pass reads from.

    python tools/film_precision_probe.py --project lux

WHY. The film emulsion TDD (lux/docs/film_emulsion_tdd.md) section 20 forbids
converting scene color to RGB8 before the film math runs, and section 7 requires
the film math to live inside the existing Lux canvas_item post pass. Those two
requirements can only both hold if the viewport's render target is
high-precision. Whether it is depends on `rendering/viewport/hdr_2d`, which the
Lux project does not set, so it sits at the engine default.

The class reference gives that default as false -- for engine 4.2. This project
runs 4.7. A 7.5 MiB-at-1080p decision should not rest on a documentation page
for a version that is not the one running, so this measures the engine instead.

WHAT IT RUNS. Two passes over the same project:

  baseline  the project exactly as it ships
  hdr_2d    the same project with rendering/viewport/hdr_2d = true injected

The second pass is not a recommendation. It is the evidence for whether option
(a) in the Phase 1 audit is even available -- a setting name that Godot ignores
would leave `viewport_use_hdr_2d` false and the format unchanged, and this tool
says so rather than reporting the injection as a success.

WHAT IT REFUSES TO DO. It never infers the format from the level count or the
level count from the format. Both are measured and both are printed; when they
disagree, the disagreement is the finding and the exit code is non-zero.

NEEDS A DISPLAY. `--headless` disables rendering, so there is nothing to read
back. godot_probe wraps this in xvfb-run on a Linux box without one, which means
llvmpipe -- fine for a format question, not for a performance one.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from godot_probe import ProbeFailed, run_probe, require_godot   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PAYLOAD = os.path.join(HERE, "film_precision_probe.gd")
MARK_BEGIN = "<<<FILM_PRECISION_JSON"
MARK_END = "FILM_PRECISION_JSON>>>"

#: Formats that can hold more than 8 bits per channel. Named rather than
#: inferred: "not RGBA8" would also be true of RGB8, which is worse.
HIGH_PRECISION = ("RGBAH", "RGBH", "RGBAF", "RGBF", "RGBE9995")


def main_scene(project_dir):
    """The project's own run/main_scene, so the probe measures ITS viewport."""
    pg = os.path.join(project_dir, "project.godot")
    if not os.path.isfile(pg):
        raise ProbeFailed("no project.godot in " + project_dir)
    with open(pg, encoding="utf-8") as f:
        m = re.search(r'^run/main_scene\s*=\s*"([^"]+)"', f.read(), re.M)
    if not m:
        raise ProbeFailed(
            "project.godot has no run/main_scene, so there is no scene to "
            "measure against. Pass --scene.")
    return m.group(1)


def probe(project_dir, scene=None, godot=None, width=1600, height=900,
          hdr_2d=None, rendering_driver=None, timeout=600, verbose=False):
    """One pass. `hdr_2d=None` leaves the project alone; True/False injects."""
    settings = {
        "display": {
            "window/size/viewport_width": width,
            "window/size/viewport_height": height,
        },
    }
    if hdr_2d is not None:
        settings["rendering"] = {"viewport/hdr_2d": bool(hdr_2d)}

    extra = []
    if rendering_driver:
        extra += ["--rendering-driver", rendering_driver]

    payload, raw, _mirror = run_probe(
        project_dir=project_dir,
        script_src=PAYLOAD,
        autoload_name="FilmPrecisionProbe",
        scene=scene or main_scene(project_dir),
        begin=MARK_BEGIN, end=MARK_END,
        godot=godot or require_godot(),
        settings=settings,
        headless=False,          # rendering is the point; headless has none
        extra_args=extra,
        timeout=timeout, verbose=verbose)

    if verbose and raw:
        inside = False
        for line in raw.splitlines():
            if line.strip() == MARK_BEGIN:
                inside = True
            elif line.strip() == MARK_END:
                inside = False
            elif not inside:
                print("  | " + line)
    return payload


def _is_high_precision(name):
    return any(name.startswith(p) for p in HIGH_PRECISION)


def report(baseline, injected):
    """Print both passes and return the number of findings that need a human."""
    findings = []

    print("  Godot        %s" % baseline.get("godot_version"))
    print("  renderer     %s" % baseline.get("rendering_method"))
    print("  adapter      %s" % baseline.get("adapter"))
    print("  ramp         %.3f -> %.3f across %d px"
          % (baseline["ramp_low"], baseline["ramp_high"], baseline["width"]))
    print("  an RGBA8 target could carry %d distinct levels over that ramp"
          % baseline["levels_if_rgba8"])
    print("")

    for label, p in (("baseline", baseline), ("hdr_2d injected", injected)):
        if p is None:
            print("  %-16s did not run" % label)
            continue
        fmt = p["image_format_name"]
        hp = _is_high_precision(fmt)
        print("  %-16s format %-22s use_hdr_2d=%-5s distinct levels %d"
              % (label, fmt, p["viewport_use_hdr_2d"], p["distinct_levels"]))

        # The two measurements must agree about which world we are in. A count
        # at or below what 8 bits can carry, from a format that claims more,
        # means something downstream of the target is quantizing -- worth more
        # than either number alone.
        counted_high = p["distinct_levels"] > p["levels_if_rgba8"]
        if hp != counted_high:
            findings.append(
                "%s: format says %s but the ramp carried %d distinct levels "
                "(an 8-bit target holds at most %d). The format and the pixels "
                "disagree; do not quote either until that is explained."
                % (label, fmt, p["distinct_levels"], p["levels_if_rgba8"]))

    if baseline and injected:
        if baseline["rendering_method"] != injected["rendering_method"]:
            findings.append(
                "the injected pass changed the rendering method (%s -> %s). "
                "Appending a second [rendering] section replaced the first "
                "rather than merging; the injected result measures a different "
                "renderer and is not comparable."
                % (baseline["rendering_method"], injected["rendering_method"]))
        elif not injected["viewport_use_hdr_2d"]:
            findings.append(
                "injecting rendering/viewport/hdr_2d=true left "
                "Viewport.use_hdr_2d false. Either the setting name is wrong "
                "for this engine version or it is not applied to the root "
                "viewport. Option (a) in the Phase 1 audit is NOT available "
                "by this route.")

    print("")
    base_fmt = baseline["image_format_name"]
    if _is_high_precision(base_fmt):
        print("  As shipped, the Lux post pass reads %s -- high precision."
              % base_fmt)
        print("  TDD section 20 is satisfiable inside the existing pass.")
    else:
        print("  As shipped, the Lux post pass reads %s." % base_fmt)
        print("  Scene color is ALREADY reduced before any film math can run.")
        print("  TDD section 20 cannot be claimed on this path (Phase 1 audit,")
        print("  option (b)). Option (a) is the hdr_2d pass above.")

    if findings:
        print("")
        for f in findings:
            print("  FINDING: " + f)
    return len(findings)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project", default="lux",
                    help="Godot project directory (default: lux)")
    ap.add_argument("--scene", default=None,
                    help="scene to run (default: the project's main_scene)")
    ap.add_argument("--godot", default=None)
    ap.add_argument("--rendering-driver", default=None,
                    help="passed through to Godot, e.g. vulkan / opengl3")
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--no-hdr-pass", action="store_true",
                    help="run only the baseline pass")
    ap.add_argument("--json", default=None, help="write both payloads here")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args(argv)

    project = os.path.abspath(a.project)
    common = dict(scene=a.scene, godot=a.godot, width=a.width, height=a.height,
                  rendering_driver=a.rendering_driver, verbose=a.verbose)
    try:
        print("film precision probe -- %s" % project)
        baseline = probe(project, hdr_2d=None, **common)
        injected = None
        if not a.no_hdr_pass:
            injected = probe(project, hdr_2d=True, **common)
    except ProbeFailed as e:
        print("NOTHING MEASURED: " + str(e))
        return 2

    n = report(baseline, injected)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump({"baseline": baseline, "hdr_2d": injected}, f, indent=2)
        print("")
        print("  wrote " + a.json)
    return 1 if n else 0


if __name__ == "__main__":
    raise SystemExit(main())
