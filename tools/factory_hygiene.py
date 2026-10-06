"""Is the factory filed the way docs/FILING.md says? One line per rule.

    python tools/factory_hygiene.py            # report
    python tools/factory_hygiene.py --check    # exit 1 on any failing rule
    python tools/factory_hygiene.py --brief    # one line, for cold_run.py --end

Read-only. It asks git, never .gitignore (the reason `factory_root_audit.py`
gives: fourteen overlapping rules across five sections, and `git check-ignore`
already knows the answer).

THE RULES, each a measurement with a number:
  LOOSE          root entries neither tracked nor ignored (`factory_root_audit.py`'s column)
  UNTRACKED      untracked, unignored files inside every tool repo
  RECORDS        untracked files under docs/ and patches/: work whose record did not ship
  INDEX          generated indexes that drift from their folder (`factory_index.py --check`)
  UNDESCRIBED    indexed entries with no docstring or heading to show
  RETIRABLE      bulk the retention rule would remove (`factory_retire.py`), in GB -- reported, never failed on
  FINDINGS       finding folders without a README -- reported, never failed on
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import factory_index  # noqa: E402

TOOLS = ("deli_counter", "dispatch", "lasertag", "level_factory", "lot",
         "lux", "patina", "pipeline", "pixelcoat", "zoo")


def git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args), capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout


def loose_at_root(root):
    tracked = set(p.split("/")[0] for p in git(root, "ls-files").splitlines())
    out = []
    for e in sorted(os.listdir(root)):
        if e == ".git" or e in TOOLS or e in tracked:
            continue
        r = subprocess.run(["git", "-C", root, "check-ignore", "-q", e])
        if r.returncode != 0:
            out.append(e)
    return out


def untracked_in(repo):
    return [ln[3:] for ln in git(repo, "status", "--porcelain", "--untracked-files=all").splitlines()
            if ln.startswith("??")]


def main():
    root = factory_index.factory_root()
    argv = sys.argv[1:]
    fails = []
    lines = []

    loose = loose_at_root(root)
    lines.append(("LOOSE", len(loose), ", ".join(loose)))
    if loose:
        fails.append("LOOSE")

    untracked = {}
    for t in TOOLS:
        repo = os.path.join(root, t)
        if os.path.isdir(os.path.join(repo, ".git")):
            u = untracked_in(repo)
            if u:
                untracked[t] = u
    n_un = sum(len(v) for v in untracked.values())
    lines.append(("UNTRACKED", n_un, "; ".join("%s: %s%s" % (k, ", ".join(v[:3]), " ..." if len(v) > 3 else "")
                                                for k, v in untracked.items())))
    if n_un:
        fails.append("UNTRACKED")

    # docs/ and patches/ are records by definition; every indexed folder is
    # too, because the index generator writes a README there. The first
    # version watched the first two only and passed two untracked READMEs
    # under migrations/ and scripts/ (2026-10-06).
    watched = ("docs/", "patches/") + tuple(k + "/" for k in factory_index.REGISTRY if "/" not in k)
    records = [u for u in untracked_in(root) if u.startswith(watched)]
    lines.append(("RECORDS", len(records), ", ".join(records[:5]) + (" ..." if len(records) > 5 else "")))
    if records:
        fails.append("RECORDS")

    drift, undescribed = [], 0
    for rel, title in factory_index.REGISTRY.items():
        folder = os.path.join(root, rel)
        if not os.path.isdir(folder):
            continue
        readme = os.path.join(folder, "README.md")
        existing = open(readme, encoding="utf-8").read() if os.path.exists(readme) else ""
        block = factory_index.render(folder, title)
        if factory_index.current_block(existing) != block:
            drift.append(rel)
        undescribed += block.count("(undescribed)")
    lines.append(("INDEX", len(drift), ", ".join(drift)))
    if drift:
        fails.append("INDEX")
    lines.append(("UNDESCRIBED", undescribed, "entries without a docstring or heading"))

    try:
        import factory_retire
        plan = factory_retire.plan(root)
        gb = sum(p["bytes"] for p in plan) / 1e9
        lines.append(("RETIRABLE", round(gb, 1), "GB in %d item(s); tools/factory_retire.py" % len(plan)))
    except Exception as exc:  # reported, never a failure
        lines.append(("RETIRABLE", "?", "factory_retire could not run: %s" % exc))

    findings = os.path.join(root, "docs", "findings")
    bare = [d for d in sorted(os.listdir(findings))
            if os.path.isdir(os.path.join(findings, d))
            and not os.path.exists(os.path.join(findings, d, "README.md"))]
    lines.append(("FINDINGS", len(bare), "folders without a README"))

    if "--brief" in argv:
        print("hygiene: " + "  ".join("%s %s" % (k, v) for k, v, _ in lines)
              + ("  -- FAILING: " + ", ".join(fails) if fails else "  -- clean"))
    else:
        for k, v, detail in lines:
            print("  %-12s %-6s %s" % (k, v, detail[:150]))
        print("  " + ("FAILING: " + ", ".join(fails) if fails else "clean"))
    if "--check" in argv and fails:
        sys.exit(1)


if __name__ == "__main__":
    main()
