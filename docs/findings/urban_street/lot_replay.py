"""Real Lot jobs replayed before and after a change to Lot: does a strip level move? (roadmap 241, the near side)

    python docs/findings/urban_street/lot_replay.py replay <tag> [<cold run N> ...]
    python docs/findings/urban_street/lot_replay.py diff <tag_a> <tag_b>

The urban near side asks Lot's planners -- parking fields, dumpsters and their pads, cover -- to treat
`blockers` (the Empties) as solid; until now they read the mission's buildings only, which was harmless while
every Empty stood across the road, where none of them places anything. On a strip level that change should move
nothing, and that is what this measures. `docs/findings/door_widths/cover_fallback_ab.py`'s replay (the Lot
0.120.2 session's), generalised from one job to many.

replay   for each cold run N named (default: every workspace on this disk from 9278 to 9287), the PICKED
         candidate's `lot_assemble` job (the seed `pick_candidate.py` printed in that run's driver log): the two
         commands its `job.log` records -- `stage_site_packages.py`, then `lot.py` -- with the job's interpreter
         and working directories, the out dir swapped for `_scratch/2026-10-13_lot_replay/run/<job>/out`, the
         same path for a job every time, so a path a file embeds cannot differ between tags; then moved to
         `<tag>/<job>/out`, with the commands' output in `<tag>/<job>/replay.log`.
diff     compares every file under two tags' outs, job by job, byte for byte, and prints each job's count of
         files that differ, which they are, and a total.

Prints what it measured and stops.
"""
import os
import pathlib
import re
import shutil
import subprocess
import sys

FACTORY = pathlib.Path(__file__).resolve().parents[3]
SCRATCH = FACTORY / "_scratch" / "2026-10-13_lot_replay"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}
DEFAULT_RUNS = range(9278, 9288)


def _picked_job(n):
    """(job dir, name) of cold run N's picked candidate's lot_assemble job, or None."""
    log = FACTORY / "docs" / "cold_runs" / f"cold_{n}" / "driver.log"
    ws = FACTORY / "workspaces" / f"cold-{n}-ws" / ".level_factory" / "jobs"
    if not log.exists() or not ws.exists():
        return None
    t = log.read_text(encoding="utf-8", errors="replace")
    seed = re.search(r"picked seed_(\d+)", t)
    jobs = sorted(ws.glob(f"*.lot_assemble.candidate.seed_{seed.group(1)}")) if seed else []
    if len(jobs) != 1:
        return None
    return jobs[0] / "1", f"{n}_{jobs[0].name.split('.')[0]}_seed_{seed.group(1)}"


def _commands(job, run_out):
    """The job's commands as its log records them: (argv, cwd), the job's out dir swapped for `run_out`."""
    lines = (job / "job.log").read_text(encoding="utf-8").splitlines()
    job_out = str(job / "out")
    cmds = []
    for i, line in enumerate(lines):
        if not line.startswith("$ "):
            continue
        cwd = lines[i + 1]
        if not (cwd.startswith("(cwd=") and cwd.endswith(")")):
            sys.exit(f"refusing: no (cwd=...) under {line[:60]!r}")
        if '"' in line or "'" in line:
            sys.exit(f"refusing: a quoted argument, which a split on spaces would break: {line[:80]!r}")
        argv = line[2:].split(" ")
        if argv.count(job_out) != 1:
            sys.exit(f"refusing: the job's out dir appears {argv.count(job_out)} times in {line[:80]!r}")
        cmds.append(([str(run_out) if a == job_out else a for a in argv], cwd[5:-1]))
    if len(cmds) != 2 or not cmds[1][0][1].endswith("lot.py"):
        sys.exit(f"refusing: expected stage + lot.py, read {[c[0][1] for c in cmds]}")
    return cmds


def replay(tag, runs):
    for n in runs:
        found = _picked_job(n)
        if found is None:
            print(f"{n}: no picked lot_assemble job on this disk")
            continue
        job, name = found
        dest = SCRATCH / tag / name
        if dest.exists():
            sys.exit(f"refusing: {dest} exists")
        run_out = SCRATCH / "run" / name / "out"
        if run_out.exists():
            shutil.rmtree(run_out)
        run_out.parent.mkdir(parents=True, exist_ok=True)
        log = []
        for argv, cwd in _commands(job, run_out):
            r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", env=ENV)
            log.append(f"$ {' '.join(argv)}\n(cwd={cwd})\n{r.stdout}{r.stderr}(exit={r.returncode})\n")
            if r.returncode:
                sys.exit(f"{name}: {argv[1]} exited {r.returncode}:\n{r.stdout[-1500:]}{r.stderr[-1500:]}")
        dest.mkdir(parents=True)
        shutil.move(str(run_out), str(dest / "out"))
        (dest / "replay.log").write_bytes("".join(log).encode("utf-8"))
        print(f"{name}: {sum(1 for p in (dest / 'out').rglob('*') if p.is_file())} files")


def diff(a, b):
    total = 0
    for job in sorted(p.name for p in (SCRATCH / a).iterdir() if p.is_dir()):
        oa, ob = SCRATCH / a / job / "out", SCRATCH / b / job / "out"
        if not ob.exists():
            print(f"{job}: missing under {b}")
            total += 1
            continue
        fa = {p.relative_to(oa).as_posix() for p in oa.rglob("*") if p.is_file()}
        fb = {p.relative_to(ob).as_posix() for p in ob.rglob("*") if p.is_file()}
        moved = sorted(f for f in fa & fb if (oa / f).read_bytes() != (ob / f).read_bytes())
        only = sorted(fa ^ fb)
        total += len(moved) + len(only)
        print(f"{job}: {len(fa & fb)} common, {len(moved)} differ, {len(only)} in one only"
              + (f" -- {moved[:6]}{' ...' if len(moved) > 6 else ''}" if moved else "")
              + (f" only: {only[:4]}" if only else ""))
    print(f"total files that differ or stand in one tag only: {total}")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "replay":
        replay(sys.argv[2], [int(x) for x in sys.argv[3:]] or DEFAULT_RUNS)
    elif len(sys.argv) == 4 and sys.argv[1] == "diff":
        diff(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
