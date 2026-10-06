"""Two lit name signs, two tables: what each library building's door box says
(Zoo `storefront_names`, from the business string Deli Counter stamps on the
anchor in `<shell>.lights.json`) against the names its street band can be
dealt (Level Factory `sign_family` -> Pixelcoat `delco_1997` pool, names
only, as LF 0.146.0 deals).

Prints what it measured: per building, the door's kind and text, the band's
family and pool, and whether the door's text is in the band's pool. Says
nothing about which facade either sign hangs on -- that is not in these
files.
"""
import collections
import glob
import json
import os
import sys

ROOT = r"C:\Projects\gabagool_studios\gabagool_factory"
sys.path.insert(0, os.path.join(ROOT, "zoo"))
sys.path.insert(0, os.path.join(ROOT, "level_factory"))
from zoo_keeper.core import storefront_names as SN          # noqa: E402
from apps.cli import commands as LF                          # noqa: E402

profile = json.load(open(os.path.join(ROOT, "pixelcoat", "profiles", "signs", "delco_1997.json"),
                         encoding="utf-8"))["signs"]
named = [s for s in profile if s.get("text")]


def pool(family):
    p = [s["text"] for s in named if family in (s.get("families") or [])]
    return p or [s["text"] for s in named if "default" in (s.get("families") or [])], bool(p)


rows = []
for f in sorted(glob.glob(os.path.join(ROOT, "deli_counter", "build", "*.lights.json"))):
    shell = os.path.basename(f)[: -len(".lights.json")]
    d = json.load(open(f, encoding="utf-8"))
    found = []

    def walk(o):
        if isinstance(o, dict):
            if "business" in o:
                found.append(o["business"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(d)
    if not found:
        continue
    door = SN.sign_for(found[0])
    fam = LF.sign_family(shell)
    names, own = pool(fam)
    rows.append((shell, door["kind"], door["text"], fam if own else f"{fam}->default", names,
                 door["text"] in names))

by = collections.defaultdict(list)
for r in rows:
    by[(r[1], r[3])].append(r)
print(f"{len(rows)} buildings with a door box\n")
print(f"{'door kind':10s} {'band family':22s} {'n':>3s} {'door text in band pool':>22s}  example")
for (kind, fam), rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
    agree = sum(1 for r in rs if r[5])
    ex = rs[0]
    print(f"{kind:10s} {fam:22s} {len(rs):3d} {agree:>14d} of {len(rs):<5d}  "
          f"{ex[0]}: door {ex[2]!r}; band from {ex[4][:4]}{'...' if len(ex[4]) > 4 else ''}")
print(f"\nagree: {sum(1 for r in rows if r[5])} of {len(rows)}")
