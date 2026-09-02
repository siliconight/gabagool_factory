r"""The roadmap's status index, derived from the roadmap instead of typed.

    python roadmap_status.py                # print the generated index
    python roadmap_status.py --check        # compare to the file, exit 1 on drift
    python roadmap_status.py --write        # rewrite the block in place
    python roadmap_status.py --unclassified # only the items with no explicit status
    python roadmap_status.py --selftest     # prove the status reader on both dialects

Run from the factory root.

## Why this exists

`PIPELINE_ROADMAP.md` is 194 KB and carries 41 numbered items. Its closures are
prose -- "Closed 2026-07-27", "Retracted 2026-07-28" -- there is exactly one
literal `DONE` in the whole file, and nothing checks any of it. Asked "what is
open?", the honest answer on 2026-08-12 was that it took a script to find out,
and the script had to guess from sentences.

Same failure as `PIPELINE_MAP.md` drifting from the planner, and `factory_map.py`
is the same answer: derive the summary from the artefact, so a stale summary
becomes impossible rather than merely discouraged.

## The convention

A status is one line immediately above an item's heading:

    *STATUS: CLOSED 2026-08-12 -- 127 lights in the shipped presentation scene*

    **30. Nothing instantiates the light loader ...**

Vocabulary, and the distinctions are load-bearing:

    OPEN        still true, still worth doing
    CLOSED      fixed, with the evidence named in the same line
    RETRACTED   the item was wrong; the defect did not exist
    NARROWED    partly closed; what remains is stated in the item
    SUPERSEDED  overtaken by other work; the mechanism no longer exists
    ANALYSIS    not a task at all -- a finding, a constraint, or a decision

ANALYSIS matters more than it looks. Items 31 and 32 are reductions of engine
documentation about what Godot's GI techniques require. Nothing "closes" them,
and leaving them in a queue of defects makes the queue lie about its own size.

## Resolution order

    1. an explicit *STATUS:* line          -- authoritative
    2. a closure phrase in the item's own prose  -- inferred, and REPORTED as
       inferred, because a sentence is not a status field
    3. otherwise OPEN

`--unclassified` lists everything resting on step 2 or 3. That list is the work
of adopting this convention, and it shrinks by one line per item.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

def _factory_root() -> Path:
    """The directory holding `factory.manifest.json`, found by walking up.

    Was `Path(__file__).resolve().parent`, which required this file to sit AT
    the factory root and kept eleven scripts pinned there. Walking up means it
    works from `tools/`, `patches/` or anywhere else, and still returns the
    root when it IS the root -- the first candidate tested is its own
    directory.

    The manifest is the marker because it is the one file that defines this
    place and exists in no tool repo. `.git` would match every tool repo.
    """
    here = Path(__file__).resolve()
    for base in (here.parent, *here.parents):
        if (base / "factory.manifest.json").is_file():
            return base
    return here.parent


ROOT = _factory_root()
DOC = ROOT / "PIPELINE_ROADMAP.md"
BEGIN = "<!-- BEGIN GENERATED: roadmap_status.py -- do not edit by hand -->"
END = "<!-- END GENERATED -->"

_ITEM = re.compile(r"^\*\*(\d+)\. (.*)$")
_STATUS = re.compile(r"^\*STATUS:\s+([A-Z]+)\b\s*(.*?)\*\s*$")
_INFERRED = re.compile(
    r"\b(Closed|CLOSED|Retracted|RETRACTED|Shipped|SHIPPED|WITHDRAWN)\b"
    r"[^.\n]{0,80}", re.M)

VOCAB = ("OPEN", "CLOSED", "RETRACTED", "NARROWED", "SUPERSEDED", "ANALYSIS")


def _title(num: int, first: str, lines: list[str], i: int) -> str:
    """An item's title: everything up to the closing ** of its bolded heading."""
    buf = first
    j = i
    while "**" not in buf.split(f"**{num}. ", 1)[-1] and j + 1 < len(lines):
        j += 1
        buf += " " + lines[j].strip()
    head = buf.split(f"**{num}. ", 1)[-1]
    return head.split("**", 1)[0].strip().rstrip(".")


def _block_above(lines: list[str], i: int) -> str:
    """The nearest non-blank block above line `i`, joined into one string.

    This used to read `lines[k]` -- the single nearest non-blank line -- and
    `_STATUS` requires that ONE line to both open with `*STATUS:` and close
    with `*`. That holds only while a status is written unwrapped, and the
    early ones are: item 41's is a single 2,400-character line. Every status
    written from 2026-08-18 on is hard-wrapped, so its last line ends with `*`
    and does not begin with `*STATUS:`, the match failed, and the item fell
    through to prose inference in silence.

    MEASURED 2026-08-24 on the roadmap at 5,811 lines: NINE items -- 54 through
    62, every item added since the convention was adopted -- had an explicit
    status line that this file could not see. Item 54 carried
    `CLOSED 2026-08-24` with a census pass behind it and the derived table
    called it `OPEN *(inferred)*` with no evidence. `--check` reported that as
    ordinary drift, so the index looked merely stale rather than blind, which
    is why it went unnoticed for six days.

    A checker that cannot see the field it wants has learned nothing. Joining
    the block is the whole fix; `--selftest` pins BOTH dialects, and it fails
    on the version of this file that reads one line.
    """
    k = i - 1
    while k >= 0 and not lines[k].strip():
        k -= 1
    if k < 0:
        return ""
    j = k
    while j >= 0 and lines[j].strip():
        j -= 1
    block = [ln.strip() for ln in lines[j + 1:k + 1]]
    # The status STARTS at the line that says so, not at the top of the block.
    # A plain block join regressed item 42, whose status is one unwrapped line
    # with NO blank line between it and the paragraph above -- so the join
    # began "correct can still look wrong..." and matched nothing, turning a
    # NARROWED with 1,039 characters of evidence into `OPEN *(inferred)*` with
    # a dash. Caught by reading every changed row of `--check`'s own diff
    # rather than only the rows the change was aimed at.
    starts = [n for n, ln in enumerate(block) if ln.startswith("*STATUS:")]
    if not starts:
        return " ".join(block)
    return " ".join(block[starts[-1]:])


def parse(text: str) -> list[dict]:
    body_at = text.index("## What to do next")
    lines = text.splitlines()
    upto = text[:body_at].count("\n")
    # Where each item starts, so an inference window can be bounded by the NEXT
    # item rather than a fixed line count. Measured: a 12-line window from item
    # 10 reached into item 11 and read its "Retracted 2026-07-28" as item 10's,
    # which is this file's own recurring defect -- an enumeration of one thing
    # standing in for the description of another.
    starts = [i for i, ln in enumerate(lines)
              if i >= upto and _ITEM.match(ln)]
    out = []
    for i, ln in enumerate(lines):
        if i < upto:
            continue
        m = _ITEM.match(ln)
        if not m:
            continue
        num = int(m.group(1))
        nxt = next((s for s in starts if s > i), len(lines))
        # An explicit status sits in the nearest non-blank BLOCK above.
        status, note, explicit = "OPEN", "", False
        sm = _STATUS.match(_block_above(lines, i))
        if sm:
            status, note, explicit = sm.group(1), sm.group(2).strip(" -–—"), True
        if not explicit:
            chunk = "\n".join(lines[i:min(i + 12, nxt)])
            im = _INFERRED.search(chunk)
            if im:
                word = im.group(1).upper()
                status = "RETRACTED" if word.startswith("RETRACT") else (
                    "SUPERSEDED" if word == "WITHDRAWN" else "CLOSED")
                note = im.group(0).strip()
        out.append(dict(num=num, title=_title(num, ln, lines, i),
                        status=status, note=note, explicit=explicit))
    out.sort(key=lambda r: r["num"])
    return out


def render(items: list[dict]) -> str:
    rows = [BEGIN, "",
            "| # | status | item | evidence |",
            "|---|---|---|---|"]
    for it in items:
        mark = "" if it["explicit"] else " *(inferred)*"
        note = it["note"].replace("|", "\\|")[:90] or "—"
        rows.append(f"| {it['num']} | **{it['status']}**{mark} | "
                    f"{it['title'][:70]} | {note} |")
    tally = {}
    for it in items:
        tally[it["status"]] = tally.get(it["status"], 0) + 1
    parts = ", ".join(f"{tally[s]} {s.lower()}" for s in VOCAB if s in tally)
    inferred = sum(1 for it in items if not it["explicit"])
    rows += ["",
             f"**{len(items)} items: {parts}.** {inferred} rest on a sentence "
             f"rather than a status line -- run `roadmap_status.py "
             f"--unclassified` for the list.",
             "",
             "A status is the block directly above the item, wrapped or "
             "not: "
             "`*STATUS: CLOSED 2026-08-12 -- what proves it*`. Vocabulary: "
             + ", ".join(f"`{v}`" for v in VOCAB) + ".",
             "", END]
    return "\n".join(rows)


_SELFTEST_DOC = """## What to do next

*STATUS: CLOSED 2026-07-27 -- one unwrapped line, the dialect items 1-53 use*

**1. An item whose status fits on one line.**
Body.

*STATUS: NARROWED 2026-08-24 -- a hard-wrapped block, the dialect every
status written since 2026-08-18 uses, whose last line ends with the closing
asterisk and whose first line is the one that says STATUS*

**2. An item whose status is wrapped.**
Body.

**3. An item with no status at all, closed only in prose.**
Closed 2026-08-01 by something.

Not a status, just prose that happens to end in an asterisk *

**4. An item preceded by prose rather than a status.**
Body.

Prose with no blank line before the status that follows it.
*STATUS: SUPERSEDED 2026-08-14 -- item 42's shape: glued to the paragraph above*

**5. An item whose status is glued to the prose above it.**
Body.
"""


def selftest() -> int:
    """Both dialects, plus the two ways a status can be absent.

    Case 2 FAILS on the version of this file that matched `lines[k]`, which is
    the only property that makes this worth having. Case 5 fails on the FIRST
    attempt at the fix, which joined the whole block and so lost item 42.
    Case 4 guards the other direction -- a block above an item that is not a
    status must not become one just because the join made it longer.
    """
    got = {it["num"]: (it["status"], it["explicit"]) for it in parse(_SELFTEST_DOC)}
    want = {
        1: ("CLOSED", True),      # unwrapped, explicit
        2: ("NARROWED", True),    # wrapped, explicit  <- regressed before this
        3: ("CLOSED", False),     # inferred from prose
        4: ("OPEN", False),       # prose above is not a status
        5: ("SUPERSEDED", True),  # glued to prose  <- regressed by the first fix
    }
    bad = {n: (got.get(n), want[n]) for n in want if got.get(n) != want[n]}
    for n, (g, w) in sorted(bad.items()):
        print(f"  item {n}: got {g}, want {w}")
    if len(got) != len(want):
        print(f"  parsed {len(got)} items, expected {len(want)}")
        return 1
    if bad:
        print(f"  selftest FAILED: {len(bad)} of {len(want)} cases")
        return 1
    print(f"  selftest ok: {len(want)} cases, both status dialects read")
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    if not DOC.is_file():
        raise SystemExit(f"not found: {DOC}")
    text = DOC.read_text(encoding="utf-8", errors="replace")
    items = parse(text)
    if not items:
        raise SystemExit("no numbered items found -- has the heading changed?")

    bad = [it for it in items if it["explicit"] and it["status"] not in VOCAB]
    if bad:
        for it in bad:
            print(f"  item {it['num']}: unknown status {it['status']!r}")
        print(f"  vocabulary is {', '.join(VOCAB)}")
        return 1

    if "--unclassified" in argv:
        rest = [it for it in items if not it["explicit"]]
        print(f"{len(rest)} of {len(items)} items have no explicit status line:")
        for it in rest:
            print(f"  {it['num']:>2}  {it['status']:<10} {it['title'][:60]}")
            if it["note"]:
                print(f"      inferred from: {it['note'][:70]}")
        return 0

    block = render(items)
    if "--check" not in argv and "--write" not in argv:
        print(block)
        return 0

    if BEGIN not in text or END not in text:
        print(f"{DOC.name} has no generated block. Paste the section above "
              f"into it, markers included, then --write and --check maintain "
              f"it.")
        return 2
    current = text[text.index(BEGIN): text.index(END) + len(END)]

    if "--write" in argv:
        # `newline=""` or this rewrites every line ending in the document.
        # `read_text` above opens with universal newlines, so the file arrives
        # as `\n` whatever it was on disk; `write_text` with the default
        # `newline=None` translates those back out to `os.linesep`, which is
        # `\r\n` on Windows. Measured 2026-08-16: the roadmap went from
        # 0 CRLF / 4,525 LF to 4,525 CRLF in a single `--write`, 277,331 bytes
        # on disk against 272,802 in the repository -- and `git status` stayed
        # SILENT, because git compares through the `text=auto eol=lf` clean
        # filter and saw no change. The conventions require `--write` after
        # every roadmap edit, so this fired on all of them.
        #
        # This writes LF rather than restoring what the file had, because
        # `read_text` has already discarded that by the time we get here, and
        # LF is canonical repo-wide since `.gitattributes` (f2713e9).
        DOC.write_text(text.replace(current, block), encoding="utf-8",
                       newline="")
        print(f"  rewrote the generated block in {DOC.name}")
        return 0

    if current == block:
        print(f"  {DOC.name} index matches its items")
        return 0
    print(f"  {DOC.name} index HAS DRIFTED. Diff:")
    import difflib
    for line in difflib.unified_diff(
            current.splitlines(), block.splitlines(),
            fromfile="committed", tofile="derived", lineterm="", n=1):
        print("    " + line)
    print("  run --write to regenerate")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
