"""What Lot's heist gate and pacing would say about every site spec on disk, if
Level Factory wrote the brief's mode and target window (roadmap 200).

    python docs/findings/brief_pacing_mode/heist_gate_census.py [workspaces_dir]

Level Factory's site spec carries no `mode` and puts `target_minutes` at its top
level. Lot's `site_tactical.gate` runs no gate without a mode, and with
`mode: heist` RAISES (the build fails) unless spawn -> objective -> extraction
are joined by declared paths or a shared street. `site_pacing.estimate_pacing`
counts travel only for a mode it knows, and reads its window from
`pacing.target_minutes`. This injects both into a COPY of each spec, read from
disk, and calls Lot's own functions on it. Nothing is written.

Reads every `.level_factory/temp/<mission>/candidate_seed_<N>/site.json` under the
workspaces directory. The `themed/` copy of a candidate is skipped: it carries
the same buildings, paths and roles as the greybox spec, which is the one the
candidate is judged on.

Pacing here counts ONE objective marker (Lot's floor, `max(1, n)`) and no loot:
the merged gameplay that holds the real markers is a Lot output, not read here.
So the objective-work term is a floor, and the travel legs are what this adds.
Distances are metres on the site plan, building origin to building origin
(`site_pacing._dist`), not walked routes.
"""
import collections
import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "lot"))
import site_pacing  # noqa: E402  (Lot's own module)
import site_tactical  # noqa: E402


def specs(ws_root):
    for p in sorted(ws_root.glob("*/.level_factory/temp/*/candidate_seed_*/site.json")):
        yield p


def main():
    ws_root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "workspaces"
    rows, unreadable = [], []
    for p in specs(ws_root):
        try:
            spec = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            unreadable.append((p, str(exc)))
            continue
        ws = p.parts[len(ws_root.parts)]
        mission, cand = p.parts[-3], p.parts[-2]
        s = copy.deepcopy(spec)
        had_mode, had_pacing = "mode" in spec, "pacing" in spec
        s["mode"] = "heist"
        tm = spec.get("target_minutes")
        if isinstance(tm, list) and len(tm) == 2:
            s.setdefault("pacing", {})["target_minutes"] = tm
        try:
            site_tactical.gate(s)
            gate = "pass"
        except site_tactical.SiteTacticalError as exc:
            gate = "FAIL: %s" % exc
        intel = site_tactical.analyze(s)["intel"]
        pace = site_pacing.estimate_pacing(s, {"markers": []})
        unpaced = site_pacing.estimate_pacing(spec, {"markers": []})
        rows.append({
            "ws": ws, "mission": mission, "cand": cand,
            "roles": (spec.get("spawn"), spec.get("objective"), spec.get("extraction")),
            "n_buildings": len(spec.get("buildings", [])),
            "had_mode": had_mode, "had_pacing": had_pacing, "gate": gate,
            "isolated": intel.get("isolated_buildings") or [],
            "approaches": intel.get("objective_approaches"),
            "travel_s": sum(b["secs"] for b in pace["breakdown"] if b["phase"].startswith("travel")),
            "expected_min": pace["estimate_expected_min"], "range": pace["range_min"],
            "target": pace["target_min"], "status": pace["status"],
            "unpaced_target": unpaced["target_min"], "unpaced_expected_min": unpaced["estimate_expected_min"],
        })

    print("site specs read: %d (themed copies skipped), unreadable: %d" % (len(rows), len(unreadable)))
    for p, e in unreadable:
        print("  UNREADABLE %s: %s" % (p, e))
    print("already carrying a mode: %d; already carrying pacing: %d"
          % (sum(r["had_mode"] for r in rows), sum(r["had_pacing"] for r in rows)))
    print()
    print("HEIST GATE (site_tactical.gate with mode=heist injected)")
    gates = collections.Counter("pass" if r["gate"] == "pass" else r["gate"].split(":")[0] for r in rows)
    print("  " + ", ".join("%s %d" % kv for kv in sorted(gates.items())))
    for r in rows:
        if r["gate"] != "pass":
            print("  %-28s %-22s %-22s roles %s  %s" % (r["ws"], r["mission"], r["cand"], r["roles"], r["gate"]))
    print("  specs with an isolated building: %d" % sum(1 for r in rows if r["isolated"]))
    by_n = collections.Counter(r["n_buildings"] for r in rows)
    print("  buildings per site: %s" % dict(sorted(by_n.items())))
    same = [r for r in rows if r["roles"][1] and r["roles"][1] == r["roles"][2]]
    print("  objective == extraction building: %d of %d" % (len(same), len(rows)))
    same_n = collections.Counter(r["n_buildings"] for r in same)
    print("    by buildings per site: %s (a one-building site is all three by construction)"
          % dict(sorted(same_n.items())))
    spawn_obj = [r for r in rows if r["n_buildings"] > 1 and r["roles"][0] == r["roles"][1]]
    print("  spawn == objective on a site of 2+ buildings: %d" % len(spawn_obj))
    print()
    print("PACING (one objective marker, no loot; origin-to-origin metres at 4.0 m/s)")
    print("  as written today: target %s on %d of %d specs"
          % (collections.Counter(r["unpaced_target"] for r in rows).most_common(1)[0][0],
             collections.Counter(r["unpaced_target"] for r in rows).most_common(1)[0][1], len(rows)))
    exp = sorted(r["expected_min"] for r in rows)
    trv = sorted(r["travel_s"] for r in rows)
    if rows:
        print("  with mode and window: expected %.1f-%.1f min (median %.1f); travel %.0f-%.0f s (median %.0f)"
              % (exp[0], exp[-1], exp[len(exp) // 2], trv[0], trv[-1], trv[len(trv) // 2]))
        print("  target windows: %s" % dict(collections.Counter(r["target"] for r in rows)))
        print("  status: %s" % dict(collections.Counter(r["status"] for r in rows)))


if __name__ == "__main__":
    main()
