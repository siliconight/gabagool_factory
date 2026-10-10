"""Level Factory 0.170.0: re-grounded to the tools of 2026-10-10, and a hint names the command that
was typed (roadmap 202's install test). See `lf_reground/CHANGELOG_0.170.0.md`.

Whole files from `lf_reground/`, each replaced file pinned by the hash its content had when this
patch was written, with its line endings made LF:
  replaced  packages/tools/contracts.py      `GROUNDED` at 2026-10-10's versions
  replaced  packages/tools/discovery.py      `COMMAND_ENV`, `command_name`
  replaced  packages/tools/doctor.py         the `setup --venv` hint uses it
  replaced  apps/cli/commands/__init__.py    `init`'s and `make`'s hints use it
  replaced  tests/fixtures/repos/*/VERSION   the stand-in tools declare the grounded versions,
            and Deli Counter's and Dispatch's stub `contract` commands report them
  new       tests/unit/test_command_name.py
CHANGELOG and VERSION from `CHANGELOG_0.170.0.md`. Nothing is written until every pin matched.

    python patch_lf_reground.py [--suite-pending]
    LF_ROOT=<copy> python patch_lf_reground.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_reground"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv

REPLACED = {
    "packages/tools/contracts.py": ("contracts.py", "1003239b0266366d"),
    "packages/tools/discovery.py": ("discovery.py", "3a609700f2b2a539"),
    "packages/tools/doctor.py": ("doctor.py", "1a03056c8751d085"),
    "apps/cli/commands/__init__.py": ("cli_commands.py", "eb9feaf0d9ceebe0"),
    # the stand-in tool repos follow GROUNDED (`test_the_stub_repos_declare_the_grounded_versions`)
    "tests/fixtures/repos/deli_counter/VERSION": ("stub_deli_counter_VERSION", "09c3e5fa1103c8bd"),
    "tests/fixtures/repos/lot/VERSION": ("stub_lot_VERSION", "e299bc6f499b7690"),
    "tests/fixtures/repos/laser_tag/VERSION": ("stub_laser_tag_VERSION", "1a2d33e79e39ccdd"),
    "tests/fixtures/repos/pixelcoat/VERSION": ("stub_pixelcoat_VERSION", "d365ad165f987827"),
    "tests/fixtures/repos/zoo/VERSION": ("stub_zoo_VERSION", "cc52f678848b8143"),
    "tests/fixtures/repos/lux/VERSION": ("stub_lux_VERSION", "3197a188c6ceb98d"),
    "tests/fixtures/repos/patina/VERSION": ("stub_patina_VERSION", "252e81879746f7a3"),
    "tests/fixtures/repos/dispatch/VERSION": ("stub_dispatch_VERSION", "d915cc95d6ca8f47"),
    "tests/fixtures/repos/deli_counter/deli_counter/__main__.py": ("stub_deli_main.py",
                                                                   "20d4c8c930534dc9"),
    "tests/fixtures/repos/dispatch/dispatch/__main__.py": ("stub_dispatch_main.py",
                                                           "c9feab6f51041ab3"),
}
NEW = {"tests/unit/test_command_name.py": "test_command_name.py"}
CHANGELOG_HEAD = ("## [0.169.0] - make: one level from a batch, start to finish; pick names the "
                  "candidate\n")


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
    assert (LF / "VERSION").read_bytes().strip() == b"0.169.0", (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.170.0.md").decode("utf-8")
    assert entry.startswith("## [0.170.0] - "), entry[:40]
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
    (LF / "VERSION").write_bytes(b"0.170.0")
    print("Level Factory 0.169.0 -> 0.170.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
