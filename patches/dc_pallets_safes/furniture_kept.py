"""Every spec the pallet migration touched: which named volumes 0.266.0 had that the clone lacks, and which it moved or
resized, the pile itself aside. The first draft of the migration refurnished the six delis' stockrooms to five pieces
fewer each (the pile counted as six; `level_design._room_volume_count`, 0.267.0); this is the instrument that saw it.

    python furniture_kept.py <clone>

Prints, per spec holding `loading_pallet_stack_1`: removed, added, moved. Exit 1 when anything but the pile was
removed. Measurements only.
"""
import json
import pathlib
import subprocess
import sys

C = pathlib.Path(sys.argv[1])
names = subprocess.run(["git", "-C", str(C), "diff", "--name-only", "--", "specs"], capture_output=True, text=True,
                       check=True).stdout.split()
KEYS = ("x", "y", "z", "size_x", "size_y", "size_z")


def vols(d):
    return {v["name"]: v for v in d.get("volumes") or [] if "name" in v}


bad = 0
seen = 0
for n in names:
    old = json.loads(subprocess.run(["git", "-C", str(C), "show", "HEAD:" + n], capture_output=True, text=True,
                                    encoding="utf-8", check=True).stdout)
    new = json.loads((C / n).read_text(encoding="utf-8"))
    o, w = vols(old), vols(new)
    if "loading_pallet_stack_1" not in w:
        continue
    seen += 1
    gone = sorted(k for k in set(o) - set(w) if k != "loading_pallet_stack")
    added = sorted(k for k in set(w) - set(o) if not k.startswith("loading_pallet_stack_"))
    moved = sorted(k for k in set(o) & set(w) if any(o[k].get(a) != w[k].get(a) for a in KEYS))
    bad += len(gone)
    print("%s removed %s added %s moved %s" % (n, gone, added, moved))
print("specs with a pile: %d; pieces removed besides the block: %d" % (seen, bad))
assert seen > 0, "no spec holds a pile: not the clone this reads"
sys.exit(1 if bad else 0)
