"""A roof is a horizontal plate, and three species lists say it is not.

    python patch_zoo_roof_plate.py --check    # verify targets, write nothing
    python patch_zoo_roof_plate.py            # apply
    python patch_zoo_roof_plate.py --revert   # restore from the .pre_roofplate sidecars

THE OTHER HALF OF THE LADDER FIX. `patch_dc_roof_voids.py` makes Deli Counter
emit `voids` on the roof slot. On its own it does NOTHING, because nothing in
Zoo reads them for a roof. Measured 2026-08-09 -- three independent gates, and
`roof` is in none of them:

    deli_counter/roofs.py   _slot() emits no `voids` key at all
    zoo core/kit.py         PLATE_ROLES = ("floor", "ceiling")
                            -> no depth_cm and no void tag in the module stem
    zoo core/arch.py        PLATE_SPECIES = ("floor", "ceiling")
                            -> plate_parts never called; collision emitted

THE PROOF IS IN THE SHIPPED FILENAMES:

    floor_rockay_01_w4000_d1300.glb           width + depth
    ceiling_rockay_01_w2600_d1200_v38cf53     width + depth + VOID TAG
    roof_rockay_01_w4000.glb                  width only

A 40x30 roof and a 40x20 roof produce the same stem. That is the `module_stem`
width-only collision this repo has already paid for twice -- latent while
`roof_mode` is `footprint` (one roof per building), live the moment a building
roofs `per_room`.

WHAT CHANGED, and why it is three edits and not one:

  * `roof` moves out of `_SOLID` into `PLATE_SPECIES`. Its holes are in x/y --
    a hatch, not a doorway -- which is what `plate_parts` was written for.
  * `roof` joins `PLATE_ROLES`, so the kit keys it on BOTH axes and on its
    voids, the way it already keys floors and ceilings.
  * `PLATE_COLLIDES = ("roof",)` is NEW, and it is the point. `PLATE_SPECIES`
    carried two independent facts at once -- "holes are in x/y" and "emits no
    collision" -- because floors and ceilings happen to be both. A roof is the
    first species that is a plate AND collides; the conflation had nowhere to
    put it, so `roof` sat in `_SOLID` and got neither. A ceiling declares
    `collision: none` and means it; the roof slot declares `collision: trimesh`
    and now gets it, tiled AROUND the void instead of over it.

MEASURED, on bank_branch_a04. Deli Counter cut the ladder's through-hole in
`slab_col_2-colonly` -- corners 15.45 / 16.55 / -10.90, confirmed by
`probe_glb_void.py`, which reads OPEN there and COVERED one storey down. The
same probe on `roof_rockay_01_w4000.glb` reads COVERED, 4 triangles, and the
file carries a node named `Roof-colonly` -- which Godot names `Roof`, character
for character the blocker in walkbot.json.

TESTS. 7 new in `tests/test_plate.py`, 5 of which fail on the unpatched tree.
The other two exercise `plate_parts` directly, which was never broken -- the bug
was that `roof` never reached it, and saying so is worth more than a number.
The clean case is asserted too: a roof with no hatch still comes out as one
`Panel`, byte for byte.

NOT VERIFIED HERE. `recipes/_arch.py` imports the bpy layer, so its collision
branch was read, not executed. `tests/test_arch.py` and
`tests/test_structural_species.py` could not run in the sandbox either (missing
genome and recipe files). Run Zoo's full suite after applying, and rebuild one
building before believing the geometry.

REFUSES on any target whose bytes are not what this patch was written against --
a whole-file SHA-256, so a drifted file cannot be half-patched.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

SIDECAR = ".pre_roofplate"
def _factory_root() -> Path:
    """The directory holding `factory.manifest.json`, found by walking up.

    Was `Path(__file__).resolve().parent`, which required this file to sit AT
    the factory root and kept eleven scripts pinned there. Walking up means it
    works from `tools/`, `patches/` or anywhere else, and still returns the
    root when it IS the root -- the first candidate tested is its own
    directory.

    The manifest is the marker because it is the one file that defines this
    place and exists in no tool repo. `.git` would match every tool repo.
    """
    here = Path(__file__).resolve()
    for base in (here.parent, *here.parents):
        if (base / "factory.manifest.json").is_file():
            return base
    return here.parent


ROOT = _factory_root()

TARGETS = [
    {
        "rel": 'zoo/zoo_keeper/core/arch.py',
        "pre_sha": 'cc9c0f14fdb47dd55a96b7deda962d65e6e970b206f1e1278f7bbd344972a970',
        "post_sha": '6ad34d5727a98b6e522492480dd3b5726ba838449df93391082f06653a968cea',
        "pre_bytes": 18394, "post_bytes": 19505,
        "hunks": [
            ('#: skin ended up capping a stairwell -- see PLATE_SPECIES below.\n#: `prop` is a vault, a counter, a desk, a crate stack: a solid object\n#: built to a Deli Counter volume\'s exact dims. It is not architecture and\n#: nothing walks through it.\n_SOLID = ("wall", "wallEnd", "roof", "prop")\n\n#: Species built as a horizontal PLATE rather than a standing slab. Their holes\n#: are in x/y and are cut by :func:`plate_parts`; ``void_for`` returns None for\n#: them, which it also did by falling off the end -- saying so is the point,\n#: because "solid by accident" is how a ceiling skin ended up capping a\n#: stairwell.\nPLATE_SPECIES = ("floor", "ceiling")\n\n_EPS = 1e-6\n\n# clean part-name prefixes (species.title() would mangle the camelCase wallEnd)\n',
             '#: skin ended up capping a stairwell -- see PLATE_SPECIES below.\n#: `prop` is a vault, a counter, a desk, a crate stack: a solid object\n#: built to a Deli Counter volume\'s exact dims. It is not architecture and\n#: nothing walks through it.\n_SOLID = ("wall", "wallEnd", "prop")\n\n#: Species built as a horizontal PLATE rather than a standing slab. Their holes\n#: are in x/y and are cut by :func:`plate_parts`; ``void_for`` returns None for\n#: them, which it also did by falling off the end -- saying so is the point,\n#: because "solid by accident" is how a ceiling skin ended up capping a\n#: stairwell.\nPLATE_SPECIES = ("floor", "ceiling", "roof")\n\n#: Plates that STILL emit collision. `PLATE_SPECIES` used to carry two\n#: independent facts at once -- "its holes are in x/y" and "it emits no\n#: collision" -- because floors and ceilings happen to be both. A roof is the\n#: first species that is a plate AND collides, and the conflation had nowhere\n#: to put it, so `roof` sat in `_SOLID` instead and got neither the void\n#: tiling nor a way to say it wanted collision.\n#:\n#: Measured 2026-08-09 on `bank_branch_a04`: Deli Counter cut the ladder\'s\n#: through-hole in its own roof slab (`slab_col_2-colonly`, corners 15.45 /\n#: 16.55 / -10.90) and Zoo laid `roof_rockay_01_w4000.glb` over it as one\n#: solid 40 x 30 panel carrying `Roof-colonly`. The walk bot stalled against a\n#: collider named `Roof` at the slab underside -- a ladder climbing a full\n#: storey into roof. That is the same failure `plate_parts` was written for,\n#: one surface up.\n#:\n#: A floor or ceiling skin declares `collision: "none"` and means it; the roof\n#: slot declares `collision: "trimesh"` and now gets it, tiled around the void\n#: rather than over it.\nPLATE_COLLIDES = ("roof",)\n\n_EPS = 1e-6\n\n# clean part-name prefixes (species.title() would mangle the camelCase wallEnd)\n'),
        ],
    },
    {
        "rel": 'zoo/zoo_keeper/core/kit.py',
        "pre_sha": '42780feb4cddb46c8086b0d286b48793e48068bba5854da65e5af487c4396fd4',
        "post_sha": '0c65b40815489ff719a592cdc6312dbe40720f6d0118419caf2a1436178bd316',
        "pre_bytes": 15721, "post_bytes": 15729,
        "hunks": [
            ('\n\n#: Roles built as a horizontal PLATE. Their footprint varies on BOTH axes, so\n#: width alone does not identify a module -- see :func:`module_stem`.\nPLATE_ROLES = ("floor", "ceiling")\n\n#: Roles whose geometry is a hole in a standing slab, cut to the slot\'s own\n#: ``fit.openings``. Their WIDTH is already in the filename; the aperture is\n#: not, which is what :func:`opening_tag` fixes.\n',
             '\n\n#: Roles built as a horizontal PLATE. Their footprint varies on BOTH axes, so\n#: width alone does not identify a module -- see :func:`module_stem`.\nPLATE_ROLES = ("floor", "ceiling", "roof")\n\n#: Roles whose geometry is a hole in a standing slab, cut to the slot\'s own\n#: ``fit.openings``. Their WIDTH is already in the filename; the aperture is\n#: not, which is what :func:`opening_tag` fixes.\n'),
        ],
    },
    {
        "rel": 'zoo/zoo_keeper/recipes/_arch.py',
        "pre_sha": '7b44290fe61097261d2cd31ba6e398ba46e7df6fb075575801f47bea83d78338',
        "post_sha": '953d07043e2eac847a47316531c5442d10e1bd6d81fde3e7e3a0e79df0bb1008',
        "pre_bytes": 5360, "post_bytes": 5865,
        "hunks": [
            ('    for name, center, size in visual:\n        bm = geometry.new_bm()\n        geometry.add_box(bm, center, size)\n        part(bm, f"{root}_{name}")\n    if species not in arch.PLATE_SPECIES:\n        # From `slab`, NOT `visual`. The collider is the solid wall it has\n        # always been -- recessing the fields must not carve notches a player\n        # can stand in, and must not change one collision box on any build\n        # before this one.\n',
             '    for name, center, size in visual:\n        bm = geometry.new_bm()\n        geometry.add_box(bm, center, size)\n        part(bm, f"{root}_{name}")\n    if species not in arch.PLATE_SPECIES or species in arch.PLATE_COLLIDES:\n        # PLATE-NESS AND COLLISION ARE TWO FACTS, and this line used to test\n        # one for the other. A floor or ceiling skin emits none because Deli\n        # Counter\'s trimesh slab under it is authoritative and already holed;\n        # a ROOF is a plate by geometry and still has to be stood on, and its\n        # slot says `collision: "trimesh"`. Tiling comes from `plate_parts`\n        # above, so these boxes now go around the void instead of over it.\n        #\n        # From `slab`, NOT `visual`. The collider is the solid wall it has\n        # always been -- recessing the fields must not carve notches a player\n        # can stand in, and must not change one collision box on any build\n        # before this one.\n'),
        ],
    },
    {
        "rel": 'zoo/tests/test_plate.py',
        "pre_sha": '6bc38006d026c1f1bfc5ac4be31dcf7681309465a634821319507759e47bc6c8',
        "post_sha": '9ad30d03e8418e113506715952b2897bea05a0fa024ddcc878b2d5ccbecf46fa',
        "pre_bytes": 7067, "post_bytes": 12006,
        "hunks": [
            ('    plan = kit.plan_kit({"slots": [_slot("ceiling", [10.0, 8.0, 0.02], v)]},\n                        theme="rockay")\n    assert plan["modules"][0]["voids"] == v\n    assert plan["modules"][0]["depth_cm"] == 800\n',
             '    plan = kit.plan_kit({"slots": [_slot("ceiling", [10.0, 8.0, 0.02], v)]},\n                        theme="rockay")\n    assert plan["modules"][0]["voids"] == v\n    assert plan["modules"][0]["depth_cm"] == 800\n\n\n# --------------------------------------------------------------------------- #\n# THE ROOF IS A PLATE TOO (2026-08-09)\n#\n# It was in `_SOLID` beside `wall` and `prop`, so it got no void tiling, no\n# depth in its stem and no void tag -- and it emitted collision, which is what\n# made it a wall rather than a cosmetic fault. Measured on `bank_branch_a04`:\n# DC cut the ladder\'s through-hole in `slab_col_2-colonly` (corners 15.45 /\n# 16.55 / -10.90) and Zoo laid a solid 40 x 30 `roof_rockay_01_w4000.glb` over\n# it carrying `Roof-colonly`. The walk bot stalled against a collider named\n# `Roof` at the slab underside.\n# --------------------------------------------------------------------------- #\n\ndef test_a_roof_is_a_plate_and_not_a_standing_slab():\n    """Its holes are in x/y -- a hatch, not a doorway."""\n    assert "roof" in arch.PLATE_SPECIES\n    assert "roof" not in arch._SOLID\n    assert arch.void_for("roof", 40.0, 0.3) is None      # no x/z opening\n\n\ndef test_a_roof_still_collides_and_a_ceiling_still_does_not():\n    """The two facts `PLATE_SPECIES` used to conflate, asserted apart. A\n    ceiling skin declares `collision: none`; a roof slot declares `trimesh`."""\n    assert "roof" in arch.PLATE_COLLIDES\n    assert "ceiling" not in arch.PLATE_COLLIDES\n    assert "floor" not in arch.PLATE_COLLIDES\n\n\ndef test_a_roof_tiles_around_its_void_instead_of_over_it():\n    parts = arch.plate_parts(40.0, 30.0, 0.3,\n                             [{"x0": 15.45, "y0": 10.9,\n                               "x1": 16.55, "y1": 12.2}])\n    assert len(parts) > 1, "a solid panel is exactly the bug"\n    # nothing survives over the hole\n    for _n, c, s in parts:\n        over_x = c[0] - s[0] / 2 < 16.0 < c[0] + s[0] / 2\n        over_y = c[1] - s[1] / 2 < 11.55 < c[1] + s[1] / 2\n        assert not (over_x and over_y), "a part still covers the ladder"\n    # and the plate\'s outer footprint is still exact\n    assert _area(parts) < 40.0 * 30.0\n\n\ndef test_the_clean_roof_is_still_one_panel_byte_for_byte():\n    """THE CASE THAT MUST NOT CHANGE. Every roof without a hatch has to come\n    out of this exactly as it did before -- "it cut the hole in the broken\n    building" cannot tell you it did not also punch one in the other 133."""\n    assert arch.plate_parts(40.0, 30.0, 0.3, None) == [\n        ("Panel", (0.0, 0.0, 0.0), (40.0, 30.0, 0.3))]\n    assert arch.plate_parts(40.0, 30.0, 0.3, []) == [\n        ("Panel", (0.0, 0.0, 0.0), (40.0, 30.0, 0.3))]\n\n\ndef test_two_roofs_of_one_width_are_no_longer_the_same_module():\n    """`roof_rockay_01_w4000` was the stem for a 40x30 roof AND a 40x20 one:\n    plates were keyed on both axes, and `roof` was not a plate. That is the\n    `module_stem` width-only collision this repo has already paid for twice.\n    Latent while `roof_mode` is `footprint` (one roof per building); live the\n    moment a building roofs `per_room`."""\n    plan = kit.plan_kit({"slots": [_slot("roof", [40.0, 30.0, 0.3]),\n                                   _slot("roof", [40.0, 20.0, 0.3])]},\n                        theme="rockay")\n    stems = {m["stem"] for m in plan["modules"]}\n    assert len(stems) == 2, stems\n    assert "roof_rockay_01_w4000_d3000" in stems\n    assert "roof_rockay_01_w4000_d2000" in stems\n\n\ndef test_two_roofs_with_different_hatches_get_different_filenames():\n    hatch_n = [{"x0": -1.0, "y0": -1.0, "x1": 0.1, "y1": 0.3}]\n    hatch_e = [{"x0": 15.45, "y0": 10.9, "x1": 16.55, "y1": 12.2}]\n    plan = kit.plan_kit({"slots": [_slot("roof", [40.0, 30.0, 0.3], hatch_n),\n                                   _slot("roof", [40.0, 30.0, 0.3], hatch_e)]},\n                        theme="rockay")\n    stems = sorted(m["stem"] for m in plan["modules"])\n    assert len(set(stems)) == 2, stems\n    assert all("_v" in s for s in stems), stems\n\n\ndef test_the_bank_branch_ladder_reaches_the_roof(): \n    """THE REGRESSION, with the shipped numbers. 40 x 30 roof, ladder at spec\n    (16, 12) width 0.5 facing S, so `ladder_geom.through_hole` puts the cut at\n    x 15.45..16.55, y 10.90..12.20. The climb column the capsule needs is\n    CLIMB_STANDOFF +/- its radius off the face."""\n    void = {"x0": 15.45, "y0": 10.9, "x1": 16.55, "y1": 12.2}\n    plan = kit.plan_kit({"slots": [_slot("roof", [40.0, 30.0, 0.3], [void])]},\n                        theme="rockay")\n    m = plan["modules"][0]\n    assert m["voids"] == [void]\n    assert m["voids_tag"], "no void tag means two hatches share one filename"\n    parts = arch.plate_parts(40.0, 30.0, 0.3, m["voids"])\n    standoff, capsule_r = 0.5, 0.35\n    for x in (16.0 - 0.25, 16.0, 16.0 + 0.25):\n        for y in (12.0 - (standoff + capsule_r), 12.0 - standoff,\n                  12.0 - (standoff - capsule_r)):\n            for _n, c, s in parts:\n                assert not (c[0] - s[0] / 2 < x < c[0] + s[0] / 2\n                            and c[1] - s[1] / 2 < y < c[1] + s[1] / 2), \\\n                    f"the roof still covers the climb column at ({x}, {y})"\n'),
        ],
    },
]

NEW_FILES = {}


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _write(p: Path, text: str) -> None:
    p.write_text(text, encoding="utf-8", newline="")


def check(verbose: bool = True):
    """(ok, todo) -- every target read and hashed, nothing written."""
    ok, todo = True, []
    for t in TARGETS:
        p = ROOT / t["rel"]
        if not p.is_file():
            print(f"  MISSING   {t['rel']}")
            ok = False
            continue
        cur = _read(p)
        got = _sha(cur)
        if got == t["post_sha"]:
            print(f"  already   {t['rel']}")
            continue
        if got != t["pre_sha"]:
            print(f"  DRIFTED   {t['rel']}")
            print(f"            expected {t['pre_bytes']} bytes "
                  f"sha {t['pre_sha'][:16]}")
            print(f"            found    {len(cur.encode('utf-8'))} bytes "
                  f"sha {got[:16]}")
            ok = False
            continue
        todo.append((p, t, cur))
        if verbose:
            print(f"  ready     {t['rel']}  ({len(t['hunks'])} hunk(s), "
                  f"{t['pre_bytes']} -> {t['post_bytes']} bytes)")
    for rel in NEW_FILES:
        p = ROOT / rel
        state = "exists (will not overwrite)" if p.is_file() else "will create"
        print(f"  new file  {rel}  -- {state}")
    return ok, todo


def apply() -> int:
    print("checking every target before writing anything")
    ok, todo = check()
    if not ok:
        print("\nREFUSED. At least one target is not the file this patch was "
              "written against; nothing has been written.")
        return 1
    for p, t, cur in todo:
        side = p.with_name(p.name + SIDECAR)
        if not side.exists():
            _write(side, cur)
        out = cur
        for old, new in t["hunks"]:
            if out.count(old) != 1:
                print(f"REFUSED mid-file on {t['rel']} -- anchor not unique. "
                      f"Restore from {side.name} and re-read.")
                return 1
            out = out.replace(old, new, 1)
        if _sha(out) != t["post_sha"]:
            print(f"REFUSED on {t['rel']} -- result does not match the "
                  f"expected post-image. Nothing further written.")
            return 1
        _write(p, out)
        print(f"  patched   {t['rel']}  ({side.name} written)")
    for rel, body in NEW_FILES.items():
        p = ROOT / rel
        if p.is_file():
            print(f"  kept      {rel} (already present, not overwritten)")
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        _write(p, body)
        print(f"  created   {rel}")
    print("\nNow run, from zoo/:  python -m pytest tests -q")
    print("Expected: test_plate.py 21 passed (14 before, +7).")
    return 0


def revert() -> int:
    n = 0
    for t in TARGETS:
        p = ROOT / t["rel"]
        side = p.with_name(p.name + SIDECAR)
        if not side.is_file():
            continue
        body = _read(side)
        if _sha(body) != t["pre_sha"]:
            print(f"  REFUSED   {t['rel']} -- {side.name} is not the "
                  f"pre-image this patch recorded")
            continue
        _write(p, body)
        side.unlink()
        n += 1
        print(f"  reverted  {t['rel']}")
    for rel in NEW_FILES:
        p = ROOT / rel
        if p.is_file() and _sha(_read(p)) == _sha(NEW_FILES[rel]):
            p.unlink()
            print(f"  removed   {rel}")
    print(f"\n{n} file(s) restored.")
    return 0


def main(argv):
    if "--check" in argv:
        ok, _ = check()
        print("\nOK to apply." if ok else "\nNOT ok to apply.")
        return 0 if ok else 1
    if "--revert" in argv:
        return revert()
    return apply()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
