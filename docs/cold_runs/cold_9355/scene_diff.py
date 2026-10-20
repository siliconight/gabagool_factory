"""Compare two Godot text scenes with the ids Godot draws at random on each save normalised away: a node's
`unique_id=<n>`, and resource ids of the form `<n>_<5 chars>` (`id="7_vdul5"`, `ExtResource("7_vdul5")`,
`SubResource(...)`), each renumbered in order of first appearance. Prints how many lines differ after that, and the
first few.

    python docs/cold_runs/cold_9355/scene_diff.py <a.tscn> <b.tscn> [...pairs]

A file whose only differences are those ids reads 0.
"""
import difflib
import re
import sys

UID = re.compile(r"unique_id=\d+")
RID = re.compile(r'(?<=["(])(\d+_[a-z0-9]{5}|[A-Za-z0-9]+_[a-z0-9]{5})(?=[")])')


def norm(path):
    text = open(path, encoding="utf-8").read()
    text = UID.sub("unique_id=X", text)
    seen = {}

    def rid(m):
        return seen.setdefault(m.group(1), "R%d" % len(seen))

    return RID.sub(rid, text).splitlines()


args = sys.argv[1:]
for a, b in zip(args[::2], args[1::2]):
    la, lb = norm(a), norm(b)
    diff = [d for d in difflib.unified_diff(la, lb, lineterm="", n=0) if d[:1] in "+-" and d[:3] not in ("+++", "---")]
    print("%s: %d lines differ once the save's random ids are set aside" % (b, len(diff)))
    for d in diff[:6]:
        print("    " + d[:160])
