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
                 a file under docs/ -- a record or its script -- or a tool repo's tests names it (a finding
                 that still reads one keeps it). Regenerable from
                 docs/cold_runs/cold_N/.

VERIFIED MEANS PUSHED (2026-10-11, the walker: "a package clean job so we
don't accrue GBs of packages that have already been pushed and verified as
known good"). Once a record is in the branch the root pushes to, what it
describes can be made again from it. None of these fires without an upstream:

  pushed runs    a cold-run workspace beyond the newest KEEP_PUSHED whose
                 docs/cold_runs/cold_N/NOTES.md is pushed (a price takes the
                 previous run's package as its control, so four stay).
  release zips   ../gabagool_factory_package_factory-vX.Y.Z.zip whose
                 docs/releases/factory-vX.Y.Z.md is pushed, but not the newest.
  test zips      ../gabagool_factory_package_<stamp>.zip a pushed record names.
  test unpacks   an install test's unpack (its script's DEST) whose
                 docs/findings/stranger_install/install_test_N/ is pushed, but
                 not the newest.

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
#: the files a reference scan reads: records, and the scripts a record carries
_SCANNED = (".md", ".py", ".txt", ".json", ".sh", ".ps1", ".cmd", ".bat", ".gd")
WALK_EXPORT_DAYS = 30
#: Pushed runs' workspaces kept, newest first: a price's control is the run before.
KEEP_PUSHED = 4
_TAGGED = re.compile(r"gabagool_factory_package_(factory-v(\d+)\.(\d+)\.(\d+))\.zip")
_STAMPED = re.compile(r"gabagool_factory_package_\d{8}_\d{4}\.zip")


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
            # a record's scripts name workspaces too: 9240's roof_frames.sh names
            # its control package, and a scan of .md/.py/.txt/.json missed it
            if os.path.splitext(p)[1].lower() not in _SCANNED:
                continue
            try:
                names.update(pat.findall(open(p, encoding="utf-8", errors="replace").read()))
            except OSError:
                pass
    return names


def _tracked(root, rel):
    r = subprocess.run(["git", "-C", root, "ls-files", "--", rel], capture_output=True, text=True)
    return bool(r.stdout.strip())


def _upstream(root):
    """The branch the root pushes to (`origin/main`), or None: then nothing is pushed."""
    r = subprocess.run(["git", "-C", root, "rev-parse", "--abbrev-ref",
                        "--symbolic-full-name", "@{u}"], capture_output=True, text=True)
    return (r.stdout.strip() or None) if r.returncode == 0 else None


def _pushed(root, upstream, rel):
    """Whether ``rel`` -- a file or a folder -- is in the pushed branch."""
    r = subprocess.run(["git", "-C", root, "cat-file", "-e", "%s:%s" % (upstream, rel)],
                       capture_output=True)
    return r.returncode == 0


def _pushed_mentions(root, upstream, needle):
    """Whether a pushed file under docs/ names ``needle``."""
    r = subprocess.run(["git", "-C", root, "grep", "-l", "-F", needle, upstream, "--", "docs"],
                       capture_output=True, text=True)
    return r.returncode == 0 and bool(r.stdout.strip())


def _stranger_installs(root):
    """``[(N, folder)]``: each install test's unpack, from its own script's DEST."""
    out = []
    d = os.path.join(root, "docs", "findings", "stranger_install")
    if not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        m = re.fullmatch(r"install_test_(\d+)\.sh", f)
        if not m:
            continue
        text = open(os.path.join(d, f), encoding="utf-8", errors="replace").read()
        dm = re.search(r"^DEST='([^']+)'", text, re.M)
        if not dm:
            continue
        folder = os.path.dirname(dm.group(1).rstrip("\\/"))
        if re.fullmatch(r"stranger_202_\d+", os.path.basename(folder)):
            out.append((int(m.group(1)), folder))
    return out


def plan(root, keep=KEEP_WORKSPACES, keep_pushed=KEEP_PUSHED, package_dir=None):
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
    upstream = _upstream(root)
    if not upstream:
        return out
    already = {o["path"] for o in out}
    if os.path.isdir(ws):
        for d in cold[keep_pushed:]:
            p = os.path.join(ws, d)
            if p in already or d in named or _tracked(root, "workspaces/" + d):
                continue
            n = d.split("-")[1]
            if _pushed(root, upstream, "docs/cold_runs/cold_%s/NOTES.md" % n):
                out.append({"path": p, "why": "cold-run workspace beyond the newest %d whose record is pushed" % keep_pushed, "bytes": _size(p)})
    pdir = package_dir or os.path.dirname(os.path.abspath(root))
    if os.path.isdir(pdir):
        zips = sorted(f for f in os.listdir(pdir) if f.startswith("gabagool_factory_package_") and f.endswith(".zip"))
        tagged = sorted((f for f in zips if _TAGGED.fullmatch(f)),
                        key=lambda f: tuple(int(x) for x in _TAGGED.fullmatch(f).group(2, 3, 4)))
        for f in zips:
            p = os.path.join(pdir, f)
            m = _TAGGED.fullmatch(f)
            if m:
                if f != tagged[-1] and _pushed(root, upstream, "docs/releases/%s.md" % m.group(1)):
                    out.append({"path": p, "why": "release package whose notes are pushed, not the newest release", "bytes": os.path.getsize(p)})
            elif _STAMPED.fullmatch(f) and _pushed_mentions(root, upstream, f):
                out.append({"path": p, "why": "install-test package a pushed record names", "bytes": os.path.getsize(p)})
    live = [(n, d) for n, d in _stranger_installs(root) if os.path.isdir(d)]
    newest = max((n for n, _d in live), default=None)
    for n, d in live:
        if n != newest and _pushed(root, upstream, "docs/findings/stranger_install/install_test_%d" % n):
            out.append({"path": d, "why": "install-test unpack whose record is pushed, not the newest", "bytes": _size(d)})
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
    # a record's script names cold-2-ws as its control package
    os.makedirs(os.path.join(root, "docs", "cold_runs", "cold_6"))
    open(os.path.join(root, "docs", "cold_runs", "cold_6", "frames.sh"), "w").write(
        'PKG_C="workspaces/cold-2-ws/.level_factory/exports/LF_x.portable-godot"\n')
    for n in range(1, 6):
        os.makedirs(os.path.join(root, "workspaces", "cold-%d-ws" % n))
    subprocess.run(["git", "-C", root, "init", "-q"])
    got = plan(root, keep=2)
    whys = sorted(os.path.basename(p["path"]) + ": " + p["why"].split(",")[0].split(" older")[0].split(" beyond")[0] for p in got)
    assert "a: perf copy" in whys and not any(w.startswith("b:") for w in whys), whys
    assert "cold-1-ws: cold-run workspace" in whys, whys
    assert not any(w.startswith("cold-2-ws") for w in whys), "a workspace a script names stays"
    assert not any(w.startswith("cold-3-ws") for w in whys), "a referenced workspace stays"
    assert not any(w.startswith("cold-4-ws") or w.startswith("cold-5-ws") for w in whys), "the newest stay"
    assert any(w.startswith("walk_export_m2") for w in whys), whys
    assert not any(w.startswith("walk_export_m1") for w in whys), "a fresh walk copy stays"
    shutil.rmtree(root, ignore_errors=True)
    _selftest_pushed()
    print("selftest ok")


def _selftest_pushed():
    """The pushed rules, on a tree with a bare upstream (2026-10-11)."""
    import tempfile
    base = tempfile.mkdtemp(prefix="factory_retire_pushed_")
    up, root, pkgs = (os.path.join(base, x) for x in ("up.git", "factory", "pkgs"))
    os.makedirs(pkgs)

    def git(*a):
        subprocess.run(["git", "-C", root, "-c", "user.name=t", "-c", "user.email=t@t"] + list(a),
                       check=True, capture_output=True)

    def write(rel, text):
        p = os.path.join(root, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(text)
    subprocess.run(["git", "init", "-q", "--bare", up], check=True, capture_output=True)
    os.makedirs(root)
    git("init", "-q")
    git("checkout", "-q", "-b", "main")
    write("docs/cold_runs/cold_1/NOTES.md", "run 1\n")
    write("docs/releases/factory-v1.0.0.md", "notes\n")
    write("docs/releases/factory-v1.1.0.md", "notes\n")
    write("docs/findings/stranger_install/README.md", "made gabagool_factory_package_20260101_0000.zip\n")
    for n in (1, 2):
        os.makedirs(os.path.join(base, "stranger_202_%d" % n, "gabagool"))
        write("docs/findings/stranger_install/install_test_%d.sh" % n,
              "DEST='%s'\n" % os.path.join(base, "stranger_202_%d" % n, "gabagool"))
    write("docs/findings/stranger_install/install_test_1/steps.txt", "ok\n")
    git("add", "-A")
    git("commit", "-q", "-m", "records")
    git("remote", "add", "origin", up)
    git("push", "-q", "-u", "origin", "main")
    # committed after the push, so NOT pushed: run 2's record and test 2's
    write("docs/cold_runs/cold_2/NOTES.md", "run 2\n")
    write("docs/findings/stranger_install/install_test_2/steps.txt", "ok\n")
    git("add", "-A")
    git("commit", "-q", "-m", "later")
    for n in range(1, 7):
        os.makedirs(os.path.join(root, "workspaces", "cold-%d-ws" % n))
    for f in ("factory-v1.0.0", "factory-v1.1.0", "20260101_0000", "20260202_0000"):
        open(os.path.join(pkgs, "gabagool_factory_package_%s.zip" % f), "wb").write(b"z")
    open(os.path.join(pkgs, "someone_else.zip"), "wb").write(b"z")
    got = sorted(os.path.basename(p["path"]) for p in plan(root, keep=12, keep_pushed=2, package_dir=pkgs))
    want = ["cold-1-ws", "gabagool_factory_package_20260101_0000.zip",
            "gabagool_factory_package_factory-v1.0.0.zip", "stranger_202_1"]
    assert got == want, got
    # with no upstream the pushed rules say nothing
    git("branch", "--unset-upstream")
    assert plan(root, keep=12, keep_pushed=2, package_dir=pkgs) == []
    shutil.rmtree(base, ignore_errors=True)


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
            if os.path.isdir(p["path"]):
                shutil.rmtree(p["path"], ignore_errors=False)
            else:
                os.remove(p["path"])


if __name__ == "__main__":
    main()
