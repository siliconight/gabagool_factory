r"""factory 1.20.0 -- the functional lock says what it is guarding.

    python patch_manifest_120.py --check
    python patch_manifest_120.py
    python patch_manifest_120.py --selftest
    python patch_manifest_120.py --revert

Run from the FACTORY ROOT, AFTER level_factory is committed and tagged
v0.28.0.

WHAT MOVES

    level_factory   0.27.0  -> 0.28.0
    factory_version 1.19.0  -> 1.20.0

Nine tools unchanged.

WHAT 0.28.0 DOES, AND WHAT IT DELIBERATELY DOES NOT

1.19.0 recorded that every functional lock this factory has written protects
nothing, and named the cause: `site.site.gameplay.json` publishes twenty
top-level keys and none of the eleven `_merged_gameplay` reads. Lot and Deli
name the same concepts differently.

0.28.0 is NOT that fix. Mapping the vocabularies is a contract question
between two tool repos and the obvious-looking pairs have not been opened.
0.28.0 is the reason nobody noticed for months: `compute_lock` would write a
lock guarding nothing, report success, and hand `verify_no_drift` something
that passes against anything. Now it measures what it protects, records it in
the lock, and `cmd_export` warns when the post-art check passes on that
basis.

WHAT WAS RUN

    export lot_demo_001 --mode portable-godot
      -> [export] WARNING the functional lock for lot_demo_001 protects no
         site data -- every signature it checks is filled from the Deli side.
         The post-art regression check passed on that basis, which is weaker
         than it reads.
    level_factory unit suite: 579 passed, 1 skipped

That warning is the deliverable. It did not appear on the first two attempts,
which is the part worth reading.

TWO DEFECTS FOUND AFTER 0.28.0's SELFTEST WENT GREEN, BOTH BY RUNNING IT

The first: the guard could not fire. It read `lock.coverage`, which only
exists on locks written by 0.28.0 or later -- so on every lock that exists, it
was empty. The selftest had asserted that behaviour as a virtue. Now
`verify_no_drift` measures from the files it is handed, which were open in
front of it the whole time.

The second: `vacuous` was the wrong predicate. It means all three signatures
are empty; Deli's two `stair_systems` keep one non-empty, so a lock guarding
no site data still reads as partly alive. The condition that describes every
lock here is `guards_no_site`. Found by simulating against the real key shape
AFTER the first correction was already written.

THREE RELEASES IN A ROW NOW

0.27.0 shipped a manifest whose `tools` block held adapter versions. Its
correction shipped a NameError. 0.28.0 shipped a guard that could not fire.
Every selftest was green and every check was true -- each was about the
mechanism rather than the outcome. What caught all three was opening the
artifact and running the command.

WHAT WAS NOT RUN

No mission re-run, no re-grade, no walk sweep, no pack load check. `pytest
tests` still aborts in collection on `_COMPOSER_SOURCES`. `pure-shell` still
has not been re-exported since 0.26.0. No portability run for this bump: the
package contents are unchanged by 0.28.0, which touches the lock and the CLI.

The description is not rewritten, for the reason 1.17.0 gave.

OPEN

The vocabulary mapping, which is the actual repair, and
`LOCK_COVERAGE_ENFORCED` stays False until it exists and one real mission
produces a non-vacuous lock. The `seed_XXXX` marker on disk -- 0.28.0 refuses
new bad ones and validates before recording, but does not rewrite data.
`_selected_lot_out` still resolves jobs from that marker, so `graybox_dir`
for lot_demo_001 is still a dead path. `pyproject.toml` still says 0.22.0.
57 stale buildings; `cbp`, `night_pawn`, `primos_pizza` still fail nav_gate;
`laser_tag` still has no CHANGELOG.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

MANIFEST = "factory.manifest.json"
CHANGELOG = "CHANGELOG.md"
SIDECAR = ".pre_120"

PINS: dict[str, tuple[str, str]] = {
    "level_factory": ("0.27.0", "0.28.0"),
}

OLD_FV, NEW_FV = "1.19.0", "1.20.0"

#: Every factory entry has been inserted after this same preamble, so the
#: newest entry stays newest.
ANCHOR = "own CHANGELOG.\n\n"

ENTRY = """## [factory-v1.20.0] - 2026-08-14

level_factory 0.27.0 -> 0.28.0. The other nine tools are unchanged from
factory-v1.19.0.

1.19.0 recorded that every functional lock this factory has written protects
nothing, and named the cause: Lot and Deli publish different vocabularies and
`_merged_gameplay` is written in Deli's. 0.28.0 is NOT that fix -- mapping
them is a contract question between two tool repos. It is the reason nobody
noticed for months.

WHAT CHANGED

`compute_lock` now measures what it protects on every call and stores it in
the lock as `coverage`, including `site_publishes_unread` -- the site's own
keys that nothing here reads, which is the vocabulary gap written beside the
hashes. `verify_no_drift` measures the same thing from the files it is
handed. `cmd_export` warns when the post-art check passes against a lock that
guards no site data.

`cmd_approve` now refuses a `--candidate` that cannot name a real candidate,
and refuses it BEFORE recording the approval, which it did not: `store.record`
ran first, so a rejected candidate would still have left an approved gate
behind it.

`LOCK_COVERAGE_ENFORCED` is False, for the reason `CLOSURE_ENFORCED` was:
every lock here is vacuous today and enforcing would refuse the gate for
every mission. The measurement always runs; the flag only decides whether it
stops anything.

WHAT WAS RUN

    export lot_demo_001 --mode portable-godot
      -> [export] WARNING the functional lock for lot_demo_001 protects no
         site data -- every signature it checks is filled from the Deli side
    unit suite: 579 passed, 1 skipped

THE WARNING TOOK THREE ATTEMPTS, AND THAT IS THE ENTRY

0.28.0's selftest passed 27 of 27 and the export printed nothing. The guard
read `lock.coverage`, which only exists on locks written by 0.28.0 or later --
empty on every lock that exists. The selftest had asserted that behaviour as
a virtue.

The correction still did not fire. `vacuous` means all three signatures are
empty, and Deli's two `stair_systems` keep one alive, so a lock guarding no
site data reads as partly healthy. The predicate that describes every lock
here is `guards_no_site`. Found by simulating against the real key shape
after the first correction was written.

That is three releases running: 0.27.0's manifest shipped adapter versions
under `tools`; its correction shipped a NameError; 0.28.0 shipped a guard
that could not fire. Every selftest was green and every check was true. Each
checked the mechanism instead of the outcome. What caught all three was
opening the artifact and running the command.

WHAT WAS NOT RUN

No mission re-run, no re-grade, no walk sweep, no pack load check, and no
portability run -- 0.28.0 does not change package contents. `pytest tests`
still aborts in collection on `_COMPOSER_SOURCES`. `pure-shell` still has not
been re-exported since 0.26.0. The description is not rewritten.

OPEN

The vocabulary mapping. The `seed_XXXX` marker on disk, which 0.28.0 refuses
to create again but does not rewrite. `_selected_lot_out` still resolving
jobs from it. `pyproject.toml` at 0.22.0. 57 stale buildings. `cbp`,
`night_pawn` and `primos_pizza` failing nav_gate. `laser_tag` without a
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
    check("it says this is not the vocabulary fix",
          "is NOT that fix" in cl and "contract question" in cl)
    check("it names the evidence: the warning actually fired",
          "protects no\n         site data" in cl or "protects no" in cl)
    check("it records that the warning took three attempts",
          "THREE ATTEMPTS" in cl and "could not fire" in cl)
    check("and that the selftest asserted the bug as a virtue",
          "as\na virtue" in cl)
    check("it names the predicate that was wrong",
          "guards_no_site" in cl and "stair_systems" in cl)
    check("it says the flag stays off and why",
          "LOCK_COVERAGE_ENFORCED" in cl and "CLOSURE_ENFORCED" in cl)
    # Whitespace-collapsed: the phrase wraps across a line in the entry, and
    # an assertion that forgets that fails on typography, not substance.
    flat = " ".join(cl.split())
    check("it says what was NOT run",
          "WHAT WAS NOT RUN" in cl and "no portability run" in flat)
    check("it records the approve ordering bug",
          "store.record" in cl and "BEFORE recording" in cl)
    check("and still names the open items",
          "vocabulary mapping" in cl and "pyproject.toml" in cl
          and "seed_XXXX" in cl)
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
        print("    python patches\\patch_manifest_120.py --selftest")
        print('    git commit -am "factory 1.18.0 -- the export package has a '
              'name, and a real run proved it"')
        print(f'    git tag -a factory-v{NEW_FV} -m "factory {NEW_FV}"')
        print("    git push --follow-tags")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
