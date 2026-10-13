"""Two bakes' lightmap users compared (`lm_users.gd`'s dumps): the users both carry, keyed by node path
and sub-instance, and how many kept their rect and slice in the atlas, how many moved, and the users
only one carries. Measurement only.

    python docs/cold_runs/cold_9269/lm_users.py <a.txt> <b.txt>
"""
import sys


def _read(path):
    out = {}
    for line in open(path, encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if len(p) != 4:
            sys.exit("%s: a line of %d fields, not 4 -- not lm_users.gd's dump: %r" % (path, len(p), line[:80]))
        key = (p[0], int(p[1]))
        if key in out:
            sys.exit("%s: %s twice" % (path, key))
        out[key] = (tuple(float(v) for v in p[2].split()), int(p[3]))
    return out


def main():
    a, b = _read(sys.argv[1]), _read(sys.argv[2])
    both = sorted(set(a) & set(b))
    same = [k for k in both if a[k] == b[k]]
    slice_moved = [k for k in both if a[k][1] != b[k][1]]
    rect_moved = [k for k in both if a[k][1] == b[k][1] and a[k][0] != b[k][0]]
    print("users: %d in %s, %d in %s; %d in both" % (len(a), sys.argv[1], len(b), sys.argv[2], len(both)))
    print("of those in both: %d kept rect and slice, %d moved slice, %d kept the slice and moved the rect"
          % (len(same), len(slice_moved), len(rect_moved)))
    only_a, only_b = sorted(set(a) - set(b)), sorted(set(b) - set(a))
    print("only in the first: %d; only in the second: %d" % (len(only_a), len(only_b)))
    for k in only_b[:12]:
        print("  +", k[0], k[1], b[k])
    for k in only_a[:12]:
        print("  -", k[0], k[1], a[k])
    for k in (slice_moved + rect_moved)[:8]:
        print("  moved", k[0], k[1], a[k], "->", b[k])


if __name__ == "__main__":
    main()
