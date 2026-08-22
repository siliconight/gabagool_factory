# The functional lock

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

## Two rules for a shared key

*Added 2026-08-14, after `tools/probe_site_vocabulary.py` measured the
overlap.*

Both tools publish `markers`, `openings`, `surfaces` and `rooms`.
`_merged_gameplay` had one rule for that -- the site wins -- and it is
right only when Lot restates what Deli said.

| | site | deli | of deli's, matched |
|---|---|---|---|
| `markers` | 42 | 14 | **1** |
| `surfaces` | 1029 | 238 | 213 |
| `openings` | 76 | 19 | 0, whole-record |
| `rooms` | 25 | 4 | 1 |

`markers` is not a subset relationship. Lot's are site-level
(`b0/ATTACKER_SPAWN_FRONT`); Deli's are interior gameplay anchors --
`CREW_SPAWN_A`, `RESPONDER_SPAWN_1`, eleven cover points. The `rooms`
row confirms it: Deli's unmatched `manager_office`, `security_room`,
`vault_room` are where those cover points live. Thirteen gameplay
anchors were being dropped from the gameplay-anchor registry.

So there are two rules, and they are named:

- **`BACKFILLED_FROM_DELI`** -- Deli's value is used when the site omits
  the key. `stair_systems`, `ladders`, `platforms`, `fire_escapes`.
- **`UNIONED_WITH_DELI`** -- both are kept, deduped by NAME-TAIL because
  Lot namespaces what it does restate. `markers` only.

**`surfaces` is deliberately not unioned.** The 25 unmatched are
`int_col_-1_2_*` -- story -1 -- and window sub-parts. If Lot never
places that geometry it is not in the shipped level, and hashing it
would protect what the package does not contain and report drift the
day Lot stops emitting it. Deli's markers ship: the Dispatch handoff
carries them into the export.

**`openings` is undecided.** 0 of 19 matched, but that compares whole
records against coordinates Lot transforms when it places a shell. Not
decidable from these two files.

**Those 25 collision nodes are a question for `lot`**, not for the lock:
geometry that exists in the shell and not in the assembled site is
either a deliberate drop nobody wrote down, or loss between two stages.

## Interactive fixtures: two collision states, one hash

*Added 2026-08-22, answering the question roadmap item 46 parked here: a
breached wall's `collision_per_state` says it stops colliding -- so which
state is the locked shell: default, worst case, or every state as a set?*

**The locked shell is the DEFAULT state.** The collision fingerprint hashes
the level AT REST -- the geometry Deli Counter builds, the state every gate
measures (nav-gate, walktest, the map grader all evaluate default-state
geometry), the state the composed scene renders visible. Non-default states
exist in the package as a declaration plus parked hidden art
(`<slot_id>_<state>`, `visible = false`), never as live offline collision.
Hashing a "worst case" or a per-state set would protect collision no
artifact realizes and no gate verifies -- the same reasoning that keeps
Deli's 25 unplaced collision nodes out of `surfaces`: the lock must not
protect what the package does not contain.

**The per-state truth is protected as DATA, not as geometry:**
`interactive_registry_hash`, a third signature over the `interactives`
declaration whole -- id, kind, states, default, transitions,
`state_geometry`, `collision_per_state`, transform. Every field is
functional; none is a presentation stage's to write. An art pass that drops
a fixture, adds a state, rewires a transition, or flips whether a broken
window still blocks moves this hash without moving a vertex -- exactly the
change "two collision states, one hash" was worried would slip through.

**Identity is `id`, and that is the OPPOSITE call from anchors --
deliberately.** Anchor ids are building-scoped (`"FRONT"` everywhere), so
anchors key on the namespaced name. Interactive ids are globally unique by
construction (`<building>:if:<hash>`, position-derived -- INTERACTIVES.md,
"Stable ids") and are the network handle every client, snapshot and saved
game references. The registry hashes the handle the shipped package
actually uses; renaming it here would protect a name nothing ships.

`interactives` is site-authoritative -- Lot concatenates every building's
declarations, ids verbatim -- and joins `BACKFILLED_FROM_DELI`: a site file
written before Lot carried the key falls back to the building's own
declaration rather than hashing an empty list that reads as coverage.

Schema: v0.2 -> v0.3. Same rule as the last bump -- a v0.2 lock reports as
**needing recompute**, never as drift.

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
