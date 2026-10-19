"""Roadmap 24's proof, measured: does opening a shipped package's scene in the editor and saving it bake Lux's
runtime scaffolding into the scene -- and does it grow with each save?

    python owner_probe.py <package> <work dir> <out.json> [cycles] [scene] [--runtime <lux addons/lux/runtime>]

Copies the package to <work dir> (removed first), enables `owner_probe_plugin.gd` there, and runs Godot's editor
headless `cycles` times (default 2). Each run opens `scene` (default `res://presentation/lux.applied.tscn`, the
scene `bake.tscn` instances), lets the @tool scripts run, and saves. After each, the saved scene's `[node ...]`
headers are compared with the shipped scene's: a node path the save ADDED is scaffolding the editor kept, which
is the trap; one it removed would be a different defect. A probe: it prints what it measured and stops.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GODOT = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
PLUGIN_DIR = os.path.join("addons", "lux_owner_probe")
_NODE = re.compile(r'^\[node name="([^"]+)"(?: type="([^"]+)")?(?: parent="([^"]*)")?')


def nodes(tscn_text):
    """{path: type} for every [node] header; the root is ".", a child of the root "Name", deeper "A/B/Name"."""
    out = {}
    for line in tscn_text.splitlines():
        m = _NODE.match(line)
        if not m:
            continue
        name, typ, parent = m.group(1), m.group(2) or "(instance)", m.group(3)
        if parent is None:
            path = "."
        elif parent == ".":
            path = name
        else:
            path = parent + "/" + name
        out[path] = typ
    return out


def overlay_runtime(src_dir, work):
    """Copy a Lux checkout's runtime scripts over the package's (a patched runtime, measured on a shipped scene),
    with Level Factory's localize rewrite applied -- the package ships `res://addons/lux/` as
    `res://runtime/lux/` -- and only for scripts the package already carries. Returns the names copied."""
    dst_dir = os.path.join(work, "runtime", "lux", "runtime")
    done = []
    for name in sorted(os.listdir(src_dir)):
        if not name.endswith(".gd") or not os.path.isfile(os.path.join(dst_dir, name)):
            continue
        text = open(os.path.join(src_dir, name), encoding="utf-8").read().replace("res://addons/lux/",
                                                                                 "res://runtime/lux/")
        with open(os.path.join(dst_dir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        done.append(name)
    return done


def main(argv):
    runtime = None
    if "--runtime" in argv:
        i = argv.index("--runtime")
        runtime = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    pkg, work, out = argv[1], argv[2], argv[3]
    cycles = int(argv[4]) if len(argv) > 4 else 2
    scene = argv[5] if len(argv) > 5 else "res://presentation/lux.applied.tscn"
    rel = scene.replace("res://", "").replace("/", os.sep)
    if os.path.exists(work):
        shutil.rmtree(work)
    shutil.copytree(pkg, work, ignore=shutil.ignore_patterns(".godot"))
    os.makedirs(os.path.join(work, PLUGIN_DIR))
    shutil.copy2(os.path.join(HERE, "owner_probe_plugin.gd"), os.path.join(work, PLUGIN_DIR, "owner_probe_plugin.gd"))
    with open(os.path.join(work, PLUGIN_DIR, "plugin.cfg"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write('[plugin]\n\nname="lux_owner_probe"\ndescription="Roadmap 24: open, settle, save, quit."\n'
                 'author="factory"\nversion="1"\nscript="owner_probe_plugin.gd"\n')
    pg = os.path.join(work, "project.godot")
    text = open(pg, encoding="utf-8").read()
    assert "[editor_plugins]" not in text, "the package already enables an editor plugin"
    with open(pg, "a", encoding="utf-8", newline="\n") as fh:
        fh.write('\n[editor_plugins]\n\nenabled=PackedStringArray("res://addons/lux_owner_probe/plugin.cfg")\n')
    overlaid = overlay_runtime(runtime, work) if runtime else []
    if runtime:
        print("runtime overlaid from %s: %d script(s)" % (runtime, len(overlaid)))
    with open(os.path.join(work, "owner_probe.json"), "w", encoding="utf-8") as fh:
        json.dump({"scene": scene, "settle_frames": 120}, fh)
    shipped = open(os.path.join(pkg, rel), encoding="utf-8").read()
    base = nodes(shipped)
    runs = []
    prev_saved = shipped
    for c in range(1, cycles + 1):
        res = os.path.join(work, "owner_probe_result.json")
        if os.path.exists(res):
            os.remove(res)
        t0 = time.time()
        log = os.path.join(os.path.dirname(os.path.abspath(out)), "owner_probe_cycle%d.log" % c)
        with open(log, "w", encoding="utf-8", errors="replace") as lf:
            try:
                proc = subprocess.run([GODOT, "--headless", "--editor", "--path", work], stdout=lf,
                                      stderr=subprocess.STDOUT, timeout=1500)
                code = proc.returncode
            except subprocess.TimeoutExpired:
                code = None
        took = round(time.time() - t0, 1)
        result = json.load(open(res, encoding="utf-8")) if os.path.exists(res) else None
        saved = open(os.path.join(work, rel), encoding="utf-8").read()
        now = nodes(saved)
        added = sorted(p for p in now if p not in base)
        removed = sorted(p for p in base if p not in now)
        runs.append({"cycle": c, "editor_s": took, "exit": code, "result": result,
                     "saved_bytes": len(saved.encode("utf-8")), "shipped_bytes": len(shipped.encode("utf-8")),
                     "nodes_shipped": len(base), "nodes_saved": len(now),
                     "added": added[:80], "added_count": len(added), "removed": removed[:80],
                     "removed_count": len(removed),
                     "added_types": sorted({now[p] for p in added})})
        r = runs[-1]
        census = (result or {}).get("census") or {}
        print("cycle %d: editor %.1f s exit %s ok %s; nodes %d -> %d, +%d -%d (%s); held WorldEnvironment %s, "
              "DirectionalLight3D %s, CanvasLayer %s" % (
                  c, took, code, (result or {}).get("ok"), r["nodes_shipped"], r["nodes_saved"], r["added_count"],
                  r["removed_count"], ", ".join(r["added_types"]) or "-", census.get("world_environments"),
                  census.get("directional_lights"), census.get("canvas_layers")))
        for p in added[:12]:
            print("   + %s  (%s)" % (p, now[p]))
        # a second save is compared against the shipped scene AND the save before it: growth is the multiplication
        if c > 1:
            prev = nodes(prev_saved)
            grew = sorted(p for p in now if p not in prev)
            r["added_since_previous_save"] = grew[:80]
            print("   since the previous save: +%d" % len(grew))
        prev_saved = saved
    json.dump({"package": pkg, "scene": scene, "runtime_overlay": {"dir": runtime, "scripts": overlaid},
               "runs": runs}, open(out, "w", encoding="utf-8"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
