r"""zoo 0.36.0 -- stop reusing version numbers that already mean something.

    python patch_zoo_036.py --check
    python patch_zoo_036.py
    python patch_zoo_036.py --selftest
    python patch_zoo_036.py --revert

Run from the FACTORY ROOT (the directory holding `factory.manifest.json`).

WHAT WENT WRONG, IN ORDER.

`zoo`'s tag list runs to v0.35.0. Its VERSION file said 0.32.0 and its
CHANGELOG stopped at 0.31.0. At some point the version was RESET BACKWARDS
past four real releases, and every number written since has been landing on
top of history that already existed:

    v0.32.0  a944ccd  enriched kit index, missing-module gap report,
                      slot-fit authority over genome ranges
    v0.33.0  37924f1  Phase 1 structural species (stair_rail, ladder,
                      wallCorner, shelving, counter)
    v0.34.0
    v0.35.0

This morning I renumbered a stray CHANGELOG entry to 0.32.0 to match VERSION,
and force-moved the v0.32.0 tag off `a944ccd` onto it. That was wrong.
`a944ccd` is a real release and I read its tag as stale because the CHANGELOG
at that number described different work -- which is exactly what a reset
version number looks like, and I diagnosed it as the opposite. Restoring the
tag is the first command this prints.

Then `patch_stale_bumps.py` numbered today's work 0.33.0, which `git tag`
refused because v0.33.0 has meant "Phase 1 structural species" since it was
cut. The tag refusing is the only reason this was caught at all.

WHAT THIS DOES. Today's zoo work becomes ONE release at 0.36.0 -- above every
existing tag, so nothing is reused. The entry numbered 0.32.0 this morning
folds into it as a `### Themes` section, because it also shipped today and
its number also collides with a real tag.

WHY NOT JUST MOVE v0.33.0 ONTO TODAY'S COMMIT. Because `37924f1` is a real
release and the tag is the only thing still pointing at it -- the CHANGELOG
entries for 0.33.0 through 0.35.0 did not survive the reset. Moving it would
destroy the last record of work that happened, to save renumbering work that
has not shipped anywhere yet. That is the trade this whole session has been
arguing the other side of.

THE GAP IS DOCUMENTED IN THE ENTRY, NOT HIDDEN. A reader looking at zoo's
CHANGELOG sees 0.36.0 sitting directly on 0.31.0 and deserves to know that
0.32.0 through 0.35.0 exist as tags whose entries were lost, rather than
being left to assume the numbering is arbitrary.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

SIDECAR = ".pre_zoo036"
VERSION_F = "zoo/VERSION"
CHANGELOG = "zoo/CHANGELOG.md"

OLD_V, NEW_V = "Zoo 0.33.0", "Zoo 0.36.0"

#: Edit 1: the heading becomes 0.36.0, gains the numbering note, and absorbs
#: the themes body as its first section.
OLD_HEAD = (
    "## [0.33.0] - Architecture becomes plates and modules, and the covers "
    "stop lying about their UVs\n"
    "\n"
    "### Changed\n"
)

NEW_HEAD = (
    "## [0.36.0] - Plates, modules, honest cover UVs, and three visual themes\n"
    "\n"
    "NUMBERING. This jumps 0.31.0 -> 0.36.0. Tags `v0.32.0` through `v0.35.0`\n"
    "exist and point at real releases -- `v0.32.0` is the enriched kit index\n"
    "and slot-fit authority, `v0.33.0` is the Phase 1 structural species\n"
    "(stair_rail, ladder, wallCorner, shelving, counter) -- but their\n"
    "CHANGELOG entries did not survive a version reset that took VERSION\n"
    "backwards to 0.31.0. Today's work therefore starts above all of them\n"
    "rather than landing on numbers that already mean something. The two\n"
    "entries written on 2026-08-14 under 0.32.0 and 0.33.0 are both here.\n"
    "\n"
    "### Themes\n"
    "- **center_city** (polished commercial: low wear, cooler/lighter, clean\n"
    "  materials) and **industrial_flats** (port/works: high wear, desaturated\n"
    "  iron tones, metal-first) join **delco** in every species genome (46) --\n"
    "  deterministic derivations of each species' anchor style, resolved through\n"
    "  the standard _pick_style_tag/resolve_module_plan path. 205 tests green.\n"
    "\n"
    "### Changed\n"
)

#: Edit 2: the old 0.32.0 entry is removed, having been folded in above.
OLD_THEMES = (
    "## [0.32.0] - Three visual themes across the species set\n"
    "\n"
    "- **center_city** (polished commercial: low wear, cooler/lighter, clean\n"
    "  materials) and **industrial_flats** (port/works: high wear, desaturated\n"
    "  iron tones, metal-first) join **delco** in every species genome (46) --\n"
    "  deterministic derivations of each species' anchor style, resolved through\n"
    "  the standard _pick_style_tag/resolve_module_plan path. 205 tests green.\n"
    "\n"
)

_CRLF = "\r\n"


def _eol(body: str) -> str:
    crlf = body.count(_CRLF)
    lf = body.count("\n") - crlf
    return _CRLF if crlf > lf else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def newest_entry(path: Path) -> str | None:
    if not path.is_file():
        return None
    m = re.search(r"^##\s*\[?v?([0-9]+\.[0-9]+\.[0-9]+)\]?",
                  path.read_text(encoding="utf-8", errors="replace"), re.M)
    return m.group(1) if m else None


def _apply(root: Path, *, check: bool) -> int:
    vp, cp = root / VERSION_F, root / CHANGELOG
    if not vp.is_file() or not cp.is_file():
        print("REFUSING: zoo is missing VERSION or CHANGELOG.md")
        return 1
    vraw, craw = vp.read_bytes(), cp.read_bytes()
    vbody, cbody = vraw.decode("utf-8"), craw.decode("utf-8")

    if NEW_V in vbody and "## [0.36.0]" in cbody:
        print("  already applied")
        return 0
    if OLD_V not in vbody:
        print(f"REFUSING: {VERSION_F} does not say {OLD_V!r} "
              f"(found {vbody.strip()!r}) -- run patch_stale_bumps.py first")
        return 1

    eol = _eol(cbody)
    oh, nh = _as(OLD_HEAD, eol), _as(NEW_HEAD, eol)
    ot = _as(OLD_THEMES, eol)
    for label, needle in (("0.33.0 heading", oh), ("0.32.0 entry", ot)):
        if cbody.count(needle) != 1:
            print(f"REFUSING: the {label} occurs {cbody.count(needle)} "
                  f"time(s), expected 1")
            return 1

    cout = cbody.replace(oh, nh, 1).replace(ot, "", 1)
    vout = vbody.replace(OLD_V, NEW_V, 1)
    vdata, cdata = vout.encode("utf-8"), cout.encode("utf-8")

    if check:
        print(f"  would bump   {VERSION_F}  {OLD_V} -> {NEW_V}")
        print(f"  would rewrite {CHANGELOG}  {len(craw):,} -> {len(cdata):,} "
              f"bytes ({len(cdata) - len(craw):+,})")
        return 0
    for p, raw in ((vp, vraw), (cp, craw)):
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(raw)
    vp.write_bytes(vdata)
    cp.write_bytes(cdata)
    print(f"  bumped       {VERSION_F}  {OLD_V} -> {NEW_V}")
    print(f"  rewrote      {CHANGELOG}  {len(craw):,} -> {len(cdata):,} bytes "
          f"({len(cdata) - len(craw):+,})  sha256 {_sha(cdata)[:16]}")
    return 0


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    v = (root / VERSION_F).read_text(encoding="utf-8")
    t = (root / CHANGELOG).read_text(encoding="utf-8")

    check("VERSION is 0.36.0", "0.36.0" in v)
    check("newest entry is 0.36.0", newest_entry(root / CHANGELOG) == "0.36.0")

    heads = re.findall(r"^##\s*\[([0-9]+\.[0-9]+\.[0-9]+)\]", t, re.M)
    check("no 0.33.0 heading -- that number is taken by 37924f1",
          "0.33.0" not in heads)
    check("no 0.32.0 heading -- that number is taken by a944ccd",
          "0.32.0" not in heads)
    check("0.36.0 sits directly on 0.31.0",
          heads[:2] == ["0.36.0", "0.31.0"])
    check("descending order throughout", heads == sorted(
        heads, key=lambda s: tuple(int(x) for x in s.split(".")),
        reverse=True))

    check("the gap is explained, not hidden",
          "NUMBERING." in t and "did not survive a version reset" in t)
    check("it names what v0.32.0 and v0.33.0 actually are",
          "enriched kit index" in t and "Phase 1 structural species" in t)

    # Both bodies survived the fold.
    check("the themes body survived", "205 tests green." in t
          and "industrial_flats" in t)
    check("the themes body appears once", t.count("205 tests green.") == 1)
    check("the plates work survived",
          "carrying the slab's holes" in t and "a03617a" in t)
    check("every commit from the 0.33.0 entry is still named",
          all(s in t for s in ("a03617a", "b919677", "56a1fc6", "13b8b2a",
                               "0b61689", "d2a8ff3", "cf8c3e8", "5f7b898",
                               "e2c6160", "f7ee3e2", "26728c7", "c26670a",
                               "3f18b6a", "ad9b111", "ebdb924", "abbe1db")))
    check("the 0.31.0 entry is untouched",
          t.count("## [0.31.0] - Branded sign faces from Pixelcoat sign packs")
          == 1)
    check("one document title", t.count("# Changelog") == 1)

    lf = str((root / "level_factory").resolve())
    if lf not in sys.path:
        sys.path.insert(0, lf)
    try:
        import importlib
        contracts = importlib.import_module("packages.tools.contracts")
        importlib.reload(contracts)
        c = contracts.newest_changelog_entry(root / "zoo")
        check(f"verify-manifest's reader sees {c}", c == "0.36.0")
        check("and calls it agreement",
              contracts.self_disagreement(v, c) is None)
    except Exception as exc:
        print(f"  skip  contracts check ({type(exc).__name__}: {exc})")

    print()
    print("  zoo is above its own history again"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")

    if "--selftest" in argv:
        return selftest(root)

    if "--revert" in argv:
        bad = 0
        for rel in (VERSION_F, CHANGELOG):
            p = root / rel
            side = p.with_suffix(p.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {rel}")
                bad = 1
                continue
            p.write_bytes(side.read_bytes())
            print(f"  reverted     {rel}")
        return bad

    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("  FIRST, put back the tag I moved this morning:")
        print("    git -C zoo tag -f v0.32.0 a944ccd")
        print("    git -C zoo push --force origin v0.32.0")
        print("    git -C zoo log --oneline -1 v0.32.0"
              "     # expect a944ccd")
        print()
        print("  then:")
        print("    python patches\\patch_zoo_036.py --selftest")
        print("    git -C zoo add -A")
        print('    git -C zoo commit -m "0.36.0 -- renumber above the tags a '
              'version reset had buried"')
        print('    git -C zoo tag -a v0.36.0 -m "0.36.0 -- plates, modules, '
              'honest cover UVs, three visual themes"')
        print("    git -C zoo push --follow-tags")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
