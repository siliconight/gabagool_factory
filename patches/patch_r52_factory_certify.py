#!/usr/bin/env python3
"""factory 1.25.0 -> 1.26.0: certify lot 0.42.0, and level_factory 0.40.0.

TWO TOOL MOVES, AND ONE OF THEM IS OVERDUE

`factory.manifest.json` pins `level_factory 0.39.0`. `level_factory/VERSION`
reads 0.40.0, tagged `v0.40.0` at `5bd29d1`, pushed to origin/main, clean tree,
commit message "0.40.0: one resource manifest per package, and it is the
current one" -- roadmap item 50's fix. The `factory-v1.25.0` changelog entry
says "level_factory 0.37.0 -> 0.39.0" and never mentions 0.40.0.

So the certified set does not contain the fix for item 50, which the roadmap
records as CLOSED. `patch_manifest_125.py` cut 1.25.0 covering LF through
0.39.0 and 0.40.0 landed afterwards with no factory bump behind it. That is a
new instance of the roadmap's standing "three version sources disagree" item,
and it is the one with teeth: the others are tools disagreeing about what is
installed, this is the certified set omitting a shipped fix.

`lot 0.41.0 -> 0.42.0` is roadmap item 51, and two of its three fixes change
shipped geometry.

THE .gitignore HAS MIXED LINE ENDINGS -- 32 CRLF and 26 LF, established by
reconciling a scratch dump against the source byte count. The house `_eol()`
REFUSES a mixed file, and correctly, because an anchored edit into one cannot
know which ending the next line wants. This change is APPEND-ONLY, which is a
different question with a safe answer: match the ending the file's own last
line uses, detected at runtime. That rule is implemented in `_append_eol` and
it does not normalise anything, so the mix survives untouched. Normalising
`.gitignore` is a separate change touching all 58 lines and is not done here.

USAGE

    python patches\\patch_r52_factory_certify.py --check
    python patches\\patch_r52_factory_certify.py --selftest
    python patches\\patch_r52_factory_certify.py
    python patches\\patch_r52_factory_certify.py --revert
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

TAG = "r52factory"

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "factory.manifest.json"
CHANGELOG = ROOT / "CHANGELOG.md"
GITIGNORE = ROOT / ".gitignore"


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def _sidecar(p: Path) -> Path:
    return p.with_name(p.name + ".pre_" + TAG)


def _eol(raw: bytes, who: str) -> str:
    """Strict: refuses a mixed file. Used for the two anchored-edit targets."""
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    if crlf and lf:
        raise SystemExit(f"REFUSING: {who} has mixed line endings "
                         f"({crlf} CRLF, {lf} LF).")
    if not crlf and not lf:
        raise SystemExit(f"REFUSING: {who} has no line endings at all.")
    return "\r\n" if crlf else "\n"


def _append_eol(raw: bytes) -> bytes:
    """The ending to append with, for a file that may legitimately be mixed.

    `.gitignore` here is 32 CRLF and 26 LF. The strict rule above refuses that,
    and should: an anchored edit into a mixed file cannot know which ending the
    line it is replacing wants. Appending is a narrower question -- the only
    ending that matters is the one already terminating the last line -- so this
    reads that and matches it, leaving every existing line alone.
    """
    if raw.endswith(b"\r\n"):
        return b"\r\n"
    if raw.endswith(b"\n"):
        return b"\n"
    # No terminator at the end at all: match whichever this file uses more, and
    # terminate the last line first so the appended block is not glued to it.
    return b"\r\n" if raw.count(b"\r\n") * 2 > raw.count(b"\n") else b"\n"


# ---------------------------------------------------------------------------
MANIFEST_EDITS = [
    ('"level_factory": {\n      "version": "0.39.0",\n      "tag": "v0.39.0",',
     '"level_factory": {\n      "version": "0.40.0",\n      "tag": "v0.40.0",'),
    ('"lot": {\n      "version": "0.41.0",\n      "tag": "v0.41.0",',
     '"lot": {\n      "version": "0.42.0",\n      "tag": "v0.42.0",'),
    ('"factory_version": "1.25.0",', '"factory_version": "1.26.0",'),
    # The notes are this manifest's own running record of what each version
    # did. Extending them is the pattern the existing text sets.
    ("mission-wide fail-fast meant one bad candidate took the other four down "
     "with it -- which is why the walktest could not be enforced.",
     "mission-wide fail-fast meant one bad candidate took the other four down "
     "with it -- which is why the walktest could not be enforced. 0.40.0 ships "
     "one resource manifest per package instead of two, and it is the one that "
     "is true; it was tagged on 2026-08-16 and sat UNCERTIFIED until "
     "factory-v1.26.0."),
    ("0.32.0 applies gravity only while airborne and probes three step heights "
     "instead of one, and says WHICH probe failed -- no headroom to lift is a "
     "finding about the stairwell, no room ahead is a finding about the "
     "obstacle.",
     "0.32.0 applies gravity only while airborne and probes three step heights "
     "instead of one, and says WHICH probe failed -- no headroom to lift is a "
     "finding about the stairwell, no room ahead is a finding about the "
     "obstacle. 0.42.0 plans cover for the crew spawn the scene actually ships "
     "and serves the crew's sightlines before the rest of the map's."),
]

CHANGELOG_ANCHOR = "## [factory-v1.25.0] - 2026-08-16\n"

CHANGELOG_ENTRY = """## [factory-v1.26.0] - 2026-08-16

lot 0.41.0 -> 0.42.0, level_factory 0.39.0 -> 0.40.0. The other eight tools
are unchanged from factory-v1.24.0.

LEVEL_FACTORY 0.40.0 WAS ALREADY SHIPPED AND WAS NOT IN THE SET

This is the more important half. `v0.40.0` was tagged and pushed on
2026-08-16, and the roadmap records item 50 as CLOSED on it -- one resource
manifest per package instead of two, the stale one dropped. But
factory-v1.25.0 was cut before it landed and pinned 0.39.0, and its changelog
entry says "level_factory 0.37.0 -> 0.39.0". Nothing bumped the set
afterwards, so for the life of 1.25.0 the certified set omitted a fix the
roadmap called closed. Found by reading the manifest rather than the handoff,
which asserted 0.40.0 was in.

The lesson is the same one the roadmap keeps relearning: a tool version and a
set version are two different claims, and closing an item against the first
says nothing about the second.

WHAT LOT 0.42.0 CHANGES

The cover in a shipped level is now planned for the crew spawn the scene
carries. It was not: `assemble` never cleared the crew spawn, so cover was
planned from inside a building while the walk scene shipped the cleared spawn
metres away. From in there almost every sightline reads as already broken, so
the planner reported zero open lines over a map that opened with a clear
51.9 m lane.

And the opening cover budget now reaches the crew. Twelve pieces were spent
longest-first across every marker pair, and on the test site none of the
twelve touched a line the crew stands on while six broke enemy-to-enemy
sightlines. Serving the crew's lines first, on the same budget, closes all
seven of them with three pieces.

`lot`'s suite went 328 passed / 8 failed -> 336 passed / 0 failed. Roadmap
item 51 is closed; two of the three mechanisms it proposed were refuted by
measurement.

Every cover measurement behind this was taken on a two-building yard fixture.
`lot_demo_001` still has not been re-exported since 0.39.0 -- now doubly
worth doing, because the five-building shape is untested against both the
0.40.0 export path and the new cover ordering.

"""

GITIGNORE_BLOCK = """
# Captured command output from debugging sessions -- regenerable, not history.
# These are the ones that had already accumulated at the root; new captures
# belong in _scratch/, which is ignored above. Enumerated rather than ruled
# because a blanket root rule would silently swallow a file somebody meant to
# track, and this repo's whole job is coordination data.
compose_diag.txt
compose_fail.txt
compose_findings.json
lux_gap.txt
real_tools.txt
suite.txt
unit_fail.txt
unlit_ab.txt
unlit_ab2.txt
"""


def _preflight():
    missing = [p for p in (MANIFEST, CHANGELOG, GITIGNORE) if not p.exists()]
    if missing:
        raise SystemExit("REFUSING: missing " + ", ".join(str(m) for m in missing))
    m = MANIFEST.read_bytes().decode("utf-8").replace("\r\n", "\n")
    c = CHANGELOG.read_bytes().decode("utf-8").replace("\r\n", "\n")
    g = GITIGNORE.read_bytes()
    problems = []
    for old, _new in MANIFEST_EDITS:
        if m.count(old) != 1:
            problems.append(f"manifest anchor found {m.count(old)}x: {old[:56]!r}")
    if c.count(CHANGELOG_ANCHOR) != 1:
        problems.append(f"changelog anchor found {c.count(CHANGELOG_ANCHOR)}x")
    if "## [factory-v1.26.0]" in c:
        problems.append("CHANGELOG.md already carries a factory-v1.26.0 entry")
    already = [ln for ln in GITIGNORE_BLOCK.split("\n")
               if ln and not ln.startswith("#")
               and ("\n" + ln + "\n") in ("\n" + g.decode("utf-8")
                                          .replace("\r\n", "\n") + "\n")]
    return m, c, g, problems, already


def _identity():
    for p in (MANIFEST, CHANGELOG, GITIGNORE):
        if p.exists():
            raw = p.read_bytes()
            crlf = raw.count(b"\r\n")
            lone = raw.count(b"\n") - crlf
            kind = "CRLF" if crlf and not lone else ("LF" if lone and not crlf
                                                     else "MIXED")
            print(f"  {p.name:24s} {len(raw):>7} B  {kind:5s} "
                  f"({crlf} CRLF, {lone} lone LF)  sha256 {_sha(raw)[:12]}...")


def check() -> int:
    _identity()
    print()
    _m, _c, _g, problems, already = _preflight()
    if already:
        print(f"  note: {len(already)} .gitignore entr(ies) already present, "
              f"they will not be duplicated: {already}")
    if problems:
        print("NOT APPLICABLE:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"APPLICABLE: {len(MANIFEST_EDITS)} manifest anchors, the changelog "
          f"anchor, and an append to .gitignore.")
    return 0


def apply() -> int:
    _identity()
    m, c, g, problems, already = _preflight()
    if problems:
        raise SystemExit("REFUSING: " + "; ".join(problems) + ". Nothing written.")
    for p in (MANIFEST, CHANGELOG, GITIGNORE):
        if _sidecar(p).exists():
            raise SystemExit(f"REFUSING: {_sidecar(p).name} exists. Use --revert.")

    m_raw, c_raw = MANIFEST.read_bytes(), CHANGELOG.read_bytes()
    m_eol = _eol(m_raw, MANIFEST.name)
    c_eol = _eol(c_raw, CHANGELOG.name)

    m_out = m
    for old, new in MANIFEST_EDITS:
        m_out = m_out.replace(old, new, 1)
    c_out = c.replace(CHANGELOG_ANCHOR, CHANGELOG_ENTRY + CHANGELOG_ANCHOR, 1)

    # The manifest must still parse, and must say what we think it says.
    parsed = json.loads(m_out)
    assert parsed["factory_version"] == "1.26.0"
    assert parsed["tools"]["lot"]["version"] == "0.42.0"
    assert parsed["tools"]["level_factory"]["version"] == "0.40.0"

    m_data = (m_out.replace("\n", m_eol).encode("utf-8") if m_eol != "\n"
              else m_out.encode("utf-8"))
    c_data = (c_out.replace("\n", c_eol).encode("utf-8") if c_eol != "\n"
              else c_out.encode("utf-8"))

    ae = _append_eol(g)
    keep = [ln for ln in GITIGNORE_BLOCK.split("\n")
            if not (ln and not ln.startswith("#") and ln in already)]
    block = ae.join(ln.encode("utf-8") for ln in keep)
    lead = b"" if g.endswith(b"\n") else ae
    g_data = g + lead + block

    for p in (MANIFEST, CHANGELOG, GITIGNORE):
        shutil.copy2(p, _sidecar(p))
    MANIFEST.write_bytes(m_data)
    CHANGELOG.write_bytes(c_data)
    GITIGNORE.write_bytes(g_data)

    print()
    print(f"  factory.manifest.json : {len(m_raw)} -> {len(m_data)} B   "
          f"factory_version 1.25.0 -> 1.26.0")
    print(f"  CHANGELOG.md          : {len(c_raw)} -> {len(c_data)} B")
    print(f"  .gitignore            : {len(g)} -> {len(g_data)} B   "
          f"appended with {ae!r}, existing lines untouched")
    print()
    print("  NEXT:")
    print("    git add -A")
    print("    git commit -m \"factory-v1.26.0: certify lot 0.42.0 and the "
          "level_factory 0.40.0 that was never in the set\"")
    print("    git tag factory-v1.26.0")
    return 0


def revert() -> int:
    done = False
    for p in (MANIFEST, CHANGELOG, GITIGNORE):
        s = _sidecar(p)
        if not s.exists():
            print(f"  {p.name}: no sidecar, left alone")
            continue
        shutil.copy2(s, p)
        s.unlink()
        print(f"  {p.name}: restored to {len(p.read_bytes())} B")
        done = True
    if not done:
        raise SystemExit("REFUSING: nothing to revert.")
    return 0


def selftest() -> int:
    fails = []

    def ok(cond, label):
        print(f"  [{'ok' if cond else 'FAIL'}]  {label}")
        if not cond:
            fails.append(label)

    m, c, g, problems, already = _preflight()
    ok(not problems, "preflight clean")
    for p in problems:
        print(f"        {p}")
    if problems:
        print("\nSELFTEST FAILED")
        return 1

    # -- the mixed-ending rule, which is the interesting part --------------
    crlf, lone = g.count(b"\r\n"), g.count(b"\n") - g.count(b"\r\n")
    ok(crlf and lone, f".gitignore really is MIXED ({crlf} CRLF, {lone} LF) -- "
                      f"the reason _append_eol exists")
    strict_refused = False
    try:
        _eol(g, ".gitignore")
    except SystemExit:
        strict_refused = True
    ok(strict_refused, "the STRICT rule refuses .gitignore, as designed")
    ok(_append_eol(b"a\r\nb\r\n") == b"\r\n", "_append_eol: CRLF tail -> CRLF")
    ok(_append_eol(b"a\nb\n") == b"\n", "_append_eol: LF tail -> LF")
    ok(_append_eol(b"a\r\nb\n") == b"\n",
       "_append_eol: mixed file ending in LF -> LF (the tail decides, not the count)")
    ok(_append_eol(b"a\nb\r\n") == b"\r\n",
       "_append_eol: mixed file ending in CRLF -> CRLF")

    # -- manifest ----------------------------------------------------------
    m_out = m
    for old, new in MANIFEST_EDITS:
        m_out = m_out.replace(old, new, 1)
    try:
        parsed = json.loads(m_out)
        ok(True, "the patched manifest is valid JSON")
        ok(parsed["factory_version"] == "1.26.0",
           f"factory_version -> {parsed['factory_version']}")
        ok(parsed["tools"]["lot"]["version"] == "0.42.0"
           and parsed["tools"]["lot"]["tag"] == "v0.42.0",
           "lot -> 0.42.0 / v0.42.0")
        ok(parsed["tools"]["level_factory"]["version"] == "0.40.0"
           and parsed["tools"]["level_factory"]["tag"] == "v0.40.0",
           "level_factory -> 0.40.0 / v0.40.0")
        before = json.loads(m)
        moved = [k for k in before["tools"]
                 if before["tools"][k]["version"] != parsed["tools"][k]["version"]]
        ok(sorted(moved) == ["level_factory", "lot"],
           f"exactly two tools move: {sorted(moved)}")
        ok(len(parsed["tools"]) == len(before["tools"]) == 10,
           "no tool is added or lost")
        ok(parsed["tools"]["lot"]["note"].endswith("the rest of the map's."),
           "lot's note is extended, not replaced")
        ok("UNCERTIFIED until factory-v1.26.0"
           in parsed["tools"]["level_factory"]["note"],
           "level_factory's note records that 0.40.0 sat uncertified")
    except json.JSONDecodeError as exc:
        ok(False, f"the patched manifest is valid JSON ({exc})")

    # -- changelog ---------------------------------------------------------
    c_out = c.replace(CHANGELOG_ANCHOR, CHANGELOG_ENTRY + CHANGELOG_ANCHOR, 1)
    ok(c_out.count("## [factory-v1.26.0]") == 1, "one 1.26.0 heading")
    ok(c_out.count("## [factory-v1.25.0]") == 1, "1.25.0's entry survives")
    ok(c_out.index("factory-v1.26.0") < c_out.index("factory-v1.25.0"),
       "newest first")
    ok(c_out.startswith("# Factory Changelog"),
       "the title line is not displaced -- the entry goes below it")
    ok("WAS ALREADY SHIPPED AND WAS NOT IN THE SET" in CHANGELOG_ENTRY,
       "the uncertified-0.40.0 finding is recorded, not buried")

    # -- gitignore ---------------------------------------------------------
    ae = _append_eol(g)
    keep = [ln for ln in GITIGNORE_BLOCK.split("\n")
            if not (ln and not ln.startswith("#") and ln in already)]
    block = ae.join(ln.encode("utf-8") for ln in keep)
    g_out = g + (b"" if g.endswith(b"\n") else ae) + block
    ok(g_out.startswith(g), "the append leaves every existing byte untouched")
    txt = g_out.decode("utf-8").replace("\r\n", "\n").split("\n")
    for name in ("compose_diag.txt", "lux_gap.txt", "unlit_ab2.txt",
                 "compose_findings.json"):
        ok(txt.count(name) == 1, f"{name} listed exactly once")
    # Compared as ENTRIES, not as substrings: the comment block appended above
    # mentions `_scratch/` in prose, so a bare `count(b"_scratch/")` grows by
    # one and fails for a reason that is not a duplicate entry. That is the
    # sixth time in this arc a bare-name count has been wrong about text its
    # own documentation contains.
    def entries(blob):
        out = {}
        for ln in blob.decode("utf-8").replace("\r\n", "\n").split("\n"):
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                out[ln] = out.get(ln, 0) + 1
        return out
    before_e, after_e = entries(g), entries(g_out)
    grew = {k: (before_e[k], after_e[k]) for k in before_e
            if after_e.get(k, 0) != before_e[k]}
    ok(not grew, f"no entry that already existed changes count ({grew})")
    added = {k: v for k, v in after_e.items() if k not in before_e}
    ok(len(added) == 9 and all(v == 1 for v in added.values()),
       f"exactly 9 new entries, each once ({sorted(added)})")
    # `.gitignore` already carries duplicates of its own (_scratch/ x3,
    # shots_*/ x2). Reported, not silently inherited as a standard.
    dupes = {k: v for k, v in before_e.items() if v > 1}
    if dupes:
        print(f"        (note) .gitignore already had duplicate entries before "
              f"this patch: {dupes} -- left alone, not this change's to fix)")

    print()
    if fails:
        print(f"SELFTEST FAILED: {len(fails)} check(s)")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("SELFTEST PASSED")
    return 0


def main(argv) -> int:
    arg = argv[1] if len(argv) > 1 else ""
    if arg == "--check":
        return check()
    if arg == "--selftest":
        return selftest()
    if arg == "--revert":
        return revert()
    if arg == "":
        return apply()
    raise SystemExit(f"unknown argument {arg!r}; "
                     f"use --check, --selftest, --revert, or no argument")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
