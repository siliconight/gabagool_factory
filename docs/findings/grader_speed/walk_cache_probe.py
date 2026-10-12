"""Can the walk copy start from the export's own import instead of importing the package again?

The cold drive's walk step (`tools/walk_export.py`) copies the package and imports it from scratch:
91 s of cold run 9252's 615 s drive, by its step stamps. The export imported the same files a
minute earlier and dropped the cache (`occluders.drop_cache`), because a package ships sidecars,
not a machine's cache. So this:

  1. re-exports a workspace's mission in-process with `drop_cache` MOVING the cache beside the
     package (`<package>.import_cache`) instead of deleting it -- the run's own package held
     aside and put back after;
  2. makes three walk copies of that package with the real `walk_export.py`:
       W0, W0b  as the drive does: copy, then a full `--import` (W0b is the control: two imports
                from scratch, to see what an import changes on its own)
       W1       copy, the kept cache copied in as `.godot`, then the same `--import`
  3. compares each copy's `.godot/imported/` file by file, and loads each copy's walk scene
     headless (`walk_copy_census.gd`): nodes, meshes, meshes with no mesh, lights.

It prints each step's wall time and the comparisons. It measures and prints.

    python docs/findings/grader_speed/walk_cache_probe.py <workspace> <mission>
"""
import collections
import hashlib
import os
import runpy
import shutil
import subprocess
import sys
import time

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "level_factory"))
sys.path.insert(0, F)
X = os.path.join(F, "_scratch", "walk_cache")
CENSUS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "walk_copy_census.gd")
GODOT = "C:/Godot/4.7/Godot_v4.7-stable_win64_console.exe"


def reexport(ws, mission, exports):
    """The export, its cache moved beside the package rather than deleted. Runs in its own
    process (`--reexport`): the export leaves module state behind."""
    from packages.exporting import occluders
    real = occluders.drop_cache

    def keep(export_dir):
        cache = os.path.join(str(export_dir), occluders.CACHE_DIR)
        kept = str(export_dir) + ".import_cache"
        if not os.path.isdir(cache):
            return False
        shutil.rmtree(kept, ignore_errors=True)
        shutil.move(cache, kept)
        print("[walk] the cache moved to %s" % kept, flush=True)
        return True
    occluders.drop_cache = keep
    sys.argv = ["level_factory", "-C", ws, "export", mission, "--mode", "portable-godot"]
    t = time.time()
    try:
        runpy.run_module("level_factory", run_name="__main__", alter_sys=True)
    except SystemExit as exc:
        print("[walk] export exit %s" % exc.code, flush=True)
    occluders.drop_cache = real
    print("[walk] the re-export %.1f s" % (time.time() - t), flush=True)


def walk_copy(ws, mission, out, cache=None):
    lf_dir = os.path.join(ws, ".level_factory")
    t = time.time()
    if cache is None:
        p = subprocess.run([sys.executable, os.path.join(F, "tools", "walk_export.py"), lf_dir, mission,
                            "--out", out, "--godot", GODOT], capture_output=True, text=True)
        wall = time.time() - t
        print("[walk] %s: walk_export.py as the drive runs it, exit %d, %.1f s"
              % (os.path.basename(out), p.returncode, wall), flush=True)
        return
    p = subprocess.run([sys.executable, os.path.join(F, "tools", "walk_export.py"), lf_dir, mission,
                        "--out", out, "--no-import"], capture_output=True, text=True)
    t1 = time.time()
    shutil.copytree(cache, os.path.join(out, ".godot"))
    t2 = time.time()
    q = subprocess.run([GODOT, "--headless", "--path", out, "--import"], capture_output=True, timeout=900)
    t3 = time.time()
    print("[walk] %s: walk_export.py --no-import exit %d %.1f s, the cache copied in %.1f s, "
          "--import exit %d %.1f s; %.1f s in all"
          % (os.path.basename(out), p.returncode, t1 - t, t2 - t1, q.returncode, t3 - t2, t3 - t), flush=True)


def imported(root):
    base = os.path.join(root, ".godot", "imported")
    out = {}
    for r, _, fs in os.walk(base):
        for f in fs:
            p = os.path.join(r, f)
            out[os.path.relpath(p, base).replace("\\", "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def compare(a, b, label):
    ia, ib = imported(a), imported(b)
    common = set(ia) & set(ib)
    diff = collections.Counter(k.rsplit(".", 1)[-1] for k in common if ia[k] != ib[k])
    only_a = collections.Counter(k.rsplit(".", 1)[-1] for k in set(ia) - set(ib))
    only_b = collections.Counter(k.rsplit(".", 1)[-1] for k in set(ib) - set(ia))
    print("[walk] %s: %d and %d imported files; identical %d; different %s; only in the first %s; "
          "only in the second %s" % (label, len(ia), len(ib), sum(1 for k in common if ia[k] == ib[k]),
                                     dict(diff), dict(only_a), dict(only_b)), flush=True)


def census(root):
    p = subprocess.run([GODOT, "--headless", "--path", root, "-s", CENSUS], capture_output=True,
                       text=True, timeout=600)
    line = [ln for ln in p.stdout.splitlines() if ln.startswith("WALK_COPY")]
    print("[walk] %s: %s" % (os.path.basename(root), line[-1] if line else "no census line, exit %d"
                             % p.returncode), flush=True)


def main():
    ws, mission = os.path.abspath(sys.argv[1]), sys.argv[2]
    exports = os.path.join(ws, ".level_factory", "exports")
    if "--reexport" in sys.argv:
        reexport(ws, mission, exports)
        return
    held_dir = os.path.join(X, "held")
    os.makedirs(held_dir, exist_ok=True)
    assert not os.listdir(held_dir), "a held package is already waiting in %s" % held_dir
    held = [n for n in os.listdir(exports) if n.startswith("LF_%s." % mission)]
    for n in held:
        shutil.move(os.path.join(exports, n), os.path.join(held_dir, n))
    print("[walk] held aside: %s" % held, flush=True)
    try:
        subprocess.run([sys.executable, "-u", os.path.abspath(__file__), ws, mission, "--reexport"],
                       check=False)
        pkg = os.path.join(exports, "LF_%s.portable-godot" % mission)
        cache = pkg + ".import_cache"
        assert os.path.isdir(pkg) and os.path.isdir(cache), (pkg, cache)
        w0, w0b, w1 = (os.path.join(X, n) for n in ("W0", "W0b", "W1"))
        walk_copy(ws, mission, w0)
        walk_copy(ws, mission, w0b)
        walk_copy(ws, mission, w1, cache=cache)
        compare(w0, w0b, "control W0 against W0b")
        compare(w0, w1, "change  W0 against W1 ")
        for w in (w0, w0b, w1):
            census(w)
    finally:
        for n in os.listdir(exports):
            if n.startswith("LF_%s." % mission):
                p = os.path.join(exports, n)
                shutil.rmtree(p, ignore_errors=True) if os.path.isdir(p) else os.remove(p)
        for n in held:
            shutil.move(os.path.join(held_dir, n), os.path.join(exports, n))
        print("[walk] the run's package restored; the walk copies kept in %s until read" % X, flush=True)


if __name__ == "__main__":
    main()
