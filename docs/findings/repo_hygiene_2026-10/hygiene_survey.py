"""Survey every repo under the factory root: untracked files and dirs with
sizes, tracked root-level files that look like scratch, and the biggest
directories. Reports; moves nothing.

    python hygiene_survey.py
"""
import os
import subprocess
import sys

ROOT = r"C:\Projects\gabagool_studios\gabagool_factory"
REPOS = ["", "deli_counter", "dispatch", "lasertag", "level_factory", "lot", "lux",
         "patina", "pipeline", "pixelcoat", "zoo"]
SCRATCH_EXT = {".txt", ".log", ".json", ".csv", ".png", ".md", ".bak", ".orig", ".tmp"}


def du(path):
    total = 0
    for dp, dn, fn in os.walk(path):
        dn[:] = [d for d in dn if d != ".git"]
        for f in fn:
            try:
                total += os.path.getsize(os.path.join(dp, f))
            except OSError:
                pass
    return total


def git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args), capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout


def main():
    for rel in REPOS:
        repo = os.path.join(ROOT, rel) if rel else ROOT
        if not os.path.isdir(os.path.join(repo, ".git")):
            continue
        print("\n" + "=" * 78)
        print("REPO", rel or "(factory root)", "|", git(repo, "log", "--oneline", "-1").strip()[:70])
        untracked = [ln[3:] for ln in git(repo, "status", "--porcelain", "--untracked-files=all").splitlines()
                     if ln.startswith("??")]
        modified = [ln for ln in git(repo, "status", "--porcelain").splitlines() if not ln.startswith("??")]
        if modified:
            print("  MODIFIED/STAGED (%d):" % len(modified))
            for m in modified[:15]:
                print("    " + m)
        # group untracked by top directory
        groups = {}
        for u in untracked:
            top = u.split("/")[0] if "/" in u else "(root)"
            groups.setdefault(top, []).append(u)
        print("  UNTRACKED: %d files in %d groups" % (len(untracked), len(groups)))
        for top, files in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            size = sum(os.path.getsize(os.path.join(repo, f)) for f in files if os.path.exists(os.path.join(repo, f)))
            sample = ", ".join(sorted(files)[:4])
            print("    %-28s %5d file(s) %8.1f MB  e.g. %s" % (top, len(files), size / 1e6, sample[:90]))
        # tracked root-level files that look like scratch
        tracked = git(repo, "ls-files").splitlines()
        root_tracked = [t for t in tracked if "/" not in t]
        scratchy = [t for t in root_tracked if os.path.splitext(t)[1].lower() in SCRATCH_EXT
                    and t.upper() not in ("README.MD", "CHANGELOG.MD", "LICENSE.MD", "CLAUDE.MD")]
        print("  TRACKED root files: %d; scratch-looking: %s" % (len(root_tracked), ", ".join(sorted(scratchy))[:400]))
        # gitignore
        gi = os.path.join(repo, ".gitignore")
        print("  .gitignore: %s" % ("present, %d lines" % len(open(gi, encoding="utf-8", errors="replace").read().splitlines()) if os.path.exists(gi) else "MISSING"))
        # biggest dirs
        sizes = []
        for d in os.listdir(repo):
            p = os.path.join(repo, d)
            if os.path.isdir(p) and d != ".git":
                sizes.append((du(p), d))
        sizes.sort(reverse=True)
        print("  biggest dirs: " + ", ".join("%s %.0f MB" % (d, s / 1e6) for s, d in sizes[:6]))


if __name__ == "__main__":
    main()
