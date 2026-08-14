r"""level_factory 0.24.0 -- the lockstep check learns to notice stale pins.

    python patch_lf_024.py --check
    python patch_lf_024.py
    python patch_lf_024.py --selftest
    python patch_lf_024.py --revert

Run from the FACTORY ROOT.

WHY THIS EXISTS AS ITS OWN BUMP. `patch_lf_manifest_staleness.py` changed
`contracts.py` and `cli/commands/__init__.py` AFTER level_factory was tagged
v0.23.0. Committing that without a bump would leave the tool's code newer
than the VERSION naming it -- which is precisely the condition the patch
itself was written to detect. The check would flag its own repo on the next
run, and it would be right.

So: 0.24.0, and the entry says what it does.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

VERSION = Path("level_factory/VERSION")
CHANGELOG = Path("level_factory/CHANGELOG.md")
SIDECAR = ".pre_024"

OLD_V, NEW_V = "0.23.0", "0.24.0"

ENTRY = """## [0.24.0] - A pin that matches a stale VERSION is not a pass

`verify-manifest` compared the manifest's pin against each tool's VERSION
file and stopped there. On 2026-08-14 that reported:

    OK  deli_counter    0.88.0 matches certified 0.88.0
    OK  level_factory   0.22.0 matches certified 0.22.0

while both tools had nineteen days of commits newer than the VERSION naming
them. Two numbers agreeing with each other, and with nothing on disk. The
same failure `deli_counter/build_freshness.py` exists for, and the same one
that made every recorded Laser Tag grade describe a draw that never shipped
-- this time in the check whose entire job is catching drift.

- **`packages/tools/contracts.py`:** new `STALE` status, ranked between
  UNKNOWN and DRIFT. Reached only from what would have been a bare OK: if
  the numbers already disagree the staleness question is moot and DRIFT's
  message is the more useful one. `ContractResult` carries
  `stale_because`, the file that outran VERSION, because naming it is the
  difference between a verdict and a place to look.
- **`stale_source()` asks git, not the filesystem.** The first cut compared
  mtimes and reported six of ten tools stale, every one naming
  `.gitignore`. Excluding `.gitignore` would only have moved the problem to
  the next non-source file -- an exclusion list always trails what gets
  added. History is the allow-list that cannot fall behind, and it is
  immune to fresh clones, which rewrite every mtime and no commit dates.
  Unknowable answers (no git, not a repo, no commit touching VERSION)
  report OK; a warning nobody can act on is worse than silence.
- **`cli/commands`:** STALE exits EXIT_FINDINGS, or EXIT_CONFIG under
  `--strict`, matching DRIFT. It wants the same thing doing.

First run against the real factory: 1 OK, 4 DRIFT, 5 STALE, where the
previous check said 8 OK and 2 DRIFT. Eight of ten tools had moved since
their versions were written and nothing was saying so.

KNOWN AND NOT ADDRESSED HERE: the CHANGELOG is a third number this does not
read. `lot`'s CHANGELOG documents 0.41.0 while its VERSION says 0.33.0 and
the manifest pins 0.32.0 -- three answers to one question, and this check
compares two of them.
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


def selftest(root: Path) -> int:
    bad = 0
    v = (root / VERSION).read_text(encoding="utf-8").strip()
    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    for label, ok in (("VERSION is 0.24.0", v == NEW_V),
                      ("CHANGELOG has the entry", "## [0.24.0]" in cl),
                      ("no duplicate heading", cl.count("## [0.24.0]") == 1)):
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")
    print()
    print("  ready to commit and tag" if not bad else f"  {bad} problem(s)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    vp, cp = root / VERSION, root / CHANGELOG
    if not vp.is_file():
        raise SystemExit(f"cannot find {VERSION} -- run from the factory root")

    if "--selftest" in argv:
        return selftest(root)

    if "--revert" in argv:
        bad = 0
        for p in (vp, cp):
            side = p.with_suffix(p.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {p.name}")
                bad = 1
                continue
            p.write_bytes(side.read_bytes())
            print(f"  reverted     {p.name}")
        return bad

    vraw = vp.read_bytes()
    vbody = vraw.decode("utf-8")
    craw = cp.read_bytes()
    cbody = craw.decode("utf-8")

    if NEW_V in vbody and "## [0.24.0]" in cbody:
        print("  already applied")
        return 0
    if OLD_V not in vbody:
        print(f"REFUSING: level_factory/VERSION does not say {OLD_V} "
              f"(found {vbody.strip()!r})")
        return 1
    if "## [0.24.0]" in cbody:
        print("REFUSING: the CHANGELOG already has a 0.24.0 entry")
        return 1

    veol, ceol = _eol(vbody), _eol(cbody)
    vout = vbody.replace(OLD_V, NEW_V, 1)
    cout = _as(ENTRY, ceol) + ceol + cbody

    if "--check" in argv:
        print(f"  would bump   VERSION  {OLD_V} -> {NEW_V}")
        print(f"  would prepend CHANGELOG.md  "
              f"+{len(cout.encode('utf-8')) - len(craw):,} bytes")
        return 0

    for p, raw in ((vp, vraw), (cp, craw)):
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(raw)
    vp.write_bytes(vout.encode("utf-8"))
    cp.write_bytes(cout.encode("utf-8"))
    print(f"  bumped       VERSION  {OLD_V} -> {NEW_V}")
    print(f"  prepended    CHANGELOG.md  sha256 "
          f"{_sha(cout.encode('utf-8'))[:16]}")
    print()
    print("  commit and tag INSIDE level_factory:")
    print("    git -C level_factory add -A")
    print('    git -C level_factory commit -m "0.24.0 -- verify-manifest '
          'notices a stale pin"')
    print("    git -C level_factory tag v0.24.0")
    print("    git -C level_factory push --follow-tags")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
