r"""pipeline: write the five entries that were never written.

    python patch_pipeline_changelog.py --check
    python patch_pipeline_changelog.py
    python patch_pipeline_changelog.py --selftest
    python patch_pipeline_changelog.py --revert

Run from the FACTORY ROOT (the directory holding `factory.manifest.json`).

WHY. `verify-manifest`, once it learned to read the CHANGELOG (level_factory
0.25.0), reported one finding across ten tools:

    UNDOCUMENTED  pipeline  VERSION says 0.5.0 but the newest CHANGELOG entry
                            is 0.1.0 -- this release has no entry; write one

Five releases shipped with no record. This writes them.

VERSION DOES NOT MOVE. `pipeline` is genuinely at 0.5.0 and always was; what
is missing is the record, not the release. `draft_version_bumps.py` proposed
0.6.0 because it found one commit newer than VERSION -- `7ed8e00`, subject
"checkpoint: uncommitted working tree", 2026-08-12. A checkpoint is not a
release. Bumping for it would add a sixth undocumented version to fix five.

EVERY ENTRY COMES OFF A COMMIT, AND THE COMMIT IS NAMED IN IT. This repo's
history is unusually cooperative: each commit that moved VERSION says in its
subject what was registered.

    e2cc8f4  2026-07-17  v0.1.0: production registrar -- registries, ID
                         grammar, distinction rules, approval enforcement
    22b4c79  2026-07-18  0.1.1: reference records stamped PASS on all engine
                         gates
    a4002e4  2026-07-19  0.2.0: register 10 Phase 1 configs + 2 missions, all
                         engine gates stamped
    a74119a  2026-07-20  0.3.0: 40 configs / 16 families / 6 missions
                         registered, all engine gates stamped
    b93273f  2026-07-21  0.4.0: 75 configs / 28 families / 12 missions /
                         4 heroes registered, all engine-stamped
    79b0db3  2026-07-21  Phase 4: registries at 100/36/20/8, every family
                         placed, engine evidence stamped; bank_job P0 record
                         backfilled

So the entries state what those commits did and nothing else. They do not
explain WHY, because nothing on disk says why and a CHANGELOG in this repo is
supposed to carry the argument for a change. An entry that invents the
argument is worse than one that admits it is a reconstruction, so each says
so and names its sha -- a reader who wants the reasoning has somewhere to go.

`79b0db3` is 0.5.0 even though its subject does not say so: it is the next
commit after 0.4.0 to touch VERSION, and VERSION reads 0.5.0. The factory
manifest's own note for pipeline corroborates it -- "Phase 4 complete: 100
configs / 36 families / 20 missions / 8 heroes registered, engine-gated" --
the same four numbers the commit reports.

AFTER THIS, `verify-manifest` READS pipeline AS OK: VERSION 0.5.0, newest
entry v0.5.0, pin 0.5.0. Ten of ten agreeing.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

TARGET = "pipeline/CHANGELOG.md"
SIDECAR = ".pre_backfill"

ANCHOR = "# Pipeline Changelog\n\n"

NEW = """# Pipeline Changelog

Entries for v0.1.1 through v0.5.0 were RECONSTRUCTED on 2026-08-14 from this
repo's own commits, weeks after the fact. They record what each release did,
taken from the commit that bumped VERSION, and each names its sha. They do
not explain why, because nothing on disk says why -- and a made-up rationale
in the file whose job is to be the record is worse than an admitted gap.

## [v0.5.0] - 2026-07-21

Phase 4 complete. Registries at 100 configs / 36 families / 20 missions /
8 heroes, every family placed, engine evidence stamped throughout. The
`bank_job` P0 record backfilled.

Reconstructed from `79b0db3`. That commit's subject does not name a version;
it is the next commit after 0.4.0 to touch VERSION, and VERSION reads 0.5.0.
The factory manifest's note for this tool reports the same four numbers.

## [v0.4.0] - 2026-07-21

75 configs / 28 families / 12 missions / 4 heroes registered, all
engine-stamped.

Reconstructed from `b93273f`.

## [v0.3.0] - 2026-07-20

40 configs / 16 families / 6 missions registered, all engine gates stamped.

Reconstructed from `a74119a`.

## [v0.2.0] - 2026-07-19

The first registrations beyond the reference set: 10 Phase 1 configs and
2 missions, all engine gates stamped.

Reconstructed from `a4002e4`.

## [v0.1.1] - 2026-07-18

Reference records stamped PASS on all engine gates.

Reconstructed from `22b4c79`.

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


def _apply(root: Path, *, check: bool) -> int:
    p = root / TARGET
    if not p.is_file():
        print(f"REFUSING: {TARGET} is not here")
        return 1
    raw = p.read_bytes()
    body = raw.decode("utf-8")
    eol = _eol(body)

    if "## [v0.5.0]" in body:
        print("  already applied")
        return 0
    a, n = _as(ANCHOR, eol), _as(NEW, eol)
    if body.count(a) != 1:
        print(f"REFUSING: the title block occurs {body.count(a)} time(s), "
              f"expected 1")
        return 1
    if "## [v0.1.0]" not in body:
        print("REFUSING: the existing v0.1.0 entry is not where it was")
        return 1

    out = body.replace(a, n, 1)
    data = out.encode("utf-8")
    if check:
        print(f"  would patch  {TARGET}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})")
        return 0
    side = p.with_suffix(p.suffix + SIDECAR)
    if not side.is_file():
        side.write_bytes(raw)
    p.write_bytes(data)
    print(f"  patched      {TARGET}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    text = (root / TARGET).read_text(encoding="utf-8")
    v = (root / "pipeline/VERSION").read_text(encoding="utf-8").strip()

    for want in ("v0.1.0", "v0.1.1", "v0.2.0", "v0.3.0", "v0.4.0", "v0.5.0"):
        check(f"one {want} entry", text.count(f"## [{want}]") == 1)

    heads = re.findall(r"^##\s*\[v?([0-9]+\.[0-9]+\.[0-9]+)\]", text, re.M)
    check("newest first: v0.5.0 is the top heading", heads[:1] == ["0.5.0"])
    check("descending order", heads == sorted(
        heads, key=lambda s: tuple(int(x) for x in s.split(".")), reverse=True))
    check("VERSION still says 0.5.0 -- the record moved, not the release",
          "0.5.0" in v)
    check("the newest entry now matches VERSION",
          heads[0] == "0.5.0" and "0.5.0" in v)
    check("every reconstructed entry names its commit",
          all(s in text for s in ("79b0db3", "b93273f", "a74119a",
                                  "a4002e4", "22b4c79")))
    check("the reconstruction is declared, not hidden",
          "RECONSTRUCTED on 2026-08-14" in text)
    check("the original v0.1.0 entry is untouched",
          "First release: the production registrar." in text)

    # And the instrument that found this must now read it as clean.
    lf = str((root / "level_factory").resolve())
    if lf not in sys.path:
        sys.path.insert(0, lf)
    try:
        import importlib
        contracts = importlib.import_module("packages.tools.contracts")
        importlib.reload(contracts)
        got = contracts.newest_changelog_entry(root / "pipeline")
        check(f"verify-manifest's reader sees {got}", got == "0.5.0")
        check("and calls it agreement",
              contracts.self_disagreement(v, got) is None)
    except Exception as exc:      # level_factory 0.25.0 not applied yet
        print(f"  skip  contracts check ({type(exc).__name__}: {exc})")

    print()
    print("  pipeline agrees with itself" if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")

    if "--selftest" in argv:
        return selftest(root)

    if "--revert" in argv:
        p = root / TARGET
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            print(f"  no sidecar for {TARGET}")
            return 1
        p.write_bytes(side.read_bytes())
        print(f"  reverted     {TARGET}")
        return 0

    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("  python patches\\patch_pipeline_changelog.py --selftest")
        print()
        print("  then, INSIDE pipeline (VERSION does not move -- no tag):")
        print("    git -C pipeline add -A")
        print('    git -C pipeline commit -m "backfill the CHANGELOG for '
              '0.1.1 through 0.5.0"')
        print("    git -C pipeline push")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
