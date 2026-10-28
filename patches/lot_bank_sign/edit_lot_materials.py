"""Lot 0.134.0: the bank's outside pieces carry their genomes' material, so Lot's resolver finds the modules Zoo built.
Run in a Lot clone's root (on 0.133.0). Every anchor is asserted to occur exactly once; nothing is written on a miss.
"""
import pathlib

HERE = pathlib.Path(__file__).parent
R = pathlib.Path.cwd()


def edit(rel, pairs):
    p = R / rel
    t = p.read_bytes().decode("utf-8")
    crlf = "\r\n" in t
    t = t.replace("\r\n", "\n")
    for a, b in pairs:
        assert t.count(a) == 1, (rel, t.count(a), a[:80])
        t = t.replace(a, b)
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print(p, "edited")


edit("lot.py", [
('''                   # the gas station's price pylon (site_furniture.plan_pylons)
                   "price_pylon": "metal_painted",''',
 '''                   # the gas station's price pylon (site_furniture.plan_pylons)
                   "price_pylon": "metal_painted",
                   # A BANK'S OUTSIDE (0.132.0, 0.133.0), each its genome's
                   # default (0.134.0). Without a row a piece asked for
                   # `metal_painted`, Zoo built it under `_mmetal_painted` --
                   # a material not its species' own is another build -- and
                   # the resolver, asking the untagged name, found nothing: on
                   # the bank level both drive-up pieces stood as greybox
                   # (LOT_COVER_MODULE_MISSING) and the night drop would hang
                   # nothing. `tests/test_bank_outside_materials.py` holds
                   # each row to its genome.
                   "drive_up_canopy": "metal", "drive_up_tube": "metal",
                   "night_drop": "metal",'''),
])

dst = R / "tests" / "test_bank_outside_materials.py"
assert not dst.exists(), dst
dst.write_bytes((HERE / "test_bank_outside_materials.py").read_bytes())
print(dst, "written")
