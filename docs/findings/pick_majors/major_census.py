"""Which major findings decide a pick? A census over every cold workspace on this disk.

    python docs/findings/pick_majors/major_census.py

The picker (`tools/cold_drive/pick_candidate.py`, as of the factory's c868b5b) puts a candidate out when its nav
walktest is not ok or Laser Tag raised a major LT_ROUTE_NEVER_COMPLETED or LT_MAP_ENEMY_PATHING_BROKEN against it,
and among the rest takes the fewest major findings, then the highest route completion, then the higher Laser
Tag score, then the lowest seed. A "major" is any validation issue whose severity is major, critical or blocker,
from any tool.

For each `workspaces/cold-NNNN-ws/` mission whose `.level_factory/validation/<mission>.json` exists, this reads
what that rule reads -- the issues, each candidate's newest walktest and newest `lasertag.report.json` -- and
prints:

  1. every major code: how many candidates carried it, in how many workspace missions, from which tool;
  2. for each code, the picks it STEERS: the workspace missions whose pick moves when that code alone stops
     counting toward the major total (it still puts a candidate out if it is an out code);
  3. the same for a named set of codes taken together (ADVISORY below), with each moved pick's before and
     after: majors counted, completion, grade and score;
  4. for each candidate carrying LT_MAP_TRAVERSAL, the runs that timed out against those that ended in a wipe;
  5. three rules side by side -- today's; ANSWERED counted only where the candidate's walktest did not walk
     every leg; that and ADVISORY not counted -- with every pick that moves between them.

WALKED (item 5) is stricter than the walktest's own `ok`: `ok` also passes a leg the director CREDITED as
vertical access ("ok(N vertical leg(s) via ladder)", `nav_qa_director._set_leg`) without walking it, so a walked
candidate is one whose walktest is ok and whose every player walker reads exactly "ok" with every target reached.

Everything is read from the workspace; nothing is run. A validation file or report in a shape this does not
know is printed as such and that mission skipped, never read as empty. Prints what it measured and stops.
"""
import collections
import json
import pathlib
import re

F = pathlib.Path(__file__).resolve().parents[3]
MAJOR = ("major", "critical", "blocker")
OUT_CODES = ("LT_ROUTE_NEVER_COMPLETED", "LT_MAP_ENEMY_PATHING_BROKEN")
_SEED = re.compile(r"seed_(\d+)$")
#: The set item 3 takes together: Laser Tag's judgements of the fight its bots played.
ADVISORY = ("LT_MAP_TRIVIAL_ENCOUNTER", "LT_MAP_NO_REACTION_TIME", "LT_MAP_NO_ENGAGEMENT", "LT_MAP_NO_CONTACT",
            "LT_NO_SURVIVABLE_OPENING")
#: Item 5's doubts a walked walktest answers: Lot cannot tell offline whether a marker's height is a storey.
ANSWERED = ("LOT_DESTINATION_ABOVE_FLOOR",)


def _newest(paths):
    def attempt(p):
        for part in reversed(p.parts):
            if part.isdigit():
                return int(part)
        return 0
    return max(paths, key=attempt) if paths else None


def _mission(ws, mission):
    """One workspace mission's candidates as {seed: row}, or a string saying why it cannot be read."""
    jobs = ws / ".level_factory" / "jobs"
    seeds = sorted(int(m.group(1)) for p in jobs.glob(f"{mission}.lot_assemble.candidate.seed_*")
                   if (m := _SEED.search(p.name)))
    if not seeds:
        return None
    try:
        issues = json.loads((ws / ".level_factory" / "validation" / f"{mission}.json").read_text(encoding="utf-8"))["issues"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return f"validation unreadable: {type(exc).__name__}"
    if not isinstance(issues, list):
        return "validation `issues` is not a list"
    rows = {s: {"seed": s, "majors": [], "walk_ok": None, "walked": False, "completion": None, "score": None,
                "grade": "?", "summary": {}} for s in seeds}
    for i in issues:
        if not isinstance(i, dict) or "severity" not in i or "code" not in i:
            return f"an issue without severity/code: {str(i)[:80]}"
        m = _SEED.search(str(i.get("candidate_id") or ""))
        if not m or int(m.group(1)) not in rows:
            continue
        if i["severity"] in MAJOR:
            rows[int(m.group(1))]["majors"].append((str(i["code"]), str(i.get("source_tool") or "?")))
    for s, row in rows.items():
        walk = _newest(list(jobs.glob(f"{mission}.walktest_navqa.candidate.seed_{s}/*/out/*.walktest.json")))
        if walk is not None:
            try:
                wd = json.loads(walk.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                wd = {}
            row["walk_ok"] = bool(wd.get("ok"))
            players = [w for w in wd.get("walkers", []) if str(w.get("name", "")).startswith("player_")]
            row["walked"] = row["walk_ok"] and bool(players) and all(
                w.get("status") == "ok" and w.get("targets_reached") == w.get("targets_total") for w in players)
        rep = _newest(list(jobs.glob(f"{mission}.laser_tag_evaluate.candidate.seed_{s}/*/out/lasertag.report.json")))
        if rep is not None:
            try:
                d = json.loads(rep.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                d = {}
            summ = d.get("summary") if isinstance(d.get("summary"), dict) else {}
            row["summary"] = summ
            try:
                row["completion"] = float(summ["route_completion_rate"])
            except (KeyError, TypeError, ValueError):
                pass
            if isinstance(d.get("overall_score"), (int, float)):
                row["score"] = d["overall_score"]
            row["grade"] = str(d.get("grade", "?"))
    return rows


def _pick(rows, advisory=(), answered=()):
    def out(r):
        why = [c for c, _t in r["majors"] if c in OUT_CODES]
        if r["walk_ok"] is not True:
            why.append("walktest")
        return why

    def counted(r):
        return sum(1 for c, _t in r["majors"]
                   if c not in advisory and not (c in answered and r["walked"]))

    good = [r for r in rows.values() if not out(r)]
    pool = good or list(rows.values())
    best = sorted(pool, key=lambda r: (counted(r), -(r["completion"] if r["completion"] is not None else -1.0),
                                       -(r["score"] if r["score"] is not None else -1), r["seed"]))[0]
    return best, counted


def main():
    missions, skipped = [], []
    for ws in sorted(F.glob("workspaces/cold-*-ws"), key=lambda p: int(p.name.split("-")[1])):
        for v in sorted((ws / ".level_factory" / "validation").glob("*.json")):
            rows = _mission(ws, v.stem)
            if rows is None:
                continue
            if isinstance(rows, str):
                skipped.append((ws.name, v.stem, rows))
                continue
            missions.append((ws.name, v.stem, rows))
    for name, mission, why in skipped:
        print(f"SKIPPED {name} {mission}: {why}")
    n_cand = sum(len(r) for _w, _m, r in missions)
    print(f"{len(missions)} workspace missions, {n_cand} candidates\n")

    carriers = collections.Counter()
    where = collections.defaultdict(set)
    tools = collections.defaultdict(collections.Counter)
    for name, mission, rows in missions:
        for r in rows.values():
            for code in sorted({c for c, _t in r["majors"]}):
                carriers[code] += 1
                where[code].add((name, mission))
            for c, t in r["majors"]:
                tools[c][t] += 1
    print("1. major codes: candidates carrying it, workspace missions, source tool")
    for code, n in carriers.most_common():
        print(f"   {code:38s} {n:4d} candidates in {len(where[code]):3d} missions  "
              + ", ".join(f"{t} {k}" for t, k in tools[code].most_common()))

    print("\n2. picks each code steers alone (the pick moves when that code stops counting)")
    base = {(n, m): _pick(rows)[0]["seed"] for n, m, rows in missions}
    for code, _n in carriers.most_common():
        moved = [(n, m) for n, m, rows in missions if _pick(rows, (code,))[0]["seed"] != base[(n, m)]]
        if moved:
            print(f"   {code:38s} {len(moved):3d}: " + ", ".join(f"{n} {m}" for n, m in moved))
    print("   (codes not listed steer none)")

    print(f"\n3. the set taken together: {', '.join(ADVISORY)}")
    moved = 0
    for n, m, rows in missions:
        b, counted0 = _pick(rows)
        a, counted1 = _pick(rows, ADVISORY)
        if a["seed"] == b["seed"]:
            continue
        moved += 1

        def say(r, counted):
            rc = "?" if r["completion"] is None else f"{r['completion']:.2f}"
            adv = sorted({c for c, _t in r["majors"] if c in ADVISORY})
            return (f"seed_{r['seed']} {counted(r)} counted major, completion {rc}, {r['grade']} {r['score']}"
                    + (f", advisory {adv}" if adv else ""))
        print(f"   {n} {m}:\n      before {say(b, counted0)}\n      after  {say(a, counted1)}")
    print(f"   {moved} of {len(missions)} picks move")

    print("\n4. candidates carrying LT_MAP_TRAVERSAL: runs, timed out, wiped, completion, progress")
    for n, m, rows in missions:
        for r in rows.values():
            if any(c == "LT_MAP_TRAVERSAL" for c, _t in r["majors"]):
                s = r["summary"]
                print(f"   {n} {m} seed_{r['seed']}: runs {s.get('runs')}, timeouts {s.get('timeout_count')}, "
                      f"wipes {s.get('team_wipe_count')}, completion {s.get('route_completion_rate')}, "
                      f"progress {s.get('route_progress_rate')}, {r['grade']} {r['score']}")

    rules = (("today", {}), ("answered", {"answered": ANSWERED}),
             ("answered+advisory", {"answered": ANSWERED, "advisory": ADVISORY}))
    print(f"\n5. three rules: today; {', '.join(ANSWERED)} counted only where the walktest did not walk every "
          f"leg; and that with the ADVISORY set not counted")
    carriers_walked = sum(1 for _n, _m, rows in missions for r in rows.values()
                          if r["walked"] and any(c in ANSWERED for c, _t in r["majors"]))
    print(f"   candidates carrying {', '.join(ANSWERED)} whose walktest walked every leg: {carriers_walked}")
    picks = {name: {(n, m): _pick(rows, **kw)[0] for n, m, rows in missions} for name, kw in rules}
    for a, b in (("today", "answered"), ("answered", "answered+advisory"), ("today", "answered+advisory")):
        moved = [(n, m) for n, m, _rows in missions if picks[a][(n, m)]["seed"] != picks[b][(n, m)]["seed"]]
        better = worse = 0
        print(f"   {a} -> {b}: {len(moved)} of {len(missions)} picks move")
        for n, m in moved:
            pa, pb = picks[a][(n, m)], picks[b][(n, m)]
            ka = (pa["completion"] if pa["completion"] is not None else -1.0, pa["score"] if pa["score"] is not None else -1)
            kb = (pb["completion"] if pb["completion"] is not None else -1.0, pb["score"] if pb["score"] is not None else -1)
            better += kb > ka
            worse += kb < ka

            def say(r):
                rc = "?" if r["completion"] is None else f"{r['completion']:.2f}"
                return f"seed_{r['seed']} completion {rc} {r['grade']} {r['score']} majors {[c for c, _t in r['majors']]}"
            print(f"      {n} {m}: {say(pa)}\n      {'':{len(n) + len(m) + 1}s}  -> {say(pb)}")
        print(f"      moved to a higher (completion, score): {better}; to a lower: {worse}; "
              f"equal: {len(moved) - better - worse}")


if __name__ == "__main__":
    main()
