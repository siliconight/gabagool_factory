"""Ship a change to a tool repo: clone, smoke, patch, prove, apply -- one tool for the steps every change takes.

    python tools/ship_change.py clone <repo> <name>
        a scratch clone of <repo> at _scratch/<name>, to edit in place
    python tools/ship_change.py smoke <batch.json> --ws <workspace> [--lf <level_factory clone>]
        make the smallest level that exercises the change and print what failed, before any long suite
    python tools/ship_change.py patch <repo> <clone> <name> --doc <file> [--whole-over N]
        write patches/patch_<name>.py from the clone's diff against <repo>'s HEAD, then dry-run it twice:
        the first run must reproduce the clone byte for byte, the second must refuse
    python tools/ship_change.py prove-old <repo> <clone> <name> --tests <t> [<t> ...] [--blender]
        run the clone's new or changed tests against <repo>'s HEAD; at least one must fail
    python tools/ship_change.py apply <repo> <name> --message <file> [--suite]
        run the patch on the real repo, fold in what `factory_index.py --write` changes inside it, commit, check
        the message carries no attribution, push

WHY ONE TOOL (the walker's yes, 2026-10-28; docs/SHIPPING_A_CHANGE.md section 5). Each change used to get its own
hand-copied generator, dry run and apply script, and the copies cost round trips of their own: an assert too broad
for the copy's new names, a heredoc that ate a backslash, a guard that refused a staged new file. The same day two
release steps were found missing at the end of the chain -- an index line committed after a tool's tag, which made
the tool STALE -- and `apply` now writes the index first and commits it with the change.

THE SUITE RUNS ONCE, ON THE CLONE. `patch` proves the applied repo byte-identical to the clone, so `apply` runs no
suite unless asked (`--suite`), for an apply that writes what the clone did not. A repo's own commit hook still runs.

WHAT A PATCH IS. Every file the clone changed, pinned by the sha256 of its LF text and either edited by anchored
hunks (each widened by context until it occurs once, then merged where they touch) or, past `--whole-over` hunks,
carried whole; every new file embedded. It refuses on any pin or anchor that does not hold and writes nothing until
all of them do. Each file keeps the line endings it has on disk. Files under `build/` are never carried: a repo
rebuilds them.

Prints what it did and stops; exit 1 on any failure.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

FACTORY = pathlib.Path(__file__).resolve().parents[1]
SCRATCH = FACTORY / "_scratch"
PATCHES = FACTORY / "patches"
ATTRIBUTION = re.compile(r"co-authored-by|generated with|claude-session", re.I)


class Failed(Exception):
    pass


def git(repo, *args, check=True):
    r = subprocess.run(["git", "-C", str(repo)] + list(args), capture_output=True, text=True)
    if check and r.returncode != 0:
        raise Failed("git %s: %s" % (" ".join(args), (r.stderr or r.stdout).strip()[-400:]))
    return r.stdout


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def lf_text(raw, what):
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    if crlf not in (0, lf):
        raise Failed("%s has mixed line endings (%d CRLF of %d)" % (what, crlf, lf))
    return raw.decode("utf-8").replace("\r\n", "\n")


def hunks(old, new):
    """[(what, old_text, new_text)] turning ``old`` into ``new``: each change widened by context until its old text
    occurs once, windows that touch merged, so applying them in order never asks for rewritten text."""
    a, b = old.splitlines(keepends=True), new.splitlines(keepends=True)
    ops = difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()

    def bstart(i):
        for tag, i1, i2, j1, j2 in ops:
            if tag == "equal" and i1 <= i <= i2:
                return j1 + (i - i1)
            if i == i1:
                return j1
        return len(b)

    def bend(i):
        pos = 0
        for tag, i1, i2, j1, j2 in ops:
            if i1 > i:
                break
            pos = j1 + (i - i1) if (tag == "equal" and i <= i2) else j2
        return pos

    wins = []
    for tag, i1, i2, _j1, _j2 in ops:
        if tag == "equal":
            continue
        ctx = 0
        while True:
            lo, hi = max(0, i1 - ctx), min(len(a), i2 + ctx)
            o = "".join(a[lo:hi])
            if o and old.count(o) == 1:
                break
            ctx += 1
            if ctx >= 60:
                raise Failed("no unique anchor near line %d" % (i1 + 1))
        wins.append([lo, hi])
    merged = []
    for w in wins:
        if merged and w[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], w[1])
        else:
            merged.append(w)
    return [("lines %d-%d" % (lo + 1, hi), "".join(a[lo:hi]), "".join(b[bstart(lo):bend(hi)])) for lo, hi in merged]


def apply_hunks(text, edits, what):
    for where, o, n in edits:
        if text.count(o) != 1:
            raise Failed("%s: the anchor at %s is there %d times" % (what, where, text.count(o)))
        text = text.replace(o, n)
    return text


# ---- clone ----------------------------------------------------------------------------------------------------

def cmd_clone(args):
    dest = SCRATCH / args.name
    if dest.exists():
        raise Failed("%s exists; pick another name or remove it" % dest)
    git(FACTORY, "clone", "-q", str(FACTORY / args.repo), str(dest))
    print("cloned %s at %s into %s" % (args.repo, git(dest, "log", "-1", "--format=%h").strip(), dest))
    # A DELI COUNTER CLONE IS BUILT AT ONCE: git does not track every build output, and 23 of its tests read one --
    # the first clone this tool made ran its suite unbuilt and failed them all on missing files (0.287.1)
    if args.repo == "deli_counter":
        r = subprocess.run([sys.executable, "build.py", "--all"], cwd=str(dest), capture_output=True, text=True)
        print("build.py --all: exit %d" % r.returncode)
        if r.returncode != 0:
            raise Failed("the clone's build failed: %s" % (r.stdout + r.stderr).strip()[-400:])


# ---- smoke ----------------------------------------------------------------------------------------------------

def cmd_smoke(args):
    py = FACTORY / ".venv" / "Scripts" / "python.exe"
    if not py.exists():
        py = pathlib.Path(sys.executable)
    lf = pathlib.Path(args.lf) if args.lf else FACTORY / "level_factory"
    ws = pathlib.Path(args.ws)
    if ws.exists():
        raise Failed("%s exists: a smoke runs in a fresh workspace" % ws)
    r = subprocess.run([str(py), str(lf / "apps" / "cli" / "main.py"), "-C", str(ws), "make", args.batch],
                       capture_output=True, text=True, cwd=str(FACTORY))
    out = (r.stdout or "") + (r.stderr or "")
    print("make exit %d" % r.returncode)
    for line in out.splitlines():
        if re.search(r"STOPPED|failed$|FAILED|error|PASS \d+|grade", line):
            print("  " + line.strip()[:200])
    jobs = ws / ".level_factory" / "jobs"
    for log in sorted(jobs.glob("*/*/job.log")) if jobs.is_dir() else []:
        text = log.read_text(encoding="utf-8", errors="replace")
        if re.search(r"\(exit=[1-9]", text):
            print("== %s" % log.relative_to(jobs))
            for line in text.splitlines():
                if re.search(r"ERROR|Error|error|Traceback|refus", line):
                    print("  " + line.strip()[:220])
    return 0 if r.returncode == 0 else 1


# ---- patch ----------------------------------------------------------------------------------------------------

BODY = '''%(doc)s
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / %(repo)r
PINS = %(pins)r
EDITS = %(edits)r
WHOLE = %(whole)r
NEW_FILES = %(new)r


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _read(name):
    """The file's LF text and whether it is CRLF on disk; refuses mixed endings and a file that is not the pinned one."""
    raw = (REPO / name).read_bytes()
    crlf, lf = raw.count(b"\\r\\n"), raw.count(b"\\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: %%s/%%s has mixed line endings; nothing written" %% (REPO.name, name))
    text = raw.decode("utf-8").replace("\\r\\n", "\\n")
    if _sha(text) != PINS[name]:
        raise SystemExit("REFUSED: %%s/%%s is %%s, not the %%s this patch was written against; nothing written"
                         %% (REPO.name, name, _sha(text), PINS[name]))
    return text, crlf > 0


def main():
    out = {}
    for name, edits in EDITS.items():
        text, crlf = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: %%s/%%s: the anchor at %%s is there %%d times; nothing written"
                                 %% (REPO.name, name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text.replace("\\n", "\\r\\n") if crlf else text
    for name, text in WHOLE.items():
        _old, crlf = _read(name)
        out[name] = text.replace("\\n", "\\r\\n") if crlf else text
    for name in NEW_FILES:
        if (REPO / name).exists():
            raise SystemExit("REFUSED: %%s/%%s exists already; nothing written" %% (REPO.name, name))
    for name, text in out.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (REPO / name).parent.mkdir(parents=True, exist_ok=True)
        (REPO / name).write_bytes(text.encode("utf-8"))
    print("%%s: %%d files edited, %%d written" %% (REPO.name, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def changed_files(clone):
    """(modified tracked files, new untracked files) in ``clone``, ``build/`` excluded."""
    mod = [f for f in git(clone, "diff", "--name-only", "HEAD").split() if not f.startswith("build/")]
    new = [f for f in git(clone, "ls-files", "--others", "--exclude-standard").split() if not f.startswith("build/")]
    return mod, new


def cmd_patch(args):
    repo, clone = FACTORY / args.repo, pathlib.Path(args.clone)
    dest = PATCHES / ("patch_%s.py" % args.name)
    if dest.exists():
        raise Failed("%s exists" % dest)
    if git(clone, "rev-parse", "HEAD").strip() != git(repo, "rev-parse", "HEAD").strip():
        raise Failed("the clone was made from %s, not %s's HEAD: re-clone it" % (git(clone, "log", "-1", "--format=%h").strip(), args.repo))
    if git(repo, "status", "--porcelain").strip():
        raise Failed("%s has uncommitted changes" % args.repo)
    mod, new = changed_files(clone)
    if not mod and not new:
        raise Failed("the clone changed nothing")
    pins, edits, whole, new_files = {}, {}, {}, {}
    for name in mod:
        old = lf_text((repo / name).read_bytes(), "%s/%s" % (args.repo, name))
        want = lf_text((clone / name).read_bytes(), "the clone's " + name)
        pins[name] = sha(old)
        h = hunks(old, want)
        if apply_hunks(old, h, name) != want:
            raise Failed("%s: the hunks do not reproduce the clone's file" % name)
        if len(h) > args.whole_over:
            whole[name] = want
        else:
            edits[name] = h
        print("  %s: %s" % (name, "carried whole" if name in whole else "%d hunk(s)" % len(h)))
    for name in new:
        new_files[name] = lf_text((clone / name).read_bytes(), "the clone's " + name)
        print("  %s: new" % name)
    doc = pathlib.Path(args.doc).read_text(encoding="utf-8").rstrip("\n")
    if not doc.startswith('"""') or not doc.endswith('"""'):
        raise Failed("--doc must be a docstring, opening and closing with triple quotes")
    body = BODY % {"doc": doc, "repo": args.repo, "pins": pins, "edits": edits, "whole": whole, "new": new_files}
    compile(body, str(dest), "exec")
    dest.write_text(body, encoding="utf-8", newline="\n")
    print("wrote %s (%d chars)" % (dest, len(body)))
    dry_run(args.repo, clone, dest, mod + new)


def dry_run(repo_name, clone, patch, names):
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        root = pathlib.Path(tmp)
        (root / "patches").mkdir()
        git(FACTORY, "clone", "-q", str(FACTORY / repo_name), str(root / repo_name))
        shutil.copy2(patch, root / "patches" / patch.name)
        for n in (1, 2):
            r = subprocess.run([sys.executable, str(root / "patches" / patch.name)], capture_output=True, text=True)
            said = (r.stdout + r.stderr).strip().splitlines()[-1:]
            print("dry run %d: exit %d %s" % (n, r.returncode, said))
            if n == 1:
                if r.returncode != 0:
                    raise Failed("the first dry run failed")
                for name in names:
                    if (root / repo_name / name).read_bytes() != (clone / name).read_bytes():
                        raise Failed("dry run: %s is not the clone's, byte for byte" % name)
                print("  the dry clone's %d changed files are the clone's, byte for byte" % len(names))
            elif r.returncode == 0:
                raise Failed("the second dry run did not refuse")


# ---- prove-old ------------------------------------------------------------------------------------------------

def cmd_prove_old(args):
    clone = pathlib.Path(args.clone)
    out = PATCHES / args.name / "fails_on_old.out.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
        old = pathlib.Path(tmp) / args.repo
        git(FACTORY, "clone", "-q", str(FACTORY / args.repo), str(old))
        for t in args.tests:
            (old / t).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(clone / t, old / t)
        if args.blender:
            expr = ("import sys,pytest;sys.path.insert(0,'.');sys.exit(pytest.main(['-q','-p','no:cacheprovider',%s]))"
                    % ",".join(repr(t) for t in args.tests))
            cmd = [args.blender_exe, "-b", "--factory-startup", "--python-expr", expr]
        else:
            cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"] + list(args.tests)
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(old),
                           env=dict(os.environ, DC_ZOO_ROOT=str(FACTORY / "zoo")))
    lines = [l for l in (r.stdout + r.stderr).splitlines() if re.match(r"^(FAILED|ERROR)|\d+ (passed|failed)", l)]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(lines))
    if not any(l.startswith(("FAILED", "ERROR")) for l in lines):
        raise Failed("no test failed on %s's HEAD: a test that cannot fail proves nothing" % args.repo)
    print("wrote %s" % out)


# ---- apply ----------------------------------------------------------------------------------------------------

def cmd_apply(args):
    repo = FACTORY / args.repo
    patch = PATCHES / ("patch_%s.py" % args.name)
    message = pathlib.Path(args.message).read_text(encoding="utf-8").strip()
    if ATTRIBUTION.search(message):
        raise Failed("the commit message carries attribution")
    if git(repo, "status", "--porcelain").strip():
        raise Failed("%s has uncommitted changes" % args.repo)
    r = subprocess.run([sys.executable, str(patch)], capture_output=True, text=True)
    print((r.stdout + r.stderr).strip())
    if r.returncode != 0:
        raise Failed("the patch refused")
    # DELI COUNTER REBUILDS ITS LIBRARY: a patch carries no `build/`, and the repo tracks part of it, so the applied
    # specs are built here and the build travels in the commit (the old per-change apply scripts did the same)
    if args.repo == "deli_counter":
        b = subprocess.run([sys.executable, "build.py", "--all"], cwd=str(repo), capture_output=True, text=True)
        print("build.py --all: exit %d" % b.returncode)
        if b.returncode != 0:
            raise Failed("the build failed on the applied repo; nothing committed")
    # THE INDEX FIRST (2026-10-28): what factory_index writes inside the repo travels in this commit, or the repo's
    # newest code commit outruns its VERSION and verify-manifest reads it STALE
    subprocess.run([sys.executable, str(FACTORY / "tools" / "factory_index.py"), "--write"], capture_output=True,
                   text=True, cwd=str(FACTORY))
    if args.suite:
        s = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=str(repo),
                           capture_output=True, text=True, env=dict(os.environ, DC_ZOO_ROOT=str(FACTORY / "zoo")))
        print("suite exit %d: %s" % (s.returncode, (s.stdout.strip().splitlines() or [""])[-1]))
        if s.returncode != 0:
            raise Failed("the suite failed on the applied repo; nothing committed")
    git(repo, "add", "-A")
    print(git(repo, "status", "--short").rstrip())
    c = subprocess.run(["git", "-C", str(repo), "commit", "-q", "-F", "-"], input=message, capture_output=True,
                       text=True)
    if c.returncode != 0:
        raise Failed("commit failed (the repo's hook?): %s" % (c.stderr or c.stdout).strip()[-600:])
    if ATTRIBUTION.search(git(repo, "log", "-1", "--format=%B")):
        raise Failed("the commit carries attribution: amend it before pushing")
    git(repo, "push", "-q")
    print("committed and pushed %s: %s" % (args.repo, git(repo, "log", "-1", "--format=%h %s").strip()[:100]))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("clone"); p.add_argument("repo"); p.add_argument("name")
    p = sub.add_parser("smoke"); p.add_argument("batch"); p.add_argument("--ws", required=True); p.add_argument("--lf")
    p = sub.add_parser("patch"); p.add_argument("repo"); p.add_argument("clone"); p.add_argument("name")
    p.add_argument("--doc", required=True); p.add_argument("--whole-over", type=int, default=12)
    p = sub.add_parser("prove-old"); p.add_argument("repo"); p.add_argument("clone"); p.add_argument("name")
    p.add_argument("--tests", nargs="+", required=True); p.add_argument("--blender", action="store_true")
    p.add_argument("--blender-exe", default=r"C:\blender\blender.exe")
    p = sub.add_parser("apply"); p.add_argument("repo"); p.add_argument("name")
    p.add_argument("--message", required=True); p.add_argument("--suite", action="store_true")
    args = ap.parse_args(argv)
    try:
        return {"clone": cmd_clone, "smoke": cmd_smoke, "patch": cmd_patch, "prove-old": cmd_prove_old,
                "apply": cmd_apply}[args.cmd](args) or 0
    except Failed as e:
        print("FAILED: %s" % e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
