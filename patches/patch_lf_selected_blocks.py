r"""A blocker on the SELECTED candidate counts, whatever the scheduler did with it.

    python patch_lf_selected_blocks.py --check
    python patch_lf_selected_blocks.py
    python patch_lf_selected_blocks.py --selftest   (run it AFTER applying)
    python patch_lf_selected_blocks.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

Roadmap item 68, and it is the other half of `patch_lf_eliminated_not_blocking.py`.
That patch fixed a real defect: on 2026-08-12 a blocker belonging to a
candidate the scheduler had already discarded labelled the whole mission
"Blocked: unresolved blocking issues" while `blocked_job` was never set -- the
run that carried on reporting as the run that halted. Its remedy was to
partition, and its reasoning was sound: "N candidates exist so that some can
be bad."

IT OVERSHOT BY EXACTLY ONE CANDIDATE. The predicate it installed is

    if issue.candidate_id in eliminated_candidates:

and it never consults the selection. So the discount fires hardest on the one
candidate whose blockers are the only ones that can matter.

MEASURED 2026-08-27, cold run `cold_7001`, on real output:

    .level_factory/approvals/category5_baie_dore_001.selected
        category5_baie_dore_001.candidate.seed_7001

    validation/category5_baie_dore_001.json -- 2 issues, severity "blocker",
    blocking: true, both candidate_id ...candidate.seed_7001
        LUX_FIXTURE_COLOCATION  20 marker(s) with no lamp within 0.10 m
        LUX_FIXTURE_COLOCATION  20 lamp(s) more than 0.10 m from any marker

    console
        1 candidate(s) eliminated (the rest carried on): ...seed_7001
        2 blocker(s) belong to eliminated candidate(s) and do not block the mission
        Structural checks passed  (blockers open: 0, total findings: 119)

The earlier bug made a good run look broken. This one makes a broken run look
good, which is the worse direction, and it is the direction this file's whole
project exists to catch.

WHAT CHANGES. `aggregate` gains `selected_candidate`. A blocker belonging to
it is never moved to `blocking_eliminated`. And because an eliminated
SELECTION is itself a finding -- the mission has nothing to hand over --
`selected_eliminated` reports it instead of letting it pass quietly.

OPT-IN, THE SAME WAY AND FOR THE SAME REASON. The default is `None`, and with
it the partition behaves exactly as it did yesterday. `cmd_validate` passes no
eliminated set at all and is untouched. `cmd_run` is the caller that knows the
selection, and `_resolve_selected_candidate` was already sitting there.

WHAT IT DOES NOT DO. It does not re-block the case the earlier patch fixed: a
blocker on a discarded candidate nobody selected still does not block. It does
not touch `blocked_job`, `readiness_label`, or what the scheduler eliminates.
The only thing that changes is which side of the partition the selection's own
blockers land on.

ACCEPTANCE TEST, and it is cheap because everything is cached:

    python -m level_factory -C <cold-7001-ws> run category5_baie_dore_001 --art --gameplay

must print `blockers open: 2` and must NOT print `Structural checks passed`.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

MODEL = Path("level_factory/packages/validation/model.py")
COMMANDS = Path("level_factory/apps/cli/commands/__init__.py")
SIDECAR = ".pre_selblocks"


OLD_SIG = '''def aggregate(issues: list[ValidationIssue],
              accepted_issue_ids: frozenset[str] = frozenset(),
              eliminated_candidates: frozenset[str] = frozenset()) -> dict:'''

NEW_SIG = '''def aggregate(issues: list[ValidationIssue],
              accepted_issue_ids: frozenset[str] = frozenset(),
              eliminated_candidates: frozenset[str] = frozenset(),
              selected_candidate: str | None = None) -> dict:'''


OLD_DOC = '''    OPT-IN. The default is empty, and with it every blocking issue lands in
    `blocking_open` exactly as before -- a caller that does not know which
    candidates were eliminated gets today's behaviour unchanged, which is the
    safe direction for a gate.
    """'''

NEW_DOC = '''    `selected_candidate` is the exception to that, and it exists because the
    paragraph above overshot by exactly one candidate. Measured 2026-08-27 on
    cold run `cold_7001` (roadmap 68): the candidate a human had approved at
    `candidate_selected` picked up two `LUX_FIXTURE_COLOCATION` blockers, the
    scheduler eliminated it, the discount fired on the strength of that
    elimination alone, and the run printed "Structural checks passed (blockers
    open: 0, total findings: 119)". A blocker on the SELECTED candidate always
    counts. "N candidates exist so that some can be bad" is true of the ones
    nobody chose; the chosen one IS the mission.

    An eliminated SELECTION is itself a finding -- a mission with nothing to
    hand over -- so `selected_eliminated` reports it rather than letting it
    read as a clean run.

    OPT-IN. The default is empty, and with it every blocking issue lands in
    `blocking_open` exactly as before -- a caller that does not know which
    candidates were eliminated gets today's behaviour unchanged, which is the
    safe direction for a gate.
    """'''


OLD_LOOP = '''        elif issue.blocking:
            if issue.candidate_id in eliminated_candidates:
                blocking_eliminated.append(issue.issue_id)
            else:
                blocking_open.append(issue.issue_id)'''

NEW_LOOP = '''        elif issue.blocking:
            # The selection is never discounted. Roadmap 68: the predicate
            # used to be `in eliminated_candidates` alone, which discounted
            # the one candidate whose blockers are the only ones that matter.
            if (issue.candidate_id in eliminated_candidates
                    and issue.candidate_id != selected_candidate):
                blocking_eliminated.append(issue.issue_id)
            else:
                blocking_open.append(issue.issue_id)'''


OLD_RET = '''        "blocking_eliminated": sorted(blocking_eliminated),
        "accepted": sorted(accepted),'''

NEW_RET = '''        "blocking_eliminated": sorted(blocking_eliminated),
        # The selection itself was thrown away. That is not a pass, it is a
        # mission with nothing to hand over, and it gets said out loud rather
        # than inferred from a blocker count that no longer mentions it.
        "selected_eliminated": bool(
            selected_candidate is not None
            and selected_candidate in eliminated_candidates),
        "accepted": sorted(accepted),'''


OLD_CALL = '''    _dropped = frozenset(getattr(summary, "eliminated_candidates", {}) or {})
    agg = aggregate(summary.all_issues, eliminated_candidates=_dropped)'''

NEW_CALL = '''    _dropped = frozenset(getattr(summary, "eliminated_candidates", {}) or {})
    # AND THE SELECTION GOES IN WITH IT -- roadmap 68. Passing only the
    # eliminated set discounts blockers on the candidate a human approved:
    # `cold_7001` printed "Structural checks passed" over a selected candidate
    # carrying two. `_resolve_selected_candidate` reads the same `.selected`
    # marker the approval gate writes.
    _selected = _resolve_selected_candidate(ws, args.mission_id)
    agg = aggregate(summary.all_issues, eliminated_candidates=_dropped,
                    selected_candidate=_selected)'''


OLD_PRINT = '''        if agg["blocking_eliminated"]:
            print(f"  {len(agg['blocking_eliminated'])} blocker(s) belong to "
                  f"eliminated candidate(s) and do not block the mission")'''

NEW_PRINT = '''        if agg["blocking_eliminated"]:
            print(f"  {len(agg['blocking_eliminated'])} blocker(s) belong to "
                  f"eliminated candidate(s) and do not block the mission")
        if agg["selected_eliminated"]:
            # Loud on purpose. This is the run having no answer, and the
            # quiet version of it is what roadmap 68 was filed for.
            print(f"  THE SELECTED CANDIDATE WAS ELIMINATED: {_selected}")
            print(f"  its blockers still count, and this mission has no "
                  f"viable selection until another candidate is approved")'''


EDITS = {
    MODEL: ((OLD_SIG, NEW_SIG), (OLD_DOC, NEW_DOC), (OLD_LOOP, NEW_LOOP),
            (OLD_RET, NEW_RET)),
    COMMANDS: ((OLD_CALL, NEW_CALL), (OLD_PRINT, NEW_PRINT)),
}


# ------------------------------------------------------------- selftest ----

def selftest(root: Path) -> int:
    """Exercise the patched `aggregate` on the run that motivated it.

    Run AFTER applying. It imports the real module off disk, so it tests what
    is installed rather than what this script believes it installed.
    """
    sys.path.insert(0, str(root / "level_factory"))
    try:
        from packages.core.models import ValidationIssue
        from packages.validation.model import aggregate, readiness_label
    except ImportError as exc:
        print(f"cannot import the patched module: {exc}")
        return 1

    def iss(i, cand, blocking=True, sev="blocker"):
        return ValidationIssue(issue_id=i, source_tool="lux",
                               mission_id="m", severity=sev,
                               category="presentation", code="x", message="m",
                               candidate_id=cand, blocking=blocking)

    if "selected_eliminated" not in aggregate([]):
        print("the installed `aggregate` has no `selected_eliminated` key -- "
              "the patch is\nnot applied. Run it without --selftest first.")
        return 1

    bad = 0

    def check(label, got, want):
        nonlocal bad
        ok = got == want
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}: {got!r}"
              + ("" if ok else f"  (wanted {want!r})"))

    SEL, OTHER = "cand.seed_7001", "cand.seed_7102"

    print("cold_7001: the SELECTED candidate is eliminated with two blockers")
    issues = [iss("a", SEL), iss("b", SEL)]
    a0 = aggregate(issues, eliminated_candidates=frozenset({SEL}),
                   selected_candidate=SEL)
    check("blocking_open", a0["blocking_open"], ["a", "b"])
    check("blocking_eliminated", a0["blocking_eliminated"], [])
    check("has_blockers", a0["has_blockers"], True)
    check("selected_eliminated", a0["selected_eliminated"], True)
    check("label", readiness_label(a0, run_completed=True),
          "Blocked: unresolved blocking issues")

    print("the SAME issues without the selection -- 2026-08-12 still holds")
    a1 = aggregate(issues, eliminated_candidates=frozenset({SEL}))
    check("blocking_open", a1["blocking_open"], [])
    check("blocking_eliminated", a1["blocking_eliminated"], ["a", "b"])
    check("label", readiness_label(a1, run_completed=True),
          "Structural checks passed")

    print("a discarded candidate nobody selected is still discounted")
    mixed = [iss("a", SEL), iss("c", OTHER)]
    a2 = aggregate(mixed, eliminated_candidates=frozenset({OTHER}),
                   selected_candidate=SEL)
    check("blocking_open", a2["blocking_open"], ["a"])
    check("blocking_eliminated", a2["blocking_eliminated"], ["c"])
    check("selected_eliminated", a2["selected_eliminated"], False)

    print("a selected candidate that was NOT eliminated is unaffected")
    a3 = aggregate([iss("c", OTHER)], eliminated_candidates=frozenset({OTHER}),
                   selected_candidate=SEL)
    check("blocking_open", a3["blocking_open"], [])
    check("selected_eliminated", a3["selected_eliminated"], False)

    print("an accepted issue is still accepted, not re-partitioned")
    a4 = aggregate(issues, accepted_issue_ids=frozenset({"a", "b"}),
                   eliminated_candidates=frozenset({SEL}),
                   selected_candidate=SEL)
    check("accepted", a4["accepted"], ["a", "b"])
    check("blocking_open", a4["blocking_open"], [])

    print("a mission-scoped issue (candidate_id None) is never eliminated")
    a5 = aggregate([iss("z", None)], eliminated_candidates=frozenset({SEL}),
                   selected_candidate=SEL)
    check("blocking_open", a5["blocking_open"], ["z"])

    print("no selection passed -- byte-identical to the previous behaviour")
    a6 = aggregate(mixed, eliminated_candidates=frozenset({SEL, OTHER}))
    check("blocking_open", a6["blocking_open"], [])
    check("blocking_eliminated", a6["blocking_eliminated"], ["a", "c"])
    check("findings NOT dropped (total)", a6["total"], 2)

    print()
    print("  all checks passed" if not bad else f"  {bad} CHECK(S) FAILED")
    return 1 if bad else 0


_CRLF = "\r\n"


def _eol(body: str) -> str:
    return _CRLF if _CRLF in body else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace("\n", eol) if eol == _CRLF else text


def _find(body: str, anchor: str):
    for cand in (anchor, _as(anchor, _CRLF)):
        n = body.count(cand)
        if n:
            return cand, n
    return anchor, 0


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
            print(f"  anchor starts: {old.splitlines()[0].strip()[:70]!r}")
            return 1
        out = out.replace(anchor, _as(new, eol), 1)

    data = out.encode("utf-8")
    bare = out.count("\n") - out.count(_CRLF)
    if eol == _CRLF and bare:
        print(f"REFUSING: {path.name} -- the edit would leave {bare} bare LF "
              f"line(s) in a CRLF document.")
        return 1
    try:
        compile(out, str(path), "exec")
    except SyntaxError as exc:
        print(f"REFUSING: {path.name} -- the patched file does not parse: {exc}")
        return 1
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
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

    if "--selftest" in argv:
        return selftest(root)

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
