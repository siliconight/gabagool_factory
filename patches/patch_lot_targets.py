"""Lot 0.112.0: the guide's gameplay targets in the site audit (roadmap 230, the fourth adoption).

New `site_targets.py` (the measures from the drawn spec, the road graph's approaches and loops,
the focal points along the critical route) and `tests/test_site_targets.py`; one anchored edit in
`site_audit.py` (the findings appended after the adjacency's, before the counts), pinned by hash
and asserted once, nothing written on a miss; the file's own line endings kept. Applies on Lot
0.111.0. CHANGELOG and VERSION from `lot_targets/CHANGELOG_0.112.0.md`; `--suite-pending` leaves
RESULT_SUITE to `--fill`.

    python patches/patch_lot_targets.py --suite-pending && cd lot && python -m pytest -q
    python patches/patch_lot_targets.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_targets"
DRAFT = "--draft" in sys.argv
PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv
VERSION_WAS, VERSION = b"Lot 0.111.0", b"Lot 0.112.0"
CHANGELOG_HEAD = "## 0.111.0 - the guide's adjacency as audit findings\n"
SHA_AUDIT = "e73132f293256c49"
NEW = {"site_targets.py": "site_targets.py", "tests/test_site_targets.py": "test_site_targets.py"}

A_OLD = "    counts = {\"HIGH\": 0, \"MED\": 0, \"INFO\": 0}\n"
A_NEW = (
    "    # --- the guide's gameplay targets (0.112.0, roadmap 230): the level's\n"
    "    # numbers against the guide's starting ranges, every line INFO, so a\n"
    "    # reviewer reads them in the same report as the pair rules\n"
    "    try:\n"
    "        import site_targets\n"
    "        for sev, code, msg in site_targets.findings(site):\n"
    "            F((sev, code, msg))\n"
    "    except Exception as exc:                             # noqa: BLE001\n"
    "        F((\"INFO\", \"S_TARGETS\", f\"not measured: {exc}\"))\n"
    "\n"
    "    counts = {\"HIGH\": 0, \"MED\": 0, \"INFO\": 0}\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _fill():
    cl = LOT / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    value = (SRC / "result_suite.txt").read_bytes().decode("utf-8").replace("\r\n", "\n").strip()
    assert value and not value.endswith("."), "result_suite.txt must be one sentence without its final stop"
    text = _once(text, "RESULT_SUITE", value, "RESULT_SUITE")
    cl.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    print("Lot 0.112.0's changelog filled")


def main():
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.112.0.md").decode("utf-8")
    assert entry.startswith("## 0.112.0 - "), entry[:40]
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    p = LOT / "site_audit.py"
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA_AUDIT, ("site_audit.py is not the file this patch read", got)
    eol = _eol(raw, "site_audit.py")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    assert "site_targets" not in text, "already applied"
    text = _once(text, A_OLD, A_NEW, "the counts")
    for rel in NEW:
        assert not (LOT / rel).exists(), (rel, "already exists")
    cl = LOT / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:90]
    # Every pin and anchor matched: now write.
    for rel, name in NEW.items():
        (LOT / rel).write_bytes(_src(name))
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + cl_text).replace("\n", cl_eol.decode()).encode("utf-8"))
    (LOT / "VERSION").write_bytes(VERSION)
    print("Lot 0.111.0 -> 0.112.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
