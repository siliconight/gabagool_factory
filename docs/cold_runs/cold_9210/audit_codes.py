"""The site audit's findings in a cold run's validation report, by candidate
and job (roadmap 215).

    python audit_codes.py <workspace> [mission]

Reads `<workspace>/.level_factory/validation/<mission>.json` -- the file
`cold_drive.sh`'s findings step counts -- and prints every issue whose code
starts `S_` or `LOT_SITE_AUDIT`, grouped by candidate and stage, with its
severity, blocking flag and message, then the job log of each Lot assembly
that wrote them, so the report can be held against what Lot printed.
Prints what it measured and stops. A report with no `issues` list FAILS.
"""
import collections
import glob
import json
import os
import sys

ws = sys.argv[1]
mission = sys.argv[2] if len(sys.argv) > 2 else "club_block_014"
lf = os.path.join(ws, ".level_factory")
with open(os.path.join(lf, "validation", mission + ".json"), encoding="utf-8") as f:
    doc = json.load(f)
issues = doc.get("issues")
if not isinstance(issues, list):
    raise SystemExit("no `issues` list in the validation report: unknown shape")
rows = [i for i in issues if str(i.get("code", "")).startswith(("S_", "LOT_SITE_AUDIT"))]
print(f"{len(issues)} issues in the report, {len(rows)} from the site audit")
by = collections.defaultdict(list)
for i in rows:
    by[(i.get("candidate_id"), i.get("stage_id"))].append(i)
for (cand, stage), its in sorted(by.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]))):
    print(f"\n{cand}  stage {stage}")
    for i in its:
        print(f"  {i['severity']:9} blocking={i['blocking']!s:5} {i['code']}: {i['message'][:110]}")
print("\nwhat each Lot assembly printed:")
for log in sorted(glob.glob(os.path.join(lf, "jobs", f"{mission}.lot_assemble*", "*", "*.log"))):
    with open(log, encoding="utf-8", errors="replace") as f:
        lines = [l.rstrip() for l in f if l.startswith(("[site_audit]", "  [MED]", "  [INFO]", "  [HIGH]"))]
    if lines:
        rel = os.path.relpath(log, lf)
        print(f"  {rel}")
        for l in lines:
            print(f"    {l[:120]}")
