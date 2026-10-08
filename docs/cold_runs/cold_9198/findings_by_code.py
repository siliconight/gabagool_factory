"""Print the validation findings of a cold run whose count moved against the
previous run's, by code, with each finding's own message -- so every item a
diff line counts can be attributed before anything is patched against it.

    python docs/cold_runs/cold_9198/findings_by_code.py <N> <PREV> <mission> [CODE ...]

Reads `workspaces/cold-<N>-ws/.level_factory/validation/<mission>.json`, the
file the driver's findings step counts. Prints what it found and stops.
"""
import collections
import json
import sys


def findings(n, mission):
    p = f"workspaces/cold-{n}-ws/.level_factory/validation/{mission}.json"
    d = json.load(open(p, encoding="utf-8"))
    out = []

    def walk(o, path):
        if isinstance(o, dict):
            if isinstance(o.get("code"), str):
                out.append((o["code"], path, o))
            for k, v in o.items():
                walk(v, path + "/" + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, path + "[%d]" % i)
    walk(d, "")
    return out


def main():
    n, prev, mission = sys.argv[1], sys.argv[2], sys.argv[3]
    want = set(sys.argv[4:])
    a = collections.Counter(c for c, _p, _o in findings(prev, mission))
    b = findings(n, mission)
    bc = collections.Counter(c for c, _p, _o in b)
    for code in sorted(set(a) | set(bc)):
        if a[code] == bc[code] or (want and code not in want):
            continue
        print("== %s  %d -> %d" % (code, a[code], bc[code]))
        for c, path, o in b:
            if c == code:
                msg = o.get("message") or o.get("detail") or ""
                print("   %s :: %s" % (path, str(msg)[:400]))


if __name__ == "__main__":
    main()
