"""Assemble `decisions.json` for the narrowed audit's roadmap patch: each item the second pass upheld, its status text
the second pass's correction where it gave one and the first pass's proposal otherwise; item 14's correction; the
walker's answers on 293, 295 and 296 (`walker_answers.json`). Items 17 and 117 are held back (see the audit's
README). Reads the audit's records from `docs/findings/narrowed_audit_2026-10-22/`.

    python patches/roadmap_narrowed_audit/build_decisions.py
"""
import json
import pathlib
import re

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
A = F / "docs" / "findings" / "narrowed_audit_2026-10-22"
HERE = pathlib.Path(__file__).resolve().parent
first = {r["n"]: r for r in json.loads((A / "all_results.json").read_text(encoding="utf-8"))}
second = {v["n"]: v for v in json.loads((A / "verify_all.json").read_text(encoding="utf-8")).values()}

HELD = {17, 117}
HEAD = re.compile(r"^\*STATUS: ([A-Z]+) 2026-10-22(?: by ([0-9][0-9 and,]*?))? -- ")
out = []
for n in sorted(second):
    if n in HELD or n == 14:
        continue
    v = second[n]
    assert v["verdict"] in ("UPHELD", "UPHELD_WITH_FIXES"), (n, v["verdict"])
    s = v["corrected_status"] or first[n]["proposed_status"]
    m = HEAD.match(s)
    assert m and s.endswith("*") and "\n" not in s, n
    out.append({"n": n, "status": m.group(1), "by": m.group(2) or "", "text": s[m.end():-1].strip()})

ITEM14 = (
    "CORRECTED: the status below says \"the walk test walks the crew's body over every leg of every candidate "
    "(208)\"; it does not. The walk test (`walktest_navqa`, which runs Lot's "
    "`godot/addons/heist_nav_qa/nav_qa_director.gd`, last changed 2026-10-06 in Lot 0.97.2) walks a capsule of "
    "`AGENT_RADIUS * 0.7` -- 0.28 m at the bake's 0.4 m (:40, :818) -- on a floor of the bake slope plus one degree, "
    "56 (:830), and nothing reads the contract's `walker_capsule_radius_m`. The crew's 0.35 m body walked once, over "
    "18 kept walk tests on patched copies, 18 of 18 (`docs/findings/walktest_crew_body/`); whether the gate adopts "
    "it is item 208's open question. The cold run 9314 figures the status cites are not in the file it names. The "
    "class this item found -- a body the path query does not stand in for -- is so carried by 208, and the doors by "
    "197 (Deli Counter 0.214.0, every walkable door to the contract's 1.25 m). The same sentence in "
    "`docs/findings/open_items_remeasure/README.md` is corrected there the same day "
    "(`docs/findings/narrowed_audit_2026-10-22/`).")
out.append({"n": 14, "status": "SUPERSEDED", "by": "197 and 208", "text": ITEM14})
out += json.loads((HERE / "walker_answers.json").read_text(encoding="utf-8"))
out.sort(key=lambda d: d["n"])
(HERE / "decisions.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(len(out), "decisions:", [(d["n"], d["status"]) for d in out])
