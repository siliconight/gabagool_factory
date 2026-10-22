"""Print the narrowed audit's per-item table and tallies, from all_results.json (first pass) and verify_all.json
(second pass) beside this file, as the roadmap stood after patch_roadmap_narrowed_audit.py.

    python docs/findings/narrowed_audit_2026-10-22/table.py > docs/findings/narrowed_audit_2026-10-22/table.out.md
"""
import collections
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
first = {r["n"]: r for r in json.loads((HERE / "all_results.json").read_text(encoding="utf-8"))}
second = {v["n"]: v for v in json.loads((HERE / "verify_all.json").read_text(encoding="utf-8")).values()}
HELD = {17: "met in letter; closing it amends CLAUDE.md's line 14 -- the walker's call",
        117: "its census was run in memory and never filed; nothing lints the case it waits for"}
WORD = {"DONE": "CLOSED", "MOOT": "CLOSED", "SUPERSEDED": "SUPERSEDED", "ANALYSIS": "ANALYSIS"}


def outcome(n, r):
    if n in HELD:
        return "held NARROWED"
    if n in second:
        return "now " + WORD[r["verdict"]]
    return {"OPEN": "open", "WALKER": "the walker's", "UNCLEAR": "unclear"}[r["verdict"]]


rows = sorted(first.items())
tally = collections.Counter(outcome(n, r) for n, r in rows)
print("| item | first pass | second pass | outcome | left | bears on | done since the status |")
print("|---|---|---|---|---|---|---|")
for n, r in rows:
    v = second.get(n, {}).get("verdict", "")
    print("| %d | %s | %s | %s | %s | %s | %d |" % (n, r["verdict"], v, outcome(n, r), r["size"], r["bears_on"],
                                                  len(r["done_since"])))
print()
print("outcomes:", dict(sorted(tally.items())))
still = [r for n, r in rows if outcome(n, r) in ("open", "the walker's", "held NARROWED")]
print("left on the", len(still), "still narrowed:", dict(sorted(collections.Counter(r["size"] for r in still).items())))
print("open, by what it bears on:",
      dict(sorted(collections.Counter(r["bears_on"] for n, r in rows if outcome(n, r) == "open").items())))
print("open with work done since its status:",
      [n for n, r in rows if outcome(n, r) == "open" and r["done_since"]])
print("open and small:", [n for n, r in rows if outcome(n, r) == "open" and r["size"] == "small"])
