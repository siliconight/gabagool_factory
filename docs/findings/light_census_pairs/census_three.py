"""The bake-aware light census on a real package: shipped, shipped again, and live.

    python census_three.py --lf <level_factory root> [--run] [--compare]

THE QUESTION. Level Factory 0.159.0's census carries two counts per mesh: BY
REACH (every positional light whose range reaches the mesh's box) and PAIRED
(of those, what Godot 4.7's culler binds: no light masked off the mesh's
layers, no hidden light, no BAKE_STATIC light on a mesh that has a
lightmap). On a real package:
- **the control:** two copies of one package must read the same in every
  field, or the instrument has noise of its own;
- **the dial:** a copy with the club's two stage rigs switched live
  (`docs/findings/club_stage_live_price/make_live_copy.py`, `bake_mode` 1 to
  0) must move PAIRED -- the stage meshes gain the live lamps -- and must not
  move BY REACH, which never read the bake mode.

HOW (`--run`). Each copy is made the way `_runs/perf_inner/run.py` makes a
price copy:
- the package copied fresh to `_runs/perf_inner/census_<tag>`, and its
  `.godot` removed;
- imported headless;
- walked by `<lf>/tools/perf_stations_run.py` -- the runner copies its own
  sibling `perf_stations.gd` in, so `--lf` names the census that runs;
- the report written beside this file as `census_<tag>.json`;
- the copy deleted once the report exists.

The windowed harness opens a Godot window for a few minutes a copy, as every
price does.

THE COMPARISON (`--compare`). Prints each report's two counts -- over the
cap, worst, pairs, histogram -- and the differences: control against
control, and live against shipped. Prints what it measured and stops; a
report without the fields it reads FAILS.

The subject is cold run 9204's club_block_014 package, the one
`club_stage_live_price` priced.
"""
import argparse
import json
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PKG = (ROOT / "workspaces" / "cold-9204-ws" / ".level_factory" / "exports"
       / "LF_club_block_014.portable-godot")
LIVE = ROOT / "docs" / "findings" / "club_stage_live_price" / "make_live_copy.py"
INNER = ROOT / "_runs" / "perf_inner"
GODOT = r"C:\Godot\4.7\Godot_v4.7-stable_win64_console.exe"
TAGS = ("shipped", "shipped2", "live")


def run(lf):
    runner = lf / "tools" / "perf_stations_run.py"
    if not runner.is_file():
        raise SystemExit(f"no runner at {runner}")
    for tag in TAGS:
        dst = INNER / f"census_{tag}"
        if dst.exists():
            shutil.rmtree(dst)
        if tag == "live":
            subprocess.run([sys.executable, str(LIVE), str(PKG), str(dst)], check=True)
        else:
            shutil.copytree(PKG, dst)
        shutil.rmtree(dst / ".godot", ignore_errors=True)
        r = subprocess.run([GODOT, "--headless", "--path", str(dst), "--import"],
                           capture_output=True, text=True, timeout=1200)
        print(f"{tag}: import {r.returncode}", flush=True)
        out = HERE / f"census_{tag}.json"
        r = subprocess.run([sys.executable, str(runner), str(dst), "--json", str(out)],
                           capture_output=True, text=True, timeout=3600, cwd=str(lf))
        (HERE / f"census_{tag}.log").write_text(r.stdout + r.stderr, encoding="utf-8")
        print(f"{tag}: perf {r.returncode}, report {'written' if out.is_file() else 'MISSING'}",
              flush=True)
        if out.is_file():
            shutil.rmtree(dst)


def census(tag):
    d = json.loads((HERE / f"census_{tag}.json").read_text(encoding="utf-8"))
    c = (d.get("rows") or [{}])[0].get("light_census")
    if not isinstance(c, dict) or not isinstance(c.get("paired"), dict):
        raise SystemExit(f"census_{tag}.json: no light_census with a paired count")
    for block in (c, c["paired"]):
        for k in ("over_cap", "worst", "worst_mesh", "pairs", "histogram"):
            if k not in block:
                raise SystemExit(f"census_{tag}.json: a census block without {k!r}")
    return c


def line(name, b):
    return (f"  {name:9s} over the cap {b['over_cap']:3d}   worst {b['worst']:3d} "
            f"({b['worst_mesh']})   pairs {b['pairs']}")


def hist_diff(a, b):
    keys = sorted({*a, *b}, key=int)
    return {k: int(b.get(k, 0)) - int(a.get(k, 0)) for k in keys if int(b.get(k, 0)) != int(a.get(k, 0))}


def compare():
    cs = {t: census(t) for t in TAGS}
    for t in TAGS:
        c = cs[t]
        print(f"{t}: {c['meshes']} meshes, {c['lights']} positional lights, "
              f"{c['paired']['lights_static']} baked, {c['paired']['lightmap_users']} lightmap users")
        print(line("by reach", c))
        print(line("paired", c["paired"]))
    print()
    a, a2, live = cs["shipped"], cs["shipped2"], cs["live"]
    same = a == a2
    print(f"control, shipped against shipped2: {'IDENTICAL in every field' if same else 'DIFFERENT'}")
    if not same:
        for k in sorted(set(a) | set(a2)):
            if a.get(k) != a2.get(k):
                print(f"  differs: {k}")
    print("live against shipped:")
    print(f"  by reach: pairs {live['pairs'] - a['pairs']:+d}, over the cap "
          f"{live['over_cap'] - a['over_cap']:+d}, histogram moved {hist_diff(a['histogram'], live['histogram'])}")
    lp, ap = live["paired"], a["paired"]
    print(f"  paired:   pairs {lp['pairs'] - ap['pairs']:+d}, over the cap "
          f"{lp['over_cap'] - ap['over_cap']:+d}, worst {ap['worst']} -> {lp['worst']}, "
          f"lights baked {ap['lights_static']} -> {lp['lights_static']}")
    print(f"            histogram moved {hist_diff(ap['histogram'], lp['histogram'])}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lf", type=pathlib.Path, required=True)
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--compare", action="store_true")
    a = ap.parse_args()
    if a.run:
        run(a.lf.resolve())
    if a.compare:
        compare()


if __name__ == "__main__":
    main()
