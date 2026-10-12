"""Can the light bake's lightmap requests ride the sidecar step's second import?

The export imports its package three times over: the sidecar step's first pass (no sidecars yet),
its second (sidecars rewritten, the cache dropped, everything imported again), and the light bake's,
which asks every model for a lightmap UV (`light_bake.mark_imports`) and imports again -- in cold
run 9248 that pass imported the shared textures 1,843 times for 476 models, and it is where the
pins race (docs/findings/texture_pins/).

The one-import plan was refuted (`import_plan_probe.py`): a model's FIRST import cannot borrow a
sibling's material. The worldskin `load()`s a building's floor module to skin its slabs, and on a
first import that module may not be imported yet -- cold run 9251's own import log: pass 1 left 105
slab meshes in the greybox material and took two reveals from roof modules; pass 2, sidecars
present and the cache dropped, skinned all 269 from floor modules. The second pass is not a first
import. So this runs the REAL export of a workspace's mission twice, in-process:

  A   as it is (the control: the same code as the run's own export)
  B   `mark_imports` applied to the sidecars once, just before the second pass (after the pins),
      with the spawned vehicles the bake would pass it

and prints, for each: the export's wall time, the sidecar step's, each light-bake `--import`'s;
the greybox census, the Empties' merge, the bake's imports and users, the occluders, the pins
read back after the last import, and the closure verdict, each from the export's own reports.
Then the three packages -- the run's own, A and B -- file by file (uids set aside): the control is
the run's against A, the change A against B. The workspace's own package is held aside and put
back. It measures and prints.

    python docs/findings/grader_speed/uv_second_pass_probe.py <workspace> <mission>
"""
import collections
import json
import os
import re
import runpy
import shutil
import sys
import time

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "level_factory"))
sys.path.insert(0, F)   # `level_factory` itself, for runpy
X = os.path.join(F, "_scratch", "uv_second_pass")
UID = re.compile(rb'uid="uid://[a-z0-9]+"|uid=uid://[a-z0-9]+')
TIMES = collections.defaultdict(list)


def timed(module, name, label):
    real = getattr(module, name)

    def wrapped(*a, **k):
        t = time.time()
        try:
            return real(*a, **k)
        finally:
            TIMES[label].append(round(time.time() - t, 1))
    setattr(module, name, wrapped)
    return real


def _compact(v):
    if isinstance(v, dict):
        return {k: (len(x) if isinstance(x, (list, dict)) else x) for k, x in v.items()}
    return len(v) if isinstance(v, list) else v


def reports(pkg):
    def j(n):
        p = os.path.join(pkg, n)
        return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
    g, m, lb, o, c = (j("greybox_skin_scan.json"), j("merge_empties.json"), j("light_bake.json"),
                      j("occluders.json"), j("export_closure_scan.json"))
    out = {}
    if g:
        out["greybox"] = {k: g.get(k) for k in ("greybox_surfaces", "greybox_area_m2", "slab_surfaces", "themed")}
    if m:
        rows = m.get("scenes") or []
        out["merge"] = {"scenes": len(rows), "meshes_in": sum(r["meshes_in"] for r in rows),
                        "surfaces_in": sum(r["surfaces_in"] for r in rows),
                        "merged": sum(r["merged"] for r in rows), "unwrapped": sum(r["unwrapped"] for r in rows),
                        "ok": m.get("ok")}
    if lb:
        out["bake"] = {"ok": lb.get("ok"), "users": (lb.get("result") or {}).get("users"),
                       "editor_s": lb.get("editor_s"),
                       "imports": {k: len(v) for k, v in (lb.get("imports") or {}).items()},
                       "primitives": _compact(lb.get("primitives"))}
    if o:
        out["occluders"] = {"occluders": o.get("occluders"), "ok": o.get("ok")}
    if c:
        out["closure"] = {k: c.get(k) for k in ("ok", "missing_resource_count")}
        out["closure"]["issues"] = len(c.get("issues") or [])
    return out


def run_arm(arm, ws, mission, exports):
    from packages.exporting import export, light_bake
    TIMES.clear()
    captured, pins = {}, {}
    real_export = export.export_mission

    def capture(*a, **k):
        captured["themed_site_dir"] = k.get("themed_site_dir")
        return real_export(*a, **k)
    export.export_mission = capture
    real_sidecars = timed(export, "_write_import_sidecars", "sidecar step")
    real_import = timed(light_bake, "_import", "light-bake --import")
    real_repin = export._repin_after_imports

    def repin(d):
        r = real_repin(d)
        pins.update(r if isinstance(r, dict) else {"result": r})
        return r
    export._repin_after_imports = repin
    real_sign = export._pin_sign_texture_imports
    if arm == "B":
        state = {"done": False}

        def sign_then_mark(export_dir):
            n = real_sign(export_dir)
            if state["done"]:
                return n
            state["done"] = True
            spawned = export.responder_vehicle_scenes(captured.get("themed_site_dir"))
            marks = light_bake.mark_imports(export_dir, spawned)
            print("[uv] B: marked before the second pass: %s"
                  % {k: len(v) for k, v in marks.items()}, flush=True)
            return n + len(marks["baked"]) + len(marks["spawned"])
        export._pin_sign_texture_imports = sign_then_mark
    sys.argv = ["level_factory", "-C", ws, "export", mission, "--mode", "portable-godot"]
    t = time.time()
    code = 0
    try:
        runpy.run_module("level_factory", run_name="__main__", alter_sys=True)
    except SystemExit as exc:
        code = exc.code
    wall = time.time() - t
    export.export_mission, export._write_import_sidecars = real_export, real_sidecars
    light_bake._import, export._repin_after_imports = real_import, real_repin
    export._pin_sign_texture_imports = real_sign
    pkg = os.path.join(exports, "LF_%s.portable-godot" % mission)
    print("[uv] %s: exit %s, the export %.1f s; %s" % (arm, code, wall, dict(TIMES)), flush=True)
    print("[uv] %s: pins after the last import %s" % (arm, {k: v for k, v in pins.items()
                                                           if not isinstance(v, (list, dict))}), flush=True)
    for k, v in reports(pkg).items():
        print("[uv] %s: %-9s %s" % (arm, k, v), flush=True)
    dst = os.path.join(X, arm)
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(dst)
    for n in os.listdir(exports):
        if n.startswith("LF_%s." % mission):
            shutil.move(os.path.join(exports, n), os.path.join(dst, n))
    return os.path.join(dst, "LF_%s.portable-godot" % mission)


def files(root):
    out = {}
    for r, ds, fs in os.walk(root):
        ds[:] = [d for d in ds if d != ".godot"]
        for f in fs:
            p = os.path.join(r, f)
            out[os.path.relpath(p, root).replace("\\", "/")] = p
    return out


def compare(a, b, label):
    fa, fb = files(a), files(b)
    same, uid_only, diff = 0, 0, collections.Counter()
    examples = collections.defaultdict(list)
    for k in sorted(set(fa) & set(fb)):
        x, y = open(fa[k], "rb").read(), open(fb[k], "rb").read()
        if x == y:
            same += 1
        elif UID.sub(b"", x) == UID.sub(b"", y):
            uid_only += 1
        else:
            ext = k.rsplit(".", 1)[-1] if "." in k else "-"
            diff[ext] += 1
            if len(examples[ext]) < 3:
                examples[ext].append(k)
    only = sorted(set(fa) ^ set(fb))
    print("[uv] %s: %d and %d files; identical %d; uids alone %d; different %d %s; on one side only %d %s"
          % (label, len(fa), len(fb), same, uid_only, sum(diff.values()), dict(diff), len(only), only[:4]),
          flush=True)
    for ext, ks in sorted(examples.items()):
        print("[uv]     %-8s e.g. %s" % (ext, ks), flush=True)


def main():
    ws, mission = os.path.abspath(sys.argv[1]), sys.argv[2]
    exports = os.path.join(ws, ".level_factory", "exports")
    if "--arm" in sys.argv:   # one arm, in its own process, the run's package already held aside
        run_arm(sys.argv[sys.argv.index("--arm") + 1], ws, mission, exports)
        return
    held_dir = os.path.join(X, "held")
    os.makedirs(held_dir, exist_ok=True)
    assert not os.listdir(held_dir), "a held package is already waiting in %s" % held_dir
    held = [n for n in os.listdir(exports) if n.startswith("LF_%s." % mission)]
    for n in held:
        shutil.move(os.path.join(exports, n), os.path.join(held_dir, n))
    print("[uv] held aside: %s" % held, flush=True)
    own = os.path.join(held_dir, "LF_%s.portable-godot" % mission)
    print("[uv] run:  the run's own package; %s" % reports(own), flush=True)
    try:
        for arm in ("A", "B"):   # each in its own process: the second inherits nothing of the first
            import subprocess
            subprocess.run([sys.executable, "-u", os.path.abspath(__file__), ws, mission, "--arm", arm],
                           check=False)
        a = os.path.join(X, "A", "LF_%s.portable-godot" % mission)
        b = os.path.join(X, "B", "LF_%s.portable-godot" % mission)
        compare(own, a, "control the run's own against A")
        compare(a, b, "change  A against B")
    finally:
        for n in os.listdir(exports):
            if n.startswith("LF_%s." % mission):
                shutil.rmtree(os.path.join(exports, n), ignore_errors=True) if os.path.isdir(
                    os.path.join(exports, n)) else os.remove(os.path.join(exports, n))
        for n in held:
            shutil.move(os.path.join(held_dir, n), os.path.join(exports, n))
        print("[uv] the run's package restored; A and B kept in %s until read" % X, flush=True)


if __name__ == "__main__":
    main()
