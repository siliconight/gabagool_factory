r"""A blocker on an eliminated candidate is not a blocked mission.

    python patch_lf_eliminated_not_blocking.py --check
    python patch_lf_eliminated_not_blocking.py
    python patch_lf_eliminated_not_blocking.py --selftest   (run it AFTER applying)
    python patch_lf_eliminated_not_blocking.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

Roadmap addendum item I, and HALF OF IT ALREADY SHIPPED. The scheduler learned
to scope a failure:

    cand = jobs_by_id[jid].candidate_id
    if cand:
        summary.eliminated_candidates.setdefault(cand, jid)
    else:
        summary.blocked_job = summary.blocked_job or jid
        stop = True

A candidate-scoped failure eliminates that candidate and the run carries on;
only a mission-level failure stops it. `cmd_batch_run` even prints the
eliminations, with a comment saying why they are not a failure line.

THE REPORTING HALF NEVER FOLLOWED. `aggregate` counts every blocking issue the
same way regardless of whose candidate it belongs to, so one eliminated
candidate's blocker still labels the whole mission:

    Blocked: unresolved blocking issues  (blockers open: 1, total findings: 56)

Measured 2026-08-12 on lot_demo_001. The run had NOT stopped -- `blocked_job`
was never set, all three candidates built, two graded fine -- and the summary
line said blocked anyway. `cmd_run` also never prints the eliminations at all;
only the batch path does. So the run that carried on reported as the run that
halted, and the reason it carried on was invisible.

WHAT CHANGES. `aggregate` takes the eliminated set and partitions:

    blocking_open        blockers that still count against the mission
    blocking_eliminated  blockers belonging to eliminated candidates
    has_blockers         follows `blocking_open`, as it always did

OPT-IN, SO NOTHING MOVES UNDER A CALLER THAT DOES NOT KNOW. The default is an
empty set, and with an empty set every issue lands in `blocking_open` exactly
as today -- byte-identical behaviour for `cmd_validate` and both test suites.
A caller that knows which candidates were eliminated says so and gets the
partition. `cmd_run` is the caller that knows.

WHAT IT DOES NOT DO. It does not touch what BLOCKS. A mission-level failure
still sets `blocked_job` and still reads "the run did not complete", and a
blocker on a surviving candidate still blocks. The only thing that stops
counting is a blocker on a candidate the scheduler already threw away.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

MODEL = Path("level_factory/packages/validation/model.py")
COMMANDS = Path("level_factory/apps/cli/commands/__init__.py")
SIDECAR = ".pre_elimnotblock"


OLD_SIG = '''def aggregate(issues: list[ValidationIssue], accepted_issue_ids: frozenset[str] = frozenset()) -> dict:
    """Aggregate findings for reporting and gating (TDD 22.4, 22.5)."""'''

NEW_SIG = '''def aggregate(issues: list[ValidationIssue],
              accepted_issue_ids: frozenset[str] = frozenset(),
              eliminated_candidates: frozenset[str] = frozenset()) -> dict:
    """Aggregate findings for reporting and gating (TDD 22.4, 22.5).

    `eliminated_candidates` are candidates the scheduler already discarded --
    `SchedulerSummary.eliminated_candidates`. A blocker belonging to one of
    them is reported separately and does NOT count against the mission,
    because the mission is not blocked by a candidate it stopped building.
    N candidates exist so that some can be bad.

    Measured 2026-08-12 on lot_demo_001: one candidate's `dispatch_handoff`
    exited 1, the scheduler eliminated that candidate and carried on, all
    three candidates built, and the summary line still read "Blocked:
    unresolved blocking issues". `blocked_job` was never set. The run that
    continued reported as the run that halted.

    OPT-IN. The default is empty, and with it every blocking issue lands in
    `blocking_open` exactly as before -- a caller that does not know which
    candidates were eliminated gets today's behaviour unchanged, which is the
    safe direction for a gate.
    """'''


OLD_LOOP = '''        if issue.issue_id in accepted_issue_ids:
            accepted.append(issue.issue_id)
        elif issue.blocking:
            blocking_open.append(issue.issue_id)'''

NEW_LOOP = '''        if issue.issue_id in accepted_issue_ids:
            accepted.append(issue.issue_id)
        elif issue.blocking:
            if issue.candidate_id in eliminated_candidates:
                blocking_eliminated.append(issue.issue_id)
            else:
                blocking_open.append(issue.issue_id)'''


OLD_INIT = '''    blocking_open: list[str] = []
    accepted: list[str] = []'''

NEW_INIT = '''    blocking_open: list[str] = []
    blocking_eliminated: list[str] = []
    accepted: list[str] = []'''


OLD_RET = '''        "blocking_open": sorted(blocking_open),
        "accepted": sorted(accepted),
        "has_blockers": len(blocking_open) > 0,
        "total": len(issues),
    }'''

NEW_RET = '''        "blocking_open": sorted(blocking_open),
        # Kept apart, not dropped. A blocker on a discarded candidate is still
        # a real finding about a real defect -- it just is not the mission's
        # to answer for. Folding it into `blocking_open` blocks a run that
        # carried on; deleting it loses the only record of why the candidate
        # went.
        "blocking_eliminated": sorted(blocking_eliminated),
        "accepted": sorted(accepted),
        "has_blockers": len(blocking_open) > 0,
        "total": len(issues),
    }'''


OLD_CALL = '''    agg = aggregate(summary.all_issues)'''

NEW_CALL = '''    # THE ELIMINATED SET GOES IN. The scheduler discards a candidate whose own
    # job failed and carries on with the rest -- and until this was passed, one
    # discarded candidate's blocker labelled the whole mission "Blocked:
    # unresolved blocking issues" while `blocked_job` was never set. Addendum
    # item I: "N candidates exist so that some can be bad."
    _dropped = frozenset(getattr(summary, "eliminated_candidates", {}) or {})
    agg = aggregate(summary.all_issues, eliminated_candidates=_dropped)
    if _dropped:
        # `cmd_batch_run` has printed this for a while and `cmd_run` never did,
        # so on a single-mission run the reason the mission survived was
        # invisible. Not a failure line.
        print(f"  {len(_dropped)} candidate(s) eliminated (the rest carried "
              f"on): {', '.join(sorted(_dropped))}")
        if agg["blocking_eliminated"]:
            print(f"  {len(agg['blocking_eliminated'])} blocker(s) belong to "
                  f"eliminated candidate(s) and do not block the mission")'''


EDITS = {MODEL: ((OLD_SIG, NEW_SIG), (OLD_INIT, NEW_INIT), (OLD_LOOP, NEW_LOOP),
                 (OLD_RET, NEW_RET)),
         COMMANDS: ((OLD_CALL, NEW_CALL),)}


# ------------------------------------------------------------- selftest ----

def selftest(root: Path) -> int:
    """Exercise the patched `aggregate` on the case that motivated it.

    Run AFTER applying. It imports the real module off disk, so it is testing
    what is installed, not what this script believes it installed.
    """
    sys.path.insert(0, str(root / "level_factory"))
    try:
        from packages.core.models import ValidationIssue
        from packages.validation.model import aggregate, readiness_label
    except ImportError as exc:
        print(f"cannot import the patched module: {exc}")
        return 1

    def iss(i, cand, blocking=True, sev="blocker"):
        return ValidationIssue(issue_id=i, source_tool="dispatch",
                               mission_id="m", severity=sev,
                               category="handoff", code="x", message="m",
                               candidate_id=cand, blocking=blocking)

    probe = aggregate([])
    if "blocking_eliminated" not in probe:
        print("the installed `aggregate` has no `blocking_eliminated` key -- "
              "the patch is\nnot applied. Run it without --selftest first.")
        return 1

    bad = 0

    def check(label, got, want):
        nonlocal bad
        ok = got == want
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}: {got!r}")

    issues = [iss("a", "cand_00"), iss("b", "cand_01"),
              iss("c", "cand_02", blocking=False, sev="minor")]

    print("no eliminations -- must be byte-identical to the old behaviour")
    a0 = aggregate(issues)
    check("blocking_open", a0["blocking_open"], ["a", "b"])
    check("has_blockers", a0["has_blockers"], True)
    check("blocking_eliminated", a0["blocking_eliminated"], [])

    print("one candidate eliminated, one survives -- still blocked")
    a1 = aggregate(issues, eliminated_candidates=frozenset({"cand_00"}))
    check("blocking_open", a1["blocking_open"], ["b"])
    check("blocking_eliminated", a1["blocking_eliminated"], ["a"])
    check("has_blockers", a1["has_blockers"], True)

    print("2026-08-12: every blocker belongs to a candidate already discarded")
    a2 = aggregate(issues, eliminated_candidates=frozenset({"cand_00",
                                                            "cand_01"}))
    check("blocking_open", a2["blocking_open"], [])
    check("has_blockers", a2["has_blockers"], False)
    check("findings NOT dropped (total)", a2["total"], 3)
    check("label", readiness_label(a2, run_completed=True),
          "Structural checks passed")

    print("a mission-level failure still stops the run, whatever the partition")
    check("label", readiness_label(a2, run_completed=False),
          "Blocked: the run did not complete")

    print("an accepted issue is still accepted, not re-partitioned")
    a3 = aggregate(issues, accepted_issue_ids=frozenset({"a"}),
                   eliminated_candidates=frozenset({"cand_00"}))
    check("accepted", a3["accepted"], ["a"])
    check("blocking_eliminated", a3["blocking_eliminated"], [])

    print("a mission-scoped issue (candidate_id None) is never eliminated")
    a4 = aggregate([iss("z", None)],
                   eliminated_candidates=frozenset({"cand_00"}))
    check("blocking_open", a4["blocking_open"], ["z"])

    print()
    print("  all checks passed" if not bad else f"  {bad} CHECK(S) FAILED")
    return 1 if bad else 0


_CRLF = "\r\n"


def _eol(body: str) -> str:
    """The file's dominant line ending -- keyed off the FILE, never an anchor."""
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
