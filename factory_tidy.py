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

    tools/            probes, censuses, checks    (34 already live there)
    scripts/          .ps1 runbooks               (9 already live there)
    docs/sessions/    SESSION_*.md
    docs/findings/    investigation write-ups
    docs/diagrams/    exported svg/png
    patches/          patch_*.py / unpatch_*.py      <- the only new folder
    _runs/            measurement scratch and dead sidecars

`_runs/` is deliberate: it is ALREADY in .gitignore and ALREADY on
factory_clean.ps1's allow-list, so everything filed there starts getting
swept without touching either list.

TRACKED FILES MOVE WITH `git mv` so history follows them. The script asks git
which files are tracked instead of assuming.

IT REFUSES TO MOVE A PYTHON FILE THAT MENTIONS `__file__`. Every patch here
is documented "run from the FACTORY ROOT" and resolves targets from
Path.cwd(), so `python patches/patch_x.py` still works after the move. A
script that instead locates things relative to itself would break, so those
are reported and left alone.

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
from fnmatch import fnmatch
from pathlib import Path

#: Ordered. First match wins.
RULES: list[tuple[str, object]] = [
    ("patches", lambda n: fnmatch(n, "patch_*.py") or fnmatch(n, "unpatch_*.py")),
    ("tools", lambda n: (fnmatch(n, "probe_*.py") or fnmatch(n, "library_*.py")
                         or fnmatch(n, "*_census.py")
                         or n in {"module_extents.py", "compare_candidates.py",
                                  "roadmap_status.py", "factory_map.py",
                                  "verify_staging_identity.py",
                                  "test_mirror_agreement.py"})),
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
    ("_runs/measurements", lambda n: (fnmatch(n, "lt_*.json") or fnmatch(n, "lt_*.csv")
                                      or fnmatch(n, "gp_*.json")
                                      or fnmatch(n, "shots_*.json")
                                      or n in {"lux_applied.tscn", "probe_roof.glb",
                                               "themed_fit.txt",
                                               "walkbot.before.json"})),
    ("_runs/attic", lambda n: ".pre_" in n or n.endswith(".pending")),
]

#: Belongs at the root. Never filed away.
KEEP = {"README.md", "CLAUDE.md", "AGENT_CONTRACT.md", "CERTIFY.md",
        "CHANGELOG.md", "ENGINE_GATES.md", "NEXT.md", "PIPELINE_MAP.md",
        "PIPELINE_ROADMAP.md", "PACKAGE_README.md", "factory.manifest.json",
        ".gitignore", "factory_tidy.py"}


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


def uses_dunder_file(path: Path) -> bool:
    """A script that locates things relative to itself breaks when moved."""
    if path.suffix != ".py":
        return False
    try:
        return "__file__" in path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def plan(root: Path):
    tracked = tracked_files(root)
    moves, skipped, unknown = [], [], []
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
        moves.append((entry, dest, entry in tracked, p.stat().st_size))
    return moves, skipped, unknown


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if "--selftest" in argv:
        return selftest()
    if not (root / ".git").exists() or not (root / "level_factory").exists():
        print("run this from the factory root")
        return 1

    moves, skipped, unknown = plan(root)
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

    if unknown:
        print(f"\n  UNCLASSIFIED -- left alone ({len(unknown)}):")
        for n in unknown:
            print(f"      {n}")
    if skipped:
        print(f"\n  NOT MOVED -- mentions __file__, would break ({len(skipped)}):")
        for n in skipped:
            print(f"      {n}")

    if "--apply" not in argv:
        print("\ndry run. Nothing moved. Re-run with --apply.")
        return 0

    print()
    moved = 0
    for name, dest, is_tracked, _size in moves:
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
    print(f"\nmoved {moved} file(s). Tracked ones went via git mv, so history "
          f"follows.\nreview with: git status --short")
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
        "make_package.ps1": "scripts",
        "run_0809.ps1": "scripts",
        "SESSION_0812.md": "docs/sessions",
        "SESSION_0803b.md": "docs/sessions",
        "LADDER_INTO_SOLID_ROOF.md": "docs/findings",
        "NARRATIVE_SLATE.md": "docs/findings",
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
        "README.md": None, "CLAUDE.md": None, "PIPELINE_ROADMAP.md": None,
        "factory.manifest.json": None, "NEXT.md": None,
    }
    bad = 0
    for name, want in FIXTURE.items():
        got = classify(name)
        got = None if got is None else got
        ok = got == want
        bad += 0 if ok else 1
        if not ok:
            print(f"  FAIL {name:<38} -> {got!r}, wanted {want!r}")
    print(f"  {len(FIXTURE) - bad}/{len(FIXTURE)} classified correctly")

    # End to end on a real git repo, so `git mv` is exercised for real.
    tmp = Path(tempfile.mkdtemp())
    try:
        (tmp / "level_factory").mkdir()
        subprocess.run(["git", "init", "-q"], cwd=tmp, check=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=tmp, check=True)
        for name in FIXTURE:
            (tmp / name).write_text("x", encoding="utf-8")
        # one file that must be refused
        (tmp / "probe_selflocating.py").write_text(
            "from pathlib import Path\nHERE = Path(__file__).parent\n",
            encoding="utf-8")
        (tmp / "mystery_thing.xyz").write_text("x", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=tmp, check=True)
        subprocess.run(["git", "commit", "-qm", "seed"], cwd=tmp, check=True)

        here = Path.cwd()
        os.chdir(tmp)
        try:
            moves, skipped, unknown = plan(tmp)
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
            print("  FAIL a __file__-dependent script was not refused")
            bad += 1
        if "mystery_thing.xyz" not in unknown:
            print("  FAIL an unclassified file was not reported")
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
