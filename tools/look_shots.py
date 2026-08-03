"""Photograph a generated level and put a number on how it is exposed.

WHAT THIS IS FOR, and the gap it does not close. Every guardrail in this repo
measures traversal correctness -- can a body get from A to B. None measures
whether the result reads as designed rather than generated, and of the three
problems found by actually playing a generated level, two were caught by a
person looking at the screen (`PIPELINE_ROADMAP.md` item 18). This does not fix
that. A histogram cannot tell you a level looks generated.

What it does do is remove the cheapest third of it from the human's plate: a
frame crushed against white is broken in a way nobody needs to be consulted
about, and until now nothing in the pipeline could see it, because nothing in
the pipeline had ever looked at a picture.

RETRACTED, kept above the result that replaced it. The first draft of this
paragraph said this tool found Lot's WorldEnvironment "blowing 28.6% of the
overview and 59.9% of the objective shot to pure white". Those figures came from
a hand-run at 1280x720, through hand-placed cameras, counting >=254 as clipped.
Re-measured through THIS tool's derived cameras at 1600x900, the same project
clips 0.00% at 255. The effect is real and an order of magnitude smaller than
advertised: on the overview, un-Lux'd is 18.62% of pixels within three codes of
white against 1.13% with Lux, and mean luminance 108.6 against 147.0. Two
framings of one scene are two instruments, and the number that ships must be the
one this tool actually produces.

    coldrun_pawn_job, opengl3/llvmpipe, HUD hidden
                    mean    p95   near-clip
      no Lux       108.6    254      18.62%
      Lux, 2 suns  151.7    248       3.17%
      Lux, 1 sun   147.0    222       1.13%

    python tools\\look_shots.py <project_dir> [--out shots/] [--scene X.tscn]

THE CAMERAS ARE DERIVED, NOT CHOSEN. Eye-level shots stand on the walk scene's
own exported spawn_pos / objective_pos / extraction_pos, at the height of the
Player's own Camera3D, facing the next leg of the spine. The overview is framed
from the site's visual AABB against the camera's FOV. Nothing here is a
coordinate somebody liked the look of, so the same tool frames a bigger site
correctly without being re-tuned.

STATE THE FRAME. Luminance is Rec.709 on the 8-bit sRGB values that reached the
swap chain -- after tonemapping, after Lux's post stack -- and it is not
scene-referred light. The report carries the rendering method and the graphics
adapter with every run, because the same scene grades differently under
Compatibility and Forward+; two runs on different adapters are two instruments
and comparing them is the mistake this line exists to prevent.

THIS ONE NEEDS A DISPLAY. `--headless` disables rendering outright, so there is
nothing to capture. On Windows it runs in a normal window. On a Linux box with
no DISPLAY it is wrapped in xvfb-run when that exists, which means llvmpipe --
usable for an A/B against itself, not for a number you quote next to a Forward+
one.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from godot_probe import ProbeFailed, run_probe, require_godot   # noqa: E402
from light_census import default_scene                          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PAYLOAD = os.path.join(HERE, "look_shots.gd")
MARK_BEGIN = "<<<LOOK_SHOTS_JSON"
MARK_END = "LOOK_SHOTS_JSON>>>"


def shoot(project_dir, out_dir, scene=None, godot=None, width=1600, height=900,
          settle=10, frames_per_shot=6, keep_hud=False, rendering_driver=None,
          timeout=900, verbose=False):
    scene = scene or default_scene(project_dir)
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    settings = {
        "look_shots": {
            # Godot writes the PNGs itself, so it needs a filesystem path it can
            # reach. Forward slashes: a Windows backslash inside a project.godot
            # string is an escape and eats the next character.
            "out_dir": out_dir.replace("\\", "/"),
            "settle_frames": settle,
            "frames_per_shot": frames_per_shot,
            "hide_non_lux_canvas": not keep_hud,
        },
        "display": {
            "window/size/viewport_width": width,
            "window/size/viewport_height": height,
        },
    }
    extra = []
    if rendering_driver:
        extra += ["--rendering-driver", rendering_driver]

    payload, _out, _mirror = run_probe(
        project_dir=project_dir,
        script_src=PAYLOAD,
        autoload_name="LookShots",
        scene="res://" + scene,
        begin=MARK_BEGIN, end=MARK_END,
        godot=godot or require_godot(),
        settings=settings,
        headless=False,          # rendering is the point; headless has none
        extra_args=extra,
        timeout=timeout, verbose=verbose)
    return payload


def report(r):
    if "error" in r:
        print("  probe error: " + str(r["error"]))
        return
    print("  engine   " + str(r.get("engine", "?")))
    print("  method   " + str(r.get("rendering_method", "?")) +
          "   (what the project asks for)")
    print("  api      " + str(r.get("adapter_api", "?")) +
          "   (what this process bound)")
    print("  adapter  " + str(r.get("adapter", "?")) +
          " (" + str(r.get("adapter_vendor", "?")) + ")")
    print("  viewport " + str(r.get("viewport", "?")))
    hidden = r.get("hidden_canvas_layers", [])
    if hidden:
        print("  hidden non-Lux CanvasLayers: " + ", ".join(hidden))
    else:
        print("  hidden non-Lux CanvasLayers: none")
    print("")
    header = ("  %-12s %8s %6s %6s %6s %9s %9s %9s"
              % ("shot", "mean", "p05", "p50", "p95", "clipped", "near-clip",
                 "crushed"))
    print(header)
    for s in r.get("shots", []):
        if not s.get("pixels"):
            print("  %-12s (no pixels)" % s.get("name", "?"))
            continue
        print("  %-12s %8.1f %6d %6d %6d %8.2f%% %8.2f%% %8.2f%%"
              % (s["name"], s["mean"], s["p05"], s["p50"], s["p95"],
                 s["clipped_pct"], s["near_clipped_pct"], s["crushed_pct"]))
    print("")
    for s in r.get("shots", []):
        print("  %-12s %s" % (s.get("name", "?"), s.get("png", "")))
        print("               from %s" % s.get("derivation", ""))
        if s.get("png_error"):
            print("               PNG WRITE FAILED, Godot error %s"
                  % s["png_error"])


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="render a generated level from derived cameras and report "
                    "the exposure of each frame")
    ap.add_argument("project", help="the Godot project folder to photograph")
    ap.add_argument("--out", default="shots",
                    help="directory for the PNGs (default: %(default)s)")
    ap.add_argument("--scene", default=None,
                    help="scene to run; default is the single *_walk.tscn")
    ap.add_argument("--godot", default=None,
                    help="path to the Godot binary; default LOT_GODOT, then "
                         "DC_GODOT, then the usual install locations, then PATH")
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--height", type=int, default=900)
    ap.add_argument("--settle", type=int, default=10,
                    help="frames to wait before the first shot")
    ap.add_argument("--frames-per-shot", type=int, default=6,
                    help="drawn frames to let each camera settle; TAA and glow "
                         "need more than one")
    ap.add_argument("--keep-hud", action="store_true",
                    help="leave the walk harness HUD in frame. Its text is pure "
                         "white and clips, so it biases every statistic below")
    ap.add_argument("--rendering-driver", default=None,
                    help="passed straight to Godot, e.g. opengl3. Leave unset "
                         "to use the project's own, which is what ships")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args(argv)

    try:
        r = shoot(a.project, a.out, a.scene, a.godot, a.width, a.height,
                  a.settle, a.frames_per_shot, a.keep_hud, a.rendering_driver,
                  a.timeout, a.verbose)
    except ProbeFailed as e:
        print("[look_shots] NOT MEASURED: " + str(e))
        return 1

    # The run records the INSTRUMENT (adapter, driver, viewport) and recorded
    # nothing about the SUBJECT, so two runs of DIFFERENT PROJECTS compared
    # cleanly and silently: a Lux-lit export against an unlit walk project,
    # reported as "every shot moved". A photograph without its subject is not
    # evidence.
    r["project"] = os.path.abspath(a.project)
    r["scene"] = a.scene or ""
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        print("[look_shots] " + os.path.abspath(a.project))
        report(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
