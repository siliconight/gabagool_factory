"""What do the light bake's two imports spend their time on?

Profiled (`README.md`, the export section): the bake's two `--import`s took 112 s of a 430.7 s
export -- 55.6 s and 50.3 s in the pin census run (`docs/findings/texture_pins/`). The first
re-imports every model `mark_imports` moved to static lightmaps (their lightmap UVs), and its
engine log showed it importing the shared textures 1,843 times for 476 models. The second runs
after the editor's bake has copied its files back. This re-runs the real export in-process on a
workspace (its own package held aside and put back), with `light_bake._import` replaced by the same
command plus `--verbose`, each call's log kept, and prints per call: the wall time and how many
files of each kind the engine imported. It measures and prints.

    python docs/findings/grader_speed/bake_imports_probe.py <workspace> <mission>
"""
import collections
import os
import re
import runpy
import shutil
import subprocess
import sys
import time

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "level_factory"))
sys.path.insert(0, F)
X = os.path.join(F, "_scratch", "bake_imports")
HELD = os.path.join(X, "held")


def main():
    ws, mission = os.path.abspath(sys.argv[1]), sys.argv[2]
    exports = os.path.join(ws, ".level_factory", "exports")
    shutil.rmtree(X, ignore_errors=True)
    os.makedirs(HELD)
    held = [n for n in os.listdir(exports) if n.startswith("LF_%s." % mission)]
    for n in held:
        shutil.move(os.path.join(exports, n), os.path.join(HELD, n))
    print("held aside: %s" % held, flush=True)
    calls = []
    try:
        from packages.exporting import light_bake

        def _import(export_dir, godot):
            n = len(calls) + 1
            t0 = time.time()
            done = subprocess.run([str(godot), "--headless", "--verbose", "--path", str(export_dir), "--import"],
                                  capture_output=True, timeout=light_bake.IMPORT_TIMEOUT_S)
            wall = time.time() - t0
            out = (done.stdout or b"") + (done.stderr or b"")
            log = os.path.join(X, "bake_import_%d.log" % n)
            open(log, "wb").write(out)
            kinds = collections.Counter(
                os.path.splitext(m.decode("utf-8", "replace"))[1].lower()
                for m in re.findall(rb"Importing file: res://(\S+)", out))
            distinct = len(set(re.findall(rb"Importing file: res://(\S+)", out)))
            calls.append((n, wall, dict(kinds), distinct))
            print("bake import %d: %.1f s, exit %s; imports by kind %s; %d distinct files; log %s"
                  % (n, wall, done.returncode, dict(kinds.most_common()), distinct, log), flush=True)
            return True

        light_bake._import = _import
        sys.argv = ["level_factory", "-C", ws, "export", mission, "--mode", "portable-godot"]
        t0 = time.time()
        try:
            runpy.run_module("level_factory", run_name="__main__", alter_sys=True)
        except SystemExit as exc:
            print("export exit %s" % exc.code, flush=True)
        print("export %.1f s (the imports verbose, so slower than a plain run)" % (time.time() - t0), flush=True)
    finally:
        out = os.path.join(X, "probe_export")
        os.makedirs(out, exist_ok=True)
        for n in os.listdir(exports):
            if n.startswith("LF_%s." % mission):
                shutil.move(os.path.join(exports, n), os.path.join(out, n))
        for n in held:
            shutil.move(os.path.join(HELD, n), os.path.join(exports, n))
        print("the run's package restored; this export kept in %s" % out, flush=True)


if __name__ == "__main__":
    main()
