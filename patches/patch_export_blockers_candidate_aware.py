"""The export's blocker query must know which candidate it is exporting.

COLD RUN 9074 COULD NOT PRODUCE A PACKAGE. Two queries of one question
disagreed, which is the shape CLAUDE.md names: one of them is wrong, and the
run stopped until somebody established which.

    cmd_run   aggregate(eliminated_candidates=..., selected_candidate=...)
              -> "1 blocker(s) belong to eliminated candidate(s) and do not
                  block the mission"  /  "blockers open: 0"
    cmd_export _open_blockers()
              -> "refused: club_block_013 has 1 open blocker(s) --
                  JOB_PREFLIGHT_REFUSED at ...candidate.seed_9074"

`seed_9074` carried the run's only blocker (`LT_ObjectivePoint` inside solid
geometry). `seed_9276` was selected instead. The mission view discounted the
blocker; the export refused on the same data. NO SELECTION COULD HAVE PASSED:
`_open_blockers` reads every blocking issue in the validation file and filters
only by `EXPORT_SELF_REPORTING_STAGES`, so any blocker on any candidate refused
the export regardless of which one a human approved.

`aggregate`'s docstring already states the rule this borrows -- "N candidates
exist so that some can be bad... the chosen one IS the mission" -- and also
warns that it is OPT-IN, and that a caller which does not opt in "gets today's
behaviour unchanged, which is the safe direction for a gate". `_open_blockers`
was exactly such a caller. This opts it in.

IT FAILS SAFE, and that matters because of what this gate is for. Its own
comment records cold run 9015: the Lux stage exited 2, the scheduler filed a
blocking finding, and the export shipped a lightless package that was walked
black and counted a zero. So a blocker is skipped ONLY when both the selection
and the blocker's own candidate are known AND they differ. No selection
recorded, no candidate in the location, or an unparseable pair -- it still
blocks, exactly as before.

Anchored: every anchor must match exactly once or this refuses to write.
"""
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "level_factory" / \
    "apps" / "cli" / "commands" / "__init__.py"

# ---------------------------------------------------------------- anchor 1
A1 = '''def _open_blockers(ws: Workspace, mission_id: str) -> list[str]:
    """The mission's blocking findings, one line each, from the validation
    file the scheduler writes -- the same file `validate` reads -- minus
    those from stages whose absence the package reports itself
    (`EXPORT_SELF_REPORTING_STAGES`). A mission with no validation recorded
    has no blockers to report (it also has nothing to export, which
    `cmd_export` says next)."""
'''

N1 = '''def _candidate_of(location: str) -> str | None:
    """The candidate a finding's location names, or None.

    Locations come in two shapes -- `<mission>.candidate.<token>` and
    `<mission>.<stage>.candidate.<token>` -- and the selection marker written
    by the approval gate is the first. Both end in `.candidate.<token>`, so
    the token after that separator is the one thing they can be compared by.
    """
    marker = ".candidate."
    i = str(location).find(marker)
    if i < 0:
        return None
    token = str(location)[i + len(marker):].strip()
    return token or None


def _open_blockers(ws: Workspace, mission_id: str) -> list[str]:
    """The mission's blocking findings, one line each, from the validation
    file the scheduler writes -- the same file `validate` reads -- minus
    those from stages whose absence the package reports itself
    (`EXPORT_SELF_REPORTING_STAGES`), and minus those belonging to a
    candidate that is not the one being exported. A mission with no
    validation recorded has no blockers to report (it also has nothing to
    export, which `cmd_export` says next).

    THE CANDIDATE FILTER, and why it was missing. Cold run 9074 could not
    produce a package: `cmd_run` printed "1 blocker(s) belong to eliminated
    candidate(s) and do not block the mission" and "blockers open: 0", while
    this function refused the export over that same blocker. Two queries of
    one question -- `cmd_run` calls `aggregate` with `eliminated_candidates`
    and `selected_candidate`; this one filtered by stage alone. So a blocker
    on ANY candidate refused the export whichever one a human approved, and
    no selection could have passed.

    `aggregate`'s docstring states the rule borrowed here: "N candidates
    exist so that some can be bad... the chosen one IS the mission". It also
    warns the discount is opt-in and that not opting in is "the safe
    direction for a gate" -- true, and this was over-safe to the point of
    being wrong.

    IT STILL FAILS SAFE. A blocker is skipped only when the selection AND the
    blocker's own candidate are both known and they differ. No selection
    recorded, no candidate in the location, or either unparseable, and it
    blocks exactly as before -- which is what cold run 9015 bought, when a
    blocker this export did not read shipped a lightless package that walked
    black and counted a zero.
    """
'''

# ---------------------------------------------------------------- anchor 2
A2 = '''    out = []
    for i in data.get("issues", []) or []:
        if not i.get("blocking"):
            continue
        where = i.get("location") or i.get("stage_id") or ""
        stage = str(i.get("stage_id") or "")
        if not stage and "." in str(where):
            stage = str(where).rsplit(".", 1)[-1]
        if stage in EXPORT_SELF_REPORTING_STAGES:
            continue
'''

N2 = '''    out = []
    selected = _resolve_selected_candidate(ws, mission_id)
    selected_token = _candidate_of(selected) if selected else None
    for i in data.get("issues", []) or []:
        if not i.get("blocking"):
            continue
        where = i.get("location") or i.get("stage_id") or ""
        stage = str(i.get("stage_id") or "")
        if not stage and "." in str(where):
            stage = str(where).rsplit(".", 1)[-1]
        if stage in EXPORT_SELF_REPORTING_STAGES:
            continue
        # The export ships the SELECTED candidate. A blocker on one that was
        # not chosen is not this package's problem -- see the docstring. Both
        # tokens must be known, and they must differ, or this blocks.
        here_token = _candidate_of(where)
        if selected_token and here_token and here_token != selected_token:
            continue
'''

EDITS = ((A1, N1), (A2, N2))


def main() -> None:
    data = TARGET.read_bytes()
    if b"\r\n" in data:
        raise SystemExit("REFUSED: expected LF, found CRLF")
    text = data.decode("utf-8")
    before = len(data)
    for i, (old, new) in enumerate(EDITS, 1):
        hits = text.count(old)
        if hits != 1:
            raise SystemExit(f"REFUSED: anchor {i} matched {hits} times")
        text = text.replace(old, new)
    out = text.encode("utf-8")
    if b"\r\n" in out:
        raise SystemExit("REFUSED: would write CRLF")
    TARGET.write_bytes(out)
    print(f"{TARGET.name}: {before} -> {len(out)} bytes (+{len(out) - before})")


if __name__ == "__main__":
    main()
