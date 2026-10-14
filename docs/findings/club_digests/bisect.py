"""Where each of `tests/test_club_bpy.py`'s five golden digests changed, between Zoo 0.86.0 and a commit.

    python docs/findings/club_digests/bisect.py [--to HEAD] [--blender C:/blender/blender.exe]

Zoo's first-parent commits from 0.86.0 (5b15338, where three of the five were measured) to `--to` are the line. A
commit's digests come from `digests_at.py` run in Blender on a `git archive` of that commit, unpacked under
`_scratch/club_digests/` and removed after; each commit's result is kept in `digests_by_commit.json` beside this
script, so a rerun builds nothing twice.

The line is split where ANY key's digest differs between two ends, down to neighbouring commits: every point where
some digest changed, every key measured at each. ASSUMED, and said so: a digest that changes and changes back
between two measured commits is not seen.

Prints, per key, the commits its digest changed at (version, subject) and its value before and after, and writes
the same to `bisect.out.json`. Names no cause; the CHANGELOG entries are what to read next.
"""
import argparse
import io
import json
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

F = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
ZOO = F / "zoo"
SCR = F / "_scratch" / "club_digests"
CACHE = HERE / "digests_by_commit.json"
BASE = "5b15338"                                  # Zoo 0.86.0


def git(*args):
    return subprocess.run(["git", "-C", str(ZOO), *args], capture_output=True, text=True, check=True).stdout


def measure(commit, blender, cache):
    if commit in cache:
        return cache[commit]
    dest = SCR / commit
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True)
    blob = subprocess.run(["git", "-C", str(ZOO), "archive", commit], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(blob)) as tf:
        tf.extractall(dest)
    out = SCR / (commit + ".json")
    p = subprocess.run([blender, "-b", "--factory-startup", "--python", str(HERE / "digests_at.py"), "--",
                        str(dest), str(out)], cwd=str(dest), capture_output=True, text=True, timeout=900,
                       stdin=subprocess.DEVNULL)
    shutil.rmtree(dest, ignore_errors=True)
    if not out.is_file():
        tail = "\n".join((p.stdout + p.stderr).splitlines()[-6:])
        raise SystemExit("NOT MEASURED: %s (exit %d)\n%s" % (commit, p.returncode, tail))
    doc = json.loads(out.read_text(encoding="utf-8"))
    out.unlink()
    cache[commit] = {"zoo_version": doc["zoo_version"], "digests": doc["digests"], "stored": doc["stored"]}
    CACHE.write_text(json.dumps(cache, indent=1, sort_keys=True), encoding="utf-8")
    print("measured %s (%s): %s" % (commit, doc["zoo_version"],
                                    " ".join(v[:8] for _, v in sorted(doc["digests"].items()))), flush=True)
    return cache[commit]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", default="HEAD")
    ap.add_argument("--blender", default="C:/blender/blender.exe")
    args = ap.parse_args()
    line = [BASE] + git("rev-list", "--reverse", "--first-parent", "--abbrev-commit", "%s..%s" % (BASE, args.to)).split()
    subject = {c: git("log", "-1", "--format=%s", c).strip() for c in line}
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.is_file() else {}
    d = lambda i: measure(line[i], args.blender, cache)["digests"]
    changes = []

    def split(lo, hi):
        if d(lo) == d(hi):
            return
        if hi == lo + 1:
            changes.append(hi)
            return
        mid = (lo + hi) // 2
        split(lo, mid)
        split(mid, hi)

    split(0, len(line) - 1)
    keys = sorted(d(0))
    stored = cache[line[0]]["stored"]
    report = {"line": len(line), "from": line[0], "to": line[-1], "keys": {}}
    print("\n%d commits from %s (0.86.0) to %s; %d measured" % (len(line), line[0], line[-1],
                                                               sum(1 for c in line if c in cache)))
    for k in keys:
        rows = []
        for i in sorted(changes):
            a, b = d(i - 1)[k], d(i)[k]
            if a != b:
                rows.append({"commit": line[i], "subject": subject[line[i]][:120], "before": a, "after": b})
        report["keys"][k] = {"stored": stored[k], "at_0_86_0": d(0)[k], "at_end": d(len(line) - 1)[k],
                             "changes": rows}
        print("\n%s\n  stored %s; at 0.86.0 %s; at %s %s" % (k, stored[k][:12], d(0)[k][:12], line[-1],
                                                            d(len(line) - 1)[k][:12]))
        for r in rows:
            print("  changed at %s  %s -> %s  %s" % (r["commit"], r["before"][:10], r["after"][:10], r["subject"]))
    (HERE / "bisect.out.json").write_text(json.dumps(report, indent=1), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
