r"""The probes stop keeping their own copy of what the lock protects.

    python patch_probes_ask_the_code.py --check
    python patch_probes_ask_the_code.py
    python patch_probes_ask_the_code.py --selftest
    python patch_probes_ask_the_code.py --revert

Run from the FACTORY ROOT. Replaces two files in tools/ wholesale, refusing
if either has changed since this was written -- the sha256 of each is pinned
below, so an edit made by hand is not silently clobbered.

WHY

`probe_selection_drift.py` crashed:

    AttributeError: module 'packages.approvals.lock' has no attribute
    '_route_graph'

It hardcoded three signature names -- including `route_graph_hash` -- and
called `lock._route_graph` directly. 0.29.0 retired both. It also carried its
own copy of the ten key names in a `READS` table and its own
`BACKFILLED_FROM_DELI` set, and 0.29.0 changed both sets.

A duplicated list that drifted from its source is the exact defect this probe
was written to find. It found it in `lock.py` and then had it.

`probe_site_vocabulary.py` had the same flaw: a module-level `PROTECTED`
tuple of ten hardcoded names. After 0.29.0 it would have reported the wrong
set with no error at all -- worse than the crash, because a crash gets fixed.

WHAT CHANGES

Both now read `packages.approvals.lock.PROTECTED_KEYS` and
`BACKFILLED_FROM_DELI` at run time.

`probe_selection_drift.signatures()` goes through `compute_lock` rather than
calling the private signature helpers, so retiring or adding a signature
needs no edit here at all. Its selftest asserts the names come from the
module rather than asserting what they are, and adds the case 0.29.0
promised: rewriting a material must not move the signatures.

`probe_site_vocabulary` prints how many keys the extraction reads and names
them, instead of asserting "ten" in its own prose -- which was wrong anyway
when it said eleven.

Both also gained something the crash made obvious: the drift probe now prints
the lock's schema against the current one, and says STALE when they differ.
That is the state every lock was in an hour ago, and the probe could not see
it.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

SIDECAR = ".pre_askthecode"

DRIFT_SRC = 'r"""Measure what the post-art functional-regression gate is comparing.\n\n    python tools\\probe_selection_drift.py -C workspaces\\lot-demo-ws lot_demo_001\n    python tools\\probe_selection_drift.py --selftest\n\nREAD-ONLY. It opens files, imports level_factory\'s own lock module so the\nsignatures are computed by the same code the gate uses, and writes nothing.\n\nWHY THIS EXISTS\n\n`cmd_approve` writes `--candidate` to\n`.level_factory/approvals/<mission>.selected` verbatim, with nothing checking\nit. For `lot_demo_001` that file holds the literal template\n`lot_demo_001.candidate.seed_XXXX`. Everything downstream derives a job\ndirectory from that string:\n\n    _resolve_selected_candidate  -> "lot_demo_001.candidate.seed_XXXX"\n    _selected_lot_out            -> jobs/<m>.lot_assemble.candidate.seed_XXXX/out\n\nwhich does not exist. So `graybox_dir` in `cmd_export` is a dead path, and\n`verify_no_drift` is handed a `site.site.gameplay.json` that is not there.\n\nTHE QUESTION THIS ANSWERS, AND THE ONE IT DOES NOT\n\n`_merged_gameplay` fills four of its six collision keys from the Deli side\nvia `setdefault`, and takes `anchors` from Deli when the site has none. So a\nmissing site file does not necessarily change the three hashes the gate\ncompares -- it depends entirely on what the site file contributes that Deli\ndoes not. If it contributes nothing, the gate has been passing on an absence\nand would pass on anything.\n\nThat is measurable, and this measures it. It does NOT decide what to do about\nit: whether the marker gets repaired, whether `_selected_lot_out` should\nprefer the functional lock, and whether a job path should be validated at\napproval time are three separate decisions with three different blast\nradii, and a probe should not make any of them.\n\nEXIT CODES\n\n    0  the gate is comparing real signatures\n    2  the gate is comparing an absence -- it would pass on anything\n    1  could not measure (files missing, no lock, no workspace)\n"""\nfrom __future__ import annotations\n\nimport json\nimport sys\nfrom pathlib import Path\n\n\ndef factory_root(start: Path) -> Path | None:\n    for d in [start] + list(start.parents):\n        if (d / "factory.manifest.json").is_file():\n            return d\n    return None\n\n\ndef _load_lock_module(root: Path):\n    lf = str((root / "level_factory").resolve())\n    if lf not in sys.path:\n        sys.path.insert(0, lf)\n    import importlib\n    return (importlib.import_module("packages.approvals.lock"),\n            importlib.import_module("packages.core.hashing"))\n\n\ndef signature_names(lock_mod) -> tuple:\n    """The signature fields, FROM THE MODULE. Never a second copy.\n\n    The first version of this probe hardcoded three names including\n    `route_graph_hash`, and called `lock._route_graph` directly. 0.29.0\n    retired both and this crashed with AttributeError -- a duplicated list\n    that drifted from its source, which is the defect this probe exists to\n    find. It now asks.\n    """\n    return tuple(sorted(lock_mod.PROTECTED_KEYS))\n\n\ndef signatures(lock_mod, hashing, site: Path, deli: Path | None):\n    """The protected signatures for these two files, via compute_lock.\n\n    Through the real entry point rather than the private helpers, so this\n    cannot drift from what a real lock would contain, and so retiring or\n    adding a signature needs no edit here.\n    """\n    import contextlib\n    import io\n    with contextlib.redirect_stderr(io.StringIO()):\n        lk = lock_mod.compute_lock(\n            mission_id="_probe", candidate_id="_probe.candidate.seed_0",\n            seed=0, site_gameplay_path=site, deli_gameplay_path=deli)\n    return tuple(getattr(lk, n) for n in signature_names(lock_mod))\n\n\n\n\ndef _row(label: str, value) -> None:\n    print(f"  {label:<34} {value}")\n\n\ndef probe(ws: Path, mission: str) -> int:\n    root = factory_root(Path(__file__).resolve().parent)\n    if root is None:\n        print("could not find factory.manifest.json above this script")\n        return 1\n    lock_mod, hashing = _load_lock_module(root)\n\n    internal = ws / ".level_factory"\n    jobs = internal / "jobs"\n    marker_p = internal / "approvals" / f"{mission}.selected"\n    lock_p = internal / "locks" / f"{mission}.json"\n\n    if not lock_p.is_file():\n        print(f"no functional lock at {lock_p}; nothing to compare against")\n        return 1\n    lock = json.loads(lock_p.read_text(encoding="utf-8"))\n    marker = (marker_p.read_text(encoding="utf-8").strip()\n              if marker_p.is_file() else None)\n\n    print("SELECTION")\n    _row("marker (.selected)", marker or "(absent)")\n    _row("lock candidate_id", lock.get("candidate_id"))\n    _row("lock seed", lock.get("seed"))\n    agree = marker == lock.get("candidate_id")\n    _row("they agree", agree)\n    _row("lock schema", lock.get("schema"))\n    _row("  current", getattr(lock_mod, "SCHEMA", "(pre-0.29.0)"))\n    if lock.get("schema") != getattr(lock_mod, "SCHEMA", None):\n        _row("  ", "STALE -- recompute with approve --gate functional_shell_locked")\n    print()\n\n    def out_dirs(cand: str | None):\n        """(site gameplay, deli gameplay) as the code derives them."""\n        if not cand:\n            return None, None\n        tail = cand.rsplit("_", 1)[-1]\n        return (jobs / f"{mission}.lot_assemble.candidate.seed_{tail}" / "out"\n                / "site.site.gameplay.json",\n                jobs / f"{mission}.deli_generate.candidate.seed_{tail}" / "out"\n                / "shell.gameplay.json")\n\n    # What the code resolves TODAY: the site from the marker, the deli from\n    # the lock\'s seed -- cmd_export reads `seed = lock.seed` for the deli path\n    # and `_selected_lot_out` reads the marker for the site path. They can\n    # disagree, and here they do.\n    marker_site, _ = out_dirs(marker)\n    lock_site, lock_deli = out_dirs(lock.get("candidate_id"))\n    deli_as_run = (jobs / f"{mission}.deli_generate.candidate.seed_"\n                   f"{lock.get(\'seed\')}" / "out" / "shell.gameplay.json")\n\n    print("PATHS")\n    _row("site, as the gate resolves it", marker_site)\n    _row("  exists", marker_site.is_file() if marker_site else None)\n    _row("site, from the lock", lock_site)\n    _row("  exists", lock_site.is_file() if lock_site else None)\n    _row("deli, as the gate resolves it", deli_as_run)\n    _row("  exists", deli_as_run.is_file())\n    print()\n\n    if lock_site is None or not lock_site.is_file():\n        print("the lock\'s own site file is missing too; cannot measure what "\n              "the site contributes")\n        return 1\n\n    # WHY, not just WHETHER. "the site contributes nothing" is a symptom;\n    # the cause is which keys the extraction reads against which keys the\n    # file publishes, and only one of those two lists is in the source.\n    def _keys(p: Path) -> dict:\n        try:\n            d = json.loads(p.read_text(encoding="utf-8"))\n        except (OSError, ValueError):\n            return {}\n        return d if isinstance(d, dict) else {}\n\n    site_d, deli_d = _keys(lock_site), _keys(deli_as_run)\n    READS = {k: tuple(v) for k, v in lock_mod.PROTECTED_KEYS.items()}\n    BACKFILLED = set(lock_mod.BACKFILLED_FROM_DELI)\n\n    def _shape(d: dict, k: str) -> str:\n        if k not in d:\n            return "-"\n        v = d[k]\n        if isinstance(v, (list, dict)):\n            return f"{type(v).__name__}[{len(v)}]"\n        return type(v).__name__\n\n    print("WHAT THE EXTRACTION READS, AND WHAT THE FILES PUBLISH")\n    print(f"  {\'key\':<20} {\'in site\':<12} {\'in deli\':<12} note")\n    for fn, keys in READS.items():\n        print(f"  -- {fn}")\n        for k in keys:\n            note = ("deli backfills this when site omits it"\n                    if k in BACKFILLED else "SITE-ONLY: nothing else supplies it")\n            print(f"  {k:<20} {_shape(site_d, k):<12} "\n                  f"{_shape(deli_d, k):<12} {note}")\n    unread = sorted(set(site_d) - {k for ks in READS.values() for k in ks})\n    print()\n    print(f"  the site file publishes {len(site_d)} top-level keys; "\n          f"{len(unread)} of them are read by nothing here:")\n    print("   ", ", ".join(unread[:24]) or "(none)")\n    if len(unread) > 24:\n        print(f"    ... and {len(unread) - 24} more")\n    print()\n\n    names = signature_names(lock_mod)\n    stored = tuple(lock.get(n) for n in names)\n    missing = Path(str(lock_site) + ".does-not-exist")\n\n    as_run = signatures(lock_mod, hashing, marker_site or missing, deli_as_run)\n    with_site = signatures(lock_mod, hashing, lock_site, deli_as_run)\n    without_site = signatures(lock_mod, hashing, missing, deli_as_run)\n\n    print("SIGNATURES  (stored / as the gate runs today / with the real site)")\n    for i, n in enumerate(names):\n        print(f"  {n}")\n        _row("    stored in the lock", str(stored[i])[:24])\n        _row("    as run today", str(as_run[i])[:24])\n        _row("    with the real site", str(with_site[i])[:24])\n        _row("    with NO site at all", str(without_site[i])[:24])\n    print()\n\n    passes = as_run == stored\n    site_matters = with_site != without_site\n    lock_made_without_site = stored == without_site\n\n    print("VERDICT")\n    _row("the gate passes today", passes)\n    _row("the site file changes the signatures", site_matters)\n    _row("the lock itself was computed w/o site", lock_made_without_site)\n    print()\n\n    if not site_matters:\n        print("  THE GATE IS COMPARING AN ABSENCE. Every signature it")\n        print("  protects is filled from the Deli side; the site file")\n        print("  contributes nothing to any of the three. It would pass")\n        print("  whether or not the site exists, which means it has not been")\n        print("  guarding the assembled site at all.")\n        return 2\n    if passes and not marker_site.is_file():\n        print("  THE GATE PASSES WHILE READING A FILE THAT IS NOT THERE, and")\n        print("  the site DOES affect the signatures -- so the lock it is")\n        print("  comparing against was computed from the same absence.")\n        return 2\n    if passes:\n        print("  The gate is comparing real signatures and they match.")\n        return 0\n    print("  The gate would BLOCK: the signatures it computes today differ")\n    print("  from the lock. That is a real drift report, not a plumbing bug.")\n    return 0\n\n\ndef selftest() -> int:\n    import json\n    import tempfile\n    bad = 0\n\n    def check(label: str, ok: bool) -> None:\n        nonlocal bad\n        bad += 0 if ok else 1\n        print(f"  {\'ok  \' if ok else \'FAIL\'} {label}")\n\n    root = factory_root(Path(__file__).resolve().parent)\n    if root is None:\n        print("run this from inside a factory checkout")\n        return 1\n    lock_mod, hashing = _load_lock_module(root)\n\n    names = signature_names(lock_mod)\n    check("the signature names come from the module, not a copy here",\n          names == tuple(sorted(lock_mod.PROTECTED_KEYS)))\n    check("and every one is a real field on a lock",\n          all(hasattr(lock_mod.FunctionalLock(\n              mission_id="m", candidate_id="c", seed=0), n) for n in names))\n\n    with tempfile.TemporaryDirectory() as td:\n        tmp = Path(td)\n\n        def w(name, data):\n            p = tmp / name\n            p.write_text(json.dumps(data), encoding="utf-8")\n            return p\n\n        deli = w("deli.json", {"stair_systems": [{"id": "s1"}]})\n        # A site in Lot\'s vocabulary that the CURRENT extraction reads.\n        site_real = w("site_real.json", {\n            "surfaces": [{"node": "b0/col0", "material": {"id": "glass"}}],\n            "ground": {"b0": {"source": "a.glb"}}})\n        # A site publishing only keys nothing reads.\n        site_inert = w("site_inert.json", {"buildings": [1], "zones": [2]})\n        gone = tmp / "not-here.json"\n\n        a = signatures(lock_mod, hashing, site_real, deli)\n        b = signatures(lock_mod, hashing, gone, deli)\n        check("a site the extraction reads changes the signatures", a != b)\n\n        c = signatures(lock_mod, hashing, site_inert, deli)\n        check("a site publishing only unread keys does not", c == b)\n        check("which is exactly the case this probe exists to detect",\n              c == b and a != b)\n\n        # Materials churn must not move them -- 0.29.0\'s promise.\n        arted = w("arted.json", {\n            "surfaces": [{"node": "b0/col0", "material": {"id": "rust"}}],\n            "ground": {"b0": {"source": "a.glb"}}})\n        check("rewriting a material does not move the signatures",\n              signatures(lock_mod, hashing, arted, deli) == a)\n\n    print()\n    print("  the probe asks the code what it protects, and can tell "\n          "a real guard from a vacuous one" if not bad\n          else f"  {bad} FAILURE(S)")\n    return 1 if bad else 0\n\n\ndef main(argv: list[str]) -> int:\n    if "--selftest" in argv:\n        return selftest()\n    ws = Path(".")\n    rest = []\n    i = 0\n    while i < len(argv):\n        if argv[i] in ("-C", "--chdir"):\n            ws = Path(argv[i + 1])\n            i += 2\n            continue\n        rest.append(argv[i])\n        i += 1\n    if not rest:\n        print(__doc__.strip().splitlines()[2])\n        return 1\n    if not (ws / ".level_factory").is_dir():\n        print(f"no .level_factory under {ws}; is that a workspace?")\n        return 1\n    return probe(ws.resolve(), rest[0])\n\n\nif __name__ == "__main__":\n    raise SystemExit(main(sys.argv[1:]))\n'

VOCAB_SRC = 'r"""What Lot\'s site gameplay file actually publishes, and where.\n\n    python tools\\probe_site_vocabulary.py -C workspaces\\lot-demo-ws lot_demo_001\n    python tools\\probe_site_vocabulary.py --selftest\n\nREAD-ONLY. Opens two json files, prints their shape, writes nothing.\n\nWHY\n\n`tools/probe_selection_drift.py` established that the functional lock guards\nnothing because `_merged_gameplay` reads ten key names that\n`site.site.gameplay.json` does not publish at its top level. Repairing that\nneeds to know what Lot publishes INSTEAD, and this answers it before anyone\nwrites a mapping.\n\nTHE QUESTION THAT DECIDES THE SHAPE OF THE FIX\n\nThere are two very different possibilities and they want different repairs:\n\n  1. RENAME. Lot publishes the same things under different top-level names --\n     `collision` is the hull list, `openings` is the doorways. Then the fix\n     is an alias table and it is small.\n\n  2. EXTRACTION. Lot publishes them NESTED -- doorways per building under\n     `buildings[]`, anchors under `site_markers[]` -- so there is no\n     top-level key to alias and the fix has to walk and gather. Then a naive\n     alias table would hash a container and call it a signature.\n\nSo this does three things: an inventory of every top-level key, a DEEP search\nfor the ten protected names at any depth, and the shape of the five keys that\nlook like candidates. The deep search is the one that decides between the two,\nand it is the reason this is not just `keys()`.\n\nWHAT IT DOES NOT DO\n\nIt does not propose a mapping. Two keys having the same shape is not evidence\nthey mean the same thing, and the whole failure being repaired here came from\na signature that looked healthy.\n"""\nfrom __future__ import annotations\n\nimport json\nimport sys\nfrom pathlib import Path\n\n#: Filled from `packages.approvals.lock.PROTECTED_KEYS` at run time, never\n#: copied. The first version of this file hardcoded ten names; 0.29.0 changed\n#: the set and a hardcoded copy would have quietly measured the wrong thing --\n#: the exact defect these probes were written to find.\nPROTECTED: tuple = ()\n\nMAX_MEMBER_KEYS = 14\nMAX_HITS = 12\n\n\ndef load_protected(root: Path) -> tuple:\n    """The protected key names, from the lock module itself."""\n    global PROTECTED\n    lf = str((root / "level_factory").resolve())\n    if lf not in sys.path:\n        sys.path.insert(0, lf)\n    import importlib\n    lk = importlib.import_module("packages.approvals.lock")\n    importlib.reload(lk)\n    PROTECTED = tuple(sorted({k for keys in lk.PROTECTED_KEYS.values()\n                              for k in keys}))\n    return PROTECTED\n\n\ndef factory_root(start: Path) -> Path | None:\n    for d in [start] + list(start.parents):\n        if (d / "factory.manifest.json").is_file():\n            return d\n    return None\n\n\ndef shape(v, depth: int = 0) -> str:\n    """A one-line description of a value: type, size, and member keys."""\n    if isinstance(v, dict):\n        ks = sorted(v)\n        shown = ", ".join(ks[:MAX_MEMBER_KEYS])\n        more = f" +{len(ks) - MAX_MEMBER_KEYS}" if len(ks) > MAX_MEMBER_KEYS else ""\n        return f"dict[{len(ks)}] {{{shown}{more}}}"\n    if isinstance(v, list):\n        if not v:\n            return "list[0]"\n        kinds = {type(x).__name__ for x in v}\n        if kinds == {"dict"}:\n            union: set = set()\n            for x in v[:200]:\n                union |= set(x)\n            ks = sorted(union)\n            shown = ", ".join(ks[:MAX_MEMBER_KEYS])\n            more = (f" +{len(ks) - MAX_MEMBER_KEYS}"\n                    if len(ks) > MAX_MEMBER_KEYS else "")\n            return f"list[{len(v)}] of dict {{{shown}{more}}}"\n        return f"list[{len(v)}] of {\'/\'.join(sorted(kinds))}"\n    if isinstance(v, str):\n        return f"str({len(v)}) {v[:40]!r}"\n    return f"{type(v).__name__} {v!r}"[:80]\n\n\ndef walk(node, path: str = "", depth: int = 0, max_depth: int = 6):\n    """Yield (path, key, value) for every dict key in the tree."""\n    if depth > max_depth:\n        return\n    if isinstance(node, dict):\n        for k, v in node.items():\n            here = f"{path}.{k}" if path else k\n            yield here, k, v\n            yield from walk(v, here, depth + 1, max_depth)\n    elif isinstance(node, list):\n        # One representative element: a list of 300 buildings has one shape,\n        # and printing 300 identical paths buries the answer.\n        for i, v in enumerate(node[:1]):\n            here = f"{path}[]"\n            yield from walk(v, here, depth + 1, max_depth)\n\n\ndef report(site: dict, deli: dict) -> int:\n    print(f"THE EXTRACTION READS {len(PROTECTED)} KEY(S), "\n          f"read from the lock module: {\', \'.join(PROTECTED)}")\n    print()\n    print("TOP-LEVEL KEYS IN THE SITE FILE")\n    read = set(PROTECTED)\n    for k in sorted(site):\n        mark = "READ" if k in read else "    "\n        print(f"  {mark} {k:<18} {shape(site[k])}")\n    print()\n\n    print("TOP-LEVEL KEYS IN THE DELI FILE")\n    for k in sorted(deli):\n        mark = "READ" if k in read else "    "\n        print(f"  {mark} {k:<18} {shape(deli[k])}")\n    print()\n\n    # THE QUESTION THAT DECIDES THE FIX.\n    print(f"THE {len(PROTECTED)} PROTECTED NAMES, ANYWHERE IN THE SITE TREE")\n    found: dict[str, list[tuple[str, str]]] = {n: [] for n in PROTECTED}\n    for path, key, value in walk(site):\n        if key in found:\n            found[key].append((path, shape(value)))\n    any_nested = False\n    for name in PROTECTED:\n        hits = found[name]\n        if not hits:\n            print(f"  {name:<18} absent at every depth")\n            continue\n        top = [h for h in hits if h[0] == name]\n        nested = [h for h in hits if h[0] != name]\n        if nested:\n            any_nested = True\n        print(f"  {name:<18} {len(hits)} hit(s)"\n              f"{\' (TOP-LEVEL)\' if top else \'\'}"\n              f"{\' (NESTED)\' if nested else \'\'}")\n        for path, sh in hits[:MAX_HITS]:\n            print(f"      {path}  ->  {sh}")\n        if len(hits) > MAX_HITS:\n            print(f"      ... and {len(hits) - MAX_HITS} more")\n    print()\n\n    print("VERDICT")\n    if any_nested:\n        print("  AT LEAST ONE PROTECTED NAME EXISTS NESTED. The repair is an")\n        print("  EXTRACTION, not an alias table -- something has to walk and")\n        print("  gather. An alias mapping a top-level container onto a")\n        print("  signature would hash the container and look healthy.")\n        rc = 2\n    else:\n        print("  NO protected name appears anywhere in the site tree. Lot")\n        print("  publishes these concepts under different names entirely, or")\n        print("  does not publish them. Read the candidate shapes below")\n        print("  against the Deli shapes above before proposing any pairing.")\n        rc = 0\n    print()\n\n    print("THE CANDIDATE KEYS, IN FULL SHAPE")\n    print("  (looking like a match is not evidence of being one)")\n    for k in ("collision", "openings", "vertical_links", "markers",\n              "site_markers", "rooms", "surfaces", "ground"):\n        if k not in site:\n            continue\n        print(f"  -- {k}")\n        print(f"     {shape(site[k])}")\n        v = site[k]\n        sample = None\n        if isinstance(v, list) and v:\n            sample = v[0]\n        elif isinstance(v, dict) and v:\n            first = sorted(v)[0]\n            sample = {first: v[first]}\n        if sample is not None:\n            txt = json.dumps(sample, indent=6, sort_keys=True)[:900]\n            print("     first element:")\n            for line in txt.splitlines()[:26]:\n                print(f"     {line}")\n            if len(txt) >= 900:\n                print("     ... truncated")\n    return rc\n\n\ndef probe(ws: Path, mission: str, root: Path) -> int:\n    load_protected(root)\n    internal = ws / ".level_factory"\n    lock_p = internal / "locks" / f"{mission}.json"\n    if not lock_p.is_file():\n        print(f"no functional lock at {lock_p}")\n        return 1\n    lock = json.loads(lock_p.read_text(encoding="utf-8"))\n    # From the LOCK, never the marker: the marker is the corrupt one.\n    seed = lock.get("seed")\n    site_p = (internal / "jobs"\n              / f"{mission}.lot_assemble.candidate.seed_{seed}" / "out"\n              / "site.site.gameplay.json")\n    deli_p = (internal / "jobs"\n              / f"{mission}.deli_generate.candidate.seed_{seed}" / "out"\n              / "shell.gameplay.json")\n    for p in (site_p, deli_p):\n        if not p.is_file():\n            print(f"missing {p}")\n            return 1\n    print(f"site: {site_p}")\n    print(f"deli: {deli_p}")\n    print()\n    return report(json.loads(site_p.read_text(encoding="utf-8")),\n                  json.loads(deli_p.read_text(encoding="utf-8")))\n\n\ndef selftest() -> int:\n    bad = 0\n\n    def check(label: str, ok: bool) -> None:\n        nonlocal bad\n        bad += 0 if ok else 1\n        print(f"  {\'ok  \' if ok else \'FAIL\'} {label}")\n\n    root = factory_root(Path(__file__).resolve().parent)\n    if root is None:\n        print("run this from inside a factory checkout")\n        return 1\n    names = load_protected(root)\n    check("the protected names are read from the lock module",\n          bool(names))\n    import importlib\n    lk = importlib.import_module("packages.approvals.lock")\n    check("and are exactly the union of its signatures",\n          set(names) == {k for keys in lk.PROTECTED_KEYS.values()\n                         for k in keys})\n\n    live = names[0]\n    nested = {"buildings": [{"id": "b1", live: [{"id": "d"}]}],\n              "collision": [{"hull": 1}]}\n    hits = {k for _p, k, _v in walk(nested)}\n    check("the deep walk finds a nested protected name", live in hits)\n    paths = {p for p, k, _v in walk(nested) if k == live}\n    check("and reports where it lives", paths == {f"buildings[].{live}"})\n\n    flat = {"buildings": [{"id": "b1"}], "collision": [{"hull": 1}]}\n    check("and finds nothing when there is nothing",\n          not ({k for _p, k, _v in walk(flat)} & set(PROTECTED)))\n\n    check("shape names a list of dicts by its member keys",\n          shape([{"a": 1, "b": 2}]) == "list[1] of dict {a, b}")\n    check("and distinguishes an empty list from an absent key",\n          shape([]) == "list[0]")\n\n    print()\n    print("  the walk can tell a rename from an extraction"\n          if not bad else f"  {bad} FAILURE(S)")\n    return 1 if bad else 0\n\n\ndef main(argv: list[str]) -> int:\n    if "--selftest" in argv:\n        return selftest()\n    ws = Path(".")\n    rest = []\n    i = 0\n    while i < len(argv):\n        if argv[i] in ("-C", "--chdir"):\n            ws = Path(argv[i + 1])\n            i += 2\n            continue\n        rest.append(argv[i])\n        i += 1\n    if not rest:\n        print("usage: probe_site_vocabulary.py -C <workspace> <mission_id>")\n        return 1\n    if not (ws / ".level_factory").is_dir():\n        print(f"no .level_factory under {ws}; is that a workspace?")\n        return 1\n    root = factory_root(Path(__file__).resolve().parent)\n    if root is None:\n        print("could not find factory.manifest.json above this script")\n        return 1\n    return probe(ws.resolve(), rest[0], root)\n\n\nif __name__ == "__main__":\n    raise SystemExit(main(sys.argv[1:]))\n'


#: sha256 of each file as this patch expects to find it. A mismatch means
#: somebody edited it and this refuses rather than overwriting the edit.
EXPECT = {
    "tools/probe_selection_drift.py":
        "40359329c2ff374ab3ed1a961e5a2b5d1c217fa56569a1fe0c23107071e3c3ff",
    "tools/probe_site_vocabulary.py":
        "5a94f0d2b9aab21022fd06e1b655b3045d1a47ba601c8a84d162e87b48049ac0",
}

NEW: dict[str, str] = {
    "tools/probe_selection_drift.py": DRIFT_SRC,
    "tools/probe_site_vocabulary.py": VOCAB_SRC,
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
    for rel, want in EXPECT.items():
        p = root / rel
        if not p.is_file():
            print(f"REFUSING: {rel} is not here")
            return 1
        cur = _sha(p.read_bytes())
        new = NEW[rel].encode("utf-8")
        if cur == _sha(new):
            print(f"  already applied  {rel}")
            continue
        if cur != want:
            print(f"REFUSING: {rel} is not the version this patch expects.")
            print(f"    on disk  {cur[:16]}")
            print(f"    expected {want[:16]}")
            print("  Somebody edited it; merge by hand rather than lose that.")
            return 1
        try:
            compile(NEW[rel], str(p), "exec")
        except SyntaxError as exc:
            print(f"REFUSING: the replacement for {rel} does not parse: {exc}")
            return 1
        if check:
            print(f"  would replace  {rel}  {p.stat().st_size:,} -> "
                  f"{len(new):,} bytes ({len(new) - p.stat().st_size:+,})")
            continue
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(p.read_bytes())
        p.write_bytes(new)
        print(f"  replaced      {rel}  {len(new):,} bytes  "
              f"sha256 {_sha(new)[:16]}")
    return 0


def selftest(root: Path) -> int:
    import importlib
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

    # BEHAVIOUR, NOT PROSE. The first cut of these checks forbade the string
    # "_route_graph" anywhere, and failed on the comment that explains why it
    # is gone -- punishing the file for documenting its own history. What
    # matters is that nothing CALLS it.
    for rel in NEW:
        src = (root / rel).read_text(encoding="utf-8")
        check(f"{rel.split('/')[-1]} calls no retired helper",
              "_route_graph(" not in src.replace("`lock._route_graph` ", ""))
        check(f"{rel.split('/')[-1]} reads PROTECTED_KEYS from the module",
              "PROTECTED_KEYS" in src)

    drift = (root / "tools" / "probe_selection_drift.py").read_text(
        encoding="utf-8")
    check("the drift probe keeps no copy of the signature names",
          "_NAMES = (" not in drift
          and "def signature_names(lock_mod)" in drift)
    check("and goes through compute_lock, not the private helpers",
          "lock_mod.compute_lock(" in drift
          and "lock_mod._collision_signature(" not in drift)
    check("and reports a stale lock schema",
          "STALE -- recompute" in drift)

    vocab = (root / "tools" / "probe_site_vocabulary.py").read_text(
        encoding="utf-8")
    check("the vocabulary probe fills PROTECTED at run time",
          "def load_protected(" in vocab
          and 'PROTECTED: tuple = ()' in vocab)
    # The list is EMPTY until load_protected fills it, which is what makes a
    # stale copy impossible. Checking that beats checking the prose.
    ns: dict = {}
    for line in vocab.splitlines():
        if line.startswith("PROTECTED"):
            exec(line, ns)
            break
    check("and starts with no names of its own",
          ns.get("PROTECTED") == ())

    # Run both selftests for real.
    import subprocess
    for rel in NEW:
        r = subprocess.run([sys.executable, str(root / rel), "--selftest"],
                           cwd=str(root), capture_output=True, text=True)
        check(f"{rel.split('/')[-1]} --selftest passes",
              r.returncode == 0)
        if r.returncode:
            print((r.stdout + r.stderr)[-700:])

    print()
    print("  the probes ask the code what it protects"
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
        for rel in NEW:
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
        print("    python patches\\patch_probes_ask_the_code.py --selftest")
        print("    python tools\\probe_selection_drift.py "
              "-C workspaces\\lot-demo-ws lot_demo_001")
        print()
        print("  expect exit 0 and 'comparing real signatures and they match'")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
