"""Two install tests' findings, stage by stage, candidate by candidate, code by code.

Reads each workspace's `levels/.level_factory/validation/<mission>.json` (the
file `make` writes; its `issues` list is the count `make` prints second) and
prints, for every (stage, candidate, code) whose count differs, the two
counts. Then the codes on each side that the other has not got at all, and
the totals by stage and by candidate. Measures only: what moved a count
belongs in the README, where it can be argued with.

    python docs/findings/stranger_install/findings_diff.py A.json B.json

Why the stage is in the key: `make`'s first count is the candidates' own
stages (`lot_assemble`, `laser_tag_evaluate`); its second adds the export's
(`themed_site_assemble`, `presentation_compose`, `lux_apply`,
`dispatch_handoff`), which all carry the PICKED candidate's id. Two tests that
picked different candidates differ by the export's whole share on two
candidates, and per candidate alone that reads as one candidate gaining 32
findings and another losing 33 (install test 9 against 8).

Every issue must carry `code` and `stage_id`; any other shape refuses. An
issue without a `candidate_id` is counted under "(none)".
"""
import collections
import json
import pathlib
import sys


def load(path):
    d = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if not isinstance(d, dict) or not isinstance(d.get("issues"), list):
        raise SystemExit("%s: no `issues` list (keys: %s)" % (path, sorted(d) if isinstance(d, dict) else type(d)))
    count = collections.Counter()
    for i, it in enumerate(d["issues"]):
        if not isinstance(it, dict) or "code" not in it or "stage_id" not in it:
            raise SystemExit(("%s: issue %d has no `code` or `stage_id`: %r" % (path, i, it))[:300])
        cand = (it.get("candidate_id") or "(none)").rsplit(".", 1)[-1]
        count[(it["stage_id"], cand, it["code"], bool(it.get("blocking")))] += 1
    return d["issues"], count


def totals(count, at):
    out = collections.Counter()
    for k, n in count.items():
        out[k[at]] += n
    return out


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    a_issues, a = load(sys.argv[1])
    b_issues, b = load(sys.argv[2])
    print("A: %s  %d issues" % (sys.argv[1], len(a_issues)))
    print("B: %s  %d issues" % (sys.argv[2], len(b_issues)))
    print()
    print("%-22s %-10s %-34s %5s %4s %4s %5s" % ("stage", "candidate", "code", "block", "A", "B", "B-A"))
    moved = 0
    keys = set(a) | set(b)
    for key in sorted(keys):
        if a[key] != b[key]:
            moved += 1
            print("%-22s %-10s %-34s %5s %4d %4d %+5d" % (key + (a[key], b[key], b[key] - a[key])))
    print()
    print("rows that moved: %d of %d" % (moved, len(keys)))
    for name, side, other in (("A", a, b), ("B", b, a)):
        only = sorted({k[2] for k in side} - {k[2] for k in other})
        print("codes only in %s: %s" % (name, ", ".join(only) or "none"))
    for label, at in (("stage", 0), ("candidate", 1)):
        ta, tb = totals(a, at), totals(b, at)
        print()
        for name in sorted(set(ta) | set(tb)):
            print("%-22s A %4d  B %4d  %+d" % (name, ta[name], tb[name], tb[name] - ta[name]))
    print("%-22s A %4d  B %4d  %+d" % ("total", sum(a.values()), sum(b.values()), sum(b.values()) - sum(a.values())))


if __name__ == "__main__":
    main()
