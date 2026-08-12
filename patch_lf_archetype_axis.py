"""Give jobs a per-building axis, so the art stages can fan out.

Run from the factory root:

    python patch_lf_archetype_axis.py --check    # report only, write nothing
    python patch_lf_archetype_axis.py            # apply

Structural only. Nothing plans a per-archetype job yet, so no behaviour
changes and no artifact changes; this is the axis those jobs will need to
exist on. Step 1 of `level_factory/docs/PER_BUILDING_ART.md`.

WHY AN AXIS AND NOT A NAMING CONVENTION. The spec builder in
`apps/cli/commands/__init__.py` dispatches on `stage_id ==`, so five
`zoo_dressing_build` jobs all land in one branch. Without a field, that branch
can only tell them apart by taking the job id back apart -- and id parsing is
already the fragile seam here: `candidate_id.rsplit("_", 1)[-1]` appears in
eleven places. A job that knows which building it is for does not need to be
decoded.

WHY THE TAIL CANNOT BE CONFUSED WITH A CANDIDATE. `candidate_id` is always
literally `<mission>.candidate.seed_<int>`, and `job_id` keeps only the
`candidate.seed_<int>` suffix. An archetype tail is a single segment that is
never the word `candidate`, and the guard below refuses one that is.

WHY THE GUARD REFUSES RATHER THAN SANITISES. Job ids are used verbatim as
directory names -- `scheduler.py:303` builds `jobs_dir / job_id / "out"` -- so
a separator or a drive letter in an archetype id would silently write outside
its own job directory. Archetype ids come from `building_library.index`, which
derives them from filenames, so they are already safe; the check exists for the
day something else supplies one.

BACKWARD COMPATIBILITY, checked rather than assumed. `Index.get_job` does
`Job(**json.loads(payload))`, so every job record already in `index.sqlite` was
written without this field. It has a default, so old payloads still construct.
`Job.as_dict` is `dataclasses.asdict`, so new payloads carry it automatically
without touching the index schema (the `jobs` table stores the payload as one
JSON blob plus a few promoted columns, and this is not one of them).
"""
from __future__ import annotations

import sys
from pathlib import Path

IDS = Path("level_factory/packages/core/ids.py")
MODELS = Path("level_factory/packages/core/models.py")

EDITS: list[tuple[Path, str, str, str]] = [
    (IDS, "ids: archetype axis", r'''def job_id(mission_id: str, stage: str, *, candidate: str | None = None) -> str:
    if candidate:
        # candidate ids already carry the mission prefix; keep the suffix only.
        suffix = candidate.split(".", 1)[-1]
        return f"{mission_id}.{stage}.{suffix}"
    return f"{mission_id}.{stage}"
''', r'''#: Segment that opens every candidate tail (`candidate.seed_1997`). An
#: archetype segment must never be this, or a job id stops being decodable by
#: eye -- which is the only way anyone reads these.
_CANDIDATE_SEGMENT = "candidate"

#: Characters that must never reach a job id, because job ids become job
#: DIRECTORIES (`scheduler.py` builds `jobs_dir / job_id / "out"`). A separator
#: or a drive colon would put a job's outputs somewhere nobody goes looking.
_UNSAFE_IN_A_PATH = set('/\\:*?"<>|') | set(" \t\r\n")


def job_id(mission_id: str, stage: str, *, candidate: str | None = None,
           archetype: str | None = None) -> str:
    """The id of one job: a mission, a stage, and optionally WHICH one.

    Two discriminators, and they answer different questions. `candidate` is
    which variant of the whole mission this is. `archetype` is which BUILDING
    within one mission this job is for -- the art stages that bake a placement
    against a specific shell need one job per building, and until this existed
    they could only be planned once per mission.

    Ids are used verbatim as directory names (the scheduler builds
    `jobs_dir / job_id / "out"`), so an archetype carrying a path separator
    would write outside its own job. That is refused here rather than
    sanitised: a silently rewritten id is a job whose outputs are somewhere
    nobody looks.
    """
    parts = [mission_id, stage]
    if candidate:
        # candidate ids already carry the mission prefix; keep the suffix only.
        parts.append(candidate.split(".", 1)[-1])
    if archetype:
        aid = str(archetype)
        if not aid.strip():
            raise ValueError("archetype id is empty")
        if aid == _CANDIDATE_SEGMENT:
            raise ValueError(
                f"archetype id {aid!r} collides with the candidate tail")
        bad = sorted(set(aid) & _UNSAFE_IN_A_PATH)
        if bad or aid in (".", ".."):
            raise ValueError(
                f"archetype id {aid!r} is not usable as a directory name "
                f"(job ids become job directories): {bad or aid}")
        parts.append(aid)
    return ".".join(parts)
'''),
    (MODELS, "models: Job.archetype_id", '''\
    candidate_id: str | None = None
    status: str = states.PLANNED
    attempt: int = 0
''', '''\
    candidate_id: str | None = None
    #: WHICH BUILDING this job is for, when its stage runs once per building
    #: rather than once per mission.
    #:
    #: The art stages that bake a PLACEMENT -- patina dressing, zoo dressing,
    #: zoo fixtures -- position props against one specific shell's walls and
    #: roof. Planned once per mission, their single output was attached to
    #: every building in a varied lot: measured 2026-08-06, one dressing box of
    #: 30.4 x 8.4 x 22.4 inside five shells whose footprints ran from 26x20 to
    #: 46x32, standing up to 4.9 m above the roof it was supposed to sit under.
    #:
    #: `None` means the job is genuinely mission-wide. A module LIBRARY is --
    #: `zoo_kit_build` resolves per slot at compose time and is correctly one
    #: job. A placement is not. See docs/PER_BUILDING_ART.md.
    archetype_id: str | None = None
    status: str = states.PLANNED
    attempt: int = 0
'''),
]


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    for path in (IDS, MODELS):
        if not path.is_file():
            print(f"[patch] {path} not found -- run from the factory root")
            return 1

    files: dict[Path, tuple[bytes, bool, str]] = {}
    for path in (IDS, MODELS):
        raw = path.read_bytes()
        crlf = b"\r\n" in raw
        files[path] = (raw, crlf, raw.decode("utf-8").replace("\r\n", "\n"))
        print(f"[patch] {path}: {len(raw)} bytes, "
              f"endings={'CRLF' if crlf else 'LF'}")

    problems = []
    for path, name, before, after in EDITS:
        text = files[path][2]
        if after in text:
            print(f"[patch]   ALREADY APPLIED: {name}")
        elif before not in text:
            print(f"[patch]   ANCHOR NOT FOUND: {name}")
            problems.append(name)
        elif text.count(before) != 1:
            print(f"[patch]   ANCHOR NOT UNIQUE ({text.count(before)}x): {name}")
            problems.append(name)

    if problems:
        print(f"[patch] REFUSING to write: {len(problems)} anchor(s) did not "
              f"match cleanly. Re-read the source and re-author rather than "
              f"forcing a partial edit.")
        return 1

    for path, name, before, after in EDITS:
        raw, crlf, text = files[path]
        if after in text:
            continue
        files[path] = (raw, crlf, text.replace(before, after))
        print(f"[patch]   applied: {name}")

    if check_only:
        print("[patch] --check: no write")
        return 0

    for path, (raw, crlf, text) in files.items():
        payload = (text.replace("\n", "\r\n") if crlf else text).encode("utf-8")
        path.write_bytes(payload)
        print(f"[patch] wrote {path}: {len(raw)} -> {len(payload)} bytes "
              f"({len(payload) - len(raw):+d})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
