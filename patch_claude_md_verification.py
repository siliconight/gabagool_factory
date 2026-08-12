r"""Three verification rules, from ten wrong calls in one session.

The tenth was made by an earlier draft of THIS file: `_apply`'s inherited
line-ending test reads `_CRLF in anchor`, and this anchor is a single line with
no newline in it, so a CRLF document got 81 bare LF lines. `_eol` now reads the
file instead, and a mixed-ending result refuses. The incident is written into
the section as its second example under rule 2.

    python patch_claude_md_verification.py --check
    python patch_claude_md_verification.py
    python patch_claude_md_verification.py --revert

Run from the FACTORY ROOT (the directory holding `CLAUDE.md`).

`Grounding` already says read the repo before changing it, and every one of the
nine below happened WITH that rule followed -- the files had been read. What
was missing is narrower and it is what this section adds: reading a file once is
not knowing it, an artefact is not evidence until you can name what produced it,
and a checker written against a guessed schema is a decoration.

Added as its own hard rule rather than folded into `Grounding`, because the
failure is not "did not read" -- it is "read, and then acted on the memory."
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

DOC = Path("CLAUDE.md")
SIDECAR = ".pre_verification"


OLD = '''## Where fixes land'''

NEW = '''## Verification — what you remember is not what is there (hard rule)

`Grounding` above is about reading the repo before changing it. This is about
the next failure along, and it is the one that actually happens: the files WERE
read, and then a claim got made from the memory of them.

Nine wrong calls in the session of 2026-08-10/11 — ten, counting the one made
while writing this section, which is the second instance under rule 2. Every one
was caught, most within minutes, several by instruments built two hours earlier
— and being caught is the consolation prize, not the goal. They fall into three
shapes, and each shape has a rule.

### 1. Name what produced an artefact before concluding anything from it

Four of the nine. The tree is unusually hostile here: five different files are
called `site.tscn`, one mission has a greybox build and a themed build standing
different shells, and `export_closure.json` (the fixer's log) sits beside
`export_closure_scan.json` (the judge's verdict).

* `grep -c Light3D site.tscn` returned 0 → "the preview is unlit". The rig is in
  `walk.tscn`, the wrapper, exactly where `build_walk_preview`'s own comment
  says it puts it. The content scene is not supposed to carry lighting.
* Score 45 on all 25 CSV rows → "the score is a constant". It is a map-level
  aggregate stamped onto every run row.
* Enemy hooks read from `lot_assemble` and building footprints from
  `preview/<mission>_walk` → a confident unfairness verdict about a site that
  does not exist. The second is the THEMED build.
* `probe_sightlines` measured 340 m open lanes → "the site needs blockers".
  `site_cover.plan_cover` already owned that question and had reported
  `still_open: 0`, `unbreakable: 0`.

**The rule:** before an artefact becomes evidence, say which job wrote it and
whether that job is the one under discussion. In the same breath, not as a later
check. If two artefacts are being compared, prove they came from the same build
before comparing them — `probe_opening.guard_same_build` does this and exists
because of the third bullet.

### 2. Re-read the interface in the turn you call it

Not "I read that file earlier." Confidence in remembered context does not decay
the way the context's accuracy does, and a long session makes that gap wide.

The clearest instance: `_copy_tree`'s `skip` was used to exclude one root
`site.tscn`. It matches **basenames anywhere in the tree**, so it also excluded
all five `lot/<archetype>/site.tscn` and the export came back with every
building unresolved and the review frame at 98% void. The comment saying `skip`
matches names sits four lines above the call — and had been quoted, correctly,
in that same patch's own docstring an hour before.

The second instance happened while writing this section, which is the most
useful thing about it. The patch installing this text reuses the standard
`_apply` helper, whose line-ending logic asks `_CRLF in anchor` — correct in
every patch before it, because every anchor before it spanned several lines.
This anchor is `## Where fixes land`: one line, containing no newline at all.
The test answered LF for a CRLF document and the first run wrote 81 bare LF
lines into this file. It was caught by counting endings in the output, not by
re-reading the helper — which is the failure, not the save. `_eol` now derives
the ending from the file, and a mixed result refuses.

**The rule:** re-read the signature and the adjacent comments of anything being
called, in the turn it is called — including helpers written yesterday, where
the assumption is not in the signature but in the shape of the data it was
written against. Cost is seconds. The alternative cost a re-export, a re-walk
and a retraction.

### 3. Never write a checker against a guessed schema

A `--verify` was written to read `export_closure_scan.json` and looked for
`unresolved` / `missing`. The file writes `ok`, `issues`,
`missing_resource_count`. Neither key matched, `or []` turned the absence into
an empty problem list, and it printed **"closure verdict clean"** three lines
below the exporter shouting `EXPORT_CLOSURE_BROKEN: 21 unresolved`.

This is the same defect the same session had already written a warning about,
in `patch_lf_score_split.py`: *"a number that silently describes four fifths of
a table is worse than no number: it looks actionable and is not."*

**The rule:** read one real instance of an artefact before writing the code that
reads it, and make an unrecognised shape FAIL rather than pass. A checker that
cannot find the field it wants has learned nothing and must say so.

### The tell

All three compress under the same pressure: producing over verifying. The tell
is a turn that ends with something shipped and nothing re-read. When a session
is going fast and every reply delivers a patch, that is the moment the checks
are being skipped — not the moment they are least needed.

One instance was a different animal and is worth separating: `ENEMY_SIGHT_RANGE`
was a change whose reasoning was sound and whose measured outcome was not — it
bought crew survival by stranding enemies on unnavigable ground, 34 stuck events
to 75. That is not a verification failure. That is what measurement is for, and
the patch was reverted with its numbers written into the constant it moved.

## Where fixes land'''


EDITS = {DOC: ((OLD, NEW),)}

_CRLF = "\r\n"


def _eol(body: str) -> str:
    """The file's dominant line ending.

    Keyed off the FILE, never off the anchor: `## Where fixes land` is a
    single line and contains no newline at all, so an anchor-derived test
    reports LF for a CRLF document and inserts mixed endings.
    """
    crlf = body.count(_CRLF)
    lf = body.count("\n") - crlf
    return _CRLF if crlf > lf else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _find(body: str, anchor: str):
    candidate = _as(anchor, _eol(body))
    return candidate, body.count(candidate)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(path: Path, edits, *, check: bool) -> int:
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR)
    eol = _eol(body)

    done = sum(1 for _o, new in edits if _find(body, new)[1] == 1)
    if done == len(edits):
        print(f"  already applied  {path.name}")
        return 0
    if done:
        print(f"REFUSING: {path.name} has {done} of {len(edits)} edits already "
              f"present.")
        return 1

    out = body
    for old, new in edits:
        anchor, count = _find(out, old)
        if count != 1:
            print(f"REFUSING: {path.name} -- expected 1 occurrence of an "
                  f"anchor, found {count}.")
            print(f"  anchor starts: {old.splitlines()[0].strip()!r}")
            return 1
        out = out.replace(anchor, _as(new, eol), 1)

    data = out.encode("utf-8")
    bare = out.count("\n") - out.count(_CRLF)
    if eol == _CRLF and bare:
        print(f"REFUSING: {path.name} -- the edit would leave {bare} bare LF "
              f"line(s) in a CRLF document.")
        return 1
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})  eol "
              f"{'CRLF' if eol == _CRLF else 'LF'}")
        return 0
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root")

    if "--revert" in argv:
        bad = 0
        for rel in EDITS:
            path = root / rel
            side = path.with_suffix(path.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {path.name}")
                bad = 1
                continue
            path.write_bytes(side.read_bytes())
            print(f"  reverted     {path.name}")
        return bad

    check = "--check" in argv
    for rel, edits in EDITS.items():
        code = _apply(root / rel, edits, check=check)
        if code:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
