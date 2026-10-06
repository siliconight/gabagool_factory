"""Level Factory 0.144.1: the export's blocker query reads the candidate a
finding names in its own `candidate_id`, not only in its location.

Cold run 9170 (card_block_001, the breadth sweep) could not export. Its shell
and art legs printed "blockers open: 0"; the export refused over
`LT_NOT_EVALUATED` on seed_9061 -- a candidate nobody chose, the driver having
picked seed_9263. The finding, verbatim from the run's validation file:

    {"blocking": true, "candidate_id": "card_block_001.candidate.seed_9061",
     "code": "LT_NOT_EVALUATED", "location": "", ...}

`_open_blockers` reads the candidate from `location` (falling back to the
stage id), finds none, and fails safe. `cmd_run`'s `aggregate` reads
`candidate_id` and discounted it. Two queries of one question again -- cold
run 9074's defect, through a different field.

    python patch_lf_blocker_candidate_id.py
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
LF = ROOT / "level_factory"

EDITS = {
    LF / "apps/cli/commands/__init__.py": [(
        '''        # The export ships the SELECTED candidate. A blocker on one that was
        # not chosen is not this package's problem -- see the docstring. Both
        # tokens must be known, and they must differ, or this blocks.
        here_token = _candidate_of(where)
''',
        '''        # The export ships the SELECTED candidate. A blocker on one that was
        # not chosen is not this package's problem -- see the docstring. Both
        # tokens must be known, and they must differ, or this blocks.
        #
        # The finding's own `candidate_id` first, then its location (0.144.1).
        # Laser Tag's LT_NOT_EVALUATED names its candidate in `candidate_id`
        # and leaves `location` empty, so reading the location alone found no
        # candidate, failed safe, and refused cold run 9170's export over a
        # candidate nobody chose -- while `cmd_run`, whose `aggregate` reads
        # `candidate_id`, printed "blockers open: 0".
        here_token = _candidate_of(i.get("candidate_id") or "") or _candidate_of(where)
''')],
    LF / "tests/unit/test_export_blockers_candidate_aware.py": [(
        '''def test_a_blocker_naming_no_candidate_still_counts(tmp_path):
    """A stage-level blocker belongs to the mission, not to a candidate, so
    there is nothing to discount it against."""
    ws = _ws(tmp_path,
             [_blocker(loc="club_block_013.lux_apply", stage="lux_apply")],
             selected="club_block_013.candidate.seed_9276")
    assert len(_open_blockers(ws, MISSION)) == 1
''',
        '''def test_a_blocker_naming_no_candidate_still_counts(tmp_path):
    """A stage-level blocker belongs to the mission, not to a candidate, so
    there is nothing to discount it against."""
    ws = _ws(tmp_path,
             [_blocker(loc="club_block_013.lux_apply", stage="lux_apply")],
             selected="club_block_013.candidate.seed_9276")
    assert len(_open_blockers(ws, MISSION)) == 1


# ---------------------------------------------------------------------------
# the candidate a finding names in its own field (0.144.1)
# ---------------------------------------------------------------------------
def _unevaluated(candidate):
    """The shape of cold run 9170's blocker: Laser Tag's LT_NOT_EVALUATED
    names its candidate in `candidate_id` and leaves the location empty."""
    return {"code": "LT_NOT_EVALUATED", "blocking": True, "location": "",
            "stage_id": "laser_tag_evaluate", "candidate_id": candidate,
            "message": "Laser Tag never evaluated this map (0 runs completed)"}


def test_a_blocker_naming_its_candidate_only_in_candidate_id_is_discounted_too(tmp_path):
    """FAILS BEFORE 0.144.1: cold run 9170 exactly. seed_9061 carried the
    only blocker, in `candidate_id` with an empty location; seed_9263 was
    picked; `cmd_run` printed "blockers open: 0" and the export refused."""
    ws = _ws(tmp_path, [_unevaluated(f"{MISSION}.candidate.seed_9061")],
             selected=f"{MISSION}.candidate.seed_9263")
    assert _open_blockers(ws, MISSION) == []


def test_the_same_blocker_on_the_selected_candidate_still_refuses(tmp_path):
    ws = _ws(tmp_path, [_unevaluated(f"{MISSION}.candidate.seed_9263")],
             selected=f"{MISSION}.candidate.seed_9263")
    out = _open_blockers(ws, MISSION)
    assert len(out) == 1 and "LT_NOT_EVALUATED" in out[0], out
''')],
}


def main():
    staged = {}
    for path, pairs in EDITS.items():
        data = path.read_bytes()
        # Each file in its own endings: the anchors here are written LF, and
        # `test_export_blockers_candidate_aware.py` is CRLF. A file that mixes
        # the two refuses rather than being guessed at.
        crlf = data.count(b"\r\n")
        assert crlf in (0, data.count(b"\n")), f"{path}: mixed line endings"
        eol = "\r\n" if crlf else "\n"
        text = data.decode("utf-8")
        for old, new in pairs:
            old, new = old.replace("\n", eol), new.replace("\n", eol)
            n = text.count(old)
            assert n == 1, f"{path}: anchor matched {n} times: {old[:70]!r}"
            text = text.replace(old, new)
        staged[path] = text
    for path, text in staged.items():
        path.write_bytes(text.encode("utf-8"))
        print("patched", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
