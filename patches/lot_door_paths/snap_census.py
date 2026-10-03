"""What `site_paths.snap_to_doors` does to every site spec on disk that has
its merged gameplay beside it. Reads, snaps a COPY, prints; writes nothing.

    python snap_census.py                 every workspace under workspaces/
    python snap_census.py <workspace> <mission> <seed>     one lot, in full

For each path end that belongs to a building: snapped (and how far it moved)
or left with a finding. Prints what it measured."""
import copy
import glob
import json
import math
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lot"))
import site_paths  # noqa: E402


def pair(ws, mission, seed):
    spec = ws / ".level_factory" / "temp" / mission / f"candidate_seed_{seed}" / "site.json"
    gp = ws / ".level_factory" / "jobs" / f"{mission}.lot_assemble.candidate.seed_{seed}" / "out" / "site.site.gameplay.json"
    return spec, gp


def run(spec_p, gp_p, verbose):
    spec = json.loads(spec_p.read_text(encoding="utf-8"))
    merged = json.loads(gp_p.read_text(encoding="utf-8"))
    bld = {b["id"]: b for b in spec.get("buildings", [])}
    before = [site_paths.endpoints_or_none(p, bld) for p in spec.get("paths", [])]
    after_spec = copy.deepcopy(spec)
    findings = site_paths.snap_to_doors(after_spec, merged)
    moved, ends, snapped = [], 0, 0
    for i, (p0, p1) in enumerate(zip(spec.get("paths", []), after_spec.get("paths", []))):
        a0, b0 = before[i]
        a1, b1 = site_paths.endpoints_or_none(p1, bld)
        if a0 is None:
            continue
        owned = 2 if "from" in p0 else (1 if p0.get("building") in bld else 0)
        ends += owned
        snapped += len(p1.get("snapped") or {})
        da, db = math.dist(a0, a1), math.dist(b0, b1)
        moved.append(max(da, db))
        if verbose:
            label = f"{p0.get('from')}->{p0.get('to')}" if "from" in p0 else f"spur {p0.get('building')}"
            print("  path %d %-10s a (%7.2f, %7.2f) -> (%7.2f, %7.2f)  b (%7.2f, %7.2f) -> (%7.2f, %7.2f)  snapped %s" % (
                i, label, a0[0], a0[1], a1[0], a1[1], b0[0], b0[1], b1[0], b1[1], p1.get("snapped")))
    if verbose:
        for f in findings:
            print("  finding:", f["message"])
    return ends, snapped, findings, moved


def main():
    if len(sys.argv) == 4:
        spec_p, gp_p = pair(pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3])
        ends, snapped, findings, moved = run(spec_p, gp_p, True)
        print("ends owned by a building: %d, snapped: %d, left: %d" % (ends, snapped, len(findings)))
        return
    tot_e = tot_s = tot_f = sites = 0
    worst = []
    for gp in sorted(glob.glob(str(ROOT / "workspaces" / "*" / ".level_factory" / "jobs" / "*.lot_assemble.candidate.seed_*" / "out" / "site.site.gameplay.json"))):
        gp_p = pathlib.Path(gp)
        job = gp_p.parents[1].name
        mission, seed = job.split(".lot_assemble.candidate.seed_")
        ws = gp_p.parents[4]
        spec_p, _ = pair(ws, mission, seed)
        if not spec_p.exists():
            continue
        try:
            ends, snapped, findings, moved = run(spec_p, gp_p, False)
        except Exception as e:  # a spec this cannot read is said, not skipped silently
            print("CANNOT READ %s %s seed %s: %r" % (ws.name, mission, seed, e))
            continue
        sites += 1
        tot_e += ends
        tot_s += snapped
        tot_f += len(findings)
        if findings:
            worst.append((len(findings), ws.name, mission, seed, [f["message"].split(": ", 1)[1][:70] for f in findings]))
    print("sites read: %d   ends owned by a building: %d   snapped: %d   left with a finding: %d" % (sites, tot_e, tot_s, tot_f))
    for n, ws, mission, seed, msgs in sorted(worst, reverse=True)[:12]:
        print("  %d  %s %s seed %s" % (n, ws, mission, seed))
        for m in msgs[:3]:
            print("       ", m)


if __name__ == "__main__":
    main()
