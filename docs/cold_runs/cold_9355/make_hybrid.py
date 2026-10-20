"""The control for 9355's price: 9355's package with 1.116.0's booths put back -- the two street payphone GLBs, their
paint atlases, the office's indoor wall unit's atlas and the office room mesh it merges into, taken from 9351's walk
copy (the package's own bytes) -- so a price of it beside 9355's, in one session, sees the booths and nothing else.

    python docs/cold_runs/cold_9355/make_hybrid.py <9355 package> <9351 walk copy> <out dir>

Refuses if the out dir exists. Prints every file it removed and put back, then the differences between the hybrid
and 9355's package, which must be exactly those.
"""
import hashlib
import pathlib
import shutil
import sys

pkg, walk, out = (pathlib.Path(a) for a in sys.argv[1:4])
assert not out.exists(), "%s exists" % out
shutil.copytree(pkg, out)
REMOVE = ["cover/_tex/Payphone_256x1360_6bb4daf8_a552136e.png", "cover/_tex/Payphone_256x1360_e097b637_e15ab832.png",
          "lot/office/art/zoo/_tex/Payphone_256x1504_c2944116_ef5387a9.png"]
PUT = ["cover/_tex/Payphone_256x1182_59d22fe9_ce43d85e.png", "cover/_tex/Payphone_256x1182_d163dc4d_16b86ac3.png",
       "lot/office/art/zoo/_tex/Payphone_256x1326_3fd3eb7a_f31b154b.png",
       "cover/prop_payphone_delco_1997_01_w75_d50_h230.glb", "cover/prop_payphone_delco_1997_01_w75_d50_h230_n1.glb",
       "lot/office/merged/r210.res"]
for r in REMOVE:
    for p in (out / r, out / (r + ".import")):
        assert p.exists(), p
        p.unlink()
        print("removed", p.relative_to(out).as_posix())
for r in PUT:
    names = [r] + ([r + ".import"] if (walk / (r + ".import")).exists() else [])
    for n in names:
        shutil.copy2(walk / n, out / n)
        print("put back", n)


def files(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()[:12]
            for p in root.rglob("*") if p.is_file() and ".godot" not in p.parts}


a, b = files(pkg), files(out)
moved = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
print("the hybrid differs from 9355's package in %d files:" % len(moved))
for k in moved:
    print("   ", k, "9355" if k in a else "-", "hybrid" if k in b else "-")
