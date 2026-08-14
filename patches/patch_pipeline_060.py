r"""pipeline 0.6.0 -- the guard-rail evidence, written from the diff.

    python patch_pipeline_060.py --check
    python patch_pipeline_060.py
    python patch_pipeline_060.py --selftest
    python patch_pipeline_060.py --revert

Run from the FACTORY ROOT (the directory holding `factory.manifest.json`).

I ARGUED AGAINST THIS BUMP AND I WAS WRONG. `patch_pipeline_changelog.py`
said, backfilling v0.1.1 through v0.5.0:

    VERSION DOES NOT MOVE. ... `draft_version_bumps.py` proposed 0.6.0
    because it found one commit newer than VERSION -- `7ed8e00`, subject
    "checkpoint: uncommitted working tree". A checkpoint is not a release.

The subject is not the change. Reading `7ed8e00`'s actual diff shows it
stamps a `guard_rails` evidence record onto EVERY mission in
`mission_registry.json`:

    "guard_rails": "Site guard-rail pass (2026-07-21): cover remediation
    applied; all mission sites re-assembled, walktest + 4-player smoke
    re-verified green"

Identical hunk shape across `ballpark_block`, `bank_tower_block`,
`brewery_block`, `central_vault`, `deli_block`, `independence_mall`,
`mainline_mansion` and the rest -- 60 changed lines, plus 6 in
`building_configuration_registry.json`. A new evidence key across the whole
registry is exactly what this tool exists to do. It is a release with a bad
commit message, and I judged it by the message.

Which is the lesson `verify-manifest` learned in 0.25.0 from the other side:
a number is not a fact, and neither is a subject line. The only thing that
knew was the diff.

WHAT THIS ENTRY DOES NOT CLAIM. I read the `mission_registry.json` hunks.
I did NOT read the 6 lines in `building_configuration_registry.json` or the
4 in `.gitignore`, so the entry names them and stops there rather than
guessing that they are the same change. `pixelcoat`'s `7ed7400` in the same
week was `gitignore: *.pre_* -- patch backups are copies of tracked files,
not history`, which makes a good guess about the .gitignore lines available
and still a guess, so it is not written as fact.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

SIDECAR = ".pre_060"

VERSION_F = "pipeline/VERSION"
CHANGELOG = "pipeline/CHANGELOG.md"

OLD_V, NEW_V = "Pipeline 0.5.0", "Pipeline 0.6.0"

#: Inserted above the newest existing entry, so the reconstruction preamble
#: written in the backfill stays next to the entries it describes.
ANCHOR = "## [v0.5.0] - 2026-07-21\n"

ENTRY = """## [v0.6.0] - guard-rail evidence stamped across the mission registry

Every mission in `mission_registry.json` gains a `guard_rails` record in its
`evidence` block:

    "guard_rails": "Site guard-rail pass (2026-07-21): cover remediation
    applied; all mission sites re-assembled, walktest + 4-player smoke
    re-verified green"

The same hunk on every site -- `ballpark_block`, `bank_tower_block`,
`brewery_block`, `central_vault`, `deli_block`, `independence_mall`,
`mainline_mansion` and the rest. 60 changed lines in the mission registry.

Also 6 lines in `building_configuration_registry.json` and 4 in `.gitignore`,
which are named here and not described: this entry was written from the
mission-registry diff on 2026-08-14, and those two were not read. A guess
about them would be the kind of thing this file exists to not contain.

WRITTEN FROM THE DIFF BECAUSE THE COMMIT SUBJECT SAYS NOTHING. `7ed8e00` is
"checkpoint: uncommitted working tree", dated 2026-08-12. On the strength of
that subject this release was passed over once already, on the reasoning that
a checkpoint is not a release. It is one; the subject was just wrong about
its own commit. A registry-wide evidence key is precisely the change this
tool is for.

"""

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
        print("REFUSING: pipeline is missing VERSION or CHANGELOG.md")
        return 1
    vraw, craw = vp.read_bytes(), cp.read_bytes()
    vbody, cbody = vraw.decode("utf-8"), craw.decode("utf-8")

    if NEW_V in vbody and "## [v0.6.0]" in cbody:
        print("  already applied")
        return 0
    if OLD_V not in vbody:
        print(f"REFUSING: {VERSION_F} does not say {OLD_V!r} "
              f"(found {vbody.strip()!r})")
        return 1
    if "## [v0.5.0]" not in cbody:
        print("REFUSING: the v0.5.0 entry is not here -- run "
              "patch_pipeline_changelog.py first")
        return 1

    ceol = _eol(cbody)
    a, n = _as(ANCHOR, ceol), _as(ENTRY + ANCHOR, ceol)
    if cbody.count(a) != 1:
        print(f"REFUSING: the v0.5.0 heading occurs {cbody.count(a)} time(s), "
              f"expected 1")
        return 1

    vout = vbody.replace(OLD_V, NEW_V, 1)
    cout = cbody.replace(a, n, 1)
    vdata, cdata = vout.encode("utf-8"), cout.encode("utf-8")
    if check:
        print(f"  would bump   {VERSION_F}  {OLD_V} -> {NEW_V}")
        print(f"  would insert {CHANGELOG}  +{len(cdata) - len(craw):,} bytes")
        return 0
    for p, raw in ((vp, vraw), (cp, craw)):
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(raw)
    vp.write_bytes(vdata)
    cp.write_bytes(cdata)
    print(f"  bumped       {VERSION_F}  {OLD_V} -> {NEW_V}")
    print(f"  inserted     {CHANGELOG}  +{len(cdata) - len(craw):,} bytes  "
          f"sha256 {_sha(cdata)[:16]}")
    return 0


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    v = (root / VERSION_F).read_text(encoding="utf-8")
    t = (root / CHANGELOG).read_text(encoding="utf-8")

    check("VERSION is 0.6.0", "0.6.0" in v)
    check("newest entry is v0.6.0", newest_entry(root / CHANGELOG) == "0.6.0")
    heads = re.findall(r"^##\s*\[v?([0-9]+\.[0-9]+\.[0-9]+)\]", t, re.M)
    check("seven entries, descending",
          heads == ["0.6.0", "0.5.0", "0.4.0", "0.3.0", "0.2.0", "0.1.1",
                    "0.1.0"])
    check("the backfill preamble still sits above the entries it describes",
          t.index("RECONSTRUCTED on 2026-08-14") < t.index("## [v0.6.0]"))
    check("the entry quotes the guard_rails record", "guard_rails" in t
          and "cover remediation" in t)
    check("it names the commit it was written from", "7ed8e00" in t)
    check("it says what it did NOT read",
          "building_configuration_registry.json" in t and "not read" in t)
    check("the earlier v0.5.0 entry is intact",
          t.count("## [v0.5.0]") == 1 and "Phase 4 complete" in t)

    lf = str((root / "level_factory").resolve())
    if lf not in sys.path:
        sys.path.insert(0, lf)
    try:
        import importlib
        contracts = importlib.import_module("packages.tools.contracts")
        importlib.reload(contracts)
        c = contracts.newest_changelog_entry(root / "pipeline")
        check(f"verify-manifest's reader sees {c}", c == "0.6.0")
        check("and calls it agreement",
              contracts.self_disagreement(v, c) is None)
    except Exception as exc:
        print(f"  skip  contracts check ({type(exc).__name__}: {exc})")

    print()
    print("  pipeline agrees with itself at 0.6.0"
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
        print("  python patches\\patch_pipeline_060.py --selftest")
        print()
        print("  then, INSIDE pipeline:")
        print("    git -C pipeline add -A")
        print('    git -C pipeline commit -m "0.6.0 -- guard-rail evidence '
              'across the mission registry"')
        print('    git -C pipeline tag -a v0.6.0 -m "0.6.0 -- guard-rail '
              'evidence across the mission registry"')
        print("    git -C pipeline push --follow-tags")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
