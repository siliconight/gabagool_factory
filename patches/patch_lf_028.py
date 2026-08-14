r"""level_factory 0.28.0 -- the functional lock says what it is guarding.

    python patch_lf_028.py --check
    python patch_lf_028.py
    python patch_lf_028.py --selftest
    python patch_lf_028.py --revert

Run from the FACTORY ROOT.

WHAT THIS IS NOT

It is NOT the fix for the vacuous lock. `tools/probe_selection_drift.py`
established that `site.site.gameplay.json` publishes twenty top-level keys and
none of the eleven `_merged_gameplay` reads -- Lot and Deli name the same
concepts differently, and the extraction is written in Deli's vocabulary.
Repairing that is a contract question between two tool repos, and the
obvious-looking pairs (`collision` -> `collision_hulls`, `openings` ->
`doorways`, `vertical_links` -> ladders and stairs, `markers`/`site_markers`
-> anchors) have not been opened and checked. A guessed mapping produces a
lock that hashes real data and still protects the wrong thing, which is
harder to notice than one that hashes nothing.

WHAT THIS IS

The reason nobody noticed for months. `compute_lock` will write a lock whose
three signatures are hashes of empty collections, report success, and hand
`verify_no_drift` something that passes against anything. Whatever the
mapping turns out to be, a lock that is guarding nothing should say so -- and
that guard needs no knowledge of the answer, which is the only reason it can
be built today.

    coverage.unguarded            which signatures have no content at all
    coverage.site_contributes     which protected keys the SITE supplied
    coverage.site_publishes_unread   the site's keys nothing here reads
    coverage.vacuous              nothing is protected

Computed on every `compute_lock`, stored in the lock file, and printed to
stderr when a signature is unguarded. `verify_no_drift` carries it through to
`RegressionResult.vacuous_lock`, and `cmd_export` prints a warning when the
post-art regression check PASSES against a lock that protects nothing --
which is the moment a human is being told something reassuring and false.

`site_publishes_unread` is the field that would have found this. It is the
vocabulary gap, written into the lock beside the hashes.

LOCK_COVERAGE_ENFORCED IS False, AND THAT IS THE PRECEDENT, NOT A DODGE

`export.py`'s `CLOSURE_ENFORCED` was False for exactly this reason, in its
own words: no export had ever been scanned at that point, the first run that
did found the current one broken, and promoting on day one would have failed
every export before anyone had looked at one. Same shape here. Every lock
this factory has ever written is vacuous; flipping the flag today refuses
`approve --gate functional_shell_locked` for every mission, including ones
whose art passes are mid-flight.

The measurement ALWAYS runs and ALWAYS lands in the lock file. The flag
decides only whether it stops the gate. Flip it when a mapping exists and one
real mission produces a non-vacuous lock -- and write down which mission.

AND THE SECOND DEFECT, WHICH IS SMALL AND HAS A REAL ORDERING BUG IN IT

`cmd_approve` writes `--candidate` to `<mission>.selected` verbatim. That is
how `lot_demo_001.candidate.seed_XXXX` -- a doc's placeholder -- became the
selected candidate. The SHAPE is now checked (`<mission>.candidate.seed_<n>`,
digits) and a bad one is refused.

Refused BEFORE the approval is recorded, which it was not. `store.record`
ran first, so a rejected candidate would already have left an approved
`candidate_selected` gate behind it. Nothing exercised that path because
nothing had ever rejected anything here.

Job EXISTENCE is warned about, not refused: whether `lot_assemble` has run
when the candidate is selected is an ordering question this patch has no
business deciding.

NOT DONE: the marker on disk is data, not code, and this does not rewrite it.
`workspaces/lot-demo-ws/.level_factory/approvals/lot_demo_001.selected` still
says `seed_XXXX`; the lock beside it says `seed_5219`.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

LOCK = "level_factory/packages/approvals/lock.py"
COMMANDS = "level_factory/apps/cli/commands/__init__.py"
VERSION_F = "level_factory/VERSION"
CHANGELOG = "level_factory/CHANGELOG.md"
SIDECAR = ".pre_028"

OLD_V, NEW_V = "0.27.0", "0.28.0"

COVERAGE_BLOCK = '''

#: The keys each protected signature actually reads. This is the same list
#: `_collision_signature`, `_anchor_registry` and `_route_graph` use, written
#: once so the coverage report cannot drift away from what is hashed. A key
#: added to a signature gets added here in the same edit.
PROTECTED_KEYS: dict[str, tuple[str, ...]] = {
    "collision_fingerprint": ("stair_systems", "ladders", "platforms",
                              "fire_escapes", "collision_hulls", "doorways"),
    "anchor_registry_hash": ("anchors",),
    "route_graph_hash": ("route", "route_graph", "nav_hints"),
}

#: Which keys `_merged_gameplay` backfills from the Deli side. These can carry
#: content while the SITE contributes nothing, which is precisely how a lock
#: that protects no site data still produces a non-empty signature and looks
#: healthy from the outside.
BACKFILLED_FROM_DELI = frozenset(
    {"stair_systems", "ladders", "platforms", "fire_escapes", "anchors"})

COVERAGE_SCHEMA = "level_factory.lock_coverage.v0.1"


class VacuousLockError(RuntimeError):
    """A functional lock whose signatures protect nothing."""


#: Whether a lock that protects nothing is refused outright.
#:
#: FALSE, for the reason `export.py`'s CLOSURE_ENFORCED was False: no lock had
#: ever been measured, the first measurement found EVERY lock this factory has
#: written to be vacuous, and refusing on day one would fail
#: `approve --gate functional_shell_locked` for every mission, including ones
#: whose art pass is already running.
#:
#: The cause is known and is not a bug in this file: `site.site.gameplay.json`
#: publishes twenty top-level keys and none of the eleven above. Lot and Deli
#: name the same concepts differently and the extraction is in Deli's
#: vocabulary. Mapping them is a contract question between two tool repos and
#: wants its own release.
#:
#: The measurement ALWAYS runs and ALWAYS lands in the lock file. This flag
#: decides only whether it stops the gate. Flip it once a mapping exists and
#: one real mission produces a non-vacuous lock -- and name that mission here.
LOCK_COVERAGE_ENFORCED = False


def _has_content(d: dict, key: str) -> bool:
    """Present AND not empty. `[]` is the shape this whole defect wore."""
    return bool(d.get(key))


def signature_coverage(gameplay: dict, site_gameplay: dict) -> dict:
    """What the three signatures are actually protecting.

    `gameplay` is the merged view that gets hashed; `site_gameplay` is the raw
    Lot file, needed separately because the merge backfills from Deli and the
    interesting question is what the SITE contributed.
    """
    read = {k for keys in PROTECTED_KEYS.values() for k in keys}
    sigs: dict[str, dict] = {}
    for name, keys in PROTECTED_KEYS.items():
        have = [k for k in keys if _has_content(gameplay, k)]
        sigs[name] = {
            "keys_with_content": have,
            "from_the_site": [k for k in keys
                              if _has_content(site_gameplay, k)],
            "backfilled_from_deli": [k for k in have
                                     if k in BACKFILLED_FROM_DELI
                                     and not _has_content(site_gameplay, k)],
            "guarding": bool(have),
        }
    unguarded = sorted(n for n, v in sigs.items() if not v["guarding"])
    return {
        "schema": COVERAGE_SCHEMA,
        "signatures": sigs,
        "unguarded": unguarded,
        "site_contributes": sorted(k for k in read
                                   if _has_content(site_gameplay, k)),
        # THE FIELD THAT WOULD HAVE FOUND THIS. The vocabulary gap, written
        # into the lock beside the hashes instead of left for a probe.
        "site_publishes_unread": sorted(set(site_gameplay) - read),
        "vacuous": len(unguarded) == len(PROTECTED_KEYS),
    }


def describe_coverage(cov: dict, mission_id: str) -> str:
    lines = [f"[lock] {mission_id}: "
             + ("THIS LOCK PROTECTS NOTHING." if cov["vacuous"]
                else "signatures with no content: "
                     + ", ".join(cov["unguarded"]))]
    if not cov["site_contributes"]:
        lines.append("[lock]   the site file contributed NO protected key; "
                     "every non-empty signature is backfilled from Deli")
    unread = cov["site_publishes_unread"]
    if unread:
        lines.append("[lock]   the site publishes %d key(s) nothing here "
                     "reads: %s" % (len(unread), ", ".join(unread[:12])
                                    + (" ..." if len(unread) > 12 else "")))
    lines.append("[lock]   see docs / probe_selection_drift.py; "
                 "LOCK_COVERAGE_ENFORCED is %s" % LOCK_COVERAGE_ENFORCED)
    return "\\n".join(lines)

'''

EDITS: list[tuple[str, str, str]] = [
    # ------------------------------------------------------------- lock.py --
    (LOCK, "import json\n", "import json\nimport sys\n"),

    (LOCK,
     "from packages.core.hashing import hash_json\n",
     "from packages.core.hashing import hash_json\n" + COVERAGE_BLOCK),

    (LOCK,
     "    locked_at: str = field(default_factory=_now)\n",
     "    locked_at: str = field(default_factory=_now)\n"
     "    #: What this lock protects. Empty on locks written before 0.28.0 --\n"
     "    #: `from_dict` filters to known fields, so an old lock loads with\n"
     "    #: no coverage rather than failing, and an absent report is not a\n"
     "    #: claim that the lock was covered.\n"
     "    coverage: dict = field(default_factory=dict)\n"),

    (LOCK,
     '            "locked_at": self.locked_at,\n        }\n',
     '            "locked_at": self.locked_at,\n'
     '            "coverage": self.coverage,\n        }\n'),

    (LOCK,
     '    """Compute a functional lock from the selected candidate\'s Lot site."""\n'
     "    gameplay = _merged_gameplay(site_gameplay_path, deli_gameplay_path)\n"
     "    return FunctionalLock(\n",

     '    """Compute a functional lock from the selected candidate\'s Lot site.\n'
     "\n"
     "    MEASURES WHAT IT IS PROTECTING, always, and records it. A lock whose\n"
     "    signatures are hashes of empty collections passes `verify_no_drift`\n"
     "    against anything, and reported success for months because nothing\n"
     "    ever asked it what it covered.\n"
     '    """\n'
     "    gameplay = _merged_gameplay(site_gameplay_path, deli_gameplay_path)\n"
     "    coverage = signature_coverage(gameplay, _load(site_gameplay_path))\n"
     "    if coverage[\"unguarded\"]:\n"
     "        note = describe_coverage(coverage, mission_id)\n"
     '        if LOCK_COVERAGE_ENFORCED and coverage["vacuous"]:\n'
     "            raise VacuousLockError(note)\n"
     "        print(note, file=sys.stderr)\n"
     "    return FunctionalLock(\n"),

    (LOCK,
     '        clearance_metrics=gameplay.get("clearance_metrics", {}),\n    )\n',
     '        clearance_metrics=gameplay.get("clearance_metrics", {}),\n'
     "        coverage=coverage,\n    )\n"),

    (LOCK,
     "class RegressionResult:\n"
     "    mission_id: str\n"
     "    passed: bool\n"
     "    drift: list[str] = field(default_factory=list)\n",

     "class RegressionResult:\n"
     "    mission_id: str\n"
     "    passed: bool\n"
     "    drift: list[str] = field(default_factory=list)\n"
     "    #: The lock this was checked against protects nothing, so `passed`\n"
     "    #: means only that nothing was compared. Carried rather than folded\n"
     "    #: into `drift`: a vacuous lock is not drift, and reporting it as\n"
     "    #: drift would block exports on a defect in the lock.\n"
     "    vacuous_lock: bool = False\n"),

    (LOCK,
     '        return {"mission_id": self.mission_id, "passed": self.passed,\n'
     '                "drift": self.drift}\n',
     '        return {"mission_id": self.mission_id, "passed": self.passed,\n'
     '                "drift": self.drift, "vacuous_lock": self.vacuous_lock}\n'),

    (LOCK,
     "    return RegressionResult(mission_id=lock.mission_id, passed=not drift, drift=drift)\n",
     "    return RegressionResult(\n"
     "        mission_id=lock.mission_id, passed=not drift, drift=drift,\n"
     "        vacuous_lock=bool((lock.coverage or {}).get(\"vacuous\")))\n"),

    # ------------------------------------------------------------ commands --
    (COMMANDS,
     "def cmd_approve(args) -> int:\n"
     "    ws = _ws(args)\n"
     '    store = gates.ApprovalStore(ws.internal_dir / "approvals")\n',

     "def _refuse_bad_candidate(ws: Workspace, mission_id: str,\n"
     "                          candidate: str) -> int:\n"
     '    """Refuse a candidate id that cannot name a real candidate.\n'
     "\n"
     "    `lot_demo_001.candidate.seed_XXXX` -- a doc's placeholder -- was the\n"
     "    selected candidate for a day, because this file wrote `--candidate`\n"
     "    to the marker verbatim and nothing looked at it. Everything\n"
     "    downstream builds a job directory from that string.\n"
     "\n"
     "    SHAPE is refused; EXISTENCE is only warned about. Whether\n"
     "    lot_assemble has run by the time a candidate is selected is an\n"
     "    ordering question this has no business deciding, but a marker that\n"
     "    cannot possibly name a job is wrong at any point in the order.\n"
     '    """\n'
     "    import re\n"
     "    want = re.compile(\n"
     '        r"^" + re.escape(str(mission_id)) + r"\\.candidate\\.seed_\\d+$")\n'
     "    if not want.match(str(candidate).strip()):\n"
     '        print(f"refusing --candidate {candidate!r}: expected "\n'
     '              f"{mission_id}.candidate.seed_<number>", file=sys.stderr)\n'
     '        print("  nothing is recorded; the gate is not approved",\n'
     "              file=sys.stderr)\n"
     "        return EXIT_BLOCKED\n"
     '    seed = str(candidate).strip().rsplit("_", 1)[-1]\n'
     '    job = ws.jobs_dir / f"{mission_id}.lot_assemble.candidate.seed_{seed}"\n'
     "    if not job.is_dir():\n"
     '        print(f"[approve] WARNING no {job.name} yet; the selection is "\n'
     '              f"recorded and will resolve once that job runs",\n'
     "              file=sys.stderr)\n"
     "    return EXIT_OK\n"
     "\n"
     "\n"
     "def cmd_approve(args) -> int:\n"
     "    ws = _ws(args)\n"
     "    # VALIDATED BEFORE ANYTHING IS RECORDED. It was not: store.record\n"
     "    # ran first, so a refused candidate would still have left an\n"
     "    # approved candidate_selected gate behind it. Nothing exercised that\n"
     "    # path because nothing here had ever refused anything.\n"
     "    if args.gate == gates.CANDIDATE_SELECTED and args.candidate:\n"
     "        rc = _refuse_bad_candidate(ws, args.mission_id, args.candidate)\n"
     "        if rc != EXIT_OK:\n"
     "            return rc\n"
     '    store = gates.ApprovalStore(ws.internal_dir / "approvals")\n'),

    (COMMANDS,
     "        if not regression.passed:\n",
     "        if regression.vacuous_lock:\n"
     "            # THE MOMENT A HUMAN IS TOLD SOMETHING REASSURING AND FALSE.\n"
     "            # `passed` here means nothing was compared, not that nothing\n"
     "            # moved. Printed on the pass, because the failure path\n"
     "            # already speaks for itself.\n"
     '            print("[export] WARNING the functional lock for "\n'
     '                  f"{mission_id} protects nothing -- the post-art "\n'
     '                  "regression check passed because it compared no "\n'
     '                  "content. See its `coverage` block, or run "\n'
     '                  "tools/probe_selection_drift.py", file=sys.stderr)\n'
     "        if not regression.passed:\n"),
]

ENTRY = """## [0.28.0] - the lock says what it is guarding

`tools/probe_selection_drift.py` established that every functional lock this
factory has written protects nothing: `site.site.gameplay.json` publishes
twenty top-level keys and none of the eleven `_merged_gameplay` reads. Lot and
Deli name the same concepts differently and the extraction is written in
Deli's vocabulary.

THIS IS NOT THAT FIX. Mapping the two vocabularies is a contract question
between two tool repos, and the obvious-looking pairs -- `collision` ->
`collision_hulls`, `openings` -> `doorways`, `vertical_links` -> ladders and
stairs, `markers`/`site_markers` -> anchors -- have not been opened and
checked. A guessed mapping gives a lock that hashes real data and still
protects the wrong thing, which is harder to notice than one that hashes
nothing.

This is the reason nobody noticed for months.

- **`compute_lock` now measures what it is protecting, every time**, and
  stores it in the lock as `coverage`: which signatures have no content at
  all, which protected keys the SITE supplied, and -- the field that would
  have found this years earlier -- `site_publishes_unread`, the site's own
  keys that nothing here reads. The vocabulary gap, written beside the
  hashes.
- **`PROTECTED_KEYS` is now one list.** The coverage report reads the same
  names the three signatures hash, so it cannot drift away from them.
- **`verify_no_drift` carries `vacuous_lock` through to
  `RegressionResult`** -- not folded into `drift`, because a vacuous lock is
  not drift and reporting it as drift would block exports on a defect in the
  lock.
- **`cmd_export` warns when the regression check PASSES against a lock that
  protects nothing.** That is the moment a human is told something reassuring
  and false; the failing path already speaks for itself.
- **Old locks load unchanged.** `from_dict` filters to known fields, so a
  pre-0.28.0 lock arrives with no coverage rather than failing -- and an
  absent report is not a claim that the lock was covered.

LOCK_COVERAGE_ENFORCED IS False, WHICH IS THE PRECEDENT AND NOT A DODGE

`export.py`'s `CLOSURE_ENFORCED` was False for the same reason, in its own
words: no export had ever been scanned at that point, the first run that did
found the current one broken, and promoting on day one would have failed
every export before anyone had looked at one. Every lock here is vacuous
today; enforcing would refuse `approve --gate functional_shell_locked` for
every mission, including ones whose art pass is already running.

The measurement ALWAYS runs and ALWAYS lands in the lock file. The flag
decides only whether it stops the gate. Flip it once a mapping exists and one
real mission produces a non-vacuous lock -- and name that mission in the
comment, the way this one names its reason.

THE SECOND DEFECT, AND THE ORDERING BUG INSIDE IT

`cmd_approve` wrote `--candidate` to `<mission>.selected` verbatim, which is
how `lot_demo_001.candidate.seed_XXXX` became the selected candidate for a
day. The shape is now checked and a bad one refused.

Refused BEFORE the approval is recorded, which it was not: `store.record` ran
first, so a rejected candidate would still have left an approved
`candidate_selected` gate behind it. Nothing had exercised that path because
nothing here had ever refused anything.

Job existence is warned about, not refused -- whether `lot_assemble` has run
when a candidate is selected is an ordering question this has no business
deciding.

NOT DONE HERE

The vocabulary mapping, which is the actual repair. The marker on disk:
`workspaces/lot-demo-ws/.level_factory/approvals/lot_demo_001.selected` still
says `seed_XXXX` while the lock beside it says `seed_5219`; that is data, and
this does not rewrite data. `_selected_lot_out` still resolves jobs from the
marker, so `graybox_dir` is still a dead path for that mission.
"""

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
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

    vp, cp = root / VERSION_F, root / CHANGELOG
    vbody = vp.read_text(encoding="utf-8")
    cbody = cp.read_text(encoding="utf-8")
    if NEW_V in vbody and f"## [{NEW_V}]" in cbody:
        print("  already applied  VERSION + CHANGELOG")
        return 0
    if OLD_V not in vbody:
        print(f"REFUSING: {VERSION_F} does not say {OLD_V} "
              f"(found {vbody.strip()!r})")
        return 1
    if check:
        print(f"  would bump   VERSION  {OLD_V} -> {NEW_V}")
        print(f"  would prepend CHANGELOG.md  "
              f"+{len(ENTRY.encode('utf-8')) + 1:,} bytes")
        return 0
    for q, txt in ((vp, vbody), (cp, cbody)):
        side = q.with_suffix(q.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(txt.encode("utf-8"))
    vp.write_bytes(vbody.replace(OLD_V, NEW_V, 1).encode("utf-8"))
    cp.write_bytes((ENTRY + "\n" + cbody).encode("utf-8"))
    print(f"  bumped       VERSION  {OLD_V} -> {NEW_V}")
    print("  prepended    CHANGELOG.md")
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

    check("the coverage report reads the keys the signatures hash",
          set(lk.PROTECTED_KEYS) ==
          {"collision_fingerprint", "anchor_registry_hash",
           "route_graph_hash"}
          and set(lk.PROTECTED_KEYS["collision_fingerprint"])
          == set(lk._collision_signature({})))
    check("enforcement is off, and the flag exists to be flipped",
          lk.LOCK_COVERAGE_ENFORCED is False)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        def w(name, data):
            p = tmp / name
            p.write_text(json.dumps(data), encoding="utf-8")
            return p

        # The real shape: a Lot site with its own vocabulary, a Deli shell.
        site = w("site.gameplay.json", {
            "buildings": [1], "collision": [1], "openings": [1],
            "vertical_links": [1], "markers": [1], "zones": [1]})
        deli = w("shell.gameplay.json", {
            "stair_systems": [{"id": "s1"}], "ladders": [], "platforms": [],
            "fire_escapes": []})

        lock = lk.compute_lock(mission_id="m1", candidate_id="m1.candidate.seed_1",
                               seed=1, site_gameplay_path=site,
                               deli_gameplay_path=deli)
        cov = lock.coverage
        check("the lock carries a coverage report", bool(cov))
        check("it knows the site contributed no protected key",
              cov["site_contributes"] == [])
        check("it names the site keys nothing reads",
              set(cov["site_publishes_unread"]) ==
              {"buildings", "collision", "openings", "vertical_links",
               "markers", "zones"})
        check("anchors and the route graph are reported unguarded",
              set(cov["unguarded"]) == {"anchor_registry_hash",
                                        "route_graph_hash"})
        check("collision is 'guarded' only by Deli's backfill",
              cov["signatures"]["collision_fingerprint"]["guarding"] is True
              and cov["signatures"]["collision_fingerprint"]
                     ["backfilled_from_deli"] == ["stair_systems"])
        check("and it is not called vacuous, because one signature has content",
              cov["vacuous"] is False)

        # Nothing anywhere -> vacuous.
        empty_site = w("empty_site.json", {"buildings": [1]})
        empty_deli = w("empty_deli.json", {})
        vac = lk.compute_lock(mission_id="m2", candidate_id="m2.candidate.seed_1",
                              seed=1, site_gameplay_path=empty_site,
                              deli_gameplay_path=empty_deli)
        check("a lock protecting nothing says so", vac.coverage["vacuous"])
        check("and the message says it in words",
              "THIS LOCK PROTECTS NOTHING"
              in lk.describe_coverage(vac.coverage, "m2"))

        # It survives the round trip through the lock file.
        back = lk.FunctionalLock.from_dict(json.loads(json.dumps(vac.as_dict())))
        check("coverage survives as_dict / from_dict",
              back.coverage == vac.coverage)

        r = lk.verify_no_drift(back, empty_site, empty_deli)
        check("the regression check passes -- against nothing", r.passed)
        check("and says so, without calling it drift",
              r.vacuous_lock is True and r.drift == [])
        check("as_dict carries it to anyone reading the report",
              r.as_dict()["vacuous_lock"] is True)

        # A pre-0.28.0 lock has no coverage, and absence is not a claim.
        old = lk.FunctionalLock.from_dict(
            {k: v for k, v in vac.as_dict().items() if k != "coverage"})
        check("an old lock loads rather than failing", old.coverage == {})
        check("and is still MEASURED, because the files are right there",
              lk.verify_no_drift(old, empty_site,
                                 empty_deli).vacuous_lock is True)
        check("the report says what THIS comparison protected",
              lk.verify_no_drift(old, empty_site, empty_deli)
              .coverage["vacuous"] is True)

        # Enforcement, when someone flips it.
        lk.LOCK_COVERAGE_ENFORCED = True
        try:
            lk.compute_lock(mission_id="m3", candidate_id="m3.candidate.seed_1",
                            seed=1, site_gameplay_path=empty_site,
                            deli_gameplay_path=empty_deli)
            check("flipping the flag refuses a vacuous lock", False)
        except lk.VacuousLockError:
            check("flipping the flag refuses a vacuous lock", True)
        finally:
            lk.LOCK_COVERAGE_ENFORCED = False

    cmds = (root / COMMANDS).read_text(encoding="utf-8")
    check("the candidate is validated before anything is recorded",
          cmds.index("rc = _refuse_bad_candidate(")
          < cmds.index('store = gates.ApprovalStore(ws.internal_dir / "approvals")\n'
                       "    protected = _protected_inputs_for_gate("))
    check("a bad shape is refused; a missing job is only warned about",
          "return EXIT_BLOCKED" in cmds
          and "will resolve once that job runs" in cmds)
    check("cmd_export warns when the check passes on nothing",
          "regression.vacuous_lock" in cmds
          and "protects nothing" in cmds)

    v = (root / VERSION_F).read_text(encoding="utf-8")
    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    check(f"VERSION is {NEW_V}", NEW_V in v)
    check(f"one {NEW_V} entry", cl.count(f"## [{NEW_V}]") == 1)
    check("the entry says this is NOT the real fix",
          "THIS IS NOT THAT FIX" in cl)
    # Markdown-stripped: the entry backticks the identifier, and an assertion
    # that forgets that fails on prose rather than on substance. Third time
    # this session.
    plain = cl.replace("`", "")
    check("and why the flag is off, citing the precedent",
          "CLOSURE_ENFORCED was False for the same reason" in plain)
    check("and names what is still not done",
          "NOT DONE HERE" in cl and "seed_XXXX" in cl)

    print()
    print("  a lock that guards nothing now says so, in the file and on stderr"
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
        for rel in (LOCK, COMMANDS, VERSION_F, CHANGELOG):
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
        print("    python patches\\patch_lf_028.py --selftest")
        print("    python -m pytest level_factory/tests/unit -q")
        print()
        print("  THEN SEE IT ON A REAL RUN -- the export should now warn that")
        print("  the regression check passed against a lock protecting nothing:")
        print("    python -m level_factory -C workspaces\\lot-demo-ws \\")
        print("        export lot_demo_001 --mode portable-godot")
        print()
        print("  then, INSIDE level_factory:")
        print('    git -C level_factory commit -am "0.28.0 -- the lock says '
              'what it is guarding"')
        print(f'    git -C level_factory tag -a v{NEW_V} -m "{NEW_V}"')
        print("    git -C level_factory push --follow-tags")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
