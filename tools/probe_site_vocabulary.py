r"""What Lot's site gameplay file actually publishes, and where.

    python tools\probe_site_vocabulary.py -C workspaces\lot-demo-ws lot_demo_001
    python tools\probe_site_vocabulary.py --selftest

READ-ONLY. Opens two json files, prints their shape, writes nothing.

WHY

`tools/probe_selection_drift.py` established that the functional lock guards
nothing because `_merged_gameplay` reads ten key names that
`site.site.gameplay.json` does not publish at its top level. Repairing that
needs to know what Lot publishes INSTEAD, and this answers it before anyone
writes a mapping.

THE QUESTION THAT DECIDES THE SHAPE OF THE FIX

There are two very different possibilities and they want different repairs:

  1. RENAME. Lot publishes the same things under different top-level names --
     `collision` is the hull list, `openings` is the doorways. Then the fix
     is an alias table and it is small.

  2. EXTRACTION. Lot publishes them NESTED -- doorways per building under
     `buildings[]`, anchors under `site_markers[]` -- so there is no
     top-level key to alias and the fix has to walk and gather. Then a naive
     alias table would hash a container and call it a signature.

So this does three things: an inventory of every top-level key, a DEEP search
for the ten protected names at any depth, and the shape of the five keys that
look like candidates. The deep search is the one that decides between the two,
and it is the reason this is not just `keys()`.

WHAT IT DOES NOT DO

It does not propose a mapping. Two keys having the same shape is not evidence
they mean the same thing, and the whole failure being repaired here came from
a signature that looked healthy.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

#: Filled from `packages.approvals.lock.PROTECTED_KEYS` at run time, never
#: copied. The first version of this file hardcoded ten names; 0.29.0 changed
#: the set and a hardcoded copy would have quietly measured the wrong thing --
#: the exact defect these probes were written to find.
PROTECTED: tuple = ()

MAX_MEMBER_KEYS = 14
MAX_HITS = 12


def load_protected(root: Path) -> tuple:
    """The protected key names, from the lock module itself."""
    global PROTECTED
    lf = str((root / "level_factory").resolve())
    if lf not in sys.path:
        sys.path.insert(0, lf)
    import importlib
    lk = importlib.import_module("packages.approvals.lock")
    importlib.reload(lk)
    PROTECTED = tuple(sorted({k for keys in lk.PROTECTED_KEYS.values()
                              for k in keys}))
    return PROTECTED


def factory_root(start: Path) -> Path | None:
    for d in [start] + list(start.parents):
        if (d / "factory.manifest.json").is_file():
            return d
    return None


def shape(v, depth: int = 0) -> str:
    """A one-line description of a value: type, size, and member keys."""
    if isinstance(v, dict):
        ks = sorted(v)
        shown = ", ".join(ks[:MAX_MEMBER_KEYS])
        more = f" +{len(ks) - MAX_MEMBER_KEYS}" if len(ks) > MAX_MEMBER_KEYS else ""
        return f"dict[{len(ks)}] {{{shown}{more}}}"
    if isinstance(v, list):
        if not v:
            return "list[0]"
        kinds = {type(x).__name__ for x in v}
        if kinds == {"dict"}:
            union: set = set()
            for x in v[:200]:
                union |= set(x)
            ks = sorted(union)
            shown = ", ".join(ks[:MAX_MEMBER_KEYS])
            more = (f" +{len(ks) - MAX_MEMBER_KEYS}"
                    if len(ks) > MAX_MEMBER_KEYS else "")
            return f"list[{len(v)}] of dict {{{shown}{more}}}"
        return f"list[{len(v)}] of {'/'.join(sorted(kinds))}"
    if isinstance(v, str):
        return f"str({len(v)}) {v[:40]!r}"
    return f"{type(v).__name__} {v!r}"[:80]


def walk(node, path: str = "", depth: int = 0, max_depth: int = 6):
    """Yield (path, key, value) for every dict key in the tree."""
    if depth > max_depth:
        return
    if isinstance(node, dict):
        for k, v in node.items():
            here = f"{path}.{k}" if path else k
            yield here, k, v
            yield from walk(v, here, depth + 1, max_depth)
    elif isinstance(node, list):
        # One representative element: a list of 300 buildings has one shape,
        # and printing 300 identical paths buries the answer.
        for i, v in enumerate(node[:1]):
            here = f"{path}[]"
            yield from walk(v, here, depth + 1, max_depth)



#: Which field identifies one element of a list, and the rule that found it.
#: Order matters: `name` is Lot's namespaced identity, `node` is a collision
#: node, `id` needs its building prefix to be unique across the site (that
#: exact non-uniqueness is what 0.29.0 fixed in the anchor registry).
def element_identity(v) -> tuple:
    if not isinstance(v, dict):
        return json.dumps(v, sort_keys=True), "value"
    if v.get("name"):
        return str(v["name"]), "name"
    if v.get("node"):
        return str(v["node"]), "node"
    if v.get("id"):
        b = v.get("building")
        return (f"{b}/{v['id']}", "building/id") if b else (str(v["id"]), "id")
    # No identifier at all -- openings are like this. Exact-match on the
    # whole record then, which is strict on purpose: see the note below.
    return json.dumps(v, sort_keys=True), "whole record"


def _tail(s: str) -> str:
    return s.rsplit("/", 1)[-1]


def overlap_report(site: dict, deli: dict) -> None:
    """For every key BOTH files publish: is Deli's content inside Lot's?

    `_merged_gameplay` backfills only the four Deli-owned collision names.
    For anything else both publish, the SITE's value wins outright and
    Deli's is discarded. That is either correct -- Lot assembles the site
    from Deli's shells, so its records supersede them -- or it is a silent
    omission from a signature, which is the failure this whole line of work
    has been about. Set membership answers it; nothing else here does.
    """
    shared = [k for k in sorted(set(site) & set(deli))
              if isinstance(site.get(k), list) and isinstance(deli.get(k), list)
              and site[k] and deli[k]]
    print("WHAT BOTH FILES PUBLISH, AND WHETHER DELI'S IS INSIDE LOT'S")
    if not shared:
        print("  no key is published as a non-empty list by both files")
        print()
        return
    print("  the site's value WINS for these; Deli's copy is discarded by")
    print("  _merged_gameplay unless the key is one of the four it backfills")
    print()
    for k in shared:
        s_ids, rules = set(), set()
        for x in site[k]:
            i, r = element_identity(x)
            s_ids.add(i)
            rules.add(r)
        d_ids = []
        for x in deli[k]:
            i, r = element_identity(x)
            d_ids.append(i)
            rules.add(r)
        s_tails = {_tail(i) for i in s_ids}
        exact = [i for i in d_ids if i in s_ids]
        by_tail = [i for i in d_ids
                   if i not in s_ids and _tail(i) in s_tails]
        missing = [i for i in d_ids
                   if i not in s_ids and _tail(i) not in s_tails]
        print(f"  -- {k}   site {len(site[k])}, deli {len(deli[k])}   "
              f"identified by {'/'.join(sorted(rules))}")
        print(f"     of deli's {len(d_ids)}: {len(exact)} exact, "
              f"{len(by_tail)} by name-tail, {len(missing)} with no match")
        if missing:
            print(f"     no match: {', '.join(str(m)[:52] for m in missing[:6])}"
                  + (" ..." if len(missing) > 6 else ""))
        if "whole record" in rules and (missing or by_tail):
            print("     NOTE: these records carry no id, so this compares "
                  "whole")
            print("     records. Lot transforms coordinates when it places a "
                  "shell,")
            print("     so a low match here can mean transformed rather than "
                  "dropped.")
        print()

    print("  READ THIS AS A QUESTION, NOT A VERDICT. A record with no match")
    print("  is either superseded by Lot or missing from the signature, and")
    print("  the difference is a contract question between the two tools.")
    print()


def report(site: dict, deli: dict) -> int:
    print(f"THE EXTRACTION READS {len(PROTECTED)} KEY(S), "
          f"read from the lock module: {', '.join(PROTECTED)}")
    print()
    print("TOP-LEVEL KEYS IN THE SITE FILE")
    read = set(PROTECTED)
    for k in sorted(site):
        mark = "READ" if k in read else "    "
        print(f"  {mark} {k:<18} {shape(site[k])}")
    print()

    print("TOP-LEVEL KEYS IN THE DELI FILE")
    for k in sorted(deli):
        mark = "READ" if k in read else "    "
        print(f"  {mark} {k:<18} {shape(deli[k])}")
    print()

    # THE QUESTION THAT DECIDES THE FIX.
    print(f"THE {len(PROTECTED)} PROTECTED NAMES, ANYWHERE IN THE SITE TREE")
    found: dict[str, list[tuple[str, str]]] = {n: [] for n in PROTECTED}
    for path, key, value in walk(site):
        if key in found:
            found[key].append((path, shape(value)))
    any_nested = False
    for name in PROTECTED:
        hits = found[name]
        if not hits:
            print(f"  {name:<18} absent at every depth")
            continue
        top = [h for h in hits if h[0] == name]
        nested = [h for h in hits if h[0] != name]
        if nested:
            any_nested = True
        print(f"  {name:<18} {len(hits)} hit(s)"
              f"{' (TOP-LEVEL)' if top else ''}"
              f"{' (NESTED)' if nested else ''}")
        for path, sh in hits[:MAX_HITS]:
            print(f"      {path}  ->  {sh}")
        if len(hits) > MAX_HITS:
            print(f"      ... and {len(hits) - MAX_HITS} more")
    print()

    print("VERDICT")
    if any_nested:
        print("  AT LEAST ONE PROTECTED NAME EXISTS NESTED. The repair is an")
        print("  EXTRACTION, not an alias table -- something has to walk and")
        print("  gather. An alias mapping a top-level container onto a")
        print("  signature would hash the container and look healthy.")
        rc = 2
    else:
        print("  NO protected name appears anywhere in the site tree. Lot")
        print("  publishes these concepts under different names entirely, or")
        print("  does not publish them. Read the candidate shapes below")
        print("  against the Deli shapes above before proposing any pairing.")
        rc = 0
    print()

    overlap_report(site, deli)

    print("THE CANDIDATE KEYS, IN FULL SHAPE")
    print("  (looking like a match is not evidence of being one)")
    for k in ("collision", "openings", "vertical_links", "markers",
              "site_markers", "rooms", "surfaces", "ground"):
        if k not in site:
            continue
        print(f"  -- {k}")
        print(f"     {shape(site[k])}")
        v = site[k]
        sample = None
        if isinstance(v, list) and v:
            sample = v[0]
        elif isinstance(v, dict) and v:
            first = sorted(v)[0]
            sample = {first: v[first]}
        if sample is not None:
            txt = json.dumps(sample, indent=6, sort_keys=True)[:900]
            print("     first element:")
            for line in txt.splitlines()[:26]:
                print(f"     {line}")
            if len(txt) >= 900:
                print("     ... truncated")
    return rc


def probe(ws: Path, mission: str, root: Path) -> int:
    load_protected(root)
    internal = ws / ".level_factory"
    lock_p = internal / "locks" / f"{mission}.json"
    if not lock_p.is_file():
        print(f"no functional lock at {lock_p}")
        return 1
    lock = json.loads(lock_p.read_text(encoding="utf-8"))
    # From the LOCK, never the marker: the marker is the corrupt one.
    seed = lock.get("seed")
    site_p = (internal / "jobs"
              / f"{mission}.lot_assemble.candidate.seed_{seed}" / "out"
              / "site.site.gameplay.json")
    deli_p = (internal / "jobs"
              / f"{mission}.deli_generate.candidate.seed_{seed}" / "out"
              / "shell.gameplay.json")
    for p in (site_p, deli_p):
        if not p.is_file():
            print(f"missing {p}")
            return 1
    print(f"site: {site_p}")
    print(f"deli: {deli_p}")
    print()
    return report(json.loads(site_p.read_text(encoding="utf-8")),
                  json.loads(deli_p.read_text(encoding="utf-8")))


def selftest() -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    root = factory_root(Path(__file__).resolve().parent)
    if root is None:
        print("run this from inside a factory checkout")
        return 1
    names = load_protected(root)
    check("the protected names are read from the lock module",
          bool(names))
    import importlib
    lk = importlib.import_module("packages.approvals.lock")
    check("and are exactly the union of its signatures",
          set(names) == {k for keys in lk.PROTECTED_KEYS.values()
                         for k in keys})

    live = names[0]
    nested = {"buildings": [{"id": "b1", live: [{"id": "d"}]}],
              "collision": [{"hull": 1}]}
    hits = {k for _p, k, _v in walk(nested)}
    check("the deep walk finds a nested protected name", live in hits)
    paths = {p for p, k, _v in walk(nested) if k == live}
    check("and reports where it lives", paths == {f"buildings[].{live}"})

    flat = {"buildings": [{"id": "b1"}], "collision": [{"hull": 1}]}
    check("and finds nothing when there is nothing",
          not ({k for _p, k, _v in walk(flat)} & set(PROTECTED)))

    check("identity prefers the namespaced name",
          element_identity({"name": "b0/VAULT", "id": "VAULT"})[0]
          == "b0/VAULT")
    check("and builds one from building + id when there is no name",
          element_identity({"id": "VAULT", "building": "b1"})[0] == "b1/VAULT")
    check("and falls back to the whole record when nothing identifies it",
          element_identity({"kind": "door", "x": 1})[1] == "whole record")
    check("a deli id that Lot namespaced is matched by tail, not missed",
          _tail("b0/VAULT") == _tail("VAULT") == "VAULT")

    check("shape names a list of dicts by its member keys",
          shape([{"a": 1, "b": 2}]) == "list[1] of dict {a, b}")
    check("and distinguishes an empty list from an absent key",
          shape([]) == "list[0]")

    print()
    print("  the walk can tell a rename from an extraction"
          if not bad else f"  {bad} FAILURE(S)")
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
        print("usage: probe_site_vocabulary.py -C <workspace> <mission_id>")
        return 1
    if not (ws / ".level_factory").is_dir():
        print(f"no .level_factory under {ws}; is that a workspace?")
        return 1
    root = factory_root(Path(__file__).resolve().parent)
    if root is None:
        print("could not find factory.manifest.json above this script")
        return 1
    return probe(ws.resolve(), rest[0], root)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
