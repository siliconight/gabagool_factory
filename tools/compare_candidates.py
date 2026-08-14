r"""Put the candidates side by side on the numbers, before you select one.

    python compare_candidates.py                       (lot-demo-ws, lot_demo_001)
    python compare_candidates.py <workspace> <mission_id>
    python compare_candidates.py <workspace> <mission_id> --json

Run from the FACTORY ROOT. Read-only: it opens files and prints. It does not
import anything from `level_factory`, so nothing it says depends on a module
being at the version you think it is -- it reads Laser Tag's own report off
disk and does its own arithmetic.

WHY THIS EXISTS. "Surface the continuous metrics on the run line and in
candidate comparison" has been the top open item in SESSION_0811 and again in
SESSION_0812, described both times as the highest-value unbuilt thing. The
reason is measured: across five evaluations of seed 5118 the total moved
exactly once, and that once was the harness failing to run. Underneath it,
kills went 0.24 -> 4.32 per run and team wipes went 25 -> 0. Every threshold
was straddled, so a 15x change in kills registered as zero. Selecting on the
grade is selecting on a number with about four reachable values.

WHAT IT CHECKS THAT A SCORE CANNOT.

  1. STALENESS. A report older than the geometry it supposedly graded is a
     grade of a level that no longer exists. This is not hypothetical -- the
     recorded grades for this mission describe a greybox draw that diverged
     from the themed draw on 14 of 15 building slots, and the selection made
     on them was invalidated. The report's mtime is compared against the
     candidate's own lot_assemble and themed_site_assemble outputs, and a
     report that predates either is called STALE in the row, not in a
     footnote.

  2. COMPARABILITY. A degraded evaluation is one where runs completed with no
     navigation -- the score describes the direct-movement fallback, not the
     map. Two candidates whose bots both walked into walls are not comparable
     to each other and neither is comparable to one whose bots walked. A
     degraded row is marked and excluded from the suggested pick.

  3. WHETHER THE SPREAD IS REAL. It prints each continuous metric across all
     candidates. If the grades tie AND every metric is identical, the
     candidates are copies of each other and the thing to fix is diversity,
     not the selection.

It does not select anything. When the ranked keys tie it prints NO SUGGESTION
and shows what actually separates the candidates instead, because a winner
picked there would be sort order wearing the word "suggested".
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

DEFAULT_WS = "workspaces/lot-demo-ws"
DEFAULT_MISSION = "lot_demo_001"

#: Laser Tag's five categories, split the way `patch_lf_score_split.py` split
#: them: three describe the MAP and two describe the ENCOUNTER. Written out
#: here rather than imported so this probe keeps working against any version
#: of the report module -- the numbers come from the report itself.
MAP_CATEGORIES = ("cover", "npc_pathing", "sightlines")          # of 60
ENCOUNTER_CATEGORIES = ("traversal", "combat_pacing")            # of 40

#: The metrics that actually moved when the score did not. SESSION_0811
#: measured every one of these changing meaningfully across three evaluations
#: that all scored 45.
CONTINUOUS = (
    ("avg_enemy_deaths_per_run", "kills/run", "{:.2f}", "up"),
    ("team_wipe_count", "wipes", "{:.0f}", "down"),
    ("avg_time_to_first_enemy_shot", "1st shot s", "{:.2f}", "up"),
    ("player_stuck_events", "stuck", "{:.0f}", "down"),
    ("shots_blocked_by_collision_percent", "blocked %", "{:.1f}", None),
    ("avg_player_survival_seconds", "survival s", "{:.1f}", "up"),
    ("route_completion_rate", "route", "{:.2f}", "up"),
)


def _num(value):
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _newest(path: Path):
    """The newest mtime anywhere under `path`, or None if it does not exist."""
    if not path.exists():
        return None
    best = None
    for f in path.rglob("*"):
        if f.is_file():
            m = f.stat().st_mtime
            best = m if best is None else max(best, m)
    return best


def _degraded(report: dict) -> bool:
    """Runs completed, but with no navigation.

    Laser Tag records this as a finding rather than a field. The report is the
    only authority on it, so the match is against what the tool writes.
    """
    for f in report.get("findings", []) or []:
        if not isinstance(f, dict):
            continue
        blob = f"{f.get('type', '')} {f.get('message', '')}".lower()
        if "navmesh" in blob or "no navigation" in blob or "navigation mesh" in blob:
            return True
    return False


def collect(ws: Path, mission: str) -> list[dict]:
    jobs = ws / ".level_factory" / "jobs"
    if not jobs.is_dir():
        raise SystemExit(f"no jobs directory under {ws} -- is that the workspace?")

    rows = []
    prefix = f"{mission}.laser_tag_evaluate.candidate.seed_"
    for d in sorted(jobs.glob(f"{prefix}*")):
        seed = d.name[len(prefix):]
        rf = d / "out" / "lasertag.report.json"
        # `packages/core/ids.py`: candidate_id(mission, seed) is
        # f"{mission_id}.candidate.seed_{seed}" -- DOTS, not underscores. Read
        # from the function rather than inferred from the job directory name,
        # which spells the same tail a second way.
        row = {"seed": seed, "candidate_id": f"{mission}.candidate.seed_{seed}",
               "report_path": str(rf)}
        if not rf.is_file():
            row["state"] = "no report"
            rows.append(row)
            continue
        try:
            report = json.loads(rf.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            row["state"] = f"unreadable: {exc}"
            rows.append(row)
            continue

        cats = {k: _num(v) or 0 for k, v in (report.get("categories") or {}).items()}
        runs = report.get("runs")
        summary = report.get("summary") or {}

        row.update({
            "state": "ok" if isinstance(runs, int) and runs > 0 else "not evaluated",
            "grade": report.get("grade"),
            "total": _num(report.get("overall_score")) or _num(report.get("score")),
            "runs": runs,
            "categories": cats,
            "map": sum(cats.get(c, 0) for c in MAP_CATEGORIES),
            "encounter": sum(cats.get(c, 0) for c in ENCOUNTER_CATEGORIES),
            "degraded": _degraded(report),
            "metrics": {k: _num(summary.get(k)) for k, *_ in CONTINUOUS},
            "report_mtime": rf.stat().st_mtime,
        })

        # STALENESS. The grade must describe the draw that ships. A report
        # written before the geometry it graded is not a weaker grade, it is a
        # grade of something else.
        graded_against = {}
        for stage in ("lot_assemble", "themed_site_assemble"):
            out = jobs / f"{mission}.{stage}.candidate.seed_{seed}" / "out"
            m = _newest(out)
            if m is not None:
                graded_against[stage] = m
        stale = [s for s, m in graded_against.items() if m > row["report_mtime"] + 1]
        row["geometry_stages"] = sorted(graded_against)
        row["stale_against"] = stale
        rows.append(row)
    return rows


def _fmt(value, spec):
    return "-" if value is None else spec.format(value)


def report(rows: list[dict], mission: str = "<mission>") -> int:
    if not rows:
        print("no laser_tag_evaluate job directories found for that mission -- "
              "has it been run?")
        return 1

    print(f"{len(rows)} candidate(s)\n")
    w = max(len(r["candidate_id"]) for r in rows)

    print(f"{'candidate':<{w}}  {'grade':<7} {'total':>5} {'map/60':>6} "
          f"{'enc/40':>6}  {'cover':>5} {'npc':>4} {'sight':>5} {'trav':>4} "
          f"{'pace':>4}  state")
    print("-" * (w + 62))
    for r in rows:
        if r["state"] not in ("ok", "not evaluated"):
            print(f"{r['candidate_id']:<{w}}  {r['state']}")
            continue
        c = r.get("categories", {})
        flags = []
        if r.get("degraded"):
            flags.append("DEGRADED (no navigation -- not comparable)")
        if r.get("stale_against"):
            flags.append("STALE (graded before " +
                         ", ".join(r["stale_against"]) + ")")
        if r["state"] != "ok":
            flags.append(r["state"])
        print(f"{r['candidate_id']:<{w}}  {str(r.get('grade') or '-'):<7} "
              f"{_fmt(r.get('total'), '{:.0f}'):>5} {r.get('map', 0):>6} "
              f"{r.get('encounter', 0):>6}  "
              f"{c.get('cover', 0):>5} {c.get('npc_pathing', 0):>4} "
              f"{c.get('sightlines', 0):>5} {c.get('traversal', 0):>4} "
              f"{c.get('combat_pacing', 0):>4}  "
              f"{'; '.join(flags) if flags else 'ok'}")

    # ---- the part the grade cannot see --------------------------------
    live = [r for r in rows if r["state"] == "ok"]
    if not live:
        print("\nnothing evaluated -- there is no comparison to make")
        return 1

    print(f"\ncontinuous metrics -- these are what actually moved when the "
          f"score did not\n")
    print(f"{'candidate':<{w}}  " +
          "  ".join(f"{label:>11}" for _k, label, _s, _d in CONTINUOUS))
    print("-" * (w + 13 * len(CONTINUOUS)))
    for r in live:
        cells = []
        for key, _label, spec, _dirn in CONTINUOUS:
            cells.append(f"{_fmt(r['metrics'].get(key), spec):>11}")
        print(f"{r['candidate_id']:<{w}}  " + "  ".join(cells))

    # ---- is the spread real? ------------------------------------------
    if len(live) > 1:
        print()
        identical = []
        for key, label, spec, _dirn in CONTINUOUS:
            vals = [r["metrics"].get(key) for r in live]
            have = [v for v in vals if v is not None]
            if len(have) == len(live) and len(set(have)) == 1:
                identical.append(label)
        totals = {r.get("total") for r in live}
        differ = len(CONTINUOUS) - len(identical)
        if not differ and len(totals) == 1:
            # EVERY metric identical, not merely some. One metric agreeing
            # across candidates is ordinary -- `route_completion_rate` is 0.00
            # everywhere for a known structural reason (the bot halts on sight)
            # and reads as agreement without being evidence of anything.
            # Calling that "copies" on a single match would be a diversity
            # alarm that fires on a working mission.
            print(f"  WARNING: every candidate scores {totals.pop()} AND every "
                  f"continuous metric is identical\n"
                  f"  across all of them. That is the signature of candidates "
                  f"that are copies of each\n  other. The thing to fix is "
                  f"diversity, not the selection.")
        else:
            print(f"  the candidates differ on {differ} of "
                  f"{len(CONTINUOUS)} continuous metrics"
                  + (f"; identical on {', '.join(identical)}" if identical
                     else "")
                  + (f", and share one grade ({sorted(totals)[0]})"
                     if len(totals) == 1 else ""))

    # ---- a suggestion, with its reasoning shown ------------------------
    print()
    usable = [r for r in live if not r["degraded"] and not r["stale_against"]]
    if not usable:
        print("  NO CANDIDATE IS SELECTABLE ON THESE NUMBERS.")
        for r in live:
            why = []
            if r["degraded"]:
                why.append("evaluated without navigation")
            if r["stale_against"]:
                why.append("graded before " + ", ".join(r["stale_against"]))
            print(f"    {r['candidate_id']}: {', '.join(why)}")
        print("\n  Re-run the mission, then compare again. A grade that "
              "describes a draw\n  that no longer ships is not a weak grade, "
              "it is a grade of something else.")
        return 1

    def rank(r):
        # Route completion first: a crew that never reached the objective
        # outranking one that did, on a cover percentage, is the ranking this
        # ordering exists to stop. Then the map half, because that is the half
        # the geometry tools can move. The total breaks ties.
        return (-(r["metrics"].get("route_completion_rate") or 0),
                -r["map"], -(r["total"] or 0))

    ranked = sorted(usable, key=rank)
    best = ranked[0]
    tied = [r for r in usable if rank(r) == rank(best)]

    if len(usable) < len(live):
        print(f"  {len(live) - len(usable)} candidate(s) excluded as degraded "
              f"or stale\n")

    if len(tied) > 1:
        # SAY SO RATHER THAN PICK. Every ranked key agrees, so any winner this
        # printed would be sort order wearing the word "suggested". The
        # difference between the candidates is real and is in the table above;
        # asserting a pick would hide that the score is what failed to see it.
        print(f"  NO SUGGESTION: {len(tied)} candidates tie on every ranked "
              f"key\n"
              f"  (route completion, map/60, total). They are not identical --"
              f" they are\n  indistinguishable TO THE GRADE. What separates "
              f"them:")
        for key, label, spec, dirn in CONTINUOUS:
            vals = {r["candidate_id"]: r["metrics"].get(key) for r in tied}
            have = [v for v in vals.values() if v is not None]
            if len(set(have)) <= 1:
                continue
            want = max(have) if dirn == "up" else min(have) if dirn == "down" else None
            leader = ("  -> " + ", ".join(sorted(c.rsplit("_", 1)[-1]
                                                 for c, v in vals.items()
                                                 if v == want))
                      if want is not None else "  (no better direction)")
            print(f"    {label:<12} " +
                  "  ".join(f"{c.rsplit('_', 1)[-1]}={_fmt(v, spec)}"
                            for c, v in sorted(vals.items())) + leader)
        print(f"\n  Pick on the metric that matters for this mission, then:\n"
              f"    lf approve {mission} candidate_selected --candidate <id>")
        return 0

    print(f"  suggested: {best['candidate_id']}  "
          f"(route {_fmt(best['metrics'].get('route_completion_rate'), '{:.2f}')}, "
          f"map {best['map']}/60, total {_fmt(best['total'], '{:.0f}')})")
    if len({r["total"] for r in usable}) == 1 and len(usable) > 1:
        print(f"  NOTE: the totals tie. This was broken on route completion "
              f"and the map half,\n  not on the grade -- the grade cannot tell "
              f"these candidates apart.")
    print(f"\n  select it with:\n"
          f"    lf approve {mission} candidate_selected "
          f"--candidate {best['candidate_id']}")
    return 0


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    ws = Path(args[0]) if args else Path(DEFAULT_WS)
    mission = args[1] if len(args) > 1 else DEFAULT_MISSION
    if not ws.is_dir():
        raise SystemExit(f"no such workspace directory: {ws}")
    print(f"workspace {ws}  mission {mission}\n")
    rows = collect(ws, mission)
    if "--json" in argv:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return 0
    return report(rows, mission)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
