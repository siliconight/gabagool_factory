"""Level Factory 0.163.0: Lot's site audit reaches the validation report
(roadmap 215).

Lot 0.102.0 keeps its site audit as `site_audit` in the site's gameplay
manifest; until then the findings went to Lot's job log only, so this report
and every cold run's findings diff carried no `S_` code (cold run 9209's
seed_9181: one MED and three INFO printed, none in the report).
`adapters.lot.normalize_validation` reads each finding as a non-blocking
issue; no block, or one it cannot read, is LOT_SITE_AUDIT_UNREAD.

Anchored edits (every anchor once; refuses on a miss; nothing is written
until every anchor in every file matched):
- `adapters/lot/__init__.py`: `LOT_SITE_AUDIT_SEVERITY`, `_site_audit_issues`,
  and the call at the end of `normalize_validation`.
- `tests/fixtures/repos/lot/lot.py`: the stub writes a clean block.
- `tests/real_tools/test_real_adapters.py`: `test_real_lot` checks the real
  block is read.
New: `tests/unit/test_site_audit_report.py`, refused if it exists.
CHANGELOG and VERSION from `lf_site_audit/CHANGELOG_0.163.0.md`.

    python patch_lf_site_audit.py
    LF_ROOT=<copy> python patch_lf_site_audit.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_site_audit"

CHANGELOG_HEAD = "## [0.162.1] - The light bake keeps the responders' car dynamic\n"

ADAPTER = [
    ("""LOT_PACING_STATUSES = LOT_PACING_WITHIN + LOT_PACING_OUTSIDE
""",
     """LOT_PACING_STATUSES = LOT_PACING_WITHIN + LOT_PACING_OUTSIDE

#: THE SITE AUDIT'S SEVERITIES (`lot/site_audit.py`, "severities HIGH / MED /
#: INFO"), in this model's words (0.163.0, roadmap 215). The audit is
#: report-only, so nothing it says blocks, HIGH included.
#: `tests/unit/test_site_audit_report.py` reads Lot's source and fails when it
#: writes a severity not named here.
LOT_SITE_AUDIT_SEVERITY = {"HIGH": "major", "MED": "moderate", "INFO": "info"}


def _site_audit_issues(block, source) -> list[dict]:
    \"\"\"Lot's `site_audit` block (Lot 0.102.0) as issues, one a finding.

    No block, or a shape this cannot read, is LOT_SITE_AUDIT_UNREAD rather
    than nothing: an absent audit and a clean one must not look alike.\"\"\"
    def unread(why: str) -> dict:
        return {"code": "LOT_SITE_AUDIT_UNREAD", "severity": "moderate",
                "category": "combat_structure", "message": why,
                "blocking": False, "raw_source_path": str(source)}

    if block is None:
        return [unread("Lot's gameplay manifest carries no site_audit block "
                       "(Lot before 0.102.0 printed the audit to its job log only)")]
    found = block.get("findings") if isinstance(block, dict) else None
    if not isinstance(found, list):
        return [unread(f"Lot's site_audit block has no findings list: {block!r:.160}")]
    out: list[dict] = []
    for raw in found:
        sev = raw.get("severity") if isinstance(raw, dict) else None
        code = raw.get("code") if isinstance(raw, dict) else None
        if (not isinstance(sev, str) or sev not in LOT_SITE_AUDIT_SEVERITY
                or not isinstance(code, str) or not code):
            out.append(unread(f"a site_audit finding this adapter cannot read: {raw!r:.160}"))
            continue
        out.append({
            "code": code,
            "severity": LOT_SITE_AUDIT_SEVERITY[sev],
            "category": "combat_structure",
            "message": str(raw.get("message", "")),
            "blocking": False,  # report-only, HIGH included
            "raw_source_path": str(source),
        })
    return out
"""),
    ("""                "blocking": sev == "blocker",
                "raw_source_path": str(gameplay),
            })
        return issues
""",
     """                "blocking": sev == "blocker",
                "raw_source_path": str(gameplay),
            })

        # THE SITE AUDIT (0.163.0, roadmap 215): the site-level design grammar
        # Lot runs at the end of every assembly -- exfil shape, responder
        # pressure, safe anchors, leg rhythm, street crossings. Until Lot
        # 0.102.0 it went to the job log only, so no report and no cold run's
        # findings diff ever counted it (cold run 9209: one MED and three INFO
        # printed, no `S_` code here). Report-only: nothing it says blocks.
        issues.extend(_site_audit_issues(data.get("site_audit"), gameplay))
        return issues
"""),
]

STUB = [
    ("""        "tactical": {"findings": []},
""",
     """        "tactical": {"findings": []},
        "site_audit": {"mode": "heist", "counts": {"HIGH": 0, "MED": 0, "INFO": 0},
                       "findings": []},
"""),
]

REAL = [
    ("""    # Pacing is surfaced as a non-blocking estimate.
    issues = adapter.normalize_validation(outs)
    assert all(not i["blocking"] or i["severity"] == "blocker" for i in issues)
""",
     """    # Pacing is surfaced as a non-blocking estimate.
    issues = adapter.normalize_validation(outs)
    assert all(not i["blocking"] or i["severity"] == "blocker" for i in issues)
    # The site audit is read, not missing (0.163.0, roadmap 215): gs_heist,
    # Lot's calibration site, carries INFO findings only.
    codes = [i["code"] for i in issues]
    assert "LOT_SITE_AUDIT_UNREAD" not in codes, codes
    assert any(c.startswith("S_") for c in codes), codes
"""),
]

EDITS = {
    str(pathlib.Path("adapters") / "lot" / "__init__.py"): ADAPTER,
    str(pathlib.Path("tests") / "fixtures" / "repos" / "lot" / "lot.py"): STUB,
    str(pathlib.Path("tests") / "real_tools" / "test_real_adapters.py"): REAL,
}

NEW_TEST = pathlib.Path("tests") / "unit" / "test_site_audit_report.py"


def _stage(root, edits):
    """{path: bytes}: every file's new content, every anchor matched once,
    endings kept; raises before anything is written."""
    staged = {}
    for rel, pairs in edits.items():
        p = root / rel
        d = p.read_bytes()
        crlf, lf = d.count(b"\r\n"), d.count(b"\n")
        assert crlf in (0, lf), (rel, "mixed endings")
        t = d.decode("utf-8").replace("\r\n", "\n")
        for old, new in pairs:
            n = t.count(old)
            assert n == 1, (rel, n, old[:70])
            t = t.replace(old, new)
        staged[p] = (t.replace("\n", "\r\n") if crlf else t).encode("utf-8")
    return staged


def main():
    v = (LF / "VERSION").read_bytes()
    assert v == b"0.162.1", repr(v)
    staged = _stage(LF, EDITS)
    test_dst = LF / NEW_TEST
    assert not test_dst.exists(), test_dst
    test_src = (SRC / NEW_TEST.name).read_bytes()
    entry = (SRC / "CHANGELOG_0.163.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    c = (LF / "CHANGELOG.md").read_bytes()
    crlf, lf = c.count(b"\r\n"), c.count(b"\n")
    assert crlf in (0, lf), "CHANGELOG.md has mixed endings"
    text = c.decode("utf-8").replace("\r\n", "\n")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:80]
    # Every anchor matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    test_dst.write_bytes(test_src)
    new = entry + text
    (LF / "CHANGELOG.md").write_bytes((new.replace("\n", "\r\n") if crlf else new).encode("utf-8"))
    (LF / "VERSION").write_bytes(b"0.163.0")
    print("Level Factory 0.162.1 -> 0.163.0")


if __name__ == "__main__":
    main()
