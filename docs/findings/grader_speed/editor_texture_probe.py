"""What does a Godot editor change in a package's texture sidecars when it opens the level?

The bake's editor log says it re-encodes the textures it detects in use: 426 "used in 3D" (mipmaps
on, VRAM compression), 22 "used as a normal map" (red-green compression), 22 "used as a roughness
map" (a roughness limiter tied to a normal map). A headless import detects nothing -- the dummy
renderer draws nothing to detect with -- so the package's own sidecars keep Godot's defaults and
every editor that opens it changes them. To pin what an editor would decide, read what one did:
this re-exports a workspace's mission in-process with the light bake's work copy -- the project
its editor opened -- moved aside instead of deleted, then compares every texture sidecar in it with
the shipped package's, key by key, and counts each change by its before and after. The
workspace's own package is held aside and put back. It measures and prints.

    python docs/findings/grader_speed/editor_texture_probe.py <workspace> <mission>
"""
import collections
import os
import re
import runpy
import shutil
import sys

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "level_factory"))
sys.path.insert(0, F)
X = os.path.join(F, "_scratch", "editor_texture")


def params(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    if "[params]" not in text:
        return {}
    return dict(re.findall(r"^([^=\n]+)=(.*)$", text[text.index("[params]"):], re.M))


def main():
    ws, mission = os.path.abspath(sys.argv[1]), sys.argv[2]
    exports = os.path.join(ws, ".level_factory", "exports")
    held_dir = os.path.join(X, "held")
    os.makedirs(held_dir, exist_ok=True)
    assert not os.listdir(held_dir), "a held package is already waiting in %s" % held_dir
    held = [n for n in os.listdir(exports) if n.startswith("LF_%s." % mission)]
    for n in held:
        shutil.move(os.path.join(exports, n), os.path.join(held_dir, n))
    kept_work = os.path.join(X, "work")
    shutil.rmtree(kept_work, ignore_errors=True)
    real_rmtree = shutil.rmtree

    def keep_the_work_copy(path, *a, **k):
        if str(path).endswith(".lightbake") and k.get("ignore_errors"):
            shutil.move(str(path), kept_work)   # the bake's last word on its work copy
            return None
        return real_rmtree(path, *a, **k)
    try:
        shutil.rmtree = keep_the_work_copy
        sys.argv = ["level_factory", "-C", ws, "export", mission, "--mode", "portable-godot"]
        import time
        t0 = time.time()
        try:
            runpy.run_module("level_factory", run_name="__main__", alter_sys=True)
        except SystemExit as exc:
            print("[editor] export exit %s" % exc.code, flush=True)
        shutil.rmtree = real_rmtree
        pkg = os.path.join(exports, "LF_%s.portable-godot" % mission)
        log = open(pkg + ".lightbake.log", encoding="utf-8", errors="replace").read()
        opened = re.search(r"BAKE the scene opened after (\d+) ms", log)
        print("[editor] the export %.1f s; its editor opened the scene after %s ms and logged %d "
              "texture(s) detected as used in 3D, %d as a normal map, %d as a roughness map"
              % (time.time() - t0, opened.group(1) if opened else "?",
                 log.count("detected as used in 3D"), log.count("detected as used as a normal map"),
                 log.count("detected as used as a roughness map")), flush=True)
        assert os.path.isdir(kept_work), "the bake's work copy was not kept"
        changes, kinds, examples = collections.Counter(), collections.Counter(), {}
        same = differ = 0
        for r, ds, fs in os.walk(kept_work):
            ds[:] = [d for d in ds if d != ".godot"]
            for f in fs:
                if not f.endswith(".png.import"):
                    continue
                w = os.path.join(r, f)
                rel = os.path.relpath(w, kept_work)
                p = os.path.join(pkg, rel)
                if not os.path.exists(p):
                    continue
                a, b = params(p), params(w)
                moved = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
                if not moved:
                    same += 1
                    continue
                differ += 1
                kind = []
                for k in moved:
                    va = a.get(k)
                    vb = b.get(k)
                    if k == "roughness/src_normal":
                        vb = "<a normal map>" if vb and vb != '""' else vb
                    changes["%s: %s -> %s" % (k, va, vb)] += 1
                    kind.append(k)
                place = rel.replace("\\", "/").split("/")
                where = "_tex" if "_tex" in place else place[0]
                kinds["%s | %s" % (where, ", ".join(kind))] += 1
                examples.setdefault(", ".join(kind), rel.replace("\\", "/"))
        print("[editor] texture sidecars the editor left as the package ships them %d, changed %d"
              % (same, differ), flush=True)
        for k, n in sorted(changes.items(), key=lambda kv: -kv[1]):
            print("[editor]   %4d  %s" % (n, k), flush=True)
        for k, n in sorted(kinds.items(), key=lambda kv: -kv[1]):
            print("[editor]   %4d  where | keys moved: %s" % (n, k), flush=True)
        for k, rel in examples.items():
            print("[editor]   e.g. %s  <- %s" % (rel, k), flush=True)
    finally:
        shutil.rmtree = real_rmtree
        for n in os.listdir(exports):
            if n.startswith("LF_%s." % mission):
                p = os.path.join(exports, n)
                shutil.rmtree(p, ignore_errors=True) if os.path.isdir(p) else os.remove(p)
        for n in held:
            shutil.move(os.path.join(held_dir, n), os.path.join(exports, n))
        print("[editor] the run's package restored; the work copy kept in %s until read" % kept_work, flush=True)


if __name__ == "__main__":
    main()
