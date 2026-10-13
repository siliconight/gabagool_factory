"""One real site's Lot job and cover plan, before and after `site_cover`'s fallback moved to the contract's cell
(roadmap 197; Lot 0.120.2).

    python docs/findings/door_widths/cover_fallback_ab.py replay <tag>
    python docs/findings/door_widths/cover_fallback_ab.py capture <tag>
    python docs/findings/door_widths/cover_fallback_ab.py diff <tag_a> <tag_b>
    python docs/findings/door_widths/cover_fallback_ab.py plans <inputs.json> <site_cover_a.py> <site_cover_b.py>

The site is cold run 9284's `club_block_014.lot_assemble.candidate.seed_9080`. Its scratch lives in
`_scratch/2026-10-13_cover_fallback/` at the factory root.

replay   runs the two commands the job's own `job.log` records (`stage_site_packages.py`, then `lot.py ...
         --walkable --navqa --portable`), with the job's interpreter and working directories, the out dir swapped
         for `run/out` -- the same path every time, so a path a file embeds cannot differ between tags -- and
         moves it to `<tag>/out`, with the commands' output in `<tag>/replay.log`.
capture  runs the same `lot.py` command with `site_cover.plan_cover` wrapped, and writes the arguments and keywords
         it was called with to `<tag>/plan_cover_inputs.json`. The wrapper calls the real function and returns its
         result; the site it builds is deleted.
diff     compares every file under two tags' `out`, byte for byte, and their logs line for line. The tag `job`
         is the cold run's own out dir, whose log is the runner's and is not compared.
plans    loads two copies of `site_cover.py` side by side (stdlib only, so a copy from git loads beside the live
         one) and asks each to plan cover on captured inputs: once as the job asked, then with the room beside a
         wall forced under the contract's (`clearance=`, the way `tests/test_lot.py` forces one) so the pinch
         check has lanes to report. Then the fixture `tests/test_cover_fallback.py` builds, whose one piece
         stands a set lane off a wall: under the job's bake, and under a 0.25 m cell. For each it prints the
         pieces, the pinches, the gap each module derives with and without the bake, and the number
         `LOT_COVER_PINCH` states.

Prints what it measured and stops.
"""
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

FACTORY = pathlib.Path(__file__).resolve().parents[3]
LOT = FACTORY / "lot"
JOB = (FACTORY / "workspaces" / "cold-9284-ws" / ".level_factory" / "jobs"
       / "club_block_014.lot_assemble.candidate.seed_9080" / "1")
SCRATCH = FACTORY / "_scratch" / "2026-10-13_cover_fallback"
RUN_OUT = SCRATCH / "run" / "out"
#: the room beside a wall each forced run asks for: under the contract's 2.5 m for a 3 m piece
FORCED_CLEARANCES = (2.0, 1.5, 1.0)
#: the job runner passes os.environ on (level_factory/packages/jobs/runner.py); Lot reads only
#: DC_AGENT_CONTRACT of it, unset there and here. UTF-8 so a print cannot fail on a code page.
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}
#: the fixture's coarser bake: 2*ceil(0.4/0.25)*0.25 + 0.5 = 1.5 m, neither the fallback's gap nor the contract's
COARSE_BAKE = {"agent_radius_m": 0.4, "cell_size_m": 0.25}


def _commands():
    """The job's commands as its log records them: (argv, cwd), the job's out dir swapped for `RUN_OUT`."""
    lines = (JOB / "job.log").read_text(encoding="utf-8").splitlines()
    job_out = str(JOB / "out")
    cmds = []
    for i, line in enumerate(lines):
        if not line.startswith("$ "):
            continue
        cwd = lines[i + 1]
        if not (cwd.startswith("(cwd=") and cwd.endswith(")")):
            sys.exit(f"refusing: no (cwd=...) under {line[:60]!r}")
        if '"' in line or "'" in line:
            sys.exit(f"refusing: a quoted argument, which a split on spaces would break: {line[:80]!r}")
        argv = line[2:].split(" ")
        if argv.count(job_out) != 1:
            sys.exit(f"refusing: the job's out dir appears {argv.count(job_out)} times in {line[:80]!r}")
        cmds.append(([str(RUN_OUT) if a == job_out else a for a in argv], cwd[5:-1]))
    if len(cmds) != 2 or not cmds[1][0][1].endswith("lot.py"):
        sys.exit(f"refusing: expected stage + lot.py, read {[c[0][1] for c in cmds]}")
    return cmds


def _fresh_run_out():
    if RUN_OUT.exists():
        shutil.rmtree(RUN_OUT)
    RUN_OUT.parent.mkdir(parents=True, exist_ok=True)


def _numbers(bake):
    return {k: v for k, v in (bake or {}).items() if isinstance(v, (int, float))}


def replay(tag):
    dest = SCRATCH / tag
    if dest.exists():
        sys.exit(f"refusing: {dest} exists")
    _fresh_run_out()
    log = []
    for argv, cwd in _commands():
        r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", env=ENV)
        log.append(f"$ {' '.join(argv)}\n(cwd={cwd})\n{r.stdout}{r.stderr}(exit={r.returncode})\n")
        if r.returncode:
            sys.exit(f"{argv[1]} exited {r.returncode}:\n{r.stdout[-2000:]}{r.stderr[-2000:]}")
    dest.mkdir(parents=True)
    shutil.move(str(RUN_OUT), str(dest / "out"))
    (dest / "replay.log").write_bytes("".join(log).encode("utf-8"))
    files = sum(1 for p in (dest / "out").rglob("*") if p.is_file())
    print(f"replay {tag}: {files} files under {dest / 'out'}")


def _spy(inputs_path, lot_argv):
    """Run in the job's interpreter: `lot.py` as `__main__`, `site_cover.plan_cover` wrapped."""
    import runpy
    sys.path.insert(0, str(LOT))
    import site_cover
    real = site_cover.plan_cover
    calls = []

    def spy(points, rects, ground, **kw):
        calls.append({"points": {k: list(v) for k, v in points.items()},
                      "rects": [list(r) for r in rects], "ground": list(ground) if ground else None,
                      "kw": json.loads(json.dumps(kw, default=list))})
        return real(points, rects, ground, **kw)

    site_cover.plan_cover = spy
    sys.argv = lot_argv
    try:
        runpy.run_path(lot_argv[0], run_name="__main__")
    except SystemExit as exc:
        if exc.code not in (None, 0):
            raise
    finally:
        site_cover.plan_cover = real
    pathlib.Path(inputs_path).write_bytes(json.dumps(calls, indent=1).encode("utf-8"))


def capture(tag):
    dest = SCRATCH / tag
    dest.mkdir(parents=True, exist_ok=True)
    inputs = dest / "plan_cover_inputs.json"
    if inputs.exists():
        sys.exit(f"refusing: {inputs} exists")
    _fresh_run_out()
    (stage_argv, stage_cwd), (lot_argv, lot_cwd) = _commands()
    r = subprocess.run(stage_argv, cwd=stage_cwd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=ENV)
    if r.returncode:
        sys.exit(f"stage exited {r.returncode}: {r.stdout[-1000:]}")
    r = subprocess.run([lot_argv[0], str(pathlib.Path(__file__).resolve()), "_spy", str(inputs)] + lot_argv[1:],
                       cwd=lot_cwd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=ENV)
    if r.returncode:
        sys.exit(f"capture exited {r.returncode}:\n{r.stdout[-2000:]}{r.stderr[-2000:]}")
    shutil.rmtree(RUN_OUT)
    calls = json.loads(inputs.read_text(encoding="utf-8"))
    for i, c in enumerate(calls):
        print(f"capture {tag}: call {i}: {len(c['points'])} points, {len(c['rects'])} rects, "
              f"keywords {sorted(c['kw'])}, nav_bake {_numbers(c['kw'].get('nav_bake'))}")


def _files(root):
    return {p.relative_to(root).as_posix(): p for p in sorted(root.rglob("*")) if p.is_file()}


def _out(tag):
    return JOB / "out" if tag == "job" else SCRATCH / tag / "out"


def diff(a, b):
    fa, fb = _files(_out(a)), _files(_out(b))
    same, differ = 0, []
    for rel in sorted(set(fa) & set(fb)):
        if fa[rel].read_bytes() == fb[rel].read_bytes():
            same += 1
        else:
            differ.append(rel)
    print(f"diff {a} {b}: {len(fa)} files / {len(fb)} files; identical {same}; differing {len(differ)}; "
          f"only in {a} {len(set(fa) - set(fb))}; only in {b} {len(set(fb) - set(fa))}")
    for rel in differ:
        la = fa[rel].read_bytes().decode("utf-8", "replace").splitlines()
        lb = fb[rel].read_bytes().decode("utf-8", "replace").splitlines()
        first = next((i for i, (x, y) in enumerate(zip(la, lb)) if x != y), min(len(la), len(lb)))
        print(f"  differs: {rel} ({len(la)} / {len(lb)} lines), first at line {first + 1}")
        print(f"    {a}: {la[first][:200] if first < len(la) else '(end)'}")
        print(f"    {b}: {lb[first][:200] if first < len(lb) else '(end)'}")
    for rel in sorted(set(fa) ^ set(fb)):
        print(f"  only in {a if rel in fa else b}: {rel}")
    if "job" in (a, b):
        return
    # the commands' output
    la = (SCRATCH / a / "replay.log").read_text(encoding="utf-8").splitlines()
    lb = (SCRATCH / b / "replay.log").read_text(encoding="utf-8").splitlines()
    dl = [(x, y) for x, y in zip(la, lb) if x != y]
    print(f"  replay.log: {len(la)} / {len(lb)} lines, {len(dl)} differing"
          + ("" if len(la) == len(lb) else " (lengths differ)"))
    for x, y in dl[:6]:
        print(f"    {a}: {x[:200]}\n    {b}: {y[:200]}")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod          # dataclasses resolve string annotations through sys.modules
    spec.loader.exec_module(mod)
    return mod


def _plan_rows(plan):
    """Every field `CoverPlan` declares, at full precision -- an unrecognised field is printed, not dropped."""
    import dataclasses
    rows = {}
    for f in dataclasses.fields(plan):
        value = getattr(plan, f.name)
        if f.name == "cover":
            value = [(c.name, repr(c.x), repr(c.y), repr(c.size_x), repr(c.size_y), c.species, c.yaw,
                      c.variant, c.breaks) for c in value]
        rows[f.name] = repr(value)
    return rows


def _stated(mod, plan, opening_range):
    found = [f for f in mod.findings(plan, opening_range=opening_range) if f["code"] == "LOT_COVER_PINCH"]
    if not found:
        return None
    m = re.search(r"less than the ([0-9.e+-]+) m", found[0]["message"])
    if not m:
        sys.exit(f"refusing: LOT_COVER_PINCH's message no longer reads 'less than the N m': {found[0]['message']}")
    return float(m.group(1))


def _ab(mods, label, args, kw):
    got = {}
    for key, mod in mods.items():
        plan = mod.plan_cover(*args, **kw)
        got[key] = (_plan_rows(plan), plan, _stated(mod, plan, kw["opening_range"]))
    rows_a, rows_b = got["a"][0], got["b"][0]
    differing = [k for k in rows_a if k in rows_b and rows_a[k] != rows_b[k]]
    only = sorted(set(rows_a) ^ set(rows_b))
    pa, pb = got["a"][1], got["b"][1]
    print(f"  {label}: a {len(pa.cover)} pieces {len(pa.pinches)} pinches; "
          f"b {len(pb.cover)} pieces {len(pb.pinches)} pinches; fields differing {differing or 'none'}; "
          f"fields in one only {only or 'none'}")
    for key in ("a", "b"):
        plan, stated = got[key][1], got[key][2]
        gaps = sorted(g for _n, _w, g in plan.pinches)
        over = [g for g in gaps if stated is not None and g >= stated]
        print(f"    {key}: LOT_COVER_PINCH states {stated!r}; pinch gaps {gaps}; "
              f"gaps at or over the stated number {over}")


def plans(inputs_path, path_a, path_b):
    calls = json.loads(pathlib.Path(inputs_path).read_text(encoding="utf-8"))
    mods = {"a": _load(path_a, "site_cover_ab_a"), "b": _load(path_b, "site_cover_ab_b")}
    print(f"a = {path_a}\nb = {path_b}")
    for i, c in enumerate(calls):
        points = {k: tuple(v) for k, v in c["points"].items()}
        rects = [tuple(r) for r in c["rects"]]
        ground = tuple(c["ground"]) if c["ground"] else None
        kw = dict(c["kw"])
        bake = kw.get("nav_bake")
        print(f"\ncall {i}: nav_bake {_numbers(bake)}")
        for key, mod in mods.items():
            print(f"  {key}: _NAV_BAKE_FALLBACK {mod._NAV_BAKE_FALLBACK}; min_passable_gap() {mod.min_passable_gap()!r}; "
                  f"min_passable_gap(bake) {mod.min_passable_gap(bake)!r}; BUILDING_CLEARANCE "
                  f"{mod.BUILDING_CLEARANCE!r}; building_clearance(3, bake) {mod.building_clearance(3.0, bake)!r}")
        _ab(mods, "as the job asked", (points, rects, ground), kw)
        for cl in FORCED_CLEARANCES:
            _ab(mods, f"clearance forced to {cl:g} m", (points, rects, ground), dict(kw, clearance=cl))
    # THE FIXTURE: a 3 m square piece lands at (35, 0) on a 100 m line, and a wall's face stands `lane` metres
    # off its edge; the room beside a wall is forced to nothing, so the piece stands there.
    job_bake = calls[0]["kw"].get("nav_bake") if calls else None
    print("\nfixture: LT_PlayerSpawn (0, 0), Enemy_0 (100, 0), one wall a lane off a 3 m piece at (35, 0)")
    for name, bake, lane in (("the job's bake", job_bake, 0.5), ("the job's bake", job_bake, 1.1),
                             ("a 0.25 m cell", COARSE_BAKE, 1.3)):
        args = ({"LT_PlayerSpawn": (0.0, 0.0), "Enemy_0": (100.0, 0.0)},
                [(30.0, 1.5 + lane, 40.0, 12.0)], (-20.0, -30.0, 120.0, 30.0))
        print(f"  {name} {_numbers(bake)}: a derives {mods['a'].min_passable_gap(bake)!r}, "
              f"b derives {mods['b'].min_passable_gap(bake)!r}")
        _ab(mods, f"lane {lane:g} m", args, {"opening_range": 45.0, "clearance": 0.0, "nav_bake": bake})


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "_spy":
        _spy(sys.argv[2], sys.argv[3:])
    elif len(sys.argv) == 3 and sys.argv[1] == "replay":
        replay(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "capture":
        capture(sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] == "diff":
        diff(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 5 and sys.argv[1] == "plans":
        plans(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        sys.exit(__doc__)
