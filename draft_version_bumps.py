#!/usr/bin/env python3
r"""Draft the bumps the STALE tools need, from their own commit history.

    python draft_version_bumps.py                 # report what changed, per tool
    python draft_version_bumps.py --apply         # bump VERSION + draft CHANGELOG
    python draft_version_bumps.py --apply --tool zoo --tool pixelcoat
    python draft_version_bumps.py --revert
    python draft_version_bumps.py --selftest

Run from the FACTORY ROOT (the directory holding `factory.manifest.json`).

WHY THIS IS A SCRIPT AND NOT ME WRITING TEN CHANGELOG ENTRIES. On 2026-08-14
`verify-manifest` reported five tools STALE -- `dispatch`, `patina`,
`pipeline`, `pixelcoat`, `zoo` -- meaning each has commits newer than the
VERSION file that names it. I did not make those changes and cannot describe
them honestly. Their own history can, so the draft is assembled from the
commits themselves: subjects, dates and the files each touched.

WHAT IT WRITES IS A DRAFT, AND IT SAYS SO IN THE FILE. Every entry it
prepends is marked `<!-- DRAFT`. A CHANGELOG in this repo carries the
argument for a change -- what was measured, what broke, why the fix is the
fix. A list of commit subjects is not that. It is the raw material, put where
the prose goes, so the entry gets written from what happened rather than from
memory.

BUMP LEVEL IS PROPOSED, NOT DECIDED. Commits touching only documentation get
a PATCH; anything touching code, data or tests gets a MINOR. Both are
overridable with `--patch` / `--minor`, because a script cannot tell a
behaviour change from a rename by reading a path. Nothing is ever a major
here: a major means an adapter is likely broken, and that is a claim for a
person to make.

NOTHING IS COMMITTED, NOTHING IS TAGGED. Each tool is its own git repo and
its commits belong to it. This writes files; you review them, then commit and
tag inside each tool.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

MANIFEST = "factory.manifest.json"
SIDECAR = ".pre_draftbump"

#: Not code. Mirrors `contracts.stale_source` so the two instruments agree
#: about what a change to a tool IS -- two definitions here would be two
#: answers to one question.
SKIP = ["VERSION", "CHANGELOG.md", ".gitignore", ".gitattributes",
        ".editorconfig", "LICENSE", "LICENSE.md"]

#: A commit touching only these is documentation.
DOC_SUFFIX = (".md", ".rst", ".txt")


def git(root: Path, args: list[str]) -> str | None:
    try:
        r = subprocess.run(["git", "-C", str(root)] + args,
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.rstrip("\n") if r.returncode == 0 else None


def commits_since_version(root: Path) -> list[dict] | None:
    """Every commit newer than the last one touching VERSION."""
    if not (root / ".git").exists():
        return None
    # RANGE FROM THE COMMIT, NOT THE TIMESTAMP. `--since=@<ct>` is inclusive,
    # so the VERSION commit came back as its own successor -- and a commit
    # that touches VERSION *and* code in one go is the normal shape of a
    # release commit, which made every freshly-bumped tool look stale again.
    head = git(root, ["log", "-1", "--format=%H", "--", "VERSION"])
    if not head:
        return None
    spec = ["."] + [f":(exclude){s}" for s in SKIP]
    raw = git(root, ["log", f"{head}..HEAD", "--format=%H%x1f%ct%x1f%s",
                     "--"] + spec)
    if raw is None:
        return None
    out = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        sha, ct, subject = line.split("\x1f", 2)
        files = [f for f in (git(root, ["show", "--name-only", "--format=",
                                        sha]) or "").split() if f not in SKIP]
        if not files:
            continue                      # touched only skipped files
        out.append({"sha": sha[:9], "when": int(ct), "subject": subject,
                    "files": files})
    return out


def proposed_level(commits: list[dict]) -> str:
    every_file = [f for c in commits for f in c["files"]]
    if every_file and all(f.lower().endswith(DOC_SUFFIX) for f in every_file):
        return "patch"
    return "minor"


def bump(version: str, level: str) -> str:
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", version)
    if not m:
        return version
    major, minor, patch = (int(x) for x in m.groups())
    if level == "minor":
        minor, patch = minor + 1, 0
    else:
        patch += 1
    return version[:m.start()] + f"{major}.{minor}.{patch}" + version[m.end():]


def entry(tool: str, new_v: str, commits: list[dict], level: str) -> str:
    import datetime as _dt
    files: list[str] = []
    for c in commits:
        for f in c["files"]:
            if f not in files:
                files.append(f)
    when = _dt.datetime.fromtimestamp(
        max(c["when"] for c in commits), _dt.timezone.utc).strftime("%Y-%m-%d")
    lines = [
        f"## [{new_v.split()[-1]}] - DRAFT, needs a real summary",
        "",
        "<!-- DRAFT. Assembled from this repo's own commits so the entry is",
        "     written from what happened, not from memory. Replace this block",
        f"     with the argument for the change: what was measured, what it",
        f"     broke, why this fix is the fix. Proposed {level} bump because",
        "     " + ("only documentation changed." if level == "patch"
                   else "code, data or tests changed."),
        "",
        f"     {len(commits)} commit(s) since VERSION was last written, "
        f"latest {when}:",
    ]
    for c in commits:
        lines.append(f"       {c['sha']}  {c['subject']}")
    lines.append("")
    lines.append(f"     {len(files)} file(s) touched:")
    for f in files[:25]:
        lines.append(f"       {f}")
    if len(files) > 25:
        lines.append(f"       ... and {len(files) - 25} more")
    lines += ["-->", ""]
    return "\n".join(lines) + "\n"


def tools_from_manifest(root: Path) -> dict:
    data = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    return {name: root / str(e.get("path", name))
            for name, e in data.get("tools", {}).items()}


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()

    root = Path.cwd()
    if not (root / MANIFEST).is_file():
        raise SystemExit(f"no {MANIFEST} here -- run from the factory root")

    wanted = [argv[i + 1] for i, a in enumerate(argv) if a == "--tool"]
    force = ("patch" if "--patch" in argv
             else "minor" if "--minor" in argv else None)
    apply_ = "--apply" in argv
    revert = "--revert" in argv

    plans = []
    for name, tool in sorted(tools_from_manifest(root).items()):
        if wanted and name not in wanted:
            continue
        vf = tool / "VERSION"
        if not vf.is_file():
            continue
        if revert:
            for f in (vf, tool / "CHANGELOG.md"):
                side = f.with_suffix(f.suffix + SIDECAR)
                if side.is_file():
                    f.write_bytes(side.read_bytes())
                    print(f"  reverted     {f.relative_to(root)}")
            continue
        commits = commits_since_version(tool)
        if commits is None:
            print(f"  {name:<14} no git history to read -- skipped")
            continue
        if not commits:
            print(f"  {name:<14} VERSION is current")
            continue
        cur = vf.read_text(encoding="utf-8").strip()
        level = force or proposed_level(commits)
        plans.append((name, tool, cur, bump(cur, level), commits, level))

    if revert:
        return 0

    for name, _t, cur, new, commits, level in plans:
        files = {f for c in commits for f in c["files"]}
        print(f"\n  {name}  {cur}  ->  {new}   ({level}, "
              f"{len(commits)} commit(s), {len(files)} file(s))")
        for c in commits[:6]:
            print(f"      {c['sha']}  {c['subject'][:68]}")
        if len(commits) > 6:
            print(f"      ... and {len(commits) - 6} more")

    if not plans:
        print("\n  nothing to bump")
        return 0
    if not apply_:
        print("\n  report only. Re-run with --apply to write VERSION and a "
              "CHANGELOG draft.")
        return 0

    for name, tool, cur, new, commits, level in plans:
        vf, cl = tool / "VERSION", tool / "CHANGELOG.md"
        for f in (vf, cl):
            side = f.with_suffix(f.suffix + SIDECAR)
            if f.is_file() and not side.is_file():
                side.write_bytes(f.read_bytes())
        raw = vf.read_bytes()
        eol = "\r\n" if raw.count(b"\r\n") else "\n"
        vf.write_bytes((new + eol).encode("utf-8"))
        body = cl.read_text(encoding="utf-8") if cl.is_file() else ""
        text = entry(name, new, commits, level)
        if eol == "\r\n":
            text = text.replace("\n", "\r\n")
        cl.write_text(text + body, encoding="utf-8", newline="")
        print(f"  drafted      {name}  {cur} -> {new}")

    print("\n  Every entry is marked <!-- DRAFT. Write the real summary, then "
          "commit and\n  tag INSIDE each tool repo. Nothing here is committed.")
    return 0


def selftest() -> int:
    import shutil
    import tempfile
    import time

    bad = 0

    def check(label, got, want):
        nonlocal bad
        ok = got == want
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}: {got!r}")

    check("minor bump", bump("0.32.0", "minor"), "0.33.0")
    check("patch bump", bump("0.3.0", "patch"), "0.3.1")
    check("prefixed version keeps its prefix",
          bump("Deli Counter 0.88.0", "minor"), "Deli Counter 0.89.0")
    check("docs-only -> patch",
          proposed_level([{"files": ["README.md", "docs/x.md"]}]), "patch")
    check("any code -> minor",
          proposed_level([{"files": ["README.md", "pkg/a.py"]}]), "minor")

    tmp = Path(tempfile.mkdtemp())
    try:
        tool = tmp / "widget"
        (tool / "pkg").mkdir(parents=True)

        def g(*a):
            subprocess.run(["git", "-C", str(tool)] + list(a), check=True,
                           capture_output=True)

        (tool / "VERSION").write_text("0.1.0\n", encoding="utf-8")
        (tool / "pkg" / "core.py").write_text("x\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(tool)], check=True,
                       capture_output=True)
        g("config", "user.email", "t@t")
        g("config", "user.name", "t")
        g("add", "-A")
        g("commit", "-qm", "seed")
        check("clean repo has no commits since VERSION",
              commits_since_version(tool), [])

        time.sleep(1.1)
        (tool / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
        g("add", "-A")
        g("commit", "-qm", "gitignore only")
        check("a skipped-file commit does not count",
              commits_since_version(tool), [])

        time.sleep(1.1)
        (tool / "pkg" / "core.py").write_text("y\n", encoding="utf-8")
        g("add", "-A")
        g("commit", "-qm", "fix the thing")
        got = commits_since_version(tool)
        check("one real commit", [c["subject"] for c in got], ["fix the thing"])
        check("and it names the file", got[0]["files"], ["pkg/core.py"])
        check("proposed level", proposed_level(got), "minor")
        text = entry("widget", "0.2.0", got, "minor")
        check("draft is marked", "<!-- DRAFT" in text, True)
        check("draft carries the subject", "fix the thing" in text, True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    print("  drafts come from history" if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
