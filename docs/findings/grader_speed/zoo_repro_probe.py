"""Does a Zoo Blender build make the same bytes twice?

Runs one Zoo build -- a fixtures kit, by default cold run 9259's deli_a01 fixtures job's own
command -- N times into scratch folders, each in its own Blender process, against the Zoo at
`--zoo` (the repo, or a draft copy of it), and prints every output file's sha256 per run and
whether the runs agree. For a GLB that differs, it says which of each mesh's arrays differ and how
(the same bytes, the same rows in another order, or values apart). It measures and prints; it
names no cause.

    python docs/findings/grader_speed/zoo_repro_probe.py [--zoo <zoo root>] [--runs N] [--tag NAME]
        [--threads N] [--no-weighted-normals]

  --threads N              Blender started with `--threads N` (1: one thread for its parallel work)
  --no-weighted-normals    Zoo's own control for its area-weighted corner normals (1.87.0)
  --jobs <workspace>       instead: every Zoo job of a cold-run workspace (`--match`, default
                           "zoo_"), its own command from its job.log, replayed `--runs` times
                           against `--zoo`; every output but the .blend compared
"""
import hashlib
import json
import os
import shutil
import struct
import subprocess
import time
import sys

import numpy as np

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
X = os.path.join(F, "_scratch", "zoo_repro")
WS = os.path.join(F, "workspaces", "cold-9259-ws", ".level_factory", "jobs")


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def blender():
    return json.load(open(os.path.join(F, "factory.local.json"), encoding="utf-8"))["blender_executable"]


def glb(path):
    data = open(path, "rb").read()
    off, js, binc = 12, None, b""
    while off < len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        chunk = data[off + 8: off + 8 + clen]
        if ctype == 0x4E4F534A:
            js = json.loads(chunk)
        elif ctype == 0x004E4942:
            binc = chunk
        off += 8 + clen
    return js, binc


DT = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def arrays(path):
    js, binc = glb(path)
    out = {}
    for n in js.get("nodes", []):
        if "mesh" not in n:
            continue
        for pi, p in enumerate(js["meshes"][n["mesh"]]["primitives"]):
            items = dict(p["attributes"])
            if "indices" in p:
                items["indices"] = p["indices"]
            for k, ai in items.items():
                a = js["accessors"][ai]
                bv = js["bufferViews"][a["bufferView"]]
                start = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
                out[(n.get("name", "?"), pi, k)] = np.frombuffer(
                    binc, dtype=DT[a["componentType"]], count=a["count"] * NC[a["type"]],
                    offset=start).reshape(a["count"], NC[a["type"]])
    return out


def how(x, y):
    if x.shape != y.shape:
        return "shapes %s and %s" % (x.shape, y.shape)
    if np.array_equal(x, y):
        return None
    if np.array_equal(x[np.lexsort(x.T[::-1])], y[np.lexsort(y.T[::-1])]):
        return "the same rows in another order"
    d = np.abs(x.astype(np.float64) - y.astype(np.float64))
    return "values apart, max %.3g, %d of %d rows" % (d.max(), int((d.max(axis=1) > 0).sum()), len(x))


def replay_jobs(zoo, runs, tag):
    """Every Zoo job of a cold-run workspace (`--jobs <workspace>`), its own command from its
    job.log replayed `runs` times against `zoo`, each into a scratch folder; every output but the
    .blend compared by sha256."""
    import shlex
    ws_jobs = os.path.join(os.path.abspath(arg("--jobs", "")), ".level_factory", "jobs")
    match = arg("--match", "zoo_")
    names = sorted(n for n in os.listdir(ws_jobs) if match in n and os.path.isfile(os.path.join(ws_jobs, n, "1", "job.log")))
    same_jobs, differing = 0, []
    for name in names:
        first = open(os.path.join(ws_jobs, name, "1", "job.log"), encoding="utf-8", errors="replace").readline()
        assert first.startswith("$ "), (name, first[:80])
        cmd = shlex.split(first[2:].strip(), posix=False)
        assert "--out" in cmd and any(c.endswith("zoo_cli.py") for c in cmd), (name, cmd[:6])
        cmd = [os.path.join(zoo, "tools", "zoo_cli.py") if c.endswith("zoo_cli.py") else c for c in cmd]
        outs = []
        for i in range(runs):
            out = os.path.join(X, "%s_%s_%d" % (tag, name.split(".", 1)[-1], i))
            if os.path.isdir(out):
                shutil.rmtree(out)
            os.makedirs(out)
            c = list(cmd)
            c[c.index("--out") + 1] = out
            t0 = time.time()
            r = subprocess.run(c, cwd=zoo, capture_output=True, text=True, timeout=1800)
            took = time.time() - t0
            if r.returncode != 0:
                print("[zoo] %s run %d: exit %d" % (name, i, r.returncode), flush=True)
            print("[zoo] TIME %s run %d %.2f s" % (name, i, took), flush=True)
            outs.append(out)
        files = sorted({os.path.relpath(os.path.join(a, f), o) for o in outs
                        for a, _d, fs in os.walk(o) for f in fs if not f.endswith(".blend")})
        bad = []
        for rel in files:
            hs = set()
            for o in outs:
                p = os.path.join(o, rel)
                hs.add(hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.isfile(p) else "absent")
            if len(hs) > 1:
                bad.append(rel)
        if bad:
            differing.append((name, bad))
            print("[zoo] %-55s %d of %d files DIFFERENT: %s" % (name, len(bad), len(files), ", ".join(bad[:4])), flush=True)
            for rel in [b for b in bad if b.endswith(".glb")][:2]:
                a, b = arrays(os.path.join(outs[0], rel)), arrays(os.path.join(outs[1], rel))
                for key in sorted(set(a) | set(b))[:400]:
                    h = how(a[key], b[key]) if key in a and key in b else "only in one"
                    if h:
                        print("[zoo]       %s %s[%d] %s: %s" % (rel, key[0], key[1], key[2], h), flush=True)
        else:
            same_jobs += 1
            print("[zoo] %-55s the same, %d files" % (name, len(files)), flush=True)
        if "--keep" in sys.argv:
            print("[zoo]   kept in %s" % ", ".join(outs), flush=True)
            continue
        for o in outs:
            shutil.rmtree(o, ignore_errors=True)
    print("[zoo] %d of %d jobs the same in every run" % (same_jobs, len(names)), flush=True)


def main():
    zoo = os.path.abspath(arg("--zoo", os.path.join(F, "zoo")))
    if "--jobs" in sys.argv:
        return replay_jobs(zoo, int(arg("--runs", "2")), arg("--tag", "job"))
    runs = int(arg("--runs", "2"))
    tag = arg("--tag", "run")
    signs = os.path.join(WS, "restaurant_row_001.pixelcoat_build", "out", "signs", "sign_scrapple_sons_deli")
    kit = os.path.join(F, "deli_counter", "build", "deli_a01.lights.json")
    outs = []
    for i in range(runs):
        out = os.path.join(X, "%s_%d" % (tag, i))
        if os.path.isdir(out):
            shutil.rmtree(out)
        os.makedirs(out)
        cmd = [blender(), "--background"]
        if "--threads" in sys.argv:
            # Blender's own worker threads (its -t): 1 runs every parallel loop in one thread
            cmd += ["--threads", arg("--threads", "0")]
        cmd += ["--python", os.path.join(zoo, "tools", "zoo_cli.py"), "--",
                "--fixtures", kit, "--out", out, "--theme", "delco_1997", "--sign-pack", signs]
        if "--no-weighted-normals" in sys.argv:
            cmd.append("--no-weighted-normals")
        r = subprocess.run(cmd, cwd=zoo, capture_output=True, text=True, timeout=900)
        print("[zoo] %s run %d: exit %d" % (tag, i, r.returncode), flush=True)
        outs.append(out)
    files = sorted({os.path.relpath(os.path.join(a, f), o) for o in outs for a, _d, fs in os.walk(o) for f in fs})
    for rel in files:
        hs = []
        for o in outs:
            p = os.path.join(o, rel)
            hs.append(hashlib.sha256(open(p, "rb").read()).hexdigest()[:12] if os.path.isfile(p) else "absent")
        print("[zoo]   %-48s %s %s" % (rel, "the same" if len(set(hs)) == 1 else "DIFFERENT", " ".join(hs)), flush=True)
        if len(set(hs)) > 1 and rel.endswith(".glb"):
            a = arrays(os.path.join(outs[0], rel))
            for j in range(1, len(outs)):
                if hs[j] == hs[0]:
                    continue
                b = arrays(os.path.join(outs[j], rel))
                print("[zoo]     run 0 against run %d:" % j)
                for key in sorted(set(a) | set(b)):
                    if key not in a or key not in b:
                        print("[zoo]       %s only in one" % (key,))
                        continue
                    h = how(a[key], b[key])
                    if h:
                        print("[zoo]       %s[%d] %s: %s" % (key[0], key[1], key[2], h))
    if "--keep" not in sys.argv:
        for o in outs:
            shutil.rmtree(o, ignore_errors=True)
    else:
        print("[zoo] outputs kept in %s" % ", ".join(outs), flush=True)


if __name__ == "__main__":
    main()
