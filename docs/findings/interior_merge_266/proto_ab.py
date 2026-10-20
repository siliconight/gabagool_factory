"""Roadmap 266's prototype, end to end on copies: a package re-baked as it is (the control) and re-baked after its
enterable buildings' static modules are merged per unit and material (`merge_buildings_proto.gd`).

    python docs/findings/interior_merge_266/proto_ab.py <package> <out dir> [--ids a,b,c] [--arm control|merged]

Both arms go through the same steps, so what differs between them is the merge and nothing else:
  1. copy the package and un-bake the copy (`tools/lux_rebake.unbake`: its bake files go and its entry points back
     at the presentation scene);
  2. import it headless;
  3. MERGED ARM ONLY: `merge_buildings_proto.gd` over `res://lot/<id>/site.tscn` for each enterable building --
     every `lot/<id>` that is not an Empty (`gs_empty_*`, `gs_midrise_*`, `gs_cornershop_*`, `gs_facade_*`), or the
     `--ids` given;
  4. bake with Level Factory's own `light_bake.bake()`, passing the shipped bake's `spawned` set, exactly as
     `tools/lux_rebake.py` does.
It writes `<out>/control` and `<out>/merged` and each arm's reports beside them; pricing them is
`_runs/perf_inner/run.py`'s, run on each. It prints what it did and stops.
"""
import json
import os
import shutil
import subprocess
import sys

F = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(F, "tools"))
import lux_rebake  # noqa: E402

GODOT = json.load(open(os.path.join(F, "factory.local.json"), encoding="utf-8"))["godot_executable"]
HERE = os.path.dirname(os.path.abspath(__file__))
EMPTY_PREFIXES = ("gs_empty_", "gs_midrise_", "gs_cornershop_", "gs_facade_")


def arm(src, dest, merge_ids=None):
    lb = lux_rebake._light_bake()
    spawned = []
    shipped = os.path.join(src, lb.REPORT)
    if os.path.isfile(shipped):
        spawned = list((json.load(open(shipped, encoding="utf-8")).get("imports") or {}).get("spawned") or [])
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    shutil.rmtree(os.path.join(dest, ".godot"), ignore_errors=True)
    lux_rebake.unbake(dest)
    r = subprocess.run([GODOT, "--headless", "--path", dest, "--import"], capture_output=True, text=True,
                       timeout=1800)
    print("[proto_ab] %s: import exit %d" % (os.path.basename(dest), r.returncode), flush=True)
    if merge_ids:
        # each building's own rooms beside its scene, in Deli Counter's frame, for the merge's units (v2)
        for i in merge_ids:
            g = json.load(open(os.path.join(F, "deli_counter", "build", i + ".gameplay.json"), encoding="utf-8"))
            spec = json.load(open(os.path.join(F, "deli_counter", "specs", i + ".json"), encoding="utf-8"))
            rooms = {"story_height": float(spec.get("story_height") or 3.5),
                     "rooms": [{"id": r["id"], "story": r["story"], "bounds": r["bounds"]} for r in g["rooms"]]}
            json.dump(rooms, open(os.path.join(dest, "lot", i, "rooms.json"), "w", encoding="utf-8"), indent=1)
        shutil.copy(os.path.join(HERE, "merge_buildings_proto.gd"), dest)
        # ABSOLUTE: Godot resolves a bare relative path under res://, and the first run's report went nowhere
        report = os.path.abspath(os.path.join(dest, "merge_buildings_proto.json"))
        scenes = ["res://lot/%s/site.tscn" % i for i in merge_ids]
        r = subprocess.run([GODOT, "--headless", "--path", dest, "--script", "res://merge_buildings_proto.gd", "--",
                            report] + scenes, capture_output=True, text=True, timeout=1800)
        open(dest + ".merge.log", "w", encoding="utf-8").write(r.stdout + r.stderr)
        rep = json.load(open(report, encoding="utf-8"))
        if rep.get("schema") != "lf.merge_buildings_proto.v1" or not rep.get("ok"):
            raise SystemExit("MERGE FAILED: %s" % rep.get("error"))
        for row in rep["scenes"]:
            print("[proto_ab] merged %s: %d slots, %d surfaces -> %d meshes, %d colliders kept"
                  % (row["scene"], row["slots_merged"], row["surfaces_in"], row["merged"], row["colliders"]),
                  flush=True)
        os.remove(os.path.join(dest, "merge_buildings_proto.gd"))
    report = lb.bake(dest, GODOT, log=lambda m: None, spawned=spawned)
    json.dump(report, open(dest + ".bake.json", "w", encoding="utf-8"), indent=1, default=str)
    print("[proto_ab] %s: baked, ok=%s" % (os.path.basename(dest), report.get("ok")), flush=True)


def main(argv):
    src, out = argv[0], argv[1]
    ids = None
    if "--ids" in argv:
        ids = argv[argv.index("--ids") + 1].split(",")
    else:
        ids = sorted(d for d in os.listdir(os.path.join(src, "lot"))
                     if os.path.isdir(os.path.join(src, "lot", d)) and not d.startswith(EMPTY_PREFIXES))
    print("[proto_ab] enterable buildings to merge:", ids, flush=True)
    os.makedirs(out, exist_ok=True)
    only = argv[argv.index("--arm") + 1] if "--arm" in argv else None
    if only in (None, "control"):
        arm(src, os.path.join(out, "control"))
    if only in (None, "merged"):
        arm(src, os.path.join(out, "merged"), merge_ids=ids)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
