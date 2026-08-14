r"""probe_site_vocabulary: does Lot's output contain Deli's?

    python patch_probe_overlap.py --check
    python patch_probe_overlap.py
    python patch_probe_overlap.py --selftest
    python patch_probe_overlap.py --revert

Run from the FACTORY ROOT. Replaces one file in tools/, refusing if it has
changed since this was written.

THE QUESTION

0.29.0 mapped the lock onto Lot's vocabulary and the probe then showed
something new: Deli publishes three of the same keys.

    openings    site list[76]     deli list[19]
    surfaces    site list[1029]   deli list[238]
    markers     site list[42]     deli list[14]

`_merged_gameplay` backfills only the four Deli-owned collision names. For
anything else both publish, the SITE's value wins outright and Deli's copy is
discarded. So the anchor registry hashes 42 markers and ignores 14, and the
collision fingerprint ignores 238 surfaces.

That is either correct -- Lot assembles the site from Deli's shells, so its
records supersede them and re-adding would double-count -- or it is a silent
omission from a signature, which is the failure this entire line of work has
been about. `coverage` cannot tell the difference: it measures whether the
site contributed, not whether anything was dropped.

It is a set-membership question, and this answers it.

HOW IT MATCHES

Per element, an identity: `name` first (Lot's namespaced form), then `node`,
then `building/id`, then the whole record when nothing identifies it. Deli's
identities are then checked three ways -- exact, by name-tail, and not at
all.

The name-tail pass is the one that matters. Lot namespaces Deli's ids when it
places a shell, so Deli's `VAULT` becomes `b0/VAULT`; an exact-match-only
report would call every one of them missing and be useless.

Records with no identifier at all -- `openings` are like this -- are compared
whole, and the output says so, because Lot transforms coordinates when it
places a shell and a low match there can mean transformed rather than
dropped. That distinction is not decidable from these two files alone, and
the report does not pretend otherwise.

IT REPORTS, IT DOES NOT DECIDE

A record with no match is either superseded by Lot or missing from a
signature, and which one it is is a contract question between two tool repos.
`LOCK_COVERAGE_ENFORCED` should not flip until it is answered: turning on a
gate over a registry that might be short a third of its anchors would bake in
exactly the quiet incompleteness the last four releases were spent removing.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

REL = "tools/probe_site_vocabulary.py"
SIDECAR = ".pre_overlap"
EXPECT = "c94012fb6a585eb2328ab9ca29a3f84fd81f67a1f6021ed885e769f491b3091b"

VOCAB_SRC = 'r"""What Lot\'s site gameplay file actually publishes, and where.\n\n    python tools\\probe_site_vocabulary.py -C workspaces\\lot-demo-ws lot_demo_001\n    python tools\\probe_site_vocabulary.py --selftest\n\nREAD-ONLY. Opens two json files, prints their shape, writes nothing.\n\nWHY\n\n`tools/probe_selection_drift.py` established that the functional lock guards\nnothing because `_merged_gameplay` reads ten key names that\n`site.site.gameplay.json` does not publish at its top level. Repairing that\nneeds to know what Lot publishes INSTEAD, and this answers it before anyone\nwrites a mapping.\n\nTHE QUESTION THAT DECIDES THE SHAPE OF THE FIX\n\nThere are two very different possibilities and they want different repairs:\n\n  1. RENAME. Lot publishes the same things under different top-level names --\n     `collision` is the hull list, `openings` is the doorways. Then the fix\n     is an alias table and it is small.\n\n  2. EXTRACTION. Lot publishes them NESTED -- doorways per building under\n     `buildings[]`, anchors under `site_markers[]` -- so there is no\n     top-level key to alias and the fix has to walk and gather. Then a naive\n     alias table would hash a container and call it a signature.\n\nSo this does three things: an inventory of every top-level key, a DEEP search\nfor the ten protected names at any depth, and the shape of the five keys that\nlook like candidates. The deep search is the one that decides between the two,\nand it is the reason this is not just `keys()`.\n\nWHAT IT DOES NOT DO\n\nIt does not propose a mapping. Two keys having the same shape is not evidence\nthey mean the same thing, and the whole failure being repaired here came from\na signature that looked healthy.\n"""\nfrom __future__ import annotations\n\nimport json\nimport sys\nfrom pathlib import Path\n\n#: Filled from `packages.approvals.lock.PROTECTED_KEYS` at run time, never\n#: copied. The first version of this file hardcoded ten names; 0.29.0 changed\n#: the set and a hardcoded copy would have quietly measured the wrong thing --\n#: the exact defect these probes were written to find.\nPROTECTED: tuple = ()\n\nMAX_MEMBER_KEYS = 14\nMAX_HITS = 12\n\n\ndef load_protected(root: Path) -> tuple:\n    """The protected key names, from the lock module itself."""\n    global PROTECTED\n    lf = str((root / "level_factory").resolve())\n    if lf not in sys.path:\n        sys.path.insert(0, lf)\n    import importlib\n    lk = importlib.import_module("packages.approvals.lock")\n    importlib.reload(lk)\n    PROTECTED = tuple(sorted({k for keys in lk.PROTECTED_KEYS.values()\n                              for k in keys}))\n    return PROTECTED\n\n\ndef factory_root(start: Path) -> Path | None:\n    for d in [start] + list(start.parents):\n        if (d / "factory.manifest.json").is_file():\n            return d\n    return None\n\n\ndef shape(v, depth: int = 0) -> str:\n    """A one-line description of a value: type, size, and member keys."""\n    if isinstance(v, dict):\n        ks = sorted(v)\n        shown = ", ".join(ks[:MAX_MEMBER_KEYS])\n        more = f" +{len(ks) - MAX_MEMBER_KEYS}" if len(ks) > MAX_MEMBER_KEYS else ""\n        return f"dict[{len(ks)}] {{{shown}{more}}}"\n    if isinstance(v, list):\n        if not v:\n            return "list[0]"\n        kinds = {type(x).__name__ for x in v}\n        if kinds == {"dict"}:\n            union: set = set()\n            for x in v[:200]:\n                union |= set(x)\n            ks = sorted(union)\n            shown = ", ".join(ks[:MAX_MEMBER_KEYS])\n            more = (f" +{len(ks) - MAX_MEMBER_KEYS}"\n                    if len(ks) > MAX_MEMBER_KEYS else "")\n            return f"list[{len(v)}] of dict {{{shown}{more}}}"\n        return f"list[{len(v)}] of {\'/\'.join(sorted(kinds))}"\n    if isinstance(v, str):\n        return f"str({len(v)}) {v[:40]!r}"\n    return f"{type(v).__name__} {v!r}"[:80]\n\n\ndef walk(node, path: str = "", depth: int = 0, max_depth: int = 6):\n    """Yield (path, key, value) for every dict key in the tree."""\n    if depth > max_depth:\n        return\n    if isinstance(node, dict):\n        for k, v in node.items():\n            here = f"{path}.{k}" if path else k\n            yield here, k, v\n            yield from walk(v, here, depth + 1, max_depth)\n    elif isinstance(node, list):\n        # One representative element: a list of 300 buildings has one shape,\n        # and printing 300 identical paths buries the answer.\n        for i, v in enumerate(node[:1]):\n            here = f"{path}[]"\n            yield from walk(v, here, depth + 1, max_depth)\n\n\n\n#: Which field identifies one element of a list, and the rule that found it.\n#: Order matters: `name` is Lot\'s namespaced identity, `node` is a collision\n#: node, `id` needs its building prefix to be unique across the site (that\n#: exact non-uniqueness is what 0.29.0 fixed in the anchor registry).\ndef element_identity(v) -> tuple:\n    if not isinstance(v, dict):\n        return json.dumps(v, sort_keys=True), "value"\n    if v.get("name"):\n        return str(v["name"]), "name"\n    if v.get("node"):\n        return str(v["node"]), "node"\n    if v.get("id"):\n        b = v.get("building")\n        return (f"{b}/{v[\'id\']}", "building/id") if b else (str(v["id"]), "id")\n    # No identifier at all -- openings are like this. Exact-match on the\n    # whole record then, which is strict on purpose: see the note below.\n    return json.dumps(v, sort_keys=True), "whole record"\n\n\ndef _tail(s: str) -> str:\n    return s.rsplit("/", 1)[-1]\n\n\ndef overlap_report(site: dict, deli: dict) -> None:\n    """For every key BOTH files publish: is Deli\'s content inside Lot\'s?\n\n    `_merged_gameplay` backfills only the four Deli-owned collision names.\n    For anything else both publish, the SITE\'s value wins outright and\n    Deli\'s is discarded. That is either correct -- Lot assembles the site\n    from Deli\'s shells, so its records supersede them -- or it is a silent\n    omission from a signature, which is the failure this whole line of work\n    has been about. Set membership answers it; nothing else here does.\n    """\n    shared = [k for k in sorted(set(site) & set(deli))\n              if isinstance(site.get(k), list) and isinstance(deli.get(k), list)\n              and site[k] and deli[k]]\n    print("WHAT BOTH FILES PUBLISH, AND WHETHER DELI\'S IS INSIDE LOT\'S")\n    if not shared:\n        print("  no key is published as a non-empty list by both files")\n        print()\n        return\n    print("  the site\'s value WINS for these; Deli\'s copy is discarded by")\n    print("  _merged_gameplay unless the key is one of the four it backfills")\n    print()\n    for k in shared:\n        s_ids, rules = set(), set()\n        for x in site[k]:\n            i, r = element_identity(x)\n            s_ids.add(i)\n            rules.add(r)\n        d_ids = []\n        for x in deli[k]:\n            i, r = element_identity(x)\n            d_ids.append(i)\n            rules.add(r)\n        s_tails = {_tail(i) for i in s_ids}\n        exact = [i for i in d_ids if i in s_ids]\n        by_tail = [i for i in d_ids\n                   if i not in s_ids and _tail(i) in s_tails]\n        missing = [i for i in d_ids\n                   if i not in s_ids and _tail(i) not in s_tails]\n        print(f"  -- {k}   site {len(site[k])}, deli {len(deli[k])}   "\n              f"identified by {\'/\'.join(sorted(rules))}")\n        print(f"     of deli\'s {len(d_ids)}: {len(exact)} exact, "\n              f"{len(by_tail)} by name-tail, {len(missing)} with no match")\n        if missing:\n            print(f"     no match: {\', \'.join(str(m)[:52] for m in missing[:6])}"\n                  + (" ..." if len(missing) > 6 else ""))\n        if "whole record" in rules and (missing or by_tail):\n            print("     NOTE: these records carry no id, so this compares "\n                  "whole")\n            print("     records. Lot transforms coordinates when it places a "\n                  "shell,")\n            print("     so a low match here can mean transformed rather than "\n                  "dropped.")\n        print()\n\n    print("  READ THIS AS A QUESTION, NOT A VERDICT. A record with no match")\n    print("  is either superseded by Lot or missing from the signature, and")\n    print("  the difference is a contract question between the two tools.")\n    print()\n\n\ndef report(site: dict, deli: dict) -> int:\n    print(f"THE EXTRACTION READS {len(PROTECTED)} KEY(S), "\n          f"read from the lock module: {\', \'.join(PROTECTED)}")\n    print()\n    print("TOP-LEVEL KEYS IN THE SITE FILE")\n    read = set(PROTECTED)\n    for k in sorted(site):\n        mark = "READ" if k in read else "    "\n        print(f"  {mark} {k:<18} {shape(site[k])}")\n    print()\n\n    print("TOP-LEVEL KEYS IN THE DELI FILE")\n    for k in sorted(deli):\n        mark = "READ" if k in read else "    "\n        print(f"  {mark} {k:<18} {shape(deli[k])}")\n    print()\n\n    # THE QUESTION THAT DECIDES THE FIX.\n    print(f"THE {len(PROTECTED)} PROTECTED NAMES, ANYWHERE IN THE SITE TREE")\n    found: dict[str, list[tuple[str, str]]] = {n: [] for n in PROTECTED}\n    for path, key, value in walk(site):\n        if key in found:\n            found[key].append((path, shape(value)))\n    any_nested = False\n    for name in PROTECTED:\n        hits = found[name]\n        if not hits:\n            print(f"  {name:<18} absent at every depth")\n            continue\n        top = [h for h in hits if h[0] == name]\n        nested = [h for h in hits if h[0] != name]\n        if nested:\n            any_nested = True\n        print(f"  {name:<18} {len(hits)} hit(s)"\n              f"{\' (TOP-LEVEL)\' if top else \'\'}"\n              f"{\' (NESTED)\' if nested else \'\'}")\n        for path, sh in hits[:MAX_HITS]:\n            print(f"      {path}  ->  {sh}")\n        if len(hits) > MAX_HITS:\n            print(f"      ... and {len(hits) - MAX_HITS} more")\n    print()\n\n    print("VERDICT")\n    if any_nested:\n        print("  AT LEAST ONE PROTECTED NAME EXISTS NESTED. The repair is an")\n        print("  EXTRACTION, not an alias table -- something has to walk and")\n        print("  gather. An alias mapping a top-level container onto a")\n        print("  signature would hash the container and look healthy.")\n        rc = 2\n    else:\n        print("  NO protected name appears anywhere in the site tree. Lot")\n        print("  publishes these concepts under different names entirely, or")\n        print("  does not publish them. Read the candidate shapes below")\n        print("  against the Deli shapes above before proposing any pairing.")\n        rc = 0\n    print()\n\n    overlap_report(site, deli)\n\n    print("THE CANDIDATE KEYS, IN FULL SHAPE")\n    print("  (looking like a match is not evidence of being one)")\n    for k in ("collision", "openings", "vertical_links", "markers",\n              "site_markers", "rooms", "surfaces", "ground"):\n        if k not in site:\n            continue\n        print(f"  -- {k}")\n        print(f"     {shape(site[k])}")\n        v = site[k]\n        sample = None\n        if isinstance(v, list) and v:\n            sample = v[0]\n        elif isinstance(v, dict) and v:\n            first = sorted(v)[0]\n            sample = {first: v[first]}\n        if sample is not None:\n            txt = json.dumps(sample, indent=6, sort_keys=True)[:900]\n            print("     first element:")\n            for line in txt.splitlines()[:26]:\n                print(f"     {line}")\n            if len(txt) >= 900:\n                print("     ... truncated")\n    return rc\n\n\ndef probe(ws: Path, mission: str, root: Path) -> int:\n    load_protected(root)\n    internal = ws / ".level_factory"\n    lock_p = internal / "locks" / f"{mission}.json"\n    if not lock_p.is_file():\n        print(f"no functional lock at {lock_p}")\n        return 1\n    lock = json.loads(lock_p.read_text(encoding="utf-8"))\n    # From the LOCK, never the marker: the marker is the corrupt one.\n    seed = lock.get("seed")\n    site_p = (internal / "jobs"\n              / f"{mission}.lot_assemble.candidate.seed_{seed}" / "out"\n              / "site.site.gameplay.json")\n    deli_p = (internal / "jobs"\n              / f"{mission}.deli_generate.candidate.seed_{seed}" / "out"\n              / "shell.gameplay.json")\n    for p in (site_p, deli_p):\n        if not p.is_file():\n            print(f"missing {p}")\n            return 1\n    print(f"site: {site_p}")\n    print(f"deli: {deli_p}")\n    print()\n    return report(json.loads(site_p.read_text(encoding="utf-8")),\n                  json.loads(deli_p.read_text(encoding="utf-8")))\n\n\ndef selftest() -> int:\n    bad = 0\n\n    def check(label: str, ok: bool) -> None:\n        nonlocal bad\n        bad += 0 if ok else 1\n        print(f"  {\'ok  \' if ok else \'FAIL\'} {label}")\n\n    root = factory_root(Path(__file__).resolve().parent)\n    if root is None:\n        print("run this from inside a factory checkout")\n        return 1\n    names = load_protected(root)\n    check("the protected names are read from the lock module",\n          bool(names))\n    import importlib\n    lk = importlib.import_module("packages.approvals.lock")\n    check("and are exactly the union of its signatures",\n          set(names) == {k for keys in lk.PROTECTED_KEYS.values()\n                         for k in keys})\n\n    live = names[0]\n    nested = {"buildings": [{"id": "b1", live: [{"id": "d"}]}],\n              "collision": [{"hull": 1}]}\n    hits = {k for _p, k, _v in walk(nested)}\n    check("the deep walk finds a nested protected name", live in hits)\n    paths = {p for p, k, _v in walk(nested) if k == live}\n    check("and reports where it lives", paths == {f"buildings[].{live}"})\n\n    flat = {"buildings": [{"id": "b1"}], "collision": [{"hull": 1}]}\n    check("and finds nothing when there is nothing",\n          not ({k for _p, k, _v in walk(flat)} & set(PROTECTED)))\n\n    check("identity prefers the namespaced name",\n          element_identity({"name": "b0/VAULT", "id": "VAULT"})[0]\n          == "b0/VAULT")\n    check("and builds one from building + id when there is no name",\n          element_identity({"id": "VAULT", "building": "b1"})[0] == "b1/VAULT")\n    check("and falls back to the whole record when nothing identifies it",\n          element_identity({"kind": "door", "x": 1})[1] == "whole record")\n    check("a deli id that Lot namespaced is matched by tail, not missed",\n          _tail("b0/VAULT") == _tail("VAULT") == "VAULT")\n\n    check("shape names a list of dicts by its member keys",\n          shape([{"a": 1, "b": 2}]) == "list[1] of dict {a, b}")\n    check("and distinguishes an empty list from an absent key",\n          shape([]) == "list[0]")\n\n    print()\n    print("  the walk can tell a rename from an extraction"\n          if not bad else f"  {bad} FAILURE(S)")\n    return 1 if bad else 0\n\n\ndef main(argv: list[str]) -> int:\n    if "--selftest" in argv:\n        return selftest()\n    ws = Path(".")\n    rest = []\n    i = 0\n    while i < len(argv):\n        if argv[i] in ("-C", "--chdir"):\n            ws = Path(argv[i + 1])\n            i += 2\n            continue\n        rest.append(argv[i])\n        i += 1\n    if not rest:\n        print("usage: probe_site_vocabulary.py -C <workspace> <mission_id>")\n        return 1\n    if not (ws / ".level_factory").is_dir():\n        print(f"no .level_factory under {ws}; is that a workspace?")\n        return 1\n    root = factory_root(Path(__file__).resolve().parent)\n    if root is None:\n        print("could not find factory.manifest.json above this script")\n        return 1\n    return probe(ws.resolve(), rest[0], root)\n\n\nif __name__ == "__main__":\n    raise SystemExit(main(sys.argv[1:]))\n'

NEW_SRC = VOCAB_SRC


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
    p = root / REL
    if not p.is_file():
        print(f"REFUSING: {REL} is not here")
        return 1
    cur = _sha(p.read_bytes())
    new = NEW_SRC.encode("utf-8")
    if cur == _sha(new):
        print(f"  already applied  {REL}")
        return 0
    if cur != EXPECT:
        print(f"REFUSING: {REL} is not the version this patch expects.")
        print(f"    on disk  {cur[:16]}")
        print(f"    expected {EXPECT[:16]}")
        print("  Run patch_probes_ask_the_code.py first, or merge by hand.")
        return 1
    try:
        compile(NEW_SRC, str(p), "exec")
    except SyntaxError as exc:
        print(f"REFUSING: the replacement does not parse: {exc}")
        return 1
    if check:
        print(f"  would replace  {REL}  {p.stat().st_size:,} -> {len(new):,} "
              f"bytes ({len(new) - p.stat().st_size:+,})")
        return 0
    side = p.with_suffix(p.suffix + SIDECAR)
    if not side.is_file():
        side.write_bytes(p.read_bytes())
    p.write_bytes(new)
    print(f"  replaced      {REL}  {len(new):,} bytes  sha256 {_sha(new)[:16]}")
    return 0


def selftest(root: Path) -> int:
    import importlib.util
    import io
    import json
    import contextlib
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    spec = importlib.util.spec_from_file_location("_probe_vocab",
                                                  root / REL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    check("identity prefers Lot's namespaced name",
          mod.element_identity({"name": "b0/VAULT", "id": "VAULT"})[0]
          == "b0/VAULT")
    check("and composes building/id when there is no name",
          mod.element_identity({"id": "VAULT", "building": "b1"})[0]
          == "b1/VAULT")
    check("and says so when nothing identifies a record",
          mod.element_identity({"kind": "door", "x": 1})[1] == "whole record")

    # A deli id Lot namespaced, and one it never restated.
    site = {"markers": [{"id": "VAULT", "name": "b0/VAULT", "type": "vault"},
                        {"id": "F", "name": "b0/F", "type": "spawn"}],
            "surfaces": [{"node": "b0/col0"}, {"node": "b0/col1"}]}
    deli = {"markers": [{"id": "VAULT", "type": "vault"},
                        {"id": "BREACH_REAR", "type": "breach"}],
            "surfaces": [{"node": "b0/col0"}]}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        mod.overlap_report(site, deli)
    out = buf.getvalue()

    check("a namespaced deli id is matched by tail, not called missing",
          "1 by name-tail" in out)
    check("and one Lot never restated is named",
          "BREACH_REAR" in out and "1 with no match" in out)
    check("an exact node match is reported exact",
          "1 exact, 0 by name-tail, 0 with no match" in out)
    check("it says the site's value wins and deli's is discarded",
          "the site's value WINS" in out)
    check("and frames the result as a question, not a verdict",
          "READ THIS AS A QUESTION, NOT A VERDICT" in out)

    # Nothing shared -> says so rather than printing an empty table.
    buf2 = io.StringIO()
    with contextlib.redirect_stdout(buf2):
        mod.overlap_report({"a": [1]}, {"b": [2]})
    check("no shared key produces a sentence, not an empty table",
          "no key is published as a non-empty list by both" in buf2.getvalue())

    r = __import__("subprocess").run(
        [sys.executable, str(root / REL), "--selftest"],
        cwd=str(root), capture_output=True, text=True)
    check("the probe's own selftest still passes", r.returncode == 0)
    if r.returncode:
        print((r.stdout + r.stderr)[-600:])

    print()
    print("  the report can tell a namespaced match from a missing record"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")
    if "--selftest" in argv:
        return selftest(root)
    if "--revert" in argv:
        p = root / REL
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            print(f"  no sidecar for {REL}")
            return 1
        p.write_bytes(side.read_bytes())
        print(f"  reverted     {REL}")
        return 0
    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_probe_overlap.py --selftest")
        print("    python tools\\probe_site_vocabulary.py "
              "-C workspaces\\lot-demo-ws lot_demo_001")
        print()
        print("  read the 'WHAT BOTH FILES PUBLISH' section. markers is the")
        print("  one that decides whether the flag can flip.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
