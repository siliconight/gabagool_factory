"""The two sets of rowhome shells the stoop breadth swaps in: the same Deli Counter, with and without stoops.

    python docs/findings/stoop_breadth/build_flat.py

`flat`: the twelve rowhome Empties as Deli Counter builds them today with `stoop=0` -- `presets.empty_rowhome`
with the stoop asked for none, which leaves the door at grade, no stoop and no railings. Built by Deli
Counter's own `build.py` from specs written here, into `_scratch/stoop_breadth/flat/`.

`stoop`: the twelve as Deli Counter 0.212.0 built them (`deli_counter/build/`), copied into
`_scratch/stoop_breadth/stoop/` so the breadth reads one fixed set for its whole run.

So the two sets differ in the stoop and its railings and in nothing a later Deli Counter changed. Prints,
for every shell of both sets, its sha256 (16), its size, and how many of its glTF nodes are named `stoop`
-- `stoop_rail` counted apart -- and how many are colliders (`-colonly` / `-convcolonly`). Prints what it
measured and stops; `build_flat.out.txt` is its output.
"""
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

F = pathlib.Path(__file__).resolve().parents[3]
DC = F / "deli_counter"
BLENDER = "C:/blender/blender.exe"
SCR = F / "_scratch" / "stoop_breadth"

sys.path.insert(0, str(DC))
import presets  # noqa: E402


def nodes(glb):
    from pygltflib import GLTF2
    g = GLTF2().load(str(glb))
    names = [n.name or "" for n in g.nodes]
    return {"nodes": len(names),
            "stoop": sum(1 for n in names if n.startswith("stoop") and not n.startswith("stoop_rail")),
            "stoop_rail": sum(1 for n in names if n.startswith("stoop_rail")),
            "colliders": sum(1 for n in names if n.endswith("colonly"))}


def describe(path):
    raw = path.read_bytes()
    d = nodes(path)
    return "%-24s sha %s  %8d bytes  nodes %3d  stoop %d  stoop_rail %d  colliders %3d" % (
        path.name, hashlib.sha256(raw).hexdigest()[:16], len(raw), d["nodes"], d["stoop"], d["stoop_rail"],
        d["colliders"])


def main():
    names = sorted(presets.EMPTY_ROWHOMES)
    if len(names) != 12:
        sys.exit("UNKNOWN SHAPE: %d rowhomes in presets.EMPTY_ROWHOMES" % len(names))
    if SCR.exists():
        shutil.rmtree(SCR)
    (SCR / "specs").mkdir(parents=True)
    (SCR / "flat").mkdir()
    (SCR / "stoop").mkdir()
    for n in names:
        spec = presets.empty_rowhome(name=n, **dict(presets.EMPTY_ROWHOMES[n], stoop=0))
        if "stoop" in spec:
            sys.exit("UNKNOWN SHAPE: %s at stoop=0 still asks for a stoop" % n)
        sp = SCR / "specs" / (n + ".json")
        sp.write_text(json.dumps(spec, indent=2), encoding="utf-8")
        r = subprocess.run([sys.executable, str(DC / "build.py"), str(sp), "--out", str(SCR / "flat" / (n + ".glb")),
                            "--blender", BLENDER], cwd=str(DC), capture_output=True, text=True,
                           stdin=subprocess.DEVNULL)
        (SCR / "flat" / (n + ".build.log")).write_text(r.stdout + r.stderr, encoding="utf-8")
        if r.returncode != 0 or not (SCR / "flat" / (n + ".glb")).exists():
            sys.exit("BUILD FAILED: %s (exit %d), see %s" % (n, r.returncode, SCR / "flat" / (n + ".build.log")))
        shutil.copy2(DC / "build" / (n + ".glb"), SCR / "stoop" / (n + ".glb"))
    dc_version = (DC / "VERSION").read_text(encoding="utf-8").strip()
    print("Deli Counter: %s; flat = presets.empty_rowhome(stoop=0) built by build.py, stoop = deli_counter/build/"
          % dc_version)
    for arm in ("flat", "stoop"):
        print(arm)
        for n in names:
            print("   " + describe(SCR / arm / (n + ".glb")))


if __name__ == "__main__":
    main()
