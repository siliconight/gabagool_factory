"""Level Factory 0.138.1: the drip's tools find Pixelcoat by searching.

`tools/drip_assets.py:38` and `tools/wet_ab_run.py:150` located Pixelcoat as
`Path(__file__).resolve().parents[2] / "pixelcoat"`, and
`test_sibling_locator`'s guard failed on both: from a git worktree that count
lands in `scratchpad`, which holds no Pixelcoat. See
`lf_pixelcoat_locator/CHANGELOG_0.138.1.md`.

Anchored edits (every anchor once; refuses on a miss):
  tools/drip_assets.py  `pixelcoat_root()`: LF_PIXELCOAT_ROOT, then a walk
                        for the file `stage` imports; `stage` refuses with a
                        sentence when neither finds it
  tools/wet_ab_run.py   `--pixelcoat` defaults to None, so the one search in
                        drip_assets answers for it
Copies the test into tests/unit; CHANGELOG and VERSION.

    python patch_lf_pixelcoat_locator.py
"""
import pathlib
import shutil

HERE = pathlib.Path(__file__).resolve().parent
LF = HERE.parent / "level_factory"
SRC = HERE / "lf_pixelcoat_locator"


def _edit(path, pairs):
    s = path.read_text(encoding="utf-8")
    assert "\r" not in s, path
    for old, new in pairs:
        assert s.count(old) == 1, (path.name, old[:70])
        s = s.replace(old, new)
    path.write_text(s, encoding="utf-8", newline="\n")


IMPORT_OLD = '''import sys
from pathlib import Path
'''
IMPORT_NEW = '''import os
import sys
from pathlib import Path
'''

DEFAULT_OLD = '''#: Pixelcoat, guessed from the factory layout. Both callers can override.
DEFAULT_PIXELCOAT = Path(__file__).resolve().parents[2] / "pixelcoat"
'''
DEFAULT_NEW = '''#: The file `stage` imports out of Pixelcoat, relative to its repo: the marker
#: that makes a directory called `pixelcoat` the repo rather than a name.
PIXELCOAT_MARKER = "pixelcoat/core/droplets.py"
#: Overrides the search (the name `tests/siblings.env_var` derives).
PIXELCOAT_ENV = "LF_PIXELCOAT_ROOT"


def pixelcoat_root() -> Path | None:
    """The nearest `pixelcoat/` at or above this file carrying the marker.

    SEARCHED, NOT COUNTED (0.138.1). This was `parents[2] / "pixelcoat"`: the
    factory from a checkout beside its siblings, and `scratchpad` from a git
    worktree, where there is no Pixelcoat -- the arithmetic `tests/siblings.py`
    removed from the suite and `test_sibling_locator` refuses. Same rules as
    `sibling_repo`, restated because a tool run as `python tools/x.py` cannot
    import `tests`: the override takes the repo or the directory holding it,
    and an override naming the wrong place answers None rather than falling
    back to the walk.
    """
    env = os.environ.get(PIXELCOAT_ENV)
    if env:
        for root in (Path(env), Path(env) / "pixelcoat"):
            if (root / PIXELCOAT_MARKER).is_file():
                return root
        return None
    for parent in Path(__file__).resolve().parents:
        if (parent / "pixelcoat" / PIXELCOAT_MARKER).is_file():
            return parent / "pixelcoat"
    return None


#: Pixelcoat as found, or None. Both callers can pass their own.
DEFAULT_PIXELCOAT = pixelcoat_root()
'''

STAGE_OLD = '''    pixelcoat = Path(pixelcoat) if pixelcoat else DEFAULT_PIXELCOAT
'''
STAGE_NEW = '''    pixelcoat = Path(pixelcoat) if pixelcoat else DEFAULT_PIXELCOAT
    if pixelcoat is None:
        raise SystemExit(
            "the drip needs Pixelcoat and none was found: no pixelcoat/%s at "
            "or above %s -- pass --pixelcoat or set %s. The atlas is "
            "generated, never carried."
            % (PIXELCOAT_MARKER, Path(__file__).resolve().parent, PIXELCOAT_ENV))
'''

WET_OLD = '''    ap.add_argument("--pixelcoat", type=Path,
                    default=Path(__file__).resolve().parents[2] / "pixelcoat",
                    help="pixelcoat repo, for the drop atlas")
'''
WET_NEW = '''    ap.add_argument("--pixelcoat", type=Path, default=None,
                    help="pixelcoat repo, for the drop atlas; unset, "
                         "`drip_assets` searches for it (LF_PIXELCOAT_ROOT "
                         "overrides)")
'''


def main():
    assert (LF / "VERSION").read_text(encoding="utf-8").strip() == "0.138.0"
    _edit(LF / "tools" / "drip_assets.py",
          [(IMPORT_OLD, IMPORT_NEW), (DEFAULT_OLD, DEFAULT_NEW), (STAGE_OLD, STAGE_NEW)])
    _edit(LF / "tools" / "wet_ab_run.py", [(WET_OLD, WET_NEW)])
    shutil.copyfile(SRC / "test_drip_pixelcoat_locator.py",
                    LF / "tests" / "unit" / "test_drip_pixelcoat_locator.py")
    ch = LF / "CHANGELOG.md"
    s = ch.read_text(encoding="utf-8")
    ch.write_text((SRC / "CHANGELOG_0.138.1.md").read_text(encoding="utf-8").rstrip("\n") + "\n\n" + s,
                  encoding="utf-8", newline="\n")
    (LF / "VERSION").write_text("0.138.1", encoding="utf-8", newline="\n")
    print("applied Level Factory 0.138.1")


if __name__ == "__main__":
    main()
