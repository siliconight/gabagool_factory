"""Lot 0.111.0: the guide's adjacency as audit findings (roadmap 230, beside Level Factory 0.176.0).

New `site_adjacency.py` (the categories, the relation, the matrix, the pair rules Lot can judge)
and `tests/test_site_adjacency.py`; one anchored edit in `site_audit.py` (the findings appended
before the counts), pinned by hash and asserted once, nothing written on a miss; the file's own
line endings kept. Applies on Lot 0.110.0. CHANGELOG and VERSION from
`lot_adjacency/CHANGELOG_0.111.0.md`; `--suite-pending` leaves RESULT_SUITE to `--fill`.

    python patches/patch_lot_adjacency.py --suite-pending && cd lot && python -m pytest -q
    python patches/patch_lot_adjacency.py --fill
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LOT = pathlib.Path(os.environ.get("LOT_ROOT") or HERE.parent / "lot")
SRC = HERE / "lot_adjacency"
DRAFT = "--draft" in sys.argv
PENDING = "--suite-pending" in sys.argv
FILL = "--fill" in sys.argv
VERSION_WAS, VERSION = b"Lot 0.110.0", b"Lot 0.111.0"
CHANGELOG_HEAD = "## 0.110.0 - the tree belt in clusters, in three forms\n"
SHA_AUDIT = "9eff610f1aae25cc"
NEW = {"site_adjacency.py": "site_adjacency.py", "tests/test_site_adjacency.py": "test_site_adjacency.py"}

A_OLD = "    counts = {\"HIGH\": 0, \"MED\": 0, \"INFO\": 0}\n"
A_NEW = (
    "    # --- the guide's adjacency (0.111.0, roadmap 230): what the pairs of lot\n"
    "    # buildings are to each other, by category and by the pair rules; MED where\n"
    "    # the guide wants an explanation, INFO where it says why a pair is good\n"
    "    try:\n"
    "        import site_adjacency\n"
    "        for sev, code, msg in site_adjacency.findings(site):\n"
    "            F((sev, code, msg))\n"
    "    except Exception as exc:                             # noqa: BLE001\n"
    "        F((\"INFO\", \"S_ADJACENCY\", f\"not judged: {exc}\"))\n"
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
    print("Lot 0.111.0's changelog filled")


def main():
    if DRAFT and not os.environ.get("LOT_ROOT"):
        sys.exit("refusing: --draft is for a LOT_ROOT copy, never the repo")
    if FILL:
        _fill()
        return
    assert (LOT / "VERSION").read_bytes().strip() == VERSION_WAS, (LOT / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.111.0.md").decode("utf-8")
    assert entry.startswith("## 0.111.0 - "), entry[:40]
    if not DRAFT and not PENDING:
        assert "RESULT_" not in entry, "the changelog still carries an unfilled result"
    p = LOT / "site_audit.py"
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA_AUDIT, ("site_audit.py is not the file this patch read", got)
    eol = _eol(raw, "site_audit.py")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    assert "site_adjacency" not in text, "already applied"
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
    print("Lot 0.110.0 -> 0.111.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
