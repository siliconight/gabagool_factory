"""Level Factory 0.167.0: init finds the tools, and the doctor asks the interpreter they run under
(roadmap 202). See `lf_tools_python/CHANGELOG_0.167.0.md`.

Whole files from `lf_tools_python/`, each replaced file pinned by the hash its content had when
this patch was written, with its line endings made LF:
  replaced  packages/jobs/scheduler.py          a blank python_executable is `tools_python`
  replaced  packages/tools/doctor.py            the `tools_python` check
  replaced  packages/project_store/workspace.py `init_workspace(..., tools_local=)`
  replaced  apps/cli/commands/__init__.py       `cmd_init` fills tools.local.json; `cmd_setup`
  replaced  apps/cli/main.py                    `setup`; --blender/--godot/--python
  replaced  adapters/deli_counter/__init__.py   the probe's interpreter is `tools_python`
  replaced  adapters/dispatch/__init__.py       the probe's interpreter is `tools_python`
  new       packages/tools/interpreter.py
  new       packages/tools/discovery.py
  new       tests/unit/test_tools_python.py
  new       tests/unit/test_discovery.py
CHANGELOG and VERSION from `CHANGELOG_0.167.0.md`. Nothing is written until every pin matched.

    python patch_lf_tools_python.py [--suite-pending]
    LF_ROOT=<copy> python patch_lf_tools_python.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_tools_python"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv

REPLACED = {
    "packages/jobs/scheduler.py": ("scheduler.py", "de6a0e373b458a99"),
    "packages/tools/doctor.py": ("doctor.py", "f64a5aa7611fb4da"),
    "packages/project_store/workspace.py": ("workspace.py", "7216ce495a4edca3"),
    "apps/cli/commands/__init__.py": ("cli_commands.py", "4ee6b86b003120fa"),
    "apps/cli/main.py": ("cli_main.py", "a162d1683a0d2d07"),
    "adapters/deli_counter/__init__.py": ("adapter_deli_counter.py", "caa6784ac3d9f1fb"),
    "adapters/dispatch/__init__.py": ("adapter_dispatch.py", "f35fe25251cec57e"),
}
NEW = {
    "packages/tools/interpreter.py": "interpreter.py",
    "packages/tools/discovery.py": "discovery.py",
    "tests/unit/test_tools_python.py": "test_tools_python.py",
    "tests/unit/test_discovery.py": "test_discovery.py",
}
CHANGELOG_HEAD = "## [0.166.0] - A dealt business's sign imports as its pack asks\n"


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
    assert (LF / "VERSION").read_bytes().strip() == b"0.166.0", (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.167.0.md").decode("utf-8")
    assert entry.startswith("## [0.167.0] - "), entry[:40]
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
    (LF / "VERSION").write_bytes(b"0.167.0")
    print("Level Factory 0.166.0 -> 0.167.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
