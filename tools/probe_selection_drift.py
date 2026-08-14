r"""Measure what the post-art functional-regression gate is comparing.

    python tools\probe_selection_drift.py -C workspaces\lot-demo-ws lot_demo_001
    python tools\probe_selection_drift.py --selftest

READ-ONLY. It opens files, imports level_factory's own lock module so the
signatures are computed by the same code the gate uses, and writes nothing.

WHY THIS EXISTS

`cmd_approve` writes `--candidate` to
`.level_factory/approvals/<mission>.selected` verbatim, with nothing checking
it. For `lot_demo_001` that file holds the literal template
`lot_demo_001.candidate.seed_XXXX`. Everything downstream derives a job
directory from that string:

    _resolve_selected_candidate  -> "lot_demo_001.candidate.seed_XXXX"
    _selected_lot_out            -> jobs/<m>.lot_assemble.candidate.seed_XXXX/out

which does not exist. So `graybox_dir` in `cmd_export` is a dead path, and
`verify_no_drift` is handed a `site.site.gameplay.json` that is not there.

THE QUESTION THIS ANSWERS, AND THE ONE IT DOES NOT

`_merged_gameplay` fills four of its six collision keys from the Deli side
via `setdefault`, and takes `anchors` from Deli when the site has none. So a
missing site file does not necessarily change the three hashes the gate
compares -- it depends entirely on what the site file contributes that Deli
does not. If it contributes nothing, the gate has been passing on an absence
and would pass on anything.

That is measurable, and this measures it. It does NOT decide what to do about
it: whether the marker gets repaired, whether `_selected_lot_out` should
prefer the functional lock, and whether a job path should be validated at
approval time are three separate decisions with three different blast
radii, and a probe should not make any of them.

EXIT CODES

    0  the gate is comparing real signatures
    2  the gate is comparing an absence -- it would pass on anything
    1  could not measure (files missing, no lock, no workspace)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def factory_root(start: Path) -> Path | None:
    for d in [start] + list(start.parents):
        if (d / "factory.manifest.json").is_file():
            return d
    return None


def _load_lock_module(root: Path):
    lf = str((root / "level_factory").resolve())
    if lf not in sys.path:
        sys.path.insert(0, lf)
    import importlib
    return (importlib.import_module("packages.approvals.lock"),
            importlib.import_module("packages.core.hashing"))


def signature_names(lock_mod) -> tuple:
    """The signature fields, FROM THE MODULE. Never a second copy.

    The first version of this probe hardcoded three names including
    `route_graph_hash`, and called `lock._route_graph` directly. 0.29.0
    retired both and this crashed with AttributeError -- a duplicated list
    that drifted from its source, which is the defect this probe exists to
    find. It now asks.
    """
    return tuple(sorted(lock_mod.PROTECTED_KEYS))


def signatures(lock_mod, hashing, site: Path, deli: Path | None):
    """The protected signatures for these two files, via compute_lock.

    Through the real entry point rather than the private helpers, so this
    cannot drift from what a real lock would contain, and so retiring or
    adding a signature needs no edit here.
    """
    import contextlib
    import io
    with contextlib.redirect_stderr(io.StringIO()):
        lk = lock_mod.compute_lock(
            mission_id="_probe", candidate_id="_probe.candidate.seed_0",
            seed=0, site_gameplay_path=site, deli_gameplay_path=deli)
    return tuple(getattr(lk, n) for n in signature_names(lock_mod))




def _row(label: str, value) -> None:
    print(f"  {label:<34} {value}")


def probe(ws: Path, mission: str) -> int:
    root = factory_root(Path(__file__).resolve().parent)
    if root is None:
        print("could not find factory.manifest.json above this script")
        return 1
    lock_mod, hashing = _load_lock_module(root)

    internal = ws / ".level_factory"
    jobs = internal / "jobs"
    marker_p = internal / "approvals" / f"{mission}.selected"
    lock_p = internal / "locks" / f"{mission}.json"

    if not lock_p.is_file():
        print(f"no functional lock at {lock_p}; nothing to compare against")
        return 1
    lock = json.loads(lock_p.read_text(encoding="utf-8"))
    marker = (marker_p.read_text(encoding="utf-8").strip()
              if marker_p.is_file() else None)

    print("SELECTION")
    _row("marker (.selected)", marker or "(absent)")
    _row("lock candidate_id", lock.get("candidate_id"))
    _row("lock seed", lock.get("seed"))
    agree = marker == lock.get("candidate_id")
    _row("they agree", agree)
    _row("lock schema", lock.get("schema"))
    _row("  current", getattr(lock_mod, "SCHEMA", "(pre-0.29.0)"))
    if lock.get("schema") != getattr(lock_mod, "SCHEMA", None):
        _row("  ", "STALE -- recompute with approve --gate functional_shell_locked")
    print()

    def out_dirs(cand: str | None):
        """(site gameplay, deli gameplay) as the code derives them."""
        if not cand:
            return None, None
        tail = cand.rsplit("_", 1)[-1]
        return (jobs / f"{mission}.lot_assemble.candidate.seed_{tail}" / "out"
                / "site.site.gameplay.json",
                jobs / f"{mission}.deli_generate.candidate.seed_{tail}" / "out"
                / "shell.gameplay.json")

    # What the code resolves TODAY: the site from the marker, the deli from
    # the lock's seed -- cmd_export reads `seed = lock.seed` for the deli path
    # and `_selected_lot_out` reads the marker for the site path. They can
    # disagree, and here they do.
    marker_site, _ = out_dirs(marker)
    lock_site, lock_deli = out_dirs(lock.get("candidate_id"))
    deli_as_run = (jobs / f"{mission}.deli_generate.candidate.seed_"
                   f"{lock.get('seed')}" / "out" / "shell.gameplay.json")

    print("PATHS")
    _row("site, as the gate resolves it", marker_site)
    _row("  exists", marker_site.is_file() if marker_site else None)
    _row("site, from the lock", lock_site)
    _row("  exists", lock_site.is_file() if lock_site else None)
    _row("deli, as the gate resolves it", deli_as_run)
    _row("  exists", deli_as_run.is_file())
    print()

    if lock_site is None or not lock_site.is_file():
        print("the lock's own site file is missing too; cannot measure what "
              "the site contributes")
        return 1

    # WHY, not just WHETHER. "the site contributes nothing" is a symptom;
    # the cause is which keys the extraction reads against which keys the
    # file publishes, and only one of those two lists is in the source.
    def _keys(p: Path) -> dict:
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        return d if isinstance(d, dict) else {}

    site_d, deli_d = _keys(lock_site), _keys(deli_as_run)
    READS = {k: tuple(v) for k, v in lock_mod.PROTECTED_KEYS.items()}
    BACKFILLED = set(lock_mod.BACKFILLED_FROM_DELI)

    def _shape(d: dict, k: str) -> str:
        if k not in d:
            return "-"
        v = d[k]
        if isinstance(v, (list, dict)):
            return f"{type(v).__name__}[{len(v)}]"
        return type(v).__name__

    print("WHAT THE EXTRACTION READS, AND WHAT THE FILES PUBLISH")
    print(f"  {'key':<20} {'in site':<12} {'in deli':<12} note")
    for fn, keys in READS.items():
        print(f"  -- {fn}")
        for k in keys:
            note = ("deli backfills this when site omits it"
                    if k in BACKFILLED else "SITE-ONLY: nothing else supplies it")
            print(f"  {k:<20} {_shape(site_d, k):<12} "
                  f"{_shape(deli_d, k):<12} {note}")
    unread = sorted(set(site_d) - {k for ks in READS.values() for k in ks})
    print()
    print(f"  the site file publishes {len(site_d)} top-level keys; "
          f"{len(unread)} of them are read by nothing here:")
    print("   ", ", ".join(unread[:24]) or "(none)")
    if len(unread) > 24:
        print(f"    ... and {len(unread) - 24} more")
    print()

    names = signature_names(lock_mod)
    stored = tuple(lock.get(n) for n in names)
    missing = Path(str(lock_site) + ".does-not-exist")

    as_run = signatures(lock_mod, hashing, marker_site or missing, deli_as_run)
    with_site = signatures(lock_mod, hashing, lock_site, deli_as_run)
    without_site = signatures(lock_mod, hashing, missing, deli_as_run)

    print("SIGNATURES  (stored / as the gate runs today / with the real site)")
    for i, n in enumerate(names):
        print(f"  {n}")
        _row("    stored in the lock", str(stored[i])[:24])
        _row("    as run today", str(as_run[i])[:24])
        _row("    with the real site", str(with_site[i])[:24])
        _row("    with NO site at all", str(without_site[i])[:24])
    print()

    passes = as_run == stored
    site_matters = with_site != without_site
    lock_made_without_site = stored == without_site

    print("VERDICT")
    _row("the gate passes today", passes)
    _row("the site file changes the signatures", site_matters)
    _row("the lock itself was computed w/o site", lock_made_without_site)
    print()

    if not site_matters:
        print("  THE GATE IS COMPARING AN ABSENCE. Every signature it")
        print("  protects is filled from the Deli side; the site file")
        print("  contributes nothing to any of the three. It would pass")
        print("  whether or not the site exists, which means it has not been")
        print("  guarding the assembled site at all.")
        return 2
    if passes and not marker_site.is_file():
        print("  THE GATE PASSES WHILE READING A FILE THAT IS NOT THERE, and")
        print("  the site DOES affect the signatures -- so the lock it is")
        print("  comparing against was computed from the same absence.")
        return 2
    if passes:
        print("  The gate is comparing real signatures and they match.")
        return 0
    print("  The gate would BLOCK: the signatures it computes today differ")
    print("  from the lock. That is a real drift report, not a plumbing bug.")
    return 0


def selftest() -> int:
    import json
    import tempfile
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    root = factory_root(Path(__file__).resolve().parent)
    if root is None:
        print("run this from inside a factory checkout")
        return 1
    lock_mod, hashing = _load_lock_module(root)

    names = signature_names(lock_mod)
    check("the signature names come from the module, not a copy here",
          names == tuple(sorted(lock_mod.PROTECTED_KEYS)))
    check("and every one is a real field on a lock",
          all(hasattr(lock_mod.FunctionalLock(
              mission_id="m", candidate_id="c", seed=0), n) for n in names))

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        def w(name, data):
            p = tmp / name
            p.write_text(json.dumps(data), encoding="utf-8")
            return p

        deli = w("deli.json", {"stair_systems": [{"id": "s1"}]})
        # A site in Lot's vocabulary that the CURRENT extraction reads.
        site_real = w("site_real.json", {
            "surfaces": [{"node": "b0/col0", "material": {"id": "glass"}}],
            "ground": {"b0": {"source": "a.glb"}}})
        # A site publishing only keys nothing reads.
        site_inert = w("site_inert.json", {"buildings": [1], "zones": [2]})
        gone = tmp / "not-here.json"

        a = signatures(lock_mod, hashing, site_real, deli)
        b = signatures(lock_mod, hashing, gone, deli)
        check("a site the extraction reads changes the signatures", a != b)

        c = signatures(lock_mod, hashing, site_inert, deli)
        check("a site publishing only unread keys does not", c == b)
        check("which is exactly the case this probe exists to detect",
              c == b and a != b)

        # Materials churn must not move them -- 0.29.0's promise.
        arted = w("arted.json", {
            "surfaces": [{"node": "b0/col0", "material": {"id": "rust"}}],
            "ground": {"b0": {"source": "a.glb"}}})
        check("rewriting a material does not move the signatures",
              signatures(lock_mod, hashing, arted, deli) == a)

    print()
    print("  the probe asks the code what it protects, and can tell "
          "a real guard from a vacuous one" if not bad
          else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    ws = Path(".")
    rest = []
    i = 0
    while i < len(argv):
        if argv[i] in ("-C", "--chdir"):
            ws = Path(argv[i + 1])
            i += 2
            continue
        rest.append(argv[i])
        i += 1
    if not rest:
        print(__doc__.strip().splitlines()[2])
        return 1
    if not (ws / ".level_factory").is_dir():
        print(f"no .level_factory under {ws}; is that a workspace?")
        return 1
    return probe(ws.resolve(), rest[0])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
