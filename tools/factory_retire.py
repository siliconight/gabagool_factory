"""Retire regenerable output by rule, so the disk stops filling between passes.

    python tools/factory_retire.py             # what would go, and why; removes nothing
    python tools/factory_retire.py --apply     # remove it
    python tools/factory_retire.py --selftest  # prove the rules on a throwaway tree

Dry-run by default, like `scripts/factory_clean.ps1`. Nothing git tracks is
ever touched, and nothing under docs/ or patches/ is looked at: those are
records. THE RULES, each from docs/FILING.md:

  perf copies    _runs/perf_inner/<name>/ whose <name>.json exists. The rule
                 since cold run 9163 filled the disk: the JSON is the
                 measurement, the copy was its input. 9.2 GB on 2026-10-06.
  walk exports   _runs/walk_export_<name>/ untouched for WALK_EXPORT_DAYS. One
                 directory per name, overwritten by each export, so "older than
                 the newest" never applies: the first rule here said that and
                 its selftest refuted it. 4.4 GB in 28 on 2026-10-06.
  workspaces     workspaces/cold-N-ws/ beyond the newest KEEP_WORKSPACES, unless
                 a file under docs/ or a tool repo's tests names it (a finding
                 that still reads one keeps it). Regenerable from
                 docs/cold_runs/cold_N/.

Everything else under _runs/ is left alone: `_runs/cold/` is the clock's
journal, `_runs/measurements/` is tracked, and the loose probe outputs at its
top are somebody's, to be archived by hand under _scratch/.
"""
import os
import re
import shutil
import subprocess
import sys

KEEP_WORKSPACES = 12
WALK_EXPORT_DAYS = 30


def _size(path):
    total = 0
    for dp, _dn, fn in os.walk(path):
        for f in fn:
            try:
                total += os.path.getsize(os.path.join(dp, f))
            except OSError:
                pass
    return total


def _referenced_workspaces(root):
    """Every `workspaces/<name>-ws` a doc or a test names."""
    names = set()
    pat = re.compile(r"workspaces[/\\\\]([A-Za-z0-9_.-]+-ws)")
    dirs = [os.path.join(root, "docs"), os.path.join(root, "PIPELINE_ROADMAP.md")]
    dirs += [os.path.join(root, t, "tests") for t in os.listdir(root)
             if os.path.isdir(os.path.join(root, t, "tests"))]
    for d in dirs:
        paths = [d] if os.path.isfile(d) else [os.path.join(dp, f) for dp, _s, fs in os.walk(d) for f in fs]
        for p in paths:
            if os.path.splitext(p)[1].lower() not in (".md", ".py", ".txt", ".json"):
                continue
            try:
                names.update(pat.findall(open(p, encoding="utf-8", errors="replace").read()))
            except OSError:
                pass
    return names


def _tracked(root, rel):
    r = subprocess.run(["git", "-C", root, "ls-files", "--", rel], capture_output=True, text=True)
    return bool(r.stdout.strip())


def plan(root, keep=KEEP_WORKSPACES):
    """``[{path, why, bytes}]`` the rules would remove, newest-first within a rule."""
    out = []
    perf = os.path.join(root, "_runs", "perf_inner")
    if os.path.isdir(perf):
        jsons = {f[:-5] for f in os.listdir(perf) if f.endswith(".json")}
        for d in sorted(os.listdir(perf)):
            p = os.path.join(perf, d)
            if os.path.isdir(p) and (d in jsons or any(j.startswith(d) for j in jsons)):
                out.append({"path": p, "why": "perf copy, its JSON exists", "bytes": _size(p)})
    runs = os.path.join(root, "_runs")
    if os.path.isdir(runs):
        # ONE DIRECTORY PER NAME, overwritten by each export -- so "older than
        # the mission's newest" never fires (the first rule here, refuted by
        # its own selftest). A walk copy exists to be walked now; one nobody
        # has touched in WALK_EXPORT_DAYS is not being walked.
        import time
        cutoff = time.time() - WALK_EXPORT_DAYS * 86400
        for d in sorted(os.listdir(runs)):
            p = os.path.join(runs, d)
            if d.startswith("walk_export_") and os.path.isdir(p) and os.path.getmtime(p) < cutoff:
                out.append({"path": p, "why": "walk export untouched for %d days" % WALK_EXPORT_DAYS, "bytes": _size(p)})
    ws = os.path.join(root, "workspaces")
    if os.path.isdir(ws):
        cold = [d for d in os.listdir(ws) if re.fullmatch(r"cold-\d+-ws", d)]
        cold.sort(key=lambda d: int(d.split("-")[1]), reverse=True)
        named = _referenced_workspaces(root)
        for d in cold[keep:]:
            if d in named or _tracked(root, "workspaces/" + d):
                continue
            p = os.path.join(ws, d)
            out.append({"path": p, "why": "cold-run workspace beyond the newest %d, unreferenced" % keep, "bytes": _size(p)})
    return out


def selftest():
    import tempfile
    root = tempfile.mkdtemp(prefix="factory_retire_")
    os.makedirs(os.path.join(root, "_runs", "perf_inner", "a"))
    os.makedirs(os.path.join(root, "_runs", "perf_inner", "b"))
    open(os.path.join(root, "_runs", "perf_inner", "a.json"), "w").write("{}")
    import time
    for d, age in (("walk_export_m1", 1), ("walk_export_m2", WALK_EXPORT_DAYS + 5)):
        p = os.path.join(root, "_runs", d)
        os.makedirs(p)
        os.utime(p, (time.time() - age * 86400, time.time() - age * 86400))
    os.makedirs(os.path.join(root, "docs"))
    open(os.path.join(root, "docs", "f.md"), "w").write("see workspaces/cold-3-ws\n")
    for n in range(1, 6):
        os.makedirs(os.path.join(root, "workspaces", "cold-%d-ws" % n))
    subprocess.run(["git", "-C", root, "init", "-q"])
    got = plan(root, keep=2)
    whys = sorted(os.path.basename(p["path"]) + ": " + p["why"].split(",")[0].split(" older")[0].split(" beyond")[0] for p in got)
    assert "a: perf copy" in whys and not any(w.startswith("b:") for w in whys), whys
    assert "cold-1-ws: cold-run workspace" in whys and "cold-2-ws: cold-run workspace" in whys, whys
    assert not any(w.startswith("cold-3-ws") for w in whys), "a referenced workspace stays"
    assert not any(w.startswith("cold-4-ws") or w.startswith("cold-5-ws") for w in whys), "the newest stay"
    assert any(w.startswith("walk_export_m2") for w in whys), whys
    assert not any(w.startswith("walk_export_m1") for w in whys), "a fresh walk copy stays"
    shutil.rmtree(root, ignore_errors=True)
    print("selftest ok")


def main():
    argv = sys.argv[1:]
    if "--selftest" in argv:
        return selftest()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import factory_index
    root = factory_index.factory_root()
    items = plan(root)
    total = sum(p["bytes"] for p in items)
    for p in items:
        print("  %7.0f MB  %-70s %s" % (p["bytes"] / 1e6, os.path.relpath(p["path"], root), p["why"]))
    print("  %d item(s), %.1f GB %s" % (len(items), total / 1e9, "removed" if "--apply" in argv else "retirable (dry run; --apply removes)"))
    if "--apply" in argv:
        for p in items:
            shutil.rmtree(p["path"], ignore_errors=False)


if __name__ == "__main__":
    main()
