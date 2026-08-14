r"""level_factory 0.29.0, corrected BEFORE it is committed.

    python patch_lf_029b.py --check
    python patch_lf_029b.py
    python patch_lf_029b.py --selftest
    python patch_lf_029b.py --revert

Run from the FACTORY ROOT, AFTER patch_lf_029.py and BEFORE the 0.29.0
commit. VERSION does not move -- 0.29.0 was never tagged.

WHY

0.29.0 applied, selftest 29 of 29, unit suite 579 passed. Then the export:

    [export] the functional lock for lot_demo_001 predates the current
             signature definitions; nothing was compared. Recompute it with
             approve --gate functional_shell_locked.
    export blocked by functional regression:
    <nothing>

It blocked. On a schema bump. With an empty list of reasons.

`docs/FUNCTIONAL_LOCK.md` says, in the paragraph that argued for this design:
"reporting it as drift would block every export on a version bump and teach
the next reader that drift means nothing." 0.29.0's own CHANGELOG entry
repeats it. I then blocked every export on a version bump -- not through
`drift`, which is empty exactly as designed, but through `passed=False`,
which `cmd_export` reads as the block signal.

Reasoning carefully about one field and then routing the same failure through
a different one is a new variant of the pattern, and worth its own line in
the record: the doc and the code disagreed, and the doc was right.

THE EMPTY REASON IS ITS OWN DEFECT

`export blocked by functional regression:` followed by nothing at all. That
header prints unconditionally and the detail comes from a loop over `drift`.
Any future blocking condition that is not a drift entry produces the same
silence. It now says what it blocked on, or says that it does not know.

WHAT CHANGES

  * `blocks_export(result)` -- one predicate, in lock.py, next to the result
    it reads. `cmd_export` calls it. It is a pure function of a
    RegressionResult, so the selftest exercises the actual decision rather
    than asserting that a line of source contains a substring. That is the
    third time today a check confirmed the presence of a mechanism instead of
    its behaviour, and this is the shape that stops it.
  * A schema mismatch does NOT block. `passed` stays False -- a comparison
    that did not happen did not pass, and that is still true -- but it is not
    what gates the export.
  * The block message names its reason or admits it has none.

WHAT IS STILL TRUE

An export against a stale lock now proceeds with a printed warning. That is
deliberate and it is the doc's position: the lock is regenerable, the skew is
this release's own doing, and refusing to ship a level because a hash format
changed is the behaviour that gets gates deleted. Recompute the lock and the
warning goes away.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

LOCK = "level_factory/packages/approvals/lock.py"
COMMANDS = "level_factory/apps/cli/commands/__init__.py"
CHANGELOG = "level_factory/CHANGELOG.md"
P029 = "patches/patch_lf_029.py"
SIDECAR = ".pre_029b"

EDITS: list[tuple[str, str, str]] = [
    # ANCHORED AFTER THE DATACLASS, NOT AFTER A FIELD. The first cut of this
    # patch appended the function to `needs_recompute: bool = False`, which is
    # NOT the last line of RegressionResult -- `coverage` follows it. That cut
    # the dataclass in half and orphaned `coverage` as a module-level
    # statement, so RegressionResult(coverage=...) raised TypeError. The
    # selftest missed it (it constructs results without coverage); the unit
    # suite caught it in three tests.
    (LOCK,
     "\n\ndef verify_no_drift(\n",

     "\n"
     "\n"
     "def blocks_export(result: RegressionResult) -> bool:\n"
     '    """Does this result stop an export?\n'
     "\n"
     "    ONE PREDICATE, HERE, so it can be tested. The first cut of 0.29.0\n"
     "    left the decision inline in `cmd_export` as `if not\n"
     "    result.passed`, and a schema mismatch -- which sets `passed` False\n"
     "    because nothing was compared -- blocked every export. The doc had\n"
     "    argued against exactly that, in those words, one release earlier.\n"
     "\n"
     "    A schema mismatch does NOT block. The lock is regenerable, the skew\n"
     "    is this release's own doing, and refusing to ship a level because a\n"
     "    hash format changed is how a gate gets deleted. `passed` stays False\n"
     "    -- a comparison that did not happen did not pass -- it simply is not\n"
     "    what gates the export.\n"
     '    """\n'
     "    return not result.passed and not result.needs_recompute\n"
     "\n"
     "\ndef verify_no_drift(\n"),

    (COMMANDS,
     "        if not regression.passed:\n"
     '            print("export blocked by functional regression:", file=sys.stderr)\n'
     "            for d in regression.drift:\n"
     '                print(f"  - {d}", file=sys.stderr)\n'
     "            return EXIT_BLOCKED\n",

     "        if blocks_export(regression):\n"
     '            print("export blocked by functional regression:",\n'
     "                  file=sys.stderr)\n"
     "            for d in regression.drift:\n"
     '                print(f"  - {d}", file=sys.stderr)\n'
     "            if not regression.drift:\n"
     "                # THE HEADER USED TO PRINT ALONE. A blocked export whose\n"
     "                # reasons are an empty list tells a reader nothing and\n"
     "                # reads like a crash. If a future condition blocks\n"
     "                # without producing drift entries, it says so.\n"
     '                print("  - no drift entries; the block came from '
     'somewhere\\n"\n'
     '                      "    other than a signature comparison. This is a '
     'bug\\n"\n'
     '                      "    in level_factory, not a problem with the '
     'mission.",\n'
     "                      file=sys.stderr)\n"
     "            return EXIT_BLOCKED\n"),

    (COMMANDS,
     "        from packages.approvals.lock import FunctionalLock, verify_no_drift\n",
     "        from packages.approvals.lock import (FunctionalLock,\n"
     "                                             blocks_export,\n"
     "                                             verify_no_drift)\n"),

    (CHANGELOG,
     "SCHEMA v0.2, AND A MISMATCH IS NOT DRIFT\n",

     "AND THEN IT BLOCKED THE EXPORT ANYWAY, WHICH IS THE ENTRY\n"
     "\n"
     "The selftest passed 29 of 29 and the unit suite passed. Then the export\n"
     "printed the schema warning and stopped:\n"
     "\n"
     "    export blocked by functional regression:\n"
     "    <nothing>\n"
     "\n"
     "`drift` was empty, exactly as designed. `passed` was False -- also as\n"
     "designed, because nothing was compared -- and `cmd_export` reads\n"
     "`passed` as the block signal. So a version bump blocked every export,\n"
     "which is the outcome `docs/FUNCTIONAL_LOCK.md` argued against in those\n"
     "words, and which the paragraph below repeats. The doc and the code\n"
     "disagreed and the doc was right.\n"
     "\n"
     "Reasoning carefully about one field and then routing the same failure\n"
     "through another is a new variant of a pattern this factory has now hit\n"
     "four times in two days. The fix is shaped to stop it: the decision is a\n"
     "named predicate, `blocks_export(result)`, living beside the result it\n"
     "reads, so a test can exercise the actual decision instead of asserting\n"
     "that a line of source contains a substring.\n"
     "\n"
     "The empty reason was a second defect. `export blocked by functional\n"
     "regression:` printed its header unconditionally and its detail from a\n"
     "loop over `drift`, so any blocking condition that is not a drift entry\n"
     "produced a bare header. It now names its reason or says it has none and\n"
     "calls that a bug in level_factory.\n"
     "\n"
     "An export against a stale lock proceeds with a warning. The lock is\n"
     "regenerable, the skew is this release's own doing, and refusing to ship\n"
     "a level because a hash format changed is how a gate gets deleted.\n"
     "\n"
     "SCHEMA v0.2, AND A MISMATCH IS NOT DRIFT\n"),
]

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
    v = (root / "level_factory" / "VERSION").read_text(encoding="utf-8")
    if "0.29.0" not in v:
        print(f"REFUSING: level_factory/VERSION says {v.strip()!r}, not "
              f"0.29.0 -- run patch_lf_029.py first")
        return 1

    by_file: dict[str, list[tuple[str, str]]] = {}
    for rel, old, new in EDITS:
        by_file.setdefault(rel, []).append((old, new))

    for rel, edits in by_file.items():
        p = root / rel
        if not p.is_file():
            print(f"REFUSING: {rel} is not here")
            return 1
        raw = p.read_bytes()
        body = raw.decode("utf-8")
        if body.count(_CRLF):
            print(f"REFUSING: {rel} has CRLF line endings; these anchors are LF")
            return 1
        out, done = body, 0
        for old, new in edits:
            if new in out:
                done += 1
                continue
            if out.count(old) != 1:
                print(f"REFUSING: {rel} -- an anchor occurs {out.count(old)} "
                      f"time(s), expected 1:\n    "
                      f"{old.strip().splitlines()[0][:72]}")
                return 1
            out = out.replace(old, new, 1)
        if done == len(edits):
            print(f"  already applied  {rel}")
            continue
        if rel.endswith(".py"):
            try:
                compile(out, str(p), "exec")
            except SyntaxError as exc:
                print(f"REFUSING: {rel} -- does not parse after the edit: {exc}")
                return 1
        data = out.encode("utf-8")
        if data == raw:
            print(f"  already applied  {rel}")
            continue
        if check:
            print(f"  would patch  {rel}  {len(raw):,} -> {len(data):,} bytes "
                  f"({len(data) - len(raw):+,})")
            continue
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(raw)
        p.write_bytes(data)
        print(f"  patched      {rel}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def selftest(root: Path) -> int:
    import importlib
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    lf = str((root / "level_factory").resolve())
    if lf not in sys.path:
        sys.path.insert(0, lf)
    lk = importlib.import_module("packages.approvals.lock")
    importlib.reload(lk)

    R = lk.RegressionResult
    B = lk.blocks_export

    # THE DECISION ITSELF, not the source that expresses it.
    check("a clean pass does not block",
          B(R(mission_id="m", passed=True)) is False)
    check("real drift blocks",
          B(R(mission_id="m", passed=False,
              drift=["collision_fingerprint changed after art pass"]))
          is True)
    check("A SCHEMA MISMATCH DOES NOT BLOCK -- the whole point",
          B(R(mission_id="m", passed=False, drift=[],
              needs_recompute=True)) is False)
    check("and neither does a vacuous lock that still compared cleanly",
          B(R(mission_id="m", passed=True, vacuous_lock=True,
              site_unguarded=True)) is False)
    check("a lock that is BOTH stale and drifting still does not block",
          B(R(mission_id="m", passed=False, drift=["x"],
              needs_recompute=True)) is False)

    cmds = (root / COMMANDS).read_text(encoding="utf-8")
    check("cmd_export asks the predicate rather than reading passed",
          "if blocks_export(regression):" in cmds
          and "if not regression.passed:" not in cmds)
    check("and imports it",
          "blocks_export," in cmds)
    check("a block with no drift entries explains itself",
          "no drift entries; the block came from somewhere" in cmds)
    check("and calls that a bug here, not a problem with the mission",
          "bug\\n" in cmds and "not a problem with the" in cmds)

    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    flat = " ".join(cl.split())
    check("0.29.0 is still one entry and was not renumbered",
          cl.count("## [0.29.0]") == 1 and "## [0.29.1]" not in cl)
    check("the entry records that it blocked anyway",
          "AND THEN IT BLOCKED THE EXPORT ANYWAY" in cl)
    check("and that the doc was right and the code was not",
          "the doc was right" in flat)
    check("and names the new variant of the pattern",
          "routing the same failure through another" in flat)
    check("and records the empty reason as its own defect",
          "bare header" in flat)

    print()
    print("  the decision is a predicate now, and a schema bump ships"
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
        for rel in (LOCK, COMMANDS, CHANGELOG):
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
        print("    python patches\\patch_lf_029b.py --selftest")
        print("    python -m pytest level_factory/tests/unit -q")
        print()
        print("  THEN THE EXPORT MUST SUCCEED, with the schema warning:")
        print("    python -m level_factory -C workspaces\\lot-demo-ws \\")
        print("        export lot_demo_001 --mode portable-godot")
        print()
        print("  expect the 'predates the current signature definitions' line")
        print("  AND an 'exported lot_demo_001' line after it.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
