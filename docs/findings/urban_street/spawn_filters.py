"""Where Lot's enemy placement finds no ground: every spot it tries, and what refuses it (roadmap 241, the near side).

    python docs/findings/urban_street/spawn_filters.py <cold run N> <mission> <seed> [<seed> ...]

Cold run 9289's seed_9205 placed none of its six enemies (`LOT_ENEMY_SPAWN_UNPLACEABLE`). Split by elimination on
its own site spec (`_scratch/2026-10-13_spawn_split/`), the near-side Empty alone or the far-side wall alone let
them stand, and the two together did not. This says why, from Lot's own code path:

  * each named candidate's `lot_assemble` job is run again as its `job.log` records it -- `stage_site_packages.py`,
    then `lot.py <site.json> <out> --walkable --navqa --portable` -- into `_scratch/2026-10-13_spawn_filters/
    seed_<S>/out`, through a runner (this file, `--run`) that wraps `site_spawns.place_enemies`;
  * inside that call and only there, every spot asked of `site_spawns.outdoors` and of
    `site_spawns.opening_engagement_is_fair` is recorded with its answer;
  * a spot `outdoors` refuses is classed by Lot's own rects, asked the same way: off the plate (`ground_rect`),
    in a building footprint or a blocker (`solid_rects`), or in a shut band alone (`shut_band_rects`: per
    `site_fences.shut_bands`, the ground behind an Empty row's front line, across the plate's whole width).
    A spot `outdoors` passed but that never reached the fairness test was refused on the standoff or the
    separation, which `place_enemies` asks inline.

Per candidate it prints the route (site metres, x and y), the Empty rows `site_fences.rows` groups and each
row's band, then per enemy how many spots were tried, how each class of refusal counted, and where it stood.
THE CONTROL: the rerun's walk scene must carry the same `Enemy_N` transforms as the job's own, and its spawn
findings the same codes; a candidate where either differs says so and its counts mean nothing.

Everything is written under `_scratch/`; nothing in a workspace or a tool is changed. Prints what it measured
and stops.
"""
import copy
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

F = pathlib.Path(__file__).resolve().parents[3]
SCR = F / "_scratch" / "2026-10-13_spawn_filters"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


def _commands(job):
    """(argv, cwd) for each command the job's log records."""
    lines = (job / "job.log").read_text(encoding="utf-8").splitlines()
    out = []
    for i, line in enumerate(lines):
        if line.startswith("$ "):
            cwd = lines[i + 1]
            if not (cwd.startswith("(cwd=") and cwd.endswith(")")):
                sys.exit(f"refusing: no (cwd=...) under {line[:60]!r}")
            out.append((line[2:].split(" "), cwd[5:-1]))
    if len(out) != 2 or not out[0][0][1].endswith("stage_site_packages.py") or not out[1][0][1].endswith("lot.py"):
        sys.exit(f"refusing: {job} does not record stage_site_packages.py then lot.py")
    return out


def _enemies(walk_scene):
    """{name: transform line} for every Enemy_N under LT_EnemySpawnPoints."""
    text = walk_scene.read_text(encoding="utf-8")
    return dict(re.findall(r'\[node name="(Enemy_\d+)" type="Node3D" parent="LT_EnemySpawnPoints"\]\s*\n'
                           r'(transform = [^\n]*)', text))


def _spawn_codes(gameplay):
    d = json.loads(gameplay.read_text(encoding="utf-8"))
    return sorted(f.get("code") for f in d.get("tactical", {}).get("findings", []) if "SPAWN" in str(f.get("code")))


def drive(n, mission, seeds):
    jobs = F / "workspaces" / f"cold-{n}-ws" / ".level_factory" / "jobs"
    for seed in seeds:
        job = jobs / f"{mission}.lot_assemble.candidate.seed_{seed}" / "1"
        (stage, scwd), (lot, lcwd) = _commands(job)
        here = SCR / f"seed_{seed}"
        out = here / "out"
        if here.exists():
            shutil.rmtree(here)
        out.mkdir(parents=True)
        stage = stage[:-1] + [str(out)]
        r = subprocess.run(stage, cwd=scwd, env=ENV, capture_output=True, text=True)
        if r.returncode:
            print(f"seed_{seed}: staging failed: {r.stderr.strip()[-200:]}")
            continue
        site_json, flags = lot[2], [a for a in lot[3:] if a.startswith("--")]
        record = here / "filters.json"
        r = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), "--run", site_json, str(out),
                            str(record), *flags], cwd=lcwd, env=ENV, capture_output=True, text=True)
        (here / "lot.log").write_text(r.stdout + r.stderr, encoding="utf-8")
        if r.returncode or not record.exists():
            print(f"seed_{seed}: the rerun failed (exit {r.returncode}); see {here / 'lot.log'}")
            continue
        theirs, ours = job / "out", out
        same_enemies = _enemies(theirs / "site_walk.tscn") == _enemies(ours / "site_walk.tscn")
        same_codes = _spawn_codes(theirs / "site.site.gameplay.json") == _spawn_codes(ours / "site.site.gameplay.json")
        _report(seed, json.loads(record.read_text(encoding="utf-8")), same_enemies, same_codes,
                _spawn_codes(theirs / "site.site.gameplay.json"))


def _report(seed, rec, same_enemies, same_codes, codes):
    print(f"seed_{seed}: control {'HOLDS' if same_enemies and same_codes else 'FAILS'} "
          f"(Enemy_N transforms {'same' if same_enemies else 'DIFFER'}, spawn codes "
          f"{'same' if same_codes else 'DIFFER'}: {', '.join(codes) or 'none'})")
    print("   route: " + " -> ".join(f"({p[0]:.1f}, {p[1]:.1f})" for p in rec["route"]))
    print(f"   plate (ground_rect): {_r(rec['ground'])}")
    for row in rec["rows"]:
        print(f"   Empty row on axis {row['axis']}: {', '.join(row['members'])}; front {row['front']:.2f} "
              f"(sign {row['sign']:+d}); its band {_r(row['band'])}")
    for i, e in enumerate(rec["enemies"]):
        c = e["classes"]
        stood = "stood at (%.1f, %.1f)" % tuple(e["stood"]) if e["stood"] else "DROPPED"
        print(f"   enemy {i}: {e['tried']} spots -- off the plate {c['off_plate']}, in a footprint or blocker "
              f"{c['in_solid']}, in a shut band alone {c['band_only']}, standoff or separation "
              f"{c['standoff_or_separation']}, unfair opening {c['unfair']}; {stood}")


def _r(rect):
    return "none" if rect is None else "(%.1f, %.1f)-(%.1f, %.1f)" % tuple(rect)


def run(site_json, out, record, flags):
    """In `lot/`, as the job runs: `lot.assemble`, with `place_enemies` watched."""
    sys.path.insert(0, os.getcwd())
    import lot
    import site_fences
    import site_spawns
    import site_streets

    seen = {}
    real_place = site_spawns.place_enemies

    def place(site_spec, positions, **kw):
        # copied at the call: `assemble` goes on adding to the same dict (cover, the backdrop) after it
        as_read = copy.deepcopy({"site_spec": site_spec, "positions": dict(positions)})
        ground = site_spawns.ground_rect(site_spec)
        solids = site_spawns.solid_rects(site_spec)
        bands = site_spawns.shut_band_rects(site_spec)
        import site_extent
        plate = site_extent.resolve(site_spec).rect
        rows = []
        roads = site_streets.roads(site_spec)
        for axis, members in site_fences.rows(site_spec):
            front, sign = site_fences.front_line(axis, members, roads, plate)
            rows.append({"axis": axis, "members": [m[0] for m in members], "front": front, "sign": sign,
                         "band": site_fences.shut_band(axis, front, sign, plate)})
        # `place_enemies` asks `_candidates` once per enemy, eagerly, before trying that enemy's spots, so
        # the last record opened is the enemy every later `outdoors` and fairness question belongs to
        enemies = []
        closed = []
        real_out, real_fair = site_spawns.outdoors, site_spawns.opening_engagement_is_fair
        real_candidates = site_spawns._candidates
        real_findings = site_spawns._findings

        def findings(*a, **k):
            # after the last enemy's loop `_findings` asks the fairness test again of every enemy placed
            # (site_spawns.py:1312); those questions belong to no enemy's search and are not counted
            closed.append(True)
            return real_findings(*a, **k)

        def candidates(index, *a, **k):
            enemies.append({"index": index, "tried": 0, "passed_outdoors": 0, "asked_fair": 0,
                            "classes": {"off_plate": 0, "in_solid": 0, "band_only": 0, "unfair": 0}})
            return real_candidates(index, *a, **k)

        def outdoors(point, g, rects):
            ok = real_out(point, g, rects)
            if closed or not enemies:
                return ok
            e = enemies[-1]
            e["tried"] += 1
            if ok:
                e["passed_outdoors"] += 1
            elif g is not None and not site_spawns._inside(point, g):
                e["classes"]["off_plate"] += 1
            elif not real_out(point, g, solids):
                e["classes"]["in_solid"] += 1
            else:
                e["classes"]["band_only"] += 1
            return ok

        def fair(candidate, crew_path, occluders, *a, **k):
            ok = real_fair(candidate, crew_path, occluders, *a, **k)
            if closed or not enemies:
                return ok
            e = enemies[-1]
            e["asked_fair"] += 1
            if not ok:
                e["classes"]["unfair"] += 1
            return ok

        site_spawns.outdoors, site_spawns.opening_engagement_is_fair = outdoors, fair
        site_spawns._candidates, site_spawns._findings = candidates, findings
        try:
            plan = real_place(site_spec, positions, **kw)
        finally:
            site_spawns.outdoors, site_spawns.opening_engagement_is_fair = real_out, real_fair
            site_spawns._candidates, site_spawns._findings = real_candidates, real_findings
        placed = iter(plan.positions)
        out_enemies = []
        for i, e in enumerate(enemies):
            e["classes"]["standoff_or_separation"] = e["passed_outdoors"] - e["asked_fair"]
            stood = None if i in plan.dropped else list(next(placed))[:2]
            out_enemies.append({"tried": e["tried"], "classes": e["classes"], "stood": stood})
        seen.update(route=[list(positions[k][:2]) for k in ("spawn", "objective", "extraction")],
                    ground=ground, rows=rows, bands=bands, enemies=out_enemies,
                    # the call's own inputs, so a test can stand on the site as `place_enemies` read it
                    site_spec=as_read["site_spec"],
                    positions={k: list(v) for k, v in as_read["positions"].items()})
        return plan

    site_spawns.place_enemies = place
    lot.assemble(site_json, out, walkable="--walkable" in flags, navqa="--navqa" in flags,
                 preview="--preview" in flags, portable="--portable" in flags)
    pathlib.Path(record).write_text(json.dumps(seen), encoding="utf-8")


if __name__ == "__main__":
    if sys.argv[1] == "--run":
        run(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:])
    else:
        drive(sys.argv[1], sys.argv[2], sys.argv[3:])
