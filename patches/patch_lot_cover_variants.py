"""Lot 0.103.0: a parked box truck wears one of Zoo's four fleets (roadmap 219 note 5). See
`lot_cover_variants/CHANGELOG_0.103.0.md`.

Zoo 1.92.0 draws `box_truck` in four invented Delco fleets, chosen by a slot's `variant`
(`module_variants: 4`). Lot already carries a cover record's `variant` into the site's slot and
asks for the variant's module before the plain one (0.90.0, the dumpster's hauler). What it did
not do is give a cover piece a variant. Now `site_cover` gives every box truck one, from its
species and where it stands, so a lot's trucks are not one fleet four times.

Anchored edits to `site_cover.py`, every anchor once, nothing written until all match:
  `import zlib`; `COVER_VARIANTS` after `COVER_SPECIES`; `Cover.variant`; both records carry it
  when it is not 0; `_species_piece` picks it.
New: `tests/test_cover_variants.py`. CHANGELOG and VERSION from `lot_cover_variants/`.

    python patch_lot_cover_variants.py [--suite-pending]
    LOT_ROOT=<copy> python patch_lot_cover_variants.py --draft

`--draft` lets the changelog's RESULT_ placeholders through, against a LOT_ROOT copy only.
`--suite-pending` lets exactly RESULT_SUITE through into the repo, filled in by hand after the
suite runs and before the commit.
"""
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_cover_variants"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv

EDITS = [
    ("import math\nfrom dataclasses import dataclass, field\n",
     "import math\nimport zlib\nfrom dataclasses import dataclass, field\n"),
    ('    ("simple_car", 1.75, 4.3, 1.45),\n)\n',
     '    ("simple_car", 1.75, 4.3, 1.45),\n)\n'
     "#: HOW MANY LOOKS A COVER SPECIES COMES IN (0.103.0): Zoo's genome `module_variants`, which a\n"
     "#: slot's `variant` picks among. A box truck is one of Zoo 1.92.0's four invented fleets\n"
     "#: (`box_truck_forms.FLEETS`); a species not named here has one look and no variant. A Zoo that\n"
     "#: cannot draw a variant still builds the plain module, which `cover_module_refs` falls back\n"
     "#: to (0.90.0), so this table and Zoo's genome need not land in the same instant.\n"
     'COVER_VARIANTS = {"box_truck": 4}\n'),
    ("    width: float = 0.0\n    depth: float = 0.0\n\n    def __post_init__(self):\n",
     "    width: float = 0.0\n    depth: float = 0.0\n"
     "    #: which of the species' looks it wears (0.103.0); 0 is the plain one\n"
     "    variant: int = 0\n\n    def __post_init__(self):\n"),
    ('            out.update({"species": self.species, "yaw": self.yaw,\n'
     '                        "width": self.width, "depth": self.depth})\n'
     "        return out\n",
     '            out.update({"species": self.species, "yaw": self.yaw,\n'
     '                        "width": self.width, "depth": self.depth})\n'
     "            if self.variant:\n"
     '                out["variant"] = int(self.variant)\n'
     "        return out\n"),
    ('            out.update({"species": self.species, "yaw": self.yaw,\n'
     '                        "dims": [self.width, self.depth, self.height]})\n'
     "        return out\n",
     '            out.update({"species": self.species, "yaw": self.yaw,\n'
     '                        "dims": [self.width, self.depth, self.height]})\n'
     "            # its look, non-zero only, as a dumpster's hauler is: a record written before\n"
     "            # 0.103.0 and a variant-0 piece read the same\n"
     "            if self.variant:\n"
     '                out["variant"] = int(self.variant)\n'
     "        return out\n"),
    ("def _species_piece(name, spot, sp, yaw, line):\n"
     "    sname, w, d, h = sp\n"
     "    sx, sy = footprint(w, d, yaw)\n"
     "    return Cover(name=name, x=spot[0], y=spot[1], size=max(sx, sy), height=h,\n"
     '                 breaks=f"{line[0]} -> {line[1]}", span=line[4],\n'
     "                 species=sname, yaw=yaw, size_x=sx, size_y=sy,\n"
     "                 width=w, depth=d)\n",
     "def cover_variant(species, spot):\n"
     '    """The look a piece of ``species`` standing at ``spot`` wears: one of\n'
     "    `COVER_VARIANTS[species]`, from the species and where it stands, so a lot's\n"
     "    trucks differ and a re-run of one site stands the same truck in the same\n"
     '    place. 0 for a species with one look."""\n'
     "    n = COVER_VARIANTS.get(species, 1)\n"
     "    if n <= 1:\n"
     "        return 0\n"
     '    key = f"{species},{round(float(spot[0]), 2)},{round(float(spot[1]), 2)}"\n'
     '    return zlib.crc32(key.encode("utf-8")) % n\n'
     "\n\n"
     "def _species_piece(name, spot, sp, yaw, line):\n"
     "    sname, w, d, h = sp\n"
     "    sx, sy = footprint(w, d, yaw)\n"
     "    return Cover(name=name, x=spot[0], y=spot[1], size=max(sx, sy), height=h,\n"
     '                 breaks=f"{line[0]} -> {line[1]}", span=line[4],\n'
     "                 species=sname, yaw=yaw, size_x=sx, size_y=sy,\n"
     "                 width=w, depth=d, variant=cover_variant(sname, spot))\n"),
]


def main():
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    v = (LOT / "VERSION").read_bytes().strip()
    assert v == b"Lot 0.102.2", v
    entry = (SRC / "CHANGELOG_0.103.0.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## 0.103.0 - "), entry[:40]
    if not DRAFT:
        left = entry.replace("RESULT_SUITE", "") if SUITE_PENDING else entry
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    p = LOT / "site_cover.py"
    raw = p.read_bytes()
    crlf = b"\r\n" in raw
    t = raw.decode("utf-8").replace("\r\n", "\n")
    assert "COVER_VARIANTS" not in t, "already applied"
    for old, new in EDITS:
        assert t.count(old) == 1, ("site_cover.py", t.count(old), old[:60])
        t = t.replace(old, new)
    test = LOT / "tests" / "test_cover_variants.py"
    assert not test.exists(), test
    cl = LOT / "CHANGELOG.md"
    text = cl.read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert text.startswith("## 0.102.2 - "), text[:40]
    # every anchor matched: now write, keeping the source's own line endings
    p.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    test.write_bytes((SRC / "test_cover_variants.py").read_bytes().replace(b"\r\n", b"\n"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + text).encode("utf-8"))
    (LOT / "VERSION").write_bytes(b"Lot 0.103.0")
    print("Lot 0.102.2 -> 0.103.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
