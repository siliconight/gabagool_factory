"""Deli Counter 0.193.0: VERSION and CHANGELOG for the repo-hygiene move (23
`git mv` into `migrations/`, no code change; the index there is written by
`tools/factory_index.py` at the factory root).

    python patch_dc_0193_release.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC = ROOT / "deli_counter"

ENTRY = '''## [0.193.0] - the root is the builder and its gates; 23 one-shots move under migrations/

Repo hygiene (`docs/findings/repo_hygiene_2026-10/` at the factory root).
The root held 235 files, and the README's Layout section described 22 of
them. The 120 `test_*.py` stay: `check.py` collects them there, and
COMMANDS.md says so.

**Moved to `migrations/`, unchanged, history following each** (`git mv`):
the seven `phase*_status.py` reports, `p2_collect.py`, `remediate_l5.py`,
`probe_fights.py`, `sweep_stair_obstruction.py`, `walk_harness.py`,
`review_render.py`, `review_sheet.py` and the `ai_review.py` it imports,
the five `patch_dc_*.py` that were applied here rather than from the
factory's `patches/`, and `generated_sweep.json`, `rockay_sweep.json`,
`stair_sweep.json`. Measured first: nothing at the root, in `hooks/` or in
the workflow imports or reads any of them. Each ran from the root when it
ran, and is kept because a patch script is the only record of how the
source came to be.

**Not moved:** the 21 `migrate_*.py`. They are live code -- presets,
`level_design.py`, `layout_lint.py` and twenty tests import them -- so
moving them is a code change for another release.

`migrations/README.md` is a generated index (`tools/factory_index.py` at
the factory root), one line per file from its own docstring; `--check`
fails when it drifts.

**Suite:** unchanged in content; the pre-commit hook ran the full check.

'''


def main():
    v = DC / "VERSION"
    assert v.read_bytes() == b"Deli Counter 0.192.0", v.read_bytes()
    cl = DC / "CHANGELOG.md"
    data = cl.read_bytes()
    assert b"\r\n" not in data
    text = data.decode("utf-8")
    assert text.startswith("## [0.192.0] - a piece where a stair now is"), text[:60]
    cl.write_bytes((ENTRY + text).encode("utf-8"))
    v.write_bytes(b"Deli Counter 0.193.0")
    print("Deli Counter 0.193.0: VERSION and CHANGELOG")


if __name__ == "__main__":
    main()
