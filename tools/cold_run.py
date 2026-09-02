r"""Roadmap 17: count the interventions a cold run needs, without trusting memory.

    python cold_run.py --begin  <label>        snapshot the tools, open a journal
    python cold_run.py --note   "what you did" record one intervention
    python cold_run.py --retry  "what failed"  record a re-run of the SAME command
    python cold_run.py --observe "what you saw" record something you only LOOKED at
    python cold_run.py --end                   snapshot again, diff, print the count
    python cold_run.py --selftest              prove the detector on a fake tree

WHAT THIS IS FOR
----------------
Item 17 is the only item in `PIPELINE_ROADMAP.md` that measures the thing the
toolchain exists to answer: *hand the tools a spec they have never seen, run one
command, and does a walkable, gated package come out with nobody touching
anything on the way?* Its acceptance test is exact -- "record every intervention
it needed. A run needing zero is the first real evidence. A run needing four is
a list of four defects."

The number is the deliverable, so the number has to be trustworthy. A count kept
in someone's head at the end of a four-hour run is the same kind of artefact
this repo already distrusts everywhere else: `check_all.py` exists because four
defects survived a check going quiet, and CLAUDE.md's whole verification section
is about the gap between what was done and what is remembered about it.

So this does not ask you to remember. It hashes the tool SOURCE before and
after, and a file that changed during the run is an intervention whether or not
anybody wrote it down. The journal records intent; the hash records fact; the
report prints both and flags any disagreement.

WHAT COUNTS AS AN INTERVENTION, stated so the number means something
---------------------------------------------------------------------
COUNTED -- anything that changes what the pipeline would do next time:

  * any edit to a tool repo (deli_counter, lot, zoo, lux, patina, pixelcoat,
    level_factory, dispatch, lasertag, pipeline) -- detected by hash, whether
    or not it was noted
  * any edit to a spec, brief, theme or genome -- same detection, same reason:
    hand-editing the input until the output works is the failure mode item 17
    is named after
  * any hand-authored file placed into the workspace
  * a re-run with DIFFERENT arguments, or with a flag added that the original
    invocation did not carry

NOT COUNTED, and separated rather than hidden:

  * re-running the identical command after a transient (recorded with --retry
    and reported as its own figure, because a pipeline needing six retries is
    not a pipeline needing six patches, and conflating them flatters one and
    slanders the other)
  * reading logs, running gates, taking measurements -- observation is not
    intervention. `--observe` records one so it is not lost, and reports it
    apart from everything else. Roadmap 70: on `cold_7001` a journal
    CORRECTION had to be filed with `--note` for want of this, and inflated
    the count by one.
  * THE PIPELINE WRITING INTO A TOOL REPO. Level Factory writes one Deli
    Counter spec per candidate into `deli_counter/specs/`, and DC regenerates
    the index beside them. Six such files on `cold_7001` were hash-detected
    and reported as an intervention nobody made. They are ATTRIBUTED against
    `GENERATED` below and reported apart -- see the warning on that table,
    because a wrong entry there hides a real edit.
  * APPROVING A GATE. `brief_approved`, `candidate_selected` and
    `functional_shell_locked` are the product working as designed, not
    patches -- Level Factory's approval model exists so a human decides those
    three things. Counting them would report every successful run as needing
    three interventions and make the metric useless in the direction that
    flatters nobody. Choosing WHICH candidate is a decision; making a
    candidate work is an intervention.
  * anything after a gated package exists; the run is over at that point

WHAT THIS DOES NOT DO. It does not judge whether the level is good, or whether
the package is gated -- `check_all.py` and the walk own that. It reports how
many times a human had to reach into the machine, and stops.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from factory_paths import factory_root                        # noqa: E402


def _root() -> Path:
    """Resolved on USE, not on import.

    `ROOT = factory_root()` at module level made `--selftest` impossible to run
    anywhere but inside a factory -- the import blew up before argparse saw the
    flag. A selftest that cannot run is the defect this file is built to
    measure, so it does not get to have one.
    """
    return factory_root()

#: The repos a cold run must not need edited. `pipeline` is included even
#: though it rarely moves -- an intervention there would be as disqualifying as
#: one in lot, and leaving it out would make the number quietly optimistic.
TOOLS = ("deli_counter", "dispatch", "lasertag", "level_factory", "lot",
         "lux", "patina", "pipeline", "pixelcoat", "zoo")

#: Generated, so a change here is the pipeline working rather than a person
#: intervening. `build` and `_runs` are the big ones: a cold run WRITES there
#: by design, and counting that as an intervention would report every
#: successful run as a failure.
SKIP_PARTS = ("__pycache__", ".git", ".pytest_cache", ".godot", "_scratch",
              "_runs", "_archive", "dist", "node_modules", ".egg-info")
SKIP_DIRS = ("build", "_preview_dressing", "_preview_plastic", "_preview_street")

#: Paths the PIPELINE writes inside a tool repo during a normal run, with the
#: reason each one is there. Matched with `fnmatch` against the repo-relative
#: path. A file that matches is reported as attributed and does NOT count.
#:
#: READ THIS BEFORE ADDING A LINE. Every entry is a claim that a human never
#: writes there, and a wrong claim hides the exact thing this tool exists to
#: catch. That is why these are narrow patterns rather than directories: the
#: whole of `deli_counter/specs/` is NOT generated -- it holds specs that ship
#: with the repo, and hand-editing one of those until the output works is the
#: failure mode roadmap 17 is named after. Only `lf_*.json`, which Level
#: Factory writes fresh per candidate per run and overwrites next run, is.
#:
#: The report prints the reason beside every attributed file, so the claim is
#: audited on every read rather than trusted once.
GENERATED = (
    ("deli_counter/specs/lf_*.json",
     "Level Factory writes one DC spec per candidate, per run"),
    ("deli_counter/specs/CATALOG.md",
     "Deli Counter regenerates its spec index when a spec is added"),
)


def attribute(rel: str) -> str | None:
    """The reason `rel` is a pipeline write, or None if nobody has claimed it.

    None is the safe answer and the default: an unrecognised file counts.
    """
    for pattern, why in GENERATED:
        if fnmatch.fnmatch(rel, pattern):
            return why
    return None

#: Measurements live under `_runs/`, which is gitignored and is where
#: `factory_tidy.py` already files them.
OUT_REL = ("_runs", "cold")


def _skip(rel: Path) -> bool:
    parts = rel.parts
    if any(p in SKIP_PARTS for p in parts):
        return True
    if any(p.endswith(".egg-info") for p in parts):
        return True
    # `build` only counts as generated at a tool's top level -- `lot/build/` is
    # output, but a `build` directory nested inside source would be source.
    return len(parts) > 1 and parts[1] in SKIP_DIRS


def snapshot(root: Path | None = None) -> dict:
    """sha256 per source file across every tool repo, plus each VERSION."""
    root = root or _root()
    files, versions = {}, {}
    for tool in TOOLS:
        base = root / tool
        if not base.is_dir():
            versions[tool] = None
            continue
        v = base / "VERSION"
        versions[tool] = v.read_text(encoding="utf-8").strip() if v.is_file() else None
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(root)
            if _skip(rel):
                continue
            try:
                files[str(rel).replace("\\", "/")] = hashlib.sha256(
                    p.read_bytes()).hexdigest()
            except OSError:
                continue
    return {"files": files, "versions": versions}


def _diff(before: dict, after: dict) -> dict:
    b, a = before["files"], after["files"]
    changed = sorted(k for k in b.keys() & a.keys() if b[k] != a[k])
    added = sorted(a.keys() - b.keys())
    removed = sorted(b.keys() - a.keys())
    bumped = sorted(t for t in after["versions"]
                    if before["versions"].get(t) != after["versions"].get(t))
    return {"changed": changed, "added": added, "removed": removed,
            "version_bumps": bumped}


def _stamp() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _out() -> Path:
    return _root().joinpath(*OUT_REL)


def _paths(label: str):
    d = _out() / label
    return d, d / "before.json", d / "journal.md"


def _active() -> str | None:
    p = _out() / "ACTIVE"
    return p.read_text(encoding="utf-8").strip() if p.is_file() else None


def cmd_begin(label: str) -> int:
    d, before, journal = _paths(label)
    if before.exists():
        print(f"  {label} already begun ({before}) -- pick another label or --end it")
        return 2
    d.mkdir(parents=True, exist_ok=True)
    snap = snapshot()
    before.write_text(json.dumps(snap, indent=1, sort_keys=True), encoding="utf-8")
    journal.write_text(
        f"# cold run: {label}\n\nbegun {_stamp()}\n"
        f"{len(snap['files'])} source files hashed across {len(TOOLS)} tools\n\n"
        f"| when | kind | what |\n|---|---|---|\n", encoding="utf-8")
    _out().mkdir(parents=True, exist_ok=True)
    (_out() / "ACTIVE").write_text(label, encoding="utf-8")
    print(f"  begun: {label}")
    print(f"  {len(snap['files'])} source files hashed")
    for t, v in sorted(snap["versions"].items()):
        print(f"    {t:<16}{v}")
    print(f"  journal: {journal}")
    return 0


def _append(kind: str, text: str) -> int:
    label = _active()
    if not label:
        print("  no cold run is active -- --begin one first")
        return 2
    _, _b, journal = _paths(label)
    with journal.open("a", encoding="utf-8") as fh:
        fh.write(f"| {_stamp()} | {kind} | {text.replace('|', '/')} |\n")
    print(f"  recorded ({kind}): {text}")
    return 0


def cmd_end() -> int:
    label = _active()
    if not label:
        print("  no cold run is active")
        return 2
    d, before_p, journal = _paths(label)
    before = json.loads(before_p.read_text(encoding="utf-8"))
    after = snapshot()
    diff = _diff(before, after)
    (d / "after.json").write_text(json.dumps(after, indent=1, sort_keys=True),
                                  encoding="utf-8")
    (d / "diff.json").write_text(json.dumps(diff, indent=1), encoding="utf-8")

    rows = [l for l in journal.read_text(encoding="utf-8").splitlines()
            if l.startswith("| 20")]
    noted = [r for r in rows if "| intervention |" in r]
    retries = [r for r in rows if "| retry |" in r]
    seen = [r for r in rows if "| observation |" in r]
    touched = diff["changed"] + diff["added"] + diff["removed"]

    # Attribution, not subtraction. Both lists are printed: a file that stops
    # counting has to say who is supposed to have written it.
    attributed = [(f, attribute(f)) for f in touched if attribute(f)]
    unattributed = [f for f in touched if not attribute(f)]
    diff["attributed"] = [{"path": f, "written_by": w} for f, w in attributed]
    diff["unattributed"] = unattributed
    (d / "diff.json").write_text(json.dumps(diff, indent=1), encoding="utf-8")

    print(f"\n  cold run: {label}")
    print(f"  {'-'*58}")
    print(f"  interventions NOTED in the journal      {len(noted)}")
    print(f"  tool source files CHANGED on disk       {len(touched)}")
    if attributed:
        print(f"    attributed to the pipeline, NOT counted   {len(attributed)}")
        for f, why in attributed[:20]:
            print(f"      {f}")
            print(f"          {why}")
        if len(attributed) > 20:
            print(f"      ... and {len(attributed)-20} more (see diff.json)")
    print(f"    UNATTRIBUTED, counted                     {len(unattributed)}")
    for f in unattributed[:20]:
        print(f"      {f}")
    if len(unattributed) > 20:
        print(f"      ... and {len(unattributed)-20} more (see diff.json)")
    if diff["version_bumps"]:
        print(f"  VERSION bumped                          "
              f"{', '.join(diff['version_bumps'])}")
    print(f"  retries (same command re-run)           {len(retries)}")
    print(f"  observations (looked, did not touch)    {len(seen)}")
    print()
    if unattributed and not noted:
        print("  DISAGREEMENT: files changed that nothing wrote down and nothing")
        print("  claims. The hashes are the fact. Read diff.json before quoting")
        print("  a number.")
    elif noted and not unattributed:
        print("  Interventions were noted but no unattributed source moved -- fine")
        print("  if they were workspace edits or changed invocations, which do not")
        print("  hash here.")
    if attributed and not unattributed and not noted:
        print("  Every changed file is one the pipeline is expected to write.")
        print("  That is a clean run, and GENERATED in this file is the claim it")
        print("  rests on -- the reasons above are printed so you can refuse it.")
    verdict = max(len(noted), len(unattributed))
    print(f"  INTERVENTIONS: {verdict}"
          f"   (journal {len(noted)}, unattributed files {len(unattributed)})")
    print(f"  A run needing zero is the first real evidence -- roadmap item 17.")
    (_out() / "ACTIVE").unlink(missing_ok=True)
    return 1 if verdict else 0


def selftest() -> int:
    """The detector must catch an edit nobody wrote down. That is its only job."""
    import tempfile, shutil
    fails = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "factory.manifest.json").write_text("{}", encoding="utf-8")
        for tool in ("lot", "zoo"):
            (root / tool).mkdir()
            (root / tool / "VERSION").write_text(f"{tool} 1.0.0", encoding="utf-8")
            (root / tool / "main.py").write_text("x = 1\n", encoding="utf-8")
            (root / tool / "build").mkdir()
            (root / tool / "build" / "out.glb").write_bytes(b"before")
            (root / tool / "__pycache__").mkdir()
            (root / tool / "__pycache__" / "c.pyc").write_bytes(b"before")
        a = snapshot(root)
        # the pipeline writing output is NOT an intervention
        (root / "lot" / "build" / "out.glb").write_bytes(b"after-a-real-run")
        (root / "zoo" / "__pycache__" / "c.pyc").write_bytes(b"recompiled")
        b = snapshot(root)
        if _diff(a, b)["changed"]:
            fails.append(f"build/pycache output counted as an edit: {_diff(a,b)}")
        # a source edit IS, noted or not
        (root / "lot" / "main.py").write_text("x = 2\n", encoding="utf-8")
        c = snapshot(root)
        d = _diff(a, c)
        if d["changed"] != ["lot/main.py"]:
            fails.append(f"source edit not caught: {d}")
        # a VERSION bump is reported separately
        (root / "zoo" / "VERSION").write_text("zoo 1.1.0", encoding="utf-8")
        e = _diff(a, snapshot(root))
        if e["version_bumps"] != ["zoo"]:
            fails.append(f"version bump not caught: {e}")
        # a new hand-authored spec is an addition
        (root / "lot" / "specs").mkdir()
        (root / "lot" / "specs" / "new.json").write_text("{}", encoding="utf-8")
        f = _diff(a, snapshot(root))
        if "lot/specs/new.json" not in f["added"]:
            fails.append(f"hand-authored file not caught: {f['added']}")

    # ---- attribution (roadmap 70) -----------------------------------------
    # The six files `cold_7001` actually reported, verbatim from its diff.json.
    COLD_7001 = ("deli_counter/specs/CATALOG.md",
                 "deli_counter/specs/lf_category5_baie_dore_001_7001.json",
                 "deli_counter/specs/lf_category5_baie_dore_001_7102.json",
                 "deli_counter/specs/lf_category5_baie_dore_001_7203.json",
                 "deli_counter/specs/lf_category5_baie_dore_001_7304.json",
                 "deli_counter/specs/lf_category5_baie_dore_001_7405.json")
    unclaimed = [f for f in COLD_7001 if not attribute(f)]
    if unclaimed:
        fails.append(f"cold_7001's own pipeline writes still count: {unclaimed}")

    # The claim must stay narrow. These are the files it must NEVER excuse.
    for rel in ("deli_counter/deli_counter.py",
                "deli_counter/build.py",
                "deli_counter/specs/night_deli.json",
                "deli_counter/specs/lf_notes.txt",
                "lot/specs/lf_something.json",
                "zoo/genome/species/wallEnd.json"):
        if attribute(rel):
            fails.append(f"GENERATED excuses a file it must not: {rel} "
                         f"({attribute(rel)})")

    # Every attributed path owes a reason; a silent excuse is not auditable.
    for pattern, why in GENERATED:
        if not why or len(why) < 20:
            fails.append(f"GENERATED entry has no usable reason: {pattern!r}")

    for line in fails:
        print("  " + line)
    if fails:
        print(f"  selftest FAILED: {len(fails)} case(s)")
        return 1
    print("  selftest ok: build output ignored, source edit / version bump / "
          "new file all caught;")
    print("  cold_7001's six pipeline writes attributed, and GENERATED refuses "
          "to excuse\n  a tool source file, a shipped spec, or another repo")
    return 0


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--begin", metavar="LABEL")
    ap.add_argument("--note", metavar="TEXT")
    ap.add_argument("--retry", metavar="TEXT")
    ap.add_argument("--observe", metavar="TEXT")
    ap.add_argument("--end", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.begin:
        return cmd_begin(a.begin)
    if a.note:
        return _append("intervention", a.note)
    if a.retry:
        return _append("retry", a.retry)
    if a.observe:
        return _append("observation", a.observe)
    if a.end:
        return cmd_end()
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
