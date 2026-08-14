r"""level_factory 0.31.0 -- the gate turns on. Applied BEFORE the commit.

    python patch_lf_031b.py --check
    python patch_lf_031b.py
    python patch_lf_031b.py --selftest
    python patch_lf_031b.py --revert

Run from the FACTORY ROOT, AFTER patch_lf_031.py and BEFORE the 0.31.0
commit. VERSION does not move -- 0.31.0 was never tagged.

THE MISSION THAT EARNED IT

`lot_demo_001`, recomputed 2026-08-14 under schema v0.2:

    counts       markers 55, openings 76, surfaces 1029,
                 vertical_links 4, ground 5, stair_systems 2
    site_counts  markers 42, openings 76, surfaces 1029,
                 vertical_links 4, ground 5, stair_systems 0

`markers` 55 against 42 is the union: exactly the thirteen Deli anchors that
0.30.0 stopped dropping. `stair_systems` 2 against 0 is the Deli backfill,
which is all the lock protected before 0.29.0 -- the entire signature set,
for months, was those two records. It now carries 1,171.

`vacuous` False, `guards_no_site` False, `unguarded` empty.

WHAT ENFORCEMENT REFUSES, AND WHAT IT STILL ONLY WARNS ABOUT

`LOCK_COVERAGE_ENFORCED` refuses a VACUOUS lock -- every signature empty. It
does NOT refuse `guards_no_site`, which is the stricter and more meaningful
predicate, and that restraint is deliberate: exactly one mission has been
measured under this spec. Refusing on the stricter test would fail missions
nobody has looked at, on day one, which is the mistake `CLOSURE_ENFORCED`'s
comment describes and this factory has now avoided twice by copying it.

Widen it to `guards_no_site` when a second and third mission have been
measured. Name them in the comment, as this one names `lot_demo_001`.

AND THE ORDERING BUG THIS WOULD OTHERWISE HAVE SHIPPED

`cmd_approve` records the approval and THEN calls `_store_functional_lock`.
With enforcement on, a refused lock would raise out of a gate that had
already been recorded as approved -- an approved `functional_shell_locked`
with no lock behind it, reported by a traceback.

That is the same defect 0.28.0 fixed for `--candidate`, in the same function,
which I fixed there and did not look for here. The lock is now attempted
before anything is recorded, and a refusal returns EXIT_BLOCKED with the
coverage report rather than a stack trace.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

LOCK = "level_factory/packages/approvals/lock.py"
COMMANDS = "level_factory/apps/cli/commands/__init__.py"
CHANGELOG = "level_factory/CHANGELOG.md"
SIDECAR = ".pre_031b"

EDITS: list[tuple[str, str, str]] = [
    (LOCK,
     "LOCK_COVERAGE_ENFORCED = False\n",

     "#: FLIPPED 2026-08-14. The mission that earned it is `lot_demo_001`,\n"
     "#: recomputed under schema v0.2 after 0.30.0:\n"
     "#:\n"
     "#:     counts       markers 55, openings 76, surfaces 1029,\n"
     "#:                  vertical_links 4, ground 5, stair_systems 2\n"
     "#:     site_counts  markers 42, openings 76, surfaces 1029,\n"
     "#:                  vertical_links 4, ground 5, stair_systems 0\n"
     "#:\n"
     "#: markers 55 against 42 is the union -- the thirteen Deli anchors\n"
     "#: 0.30.0 stopped dropping. stair_systems 2 against 0 is the Deli\n"
     "#: backfill, and it is ALL this lock protected before 0.29.0: two\n"
     "#: records, for months. It now carries 1,171. vacuous False,\n"
     "#: guards_no_site False, unguarded empty.\n"
     "#:\n"
     "#: THIS REFUSES A VACUOUS LOCK ONLY -- every signature empty. It does\n"
     "#: NOT refuse `guards_no_site`, which is stricter and more meaningful,\n"
     "#: because exactly ONE mission has been measured under this spec.\n"
     "#: Refusing on the stricter test would fail missions nobody has looked\n"
     "#: at. Widen it when a second and third have been measured, and name\n"
     "#: them here the way this names lot_demo_001.\n"
     "LOCK_COVERAGE_ENFORCED = True\n"),

    # THE COVERAGE REPORT MUST READ WHAT THE SIGNATURE READS, and for the
    # anchor registry it did not. `_anchor_registry` falls back to Deli's
    # `anchors` when the site publishes no `markers` -- 0.29.0 wrote that
    # fallback and left `anchors` out of PROTECTED_KEYS, so a Deli-shaped
    # input read as UNGUARDED while the registry was happily hashing it.
    # Harmless while enforcement was off. The moment it went on, the unit
    # suite's own fixture became a vacuous lock and raised.
    #
    # 0.28.0's selftest asserts this invariant for _collision_signature and
    # there was never an equivalent for the registry. There is now.
    (LOCK,
     '    "anchor_registry_hash": ("markers",),\n',
     '    "anchor_registry_hash": ("markers", "anchors"),\n'),

    (LOCK,
     "BACKFILLED_FROM_DELI = frozenset(\n"
     '    {"stair_systems", "ladders", "platforms", "fire_escapes"})\n',
     "BACKFILLED_FROM_DELI = frozenset(\n"
     '    {"stair_systems", "ladders", "platforms", "fire_escapes",\n'
     '     # `_merged_gameplay` has always backfilled this, and\n'
     '     # `_anchor_registry` still falls back to it. 0.29.0 removed it from\n'
     '     # this set while leaving both behaviours in place.\n'
     '     "anchors"})\n'),

    (COMMANDS,
     "    if args.gate == gates.CANDIDATE_SELECTED and args.candidate:\n"
     "        rc = _refuse_bad_candidate(ws, args.mission_id, args.candidate)\n"
     "        if rc != EXIT_OK:\n"
     "            return rc\n",

     "    if args.gate == gates.CANDIDATE_SELECTED and args.candidate:\n"
     "        rc = _refuse_bad_candidate(ws, args.mission_id, args.candidate)\n"
     "        if rc != EXIT_OK:\n"
     "            return rc\n"
     "    # SAME REASON, SAME FUNCTION, AND I MISSED IT THE FIRST TIME.\n"
     "    # 0.28.0 moved the candidate check above store.record so a refusal\n"
     "    # could not leave an approved gate behind it. With\n"
     "    # LOCK_COVERAGE_ENFORCED on, a refused LOCK would do exactly that:\n"
     "    # an approved functional_shell_locked with no lock behind it,\n"
     "    # reported by a traceback out of _store_functional_lock.\n"
     "    if args.gate == gates.FUNCTIONAL_SHELL_LOCKED:\n"
     "        rc = _refuse_vacuous_lock(ws, args.mission_id)\n"
     "        if rc != EXIT_OK:\n"
     "            return rc\n"),

    (COMMANDS,
     "def _store_functional_lock(ws: Workspace, mission_id: str) -> None:\n",

     "def _refuse_vacuous_lock(ws: Workspace, mission_id: str) -> int:\n"
     '    """Compute the lock and throw it away, to see whether it is refused.\n'
     "\n"
     "    A dry run, so the decision happens BEFORE the approval is recorded.\n"
     "    The cost is computing the signatures twice; the alternative is\n"
     "    splitting `_store_functional_lock` in half for the sake of one\n"
     "    branch, and hashing a few thousand records twice is cheaper than a\n"
     "    seam nobody maintains.\n"
     "\n"
     "    stderr is swallowed here because the real write below prints the\n"
     "    same coverage report, and a warning printed twice reads like two\n"
     "    problems.\n"
     '    """\n'
     "    import contextlib\n"
     "    import io\n"
     "    from packages.approvals.lock import VacuousLockError\n"
     "    try:\n"
     "        with contextlib.redirect_stderr(io.StringIO()):\n"
     "            _store_functional_lock(ws, mission_id, write=False)\n"
     "    except VacuousLockError as exc:\n"
     '        print(f"functional_shell_locked REFUSED for {mission_id}: the "\n'
     '              f"lock this would write protects nothing.",\n'
     "              file=sys.stderr)\n"
     "        print(str(exc), file=sys.stderr)\n"
     '        print("  nothing was recorded and no lock was written.",\n'
     "              file=sys.stderr)\n"
     "        return EXIT_BLOCKED\n"
     "    return EXIT_OK\n"
     "\n"
     "\n"
     "def _store_functional_lock(ws: Workspace, mission_id: str,\n"
     "                           write: bool = True) -> None:\n"),

    (COMMANDS,
     "    p = _lock_path(ws, mission_id)\n"
     "    p.parent.mkdir(parents=True, exist_ok=True)\n"
     "    p.write_text(pretty_dumps(lock.as_dict()), encoding=\"utf-8\")\n",

     "    if not write:\n"
     "        return\n"
     "    p = _lock_path(ws, mission_id)\n"
     "    p.parent.mkdir(parents=True, exist_ok=True)\n"
     "    p.write_text(pretty_dumps(lock.as_dict()), encoding=\"utf-8\")\n"),

    (CHANGELOG,
     "## [0.31.0] - the coverage report counts\n",

     "## [0.31.0] - the coverage report counts, and the gate turns on\n"
     "\n"
     "`LOCK_COVERAGE_ENFORCED` is True. The mission that earned it is\n"
     "`lot_demo_001`, recomputed under schema v0.2:\n"
     "\n"
     "    counts       markers 55, openings 76, surfaces 1029,\n"
     "                 vertical_links 4, ground 5, stair_systems 2\n"
     "    site_counts  markers 42, openings 76, surfaces 1029,\n"
     "                 vertical_links 4, ground 5, stair_systems 0\n"
     "\n"
     "`markers` 55 against 42 is the union -- exactly the thirteen Deli\n"
     "anchors 0.30.0 stopped dropping. `stair_systems` 2 against 0 is the\n"
     "Deli backfill, and it is everything this lock protected before 0.29.0:\n"
     "two records, for months, under three signatures that all reported\n"
     "healthy. The protected set now carries 1,171.\n"
     "\n"
     "IT REFUSES A VACUOUS LOCK, NOT AN UNGUARDED SITE\n"
     "\n"
     "Enforcement rejects a lock whose every signature is empty. It does NOT\n"
     "reject `guards_no_site`, which is stricter and more meaningful, because\n"
     "exactly one mission has been measured under this spec and refusing on\n"
     "the stricter test would fail missions nobody has looked at. That is the\n"
     "argument `CLOSURE_ENFORCED`'s comment makes, and it is the second time\n"
     "this factory has avoided a day-one over-enforcement by copying it.\n"
     "Widen it when a second and third mission have been measured, naming\n"
     "them where this names lot_demo_001.\n"
     "\n"
     "THE GATE IMMEDIATELY FAILED THE UNIT SUITE, AND IT WAS RIGHT TO\n"
     "\n"
     "`test_anchor_drift_is_detected` uses a Deli-shaped fixture -- `anchors`,\n"
     "no `markers` -- and turning enforcement on made it raise. Not a bad\n"
     "test: `_anchor_registry` falls back to Deli's `anchors` when the site\n"
     "publishes no `markers`, and 0.29.0 wrote that fallback while leaving\n"
     "`anchors` out of `PROTECTED_KEYS`. So coverage reported the registry\n"
     "UNGUARDED while it was hashing that very list, and the same omission\n"
     "had dropped `anchors` from `BACKFILLED_FROM_DELI` even though\n"
     "`_merged_gameplay` still backfills it.\n"
     "\n"
     "Harmless while the flag was off. The moment it went on, a misreading\n"
     "became a refusal. 0.28.0's selftest asserts exactly this invariant for\n"
     "`_collision_signature` -- that coverage reads what the signature reads\n"
     "-- and there was never an equivalent for the registry. There is now.\n"
     "\n"
     "AND AN ORDERING BUG I HAD ALREADY FIXED ONCE, IN THE SAME FUNCTION\n"
     "\n"
     "`cmd_approve` recorded the approval and then called\n"
     "`_store_functional_lock`. With enforcement on, a refused lock raises\n"
     "out of a gate already recorded as approved -- an approved\n"
     "`functional_shell_locked` with no lock behind it, delivered as a\n"
     "traceback. 0.28.0 fixed precisely this for `--candidate`, four lines\n"
     "higher, and I did not look for it here. The lock is now attempted\n"
     "before anything is recorded, and a refusal returns EXIT_BLOCKED with\n"
     "the coverage report.\n"
     "\n"
     "WHY COUNTS, ORIGINALLY\n"),
]

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
    v = (root / "level_factory" / "VERSION").read_text(encoding="utf-8")
    if "0.31.0" not in v:
        print(f"REFUSING: level_factory/VERSION says {v.strip()!r}, not "
              f"0.31.0 -- run patch_lf_031.py first")
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

    check("THE GATE IS ON", lk.LOCK_COVERAGE_ENFORCED is True)

    # THE INVARIANT, for the signature that did not have one.
    reg_keys = set(lk.PROTECTED_KEYS["anchor_registry_hash"])
    check("coverage reads every key the anchor registry reads",
          reg_keys == {"markers", "anchors"}
          and lk._anchor_registry({"anchors": [{"id": "a"}]})
          and lk._anchor_registry({"markers": [{"id": "m"}]}))
    check("and the same invariant still holds for collision",
          set(lk.PROTECTED_KEYS["collision_fingerprint"])
          >= set(lk._collision_signature({})) - {"collision_nodes",
                                                 "ground_sources"})

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        def w(name, data):
            p = tmp / name
            p.write_text(json.dumps(data), encoding="utf-8")
            return p

        # A real site: not vacuous, so enforcement must not touch it.
        site = w("site.json", {
            "markers": [{"id": "F", "name": "b0/F", "type": "spawn"}],
            "surfaces": [{"node": "b0/c0"}],
            "ground": {"b0": {"source": "a.glb"}}})
        deli = w("deli.json", {"stair_systems": [{"id": "s1"}],
                               "markers": [{"id": "CREW_A", "type": "crew"}]})
        lock = lk.compute_lock(mission_id="m1",
                               candidate_id="m1.candidate.seed_1", seed=1,
                               site_gameplay_path=site,
                               deli_gameplay_path=deli)
        check("a lock that protects something is still written",
              lock.coverage["vacuous"] is False)
        check("and the union still shows as a subtraction",
              lock.coverage["counts"]["markers"]
              - lock.coverage["site_counts"]["markers"] == 1)

        # Nothing anywhere: refused, where it used to be written and warned.
        empty_site = w("empty.json", {"buildings": [1]})
        empty_deli = w("empty_deli.json", {})
        try:
            lk.compute_lock(mission_id="m2",
                            candidate_id="m2.candidate.seed_1", seed=1,
                            site_gameplay_path=empty_site,
                            deli_gameplay_path=empty_deli)
            check("A LOCK PROTECTING NOTHING IS NOW REFUSED", False)
        except lk.VacuousLockError as exc:
            check("A LOCK PROTECTING NOTHING IS NOW REFUSED", True)
            check("and the refusal carries the coverage report",
                  "PROTECTS NOTHING" in str(exc))

        # guards_no_site alone must NOT refuse -- only vacuous does.
        deli_only = w("deli_only.json", {"stair_systems": [{"id": "s1"}]})
        try:
            g = lk.compute_lock(mission_id="m3",
                                candidate_id="m3.candidate.seed_1", seed=1,
                                site_gameplay_path=empty_site,
                                deli_gameplay_path=deli_only)
            check("a site-unguarded lock still WRITES, it does not refuse",
                  g.coverage["guards_no_site"] is True
                  and g.coverage["vacuous"] is False)
        except lk.VacuousLockError:
            check("a site-unguarded lock still WRITES, it does not refuse",
                  False)

        # THE UNIT SUITE'S OWN FIXTURE: Deli-shaped, no markers. It read as
        # vacuous until `anchors` joined PROTECTED_KEYS, and enforcement
        # turned that misreading into a raised exception.
        deli_shaped_site = w("ds_site.json", {})
        deli_shaped = w("ds_deli.json", {
            "anchors": [{"id": "v", "type": "breach"}]})
        d = lk.compute_lock(mission_id="m4",
                            candidate_id="m4.candidate.seed_1", seed=1,
                            site_gameplay_path=deli_shaped_site,
                            deli_gameplay_path=deli_shaped)
        check("A DELI-SHAPED FIXTURE IS NOT VACUOUS",
              d.coverage["vacuous"] is False)
        check("and its registry is reported as guarding",
              d.coverage["signatures"]["anchor_registry_hash"]["guarding"]
              is True)

    cmds = (root / COMMANDS).read_text(encoding="utf-8")
    check("the lock is attempted before the approval is recorded",
          cmds.index("_refuse_vacuous_lock(ws, args.mission_id)")
          < cmds.index("store = gates.ApprovalStore(ws.internal_dir"
                       ' / "approvals")\n    protected ='))
    check("and a refusal is EXIT_BLOCKED, not a traceback",
          "functional_shell_locked REFUSED for" in cmds
          and "nothing was recorded and no lock was written" in cmds)
    check("the dry run does not write a lock",
          "_store_functional_lock(ws, mission_id, write=False)" in cmds
          and "    if not write:\n        return\n" in cmds)
    check("and it does not print the same warning twice",
          "redirect_stderr" in cmds)

    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    flat = " ".join(cl.split())
    check("0.31.0 is still one entry and was not renumbered",
          cl.count("## [0.31.0]") == 1 and "## [0.32.0]" not in cl)
    check("the entry names the mission and the numbers",
          "lot_demo_001" in cl and "markers 55" in flat
          and "site_counts markers 42" in flat)
    check("and what the lock protected before",
          "two records, for months" in flat and "1,171" in cl)
    check("and why it does not refuse guards_no_site yet",
          "NOT reject `guards_no_site`" in flat
          and "nobody has looked at" in flat)
    check("and records the ordering bug it nearly shipped",
          "AND AN ORDERING BUG I HAD ALREADY FIXED ONCE" in cl)

    print()
    print("  the gate is on, and it names the mission that earned it"
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
        for rel in (LOCK, COMMANDS, CHANGELOG):
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
        print("    python patches\\patch_lf_031b.py --selftest")
        print("    python -m pytest level_factory/tests/unit -q")
        print()
        print("  THEN RE-APPROVE lot_demo_001. It must still succeed -- the")
        print("  gate is on and this lock is the one that earned it:")
        print("    python -m level_factory -C workspaces\\lot-demo-ws \\")
        print("        approve lot_demo_001 functional_shell_locked")
        print()
        print("  then, INSIDE level_factory:")
        print('    git -C level_factory commit -am "0.31.0 -- the coverage '
              'report counts, and the gate turns on"')
        print('    git -C level_factory tag -a v0.31.0 -m "0.31.0"')
        print("    git -C level_factory push --follow-tags")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
