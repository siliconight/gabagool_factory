"""Count the Empties a drawn site placed, by design.

    python count_terrace.py <site.site.drawn.json> [...]

Reads `blockers[]` entries carrying `empty: true` and their `archetype` --
the shape Lot writes (read off cold run 9159's seed_9080 site before this
was written). Prints houses placed, designs seen, each design's count, the
most any one design appears, and adjacent repeats in list order. A file with
no `blockers` list, or none marked empty, is refused rather than read as an
empty terrace.
"""
import collections
import json
import sys

rc = 0
for p in sys.argv[1:]:
    d = json.load(open(p, encoding="utf-8"))
    bl = d.get("blockers")
    if not isinstance(bl, list):
        print("REFUSED %s: no blockers list (keys %s)" % (p, sorted(d)[:12]))
        rc = 2
        continue
    houses = [b for b in bl if isinstance(b, dict) and b.get("empty") is True]
    if not houses or any("archetype" not in b for b in houses):
        print("REFUSED %s: %d blocker(s), %d marked empty, archetype missing on some"
              % (p, len(bl), len(houses)))
        rc = 2
        continue
    seq = [b["archetype"] for b in houses]
    c = collections.Counter(seq)
    adj = sum(1 for a, b in zip(seq, seq[1:]) if a == b)
    print("%s\n  %d house(s), %d design(s); most of one design %d; adjacent repeats %d"
          % (p, len(seq), len(c), max(c.values()), adj))
    print("  " + "  ".join("%s:%d" % (k.replace("gs_empty_rowhome_", ""), v) for k, v in sorted(c.items())))
sys.exit(rc)
