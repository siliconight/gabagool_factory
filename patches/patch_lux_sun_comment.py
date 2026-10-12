"""Lux 0.76.1: a correction -- the bake traces the sun's occlusion whatever its shadow flag (factory
roadmap 243; `docs/findings/lux_tiers/`, 2026-10-12).

0.76.0 said, in `_apply_sun_mode`'s comment, its CHANGELOG entry and its commit, that a static sun baked
with its shadows off "bakes flat" -- "measured, the factory's B arm". It was never measured: B's frames
were in no table. Measured since, B (the flag off for the bake) and B2 (on) read the same frames within
a re-bake's noise. No behaviour changes; the comment and the self-test's docstring say what was
measured, and what the lightmap does not hold (what moves, and what a level loads outside the baked
scene -- the factory's backdrop, `docs/findings/lux_tiers/backdrop_split.py`).

Anchored edits, each asserted once, nothing written until all of them matched:
  addons/lux/runtime/lux_lighting.gd   `_apply_sun_mode`'s comment
  tools/sun_bake_selftest.gd           the docstring's paragraph on the editor's case
CHANGELOG and VERSION from `lux_sun_comment/CHANGELOG_0.76.1.md`.

Read before it was written: both files as Lux 0.76.0 (40a81fe) committed them, LF, pinned below.

    python patches/patch_lux_sun_comment.py
    LUX_ROOT=<copy> python patches/patch_lux_sun_comment.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LUX = pathlib.Path(os.environ.get("LUX_ROOT") or HERE.parent / "lux")
SRC = HERE / "lux_sun_comment"
DRAFT = "--draft" in sys.argv
VERSION_WAS, VERSION = b"Lux 0.76.0", b"Lux 0.76.1"
CHANGELOG_HEAD = "# Changelog\n\n## [0.76.0] - the sun is baked while the lightmap shows\n"
LIGHTING = "addons/lux/runtime/lux_lighting.gd"
TEST = "tools/sun_bake_selftest.gd"
SHA = {LIGHTING: "9cf37ce454563cec", TEST: "f0b24dccd0dca0b7"}

COMMENT_OLD = ("## them, 788 draws and 4.42 ms, the look kept but for what moves -- it casts\n"
               "## and takes no sun shadow -- and shadows as soft as the lightmap's texels.\n"
               "## So: in the editor, where Level Factory bakes, the sun is STATIC with the\n"
               "## preset's shadows, so the bake traces them (a static sun baked unshadowed\n"
               "## bakes flat); at run time it is static and unshadowed while a lightmap\n"
               "## shows, and dynamic with the preset's shadows whenever none does -- no\n")
COMMENT_NEW = ("## them, 788 draws and 4.42 ms, the look kept but for what the lightmap does\n"
               "## not hold -- what moves, and anything a level loads outside the baked scene\n"
               "## (the factory's backdrop) -- which takes the sun with no shadow, and shadows\n"
               "## as soft as the lightmap's texels.\n"
               "## So: in the editor, where Level Factory bakes, the sun is STATIC, so the\n"
               "## bake carries its light; its shadow flag stays as the preset and the tier\n"
               "## ask, and the bake traces the sun's occlusion either way (0.76.1: the\n"
               "## factory's arms B and B2, baked with the flag off and on, read the same\n"
               "## frames -- 0.76.0 said a static sun baked unshadowed bakes flat, which was\n"
               "## never measured and is not so). At run time it is static and unshadowed\n"
               "## while a lightmap shows, and dynamic with the preset's shadows whenever\n"
               "## none does -- no\n")

TEST_OLD = ("## What it cannot hold: the editor, where the sun is static WITH its shadows\n"
            "## so Level Factory's bake traces them (`Engine.is_editor_hint()` cannot be\n"
            "## set from a script). A cold run's bake proves that case.\n")
TEST_NEW = ("## What it cannot hold: the editor, where the sun is static so Level\n"
            "## Factory's bake carries its light (`Engine.is_editor_hint()` cannot be set\n"
            "## from a script). The factory's cold run 9265 proves that case: 0.76.0 in a\n"
            "## real drive, its frames reading as the re-baked arm it was written from,\n"
            "## inside a re-bake's own noise.\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    raw = (LUX / rel).read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def main():
    if DRAFT and not os.environ.get("LUX_ROOT"):
        sys.exit("refusing: --draft is for a LUX_ROOT copy, never the repo")
    assert (LUX / "VERSION").read_bytes().strip() == VERSION_WAS, (LUX / "VERSION").read_bytes()
    entry = (SRC / "CHANGELOG_0.76.1.md").read_bytes().decode("utf-8").replace("\r\n", "\n")
    assert entry.startswith("## [0.76.1] - "), entry[:40]
    assert "RESULT_" not in entry, "the changelog carries an unfilled result"
    l_eol, l_text = _read(LIGHTING)
    t_eol, t_text = _read(TEST)
    l_text = _once(l_text, COMMENT_OLD, COMMENT_NEW, "_apply_sun_mode's comment")
    t_text = _once(t_text, TEST_OLD, TEST_NEW, "the self-test's editor paragraph")
    cl = LUX / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD), cl_text[:160]
    cl_new = "# Changelog\n\n" + entry.rstrip("\n") + "\n\n" + cl_text[len("# Changelog\n\n"):]
    # every anchor matched: now write
    (LUX / LIGHTING).write_bytes(l_text.encode("utf-8").replace(b"\n", l_eol))
    (LUX / TEST).write_bytes(t_text.encode("utf-8").replace(b"\n", t_eol))
    cl.write_bytes(cl_new.encode("utf-8").replace(b"\n", cl_eol))
    (LUX / "VERSION").write_bytes(VERSION)
    print("Lux 0.76.0 -> 0.76.1" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
