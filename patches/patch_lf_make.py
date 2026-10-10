"""Level Factory 0.169.0: make, one level from a batch start to finish, and pick (roadmap 202). See
`lf_make/CHANGELOG_0.169.0.md`.

Whole files from `lf_make/`, each replaced file pinned by the hash its content had when this
patch was written, with its line endings made LF:
  replaced  apps/cli/commands/__init__.py   `cmd_pick`, `_make_leg`, `cmd_make`
  replaced  apps/cli/main.py                `make`, `pick`
  new       packages/pipeline/pick.py
  new       tests/unit/test_make_and_pick.py
CHANGELOG and VERSION from `CHANGELOG_0.169.0.md`. Nothing is written until every pin matched.

    python patch_lf_make.py [--suite-pending]
    LF_ROOT=<copy> python patch_lf_make.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_make"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv

REPLACED = {
    "apps/cli/commands/__init__.py": ("cli_commands.py", "e7337f8e44c27b3b"),
    "apps/cli/main.py": ("cli_main.py", "6945429689c67e01"),
}
NEW = {
    "packages/pipeline/pick.py": "pick.py",
    "tests/unit/test_make_and_pick.py": "test_make_and_pick.py",
}
CHANGELOG_HEAD = "## [0.168.0] - setup --venv gives the tools a Python of their own\n"


def _src(name):
    return (SRC / name).read_bytes().replace(b"\r\n", b"\n")


def _sha(raw):
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]


def _eol(raw, rel):
    """The file's own line ending. A file with both refuses: there is no one ending to restore."""
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def main():
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == b"0.168.0", (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.169.0.md").decode("utf-8")
    assert entry.startswith("## [0.169.0] - "), entry[:40]
    if not DRAFT:
        left = entry.replace("RESULT_SUITE", "") if SUITE_PENDING else entry
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    writes = {}
    for rel, (name, sha) in REPLACED.items():
        raw = (LF / rel).read_bytes()
        assert _sha(raw) == sha, (rel, "is not the file this patch read", _sha(raw))
        writes[LF / rel] = _src(name).replace(b"\n", _eol(raw, rel))
    for rel, name in NEW.items():
        assert not (LF / rel).exists(), (rel, "already exists")
        writes[LF / rel] = _src(name)
    cl = LF / "CHANGELOG.md"
    raw = cl.read_bytes()
    eol = _eol(raw, "CHANGELOG.md")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    assert text.startswith(CHANGELOG_HEAD) and text.count(CHANGELOG_HEAD) == 1, text[:90]
    # every pin matched: now write
    for p, data in writes.items():
        p.write_bytes(data)
    cl.write_bytes((entry.rstrip("\n") + "\n\n" + text).encode("utf-8").replace(b"\n", eol))
    (LF / "VERSION").write_bytes(b"0.169.0")
    print("Level Factory 0.168.0 -> 0.169.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
