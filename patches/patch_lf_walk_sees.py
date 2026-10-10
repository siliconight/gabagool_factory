"""Level Factory 0.171.0: the walk preview starts at the player_start, its visual check can see, and
its hints name what the person has (roadmap 202's install test). See
`lf_walk_sees/CHANGELOG_0.171.0.md`.

Whole files from `lf_walk_sees/`, each replaced file pinned by the hash its content had when this
patch was written, with its line endings made LF:
  replaced  packages/preview/walk_preview.py   `_spawn_from_anchors`, read before the markers
  replaced  assets/godot/shot_bot.gd           holds the warm-up; a one-colour frame fails
  replaced  apps/cli/commands/__init__.py      walk's open/play and the export's hints
  replaced  packages/exporting/export.py       HANDOFF.md sends its reader to `walk`
  new       tests/unit/test_walk_preview_sees.py
CHANGELOG and VERSION from `CHANGELOG_0.171.0.md`. Nothing is written until every pin matched.

    python patch_lf_walk_sees.py [--suite-pending]
    LF_ROOT=<copy> python patch_lf_walk_sees.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_walk_sees"
DRAFT = "--draft" in sys.argv
SUITE_PENDING = "--suite-pending" in sys.argv

REPLACED = {
    "packages/preview/walk_preview.py": ("walk_preview.py", "670b2cc372518eec"),
    "assets/godot/shot_bot.gd": ("shot_bot.gd", "c60ccaef870b135f"),
    "apps/cli/commands/__init__.py": ("cli_commands.py", "4979b0482680ce0f"),
    "packages/exporting/export.py": ("export.py", "192f261c49dbc058"),
}
NEW = {"tests/unit/test_walk_preview_sees.py": "test_walk_preview_sees.py"}
CHANGELOG_HEAD = ("## [0.170.0] - Re-grounded to the tools of 2026-10-10; a hint names the "
                  "command that was typed\n")


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
    assert (LF / "VERSION").read_bytes().strip() == b"0.170.0", (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.171.0.md").decode("utf-8")
    assert entry.startswith("## [0.171.0] - "), entry[:40]
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
    (LF / "VERSION").write_bytes(b"0.171.0")
    print("Level Factory 0.170.0 -> 0.171.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
