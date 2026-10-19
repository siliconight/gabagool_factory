"""The disk retire the walker approved on 2026-10-16, when C: was 100 % full (466 GB, 447 MB free) and cold run
9319 died on it at the art stage. Two rules, both the walker's call that morning:

  * cold-run workspaces whose record is PUSHED (docs/cold_runs/cold_N/NOTES.md tracked), beyond the newest four
    -- regenerable from the record, as `tools/factory_retire.py`'s own `pushed runs` rule says; the retire tool
    kept them because findings name them literally, and a name in a record was never meant to pin a gigabyte.
  * `_runs/` entries last touched before 2026-10-01 -- perf copies, A/B arms and probes whose JSON records are
    in docs/ (the memory rule since cold run 9163: the JSON is the measurement, the copy was its input).

Dry run by default: prints every path it would remove and the count, writes the list beside this file. With
--apply it removes exactly that list, each by its literal absolute path, refusing anything outside
workspaces/ or _runs/ and refusing the process's own working directory.

    python docs/findings/disk_full_2026_10_16/retire_approved.py            # list
    python docs/findings/disk_full_2026_10_16/retire_approved.py --apply    # remove
"""
import datetime
import os
import re
import shutil
import subprocess
import sys

ROOT = r"C:\Projects\gabagool_studios\gabagool_factory"
HERE = os.path.dirname(os.path.abspath(__file__))
KEEP_NEWEST = 4
CUTOFF = datetime.date(2026, 10, 1)


def _tracked(*roots):
    """Every path git tracks under the given repo-relative roots, '/'-separated."""
    return set(subprocess.run(["git", "-C", ROOT, "ls-files", *roots],
                              capture_output=True, text=True, check=True).stdout.split())


def plan():
    tracked = _tracked("docs/cold_runs")
    ws = os.path.join(ROOT, "workspaces")
    cold = sorted(int(m.group(1)) for d in os.listdir(ws) if (m := re.match(r"cold-(\d+)-ws$", d)))
    pushed = [n for n in cold if f"docs/cold_runs/cold_{n}/NOTES.md" in tracked]
    keep = sorted(pushed)[-KEEP_NEWEST:]
    paths = [os.path.join(ws, f"cold-{n}-ws") for n in pushed if n not in keep]
    runs = os.path.join(ROOT, "_runs")
    for e in sorted(os.listdir(runs)):
        p = os.path.join(runs, e)
        if datetime.date.fromtimestamp(os.path.getmtime(p)) < CUTOFF:
            paths.append(p)
    # NOTHING GIT TRACKS, the retire tool's own rule (`tools/factory_retire.py`). The run of 2026-10-16 had
    # no such guard and took `_runs/attic/`, which held one tracked file
    # (`_runs/attic/test_themed_selection.py.pending`); it was restored from git on 2026-10-18 and this guard
    # added, so the script as kept cannot do it again. A path that IS a tracked file, or holds one, stays.
    held = _tracked("_runs", "workspaces")
    kept_tracked = []
    for p in list(paths):
        rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
        if rel in held or any(t.startswith(rel + "/") for t in held):
            paths.remove(p)
            kept_tracked.append(rel)
    return keep, paths, kept_tracked


def main(argv):
    keep, paths, kept_tracked = plan()
    print(f"keeping the newest pushed cold workspaces {keep}; {len(paths)} paths to remove")
    for rel in kept_tracked:
        print(f"   kept, git tracks it or a file in it: {rel}")
    for p in paths[:5] + ["..."] + paths[-3:]:
        print("  ", p)
    if "--apply" not in argv:
        return 0
    # THE RECORD IS WRITTEN ONCE. `retired_paths.txt` is the list the run of 2026-10-16 removed (682 paths);
    # a later run must not overwrite it, and writes its own list beside it under its own date.
    listing = os.path.join(HERE, "retired_paths.txt")
    if os.path.exists(listing):
        listing = os.path.join(HERE, "retired_paths_%s.txt" % datetime.date.today().isoformat())
        assert not os.path.exists(listing), f"refusing: {listing} already records a run today"
    with open(listing, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(paths) + "\n")
    print(f"listed in {listing}")
    cwd = os.path.normcase(os.path.abspath(os.getcwd()))
    removed, bytes_freed = 0, 0
    for p in paths:
        ap = os.path.normcase(os.path.abspath(p))
        assert ap.startswith(os.path.normcase(os.path.join(ROOT, "workspaces"))) or \
            ap.startswith(os.path.normcase(os.path.join(ROOT, "_runs"))), p
        assert not cwd.startswith(ap), f"refusing: {p} holds the working directory"
        if os.path.isdir(p) and not os.path.islink(p):
            shutil.rmtree(p, ignore_errors=False)
        elif os.path.exists(p):
            os.remove(p)
        removed += 1
    print(f"removed {removed} paths")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
