"""Lot 0.102.0: the site audit is kept in the gameplay manifest, not only
printed (roadmap 215).

`assemble` printed `site_audit.format_report` to the job log and stored
nothing, so no validation report and no cold run's findings diff ever counted
an `S_` code (cold run 9209's seed_9181: one MED and three INFO printed, none
in Level Factory's report). `site_audit.record` makes the block, and
`assemble` keeps it as `merged["site_audit"]`. Level Factory 0.163.0 reads it.

Anchored edits (every anchor once; refuses on a miss; nothing is written
until every anchor in every file matched):
- `site_audit.py`: the docstring's usage line, and `record` after
  `format_report`.
- `lot.py`: `assemble` keeps the result it prints.
New: `tests/test_site_audit_kept.py`, refused if it exists.
CHANGELOG and VERSION from `lot_site_audit_record/CHANGELOG_0.102.0.md`.

    python patch_lot_site_audit_record.py
    LOT_ROOT=<copy> python patch_lot_site_audit_record.py
"""
import os
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_site_audit_record"

SITE_AUDIT = [
    ("""Also runs automatically at the end of every lot.py assembly.
""",
     """Also runs automatically at the end of every lot.py assembly, which prints
the report and keeps it in the site's gameplay manifest as `site_audit`
(`record`, 0.102.0).
"""),
    (r'''    return "\n".join(lines)


def main(argv=None):
''',
     r'''    return "\n".join(lines)


def record(res):
    """The audit as the site's gameplay manifest keeps it (0.102.0, roadmap
    215): the mode, the counts, and one dict a finding with named fields --
    not the tuple's positions -- so a reader that cannot find one can say
    so. Until 0.102.0 `assemble` printed the report and kept nothing, so no
    validation report counted a finding."""
    return {"mode": res["mode"], "counts": dict(res["counts"]),
            "findings": [{"severity": sev, "code": code, "message": msg}
                         for sev, code, msg in res["findings"]]}


def main(argv=None):
'''),
]

LOT_PY = [
    ("""    import site_audit
    print(site_audit.format_report(site_audit.audit(site_spec)))
    merged["encounters"] = site_pacing.encounter_intel(site_spec, adj)
""",
     """    import site_audit
    audit_result = site_audit.audit(site_spec)
    print(site_audit.format_report(audit_result))
    # KEPT, NOT ONLY PRINTED (0.102.0, roadmap 215): the report went to the
    # job log and nowhere else, so no validation report ever counted a
    # finding it raised. Level Factory reads this block into its report.
    merged["site_audit"] = site_audit.record(audit_result)
    merged["encounters"] = site_pacing.encounter_intel(site_spec, adj)
"""),
]

EDITS = {
    "site_audit.py": SITE_AUDIT,
    "lot.py": LOT_PY,
}

NEW_TEST = pathlib.Path("tests") / "test_site_audit_kept.py"


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
    v = LOT / "VERSION"
    assert v.read_bytes() == b"Lot 0.101.0", v.read_bytes()
    staged = _stage(LOT, EDITS)
    test_dst = LOT / NEW_TEST
    assert not test_dst.exists(), test_dst
    test_src = (SRC / NEW_TEST.name).read_bytes()
    entry = (SRC / "CHANGELOG_0.102.0.md").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    cl = LOT / "CHANGELOG.md"
    data = cl.read_bytes()
    crlf, lf = data.count(b"\r\n"), data.count(b"\n")
    assert crlf in (0, lf), "CHANGELOG.md has mixed endings"
    text = data.decode("utf-8").replace("\r\n", "\n")
    assert text.startswith("## 0.101.0 - the responders' car is built and shipped, and stood nowhere"), text[:60]
    # Every anchor matched: now write.
    for p, raw in staged.items():
        p.write_bytes(raw)
    test_dst.write_bytes(test_src)
    new_cl = entry + text
    cl.write_bytes((new_cl.replace("\n", "\r\n") if crlf else new_cl).encode("utf-8"))
    v.write_bytes(b"Lot 0.102.0")
    print("Lot 0.101.0 -> 0.102.0")


if __name__ == "__main__":
    main()
