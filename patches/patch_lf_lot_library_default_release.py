"""Level Factory 0.145.0: VERSION and the CHANGELOG entry for
`patch_lf_lot_library_default.py`.

    python patch_lf_lot_library_default_release.py
"""
import pathlib

LF = pathlib.Path(__file__).resolve().parent.parent / "level_factory"

ENTRY = '''## [0.145.0] - The lot library by default, wherever it can honour the brief

**The walker, 2026-10-06: yes.** Three of the breadth sweep's ten missions
named no `lot_library`, so each placed one generated shell N times and stood
no Empties, which draw from the library:
- restaurant_row_001: three copies;
- warehouse_yard_001: two copies;
- county_hospital_001: one building.

That is roadmap item 37's site that is one building several times.

**Not a blanket default, measured first.** `anchor_families`, the rule
`pick_lot` draws with, finds no family for `county_hospital` in today's
library: it has `clinic`, not `hospital`. A blanket default would have swapped
that mission's hospital for whatever the seed drew, which is the "bank block
with no bank" the anchor rule was written for. And `lot_for` places no lot
below two buildings, so a library there would change the brief's signature
and nothing else.

**The rule** (`apps/cli/commands/__init__.py`, `_default_lot_library`).
`batch create` gives a brief the workspace's Deli Counter `build/` when all of
these hold:
- the brief names no library;
- it asks for two or more buildings;
- the configured Deli Counter has a `build/` folder;
- its archetype anchors on a family there.

It prints which way it went for each mission. `"none"` keeps the generated
shell, and is stored as no library; `_brief_model` reads it that way too, so
it is never taken for a path.

**Decided once, where the brief enters the workspace,** and written into the
workspace's copy, which `plan`, `run` and the functional lock all read. A
mission already in a workspace keeps the brief it was graded on, which is why
the library stayed opt-in until now.

**For the breadth sweep's briefs:**
- restaurant_row_001 (`corner_deli`, 3) anchors on `deli`, and
  warehouse_yard_001 (`industrial_warehouse`, 2) on `warehouse`. Both gain
  varied buildings, and with them the Empties.
- county_hospital_001 (`county_hospital`, 1) keeps its generated building.

**Unproven until those three run cold.**

**Tests** (`tests/unit/test_lot_library_default.py`, 6). They cover the
anchored default, the hospital kept, one building left alone, a named library
and `"none"` obeyed, no Deli Counter configured, and `"none"` never read as a
path. The file cannot be collected on 0.144.4.

**Suite:** 1,939 collected: 1,924 passed, 14 skipped, 1 xfail. That is
0.144.4's 1,932, plus these 6, plus one `test_sibling_locator` case.

'''


def main():
    version = LF / "VERSION"
    changelog = LF / "CHANGELOG.md"
    v = version.read_bytes()
    assert v == b"0.144.4", v
    c = changelog.read_bytes()
    assert b"\r\n" not in c
    assert c.startswith(b"## [0.144.4] - "), c[:60]
    version.write_bytes(b"0.145.0")
    changelog.write_bytes(ENTRY.encode("utf-8") + c)
    print("Level Factory 0.145.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
