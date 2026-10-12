"""Where does the light bake's editor spend its time?

The export's light bake opens the package's work copy in a Godot editor, which a plugin
(`level_factory/assets/godot/light_bake_plugin.gd`) drives: open the bake scene, press Bake
Lightmaps, save, quit. The run records the editor's whole time (`light_bake.json` `editor_s`, 96 s
in cold run 9255) and two of its parts in the editor's log -- the scene's opening (14.7 s since
0.190.0) and the bake (`bake_ms`, 35 s) -- and nothing of the rest. This re-exports a workspace's
mission in-process with the plugin swapped for a copy that prints `BAKE_T <step> <ms>` -- the
engine's own clock, from its start -- at each step, and prints the steps' times beside the
editor's whole time. The workspace's own package is held aside and put back. It measures and
prints; the plugin in Level Factory is not touched.

    python docs/findings/grader_speed/bake_phases_probe.py <workspace> <mission> [--arm NAME]
        [--scan] [--verbose] [--groups-cache <cfg>] [--no-groups-cache]

  --scan             every 30 frames while the plugin waits: the clock, and whether the editor's
                     file system is scanning
  --verbose          the editor run with Godot's --verbose
  --groups-cache     an editor's scene_groups_cache.cfg put in the work copy (0.190.0's question)
  --no-groups-cache  Level Factory 0.191.0's `write_scene_groups_cache` made a no-op: the control
                     arm, the bake as 0.190.0 ran it
  --arm NAME         names the kept editor log and the package digest (default "run")
  --open-floor N     the frames the plugin waits after asking for the scene before it looks
                     whether it opened (the plugin's own 240 replaced by N)
  --freeze-time      Engine.time_scale = 0 as the plugin starts: scripts that keep a clock from
                     their frame deltas keep it at 0 (the instrument that found it; 0.192.0's
                     plugin does it itself)
  --clock-runs       0.192.0's own `Engine.time_scale = 0.0` taken out: the clock runs, as it
                     did to 0.191.0

Since 0.191.0 it also times each of the bake's import passes, says what the bake wrote as the
scene groups cache and whether the cache kept beside the package still holds it, and compares the
package it made with the workspace's own, file by file (sha256), the bake's files by name. It
keeps the arm's lightmap as `bake.<arm>.exr` beside its log (and the workspace's as
`bake.ref.exr`), for `lightmap_compare.py`.
"""
import hashlib
import json
import os
import re
import runpy
import shutil
import sys
import time

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "level_factory"))
sys.path.insert(0, F)
X = os.path.join(F, "_scratch", "bake_phases")

#: (the line after which to print, the step's name) -- each line asserted present once.
STEPS = [
    ("\tset_process(true)\n", "the plugin entered the tree"),
    ('\t\t\tprint("BAKE asked to open the scene at frame ", _frames)\n', "the scene asked for"),
    ('\t\t\tprint("BAKE the scene opened after ", Time.get_ticks_msec() - _open_t0, " ms, frame ", _frames)\n',
     "the scene open"),
    ("\t\t\t_t0 = Time.get_ticks_msec()\n", "Bake pressed"),
    ("\t\t\tb.pressed.emit()\n", "the press returned"),
    ("\t\t\t_free_room_fill()\n", "the light data read"),
    ("\t\t\tEditorInterface.save_scene()\n", "the scene saved"),
]


def instrumented(src):
    out = src
    for line, step in STEPS:
        assert out.count(line) == 1, (step, out.count(line))
        indent = line[:len(line) - len(line.lstrip("\t"))]
        out = out.replace(line, line + '%sprint("BAKE_T %s ", Time.get_ticks_msec())\n' % (indent, step))
    done = "func _done(result: Dictionary) -> void:\n"
    assert out.count(done) == 1
    out = out.replace(done, done + '\tprint("BAKE_T quit asked ", Time.get_ticks_msec())\n')
    if "--freeze-time" in sys.argv:
        # the engine's clock stopped as the plugin starts: every script's `_process` delta is 0,
        # so a clock a script keeps from its deltas (Lux's failing fixtures' `_fail_t`) stays at 0
        start = "\tset_process(true)\n"
        assert out.count(start) == 1
        out = out.replace(start, start + "\tEngine.time_scale = 0.0\n\tprint(\"BAKE_FREEZE time_scale 0\")\n")
    if "--clock-runs" in sys.argv:
        # 0.192.0's plugin stops the engine's clock as it starts; this takes that line out
        stop = "\tEngine.time_scale = 0.0\n"
        assert out.count(stop) == 1, out.count(stop)
        out = out.replace(stop, "")
    if "--open-floor" in sys.argv:
        # the frames the plugin waits after asking for the scene before it looks whether the
        # scene opened (240 in 0.191.0's plugin, OPEN_FLOOR_FRAMES = 1 since 0.192.0)
        floor = int(sys.argv[sys.argv.index("--open-floor") + 1])
        lines = [ln for ln in ("\t\t\tif _frames < 240:\n", "\t\t\tif _frames < OPEN_FLOOR_FRAMES:\n")
                 if out.count(ln) == 1]
        assert len(lines) == 1, "the open's floor is not where this was written against"
        out = out.replace(lines[0], "\t\t\tif _frames < %d:\n" % floor)
    if "--scan" in sys.argv:
        # while the plugin waits to ask for the scene: every 30 frames, the clock, the frame, and
        # whether the editor's file system is scanning and how far along
        tick = "\t_frames += 1\n"
        assert out.count(tick) == 1
        out = out.replace(tick, tick + (
            '\tif _phase == 0 and _frames % 30 == 0:\n'
            '\t\tvar fs: EditorFileSystem = EditorInterface.get_resource_filesystem()\n'
            '\t\tprint("BAKE_SCAN ", Time.get_ticks_msec(), " frame ", _frames, " scanning ", '
            'fs.is_scanning(), " progress ", fs.get_scanning_progress())\n'))
    return out


def digest(root):
    """{relative path: sha256[:16]} of every file under `root`."""
    out = {}
    for r, _ds, fs in os.walk(root):
        for f in fs:
            p = os.path.join(r, f)
            h = hashlib.sha256()
            with open(p, "rb") as fh:
                for block in iter(lambda: fh.read(1 << 20), b""):
                    h.update(block)
            out[os.path.relpath(p, root).replace("\\", "/")] = h.hexdigest()[:16]
    return out


def compare(mine, theirs):
    """(same, {extension: differing count}, only in mine, only in theirs)."""
    same, differ = 0, {}
    for k in set(mine) & set(theirs):
        if mine[k] == theirs[k]:
            same += 1
        else:
            ext = os.path.splitext(k)[1] or k
            differ[ext] = differ.get(ext, 0) + 1
    return same, dict(sorted(differ.items())), sorted(set(mine) - set(theirs)), sorted(set(theirs) - set(mine))


def main():
    ws, mission = os.path.abspath(sys.argv[1]), sys.argv[2]
    arm = sys.argv[sys.argv.index("--arm") + 1] if "--arm" in sys.argv else "run"
    exports = os.path.join(ws, ".level_factory", "exports")
    from packages.exporting import light_bake
    os.makedirs(X, exist_ok=True)
    plugin = os.path.join(X, "light_bake_plugin.gd")
    with open(plugin, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(instrumented(open(str(light_bake.PLUGIN_SCRIPT), encoding="utf-8").read()))
    light_bake.PLUGIN_SCRIPT = type(light_bake.PLUGIN_SCRIPT)(plugin)
    if "--groups-cache" in sys.argv:
        # a scene groups cache an editor wrote, put in the work copy's .godot before its editor
        # starts -- does the editor still load every scene to read their groups?
        cache = sys.argv[sys.argv.index("--groups-cache") + 1]
        real_fp = light_bake._forward_plus

        def with_cache(project_godot):
            shutil.copy(cache, os.path.join(os.path.dirname(str(project_godot)), ".godot",
                                            "scene_groups_cache.cfg"))
            print("[bake] the work copy given %s" % cache, flush=True)
            return real_fp(project_godot)
        light_bake._forward_plus = with_cache
    written = {}
    if hasattr(light_bake, "write_scene_groups_cache"):
        real_write = light_bake.write_scene_groups_cache
        if "--no-groups-cache" in sys.argv:
            def no_cache(export_dir):
                print("[bake] the scene groups cache NOT written (the control arm)", flush=True)
                return 0
            light_bake.write_scene_groups_cache = no_cache
        else:
            def recorded(export_dir):
                n = real_write(export_dir)
                written["bytes"] = open(os.path.join(str(export_dir), light_bake.SCENE_GROUPS_CACHE),
                                        "rb").read()
                written["scenes"] = n
                return n
            light_bake.write_scene_groups_cache = recorded
    elif "--no-groups-cache" in sys.argv:
        sys.exit("--no-groups-cache: this Level Factory has no write_scene_groups_cache")
    imports = []
    real_import = light_bake._import

    def timed_import(export_dir, godot):
        t = time.time()
        ok = real_import(export_dir, godot)
        imports.append(round(time.time() - t, 1))
        return ok
    light_bake._import = timed_import
    if "--verbose" in sys.argv:
        # the editor run with Godot's --verbose, so its log says what it did before the scene
        real_run = light_bake._run

        def verbose_run(cmd, timeout, log_path=None):
            if "--editor" in cmd:
                cmd = list(cmd) + ["--verbose"]
            return real_run(cmd, timeout, log_path=log_path)
        light_bake._run = verbose_run
    held_dir = os.path.join(X, "held")
    os.makedirs(held_dir, exist_ok=True)
    assert not os.listdir(held_dir), "a held package is already waiting in %s" % held_dir
    held = [n for n in os.listdir(exports) if n.startswith("LF_%s." % mission)]
    for n in held:
        shutil.move(os.path.join(exports, n), os.path.join(held_dir, n))
    try:
        ref_pkg = os.path.join(held_dir, "LF_%s.portable-godot" % mission)
        ref = digest(ref_pkg) if os.path.isdir(ref_pkg) else {}
        sys.argv = ["level_factory", "-C", ws, "export", mission, "--mode", "portable-godot"]
        t0 = time.time()
        try:
            runpy.run_module("level_factory", run_name="__main__", alter_sys=True)
        except SystemExit as exc:
            print("[bake] export exit %s" % exc.code, flush=True)
        pkg = os.path.join(exports, "LF_%s.portable-godot" % mission)
        report = json.load(open(os.path.join(pkg, "light_bake.json"), encoding="utf-8"))
        log = open(pkg + ".lightbake.log", encoding="utf-8", errors="replace").read()
        steps = [(m.group(1), int(m.group(2))) for m in re.finditer(r"BAKE_T (.+?) (\d+)\s*$", log, re.M)]
        print("[bake] arm %s: the export %.1f s; the editor %s s in all (light_bake.json); bake_ms %s"
              % (arm, time.time() - t0, report.get("editor_s"), (report.get("result") or {}).get("bake_ms")),
              flush=True)
        last = 0
        for name, ms in steps:
            print("[bake]   %8.1f s  %-30s +%.1f s" % (ms / 1000.0, name, (ms - last) / 1000.0), flush=True)
            last = ms
        if steps:
            print("[bake]   after the last step to the editor's exit: %.1f s (the editor's whole time "
                  "less its clock at the last step)" % (float(report.get("editor_s") or 0) - last / 1000.0),
                  flush=True)
        for m in re.finditer(r"^BAKE_SCAN (\d+) frame (\d+) scanning (\w+) progress ([0-9.]+)", log, re.M):
            print("[bake]   scan  %7.1f s  frame %4s  scanning %-5s  progress %s"
                  % (int(m.group(1)) / 1000.0, m.group(2), m.group(3), m.group(4)), flush=True)
        print("[bake]   the bake's import passes: %s s (the UV2 pass, then the one after the bake)" % imports,
              flush=True)
        res = report.get("result") or {}
        print("[bake]   light_bake.json: ok %s, users %s, imports %s, primitives %s, rigs %s, room_fills %s, "
              "scene_groups_cached %s"
              % (report.get("ok"), res.get("users"),
                 {k: len(v) if isinstance(v, list) else v for k, v in (report.get("imports") or {}).items()},
                 sum((report.get("primitives") or {}).values()), report.get("rigs"), report.get("room_fills"),
                 report.get("scene_groups_cached")), flush=True)
        kept = pkg + ".import_cache"
        kept_cfg = os.path.join(kept, "scene_groups_cache.cfg")
        if written:
            now = open(kept_cfg, "rb").read() if os.path.isfile(kept_cfg) else None
            print("[bake]   the groups cache written: %d scene(s), %d bytes; in the cache kept beside the "
                  "package: %s" % (written["scenes"], len(written["bytes"]),
                                   "absent" if now is None else
                                   ("the same bytes" if now == written["bytes"] else "DIFFERENT, %d bytes" % len(now))),
                  flush=True)
        else:
            print("[bake]   the groups cache written: none; in the cache kept beside the package: %s"
                  % ("present" if os.path.isfile(kept_cfg) else "absent"), flush=True)
        mine = digest(pkg)
        with open(os.path.join(X, "digest.%s.json" % arm), "w", encoding="utf-8") as fh:
            json.dump(mine, fh, indent=0, sort_keys=True)
        if ref:
            same, differ, only_mine, only_ref = compare(mine, ref)
            print("[bake]   the package against the workspace's own: %d and %d files; the same %d; "
                  "differing %s; only in this %s; only in the workspace's %s"
                  % (len(mine), len(ref), same, differ, only_mine[:6], only_ref[:6]), flush=True)
            for f in light_bake.BAKE_FILES + (light_bake.REPORT, "mission.tscn"):
                print("[bake]     %-18s %s" % (f, "absent" if f not in mine or f not in ref else
                                                ("the same" if mine[f] == ref[f] else "different")), flush=True)
        # the lightmap itself, kept for lightmap_compare.py (the package goes when this ends); and
        # the bake's data beside it, so --layout can read where each user was put
        shutil.copy(os.path.join(pkg, "bake.exr"), os.path.join(X, "bake.%s.exr" % arm))
        keep_pkg = os.path.join(X, "pkg.%s" % arm)
        os.makedirs(keep_pkg, exist_ok=True)
        for f in ("bake.exr", "bake.exr.import", "bake.lmbake"):
            shutil.copy(os.path.join(pkg, f), os.path.join(keep_pkg, f))
        if os.path.isfile(os.path.join(ref_pkg, "bake.exr")) and not os.path.isfile(os.path.join(X, "bake.ref.exr")):
            shutil.copy(os.path.join(ref_pkg, "bake.exr"), os.path.join(X, "bake.ref.exr"))
        keep = os.path.join(X, "lightbake.%s.log" % arm)
        shutil.copy(pkg + ".lightbake.log", keep)
        print("[bake]   the editor's log kept at %s (%d lines)" % (keep, log.count("\n")), flush=True)
    finally:
        for n in os.listdir(exports):
            if n.startswith("LF_%s." % mission):
                p = os.path.join(exports, n)
                shutil.rmtree(p, ignore_errors=True) if os.path.isdir(p) else os.remove(p)
        for n in held:
            shutil.move(os.path.join(held_dir, n), os.path.join(exports, n))
        print("[bake] the run's package restored", flush=True)


if __name__ == "__main__":
    main()
