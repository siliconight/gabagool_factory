"""What does the Lux job's staging import cost, and does Lux need what it pays for?

Cold runs 9251 to 9253 wait about 26.7 s before the Lux job's command with nothing else running:
the scheduler stages a project of the whole themed site (`stage_godot_project`) and imports all of
it -- 480 models and 428 textures in 9253's -- before the job starts, because the driver
instantiates the scene. The staged project sets no importer defaults, so Godot compresses every
texture it detects in 3D and builds level-of-detail meshes for every model. Lux reads node
structure, material names and mesh bounds; neither is what it reads, and neither changes a
resource path in the scene it saves.

From a workspace's staged Lux project (`.level_factory/staging/<mission>.lux_apply`, cache set
aside) this makes copies and, for each, times a fresh `--import` and then the Lux job's own command
(read from the workspace index, its paths moved to the copy):

  S0, S0b  as staged (the control: two fresh imports and applies)
  S1       textures not compressed for 3D (`detect_3d/compress_to=0`)
  S2       that, and no level-of-detail meshes (`meshes/generate_lods=false`)

and compares what Lux writes -- `lux.applied.tscn` (node ids set aside), `lux.quality.json`,
`lux.validation.json` -- against S0. It measures and prints.

    python docs/findings/grader_speed/lux_staging_probe.py <workspace> <mission>
"""
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
X = os.path.join(F, "_scratch", "lux_staging")
GODOT = "C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"
DEFAULTS = {
    "S1": '[importer_defaults]\n\ntexture={\n"detect_3d/compress_to": 0\n}\n',
    "S2": ('[importer_defaults]\n\ntexture={\n"detect_3d/compress_to": 0\n}\n'
           'scene={\n"meshes/generate_lods": false\n}\n'),
}
OUTPUTS = ("lux.applied.tscn", "lux.quality.json", "lux.validation.json")
UNIQUE = re.compile(rb" unique_id=\d+")


def job_command(ws, mission):
    c = sqlite3.connect(os.path.join(ws, ".level_factory", "index.sqlite"))
    row = c.execute("select payload from jobs where job_id = ?", ("%s.lux_apply" % mission,)).fetchone()
    d = json.loads(row[0])
    return d["command"], d["working_directory"]


def stage(src, name):
    """Staged the way the job stages it: `stage_godot_project` over the scene the run's staging
    notes name, the staged addons, the driver beside them -- not a copy of the staged folder,
    which holds what its import extracted."""
    sys.path.insert(0, os.path.join(F, "level_factory"))
    from pathlib import Path
    from packages.staging.godot_project import stage_godot_project
    notes = json.load(open(os.path.join(src, "staging.notes.json"), encoding="utf-8"))
    dst = os.path.join(X, name)
    shutil.rmtree(dst, ignore_errors=True)
    addons = [Path(src, "addons", a) for a in sorted(os.listdir(os.path.join(src, "addons")))]
    addons.sort(key=lambda p: p.name != "lux")   # the adapter stages Lux's first
    stage_godot_project(Path(dst), addon_dirs=addons, scene_src=Path(notes["scene_source"]),
                        plugins=["lux"], godot_executable=None)
    shutil.copy2(os.path.join(src, "run_lux_apply.gd"), os.path.join(dst, "run_lux_apply.gd"))
    if name in DEFAULTS:
        pg = os.path.join(dst, "project.godot")
        text = open(pg, encoding="utf-8").read()
        open(pg, "w", encoding="utf-8", newline="\n").write(text.rstrip("\n") + "\n\n" + DEFAULTS[name])
    return dst


def run(name, project, cmd, old_project, old_out):
    t = time.time()
    p = subprocess.run([GODOT, "--headless", "--path", project, "--import"], capture_output=True, timeout=900)
    t_import = time.time() - t
    out = os.path.join(X, name + "_out")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    argv = [project if a == old_project else out if a == old_out else a for a in cmd[1:]]
    t = time.time()
    q = subprocess.run([GODOT] + argv, capture_output=True, timeout=900, cwd=project)
    t_apply = time.time() - t
    print("[lux] %-3s import exit %d %.1f s; apply exit %d %.1f s" % (name, p.returncode, t_import,
                                                                     q.returncode, t_apply), flush=True)
    return out


def same(a, b, label):
    rows = []
    for f in OUTPUTS:
        pa, pb = os.path.join(a, f), os.path.join(b, f)
        if not (os.path.exists(pa) and os.path.exists(pb)):
            rows.append("%s missing" % f)
            continue
        x, y = open(pa, "rb").read(), open(pb, "rb").read()
        if f.endswith(".tscn"):
            x, y = UNIQUE.sub(b"", x), UNIQUE.sub(b"", y)
        rows.append("%s %s" % (f, "same" if x == y else "DIFFERENT (%d and %d bytes)" % (len(x), len(y))))
    print("[lux] %s: %s" % (label, "; ".join(rows)), flush=True)


def main():
    ws, mission = os.path.abspath(sys.argv[1]), sys.argv[2]
    src = os.path.join(ws, ".level_factory", "staging", "%s.lux_apply" % mission)
    cmd, work = job_command(ws, mission)
    old_project = cmd[cmd.index("--path") + 1]
    old_out = cmd[cmd.index("--out") + 1]
    assert os.path.normcase(os.path.abspath(old_project)) == os.path.normcase(src), (old_project, src)
    os.makedirs(X, exist_ok=True)
    outs = {}
    for name in ("S0", "S0b", "S1", "S2"):
        outs[name] = run(name, stage(src, name), cmd, old_project, old_out)
    same(outs["S0"], outs["S0b"], "control S0 against S0b")
    for name in ("S1", "S2"):
        same(outs["S0"], outs[name], "change  S0 against %s " % name)
    print("[lux] copies kept in %s until read" % X, flush=True)


if __name__ == "__main__":
    main()
