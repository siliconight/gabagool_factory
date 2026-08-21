#!/usr/bin/env python3
"""patch_mpt_clamp.py -- keep the five new grammars inside the texel-density band.

pixelcoat holds max/min of 512/meters_per_tile to 3.0 across all materials.
paper_neutral (0.6) and carbon_neutral (0.5) sat below the existing floor and
took the spread to 6.0. This clamps the five new profiles into the range the
other 55 already occupy -- it does not widen the invariant to fit my guess.

  --check / (apply) / --revert / --selftest
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MATS = os.path.join(ROOT, "pixelcoat", "profiles", "materials")
SIDE = ".pre_mpt"
NEW_IDS = {"laminate_neutral", "paper_neutral", "carbon_neutral",
           "tar_neutral", "vegetation_neutral"}

MODE = "apply"
for a in sys.argv[1:]:
    if a in ("--check", "--revert", "--selftest"):
        MODE = a[2:]
    else:
        print("unknown argument %r" % a)
        sys.exit(2)


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def load(p):
    with open(p, "r", encoding="utf-8") as fh:
        return fh.read()


if MODE == "revert":
    n = 0
    for fn in sorted(os.listdir(MATS)):
        if fn.endswith(SIDE):
            side = os.path.join(MATS, fn)
            tgt = side[: -len(SIDE)]
            shutil.copyfile(side, tgt)
            os.remove(side)
            print("  restored %s" % rel(tgt))
            n += 1
    print("REVERTED -- %d file(s)" % n)
    sys.exit(0)

profiles = {}
for fn in sorted(os.listdir(MATS)):
    if not fn.endswith(".json"):
        continue
    p = os.path.join(MATS, fn)
    text = load(p)
    data = json.loads(text)
    profiles[fn[:-5]] = {"path": p, "text": text, "data": data,
                         "mpt": float(data.get("meters_per_tile", 1.0))}

if not profiles:
    print("REFUSING TO CONCLUDE -- no material profiles read")
    sys.exit(2)

existing = {k: v["mpt"] for k, v in profiles.items() if k not in NEW_IDS}
mine = {k: v["mpt"] for k, v in profiles.items() if k in NEW_IDS}
if len(mine) != len(NEW_IDS):
    print("REFUSING -- expected %d new profiles, found %d: %s"
          % (len(NEW_IDS), len(mine), sorted(mine)))
    sys.exit(1)

lo, hi = min(existing.values()), max(existing.values())
all_now = list(existing.values()) + list(mine.values())
print("meters_per_tile across %d profiles" % len(profiles))
print("  the other %d occupy      %.3f .. %.3f   spread %.3f"
      % (len(existing), lo, hi, (512.0 / lo) / (512.0 / hi)))
print("  including my five        %.3f .. %.3f   spread %.3f"
      % (min(all_now), max(all_now),
         (512.0 / min(all_now)) / (512.0 / max(all_now))))
print("")
band = (512.0 / lo) / (512.0 / hi)
if abs(band - 3.0) > 0.01:
    print("REFUSING -- the pre-existing band is %.3f, not the 3.0 the test asserts."
          % band)
    print("            My assumption about the invariant is wrong; look before editing.")
    sys.exit(1)

plan = []
print("%-22s %8s %8s" % ("profile", "now", "clamped"))
print("-" * 42)
for k in sorted(NEW_IDS):
    cur = profiles[k]["mpt"]
    new = min(max(cur, lo), hi)
    print("%-22s %8.3f %8.3f%s"
          % (k, cur, new, "" if new == cur else "   <-- change"))
    if new == cur:
        continue
    data = dict(profiles[k]["data"])
    data["meters_per_tile"] = new
    want = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    plan.append((profiles[k]["path"], profiles[k]["text"], want))

print("")
if MODE == "selftest":
    vals = [v["mpt"] for v in profiles.values()]
    spread = (512.0 / min(vals)) / (512.0 / max(vals))
    if abs(spread - 3.0) > 0.01:
        print("SELFTEST FAILED -- spread is %.3f, expected 3.0" % spread)
        sys.exit(1)
    out = [k for k in NEW_IDS if not (lo <= profiles[k]["mpt"] <= hi)]
    if out:
        print("SELFTEST FAILED -- outside the band: %s" % ", ".join(sorted(out)))
        sys.exit(1)
    # falsification: the check must FAIL on a value outside the band
    probe = vals + [lo / 2.0]
    if abs(((512.0 / min(probe)) / (512.0 / max(probe))) - 3.0) <= 0.01:
        print("SELFTEST FAILED -- the spread check accepted an out-of-band value")
        sys.exit(1)
    print("SELFTEST OK -- all %d profiles sit in %.3f..%.3f, spread %.3f, and the"
          % (len(profiles), lo, hi, spread))
    print("               check was shown to FAIL on a deliberately out-of-band value")
    sys.exit(0)

if not plan:
    print("NOTHING TO DO -- already inside the band")
    sys.exit(0)
if MODE == "check":
    print("CHECK OK -- %d file(s) would change" % len(plan))
    sys.exit(0)

for path, old_text, new_text in plan:
    if not os.path.exists(path + SIDE):
        with open(path + SIDE, "w", encoding="utf-8", newline="") as fh:
            fh.write(old_text)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(new_text)
    print("  wrote %s" % rel(path))
print("")
print("APPLIED -- %d file(s). Rebuild so the packs pick up the new"
      " meters_per_tile." % len(plan))
