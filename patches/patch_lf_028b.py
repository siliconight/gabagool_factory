r"""level_factory 0.28.0, corrected BEFORE it is committed.

    python patch_lf_028b.py --check
    python patch_lf_028b.py
    python patch_lf_028b.py --selftest
    python patch_lf_028b.py --revert

Run from the FACTORY ROOT, AFTER patch_lf_028.py and BEFORE the 0.28.0
commit. VERSION does not move -- 0.28.0 was never tagged.

WHY

0.28.0 was applied, its selftest passed 27 of 27, the unit suite passed, and
then the real export printed the marker/lock disagreement and NOT the
vacuous-lock warning the whole release exists to produce.

The guard was wired correctly and could not fire. `RegressionResult.
vacuous_lock` read `lock.coverage`, which is written by `compute_lock` -- so
only locks created by 0.28.0 or later carry one. Every lock on disk today
predates it. The warning would have stayed silent until every mission was
re-locked, which is to say silent on exactly the locks that need it.

Worse, 0.28.0's own selftest asserted that behaviour and called it a virtue:

    check("and is not reported as vacuous on no evidence",
          lk.verify_no_drift(old, ...).vacuous_lock is False)

"Absence is not a claim" is the right instinct and the wrong application. It
is right about a STORED report, which may be missing for any number of
reasons. It is wrong here because the evidence is not absent -- both gameplay
files are open in front of `verify_no_drift`, which already merges them to
compute the very signatures it is comparing. There was nothing to infer. It
just did not look.

WHAT CHANGES

`verify_no_drift` now computes coverage from the files it was handed, every
time, and reports it. Two consequences worth stating:

  * The warning fires on locks written before 0.28.0, which is all of them.
  * `RegressionResult.coverage` answers "what did THIS COMPARISON protect",
    while `lock.coverage` still answers "what did the lock protect when it
    was written". Two different questions; they are not merged, and the
    stored one is not consulted here. If they ever disagree, the site's shape
    changed between locking and checking, which is worth knowing and is not
    something this release tries to interpret.

`LOCK_COVERAGE_ENFORCED` is still False. Nothing about enforcement changes;
this only makes the measurement visible on the locks that exist.

THE PATTERN, SINCE IT IS THREE FOR THREE TODAY

0.27.0 shipped a manifest whose `tools` block was adapter versions, and the
selftest passed because it checked that the plumbing carried what it was
handed. patch_lf_027b shipped a NameError, and its selftest passed because it
read strings out of the file instead of calling the function. This one
shipped a guard that could not fire, and its selftest passed because it
asserted the behaviour of the bug. Each check was true. Each was about the
mechanism rather than the outcome. The only two things that caught any of
them were opening the artifact and running the command.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

LOCK = "level_factory/packages/approvals/lock.py"
COMMANDS = "level_factory/apps/cli/commands/__init__.py"
CHANGELOG = "level_factory/CHANGELOG.md"
P028 = "patches/patch_lf_028.py"
SIDECAR = ".pre_028b"

EDITS: list[tuple[str, str, str]] = [
    # ONE EDIT PER ANCHOR. The first draft of this patch added `coverage` and
    # `site_unguarded` as two separate edits sharing the anchor
    # `vacuous_lock: bool = False` -- each one's `new` string was destroyed by
    # the other, so the `if new in out` idempotency check would miss on a
    # re-run and apply both a second time. Same for the two as_dict edits and
    # the two return-statement edits. Merged.
    (LOCK,
     "    vacuous_lock: bool = False\n",
     "    vacuous_lock: bool = False\n"
     "    #: No protected key came from the SITE. Weaker than vacuous_lock and\n"
     "    #: far more common -- it is the state every lock here is in. A\n"
     "    #: signature kept alive entirely by Deli's backfill is not guarding\n"
     "    #: the assembled site, however non-empty its hash looks.\n"
     "    site_unguarded: bool = False\n"
     "    #: What THIS COMPARISON protected, measured from the files handed\n"
     "    #: in. Distinct from `lock.coverage`, which is what the lock\n"
     "    #: protected when it was WRITTEN. Not merged: if they disagree the\n"
     "    #: site's shape changed between locking and checking, and that is\n"
     "    #: worth seeing rather than reconciling away.\n"
     "    coverage: dict = field(default_factory=dict)\n"),

    (LOCK,
     '                "drift": self.drift, "vacuous_lock": self.vacuous_lock}\n',
     '                "drift": self.drift, "vacuous_lock": self.vacuous_lock,\n'
     '                "site_unguarded": self.site_unguarded,\n'
     '                "coverage": self.coverage}\n'),

    (LOCK,
     "    return RegressionResult(\n"
     "        mission_id=lock.mission_id, passed=not drift, drift=drift,\n"
     '        vacuous_lock=bool((lock.coverage or {}).get("vacuous")))\n',

     "    # MEASURED HERE, NOT READ OFF THE LOCK. The first version of this\n"
     "    # took `lock.coverage`, which only exists on locks written by 0.28.0\n"
     "    # or later -- so on every lock that exists today it was empty, and\n"
     "    # the warning this release was built to produce could not fire. The\n"
     "    # evidence was never absent: both files are open right here, and\n"
     "    # `gameplay` above is already the merge of them.\n"
     "    coverage = signature_coverage(\n"
     "        gameplay, _load(post_art_site_gameplay_path))\n"
     "    return RegressionResult(\n"
     "        mission_id=lock.mission_id, passed=not drift, drift=drift,\n"
     '        vacuous_lock=bool(coverage.get("vacuous")),\n'
     '        site_unguarded=bool(coverage.get("guards_no_site")),\n'
     "        coverage=coverage)\n"),

    # `vacuous` means ALL THREE signatures are empty. Against the real key
    # shape that is False -- Deli supplies two stair_systems, so
    # collision_fingerprint has content and the lock looks partly alive. The
    # condition that actually describes every lock here is narrower and
    # worse: the SITE contributed nothing. Found by running the report
    # against the real shape, after this patch had already been written to
    # fix the previous miss.
    (LOCK,
     '        "vacuous": len(unguarded) == len(PROTECTED_KEYS),\n    }\n',
     '        # NOT the same question as `vacuous`, and this is the one that\n'
     "        # is true here.\n"
     '        "guards_no_site": not any(_has_content(site_gameplay, k)\n'
     "                                  for k in read),\n"
     '        "vacuous": len(unguarded) == len(PROTECTED_KEYS),\n    }\n'),

    (LOCK,
     '    if not cov["site_contributes"]:\n',
     '    if cov["guards_no_site"]:\n'),

    (COMMANDS,
     "        if regression.vacuous_lock:\n"
     "            # THE MOMENT A HUMAN IS TOLD SOMETHING REASSURING AND FALSE.\n"
     "            # `passed` here means nothing was compared, not that nothing\n"
     "            # moved. Printed on the pass, because the failure path\n"
     "            # already speaks for itself.\n"
     '            print("[export] WARNING the functional lock for "\n'
     '                  f"{mission_id} protects nothing -- the post-art "\n'
     '                  "regression check passed because it compared no "\n'
     '                  "content. See its `coverage` block, or run "\n'
     '                  "tools/probe_selection_drift.py", file=sys.stderr)\n',

     "        if regression.vacuous_lock or regression.site_unguarded:\n"
     "            # THE MOMENT A HUMAN IS TOLD SOMETHING REASSURING AND FALSE.\n"
     "            # `passed` here means little was compared, not that nothing\n"
     "            # moved. Printed on the pass, because the failure path\n"
     "            # already speaks for itself.\n"
     "            #\n"
     "            # TWO CONDITIONS, because `vacuous` (all three signatures\n"
     "            # empty) is not what is true here: Deli's stair_systems keep\n"
     "            # one signature non-empty, so a lock guarding no site data\n"
     "            # at all still reads as partly alive.\n"
     '            what = ("protects nothing at all"\n'
     "                    if regression.vacuous_lock else\n"
     '                    "protects no site data -- every signature it checks "\n'
     '                    "is filled from the Deli side")\n'
     '            print(f"[export] WARNING the functional lock for "\n'
     '                  f"{mission_id} {what}. The post-art regression check "\n'
     '                  f"passed on that basis, which is weaker than it "\n'
     '                  f"reads. Run tools/probe_selection_drift.py, or read "\n'
     '                  f"the coverage block in the report.",\n'
     "                  file=sys.stderr)\n"),

    # 0.28.0's selftest asserted the bug. Neither file is committed, so this
    # is one edit rather than a rewrite of history.
    (P028,
     '        check("an old lock loads rather than failing", old.coverage == {})\n'
     '        check("and is not reported as vacuous on no evidence",\n'
     "              lk.verify_no_drift(old, empty_site,\n"
     "                                 empty_deli).vacuous_lock is False)\n",

     '        check("an old lock loads rather than failing", old.coverage == {})\n'
     '        check("and is still MEASURED, because the files are right there",\n'
     "              lk.verify_no_drift(old, empty_site,\n"
     "                                 empty_deli).vacuous_lock is True)\n"
     '        check("the report says what THIS comparison protected",\n'
     "              lk.verify_no_drift(old, empty_site, empty_deli)\n"
     '              .coverage["vacuous"] is True)\n'),

    (CHANGELOG,
     "- **Old locks load unchanged.**",

     "- **The warning has two conditions, because `vacuous` was not the one\n"
     "  that is true here.** `vacuous` means all three signatures are empty;\n"
     "  Deli's two `stair_systems` keep `collision_fingerprint` non-empty, so\n"
     "  a lock guarding no site data at all still reads as partly alive. The\n"
     "  condition that describes every lock in this factory is\n"
     "  `guards_no_site`: no protected key came from the site. Found by\n"
     "  running the report against the real key shape, after this correction\n"
     "  had already been written to fix the previous miss.\n"
     "- **Coverage is measured by `verify_no_drift` from the files it is\n"
     "  handed, not read off the lock.** The first cut of this release read\n"
     "  `lock.coverage`, which only exists on locks written by 0.28.0 or\n"
     "  later -- so on every lock that exists today it was empty, and the\n"
     "  warning this release was built to produce could not fire. It was\n"
     "  caught by running the export, not by the selftest, which had asserted\n"
     "  the broken behaviour as though it were a virtue: \"absence is not a\n"
     "  claim\" is right about a stored report and wrong here, because the\n"
     "  evidence was never absent. Both gameplay files are open in\n"
     "  `verify_no_drift`, which already merges them to compute the\n"
     "  signatures it compares.\n"
     "- **`RegressionResult.coverage` and `lock.coverage` answer different\n"
     "  questions** -- what this comparison protected, versus what the lock\n"
     "  protected when it was written -- and are deliberately not merged. If\n"
     "  they disagree, the site's shape changed between locking and checking.\n"
     "- **Old locks load unchanged.**"),
]

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
    v = (root / "level_factory" / "VERSION").read_text(encoding="utf-8")
    if "0.28.0" not in v:
        print(f"REFUSING: level_factory/VERSION says {v.strip()!r}, not "
              f"0.28.0 -- run patch_lf_028.py first")
        return 1

    by_file: dict[str, list[tuple[str, str]]] = {}
    for rel, old, new in EDITS:
        by_file.setdefault(rel, []).append((old, new))

    for rel, edits in by_file.items():
        p = root / rel
        if not p.is_file():
            print(f"REFUSING: {rel} is not here")
            return 1
        raw = p.read_bytes()
        body = raw.decode("utf-8")
        if body.count(_CRLF):
            print(f"REFUSING: {rel} has CRLF line endings; these anchors are LF")
            return 1
        out, done = body, 0
        for old, new in edits:
            if new in out:
                done += 1
                continue
            if out.count(old) != 1:
                print(f"REFUSING: {rel} -- an anchor occurs {out.count(old)} "
                      f"time(s), expected 1:\n    "
                      f"{old.strip().splitlines()[0][:72]}")
                return 1
            out = out.replace(old, new, 1)
        if done == len(edits):
            print(f"  already applied  {rel}")
            continue
        if rel.endswith(".py"):
            try:
                compile(out, str(p), "exec")
            except SyntaxError as exc:
                print(f"REFUSING: {rel} -- does not parse after the edit: {exc}")
                return 1
        data = out.encode("utf-8")
        if data == raw:
            print(f"  already applied  {rel}")
            continue
        if check:
            print(f"  would patch  {rel}  {len(raw):,} -> {len(data):,} bytes "
                  f"({len(data) - len(raw):+,})")
            continue
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(raw)
        p.write_bytes(data)
        print(f"  patched      {rel}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def selftest(root: Path) -> int:
    import importlib
    import json
    import tempfile
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    lf = str((root / "level_factory").resolve())
    if lf not in sys.path:
        sys.path.insert(0, lf)
    lk = importlib.import_module("packages.approvals.lock")
    importlib.reload(lk)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        def w(name, data):
            p = tmp / name
            p.write_text(json.dumps(data), encoding="utf-8")
            return p

        # The shape on disk: Lot's vocabulary, Deli with nothing either.
        site = w("site.json", {"buildings": [1], "collision": [1],
                               "openings": [1], "vertical_links": [1]})
        deli = w("deli.json", {})

        fresh = lk.compute_lock(mission_id="m1",
                                candidate_id="m1.candidate.seed_1", seed=1,
                                site_gameplay_path=site,
                                deli_gameplay_path=deli)

        # THE CASE THAT MATTERS: a lock with no stored coverage, which is
        # every lock that exists today.
        old = lk.FunctionalLock.from_dict(
            {k: v for k, v in fresh.as_dict().items() if k != "coverage"})
        check("a pre-0.28.0 lock still has no stored coverage",
              old.coverage == {})

        r = lk.verify_no_drift(old, site, deli)
        check("and verify_no_drift measures it anyway",
              r.vacuous_lock is True)
        check("the report says what THIS comparison protected",
              r.coverage.get("vacuous") is True
              and set(r.coverage["site_publishes_unread"]) ==
              {"buildings", "collision", "openings", "vertical_links"})
        check("without calling it drift", r.drift == [] and r.passed)
        check("and it reaches anyone reading the json",
              r.as_dict()["vacuous_lock"] is True
              and r.as_dict()["coverage"]["vacuous"] is True)

        # THE REAL SHAPE, and the case `vacuous` alone misses: Deli's
        # stair_systems keep one signature non-empty while the site
        # contributes nothing.
        lot_site = w("lot.json", {"buildings": [1], "collision": [1],
                                  "openings": [1], "vertical_links": [1],
                                  "markers": [1], "rooms": [1], "zones": [1]})
        lot_deli = w("lot_deli.json", {
            "stair_systems": [{"id": "s1"}, {"id": "s2"}],
            "ladders": [], "platforms": [], "fire_escapes": []})
        real = lk.verify_no_drift(
            lk.FunctionalLock.from_dict({"mission_id": "lot_demo_001",
                                         "candidate_id": "c", "seed": 5219}),
            lot_site, lot_deli)
        check("the real shape is NOT vacuous -- Deli keeps one alive",
              real.vacuous_lock is False)
        check("but the site guards nothing, and that is the flag that fires",
              real.site_unguarded is True)
        check("which is what cmd_export branches on",
              (real.vacuous_lock or real.site_unguarded) is True)
        check("and the report names the site keys nothing reads",
              "collision" in real.coverage["site_publishes_unread"]
              and "vertical_links" in real.coverage["site_publishes_unread"])

        # A lock that DOES protect something is not flagged.
        real_site = w("real.json", {"collision_hulls": [{"id": "h"}],
                                    "doorways": [{"id": "d"}],
                                    "route": {"n": 1}})
        real_deli = w("real_deli.json", {"anchors": [{"id": "a"}],
                                         "stair_systems": [{"id": "s"}]})
        good = lk.compute_lock(mission_id="m2",
                               candidate_id="m2.candidate.seed_1", seed=1,
                               site_gameplay_path=real_site,
                               deli_gameplay_path=real_deli)
        rg = lk.verify_no_drift(good, real_site, real_deli)
        check("a lock with real content is not flagged",
              rg.vacuous_lock is False and rg.passed)
        check("and its coverage names what the site supplied",
              set(rg.coverage["site_contributes"]) ==
              {"collision_hulls", "doorways", "route"})

        # The two coverages answer different questions and are not merged.
        crossed = lk.verify_no_drift(good, site, deli)
        check("lock.coverage and result.coverage are not the same field",
              good.coverage.get("vacuous") is False
              and crossed.coverage.get("vacuous") is True)

    cmds = (root / COMMANDS).read_text(encoding="utf-8")
    check("cmd_export warns on either condition",
          "if regression.vacuous_lock or regression.site_unguarded:" in cmds)
    check("and says which of the two it is",
          "protects nothing at all" in cmds
          and "protects no site data" in cmds)

    src = (root / LOCK).read_text(encoding="utf-8")
    check("verify_no_drift no longer reads coverage off the lock",
          '(lock.coverage or {}).get("vacuous")' not in src)
    check("and computes it from the files it was handed",
          "coverage = signature_coverage(\n"
          "        gameplay, _load(post_art_site_gameplay_path))" in src)

    p028 = (root / P028).read_text(encoding="utf-8")
    check("patch_lf_028's selftest no longer asserts the bug",
          "not reported as vacuous on no evidence" not in p028
          and "because the files are right there" in p028)

    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    check("0.28.0 is still one entry and was not renumbered",
          cl.count("## [0.28.0]") == 1 and "## [0.28.1]" not in cl)
    check("the entry records that the guard could not fire",
          "could not fire" in cl and "caught by running the export" in cl)
    check("and that the selftest had asserted the broken behaviour",
          "asserted\n  the broken behaviour" in cl)

    print()
    print("  the guard now fires on the locks that exist, not the ones to come"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")

    if "--selftest" in argv:
        return selftest(root)

    if "--revert" in argv:
        bad = 0
        for rel in (LOCK, COMMANDS, CHANGELOG, P028):
            p = root / rel
            side = p.with_suffix(p.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {rel}")
                bad = 1
                continue
            p.write_bytes(side.read_bytes())
            print(f"  reverted     {rel}")
        return bad

    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_lf_028b.py --selftest")
        print("    python patches\\patch_lf_028.py --selftest")
        print("    python -m pytest level_factory/tests/unit -q")
        print()
        print("  THEN THE EXPORT MUST WARN. It did not last time, which is")
        print("  why this patch exists:")
        print("    python -m level_factory -C workspaces\\lot-demo-ws \\")
        print("        export lot_demo_001 --mode portable-godot")
        print()
        print("  expect: [export] WARNING the functional lock for lot_demo_001")
        print("          protects nothing")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
