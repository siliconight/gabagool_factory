#!/usr/bin/env python3
r"""File the factory root's loose SOURCE into the folders that already exist.

    python factory_tidy.py            # report only, moves nothing
    python factory_tidy.py --apply
    python factory_tidy.py --selftest # prove the rules on a throwaway repo

Companion to `scripts/factory_clean.ps1`. That one clears regenerable
ARTIFACTS; this one files loose SOURCE. Same doctrine, from docs/CLEANUP.md:

    allow-list, never guess.  Dry-run by default.  --apply to execute.

ANYTHING WITHOUT AN EXPLICIT RULE STAYS WHERE IT IS. Silence means "not
classified", never "safe to move". Unclassified files are listed loudly so
the list is a to-do, not a shrug.

DESTINATIONS ARE FOLDERS THE REPO ALREADY USES -- nothing invented:

    tools/            probes, censuses, checks, audits
    scripts/          .ps1 runbooks
    docs/             the prose that is not the front door
    docs/sessions/    SESSION_*.md
    docs/findings/    investigation write-ups
    docs/diagrams/    exported svg/png
    patches/          patch_*.py / unpatch_*.py
    _runs/            measurement scratch and dead sidecars

WHAT CHANGED IN THIS VERSION

1. The two files the last run left UNCLASSIFIED are classified.
   `draft_version_bumps.py` and `factory_root_audit.py` are both checks that
   read the whole factory and write nothing outside it -- the same shape as
   everything already in `tools/`. They were unclassified because they were
   written after the rules were, which is exactly the case the loud
   UNCLASSIFIED list exists to surface. It worked; this closes it.

2. A `docs/` rule, so the root gets down to the front door. `README.md`,
   `CLAUDE.md`, `CHANGELOG.md`, `factory.manifest.json` and `.gitignore`
   stay. The rest of the root prose -- `AGENT_CONTRACT.md`, `CERTIFY.md`,
   `ENGINE_GATES.md`, `NEXT.md`, `PIPELINE_MAP.md`, `PIPELINE_ROADMAP.md`,
   `PACKAGE_README.md` -- is proposed for `docs/`.

3. But a document a SCRIPT WRITES TO cannot just move, so it is not moved.
   `factory_map.py` regenerates `PIPELINE_MAP.md`; `roadmap_status.py`
   rewrites `PIPELINE_ROADMAP.md`; `patch_map_generated_block.py` splices
   into the former. Move the file and the writer silently recreates it at the
   root -- you would end up with two, and the stale one is the one people
   read. So `names_a_writer()` greps the repo's own .py and .ps1 for the
   literal filename and REFUSES anything that is mentioned, naming the script
   that mentions it. Same discipline as `uses_dunder_file()` below: judge on
   what the code does, never on what I remember it doing.

   It only reads CODE. A markdown link to a moved file is a broken link, not
   a duplicated file -- a different problem, and one `git grep` finds after.

TRACKED FILES MOVE WITH `git mv` so history follows them. The script asks git
which files are tracked instead of assuming.

IT REFUSES TO MOVE A SCRIPT PINNED TO ITS OWN DIRECTORY -- one taking the
root as `Path(__file__).parent` with no search. Every patch here is
documented "run from the FACTORY ROOT" and resolves targets from Path.cwd(),
so `python patches/patch_x.py` still works after the move.

The test is what the script DOES, not whether it says `__file__`. The first
version refused on the keyword and held back five files that were always
movable -- three already walk up through `parents`, and one mentions
`__file__` only inside code it emits into another file. A file carrying
`_factory_root()` has been converted by `patch_root_resolution.py` and is
fine anywhere.

WHY PYTHON AND NOT POWERSHELL. The first version of this was a .ps1 and it
was wrong: its match rules were scriptblocks invoked as `& $_.Match $f`,
where `$_` inside the block still referred to the rule rather than the
filename, so every file fell through to "unclassified" and it moved nothing.
It shipped that way because there was no PowerShell available to run it in.
This one has `--selftest`, which builds a throwaway git repo, files a replica
of the real root through the real rules, and checks where everything landed.
"""
from __future__ import annotations

import os
import subprocess
import sys
import re
from fnmatch import fnmatch
from pathlib import Path

#: Checks that read the whole factory and write nothing outside it. Same
#: shape as everything else in `tools/`.
_TOOL_NAMES = {
    "module_extents.py", "compare_candidates.py", "roadmap_status.py",
    "factory_map.py", "verify_staging_identity.py", "test_mirror_agreement.py",
    # added this round -- the two the previous run reported UNCLASSIFIED
    "draft_version_bumps.py", "factory_root_audit.py",
    "factory_tidy.py", "factory_folders.py",
}

#: Root prose that is not the front door. Anything here that a script writes
#: to is refused by `names_a_writer()` before it can move.
_DOC_NAMES = {
    "AGENT_CONTRACT.md", "CERTIFY.md", "ENGINE_GATES.md", "NEXT.md",
    "PIPELINE_MAP.md", "PIPELINE_ROADMAP.md", "PACKAGE_README.md",
}

#: Ordered. First match wins.
RULES: list[tuple[str, object]] = [
    ("patches", lambda n: fnmatch(n, "patch_*.py") or fnmatch(n, "unpatch_*.py")),
    ("tools", lambda n: (fnmatch(n, "probe_*.py") or fnmatch(n, "library_*.py")
                         or fnmatch(n, "*_census.py")
                         or n in _TOOL_NAMES)),
    ("scripts", lambda n: fnmatch(n, "*.ps1")),
    ("docs/sessions", lambda n: fnmatch(n, "SESSION_*.md")),
    ("docs/findings", lambda n: n in {"LADDER_INTO_SOLID_ROOF.md",
                                      "LASERTAG_STAGES_A_STALE_SCENE.md",
                                      "ITEM7_SOURCE_LIBRARY.md",
                                      "ROADMAP_0809_ADDENDUM.md",
                                      "GUARDRAILS_PLAN.md",
                                      "NARRATIVE_SLATE.md"}),
    ("docs/diagrams", lambda n: (fnmatch(n, "*.svg") or fnmatch(n, "dag_*.png")
                                 or fnmatch(n, "factory_for_*.png")
                                 or fnmatch(n, "levelfactory_*.png"))),
    ("docs", lambda n: n in _DOC_NAMES),
    ("_runs/measurements", lambda n: (fnmatch(n, "lt_*.json") or fnmatch(n, "lt_*.csv")
                                      or fnmatch(n, "gp_*.json")
                                      or fnmatch(n, "shots_*.json")
                                      or n in {"lux_applied.tscn", "probe_roof.glb",
                                               "themed_fit.txt",
                                               "walkbot.before.json"})),
    ("_runs/attic", lambda n: ".pre_" in n or n.endswith(".pending")),
]

#: Belongs at the root. Never filed away. `factory.manifest.json` is the
#: marker every script walks up to find, so it can never move; the other four
#: are what a stranger opens first.
KEEP = {"README.md", "CLAUDE.md", "CHANGELOG.md",
        "factory.manifest.json", ".gitignore"}


def classify(name: str):
    if name in KEEP:
        return None
    for dest, match in RULES:
        if match(name):
            return dest
    return "?"


def tracked_files(root: Path) -> set[str]:
    try:
        out = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True,
                             text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return set()
    return {line.strip() for line in out.splitlines() if line.strip()}


# --------------------------------------------- refuse to orphan a writer ----

#: Where the factory's own code lives. Tool repos are excluded on purpose --
#: they are separate repos and do not reach up into this one.
_CODE_DIRS = (".", "tools", "patches", "scripts")
_CODE_SUFFIX = (".py", ".ps1")


def code_blob(root: Path, exclude: set[str] = frozenset()) -> list[tuple[str, str]]:
    """Every line of the factory's own scripts, with the file it came from."""
    out: list[tuple[str, str]] = []
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
            rel = p.name if sub == "." else f"{sub}/{p.name}"
            out.append((rel, text))
    return out


#: Tokens that turn a quoted filename into a PATH rather than a topic.
_PATHISH = ("/", "\\", "Join-Path", "open(", "write_text", "write_bytes",
            "read_text", "read_bytes", "Set-Content", "Out-File", "Get-Content")


def names_a_writer(name: str, blob: list[tuple[str, str]]) -> str | None:
    """The first script that OPENS this file by path, or None.

    A document a script regenerates cannot move on its own: the writer keeps
    writing to the old path, and you end up with two copies where the stale
    one is the one at the root that people read. `PIPELINE_MAP.md` is the live
    case -- `factory_map.py` line 85 is `DOC = ROOT / "PIPELINE_MAP.md"`.

    THE FIRST VERSION TESTED FOR A BARE MENTION AND OVER-REFUSED 7 TO 2. Run
    against the real root it blocked all seven candidate documents, and five
    of those blocks were wrong:

        AGENT_CONTRACT.md   scripts/factory_tidy.ps1:81   a $Keep array
        CERTIFY.md          scripts/factory_tidy.ps1:81   in the dead .ps1
        NEXT.md             scripts/factory_tidy.ps1:82   predecessor of
        PACKAGE_README.md   scripts/factory_tidy.ps1:83   this very file
        ENGINE_GATES.md     patch_lf_export_closure.py    prose in a docstring

    A document being *discussed* by a script is not a document being written
    by one, and in a repo where every script argues for itself in a long
    docstring, prose mentions are the common case. So the name must appear
    QUOTED and on a line that also builds or opens a path. Both real writers
    here are `DOC = ROOT / "..."`, which passes; `$Keep = @("NEXT.md", ...)`
    and `` see `ENGINE_GATES.md` `` do not.

    THE LIMIT, STATED. A writer that builds its path across two lines is
    missed. That is a false negative -- the move happens and the writer
    recreates the file -- so if a document you moved reappears at the root,
    this is why. Both writers in the factory today are single-line.

    This is a REFUSAL, not a fix. The fix is to move the file and patch the
    writer in the same commit, which is a decision, not a rule.
    """
    quoted = (f'"{name}"', f"'{name}'")
    for rel, text in blob:
        for line in text.splitlines():
            if any(q in line for q in quoted) and any(t in line
                                                      for t in _PATHISH):
                return rel
    return None


#: The one pattern that actually pins a script to its directory: taking the
#: root as its OWN parent, with no search. Anything that walks up from
#: `__file__` is location-independent already.
_PINNED = re.compile(r"Path\(__file__\)(?:\.resolve\(\))?\.parent(?!s)")


def uses_dunder_file(path: Path) -> bool:
    """True only for scripts that anchor on their own directory.

    NOT "mentions __file__". That test was too blunt and refused five files
    that were always movable: `probe_reach.py` and `probe_sightlines.py` call
    `_lf_root()`, which walks `(start, *start.parents)`; `module_extents.py`
    searches `here.parents` and `Path.cwd()`; `test_mirror_agreement.py`
    walks `(here.parent, *here.parents)`; and `patch_lf_walkable_site.py`
    mentions `__file__` only inside code it EMITS into another file. Judging
    them on a keyword rather than on what they do cost five files a move.

    A file carrying `_factory_root()` has been converted by
    `patch_root_resolution.py` and is fine wherever it sits.
    """
    if path.suffix != ".py":
        return False
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    if "def _factory_root(" in src:
        return False
    if "_lf_root(" in src:          # already walks up
        return False
    # `(?!s)` matters: `.parents[2]` CONTAINS `.parent`, and a substring test
    # refused `patch_lf_walkable_site.py` whose only `__file__` sits inside
    # code it emits into a tool repo -- addressing that file's tree, not its
    # own. An indexed `parents[N]` is a different construct and the only one
    # here is emitted, so it is not matched. If a script ever anchors on
    # `parents[N]` for real, this will miss it; the cost of that mistake is
    # cheaper than the five files the blunt test held back.
    return bool(_PINNED.search(src))


def plan(root: Path):
    tracked = tracked_files(root)
    # A doc naming ITSELF in its own text is not a writer, and this script
    # lists every doc name in `_DOC_NAMES`, so exclude it from its own scan.
    blob = code_blob(root, exclude={"factory_tidy.py"})
    moves, skipped, unknown, pinned_docs = [], [], [], []
    for entry in sorted(os.listdir(root)):
        p = root / entry
        if not p.is_file():
            continue
        dest = classify(entry)
        if dest is None:
            continue
        if dest == "?":
            unknown.append(entry)
            continue
        if uses_dunder_file(p):
            skipped.append(entry)
            continue
        if p.suffix == ".md":
            writer = names_a_writer(entry, blob)
            if writer:
                pinned_docs.append((entry, writer))
                continue
        moves.append((entry, dest, entry in tracked, p.stat().st_size))
    return moves, skipped, unknown, pinned_docs


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if "--selftest" in argv:
        return selftest()
    if not (root / ".git").exists() or not (root / "level_factory").exists():
        print("run this from the factory root")
        return 1

    moves, skipped, unknown, pinned_docs = plan(root)
    total = sum(1 for e in os.listdir(root) if (root / e).is_file())
    print(f"\nloose files at the root: {total}\n")

    by_dest: dict[str, list] = {}
    for name, dest, _t, size in moves:
        by_dest.setdefault(dest, []).append((name, size))
    for dest in sorted(by_dest):
        rows = by_dest[dest]
        mb = sum(s for _n, s in rows) / (1024 * 1024)
        print(f"  {dest:<20} {len(rows):>3} file(s)  {mb:>6.1f} MB")
    print(f"  {'stays at the root':<20} {len(KEEP & set(os.listdir(root))):>3}")

    if pinned_docs:
        print(f"\n  NOT MOVED -- a script writes to it ({len(pinned_docs)}):")
        for n, writer in pinned_docs:
            print(f"      {n:<24} named by {writer}")
        print("      Move one of these only together with a patch to its "
              "writer,\n      or the writer recreates it at the root and the "
              "stale copy wins.")
    if unknown:
        print(f"\n  UNCLASSIFIED -- left alone ({len(unknown)}):")
        for n in unknown:
            print(f"      {n}")
    if skipped:
        print(f"\n  NOT MOVED -- pinned to its own directory ({len(skipped)}):")
        for n in skipped:
            print(f"      {n}")

    if "--apply" not in argv:
        print("\ndry run. Nothing moved. Re-run with --apply.")
        return 0

    print()
    moved = 0
    self_moved = None
    # This file is in the plan. Move it LAST so the rest of the run is not
    # relying on a path that just changed.
    ordered = sorted(moves, key=lambda m: m[0] == "factory_tidy.py")
    for name, dest, is_tracked, _size in ordered:
        (root / dest).mkdir(parents=True, exist_ok=True)
        target = root / dest / name
        if target.exists():
            print(f"  SKIP {name} -- already at {dest}/")
            continue
        if is_tracked:
            r = subprocess.run(["git", "mv", "--", name, f"{dest}/{name}"],
                               cwd=root, capture_output=True, text=True)
            if r.returncode:
                print(f"  git mv FAILED {name}: {r.stderr.strip()}")
                continue
        else:
            (root / name).rename(target)
        moved += 1
        if name == "factory_tidy.py":
            self_moved = f"{dest}/{name}"
    print(f"\nmoved {moved} file(s). Tracked ones went via git mv, so history "
          f"follows.\nreview with: git status --short")
    if self_moved:
        print(f"\nthis script moved itself to {self_moved} -- it resolves the "
              f"root from\nPath.cwd(), so from now on run it as: python "
              f"{self_moved}")
    return 0


# ------------------------------------------------------------- selftest ----

def selftest() -> int:
    """Build a throwaway repo, run the real rules, check where things land."""
    import shutil
    import tempfile

    # A replica of the real root, including the awkward cases.
    FIXTURE = {
        "patch_lf_grade_what_ships.py": "patches",
        "patch_dc_office_elevator.py": "patches",
        "unpatch_lf_themed_selection.py": "patches",
        "probe_stair_islands.py": "tools",
        "library_census.py": "tools",
        "marker_scope_census.py": "tools",
        "module_extents.py": "tools",
        "compare_candidates.py": "tools",
        "test_mirror_agreement.py": "tools",
        "draft_version_bumps.py": "tools",
        "factory_root_audit.py": "tools",
        "factory_folders.py": "tools",
        "make_package.ps1": "scripts",
        "run_0809.ps1": "scripts",
        "SESSION_0812.md": "docs/sessions",
        "SESSION_0803b.md": "docs/sessions",
        "LADDER_INTO_SOLID_ROOF.md": "docs/findings",
        "NARRATIVE_SLATE.md": "docs/findings",
        "AGENT_CONTRACT.md": "docs",
        "CERTIFY.md": "docs",
        "ENGINE_GATES.md": "docs",
        "NEXT.md": "docs",
        "PACKAGE_README.md": "docs",
        "dag_dark.png": "docs/diagrams",
        "factory_for_engineers.svg": "docs/diagrams",
        "levelfactory_for_directors.png": "docs/diagrams",
        "lt_after.json": "_runs/measurements",
        "lt_5118.csv": "_runs/measurements",
        "gp_5118.json": "_runs/measurements",
        "shots_spine.json": "_runs/measurements",
        "lux_applied.tscn": "_runs/measurements",
        "probe_roof.glb": "_runs/measurements",
        "walkbot.before.json": "_runs/measurements",
        "CLAUDE.md.pre_verification": "_runs/attic",
        "check_all.py.pre_root": "_runs/attic",
        "PIPELINE_ROADMAP.md.pre_status": "_runs/attic",
        "test_themed_selection.py.pending": "_runs/attic",
        # must never move
        "README.md": None, "CLAUDE.md": None, "CHANGELOG.md": None,
        "factory.manifest.json": None,
    }
    bad = 0
    for name, want in FIXTURE.items():
        got = classify(name)
        ok = got == want
        bad += 0 if ok else 1
        if not ok:
            print(f"  FAIL {name:<38} -> {got!r}, wanted {want!r}")
    print(f"  {len(FIXTURE) - bad}/{len(FIXTURE)} classified correctly")

    # End to end on a real git repo, so `git mv` is exercised for real.
    tmp = Path(tempfile.mkdtemp())
    try:
        (tmp / "level_factory").mkdir()
        (tmp / "tools").mkdir()
        subprocess.run(["git", "init", "-q"], cwd=tmp, check=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=tmp, check=True)
        for name in FIXTURE:
            (tmp / name).write_text("x", encoding="utf-8")
        # one file that must be refused for pinning itself to its directory
        (tmp / "probe_selflocating.py").write_text(
            "from pathlib import Path\nHERE = Path(__file__).parent\n",
            encoding="utf-8")
        # a doc that a script writes to: must be refused, and the script that
        # names it must be the one reported.
        (tmp / "PIPELINE_MAP.md").write_text("x", encoding="utf-8")
        (tmp / "tools" / "factory_map.py").write_text(
            'OUT = ROOT / "PIPELINE_MAP.md"\n', encoding="utf-8")
        # The two shapes that fooled the first version of the guard and cost
        # five documents a move. Neither opens anything; both must be ignored.
        (tmp / "scripts").mkdir(exist_ok=True)
        (tmp / "scripts" / "dead_predecessor.ps1").write_text(
            '$Keep = @("README.md", "AGENT_CONTRACT.md", "CERTIFY.md",\n'
            '          "NEXT.md", "PACKAGE_README.md")\n', encoding="utf-8")
        (tmp / "patches" / "patch_prose.py").parent.mkdir(exist_ok=True)
        (tmp / "patches" / "patch_prose.py").write_text(
            'r"""The gate is spelled out in `ENGINE_GATES.md`, which says\n'
            'ENGINE_GATES.md is the authority here.\n"""\n', encoding="utf-8")
        (tmp / "mystery_thing.xyz").write_text("x", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=tmp, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=tmp, check=True)

        here = Path.cwd()
        os.chdir(tmp)
        try:
            moves, skipped, unknown, pinned_docs = plan(tmp)
            for name, dest, is_tracked, _s in moves:
                (tmp / dest).mkdir(parents=True, exist_ok=True)
                if is_tracked:
                    subprocess.run(["git", "mv", "--", name, f"{dest}/{name}"],
                                   cwd=tmp, check=True, capture_output=True)
                else:
                    (tmp / name).rename(tmp / dest / name)
        finally:
            os.chdir(here)

        for name, want in FIXTURE.items():
            landed = (tmp / want / name) if want else (tmp / name)
            if not landed.exists():
                print(f"  FAIL {name} is not at {landed.relative_to(tmp)}")
                bad += 1
        if "probe_selflocating.py" not in skipped:
            print("  FAIL a directory-pinned script was not refused")
            bad += 1
        if "mystery_thing.xyz" not in unknown:
            print("  FAIL an unclassified file was not reported")
            bad += 1
        names = dict(pinned_docs)
        if "PIPELINE_MAP.md" not in names:
            print("  FAIL a doc a script writes to was not refused")
            bad += 1
        elif names["PIPELINE_MAP.md"] != "tools/factory_map.py":
            print(f"  FAIL wrong writer reported: {names['PIPELINE_MAP.md']}")
            bad += 1
        else:
            print("  ok   PIPELINE_MAP.md refused, blamed on "
                  "tools/factory_map.py")
        overblocked = [n for n in ("AGENT_CONTRACT.md", "CERTIFY.md", "NEXT.md",
                                   "PACKAGE_README.md", "ENGINE_GATES.md")
                       if n in names]
        if overblocked:
            print(f"  FAIL a prose mention still blocks: {overblocked}")
            bad += 1
        else:
            print("  ok   a $Keep array and a docstring do not count as "
                  "writers")
        if (tmp / "PIPELINE_MAP.md").exists() is False:
            print("  FAIL PIPELINE_MAP.md moved anyway")
            bad += 1
        st = subprocess.run(["git", "status", "--porcelain"], cwd=tmp,
                            capture_output=True, text=True).stdout
        renames = sum(1 for line in st.splitlines() if line.startswith("R"))
        print(f"  git recorded {renames} rename(s) -- history follows")
        if renames < 20:
            print("  FAIL git did not record these as renames")
            bad += 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    print("  selftest passed" if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
