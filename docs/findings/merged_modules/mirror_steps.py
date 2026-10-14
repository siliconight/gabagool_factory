"""The steps `mirror.sh` runs on its two copies of a package (roadmap 249). Each prints what it measured and stops.

    python mirror_steps.py drop <package> <out.json>          Level Factory's drop_merged_modules, with the
                                                              package's own merge_empties.json
    python mirror_steps.py closure <a> <b>                    Level Factory's closure scan of each
    python mirror_steps.py import <godot> <a> <b>             a first `--import` of each, timed, one run each
    python mirror_steps.py frames <a frames> <a2 frames> <b frames>
                                                              pixels differing by more than 24 levels: a against
                                                              a shot again (the control) and a against b
"""
import json
import subprocess
import sys
import time
from pathlib import Path

F = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(F / "level_factory"))
THRESHOLD = 24


def drop(pkg, out):
    from packages.exporting.merge_empties import drop_merged_modules
    pkg = Path(pkg)
    report = json.loads((pkg / "merge_empties.json").read_text(encoding="utf-8"))
    got = drop_merged_modules(pkg, report)
    Path(out).write_text(json.dumps(got, indent=1), encoding="utf-8")
    print("dropped %d module(s), %d bytes with their sidecars; %d named and kept"
          % (len(got["dropped"]), got["bytes"], got["kept"]))


def closure(a, b):
    from packages.exporting.closure import scan_closure
    for name, root in (("a, as shipped", a), ("b, dropped", b)):
        r = scan_closure(Path(root))
        print("%-14s resources %d  missing %d  misrooted %d  relative %d  absolute %d  external %d  issues %d"
              % (name, r.resource_count, r.missing_resource_count, r.misrooted_resource_count,
                 r.relative_reference_count, r.absolute_path_count, r.external_reference_count, len(r.issues)))
        for i in r.issues[:12]:
            print("    " + i)


def import_(godot, a, b):
    for name, root in (("a, as shipped", a), ("b, dropped", b)):
        models = sum(1 for _ in Path(root).rglob("*.glb.import"))
        t = time.perf_counter()
        p = subprocess.run([godot, "--headless", "--path", root, "--import"], capture_output=True, text=True,
                           timeout=1800, stdin=subprocess.DEVNULL)
        print("%-14s %4d model imports  first --import %.1f s  exit %d"
              % (name, models, time.perf_counter() - t, p.returncode))
    print("one run each, a then b: a measurement, not a price")


def frames(a, a2, b):
    import numpy as np
    from PIL import Image, ImageChops
    a, a2, b = Path(a), Path(a2), Path(b)
    names = sorted(p.name for p in a.glob("*.png"))
    for d in (a2, b):
        if not names or sorted(p.name for p in d.glob("*.png")) != names:
            raise SystemExit("UNKNOWN SHAPE: the copies shot different frames")

    def diff(x, y, n):
        d = np.asarray(ImageChops.difference(Image.open(x / n).convert("RGB"), Image.open(y / n).convert("RGB")))
        m = d.max(axis=2)
        return int((m > THRESHOLD).sum()), int(m.max()), m.size

    print("pixels differing by more than %d levels of 255, and the largest difference" % THRESHOLD)
    print("%-30s %24s %24s" % ("frame", "a vs a again (control)", "a vs b (dropped)"))
    tc = ts = tp = 0
    for n in names:
        c, cm, size = diff(a, a2, n)
        s, sm, _ = diff(a, b, n)
        tc += c
        ts += s
        tp += size
        print("%-30s %16d (%3d) %17d (%3d)" % (n, c, cm, s, sm))
    print("%-30s %16d       %17d        of %d pixels" % ("all %d frames" % len(names), tc, ts, tp))


if __name__ == "__main__":
    step, args = sys.argv[1], sys.argv[2:]
    {"drop": drop, "closure": closure, "import": import_, "frames": frames}[step](*args)
