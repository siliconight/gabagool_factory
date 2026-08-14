r"""docs/FUNCTIONAL_LOCK.md -- what the lock protects, and where each field comes from.

    python patch_functional_lock_doc.py --check
    python patch_functional_lock_doc.py
    python patch_functional_lock_doc.py --selftest
    python patch_functional_lock_doc.py --revert

Run from the FACTORY ROOT. Creates one doc; touches no code.

The doc first, for the reason EXPORT_NAMING.md went first: this changes what a
functional lock MEANS. Every lock on disk becomes incomparable with every lock
written after it, and one of the three signatures is retired outright. That is
a spec decision, and a spec decision written down after the code is a
rationalisation.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

DOC = "docs/FUNCTIONAL_LOCK.md"
SIDECAR = ".pre_lockdoc"

BODY = '''# The functional lock

Accepted 2026-08-14. Supersedes nothing -- there was no spec; the lock was
whatever `packages/approvals/lock.py` happened to read.

## What it is for

One sentence, from `lock.py`'s own docstring: the lock captures a fingerprint
of everything that must NOT change during the art pass. Lux, Patina,
Pixelcoat and Zoo rewrite materials, lighting and dressing. None of them may
move a wall, a door, a stair or a spawn point. The lock is how that is
enforced, and `verify_no_drift` is where it is checked.

## What was measured, 2026-08-14

It has never enforced it.

`tools/probe_selection_drift.py` compared the three protected signatures three
ways -- as the gate resolves them, from the real site file, and from no site
file at all. All three agreed on all three signatures. The site file changes
nothing.

`tools/probe_site_vocabulary.py` found why. `_merged_gameplay` reads **ten**
key names. `site.site.gameplay.json` publishes twenty top-level keys and none
of the ten, at any depth. Lot and Deli name the same concepts differently and
the extraction was written in Deli's vocabulary. Four of the ten --
`stair_systems`, `ladders`, `platforms`, `fire_escapes` -- are backfilled from
the Deli side by `setdefault`, which is what hid it: the signature was never
empty, so it never looked broken.

*(The count is ten. The 0.28.0, factory-v1.19.0 and factory-v1.20.0 entries
all say eleven. Six collision keys, one anchor, three route. Nothing else in
those entries changes.)*

What the lock actually protected, until now: Deli's `stair_systems`, a list
of 2.

## The mapping

| signature | reads today | reads after | why |
|---|---|---|---|
| `collision_fingerprint` | 6 Deli-shaped names | + `surfaces` node names, `ground` sources, `openings`, `vertical_links` | the site's collision identity is its node names, not a count |
| `anchor_registry_hash` | `anchors` | `markers` | 42 entries with id, type, name, room, building |
| `route_graph_hash` | `route`/`route_graph`/`nav_hints` | **retired** | nothing in the factory publishes a route graph |

### `collision_fingerprint`

**From `surfaces`, node names only.** 1029 entries of
`{node: "b0/ext_col_0_N_seg0", material: {...}}`. The node names are the
collision geometry's identity: they change when the geometry changes.

**The material dict is excluded, and that is the point.** Patina and
Pixelcoat rewrite materials during the art pass. Hashing them would report
drift on every normal run -- the false-positive failure that makes a gate get
disabled. A lock that cries drift is removed; a lock that never does is
ignored. Neither protects anything.

**Plus `ground`**, per building: `{source: "mansion_a02.glb", state,
detail}`. The source glb is what the collision came from. Swapping a
building's source mesh is exactly the change this must catch, and it would
not necessarily alter a node name.

**Plus `openings`** (76), whole. `{kind: "door", width, height, sill, wall,
story, building, x, y, z, breach_class, vaultable, reinforceable}`. This is
what `doorways` always meant. Geometry AND the breach fields -- a door
becoming unvaultable is a functional change even if it does not move.

**Plus `vertical_links`** (4), whole. `{kind: "hatch", from_story, to_story,
climb_height, breachable, building, x, y}`. Lot's own vertical connectivity,
a DIFFERENT population from Deli's `stair_systems` (2), not a replacement for
it. Both are kept. A hatch that stops existing between the graybox and the
shipped level is a functional change.

**`collision` is NOT used.** It is a four-field report --
`{colliders: 1067, complete, detail, unread}` -- and a count is a weak
fingerprint: geometry can be replaced wholesale at 1067 colliders. It looks
like the obvious mapping and it is the wrong one.

### `anchor_registry_hash`

**From `markers`** (42):
`{id: "FRONT", name: "b0/ATTACKER_SPAWN_FRONT", type: "attacker_spawn",
room: "hall", building: "b0", x, y, z, facing, rot_z, ...}`.

**Identity is `name`, not `id`.** `id` is `"FRONT"`, scoped to its building;
two buildings both have one. `_anchor_registry` keys and sorts on `id` today,
so two distinct anchors would normalise to identical entries and the registry
would silently under-count. `name` is already namespaced, and
`ids.namespaced_anchor` exists for exactly this.

**`site_markers` is `list[0]`.** It is not a second half of the registry.

**Position is added, and this is a change of meaning.** Today
`_anchor_registry` keeps only `id`, `type` and `authority` -- so the art pass
could move every spawn point in the level and the hash would not move.
Nothing else checks anchor position either. `x`, `y`, `z` and `facing` join
the registry. A spawn that slides into a wall during dressing is the failure
this gate exists for.

*Volatile fields excluded:* `meta`, and any field a presentation stage is
expected to write.

### `route_graph_hash` -- retired

No tool in the factory publishes a route graph. `rooms` (25) has `bounds`,
`center`, `role`, `combat_range`, `objective` -- spatial, no adjacency.
`openings` implies connectivity but is not a graph. `nav_hints` exists
nowhere.

It is removed from `PROTECTED_KEYS` rather than left to hash two empty dicts,
because an empty signature is not neutral: it reads as coverage. Its drift
message -- "route graph changed after art pass" -- has never been capable of
firing, and a reader counting three protected signatures was counting one
that could not work.

Deriving one from `rooms` + `openings` was considered and rejected: the lock
would be inventing a graph no other stage uses, and a wrong derivation is
harder to notice than an absent one, because it produces a real-looking hash.

**If a route graph is wanted, it belongs in Lot's output contract, not in the
lock's imagination.** That is a roadmap item against `lot`, not work here.

## What this deliberately does NOT protect

- **Materials, lighting, dressing.** The art pass owns them.
- **Anything Deli owns that Lot does not restate.** `stair_systems`,
  `ladders`, `platforms`, `fire_escapes` keep coming from the Deli side; the
  backfill stays, and is now visible in `coverage.backfilled_from_deli`
  rather than silently propping up a signature.
- **Clearance metrics.** Carried on the lock, not hashed. Unchanged.
- **Route/topology.** See above.

## Every existing lock becomes incomparable

The signatures change definition, so a lock written before this and one
written after cannot be compared -- `verify_no_drift` would report drift on
every field, for every mission, immediately.

Locks are regenerable: `approve --gate functional_shell_locked` recomputes
one from the job outputs. The lock carries a `schema` field
(`level_factory.functional_lock.v0.1`); it goes to `v0.2`, and a lock whose
schema does not match is reported as **needing recompute**, NOT as drift.
Reporting a schema change as drift would block every export on a version
bump and teach the next reader that drift means nothing.

## Enforcement

`LOCK_COVERAGE_ENFORCED` stays `False` until one real mission produces a
non-vacuous lock under this spec. When it flips, the comment in `lock.py`
names the mission that earned it -- the way `CLOSURE_ENFORCED`'s comment
names the run that earned it.

The order is: land this mapping, recompute `lot_demo_001`'s lock, confirm
`coverage.site_contributes` is non-empty and `guards_no_site` is false, then
flip. Not before.

## Open

**Does a `kind` on `vertical_links` need splitting?** Lot's four are
`kind: "hatch"`. If ladders and stairs also arrive there, they are
functionally distinct from Deli's `stair_systems` and may want their own
signature rather than sharing the collision one. Four entries is too small a
sample to decide, and this does not decide it.
'''

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
    p = root / DOC
    if not p.parent.is_dir():
        print(f"REFUSING: {p.parent} is not here")
        return 1
    data = BODY.encode("utf-8")
    if p.is_file():
        cur = p.read_bytes()
        if cur == data:
            print(f"  already applied  {DOC}")
            return 0
        print(f"REFUSING: {DOC} exists and differs; this patch creates it. "
              f"Diff it by hand or --revert first.")
        return 1
    if check:
        print(f"  would create  {DOC}  {len(data):,} bytes")
        return 0
    p.write_bytes(data)
    print(f"  created      {DOC}  {len(data):,} bytes  "
          f"sha256 {_sha(data)[:16]}")
    return 0


def selftest(root: Path) -> int:
    import importlib
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    doc = (root / DOC).read_text(encoding="utf-8")
    flat = " ".join(doc.split())

    # THE DOC IS CHECKED AGAINST THE CODE, not against itself. Today's lesson
    # was three green selftests over wrong artifacts; a spec that asserts its
    # own contents proves nothing.
    lf = str((root / "level_factory").resolve())
    if lf not in sys.path:
        sys.path.insert(0, lf)
    lk = importlib.import_module("packages.approvals.lock")
    importlib.reload(lk)

    names = {k for keys in lk.PROTECTED_KEYS.values() for k in keys}
    check(f"the code really reads ten names (found {len(names)})",
          len(names) == 10)
    check("and the doc says ten", "reads **ten**" in doc)
    check("route_graph_hash is still live in the code, as the doc implies",
          "route_graph_hash" in lk.PROTECTED_KEYS)
    check("the doc marks it retired", "`route_graph_hash` -- retired" in doc)
    check("the four Deli-backfilled names are the ones the doc names",
          lk.BACKFILLED_FROM_DELI ==
          frozenset({"stair_systems", "ladders", "platforms", "fire_escapes",
                     "anchors"}))
    check("the doc names the anchor-registry fields the code keeps today",
          all(s in doc for s in ("`id`, `type` and `authority`",)))
    check("enforcement is still off, as the doc says",
          lk.LOCK_COVERAGE_ENFORCED is False
          and "stays `False` until one real mission" in doc)
    check("the schema the doc bumps is the schema the code writes",
          lk.FunctionalLock(mission_id="m", candidate_id="c", seed=1).schema
          == "level_factory.functional_lock.v0.1"
          and "level_factory.functional_lock.v0.1" in doc)

    # The decisions, stated where a reader will look for them.
    check("it says why `collision` is rejected",
          "`collision` is NOT used" in doc and "colliders: 1067" in flat)
    check("it says why materials are excluded",
          "cries drift is removed" in flat)
    check("it says identity is name, not id",
          "Identity is `name`, not `id`" in doc)
    check("it says position is added and calls it a change of meaning",
          "change of meaning" in doc)
    check("it says vertical_links is an addition, not a substitution",
          "not a replacement for" in flat)
    check("it refuses to invent a route graph",
          "inventing a graph no other stage uses" in flat)
    check("it says where a route graph would belong instead",
          "Lot's output contract" in doc)
    check("it says every existing lock becomes incomparable",
          "incomparable" in doc and "v0.2" in doc)
    check("and that a schema change is NOT drift",
          "NOT as drift" in doc)
    check("it names the order enforcement flips in",
          "recompute `lot_demo_001`'s lock" in doc)
    check("it corrects the eleven/ten misstatement in the record",
          "all say eleven" in flat)
    check("it leaves the vertical_links question open rather than deciding",
          "## Open" in doc and "too small a sample" in flat)

    print()
    print("  the spec agrees with the code it is about to change"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")

    if "--selftest" in argv:
        return selftest(root)

    if "--revert" in argv:
        p = root / DOC
        if not p.is_file():
            print(f"  {DOC} is not here")
            return 1
        p.unlink()
        print(f"  removed      {DOC}")
        return 0

    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_functional_lock_doc.py --selftest")
        print()
        print("  READ IT BEFORE THE CODE PATCH. It retires one of the three")
        print("  signatures and changes what the other two mean.")
        print()
        print('    git add docs/FUNCTIONAL_LOCK.md patches/')
        print('    git commit -m "docs: the functional lock, and what it '
              'actually protects"')
        print("    git push")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
