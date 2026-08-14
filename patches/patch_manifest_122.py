r"""factory 1.22.0 -- the dark tests, and three roadmap items.

    python patch_manifest_122.py --check
    python patch_manifest_122.py
    python patch_manifest_122.py --selftest
    python patch_manifest_122.py --revert

Run from the FACTORY ROOT, AFTER level_factory is committed and tagged
v0.32.0, and after patch_roadmap_43_45.py + roadmap_status.py --write.

WHAT MOVES

    level_factory   0.31.0  -> 0.32.0
    factory_version 1.21.0  -> 1.22.0

Nine tools unchanged.

WHAT 0.32.0 FOUND

`pytest level_factory/tests` had been aborting during collection on an
ImportError. I expected a stale import against a renamed symbol. Neither
`_COMPOSER_SOURCES` nor `_composer_fingerprint` existed anywhere in the
repository and `fingerprint_inputs` had no `composer` key -- the test was not
stale, it described a guard nobody built.

The guard is for a measured failure from 2026-08-05: a DC fix that did not
invalidate a cached compose, so `site_base.glb` came back byte-identical and
an invisible wall shipped. The presentation job EXECUTES DC's code, so its
output can change while every input hash stays identical.

AND THE COLLECTION ERROR WAS HIDING NINE FAILURES

One broken import takes a whole directory dark -- collection aborts before
any test in it runs -- so `tests/integration` and `tests/service` had both
been silent. With the import fixed, nine tests fail, and all nine trace to
one thing: `run --target presentation` plans no art stages. Roadmap item 43.

Whether those nine are pre-existing or were exposed by 0.32.0's new
`composer` fingerprint key -- which turns former cache hits into real runs --
is NOT established. The comparison is one revert and two runs, and it has not
been done. The item says so rather than assuming.

ROADMAP 43, 44, 45

    43  the CLI spelling that plans nothing
    44  Semantic Proxy Replacement -- art variants over graybox blocks, with
        the block's collision still authoritative
    45  Surface Dressing -- collisionless instanced detail geometry

44 and 45 come from three specifications written outside this repo. Both note
something worth repeating here: their acceptance test is the functional lock,
and until factory-v1.21.0 that lock hashed two Deli stair systems and would
have passed an art pass that bulldozed the site. It now protects 1,171
records. The lock work and the art-pass items were built in the wrong order
and it came out right.

Item 42's status was also false -- it read "nothing produces it yet" after
stage 1 shipped and a real package was verified. Corrected.

WHAT WAS RUN

    level_factory unit suite: 579 passed, 1 skipped
    pytest level_factory/tests: COLLECTS. 9 failed, the rest passed.
    roadmap_status.py --check: index matches its items

WHAT WAS NOT RUN

No mission re-run, no re-grade, no walk sweep, no pack load check, no
portability run. `pure-shell` still has not been re-exported since 0.26.0.
The description is not rewritten.

A KNOWN COST, STATED

`composer` is a new fingerprint key, so the next `--art` run recomposes every
mission once. That is correct for a guard whose premise is that a stale
compose is invisible, and it is the last time it happens for this reason.

OPEN

The nine failures and item 43 behind them. The 25 Deli collision nodes absent
from the assembled site -- a question for `lot`. `openings` undecidable
between the two files. `vertical_links` possibly needing a `kind` split.
Enforcement still narrower than the problem until a second and third mission
are measured. `pyproject.toml` at 0.22.0 against VERSION 0.32.0. 57 stale
buildings. `cbp`, `night_pawn`, `primos_pizza` failing nav_gate. `laser_tag`
without a CHANGELOG.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

MANIFEST = "factory.manifest.json"
CHANGELOG = "CHANGELOG.md"
SIDECAR = ".pre_122"

PINS: dict[str, tuple[str, str]] = {
    "level_factory": ("0.31.0", "0.32.0"),
}

OLD_FV, NEW_FV = "1.21.0", "1.22.0"

#: Every factory entry has been inserted after this same preamble, so the
#: newest entry stays newest.
ANCHOR = "own CHANGELOG.\n\n"

ENTRY = """## [factory-v1.22.0] - 2026-08-14

level_factory 0.31.0 -> 0.32.0. The other nine tools are unchanged from
factory-v1.21.0.

A GUARD THAT WAS NEVER BUILT, AND NINE FAILURES BEHIND ONE IMPORT

`pytest level_factory/tests` had been aborting during collection on an
ImportError for `_COMPOSER_SOURCES`. That looked like a stale import against
a renamed symbol. Neither `_COMPOSER_SOURCES` nor `_composer_fingerprint`
existed anywhere in the repository, and `fingerprint_inputs` had no
`composer` key. The test was not stale -- it described a guard nobody built,
and because collection aborted, nothing said so.

The guard is for a failure measured 2026-08-05: `strip_greybox_base` was
fixed in Deli Counter, DC's suite went green, `run --art --force` reported
its stages SUCCEEDED, this job reported `cache`, and the composed
`site_base.glb` came back byte-identical with the invisible wall still in it.
The presentation job EXECUTES DC's code rather than only reading its data, so
its output can change while every input hash stays identical.

0.32.0 implements it. Sources are measured, not guessed: the import closure
of `portable_building` in DC 0.89.0 is itself plus `themed_tscn.py`.
`circulation.py` is declared and absent from 0.89.0 -- an absent declared
source is skipped, never faked, because a placeholder hash is identical
across every DC version that lacks the file.

ONE BROKEN IMPORT TOOK A DIRECTORY DARK

Collection aborts before any test in the directory runs, so
`tests/integration` and `tests/service` had both been silent. With the import
fixed, nine tests fail and all nine trace to one cause: `run --target
presentation` plans no art stages. Roadmap item 43.

Whether those nine are pre-existing or were exposed by the new `composer`
fingerprint key -- which turns former cache hits into real runs -- is NOT
established. The comparison is one revert and two runs and it has not been
done. The item records that rather than assuming either.

ROADMAP 43, 44, 45

43 is the CLI spelling above. 44 is Semantic Proxy Replacement: art variants
standing in for graybox blocks with the block's collision still
authoritative, a shape-to-category-to-variants abstraction, and Pixelcoat
skinning the families Zoo owns. 45 is Surface Dressing: collisionless
instanced detail for relief and parallax, placed from a deterministic
manifest, post-lock.

Both name the same thing as their acceptance test, and it is worth repeating
here: the functional lock. Until factory-v1.21.0 that lock hashed two Deli
stair systems and would have passed an art pass that bulldozed the site. It
now protects 1,171 records. The lock work and these items were built in the
wrong order and it came out right.

Item 42's status was corrected -- it still read "nothing produces it yet"
after stage 1 shipped and a real package was built and verified.

WHAT WAS RUN

    level_factory unit suite     579 passed, 1 skipped
    pytest level_factory/tests   COLLECTS; 9 failed, rest passed
    roadmap_status.py --check    index matches its items

WHAT WAS NOT RUN

No mission re-run, no re-grade, no walk sweep, no pack load check, no
portability run. `pure-shell` has not been re-exported since 0.26.0. The
description is not rewritten.

A COST, STATED IN ADVANCE

`composer` is a new fingerprint key, so the next `--art` run recomposes every
mission once. Correct for a guard whose premise is that a stale compose is
invisible, and the last time it happens for this reason.

OPEN

The nine failures and item 43. The 25 Deli collision nodes absent from the
assembled site, a question for `lot`. `openings` undecidable from the two
files. `vertical_links` possibly needing a `kind` split. Enforcement narrower
than the problem until a second and third mission are measured.
`pyproject.toml` at 0.22.0 against VERSION 0.32.0. 57 stale buildings.
`cbp`, `night_pawn`, `primos_pizza` failing nav_gate. `laser_tag` without a
CHANGELOG.

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


def _pin_anchor(tool: str, ver: str) -> str:
    return (f'"{tool}": {{\n      "version": "{ver}",\n'
            f'      "tag": "v{ver}",')


def newest_entry(path: Path) -> str | None:
    if not path.is_file():
        return None
    m = re.search(r"^##\s*\[?v?([0-9]+\.[0-9]+\.[0-9]+)\]?",
                  path.read_text(encoding="utf-8", errors="replace"), re.M)
    return m.group(1) if m else None


def version_of(path: Path) -> str | None:
    if not path.is_file():
        return None
    m = re.search(r"[0-9]+\.[0-9]+\.[0-9]+",
                  path.read_text(encoding="utf-8", errors="replace"))
    return m.group(0) if m else None


def _preflight(root: Path) -> int:
    """Refuse to pin a version the tool on disk does not claim.

    The manifest is the certified COMBINATION; a pin is a claim about what is
    installed. Writing one the tool does not support is the exact failure the
    manifest exists to prevent, so this runs before anything is touched.
    """
    bad = 0
    for tool, (_old, new) in PINS.items():
        d = root / tool
        v = version_of(d / "VERSION")
        c = newest_entry(d / "CHANGELOG.md")
        if v != new:
            print(f"REFUSING: {tool}/VERSION says {v}, not {new} -- run its "
                  f"patch first")
            bad = 1
        elif c is not None and c != new:
            print(f"REFUSING: {tool}'s newest CHANGELOG entry is {c}, not "
                  f"{new} -- the tool does not agree with itself yet")
            bad = 1
    return bad


def _apply(root: Path, *, check: bool) -> int:
    if _preflight(root):
        return 1

    mp, cp = root / MANIFEST, root / CHANGELOG
    mraw = mp.read_bytes()
    mbody = mraw.decode("utf-8")

    if f'"factory_version": "{NEW_FV}"' in mbody:
        print(f"  already applied  {MANIFEST}")
    else:
        out = mbody
        for tool, (old, new) in PINS.items():
            a = _pin_anchor(tool, old)
            if out.count(a) != 1:
                print(f"REFUSING: {tool} pin anchor occurs {out.count(a)} "
                      f"time(s), expected 1 (already {new}?)")
                return 1
            out = out.replace(a, _pin_anchor(tool, new), 1)
        fv = f'"factory_version": "{OLD_FV}"'
        if out.count(fv) != 1:
            print(f"REFUSING: factory_version {OLD_FV} occurs {out.count(fv)} "
                  f"time(s)")
            return 1
        out = out.replace(fv, f'"factory_version": "{NEW_FV}"', 1)

        try:
            data = json.loads(out)
        except ValueError as exc:
            print(f"REFUSING: the result is not valid JSON: {exc}")
            return 1
        for tool, (_o, new) in PINS.items():
            if data["tools"][tool]["version"] != new:
                print(f"REFUSING: {tool} reads "
                      f"{data['tools'][tool]['version']} after the edit")
                return 1
        # Nine tools must be untouched. A one-pin patch that moved two would
        # be a certified set nobody certified.
        before = json.loads(mbody)["tools"]
        for name in before:
            if name in PINS:
                continue
            if data["tools"][name] != before[name]:
                print(f"REFUSING: {name} changed and this patch does not "
                      f"move it")
                return 1

        blob = out.encode("utf-8")
        if check:
            print(f"  would patch  {MANIFEST}  {len(mraw):,} -> {len(blob):,} "
                  f"bytes ({len(blob) - len(mraw):+,})")
        else:
            side = mp.with_suffix(mp.suffix + SIDECAR)
            if not side.is_file():
                side.write_bytes(mraw)
            mp.write_bytes(blob)
            print(f"  patched      {MANIFEST}  {len(mraw):,} -> {len(blob):,} "
                  f"bytes  sha256 {_sha(blob)[:16]}")

    craw = cp.read_bytes()
    cbody = craw.decode("utf-8")
    if f"## [factory-v{NEW_FV}]" in cbody:
        print(f"  already applied  {CHANGELOG}")
        return 0
    eol = _eol(cbody)
    a = _as(ANCHOR, eol)
    if cbody.count(a) != 1:
        print(f"REFUSING: the CHANGELOG preamble occurs {cbody.count(a)} "
              f"time(s), expected 1")
        return 1
    cout = cbody.replace(a, a + _as(ENTRY, eol), 1)
    cblob = cout.encode("utf-8")
    if check:
        print(f"  would patch  {CHANGELOG}  {len(craw):,} -> {len(cblob):,} "
              f"bytes ({len(cblob) - len(craw):+,})")
        return 0
    side = cp.with_suffix(cp.suffix + SIDECAR)
    if not side.is_file():
        side.write_bytes(craw)
    cp.write_bytes(cblob)
    print(f"  patched      {CHANGELOG}  {len(craw):,} -> {len(cblob):,} bytes "
          f"({len(cblob) - len(craw):+,})  sha256 {_sha(cblob)[:16]}")
    return 0


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    data = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    check(f"factory_version is {NEW_FV}",
          data.get("factory_version") == NEW_FV)

    for name, entry in sorted(data["tools"].items()):
        d = root / str(entry.get("path", name))
        pin, tag = entry.get("version"), entry.get("tag")
        v, c = version_of(d / "VERSION"), newest_entry(d / "CHANGELOG.md")
        check(f"{name:<14} tag {tag} matches pin", tag == f"v{pin}")
        if c is None:
            check(f"{name:<14} pin {pin} == VERSION {v} (no CHANGELOG)",
                  pin == v)
        else:
            check(f"{name:<14} pin {pin} == VERSION {v} == CHANGELOG {c}",
                  pin == v == c)

    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    check(f"one {NEW_FV} entry", cl.count(f"## [factory-v{NEW_FV}]") == 1)
    check("the older entries survive",
          all(s in cl for s in ("## [factory-v1.17.0]", "## [factory-v1.16.0]",
                                "## [factory-v1.0.0]")))
    check("it is the newest entry",
          cl.index(f"factory-v{NEW_FV}") < cl.index(f"factory-v{OLD_FV}"))
    flat = " ".join(cl.split())
    check("it says the guard was never built",
          "described a guard nobody built" in flat)
    check("and names the failure it is for",
          "strip_greybox_base" in cl and "invisible wall" in flat)
    check("it explains how one import took a directory dark",
          "Collection aborts before any test" in flat)
    check("it refuses to assume the nine are pre-existing",
          "is NOT established" in flat and "has not been done" in flat)
    check("it names the three roadmap items",
          "Semantic Proxy Replacement" in cl and "Surface Dressing" in cl
          and "item 43" in flat)
    check("and that the lock is their acceptance test",
          "1,171 records" in flat and "wrong order" in flat)
    check("it records item 42's correction",
          "nothing produces it yet" in flat and "stage 1 shipped" in flat)
    check("it states the recompose cost in advance",
          "recomposes every mission once" in flat)
    check("it says what was NOT run",
          "WHAT WAS NOT RUN" in cl and "no portability run" in flat)
    check("and still names the open items",
          "25 Deli collision nodes" in flat and "pyproject.toml" in cl)
    check("the description still carries its own dated evidence, unrewritten",
          "Re-certified 2026-08-14" in data["description"])

    # And the claim the entry makes about pyproject is checked, not asserted.
    pp = root / "level_factory" / "pyproject.toml"
    if pp.is_file():
        m = re.search(r'^version\s*=\s*"([^"]+)"', pp.read_text(
            encoding="utf-8", errors="replace"), re.M)
        found = m.group(1) if m else None
        check(f"pyproject really does say 0.22.0 (found {found})",
              found == "0.22.0")

    # The instrument's own verdict over all ten tools.
    lf = str((root / "level_factory").resolve())
    if lf not in sys.path:
        sys.path.insert(0, lf)
    try:
        import importlib
        contracts = importlib.import_module("packages.tools.contracts")
        importlib.reload(contracts)
        results = contracts.verify_manifest(root)
        print()
        width = max(len(r.adapter_id) for r in results)
        for r in results:
            print(f"    {r.status:<13} {r.adapter_id:<{width}}  "
                  f"{r.message[:74]}")
        print(f"\n    worst: {contracts.worst_status(results)}")
        notok = [r.adapter_id for r in results if r.status != contracts.OK]
        check(f"every tool reads OK{'' if not notok else f' (not: {notok})'}",
              not notok)
    except Exception as exc:
        print(f"  skip  contracts check ({type(exc).__name__}: {exc})")

    print()
    print("  one pin moved, and the entry says what earned it"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / MANIFEST).is_file():
        raise SystemExit("run this from the factory root")

    if "--selftest" in argv:
        return selftest(root)

    if "--revert" in argv:
        bad = 0
        for rel in (MANIFEST, CHANGELOG):
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
        print("    python patches\\patch_manifest_122.py --selftest")
        print('    git commit -am "factory 1.18.0 -- the export package has a '
              'name, and a real run proved it"')
        print(f'    git tag -a factory-v{NEW_FV} -m "factory {NEW_FV}"')
        print("    git push --follow-tags")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
