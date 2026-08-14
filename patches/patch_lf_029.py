r"""level_factory 0.29.0 -- the functional lock protects the site.

    python patch_lf_029.py --check
    python patch_lf_029.py
    python patch_lf_029.py --selftest
    python patch_lf_029.py --revert

Run from the FACTORY ROOT, AFTER docs/FUNCTIONAL_LOCK.md is in.

This is the repair. `docs/FUNCTIONAL_LOCK.md` is the spec; every decision
below is argued there and only summarised here.

    collision_fingerprint   + surfaces node names, ground sources,
                              openings, vertical_links
    anchor_registry_hash    markers, keyed on `name`, WITH position
    route_graph_hash        RETIRED

SCHEMA GOES TO v0.2, AND A MISMATCH IS NOT DRIFT

The signatures change definition, so a lock written before this and one
written after are incomparable -- `verify_no_drift` against an old lock would
report every field as drift, for every mission, immediately. That is not
drift, it is a version skew, and reporting it as drift would block every
export on a version bump and teach the next reader that drift means nothing.
An old-schema lock now returns `needs_recompute` with the comparison SKIPPED,
and `passed` is not asserted either way -- it is False with no drift entries,
because a comparison that did not happen did not pass.

WHAT EACH SIGNATURE READS NOW

`surfaces` node names ONLY -- the material dict is excluded because Patina and
Pixelcoat rewrite it during the art pass, and a lock that reports drift on
every normal run gets disabled. `ground` contributes each building's source
glb: swapping a building's mesh is exactly the change this must catch and
would not necessarily alter a node name. `openings` (76) and `vertical_links`
(4) whole, including their breach fields -- a door that stops being vaultable
is a functional change even if it does not move.

`markers` (42) replaces `anchors`, keyed on `name` rather than `id`, because
`id` is `"FRONT"` scoped to its building and two buildings both have one --
`_anchor_registry` sorted on `id`, so two distinct anchors normalised to
identical entries. Position joins the registry: today the art pass could move
every spawn point and the hash would not move, and nothing else checks anchor
position either.

`route_graph_hash` is removed rather than left hashing two empty dicts,
because an empty signature is not neutral -- it reads as coverage. Nothing in
the factory publishes a route graph. If one is wanted it belongs in `lot`'s
output contract.

THE DELI BACKFILL STAYS, AND IS NOW VISIBLE

`stair_systems`, `ladders`, `platforms` and `fire_escapes` still come from the
Deli side. That was never wrong; what was wrong is that it silently propped
up a signature carrying nothing else. `coverage.backfilled_from_deli` names
them.

WHAT THIS DOES NOT DO

It does not flip `LOCK_COVERAGE_ENFORCED`. The order in the doc is: land the
mapping, recompute a real lock, confirm `guards_no_site` is false, then flip
-- naming the mission that earned it. Recomputing `lot_demo_001` needs
`approve --gate functional_shell_locked`, which resolves its job paths
through the `seed_XXXX` marker and will not work until that is repaired. That
is the next patch, not this one.

The unit suite's three lock tests use `anchors` and `stair_systems`. They keep
passing: `_anchor_registry` reads `markers` first and falls back to `anchors`,
so a fixture written in Deli's vocabulary still works. That fallback is not
compatibility scaffolding to be removed later -- Deli-shaped anchors are a
real input.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

LOCK = "level_factory/packages/approvals/lock.py"
COMMANDS = "level_factory/apps/cli/commands/__init__.py"
VERSION_F = "level_factory/VERSION"
CHANGELOG = "level_factory/CHANGELOG.md"
DOC = "docs/FUNCTIONAL_LOCK.md"
SIDECAR = ".pre_029"

OLD_V, NEW_V = "0.28.0", "0.29.0"

EDITS: list[tuple[str, str, str]] = [
    (LOCK,
     "#: `_collision_signature`, `_anchor_registry` and `_route_graph` use, written\n",
     "#: `_collision_signature` and `_anchor_registry` use, written\n"),

    (LOCK,
     '    "collision_fingerprint": ("stair_systems", "ladders", "platforms",\n'
     '                              "fire_escapes", "collision_hulls", "doorways"),\n'
     '    "anchor_registry_hash": ("anchors",),\n'
     '    "route_graph_hash": ("route", "route_graph", "nav_hints"),\n'
     "}\n",

     '    "collision_fingerprint": ("stair_systems", "ladders", "platforms",\n'
     '                              "fire_escapes", "openings",\n'
     '                              "vertical_links", "surfaces", "ground"),\n'
     '    "anchor_registry_hash": ("markers",),\n'
     "}\n"
     "\n"
     "#: The schema a lock written by THIS code carries. Bumped whenever a\n"
     "#: signature changes definition, because two locks with different\n"
     "#: definitions are not comparable and diffing them produces drift\n"
     "#: reports that mean nothing. See docs/FUNCTIONAL_LOCK.md.\n"
     'SCHEMA = "level_factory.functional_lock.v0.2"\n'),

    (LOCK,
     "BACKFILLED_FROM_DELI = frozenset(\n"
     '    {"stair_systems", "ladders", "platforms", "fire_escapes", "anchors"})\n',
     "BACKFILLED_FROM_DELI = frozenset(\n"
     '    {"stair_systems", "ladders", "platforms", "fire_escapes"})\n'),

    (LOCK,
     "def _anchor_registry(gameplay: dict) -> list[dict]:\n"
     '    """Stable, order-independent view of the gameplay anchors."""\n'
     '    anchors = gameplay.get("anchors", [])\n',

     "def _anchor_identity(a: dict) -> str:\n"
     '    """The name that identifies one anchor across the whole site.\n'
     "\n"
     "    NOT `id`. Lot's markers carry `id: \"FRONT\"` scoped to a building,\n"
     "    and every building has one -- `_anchor_registry` sorted and keyed on\n"
     "    `id`, so two distinct anchors normalised to identical entries and\n"
     "    the registry silently under-counted. `name` is already namespaced\n"
     '    (`b0/ATTACKER_SPAWN_FRONT`); `ids.namespaced_anchor` exists for the\n'
     "    same reason.\n"
     '    """\n'
     '    name = a.get("name")\n'
     "    if name:\n"
     "        return str(name)\n"
     '    ident = a.get("id") or a.get("shell_id")\n'
     '    building = a.get("building")\n'
     '    return f"{building}/{ident}" if building and ident else str(ident)\n'
     "\n"
     "\n"
     "def _anchor_registry(gameplay: dict) -> list[dict]:\n"
     '    """Stable, order-independent view of the gameplay anchors.\n'
     "\n"
     "    Reads Lot's `markers` first, Deli's `anchors` second. The fallback is\n"
     "    not compatibility scaffolding: a Deli-shaped anchor list is a real\n"
     "    input, and the unit fixtures are written that way.\n"
     "\n"
     "    POSITION IS PART OF THE REGISTRY. It was not, so the art pass could\n"
     "    move every spawn point in the level and this hash would not change.\n"
     "    Nothing else checks anchor position either. See\n"
     "    docs/FUNCTIONAL_LOCK.md -- this is a change of meaning, not a rename.\n"
     '    """\n'
     '    anchors = gameplay.get("markers") or gameplay.get("anchors") or []\n'),

    (LOCK,
     "        norm.append({\n"
     '            "id": a.get("id") or a.get("shell_id"),\n'
     '            "type": a.get("type") or a.get("anchor_type"),\n'
     '            "authority": a.get("required_authority") or a.get("authoritative_owner"),\n'
     "        })\n",

     "        norm.append({\n"
     '            "id": _anchor_identity(a),\n'
     '            "type": a.get("type") or a.get("anchor_type"),\n'
     '            "authority": a.get("required_authority") or a.get("authoritative_owner"),\n'
     '            "at": [a.get("x"), a.get("y"), a.get("z")],\n'
     '            "facing": a.get("facing"),\n'
     "        })\n"),

    (LOCK,
     '        "collision_hulls": gameplay.get("collision_hulls", []),\n'
     '        "doorways": gameplay.get("doorways", []),\n'
     "    }\n"
     "\n"
     "\n"
     "def _route_graph(gameplay: dict) -> dict:\n"
     "    return {\n"
     '        "route": gameplay.get("route", gameplay.get("route_graph", {})),\n'
     '        "nav_hints": gameplay.get("nav_hints", {}),\n'
     "    }\n",

     "        # Lot's vocabulary. `collision_hulls` and `doorways` were read\n"
     "        # here and Lot has never published either; see\n"
     "        # docs/FUNCTIONAL_LOCK.md for what it publishes instead.\n"
     '        "openings": gameplay.get("openings", []),\n'
     '        "vertical_links": gameplay.get("vertical_links", []),\n'
     "        # NODE NAMES ONLY. The material dict beside them is rewritten by\n"
     "        # Patina and Pixelcoat during the art pass; hashing it would\n"
     "        # report drift on every normal run, and a gate that cries drift\n"
     "        # gets switched off.\n"
     '        "collision_nodes": _collision_nodes(gameplay),\n'
     "        # Which mesh each building's collision came from. Swapping a\n"
     "        # source glb is exactly this gate's job and need not rename a\n"
     "        # single node.\n"
     '        "ground_sources": _ground_sources(gameplay),\n'
     "    }\n"),

    (LOCK,
     'def _collision_signature(gameplay: dict) -> dict:\n',

     "def _collision_nodes(gameplay: dict) -> list[str]:\n"
     '    """Every collision node name Lot published, sorted and de-duped."""\n'
     "    out = set()\n"
     '    for s in gameplay.get("surfaces") or []:\n'
     '        if isinstance(s, dict) and s.get("node"):\n'
     '            out.add(str(s["node"]))\n'
     "    return sorted(out)\n"
     "\n"
     "\n"
     "def _ground_sources(gameplay: dict) -> dict:\n"
     '    """Each building -> the mesh its collision came from."""\n'
     '    ground = gameplay.get("ground") or {}\n'
     "    if not isinstance(ground, dict):\n"
     "        return {}\n"
     "    return {str(k): (v or {}).get(\"source\")\n"
     "            for k, v in sorted(ground.items())\n"
     "            if isinstance(v, dict)}\n"
     "\n"
     "\n"
     "def _collision_signature(gameplay: dict) -> dict:\n"),

    (LOCK,
     '    schema: str = "level_factory.functional_lock.v0.1"\n',
     "    schema: str = SCHEMA\n"),

    (LOCK, "    route_graph_hash: str = \"\"\n", ""),

    (LOCK, '            "route_graph_hash": self.route_graph_hash,\n', ""),

    (LOCK, "        route_graph_hash=hash_json(_route_graph(gameplay)),\n", ""),

    (LOCK,
     "    if hash_json(_route_graph(gameplay)) != lock.route_graph_hash:\n"
     '        drift.append("route graph changed after art pass")\n',
     ""),

    (LOCK,
     "    site_unguarded: bool = False\n",
     "    site_unguarded: bool = False\n"
     "    #: The lock predates the current signature definitions, so nothing\n"
     "    #: was compared. NOT drift -- reporting a version skew as drift\n"
     "    #: would block every export on a schema bump and teach the reader\n"
     "    #: that drift means nothing. `passed` is False with no drift\n"
     "    #: entries: a comparison that did not happen did not pass.\n"
     "    needs_recompute: bool = False\n"),

    (LOCK,
     "    gameplay = _merged_gameplay(post_art_site_gameplay_path, post_art_deli_gameplay_path)\n"
     "    drift: list[str] = []\n",

     "    gameplay = _merged_gameplay(post_art_site_gameplay_path, post_art_deli_gameplay_path)\n"
     "    coverage = signature_coverage(\n"
     "        gameplay, _load(post_art_site_gameplay_path))\n"
     "    if str(getattr(lock, \"schema\", \"\")) != SCHEMA:\n"
     "        return RegressionResult(\n"
     "            mission_id=lock.mission_id, passed=False, drift=[],\n"
     "            needs_recompute=True,\n"
     '            vacuous_lock=bool(coverage.get("vacuous")),\n'
     '            site_unguarded=bool(coverage.get("guards_no_site")),\n'
     "            coverage=coverage)\n"
     "    drift: list[str] = []\n"),

    (LOCK,
     '                "drift": self.drift, "vacuous_lock": self.vacuous_lock,\n'
     '                "site_unguarded": self.site_unguarded,\n'
     '                "coverage": self.coverage}\n',
     '                "drift": self.drift, "vacuous_lock": self.vacuous_lock,\n'
     '                "site_unguarded": self.site_unguarded,\n'
     '                "needs_recompute": self.needs_recompute,\n'
     '                "coverage": self.coverage}\n'),

    (COMMANDS,
     "        if regression.vacuous_lock or regression.site_unguarded:\n",

     "        if regression.needs_recompute:\n"
     "            # NOT DRIFT, and not a pass either. The lock predates the\n"
     "            # current signature definitions, so nothing was compared.\n"
     '            print(f"[export] the functional lock for {mission_id} "\n'
     '                  f"predates the current signature definitions; "\n'
     '                  f"nothing was compared. Recompute it with "\n'
     '                  f"approve --gate functional_shell_locked.",\n'
     "                  file=sys.stderr)\n"
     "        elif regression.vacuous_lock or regression.site_unguarded:\n"),
]

_CRLF = "\r\n"

ENTRY = """## [0.29.0] - the lock protects the site

The repair. `docs/FUNCTIONAL_LOCK.md`, accepted 2026-08-14, is the spec;
every decision here is argued there.

    collision_fingerprint   + surfaces node names, ground sources,
                              openings, vertical_links
    anchor_registry_hash    markers, keyed on `name`, WITH position
    route_graph_hash        retired

- **`surfaces` contributes node names only.** The material dict beside each
  node is rewritten by Patina and Pixelcoat during the art pass; hashing it
  would report drift on every normal run, and a gate that cries drift gets
  switched off. A lock that never fires and a lock that always fires protect
  the same amount.
- **`ground` contributes each building's source glb.** Swapping a building's
  mesh is exactly what this gate is for and need not rename a single node.
- **`openings` and `vertical_links` are hashed whole**, breach fields
  included. A door that stops being vaultable is a functional change even if
  it does not move. Lot's four `vertical_links` are a different population
  from Deli's two `stair_systems`, not a replacement: both are kept.
- **`markers` replaces `anchors`, keyed on `name`.** `id` is `"FRONT"` scoped
  to a building and every building has one; the old registry sorted and keyed
  on `id`, so two distinct anchors normalised to identical entries and it
  silently under-counted.
- **Anchor position joins the registry, and that is a change of meaning.**
  The art pass could move every spawn point in the level and the hash would
  not move. Nothing else checks anchor position either.
- **`route_graph_hash` is retired**, not left hashing two empty dicts. An
  empty signature is not neutral -- it reads as coverage, and its drift
  message has never been capable of firing. Nothing in the factory publishes
  a route graph; if one is wanted it belongs in `lot`'s output contract.
- **`collision` is deliberately not used.** It is a four-field report
  (`colliders: 1067`) and a count is a weak fingerprint: geometry can be
  replaced wholesale at 1067 colliders. It looks like the obvious mapping and
  it is the wrong one.

SCHEMA v0.2, AND A MISMATCH IS NOT DRIFT

The signatures change definition, so an old lock and a new one are not
comparable; diffing them reports every field as drift, for every mission,
immediately. That is version skew. `verify_no_drift` now returns
`needs_recompute` with the comparison SKIPPED, `passed` False and `drift`
empty -- a comparison that did not happen did not pass, and calling it drift
would block every export on a version bump and teach the next reader that
drift means nothing.

THE DELI BACKFILL STAYS AND IS NOW VISIBLE

`stair_systems`, `ladders`, `platforms`, `fire_escapes` still come from Deli.
That was never wrong. What was wrong is that it silently propped up a
signature carrying nothing else, which is why the whole thing looked healthy
for months. `coverage.backfilled_from_deli` names them now.

NOT DONE HERE

`LOCK_COVERAGE_ENFORCED` stays False. The order the doc sets is: land the
mapping, recompute a real lock, confirm `guards_no_site` is false, then flip
and name the mission that earned it. Recomputing `lot_demo_001` needs
`approve --gate functional_shell_locked`, which resolves job paths through
the `seed_XXXX` marker -- so the marker has to be repaired first. That is the
next patch.

Whether Lot's `vertical_links` need splitting by `kind` is open: all four are
`hatch`, which is too small a sample to decide.
"""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
    if not (root / DOC).is_file():
        print(f"REFUSING: {DOC} is not here. The spec goes first -- run "
              f"patch_functional_lock_doc.py.")
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
            if new and new in out:
                done += 1
                continue
            if not new and old not in out:
                done += 1
                continue
            if out.count(old) != 1:
                print(f"REFUSING: {rel} -- an anchor occurs {out.count(old)} "
                      f"time(s), expected 1:\n    "
                      f"{old.strip().splitlines()[0][:72]}")
                return 1
            out = out.replace(old, new, 1)

        if rel == LOCK:
            for gone in ("_route_graph", "route_graph_hash"):
                if gone in out:
                    print(f"REFUSING: {rel} still mentions {gone} after the "
                          f"edit")
                    return 1

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

    check("route_graph_hash is gone from the protected set",
          "route_graph_hash" not in lk.PROTECTED_KEYS)
    check("and the module no longer defines it",
          not hasattr(lk, "_route_graph"))
    check("the schema is v0.2", lk.SCHEMA.endswith("v0.2"))
    check("the backfill no longer claims anchors",
          "anchors" not in lk.BACKFILLED_FROM_DELI)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        def w(name, data):
            p = tmp / name
            p.write_text(json.dumps(data), encoding="utf-8")
            return p

        # THE REAL SHAPE, from tools/probe_site_vocabulary.py.
        site_data = {
            "buildings": [{"id": "b0"}],
            "collision": {"colliders": 1067, "complete": True},
            "openings": [{"kind": "door", "building": "b0", "wall": "ext_0_N",
                          "width": 1.8, "height": 2.2, "sill": 0.0,
                          "vaultable": False, "x": 8.5, "y": 12.0, "z": 1.1}],
            "vertical_links": [{"kind": "hatch", "building": "b1", "story": 2,
                                "x": 13.0, "y": -9.0}],
            "markers": [
                {"id": "FRONT", "name": "b0/ATTACKER_SPAWN_FRONT",
                 "type": "attacker_spawn", "building": "b0", "room": "hall",
                 "x": -77.0, "y": -65.0, "z": 0},
                # SAME `id`, different building -- the collision the old
                # registry could not see.
                {"id": "FRONT", "name": "b1/ATTACKER_SPAWN_FRONT",
                 "type": "attacker_spawn", "building": "b1",
                 "x": 10.0, "y": 2.0, "z": 0}],
            "site_markers": [],
            "surfaces": [{"node": "b0/ext_col_0_N_seg0",
                          "material": {"id": "glass", "absorption": 0.1}},
                         {"node": "b0/ext_col_0_N_seg1",
                          "material": {"id": "brick"}}],
            "ground": {"b0": {"source": "mansion_a02.glb", "state": "present"}},
        }
        site = w("site.json", site_data)
        deli = w("deli.json", {"stair_systems": [{"id": "s1"}, {"id": "s2"}],
                               "ladders": [], "platforms": [],
                               "fire_escapes": []})

        lock = lk.compute_lock(mission_id="m1",
                               candidate_id="m1.candidate.seed_1", seed=1,
                               site_gameplay_path=site,
                               deli_gameplay_path=deli)
        cov = lock.coverage
        check("THE SITE NOW CONTRIBUTES -- guards_no_site is false",
              cov["guards_no_site"] is False)
        check("and it is not vacuous", cov["vacuous"] is False)
        check("every protected key the site publishes is named",
              set(cov["site_contributes"]) ==
              {"openings", "vertical_links", "surfaces", "ground", "markers"})
        check("the Deli backfill is visible, not silent",
              set(cov["signatures"]["collision_fingerprint"]
                  ["backfilled_from_deli"]) == {"stair_systems"})
        check("nothing is reported unguarded", cov["unguarded"] == [])

        # The registry.
        reg = lk._anchor_registry(lk._merged_gameplay(site, deli))
        check("two same-id anchors are now two distinct entries",
              len(reg) == 2 and reg[0]["id"] != reg[1]["id"])
        check("identity is the namespaced name",
              reg[0]["id"] == "b0/ATTACKER_SPAWN_FRONT")
        check("and position is in the registry",
              reg[0]["at"] == [-77.0, -65.0, 0])

        # Moving an anchor is now drift. It was not.
        moved = dict(site_data)
        moved["markers"] = [dict(site_data["markers"][0], x=-70.0),
                            site_data["markers"][1]]
        r = lk.verify_no_drift(lock, w("moved.json", moved), deli)
        check("MOVING A SPAWN POINT IS NOW DRIFT",
              not r.passed and any("anchor" in d for d in r.drift))

        # Materials churn without tripping it.
        arted = json.loads(json.dumps(site_data))
        for s in arted["surfaces"]:
            s["material"] = {"id": "patina_worn", "absorption": 0.9}
        r2 = lk.verify_no_drift(lock, w("arted.json", arted), deli)
        check("REWRITING EVERY MATERIAL IS NOT DRIFT", r2.passed)

        # But losing a collision node is.
        fewer = json.loads(json.dumps(site_data))
        fewer["surfaces"] = fewer["surfaces"][:1]
        r3 = lk.verify_no_drift(lock, w("fewer.json", fewer), deli)
        check("losing a collision node IS drift",
              not r3.passed and any("collision" in d for d in r3.drift))

        # And swapping a source mesh is, at identical node names.
        swapped = json.loads(json.dumps(site_data))
        swapped["ground"]["b0"]["source"] = "mansion_b01.glb"
        r4 = lk.verify_no_drift(lock, w("swapped.json", swapped), deli)
        check("swapping a source glb IS drift, at identical node names",
              not r4.passed)

        # A door that stops being vaultable.
        vault = json.loads(json.dumps(site_data))
        vault["openings"][0]["vaultable"] = True
        r5 = lk.verify_no_drift(lock, w("vault.json", vault), deli)
        check("a door that stops being vaultable IS drift", not r5.passed)

        # Schema skew is not drift.
        old = lk.FunctionalLock.from_dict(
            dict(lock.as_dict(), schema="level_factory.functional_lock.v0.1"))
        r6 = lk.verify_no_drift(old, site, deli)
        check("an old-schema lock reports needs_recompute",
              r6.needs_recompute is True)
        check("and reports NO drift entries", r6.drift == [])
        check("and does not claim to have passed", r6.passed is False)
        check("it reaches anyone reading the json",
              r6.as_dict()["needs_recompute"] is True)

        # A fresh lock does not.
        r7 = lk.verify_no_drift(lock, site, deli)
        check("a current lock compares normally",
              r7.needs_recompute is False and r7.passed)

    cmds = (root / COMMANDS).read_text(encoding="utf-8")
    check("cmd_export reports needs_recompute separately from vacuous",
          "if regression.needs_recompute:" in cmds
          and "elif regression.vacuous_lock or regression.site_unguarded:"
          in cmds)

    v = (root / VERSION_F).read_text(encoding="utf-8")
    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    check(f"VERSION is {NEW_V}", NEW_V in v)
    check(f"one {NEW_V} entry", cl.count(f"## [{NEW_V}]") == 1)
    flat = " ".join(cl.split())
    check("the entry says why materials are excluded",
          "gate that cries drift gets switched off" in flat)
    check("and why `collision` was rejected", "colliders: 1067" in flat)
    check("and that a schema mismatch is not drift",
          "did not happen did not pass" in flat)
    check("and what is still not done",
          "NOT DONE HERE" in cl and "seed_XXXX" in cl)

    print()
    print("  the site is protected, materials are not, and skew is not drift"
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
        print("    python patches\\patch_lf_029.py --selftest")
        print("    python -m pytest level_factory/tests/unit -q")
        print()
        print("  THEN THE EXPORT SHOULD CHANGE ITS TUNE. lot_demo_001's lock")
        print("  is v0.1, so expect 'predates the current signature")
        print("  definitions' rather than 'protects no site data':")
        print("    python -m level_factory -C workspaces\\lot-demo-ws \\")
        print("        export lot_demo_001 --mode portable-godot")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
