"""Two cold runs' fights on one mission, side by side (roadmap 241, street trees).

    python docs/findings/urban_street/fight_fields.py <mission> <cold run A> <cold run B> [<seed> ...]

Per candidate seed (default seed_9003, seed_9104, seed_9205), reads:

- each run's Laser Tag report (`workspaces/cold-N-ws/.level_factory/jobs/<mission>.laser_tag_evaluate.
  candidate.<seed>/1/out/lasertag.report.json`): the grade, the score, the evaluation's own seed, and every
  `summary` field that differs, A -> B;
- each run's Lot walk scene (`<mission>.lot_assemble.candidate.<seed>/1/out/site_walk.tscn`): whether every
  `Enemy_N` under `LT_EnemySpawnPoints` stands at the same transform, and every `LT_PlayerSpawn[_N]` likewise --
  so a moved fight can be told from moved spawns before anything is said about why it moved.

Prints what it measured and stops. An unrecognised report or a scene with no enemies is printed as UNKNOWN SHAPE.
"""
import json
import pathlib
import re
import sys

F = pathlib.Path(__file__).resolve().parents[3]


def _job(n, mission, kind, seed):
    return F / "workspaces" / f"cold-{n}-ws" / ".level_factory" / "jobs" / f"{mission}.{kind}.candidate.{seed}" / "1"


def _report(n, mission, seed):
    p = _job(n, mission, "laser_tag_evaluate", seed) / "out" / "lasertag.report.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(d.get("summary"), dict) or "grade" not in d:
        return None
    return d


def _spawns(n, mission, seed):
    """({Enemy_N: transform line}, {LT_PlayerSpawn[_N]: transform line}) from the candidate's walk scene."""
    text = (_job(n, mission, "lot_assemble", seed) / "out" / "site_walk.tscn").read_text(encoding="utf-8")
    enemies = dict(re.findall(r'\[node name="(Enemy_\d+)" type="Node3D" parent="LT_EnemySpawnPoints"\]\s*\n'
                              r'(transform = [^\n]*)', text))
    crew = dict(re.findall(r'\[node name="(LT_PlayerSpawn(?:_\d+)?)" type="Node3D" parent="\."\]\s*\n'
                           r'(transform = [^\n]*)', text))
    return enemies, crew


def _fmt(v):
    return ("%.3f" % v) if isinstance(v, float) else str(v)


def main():
    mission, a, b = sys.argv[1], sys.argv[2], sys.argv[3]
    seeds = sys.argv[4:] or ["seed_9003", "seed_9104", "seed_9205"]
    for seed in seeds:
        ra, rb = _report(a, mission, seed), _report(b, mission, seed)
        if ra is None or rb is None:
            print(f"{seed}: UNKNOWN SHAPE (a report with no summary or grade)")
            continue
        (ea, pa), (eb, pb) = _spawns(a, mission, seed), _spawns(b, mission, seed)
        if not ea or not eb:
            print(f"{seed}: UNKNOWN SHAPE (no Enemy_N under LT_EnemySpawnPoints: {a} {len(ea)}, {b} {len(eb)})")
            continue
        same_e = ea == eb
        moved_e = sorted(k for k in set(ea) | set(eb) if ea.get(k) != eb.get(k))
        sa, sb = ra["summary"], rb["summary"]
        moved = sorted(k for k in set(sa) | set(sb) if sa.get(k) != sb.get(k))
        print(f"{seed}: {ra['grade']} {ra['overall_score']} -> {rb['grade']} {rb['overall_score']}; "
              f"evaluation seed {ra.get('seed')} -> {rb.get('seed')}; "
              f"enemies {len(ea)} -> {len(eb)}, transforms {'same' if same_e else 'DIFFER: ' + ', '.join(moved_e)}; "
              f"crew spawns {len(pa)} -> {len(pb)}, {'same' if pa == pb and pa else 'DIFFER' if pa and pb else 'NOT FOUND'}")
        ca, cb = ra.get("categories") or {}, rb.get("categories") or {}
        for k in sorted(set(ca) | set(cb)):
            if ca.get(k) != cb.get(k):
                print(f"    category {k}: {ca.get(k)} -> {cb.get(k)}")
        print(f"    {len(moved)} of {len(sa)} summary fields moved")
        for k in moved:
            print(f"    {k}: {_fmt(sa.get(k))} -> {_fmt(sb.get(k))}")


if __name__ == "__main__":
    main()
