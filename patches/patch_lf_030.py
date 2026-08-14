r"""level_factory 0.30.0 -- the anchor registry stops dropping Deli's anchors.

    python patch_lf_030.py --check
    python patch_lf_030.py
    python patch_lf_030.py --selftest
    python patch_lf_030.py --revert

Run from the FACTORY ROOT. Touches level_factory AND docs/FUNCTIONAL_LOCK.md,
so it is two commits -- the doc at factory level, the code in the tool repo.

WHAT THE OVERLAP REPORT FOUND

    markers   site 42, deli 14
      of deli's 14: 0 exact, 1 by name-tail, 13 with no match
      no match: CREW_SPAWN_A, RESPONDER_SPAWN_1,
                COVER_LOW_AUTO_TELLER_COUNTER,
                COVER_LOW_AUTO_DESK_MANAGER_OFFICE_0, ...

Thirteen of Deli's fourteen markers do not appear in Lot's forty-two, and
they are not incidental: two spawns and a set of cover points. The anchor
registry -- whose drift message reads "gameplay-anchor registry changed after
art pass" -- was hashing Lot's 42 and discarding those 13.

THEY ARE NOT A SUBSET. THEY ARE A DIFFERENT POPULATION.

Lot's markers are site-level: `b0/ATTACKER_SPAWN_FRONT`, building entries.
Deli's are interior gameplay anchors, and the `rooms` line of the same report
confirms it -- Deli's unmatched `manager_office`, `security_room` and
`vault_room` are exactly where `COVER_LOW_AUTO_DESK_MANAGER_OFFICE_0` lives.
The same shape as `vertical_links` (4 hatches) against `stair_systems` (2):
complementary, not competing.

`_merged_gameplay` had one rule for shared keys -- the site wins -- and that
rule is right for a key where Lot restates what Deli said, and wrong for a
key where they each say something the other does not.

THE FIX: A SECOND RULE, NAMED

    BACKFILLED_FROM_DELI   Deli's value is used when the site omits the key
    UNIONED_WITH_DELI      both are kept; Deli's records that the site
                           already carries (by name-tail) are not duplicated

`markers` is the only member of the second set. Dedupe is by NAME-TAIL, not
by exact id, because Lot namespaces what it does restate -- Deli's `VAULT`
becomes `b0/VAULT`, and an exact-match dedupe would carry both and count one
anchor twice.

WHY markers AND NOT surfaces

`surfaces` matched 213 of Deli's 238 by tail. The 25 that did not are
`int_col_-1_2_*` -- story -1, a basement -- and window sub-parts (pane, sill,
lintel). If Lot never places that geometry it is not in the shipped level,
and hashing it would protect something the package does not contain and
report drift the day Lot legitimately stops emitting it. Deli's markers, by
contrast, ship: the Dispatch handoff carries them into the export.

`openings` is 0 of 19, but that is a whole-record comparison against
coordinates Lot transforms when it places a shell. Undecidable from these two
files, and not decided here.

NOT DONE: `LOCK_COVERAGE_ENFORCED` STAYS FALSE

The doc's order is land the change, recompute a real lock, confirm, then
flip. Recompute `lot_demo_001` after this and check that the registry grew by
13. Flipping before that would be asserting the fix worked without looking,
which is the failure this factory has hit five times in two days.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

LOCK = "level_factory/packages/approvals/lock.py"
VERSION_F = "level_factory/VERSION"
CHANGELOG = "level_factory/CHANGELOG.md"
DOC = "docs/FUNCTIONAL_LOCK.md"
SIDECAR = ".pre_030"

OLD_V, NEW_V = "0.29.0", "0.30.0"

EDITS: list[tuple[str, str, str]] = [
    (LOCK,
     "BACKFILLED_FROM_DELI = frozenset(\n"
     '    {"stair_systems", "ladders", "platforms", "fire_escapes"})\n',

     "BACKFILLED_FROM_DELI = frozenset(\n"
     '    {"stair_systems", "ladders", "platforms", "fire_escapes"})\n'
     "\n"
     "#: Keys where BOTH tools publish real content and neither restates the\n"
     "#: other, so the lock protects the UNION.\n"
     "#:\n"
     "#: `_merged_gameplay` had exactly one rule for a shared key -- the site\n"
     "#: wins -- which is right when Lot restates what Deli said and wrong\n"
     "#: when they each say something the other does not. Measured\n"
     "#: 2026-08-14 by tools/probe_site_vocabulary.py: of Deli's 14 markers,\n"
     "#: ONE appeared in Lot's 42. The other thirteen -- CREW_SPAWN_A,\n"
     "#: RESPONDER_SPAWN_1 and eleven cover points -- were being dropped from\n"
     "#: the gameplay-anchor registry by a rule written for the other case.\n"
     "#:\n"
     "#: `surfaces` is deliberately NOT here: 25 of Deli's 238 collision\n"
     "#: nodes are story -1 and window sub-parts that Lot appears never to\n"
     "#: place, and hashing geometry the package does not contain would\n"
     "#: report drift the day Lot legitimately stops emitting it.\n"
     "UNIONED_WITH_DELI = frozenset({\"markers\"})\n"),

    (LOCK,
     '        if not merged.get("anchors"):\n'
     '            merged["anchors"] = deli_gp.get("anchors", [])\n'
     "        gameplay = merged\n",

     '        if not merged.get("anchors"):\n'
     '            merged["anchors"] = deli_gp.get("anchors", [])\n'
     "        # UNION, not overwrite. See UNIONED_WITH_DELI.\n"
     "        for k in UNIONED_WITH_DELI:\n"
     "            merged[k] = _union_by_tail(merged.get(k) or [],\n"
     "                                       deli_gp.get(k) or [])\n"
     "        gameplay = merged\n"),

    (LOCK,
     "def _merged_gameplay(site_gameplay_path: Path, deli_gameplay_path: Path | None) -> dict:\n",

     "def _tail(ident: str) -> str:\n"
     '    """The part of an identity after its namespace prefix."""\n'
     '    return str(ident).rsplit("/", 1)[-1]\n'
     "\n"
     "\n"
     "def _union_by_tail(site_records: list, deli_records: list) -> list:\n"
     '    """Site records, plus Deli records the site does not already carry.\n'
     "\n"
     "    DEDUPED BY NAME-TAIL, not by exact identity. Lot namespaces the\n"
     "    anchors it does restate -- Deli's `VAULT` becomes `b0/VAULT` -- so\n"
     "    an exact-match dedupe would keep both and count one anchor twice.\n"
     "    Of Deli's 14 markers in lot_demo_001, exactly one matches this way;\n"
     "    the rule exists for that one.\n"
     '    """\n'
     "    out = list(site_records)\n"
     "    have = {_tail(_anchor_identity(r)) for r in site_records\n"
     "            if isinstance(r, dict)}\n"
     "    for r in deli_records:\n"
     "        if not isinstance(r, dict):\n"
     "            continue\n"
     "        if _tail(_anchor_identity(r)) in have:\n"
     "            continue\n"
     "        out.append(r)\n"
     "    return out\n"
     "\n"
     "\n"
     "def _merged_gameplay(site_gameplay_path: Path, deli_gameplay_path: Path | None) -> dict:\n"),

    (LOCK,
     '            "backfilled_from_deli": [k for k in have\n'
     "                                     if k in BACKFILLED_FROM_DELI\n"
     "                                     and not _has_content(site_gameplay, k)],\n",

     '            "backfilled_from_deli": [k for k in have\n'
     "                                     if k in BACKFILLED_FROM_DELI\n"
     "                                     and not _has_content(site_gameplay, k)],\n"
     "            # Visible for the same reason the backfill is: a signature\n"
     "            # carrying two tools' records should say so.\n"
     '            "unioned_with_deli": [k for k in keys\n'
     "                                  if k in UNIONED_WITH_DELI],\n"),

    # ------------------------------------------------------------------ doc --
    (DOC,
     "## What this deliberately does NOT protect\n",

     "## Two rules for a shared key\n"
     "\n"
     "*Added 2026-08-14, after `tools/probe_site_vocabulary.py` measured the\n"
     "overlap.*\n"
     "\n"
     "Both tools publish `markers`, `openings`, `surfaces` and `rooms`.\n"
     "`_merged_gameplay` had one rule for that -- the site wins -- and it is\n"
     "right only when Lot restates what Deli said.\n"
     "\n"
     "| | site | deli | of deli's, matched |\n"
     "|---|---|---|---|\n"
     "| `markers` | 42 | 14 | **1** |\n"
     "| `surfaces` | 1029 | 238 | 213 |\n"
     "| `openings` | 76 | 19 | 0, whole-record |\n"
     "| `rooms` | 25 | 4 | 1 |\n"
     "\n"
     "`markers` is not a subset relationship. Lot's are site-level\n"
     "(`b0/ATTACKER_SPAWN_FRONT`); Deli's are interior gameplay anchors --\n"
     "`CREW_SPAWN_A`, `RESPONDER_SPAWN_1`, eleven cover points. The `rooms`\n"
     "row confirms it: Deli's unmatched `manager_office`, `security_room`,\n"
     "`vault_room` are where those cover points live. Thirteen gameplay\n"
     "anchors were being dropped from the gameplay-anchor registry.\n"
     "\n"
     "So there are two rules, and they are named:\n"
     "\n"
     "- **`BACKFILLED_FROM_DELI`** -- Deli's value is used when the site omits\n"
     "  the key. `stair_systems`, `ladders`, `platforms`, `fire_escapes`.\n"
     "- **`UNIONED_WITH_DELI`** -- both are kept, deduped by NAME-TAIL because\n"
     "  Lot namespaces what it does restate. `markers` only.\n"
     "\n"
     "**`surfaces` is deliberately not unioned.** The 25 unmatched are\n"
     "`int_col_-1_2_*` -- story -1 -- and window sub-parts. If Lot never\n"
     "places that geometry it is not in the shipped level, and hashing it\n"
     "would protect what the package does not contain and report drift the\n"
     "day Lot stops emitting it. Deli's markers ship: the Dispatch handoff\n"
     "carries them into the export.\n"
     "\n"
     "**`openings` is undecided.** 0 of 19 matched, but that compares whole\n"
     "records against coordinates Lot transforms when it places a shell. Not\n"
     "decidable from these two files.\n"
     "\n"
     "**Those 25 collision nodes are a question for `lot`**, not for the lock:\n"
     "geometry that exists in the shell and not in the assembled site is\n"
     "either a deliberate drop nobody wrote down, or loss between two stages.\n"
     "\n"
     "## What this deliberately does NOT protect\n"),
]

ENTRY = """## [0.30.0] - the registry stops dropping Deli's anchors

`tools/probe_site_vocabulary.py` compared what both tools publish for the
keys they share:

    markers   site 42, deli 14 -- of deli's 14, ONE appears in the site's 42
    no match: CREW_SPAWN_A, RESPONDER_SPAWN_1, COVER_LOW_AUTO_TELLER_COUNTER,
              COVER_LOW_AUTO_DESK_MANAGER_OFFICE_0, ... (13 in all)

Thirteen gameplay anchors -- two spawns and eleven cover points -- were being
dropped from the gameplay-anchor registry.

THEY WERE NEVER A SUBSET

Lot's markers are site-level (`b0/ATTACKER_SPAWN_FRONT`, building entries).
Deli's are interior anchors, and the same report's `rooms` line confirms it:
Deli's unmatched `manager_office`, `security_room` and `vault_room` are
exactly where those cover points live. The same shape as `vertical_links`
(4 hatches) against `stair_systems` (2) -- complementary, not competing.

`_merged_gameplay` had one rule for a shared key: the site wins. That is
right when Lot restates what Deli said and wrong when each says something the
other does not, and nothing distinguished the two cases.

- **`UNIONED_WITH_DELI` is the second rule**, beside `BACKFILLED_FROM_DELI`,
  and `markers` is its only member. Both tools' records are kept.
- **Deduped by NAME-TAIL, not exact id.** Lot namespaces what it does
  restate -- Deli's `VAULT` becomes `b0/VAULT` -- so an exact-match dedupe
  would keep both and count one anchor twice. Exactly one of Deli's 14
  matches this way; the rule exists for that one.
- **`coverage.unioned_with_deli` names it**, for the reason
  `backfilled_from_deli` exists: a signature carrying two tools' records
  should say so.

WHY NOT `surfaces`

213 of Deli's 238 matched by tail. The 25 that did not are `int_col_-1_2_*`
-- story -1, a basement -- and window sub-parts (pane, sill, lintel). If Lot
never places that geometry it is not in the shipped level, and hashing it
would protect what the package does not contain, and report drift the day Lot
legitimately stops emitting it. Deli's markers ship: the Dispatch handoff
carries them into the export. That asymmetry is the whole argument.

`openings` is 0 of 19, but that compares whole records against coordinates
Lot transforms when it places a shell. Undecidable from these two files, and
not decided here.

NOT DONE HERE

`LOCK_COVERAGE_ENFORCED` stays False. The order is land the change, recompute
`lot_demo_001`, confirm the registry grew by 13, THEN flip. Flipping now
would assert the fix worked without looking, which is the failure this
factory has hit five times in two days.

Those 25 collision nodes are a question for `lot`: geometry present in the
shell and absent from the assembled site is either a deliberate drop nobody
recorded, or loss between two stages. The lock cannot tell which.
"""

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
    if not (root / DOC).is_file():
        print(f"REFUSING: {DOC} is not here")
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

    vp, cp = root / VERSION_F, root / CHANGELOG
    vbody = vp.read_text(encoding="utf-8")
    cbody = cp.read_text(encoding="utf-8")
    if NEW_V in vbody and f"## [{NEW_V}]" in cbody:
        print("  already applied  VERSION + CHANGELOG")
        return 0
    if OLD_V not in vbody:
        print(f"REFUSING: {VERSION_F} does not say {OLD_V}")
        return 1
    if check:
        print(f"  would bump   VERSION  {OLD_V} -> {NEW_V}")
        print(f"  would prepend CHANGELOG.md  +{len(ENTRY) + 1:,} bytes")
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

    check("there are two named rules, not one",
          lk.UNIONED_WITH_DELI == frozenset({"markers"})
          and "markers" not in lk.BACKFILLED_FROM_DELI)
    check("surfaces is deliberately not unioned",
          "surfaces" not in lk.UNIONED_WITH_DELI)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        def w(name, data):
            p = tmp / name
            p.write_text(json.dumps(data), encoding="utf-8")
            return p

        # THE REAL SHAPE: Lot's site-level markers, Deli's interior ones,
        # and one that Lot restated under a namespace.
        site = w("site.json", {
            "markers": [
                {"id": "FRONT", "name": "b0/ATTACKER_SPAWN_FRONT",
                 "type": "attacker_spawn", "x": -77.0, "y": -65.0, "z": 0},
                {"id": "VAULT", "name": "b0/VAULT", "type": "vault",
                 "x": 3.0, "y": 4.0, "z": 0}],
            "surfaces": [{"node": "b0/ext_col_0", "material": {"id": "glass"}}],
            "ground": {"b0": {"source": "a.glb"}},
            "openings": [{"kind": "door", "building": "b0"}]})
        deli = w("deli.json", {
            "stair_systems": [{"id": "s1"}],
            "markers": [
                {"id": "VAULT", "type": "vault"},              # Lot restated
                {"id": "CREW_SPAWN_A", "type": "crew_spawn"},  # it did not
                {"id": "RESPONDER_SPAWN_1", "type": "responder_spawn"},
                {"id": "COVER_LOW_AUTO_TELLER_COUNTER", "type": "cover"}],
            # 25-of-238 case: Deli collision Lot never places.
            "surfaces": [{"node": "b0/int_col_-1_2_seg0"}]})

        merged = lk._merged_gameplay(site, deli)
        ids = {lk._anchor_identity(m) for m in merged["markers"]}
        check("the site's own markers survive",
              "b0/ATTACKER_SPAWN_FRONT" in ids)
        check("DELI'S INTERIOR ANCHORS ARE NO LONGER DROPPED",
              {"CREW_SPAWN_A", "RESPONDER_SPAWN_1",
               "COVER_LOW_AUTO_TELLER_COUNTER"} <= ids)
        check("the one Lot restated is not counted twice",
              len(merged["markers"]) == 5
              and sum(1 for i in ids if lk._tail(i) == "VAULT") == 1)
        check("and it is the namespaced form that survives",
              "b0/VAULT" in ids and "VAULT" not in ids)

        check("surfaces is NOT unioned -- Deli's basement stays out",
              [s["node"] for s in merged["surfaces"]] == ["b0/ext_col_0"])

        lock = lk.compute_lock(mission_id="m1",
                               candidate_id="m1.candidate.seed_1", seed=1,
                               site_gameplay_path=site,
                               deli_gameplay_path=deli)
        check("the registry hashes all five", len(
            lk._anchor_registry(merged)) == 5)
        check("coverage names the union, as it names the backfill",
              lock.coverage["signatures"]["anchor_registry_hash"]
              ["unioned_with_deli"] == ["markers"])
        check("and the lock still protects the site",
              lock.coverage["guards_no_site"] is False
              and lock.coverage["vacuous"] is False)

        # Dropping a Deli anchor is now drift. It was invisible.
        deli2 = w("deli2.json", {
            "stair_systems": [{"id": "s1"}],
            "markers": [{"id": "VAULT", "type": "vault"},
                        {"id": "CREW_SPAWN_A", "type": "crew_spawn"},
                        {"id": "RESPONDER_SPAWN_1", "type": "responder_spawn"}]})
        r = lk.verify_no_drift(lock, site, deli2)
        check("LOSING A DELI COVER POINT IS NOW DRIFT",
              not r.passed and any("anchor" in d for d in r.drift))

    check("enforcement is still off", lk.LOCK_COVERAGE_ENFORCED is False)

    doc = (root / DOC).read_text(encoding="utf-8")
    check("the doc carries the measured table",
          "| `markers` | 42 | 14 | **1** |" in doc)
    check("and names both rules",
          "BACKFILLED_FROM_DELI" in doc and "UNIONED_WITH_DELI" in doc)
    # Whitespace-collapsed. Fourth time this session an assertion has failed
    # on a line wrap rather than on substance; the flat copy is the fix.
    flat_doc = " ".join(doc.split())
    check("and says why surfaces is excluded",
          "story -1" in flat_doc
          and "the day Lot stops emitting it" in flat_doc)
    check("and hands the 25 nodes to lot",
          "a question for `lot`" in doc)

    v = (root / VERSION_F).read_text(encoding="utf-8")
    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    check(f"VERSION is {NEW_V}", NEW_V in v)
    check(f"one {NEW_V} entry", cl.count(f"## [{NEW_V}]") == 1)
    check("the entry names the thirteen and what they are",
          "CREW_SPAWN_A" in cl and "eleven cover points" in cl)
    check("and says the flag is not flipped yet",
          "stays False" in cl and "without looking" in cl)

    print()
    print("  two rules, and thirteen anchors that stopped being invisible"
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
        for rel in (LOCK, DOC, VERSION_F, CHANGELOG):
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
        print("    python patches\\patch_lf_030.py --selftest")
        print("    python -m pytest level_factory/tests/unit -q")
        print()
        print("  THEN RECOMPUTE AND COUNT. The registry should grow by 13:")
        print("    python -m level_factory -C workspaces\\lot-demo-ws \\")
        print("        approve lot_demo_001 functional_shell_locked")
        print("    python tools\\probe_site_vocabulary.py "
              "-C workspaces\\lot-demo-ws lot_demo_001 | "
              'Select-String "of deli.s 14"')
        print()
        print("  expect '14 exact/by name-tail, 0 with no match' once the")
        print("  merged view is what the probe reads.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
