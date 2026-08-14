#!/usr/bin/env python3
r"""Get the factory root down to folders you can name out loud.

    python factory_folders.py              # report only, moves nothing
    python factory_folders.py --apply
    python factory_folders.py --selftest

Run from the FACTORY ROOT (the directory holding `factory.manifest.json`).

`factory_tidy.py` files loose FILES. This does the other half: the eight
underscore-prefixed directories and the two loose workspaces. The target is
the shape you approved --

    gabagool_factory/
      deli_counter/ dispatch/ lasertag/ level_factory/ lot/
      lux/ patina/ pipeline/ pixelcoat/ zoo/     <- nine tools + the registrar
      docs/  patches/  tools/  scripts/  workspaces/  _scratch/
      README.md  CHANGELOG.md  CLAUDE.md  factory.manifest.json  .gitignore

-- and the only thing standing between here and there is that nobody has ever
said out loud what `_bridge_fresh` versus `_bridge` versus `_scratch2` are
for. They are all the same thing: somewhere to put output while looking at
it. One folder, `_scratch/`, with subfolders that keep their old names so
nothing you half-remember is lost.

IT ASKS GIT, IT DOES NOT READ .gitignore. Same reason as
`factory_root_audit.py`: fourteen rules across five sections, some
overlapping, and the answer to "is this ignored" is one `git check-ignore`
away. Guessing at precedence is how you move something git was tracking.

THREE THINGS MAKE IT REFUSE, and each refusal names what to do about it.

1. `_scratch/` IS NOT IGNORED YET. Consolidating eight ignored folders into
   one folder git wants to commit is worse than leaving them alone -- you
   would go from "messy but ignored" to "one `git add -A` from committing a
   19 MB zip". So the whole run refuses until `.gitignore` covers it, and
   prints the line to add. Order matters here, so it is enforced rather than
   mentioned.

2. A SCRIPT NAMES THE FOLDER. `_runs/` is the live case: it is already on
   `factory_clean.ps1`'s sweep allow-list and it is where `factory_tidy.py`
   files measurements and dead sidecars. Move the directory and both keep
   writing to the old path, which quietly recreates it. So the folder is
   refused and the script that names it is reported -- move it in the same
   commit as a patch to that script, or not at all. That is a decision, not
   a rule, so the script will not make it for you.

3. THE FOLDER IS TRACKED. `git mv`-ing tracked content under an ignored path
   leaves it tracked (gitignore does not un-track anything) but invisible to
   everyone reading the ignore file, which is the worst of both. Tracked
   content is content; it gets reported and left where it is.

Everything else is a plain rename, with `git mv` when git knows the folder
and a filesystem rename when it does not.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

MANIFEST = "factory.manifest.json"
SCRATCH = "_scratch"

#: Explicit, in the order they will be reported. Allow-list, never guess:
#: a root directory not named here is REPORTED, not moved.
MAP: list[tuple[str, str]] = [
    ("_bridge",           f"{SCRATCH}/bridge"),
    ("_bridge_fresh",     f"{SCRATCH}/bridge_fresh"),
    ("_runs",             f"{SCRATCH}/runs"),
    ("_scratch_archive",  f"{SCRATCH}/archive"),
    ("_scratch_walkable", f"{SCRATCH}/walkable"),
    ("_scratch2",         f"{SCRATCH}/scratch2"),
    ("_send",             f"{SCRATCH}/send"),
    ("lot-demo-ws",       "workspaces/lot-demo-ws"),
    ("rockay-ws",         "workspaces/rockay-ws"),
]

#: NOT scratch that moved. Python and pytest recreate these anywhere, in every
#: tool repo, the moment anything runs -- moving one just relocates the place
#: it reappears. They are deleted, not filed, and both checks already skip
#: them by name. Reported so the root's contents are still fully accounted
#: for; never moved.
REGENERATED = ("__pycache__", ".pytest_cache")

#: Folders that are the destination shape. Never touched, never reported.
KEEP_DIRS = {"docs", "patches", "tools", "scripts", "workspaces", SCRATCH,
             ".git", ".github", ".vscode"}

_CODE_DIRS = (".", "tools", "patches", "scripts")
_CODE_SUFFIX = (".py", ".ps1")


def git(root: Path, args: list[str]):
    try:
        return subprocess.run(["git", "-C", str(root)] + args,
                              capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None


def is_ignored(root: Path, name: str) -> bool:
    r = git(root, ["check-ignore", "-q", "--", name])
    return bool(r) and r.returncode == 0


def tracked_dirs(root: Path) -> set[str]:
    r = git(root, ["ls-files"])
    if not r or r.returncode != 0:
        return set()
    return {line.split("/", 1)[0] for line in r.stdout.splitlines()
            if "/" in line}


def code_blob(root: Path, exclude: set[str] = frozenset()):
    """Every line of the factory's own scripts, with the file it came from.

    Tool repos are excluded on purpose -- they are separate repos and do not
    reach up into this one.
    """
    out = []
    for sub in _CODE_DIRS:
        d = root / sub
        if not d.is_dir():
            continue
        for p in sorted(d.iterdir()):
            if not p.is_file() or p.suffix not in _CODE_SUFFIX:
                continue
            if p.name in exclude:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            out.append((p.name if sub == "." else f"{sub}/{p.name}", text))
    return out


#: A folder name counts only when something DELIMITS it -- a quote, or a path
#: separator on either side.
def _rx(folder: str):
    return re.compile(r'''["'/\\]''' + re.escape(folder) + r'''["'/\\]''')


#: Folders a script still names AFTER the mention was read and judged safe.
#: An entry here is a claim someone checked, so it carries the reason. This is
#: not a silencer: the folder is still reported, just not blocked.
REVIEWED: dict[str, str] = {
    "lot-demo-ws":
        "compare_candidates.py DEFAULT_WS was moved to workspaces/lot-demo-ws "
        "by patch_scratch_skips.py",
    "rockay-ws":
        "check_all.py SKIP_EVIDENCE is os.sep-wrapped, so it goes on matching "
        "workspaces/rockay-ws unchanged",
}


def names_it(folder: str, blob) -> str | None:
    """The first script that uses this folder as a PATH, or None.

    THE BARE-SUBSTRING VERSION REFUSED ELEVEN OF ELEVEN. Two separate bugs,
    both of which this fixes, and one correct result underneath them:

      - `_scratch2/` was blamed on `factory_root_audit.py`, where the only
        mention is a backticked sentence in the docstring arguing about this
        very folder. Prose, not a path.
      - `_bridge` matched inside `"_bridge_fresh"`, so a folder nothing
        references was blamed for its neighbour's name.

    Requiring a quote or a separator on BOTH sides fixes both: `"_bridge"` and
    `\\_runs\\` and `"lot-demo-ws"` match; `` `_scratch2/` `` and
    `"_bridge_fresh"` and `(lot-demo-ws,` do not.

    The other eight refusals were right, and were not prose at all -- they
    were skip lists. `check_all.py`'s SKIP_GENERATED and `never_wired.py`'s
    _SKIP_DIRS name these folders so their checks do not raise findings
    against staging copies. `patch_scratch_skips.py` collapses those entries
    into a single `_scratch` and updates `compare_candidates.py`'s workspace
    default; run it first and these stop being mentioned at all.
    """
    if folder in REVIEWED:
        return None
    rx = _rx(folder)
    for rel, text in blob:
        if rx.search(text):
            return rel
    return None


def du(path: Path) -> int:
    total = 0
    for p in path.rglob("*"):
        try:
            if p.is_file():
                total += p.stat().st_size
        except OSError:
            pass
    return total


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:,.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return str(n)


def plan(root: Path):
    blob = code_blob(root, exclude={"factory_folders.py"})
    tracked = tracked_dirs(root)
    known = {src for src, _ in MAP} | set(REGENERATED)

    moves, refused, unlisted = [], [], []
    junk = [d for d in REGENERATED if (root / d).is_dir()]
    for src, dest in MAP:
        p = root / src
        if not p.is_dir():
            continue
        if (p / ".git").exists():
            refused.append((src, dest, "it is its own git repo"))
            continue
        if (root / dest).exists():
            refused.append((src, dest, f"{dest} already exists"))
            continue
        writer = names_it(src, blob)
        if writer:
            refused.append((src, dest, f"{writer} names it -- patch that first"))
            continue
        if src in tracked and dest.startswith(SCRATCH + "/"):
            refused.append((src, dest, "git tracks it; that is content, not "
                                       "scratch"))
            continue
        moves.append((src, dest, src in tracked, is_ignored(root, src),
                      du(p)))

    for entry in sorted(os.listdir(root)):
        p = root / entry
        if not p.is_dir() or entry in KEEP_DIRS or entry in known:
            continue
        if (p / ".git").exists():
            continue                      # a tool repo, by design
        unlisted.append(entry)
    return moves, refused, unlisted, junk


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if "--selftest" in argv:
        return selftest()
    if not (root / MANIFEST).is_file():
        print(f"no {MANIFEST} here -- run from the factory root")
        return 1

    moves, refused, unlisted, junk = plan(root)

    scratch_ok = is_ignored(root, SCRATCH + "/x")
    wants_scratch = any(d.startswith(SCRATCH + "/") for _s, d, *_ in moves)

    print()
    if moves:
        print("  WOULD MOVE")
        for src, dest, is_tracked, ign, size in moves:
            flag = "tracked" if is_tracked else ("ignored" if ign else "LOOSE")
            print(f"    {src + '/':<20} -> {dest + '/':<26} "
                  f"{human(size):>9}  [{flag}]")
    if refused:
        print("\n  REFUSED")
        for src, dest, why in refused:
            print(f"    {src + '/':<20} -> {dest + '/':<26} {why}")
        if any("git tracks it" in why for _s, _d, why in refused):
            names = " ".join(s for s, _d, w in refused if "git tracks it" in w)
            print(f"\n    See what git is holding in those:\n"
                  f"      git ls-files -- {names}")
    if junk:
        print(f"\n  REGENERATED -- delete, do not move ({len(junk)}):")
        for d in junk:
            print(f"    {d + '/':<20} {human(du(root / d)):>9}  "
                  f"comes back the moment anything runs")
    if REVIEWED:
        print("\n  REVIEWED -- named by a script, checked, moving anyway:")
        for k, why in REVIEWED.items():
            if any(s == k for s, _d, *_ in moves):
                print(f"    {k + '/':<20} {why}")
    if unlisted:
        print(f"\n  NOT IN THE MAP -- left alone ({len(unlisted)}):")
        for n in unlisted:
            print(f"    {n}/")
        print("    Add a rule or leave it. Silence means unclassified, never "
              "safe.")

    if not moves and not refused:
        print("  the root is already folders you can name out loud")
        return 0

    if wants_scratch and not scratch_ok:
        print(f"\n  STOP. `{SCRATCH}/` is not ignored, and consolidating "
              f"ignored folders into\n  a tracked one is worse than leaving "
              f"them. Add this to .gitignore first:\n\n      {SCRATCH}/\n")
        return 1

    if "--apply" not in argv:
        print("\n  dry run. Nothing moved. Re-run with --apply.")
        return 0

    print()
    moved = 0
    for src, dest, is_tracked, _ign, _size in moves:
        (root / dest).parent.mkdir(parents=True, exist_ok=True)
        if is_tracked:
            r = git(root, ["mv", "--", src, dest])
            if not r or r.returncode:
                print(f"  git mv FAILED {src}: "
                      f"{(r.stderr.strip() if r else 'git unavailable')}")
                continue
        else:
            try:
                (root / src).rename(root / dest)
            except OSError as exc:
                print(f"  FAILED {src}: {exc}")
                continue
        moved += 1
        print(f"  moved  {src}/ -> {dest}/")
    print(f"\n  moved {moved} folder(s). Review with: git status --short")
    return 0


# ------------------------------------------------------------- selftest ----

def selftest() -> int:
    import shutil
    import tempfile

    bad = 0
    tmp = Path(tempfile.mkdtemp())
    try:
        root = tmp / "factory"
        (root / "tools").mkdir(parents=True)
        (root / MANIFEST).write_text("{}", encoding="utf-8")
        (root / ".gitignore").write_text(
            "_scratch/\n_bridge/\n_runs/\n_send/\n", encoding="utf-8")

        for d in ("_bridge", "_runs", "_send", "lot-demo-ws", "mystery_dir"):
            (root / d).mkdir()
            (root / d / "f.txt").write_text("x" * 10, encoding="utf-8")
        # a tool repo: must never be reported
        (root / "lux" / ".git").mkdir(parents=True)
        # a script that names _runs: that folder must be refused and blamed
        (root / "tools" / "factory_tidy.py").write_text(
            'DEST = "_runs/measurements"\n', encoding="utf-8")
        # The two shapes that made the bare-substring version refuse 11 of 11.
        (root / "_bridge_fresh").mkdir(exist_ok=True)
        (root / "_scratch2").mkdir(exist_ok=True)
        (root / "tools" / "decoys.py").write_text(
            'r"""Whether `_scratch2/` is covered is a question for git."""\n'
            'STAGE = "_bridge_fresh/out.glb"\n', encoding="utf-8")
        # tracked content that the map would push into _scratch
        (root / "_send" / "keep.txt").write_text("y", encoding="utf-8")

        subprocess.run(["git", "init", "-q", str(root)], check=True,
                       capture_output=True)
        for k, v in (("user.email", "t@t"), ("user.name", "t")):
            subprocess.run(["git", "-C", str(root), "config", k, v],
                           check=True, capture_output=True)
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True,
                       capture_output=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", "seed"],
                       check=True, capture_output=True)

        moves, refused, unlisted, junk = plan(root)
        mv = {s: d for s, d, *_ in moves}
        rf = {s: why for s, _d, why in refused}

        def check(label, ok):
            nonlocal bad
            bad += 0 if ok else 1
            print(f"  {'ok  ' if ok else 'FAIL'} {label}")

        check("_bridge/ is moved", mv.get("_bridge") == "_scratch/bridge")
        check("lot-demo-ws/ goes to workspaces/",
              mv.get("lot-demo-ws") == "workspaces/lot-demo-ws")
        check("a backticked docstring mention does not block _scratch2",
              "_scratch2" not in rf)
        check("_bridge is not blamed for _bridge_fresh's name",
              rf.get("_bridge", "") == "" or "decoys" not in rf["_bridge"])
        check("but a real quoted path still blocks _bridge_fresh",
              "tools/decoys.py" in rf.get("_bridge_fresh", ""))
        check("__pycache__ is never in the move plan",
              "__pycache__" not in mv and "__pycache__" not in rf)
        check("_runs/ is refused", "_runs" in rf)
        check("  and factory_tidy.py is blamed",
              "tools/factory_tidy.py" in rf.get("_runs", ""))
        check("a tool repo is never reported",
              "lux" not in mv and "lux" not in rf and "lux" not in unlisted)
        check("an unmapped folder is reported, not moved",
              unlisted == ["mystery_dir"])
        check("is_ignored agrees with git", is_ignored(root, "_bridge")
              and not is_ignored(root, "mystery_dir"))
        check("the _scratch/ gate sees the rule", is_ignored(root, "_scratch/x"))

        # And the gate must FIRE when the rule is absent.
        (root / ".gitignore").write_text("_bridge/\n", encoding="utf-8")
        check("the gate fires without the rule",
              not is_ignored(root, "_scratch/x"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    print("  selftest passed" if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
