"""Do the LuxEmit_* markers carry their glTF-extras payload at runtime?

One diagnostic question with a yes/no answer, asked after the 2026-08-24
census showed every fluorescent at the no-drop range fallback while the
fixtures GLB verifiably carried `lux_drop` in every marker's extras. The
only step between the file and the spawner is Godot's import of node extras
into metadata, and `marker_type`'s name-parse fallback has masked that
step's health since v0.30 -- the type working proves nothing, because the
type is also in the node name.

    python tools\\marker_meta_probe.py <project_dir> [--scene X.tscn]

Exit 0 whenever it measured; the numbers are the answer. Exit 1 = did not
measure (no Godot, no project, no fence) -- never reported as a result.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from godot_probe import ProbeFailed, run_probe, require_godot   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PAYLOAD = os.path.join(HERE, "marker_meta_probe.gd")
MARK_BEGIN = "<<<MARKER_META_JSON"
MARK_END = "MARKER_META_JSON>>>"


def default_scene(project_dir):
    pg = os.path.join(project_dir, "project.godot")
    if os.path.isfile(pg):
        with open(pg, encoding="utf-8", errors="replace") as f:
            m = re.search(r'run/main_scene="res://([^"]+)"', f.read())
        if m and os.path.isfile(os.path.join(project_dir, m.group(1))):
            return m.group(1)
    raise ProbeFailed("no run/main_scene in project.godot. Pass --scene.")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="runtime check: LuxEmit markers' extras-as-metadata")
    ap.add_argument("project")
    ap.add_argument("--scene", default=None)
    ap.add_argument("--godot", default=None)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args(argv)
    try:
        scene = a.scene or default_scene(a.project)
        c, _out, _mirror = run_probe(
            project_dir=a.project, script_src=PAYLOAD,
            autoload_name="MarkerMetaProbe", scene="res://" + scene,
            begin=MARK_BEGIN, end=MARK_END,
            godot=a.godot or require_godot(),
            headless=True, timeout=a.timeout, verbose=a.verbose)
    except ProbeFailed as e:
        print("[marker_meta_probe] NOT MEASURED: " + str(e))
        return 1

    if "error" in c:
        print("[marker_meta_probe] probe error: " + str(c["error"]))
        return 1
    print("[marker_meta_probe] scene " + str(c["scene"]))
    print("  markers found            " + str(c["markers_found"]))
    print("  with ANY metadata        " + str(c["markers_with_any_meta"]))
    print("  with lux_drop            " + str(c["markers_with_lux_drop"]))
    for s in c.get("samples", []):
        print("    %-28s keys=%s  lux_drop=%s"
              % (s["name"], s["meta_keys"], s["lux_drop"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
