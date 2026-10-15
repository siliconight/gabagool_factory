"""Lot 0.124.0 -- an isolated building is a major finding, not a log line (factory roadmap 178).

`site_tactical.analyze` has reported a building no path or street reaches since the graph existed, as a
`warnings` string that `lot.py` prints as `[lot]   WARNING: isolated buildings: ...` and nothing reads
(roadmap 178: "fires always, blocks nothing"). Lot 0.77.0 fixed the graph, and the warning now reads zero on
every site a current Level Factory writes -- 0 of 320 on disk (`docs/findings/open_items_remeasure/lot_intel_178.py`),
the four exceptions a 2026-09-23 experiment whose door paths predate the `building` key. By item 59's rule a
reading that is zero across the library may graduate. This emits the same fact as a structured finding in
`report["findings"]` -- `LOT_ISOLATED_BUILDING`, severity `major` -- which Level Factory's Lot adapter already
ingests from `tactical.findings` and `pick.py` already counts (`MAJOR = ("major", "critical", "blocker")`): a
candidate with an unreachable building loses the pick to one without, and the finding stands in the report. Not
a blocker: a run whose every candidate has one still ships, saying so. The warning string stays.

New file beside this patch: lot/tests/test_isolated_finding.py (it cannot pass on 0.123.0's tree: no finding).
Every anchor is asserted once and every touched file is pinned by sha16.

    python patches/patch_lot_isolated_finding.py
    (cd lot && python -m pytest -q)
"""
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOT = ROOT / "lot"

SHA = {
    LOT / "site_tactical.py": "7487475fb7a137b8",
    LOT / "VERSION": "5ad8dfc71dbe4f0f",
    LOT / "CHANGELOG.md": "d02fa2b112631394",
}

CHANGELOG = """## 0.124.0 - an isolated building is a major finding, not a log line

**Factory roadmap 178** ("the instruments report and nothing blocks"). `site_tactical.analyze` has said
"buildings with no declared path-route from 'b0': ..." in `report["warnings"]` since the graph existed, and
`lot.py` printed it as a WARNING that nothing downstream read. 0.77.0 fixed the graph the warning read (the
street joins the buildings on it), and today it reads zero on every site a current Level Factory writes: 0 of
320 on disk (the factory's `docs/findings/open_items_remeasure/lot_intel_178.py`), the four exceptions a
2026-09-23 experiment whose door paths predate the `building` key. A reading that is zero across the library
may graduate (the factory's item 59).

### Added
- **`LOT_ISOLATED_BUILDING`**, severity `major`, in `report["findings"]` whenever `intel.isolated_buildings`
  is not empty -- the same fact as the warning, in the shape Level Factory's Lot adapter already ingests from
  `tactical.findings` and its pick already counts: a candidate with a building no path or street reaches loses
  the pick to one without, and the finding stands in the report. Not a blocker: a run whose every candidate has
  one still ships, saying so; graduating it further is a decision for a run of cold runs on today's graph. The
  warning string and the `[lot] WARNING` line stay. `report["findings"]` is always present now, `[]` when the
  site is whole, so a reader that wants the list never has to guess from its absence.
- `tests/test_isolated_finding.py`: a site with no road and no building paths reports every building but the
  root as isolated, with one major finding naming them; the street-graph fixture reports none and no finding;
  the finding carries the adapter's four fields.

"""

EDITS = [
    (LOT / "site_tactical.py",
     '        "intel": {},\n        "warnings": [],\n    }\n',
     '        "intel": {},\n        "warnings": [],\n'
     '        # STRUCTURED FINDINGS (0.124.0): what Level Factory\'s Lot adapter\n'
     '        # ingests from `tactical.findings` and its pick counts by severity.\n'
     '        # Always a list, so a reader never infers "none" from an absent key.\n'
     '        "findings": [],\n    }\n'),
    (LOT / "site_tactical.py",
     '    if isolated:\n'
     '        report["warnings"].append(\n'
     '            f"buildings with no declared path-route from \'{root}\': "\n'
     '            f"{\', \'.join(isolated)}")\n',
     '    if isolated:\n'
     '        report["warnings"].append(\n'
     '            f"buildings with no declared path-route from \'{root}\': "\n'
     '            f"{\', \'.join(isolated)}")\n'
     '        # THE SAME FACT AS A FINDING (0.124.0, factory roadmap 178). The\n'
     '        # warning above fired on 65 of 79 sites before 0.77.0 taught the\n'
     '        # graph the street, and on 0 of 320 after; a reading that is zero\n'
     '        # across the library may graduate (the factory\'s item 59). MAJOR,\n'
     '        # not a blocker: the pick counts it, so a candidate with a building\n'
     '        # nobody can reach loses to one without, and a run whose every\n'
     '        # candidate has one still ships, saying so. The four sites on disk\n'
     '        # that still read it are a 2026-09-23 experiment whose door paths\n'
     '        # predate the `building` key, not a reachable defect.\n'
     '        report["findings"].append({\n'
     '            "code": "LOT_ISOLATED_BUILDING",\n'
     '            "severity": "major",\n'
     '            "category": "combat_structure",\n'
     '            "message": (\n'
     '                f"{len(isolated)} building(s) no declared path or shared "\n'
     '                f"street reaches from \'{root}\': {\', \'.join(isolated)}. "\n'
     '                f"A building nobody can walk to is not part of the level; "\n'
     '                f"give it a door path to the sidewalk or a path from a "\n'
     '                f"building that has one."),\n'
     '        })\n'),
    (LOT / "VERSION", "Lot 0.123.0", "Lot 0.124.0"),
    (LOT / "CHANGELOG.md", "## 0.123.0 - an urban street plants a city block's trees: one every 30 ft",
     CHANGELOG + "## 0.123.0 - an urban street plants a city block's trees: one every 30 ft"),
]


def sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def main():
    assert (LOT / "tests" / "test_isolated_finding.py").exists(), "write the test first"
    for p, want in SHA.items():
        assert b"\r\n" not in p.read_bytes(), f"{p} is CRLF; the patch assumes LF"
        got = sha16(p)
        assert got == want, f"{p}: sha16 {got} != {want}; re-ground before applying"
    texts = {}
    for p, old, new in EDITS:
        t = texts.get(p) or p.read_text(encoding="utf-8")
        assert t.count(old) == 1, (p.name, old[:70])
        texts[p] = t.replace(old, new)
    for p, t in texts.items():
        p.write_text(t, encoding="utf-8", newline="\n")
    print("Lot 0.124.0 applied: LOT_ISOLATED_BUILDING; now the suite")


if __name__ == "__main__":
    sys.exit(main())
