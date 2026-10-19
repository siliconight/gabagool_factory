"""Shoot the asset flags' boxes in a real walk copy, from where the walker stood when they flagged.

    python outline_frames.py <walk copy> [--out DIR]     # default: outline_frames/ beside this file
    python outline_frames.py --jpeg DIR                  # convert a run's PNG frames to JPEG, as a run does at its end

Reads the copy's `asset_flags.jsonl` for the walker's own flags of 2026-10-19 (the first and the fourth: behind the
car and beside it), and runs `outline_frame.gd` through `tools/godot_probe.py` -- on a MIRROR of the copy, in a
1152 x 648 window like the walker's -- which presses P and G from those places and from four more worked from them:
nine metres back, turned 35 degrees left toward the street's buildings, at the ground two metres right of the car, and
five metres from the nearest part of a building the handler's own pick finds, swept round where the walker stood.
Writes the frames and `outline_frames.json` (each press's record and every box drawn, in Godot metres, Y up), with any
line of Godot's output that says ERROR or SHADER beside them. Prints what it measured and stops.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from godot_probe import run_probe, require_godot   # noqa: E402

BEGIN, END = "<<<OUTLINE_FRAME_JSON", "OUTLINE_FRAME_JSON>>>"


def _add(a, b, k=1.0):
    return [a[i] + k * b[i] for i in range(3)]


def shots_from(records):
    """The five shots, from the walker's flags 1 and 4 of 2026-10-19."""
    by_time = sorted(records, key=lambda r: r["time_utc"])
    r1, r4 = by_time[0], by_time[3]
    look = r1["looking"]
    flat = [look[0], 0.0, look[2]]
    n = math.hypot(flat[0], flat[2])
    flat = [flat[0] / n, 0.0, flat[2] / n]
    right = [-flat[2], 0.0, flat[0]]           # forward x up, for Y up
    mid = [(r1["point"][i] + r4["point"][i]) / 2 for i in range(3)]
    far_eye = _add(mid, flat, -9.0)
    far_eye[1] = 2.2
    a = math.radians(35.0)                     # about +Y, which turns a view to its left
    left = [look[0] * math.cos(a) + look[2] * math.sin(a), 0.05, -look[0] * math.sin(a) + look[2] * math.cos(a)]
    ground = _add(r1["point"], right, 2.0)
    ground[1] = 0.05
    return [
        {"name": "p_behind_the_car", "eye": r1["camera"], "target": r1["point"], "verdict": "needs_love"},
        {"name": "g_beside_the_car", "eye": r4["camera"], "target": r4["point"], "verdict": "good"},
        {"name": "p_nine_metres_back", "eye": far_eye, "target": mid, "verdict": "needs_love"},
        {"name": "p_turned_left", "eye": r1["camera"], "target": _add(r1["camera"], left, 10.0), "verdict": "needs_love"},
        {"name": "p_ground_right_of_the_car", "eye": r1["camera"], "target": ground, "verdict": "needs_love"},
        {"name": "p_nearest_building_wall", "eye": r1["camera"], "target": r1["point"], "verdict": "needs_love",
         "sweep_for": "res://lot/", "stand_m": 5.0},
    ]


def to_jpeg(out):
    """The frames as JPEGs at quality 85, the PNGs removed and the report's paths moved with them: a 1152 x 648 PNG of a
    rainy night is about 1.2 MB, more than the repo needs to show a box."""
    from PIL import Image
    path = os.path.join(out, "outline_frames.json")
    with open(path, encoding="utf-8") as fh:
        payload = json.load(fh)
    for s in payload.get("shots", []):
        png = s["frame"]
        if png.lower().endswith(".png") and os.path.isfile(png):
            jpg = png[:-4] + ".jpg"
            Image.open(png).convert("RGB").save(jpg, quality=85, optimize=True)
            os.remove(png)
            s["frame"] = jpg
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=1)


def main(argv):
    if "--jpeg" in argv:
        return to_jpeg(os.path.abspath(argv[argv.index("--jpeg") + 1])) or 0
    copy = os.path.abspath(argv[0])
    out = os.path.abspath(argv[argv.index("--out") + 1]) if "--out" in argv else os.path.join(HERE, "outline_frames")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(copy, "asset_flags.jsonl"), encoding="utf-8") as fh:
        records = [json.loads(line) for line in fh if line.strip()]
    records = [r for r in records if r.get("time_utc", "").startswith("2026-10-19T21:25:")]
    if len(records) != 5:
        raise SystemExit("expected the walker's five flags of 2026-10-19T21:25, found %d" % len(records))
    shots = shots_from(records)
    payload, raw, _mirror = run_probe(
        project_dir=copy, script_src=os.path.join(HERE, "outline_frame.gd"), autoload_name="OutlineFrame",
        scene="res://_walk.tscn", begin=BEGIN, end=END, godot=require_godot(),
        settings={"outline_frame": {"out_dir": out.replace("\\", "/"), "shots": json.dumps(shots)},
                  "display": {"window/size/viewport_width": 1152, "window/size/viewport_height": 648}},
        headless=False, timeout=900)
    payload["godot_said"] = [ln for ln in raw.splitlines() if "ERROR" in ln or "SHADER" in ln][:40]
    payload["copy"] = copy
    with open(os.path.join(out, "outline_frames.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=1)
    to_jpeg(out)
    if "error" in payload:
        print("probe error:", payload["error"])
        return 1
    for s in payload["shots"]:
        print("%-28s %-10s how=%-7s %5.2f m  %s" % (s["name"], s["verdict"], s["how"], s["distance_m"], s["asset"] or s["node"]))
    print("boxes after the last press:")
    for b in payload["shots"][-1]["boxes"]:
        print("  %-10s size %s  round %s" % (b["verdict"], [round(v, 2) for v in b["size"]], b["target"]))
    print("%d line(s) of Godot's output say ERROR or SHADER" % len(payload["godot_said"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
