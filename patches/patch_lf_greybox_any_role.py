"""Level Factory 0.218.0: the greybox census refuses ANY greybox surface in a themed package (factory roadmap 168).

WHY NOW. `greybox_skin` refused on slabs only and REPORTED the rest, for a reason its docstring gave: a greybox
ladder was "a capability the toolchain does not have yet", and refusing would block every export on work nobody
had done. That reason has run out. Every class the census once reported now has an owner -- ladders a worldskin
pass (Level Factory 0.136.0), roof parapets wall slots the composer dresses (Deli Counter 0.177.0), vault ledges a
worldskin pass (Level Factory 0.217.0) -- and every package exported since 2026-10-10 that drew greybox at all drew
only vault ledges (40 censuses read off disk on 2026-10-19). On cold run 9322, the first export on 0.217.0, the
census reads 0 greybox surfaces (no role), where cold run 9321's, on 0.216.1, read the three vault ledges. So a greybox surface in a themed package now means a pass failed, or base geometry of a new
kind arrived without one; both are defects to see at the export rather than in a walk.

A DECISION THAT CAN BE CHANGED: `ExportProfile.require_no_greybox` (default True). Off, the census runs and reports
as before, refusing slabs only -- for a build that knowingly ships a new kind before its pass exists.

What it changes (anchored; each file pinned by hash; nothing written on a miss; CRLF-safe -- greybox_skin.py is CRLF):
  * packages/exporting/greybox_skin.py -- the docstring's new paragraph; `summary(report, any_role=True)`;
    `assert_skinned(export_dir, report, any_role=True)` keeps its slab message and, past it, refuses any greybox
    role through `_assert_no_greybox`, naming each role's count and the worst nodes.
  * packages/exporting/export.py -- `ExportProfile.require_no_greybox`; step 4.87 passes it; the error class's
    docstring.
  * tests/unit/test_greybox_skin_verdict.py (new; the verdict had no unit test): the slab rule as it was, a
    vault ledge refused, the profile's off switch, a clean themed package, an unthemed one, the summary.
  * VERSION 0.217.0 -> 0.218.0, CHANGELOG.

    python patches/patch_lf_greybox_any_role.py --tests   # the new test file only (prove it fails first)
    python patches/patch_lf_greybox_any_role.py           # everything
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LF = ROOT / "level_factory"
GB = LF / "packages" / "exporting" / "greybox_skin.py"
EX = LF / "packages" / "exporting" / "export.py"
SHA = {GB: "cf4b500f3dc7dfb1", EX: "edd4581dcc1c5f0f"}


def _apply(text, old, new, eol, what, count=1):
    o, n = old.replace("\n", eol), new.replace("\n", eol)
    assert text.count(o) == count, (what, text.count(o))
    return text.replace(o, n)


def _read(path):
    raw = path.read_bytes()
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    assert crlf == 0 or lf == 0, f"{path.name}: mixed endings ({crlf} CRLF, {lf} LF)"
    got = hashlib.sha256(raw).hexdigest()[:16]
    assert got == SHA[path], (f"{path.name} is not the file this patch read", got)
    return raw.decode("utf-8"), ("\r\n" if crlf else "\n")


DOC_OLD = r'''AREA IS TOTAL MESH SURFACE AREA, NOT VISIBLE AREA.'''
DOC_NEW = r'''SINCE 0.218.0 IT REFUSES ANY GREYBOX ROLE in a themed package (factory
roadmap 168), because the reason it reported the rest has run out: every class
that census reported now has an owner -- ladders a worldskin pass (0.136.0),
roof parapets wall slots the composer dresses (Deli Counter 0.177.0), vault
ledges a worldskin pass (0.217.0) -- and every package exported since
2026-10-10 that drew greybox at all drew only vault ledges. A greybox surface
in a themed package now means a pass failed or base geometry of a new kind
arrived without one, and both are defects to see at the export rather than in
a walk. `ExportProfile.require_no_greybox = False` reports without refusing
(slabs only, as before), for a build that knowingly ships a new kind early.

AREA IS TOTAL MESH SURFACE AREA, NOT VISIBLE AREA.'''

SUMMARY_OLD = r'''def summary(report: dict) -> str:
    """One line for the export log. Says which question it answered."""
'''
SUMMARY_NEW = r'''def summary(report: dict, any_role: bool = True) -> str:
    """One line for the export log. Says which question it answered."""
'''
SUMMARY_TAIL_OLD = r'''    return ("%d surface(s) on a greybox material (%s); slabs %d -- the class "
            "this gate refuses on"
            % (int(report["greybox_surfaces"]), parts or "none",
               int(report["slab_surfaces"])))
'''
SUMMARY_TAIL_NEW = r'''    if any_role:
        return ("%d surface(s) on a greybox material (%s), %d of them slabs; "
                "any one is refused (require_no_greybox)"
                % (int(report["greybox_surfaces"]), parts or "none",
                   int(report["slab_surfaces"])))
    return ("%d surface(s) on a greybox material (%s); slabs %d -- the class "
            "this gate refuses on"
            % (int(report["greybox_surfaces"]), parts or "none",
               int(report["slab_surfaces"])))
'''

ASSERT_OLD = r'''def assert_skinned(export_dir, report: dict) -> dict:
    """Raise `GreyboxSkinError` when a themed package draws a greybox slab.

    Only slabs. The reasoning, and the census that set the threshold, are in
    this module's docstring: a greybox ladder is an absent capability and
    refusing over it would block every export on work nobody has done.
    """
    if report.get("nothing_to_check"):
        return report
    bad = int(report.get("slab_surfaces", 0))
    if not bad:
        return report
'''
ASSERT_NEW = r'''def assert_skinned(export_dir, report: dict, any_role: bool = True) -> dict:
    """Raise `GreyboxSkinError` when a themed package draws a greybox slab, and
    -- with `any_role`, the default since 0.218.0 -- any greybox surface at all.

    A slab keeps its own message, because its cause is one pass. The reasoning
    for each threshold, and the census that set it, are in this module's
    docstring. `any_role=False` is the pre-0.218.0 verdict: slabs only.
    """
    if report.get("nothing_to_check"):
        return report
    bad = int(report.get("slab_surfaces", 0))
    if not bad:
        return _assert_no_greybox(export_dir, report) if any_role else report
'''

TAIL_OLD = r'''    lines.append("  full report: %s"
                 % (Path(export_dir) / REPORT_NAME))
    raise GreyboxSkinError("\n".join(lines))
'''
TAIL_NEW = r'''    lines.append("  full report: %s"
                 % (Path(export_dir) / REPORT_NAME))
    raise GreyboxSkinError("\n".join(lines))


def _assert_no_greybox(export_dir, report: dict) -> dict:
    """Raise `GreyboxSkinError` when a themed package draws any greybox
    surface (0.218.0). Called past the slab check, so slabs are 0 here."""
    bad = int(report.get("greybox_surfaces", 0))
    if not bad:
        return report
    roles = report.get("by_role") or {}
    lines = [
        "GREYBOX_IN_A_THEMED_PACKAGE: %d surface(s) still carry a greybox "
        "material (%s)" % (bad, ", ".join(
            "%s %d" % (name, int(row["surfaces"]))
            for name, row in sorted(roles.items())) or "no role named"),
        "  every kind of base geometry the census has met has an owner -- "
        "slabs, flights, ladders and vault ledges a worldskin pass, parapets "
        "a wall slot -- so this is a pass that failed (its own log line says "
        "which, and it push_error()s) or a new kind that arrived without one",
        "  a build that knowingly ships a new kind before its pass sets "
        "ExportProfile.require_no_greybox = False",
    ]
    for w in (report.get("worst") or [])[:6]:
        lines.append("    %s  on %s" % (w.get("node"), w.get("material")))
    lines.append("  full report: %s" % (Path(export_dir) / REPORT_NAME))
    raise GreyboxSkinError("\n".join(lines))
'''

EX_DOC_OLD = r'''    Refuses on SLABS only; see `packages.exporting.greybox_skin` for the
    census that set that threshold and for what it deliberately only
    reports."""
'''
EX_DOC_NEW = r'''    Refuses on any greybox surface in a themed package since 0.218.0
    (`ExportProfile.require_no_greybox`; on slabs only before it, and with it
    off); see `packages.exporting.greybox_skin` for the census that set each
    threshold."""
'''
EX_PROFILE_OLD = r'''    require_declared_drops: bool = True
'''
EX_PROFILE_NEW = r'''    require_declared_drops: bool = True
    #: Refuse a THEMED package that draws any greybox surface (0.218.0, factory
    #: roadmap 168; `packages/exporting/greybox_skin`). Every kind of base
    #: geometry the census has met has an owner now, so a greybox surface is a
    #: pass that failed or a new kind without one. Off, the census reports and
    #: refuses slabs only, as it did before -- for a build that knowingly ships
    #: a new kind before its pass exists.
    require_no_greybox: bool = True
'''
EX_CALL_OLD = r'''            print("[export] greybox skin: " + greybox_skin.summary(gb_report))
            greybox_skin.assert_skinned(export_dir, gb_report)
'''
EX_CALL_NEW = r'''            print("[export] greybox skin: " + greybox_skin.summary(
                gb_report, any_role=profile.require_no_greybox))
            greybox_skin.assert_skinned(export_dir, gb_report,
                                        any_role=profile.require_no_greybox)
'''

TEST = r'''"""The greybox census's verdict, on synthetic reports (0.218.0, factory roadmap 168).

`packages.exporting.greybox_skin.assert_skinned` refused on slabs only and reported the rest; since 0.218.0 it
refuses any greybox surface in a themed package, behind `ExportProfile.require_no_greybox` (default on). The
measurement half is `assets/godot/greybox_census.gd`; these pin what the verdict does with a report. The verdict
had no unit test before this file.

Run: python -m pytest -q tests/unit/test_greybox_skin_verdict.py
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from packages.exporting import greybox_skin as G  # noqa: E402
from packages.exporting.export import ExportProfile  # noqa: E402


def _report(by_role, slabs=0, themed=True, worst=()):
    n = sum(int(r["surfaces"]) for r in by_role.values())
    return {"schema": G.SCHEMA, "themed": themed, "greybox_surfaces": n, "slab_surfaces": slabs,
            "by_role": by_role, "worst": list(worst), "nothing_to_check": not themed}


#: cold run 9321's package, as its census read it: the three vault ledges, nothing else
LEDGES = _report({"gb_floor": {"area_m2": 49.73, "surfaces": 3}},
                 worst=[{"node": "Bake/Site/b0/GreyboxBase/VAULTLEDGE_1", "material": "gb_floor", "area_m2": 20.16}])


def test_a_greybox_slab_is_refused_as_it_was(tmp_path):
    rep = _report({"gb_floor": {"area_m2": 10.4, "surfaces": 8}}, slabs=8,
                  worst=[{"node": "Bake/Site/b0/GreyboxBase/slab_1_t0_0", "material": "gb_floor"}])
    for any_role in (True, False):
        with pytest.raises(G.GreyboxSkinError) as err:
            G.assert_skinned(tmp_path, rep, any_role=any_role)
        assert "GREYBOX_SLAB_IN_A_THEMED_PACKAGE: 8" in str(err.value)


def test_a_greybox_vault_ledge_is_refused(tmp_path):
    with pytest.raises(G.GreyboxSkinError) as err:
        G.assert_skinned(tmp_path, LEDGES)
    msg = str(err.value)
    assert "GREYBOX_IN_A_THEMED_PACKAGE: 3 surface(s)" in msg and "gb_floor 3" in msg
    assert "VAULTLEDGE_1" in msg and "require_no_greybox = False" in msg


def test_the_switch_off_reports_without_refusing(tmp_path):
    assert G.assert_skinned(tmp_path, LEDGES, any_role=False) is LEDGES
    assert "the class this gate refuses on" in G.summary(LEDGES, any_role=False)


def test_a_clean_themed_package_passes(tmp_path):
    clean = _report({})
    assert G.assert_skinned(tmp_path, clean) is clean
    assert "0 surface(s) on a greybox material (none), 0 of them slabs" in G.summary(clean)


def test_an_unthemed_package_is_never_refused(tmp_path):
    grey = _report({"gb_floor": {"area_m2": 900.0, "surfaces": 400}}, slabs=346, themed=False)
    assert G.assert_skinned(tmp_path, grey) is grey
    assert "no theming was applied" in G.summary(grey)


def test_the_summary_says_any_one_is_refused():
    assert "any one is refused (require_no_greybox)" in G.summary(LEDGES)


def test_the_profile_refuses_by_default():
    assert ExportProfile.__dataclass_fields__["require_no_greybox"].default is True
'''

CHANGELOG = '''## [0.218.0] - the greybox census refuses any greybox surface in a themed package

**Factory roadmap 168's last step.** `greybox_skin` refused on slabs only and reported the rest, because a greybox
ladder was "a capability the toolchain does not have yet". That has run out. Every class the census reported now
has an owner: ladders a worldskin pass (0.136.0), roof parapets wall slots the composer dresses (Deli Counter
0.177.0), and vault ledges a worldskin pass (0.217.0). Every package exported since 2026-10-10 that drew greybox at
all drew only vault ledges, across 40 censuses read off disk. On the factory's cold run 9322, the first export on
0.217.0, the census reads 0 greybox surfaces (no role), where cold run 9321's, on 0.216.1, read the three vault ledges.

**A decision that can be changed:** `ExportProfile.require_no_greybox`, default on. Off, the census reports and
refuses slabs only, as before, for a build that knowingly ships a new kind of base geometry before its pass.

### Changed
- `assert_skinned(export_dir, report, any_role=True)` keeps the slab message and, past it, refuses any greybox
  role (`GREYBOX_IN_A_THEMED_PACKAGE`), naming each role's count and the worst nodes. `summary` says which verdict
  it applied. Export step 4.87 passes the profile's switch.

### Added
- `tests/unit/test_greybox_skin_verdict.py` (7; the verdict had no unit test): the slab rule as it was, a vault
  ledge refused, the switch off, a clean themed package, an unthemed one, the summary, the default.

'''


def write_tests():
    p = LF / "tests" / "unit" / "test_greybox_skin_verdict.py"
    assert not p.exists(), f"{p.name} exists"
    p.write_text(TEST, encoding="utf-8", newline="\n")
    print("wrote level_factory/tests/unit/test_greybox_skin_verdict.py")


def main(argv):
    assert ("@@" + "9322@@") not in CHANGELOG + __doc__, "fill cold run 9322's census before applying"
    if "--tests" in argv:
        write_tests()
        return 0
    gb, gb_eol = _read(GB)
    assert "_assert_no_greybox" not in gb, "already applied"
    gb = _apply(gb, DOC_OLD, DOC_NEW, gb_eol, "the docstring")
    gb = _apply(gb, SUMMARY_OLD, SUMMARY_NEW, gb_eol, "summary's signature")
    gb = _apply(gb, SUMMARY_TAIL_OLD, SUMMARY_TAIL_NEW, gb_eol, "summary's return")
    gb = _apply(gb, ASSERT_OLD, ASSERT_NEW, gb_eol, "assert_skinned")
    gb = _apply(gb, TAIL_OLD, TAIL_NEW, gb_eol, "the slab raise")
    ex, ex_eol = _read(EX)
    ex = _apply(ex, EX_DOC_OLD, EX_DOC_NEW, ex_eol, "ExportGreyboxSkinError")
    ex = _apply(ex, EX_PROFILE_OLD, EX_PROFILE_NEW, ex_eol, "the profile")
    ex = _apply(ex, EX_CALL_OLD, EX_CALL_NEW, ex_eol, "step 4.87")
    v = LF / "VERSION"
    assert v.read_text(encoding="utf-8").strip() == "0.217.0", v.read_text(encoding="utf-8")
    cl = LF / "CHANGELOG.md"
    rawc = cl.read_bytes()
    assert b"\r\n" not in rawc, "CHANGELOG.md is LF"
    text = rawc.decode("utf-8")
    assert text.startswith("## [0.217.0]"), text[:40]
    GB.write_bytes(gb.encode("utf-8"))
    EX.write_bytes(ex.encode("utf-8"))
    v.write_text("0.218.0", encoding="utf-8")
    cl.write_bytes((CHANGELOG + text).encode("utf-8"))
    write_tests()
    print("Level Factory 0.218.0 applied: the census refuses any greybox role in a themed package; test, VERSION, CHANGELOG")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
