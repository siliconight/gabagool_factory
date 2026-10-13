"""What a refurnish would move in the library, spec by spec, after the doors widen (roadmap 197; Deli Counter
0.214.0).

    python docs/findings/door_widths/refurnish_delta.py <deli_counter dir> [<git ref for the doors before>]

`migrate_furnish_recipes.migrate` strips every piece `level_design.furnish` wrote and furnishes again; the
library is tested to be its fixed point (`test_wall_backing`, `test_club_fixtures`). Widening a door can move
what furnish puts beside it. This runs `migrate` in memory on every library spec in the given directory and
prints, for each spec it changes, the furnished pieces before and after, the pieces lost and gained by name
stem, and how the spec's walkable doors changed against the given git ref (default HEAD): the authored
widths that moved, and the width-less doors whose default moved under them. A spec with no rooms is never
furnished and is skipped, as the test skips it. Prints what it measured and stops; nothing is written.
"""
import collections
import json
import pathlib
import re
import subprocess
import sys

DC = pathlib.Path(sys.argv[1]).resolve()
REF = sys.argv[2] if len(sys.argv) > 2 else "HEAD"
sys.path.insert(0, str(DC))

import migrate_furnish_recipes as MF   # noqa: E402

STEM = re.compile(r"^(?P<stem>[a-z_]+?)_r[0-9a-f]{8}_\d+(_\d+)?$")


def _doors(d):
    out = []
    for w in (d.get("ext_walls") or []) + (d.get("partitions") or []):
        for o in w.get("openings") or []:
            if o.get("kind") == "door":
                out.append(o.get("width"))
    return out


def _furnished(d):
    tags = {MF.level_design._room_tag(r) for r in d.get("rooms") or []}
    return [v for v in d.get("volumes") or [] if MF.furnished_by_this_pass(v, tags)]


def _stems(vols):
    return collections.Counter((STEM.match(v["name"]).group("stem") if STEM.match(v["name"]) else v["name"])
                               for v in vols)


def _before(name):
    rel = "specs/%s.json" % name
    run = subprocess.run(["git", "-C", str(DC), "show", "%s:%s" % (REF, rel)], capture_output=True, text=True,
                         encoding="utf-8")
    return json.loads(run.stdout) if run.returncode == 0 else None


def main():
    moved = 0
    lost = gained = 0
    for p in sorted((DC / "specs").glob("*.json")):
        if p.name.startswith("lf_"):
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        if not d.get("rooms"):
            continue
        before = json.dumps(d, sort_keys=True)
        was = _furnished(d)
        MF.migrate(d)
        if json.dumps(d, sort_keys=True) == before:
            continue
        moved += 1
        now = _furnished(d)
        a, b = _stems(was), _stems(now)
        lost += sum((a - b).values())
        gained += sum((b - a).values())
        old = _before(d["name"])
        old_doors = _doors(old) if old else None
        authored = sum(1 for x, y in zip(old_doors or [], _doors(d)) if x is not None and x != y)
        widthless = sum(1 for x in _doors(d) if x is None)
        print("%-44s furnished %4d -> %4d  lost %s  gained %s  | doors re-widthed %d, width-less %d%s" % (
            d["name"], len(was), len(now), dict(a - b) or "{}", dict(b - a) or "{}", authored, widthless,
            "" if old else "  (no %s copy)" % REF))
    print("%d spec(s) move under a refurnish: %d furnished piece(s) lost, %d gained" % (moved, lost, gained))


if __name__ == "__main__":
    main()
