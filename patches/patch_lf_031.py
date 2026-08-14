r"""level_factory 0.31.0 -- the coverage report counts, and the gate turns on.

    python patch_lf_031.py --check
    python patch_lf_031.py
    python patch_lf_031.py --selftest
    python patch_lf_031.py --revert

Run from the FACTORY ROOT.

WHY COUNTS

`coverage` answers "is something there" and never "how much". `markers:
guarding=True` reads identically whether the registry holds fifty-five
anchors or one. That is the gap that hid this entire defect: before 0.29.0
the collision signature reported `guarding=True` while carrying two Deli
stair systems and nothing else, and every report agreed with it.

A count would have shown it the first time anyone looked.

    counts        per protected key, in the MERGED view -- what is hashed
    site_counts   the same keys in the site file alone

The pair is the interesting part. For `markers` they differ by exactly the
number of Deli anchors the union pulled in, so the union's effect is a
subtraction a reader can do in their head, from the lock file, without a
probe and without this conversation.

WHAT THIS DOES NOT DO

It does not flip `LOCK_COVERAGE_ENFORCED`. Land this, recompute
`lot_demo_001`, read `counts.markers` against `site_counts.markers`, and
flip only if the difference is the thirteen. The flip belongs in this same
release -- it is uncommitted until then -- with the real number in the entry
rather than a hash delta.

Verified so far, and it is not enough on its own: after 0.30.0 the recomputed
lock's `anchor_registry_hash` moved from `b47f0dc` to `6dd9d16` while
`collision_fingerprint` stayed at `091d798`. The registry changed and the
collision signature did not, which is the right shape -- Deli's anchors in,
Deli's 238 surfaces still out. It proves the union fired. It does not prove
how many it added, and this release exists because that distinction is the
whole lesson.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

LOCK = "level_factory/packages/approvals/lock.py"
VERSION_F = "level_factory/VERSION"
CHANGELOG = "level_factory/CHANGELOG.md"
SIDECAR = ".pre_031"

OLD_V, NEW_V = "0.30.0", "0.31.0"

EDITS: list[tuple[str, str, str]] = [
    (LOCK,
     "def _has_content(d: dict, key: str) -> bool:\n",

     "def _size(d: dict, key: str) -> int:\n"
     '    """How many records a key carries. 0 when absent or empty.\n'
     "\n"
     "    THE NUMBER `guarding` DOES NOT CARRY. `markers: guarding=True`\n"
     "    reads the same whether the registry holds fifty-five anchors or\n"
     "    one, and before 0.29.0 the collision signature reported guarding\n"
     "    while carrying two Deli stair systems and nothing else. Every\n"
     "    report agreed with it. A count would not have.\n"
     '    """\n'
     "    v = d.get(key)\n"
     "    if isinstance(v, (list, dict, str)):\n"
     "        return len(v)\n"
     "    return 0 if v is None else 1\n"
     "\n"
     "\n"
     "def _has_content(d: dict, key: str) -> bool:\n"),

    (LOCK,
     '        "guards_no_site": not any(_has_content(site_gameplay, k)\n'
     "                                  for k in read),\n",

     '        "guards_no_site": not any(_has_content(site_gameplay, k)\n'
     "                                  for k in read),\n"
     "        # WHAT IS HASHED, and what the site alone published. The pair is\n"
     "        # the point: for a unioned key they differ by exactly what the\n"
     "        # other tool contributed, so a reader can do the subtraction\n"
     "        # from the lock file without a probe.\n"
     '        "counts": {k: _size(gameplay, k) for k in sorted(read)},\n'
     '        "site_counts": {k: _size(site_gameplay, k)\n'
     "                        for k in sorted(read)},\n"),
]

ENTRY = """## [0.31.0] - the coverage report counts

`coverage` answered "is something there" and never "how much".
`markers: guarding=True` read identically whether the registry held
fifty-five anchors or one.

That is the gap that hid the whole defect. Before 0.29.0 the collision
signature reported `guarding=True` while carrying two Deli stair systems and
nothing else, and every report in the system agreed with it. A count would
have shown it the first time anyone looked.

- **`coverage.counts`** -- per protected key, in the MERGED view. What is
  actually hashed.
- **`coverage.site_counts`** -- the same keys in the site file alone.

The pair is the useful part. For a unioned key the two differ by exactly what
the other tool contributed, so the union's effect is a subtraction a reader
can do in their head, from the lock file, without a probe.

WHAT THE HASHES ALONE COULD NOT SAY

After 0.30.0 the recomputed lock's `anchor_registry_hash` moved from
`b47f0dc` to `6dd9d16` while `collision_fingerprint` stayed at `091d798` --
the registry changed, the collision signature did not, which is the right
shape: Deli's anchors in, Deli's 238 surfaces still out. It proved the union
fired. It could not say how many anchors it added, and the difference between
"it fired" and "it added thirteen" is the entire lesson of the last two days.
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

    check("an absent key counts zero, not None", lk._size({}, "markers") == 0)
    check("an empty list counts zero", lk._size({"markers": []}, "markers") == 0)
    check("a dict counts its keys",
          lk._size({"ground": {"b0": 1, "b1": 2}}, "ground") == 2)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        def w(name, data):
            p = tmp / name
            p.write_text(json.dumps(data), encoding="utf-8")
            return p

        site = w("site.json", {
            "markers": [{"id": "F", "name": "b0/F", "type": "spawn"},
                        {"id": "VAULT", "name": "b0/VAULT", "type": "vault"}],
            "surfaces": [{"node": "b0/c0"}, {"node": "b0/c1"}],
            "ground": {"b0": {"source": "a.glb"}},
            "openings": [{"kind": "door"}]})
        deli = w("deli.json", {
            "stair_systems": [{"id": "s1"}],
            "markers": [{"id": "VAULT", "type": "vault"},
                        {"id": "CREW_SPAWN_A", "type": "crew"},
                        {"id": "RESPONDER_SPAWN_1", "type": "responder"}],
            "surfaces": [{"node": "b0/int_col_-1_0"}]})

        lock = lk.compute_lock(mission_id="m1",
                               candidate_id="m1.candidate.seed_1", seed=1,
                               site_gameplay_path=site,
                               deli_gameplay_path=deli)
        cov = lock.coverage
        check("the lock carries both counts",
              "counts" in cov and "site_counts" in cov)
        check("THE UNION IS A SUBTRACTION A READER CAN DO",
              cov["counts"]["markers"] - cov["site_counts"]["markers"] == 2)
        check("and the merged count is what the registry hashes",
              cov["counts"]["markers"]
              == len(lk._anchor_registry(lk._merged_gameplay(site, deli))))
        check("a key that is NOT unioned shows no difference",
              cov["counts"]["surfaces"] == cov["site_counts"]["surfaces"] == 2)
        check("even though deli published one the site did not",
              lk._size(json.loads(deli.read_text(encoding="utf-8")),
                       "surfaces") == 1)
        check("a backfilled key counts from the merged view",
              cov["counts"]["stair_systems"] == 1
              and cov["site_counts"]["stair_systems"] == 0)
        check("ground counts its buildings", cov["counts"]["ground"] == 1)
        check("every protected key is counted",
              set(cov["counts"]) ==
              {k for keys in lk.PROTECTED_KEYS.values() for k in keys})

        # The case that started all this: a signature that says guarding=True
        # while carrying almost nothing is now visible as a number.
        thin_site = w("thin.json", {"buildings": [1]})
        thin = lk.compute_lock(mission_id="m2",
                               candidate_id="m2.candidate.seed_1", seed=1,
                               site_gameplay_path=thin_site,
                               deli_gameplay_path=deli)
        tc = thin.coverage
        check("A SIGNATURE CARRYING ALMOST NOTHING NOW SAYS SO",
              tc["signatures"]["collision_fingerprint"]["guarding"] is True
              and sum(tc["counts"][k] for k in
                      lk.PROTECTED_KEYS["collision_fingerprint"]) == 1)
        check("which is the reading that would have found this in a minute",
              tc["counts"]["stair_systems"] == 1
              and tc["counts"]["surfaces"] == 0)

    check("enforcement is still off, and this release does not flip it",
          lk.LOCK_COVERAGE_ENFORCED is False)

    v = (root / VERSION_F).read_text(encoding="utf-8")
    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    flat = " ".join(cl.split())
    check(f"VERSION is {NEW_V}", NEW_V in v)
    check(f"one {NEW_V} entry", cl.count(f"## [{NEW_V}]") == 1)
    check("the entry says what the hashes alone could not",
          "it fired" in flat and "added thirteen" in flat)
    check("and names the case that hid",
          "two Deli stair systems" in flat)

    print()
    print("  a signature that empties out is now a number, not a probe run"
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
        for rel in (LOCK, VERSION_F, CHANGELOG):
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
        print("    python patches\\patch_lf_031.py --selftest")
        print("    python -m pytest level_factory/tests/unit -q")
        print()
        print("  THEN RECOMPUTE AND READ THE NUMBER:")
        print("    python -m level_factory -C workspaces\\lot-demo-ws \\")
        print("        approve lot_demo_001 functional_shell_locked")
        print("    python -c \"import json;c=json.load(open("
              r"r'workspaces\lot-demo-ws\.level_factory\locks"
              "\\lot_demo_001.json'))['coverage'];"
              "print(c['counts']);print(c['site_counts'])\"")
        print()
        print("  counts.markers - site_counts.markers should be 13.")
        print("  Paste it; the flip goes in THIS release, before the commit.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
