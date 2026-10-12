"""In which phase of a real export do the shared textures lose their import pins?

`pin_step_probe.py` showed the sidecar step leaves all 415 sidecars under `_tex/` pinned, and one
more `--import` keeps them. The shipped package does not: 65 to 77 carry Godot's defaults. So this
runs the REAL export (`level_factory -C <ws> export <mission>`, in-process) with the phases after
the sidecar step wrapped -- the occluder bake, the Empties' merge, the light bake and each import
inside it, the greybox census, the cache drop -- and prints the pin census under `_tex/` before and
after each. The workspace's own package is moved aside first and put back after, so the run's
record is left as it was. It measures and prints.

    python docs/findings/texture_pins/pin_phase_probe.py <workspace> <mission>
"""
import collections
import os
import runpy
import shutil
import sys
import time

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "level_factory"))
sys.path.insert(0, F)   # `level_factory` itself, for runpy
X = os.path.join(F, "_scratch", "texture_pins", "held")


def census(root):
    c = collections.Counter()
    for r, _, fs in os.walk(root):
        if os.path.basename(r) != "_tex" or ".godot" in r.replace("\\", "/").split("/"):
            continue
        for f in fs:
            if f.endswith(".png.import"):
                text = open(os.path.join(r, f), encoding="utf-8", errors="replace").read()
                mip = "mipmaps/generate=true" in text
                fab = "process/fix_alpha_border=false" in text
                c["pinned" if (mip and fab) else "defaulted" if (not mip and not fab) else "mixed"] += 1
    return dict(c)


T0 = time.time()


def say(where, export_dir):
    print("[pins] %7.1f s  %-44s %s" % (time.time() - T0, where, census(export_dir)), flush=True)


def wrap(module, name, label, dir_arg=0):
    real = getattr(module, name)

    def wrapped(*a, **k):
        d = a[dir_arg] if len(a) > dir_arg else k.get("export_dir")
        say("before " + label, d)
        try:
            return real(*a, **k)
        finally:
            say("after  " + label, d)
    setattr(module, name, wrapped)


def main():
    ws, mission = os.path.abspath(sys.argv[1]), sys.argv[2]
    exports = os.path.join(ws, ".level_factory", "exports")
    held = [n for n in os.listdir(exports) if n.startswith("LF_%s." % mission)]
    os.makedirs(X, exist_ok=True)
    assert not os.listdir(X), "a held package is already waiting in %s" % X
    for n in held:
        shutil.move(os.path.join(exports, n), os.path.join(X, n))
    print("[pins] held aside: %s" % held, flush=True)
    try:
        from packages.exporting import export, greybox_skin, light_bake, merge_empties, occluders
        wrap(occluders, "emit", "the occluder bake")
        wrap(merge_empties, "merge", "the Empties' merge")
        wrap(light_bake, "bake", "the light bake")
        wrap(light_bake, "_import", "a light-bake --import")
        wrap(light_bake, "mark_imports", "mark_imports")
        wrap(greybox_skin, "measure", "the greybox census")
        wrap(occluders, "drop_cache", "the cache drop")
        sys.argv = ["level_factory", "-C", ws, "export", mission, "--mode", "portable-godot"]
        try:
            runpy.run_module("level_factory", run_name="__main__", alter_sys=True)
        except SystemExit as exc:
            print("[pins] export exit %s" % exc.code, flush=True)
        pkg = os.path.join(exports, "LF_%s.portable-godot" % mission)
        say("the shipped package", pkg)
    finally:
        out = os.path.join(F, "_scratch", "texture_pins", "probe_export")
        shutil.rmtree(out, ignore_errors=True)
        os.makedirs(out)
        for n in os.listdir(exports):
            if n.startswith("LF_%s." % mission):
                shutil.move(os.path.join(exports, n), os.path.join(out, n))
        for n in held:
            shutil.move(os.path.join(X, n), os.path.join(exports, n))
        print("[pins] the run's package restored; this export kept in %s" % out, flush=True)


if __name__ == "__main__":
    main()
