"""The DAG section of PIPELINE_MAP.md, derived from the planner instead of typed.

    python factory_map.py                 # print the generated section
    python factory_map.py --check         # compare it to PIPELINE_MAP.md, exit 1 on drift
    python factory_map.py --write         # rewrite the section in place
    python factory_map.py --selftest      # prove the derivation before trusting it

Run from the factory root (the file must SIT there -- it locates
`level_factory/packages` relative to itself, so cwd does not matter).

## Why this exists

`PIPELINE_MAP.md` is the architecture document and its DAG table is hand-typed,
so it drifts silently. Measured 2026-08-09, before this script existed:

    walktest_navqa          named nowhere in PIPELINE_MAP.md
    themed_site_assemble    named nowhere in PIPELINE_MAP.md
    regression              named nowhere in PIPELINE_MAP.md
    lux_apply               documented as depending on presentation_compose;
                            planner.py line 415 says themed_site_assemble
    patina_apply            documented as emitting shell.patina.*; the planner
                            has used `stem = aid or "shell"` since the kit
                            fan-out, so it is <archetype>.patina.*
    "everything below the gate runs once, on the selected candidate only"
                            false for six stages since the fan-out landed

None of that is visible to a reader, which is the whole problem. `build_freshness.py`
exists because a shell older than the code that produced it reported with full
confidence; a doc older than the planner does the same thing, and nothing checked.

## How it derives, rather than restates

It IMPORTS `plan_mission` and plans a real mission against a synthetic library,
then reads the graph back. Nothing here knows the stage list, the edges or the
scopes -- they are measurements of the object the pipeline actually builds. A
stage added to `planner.py` appears here on the next run without this file
changing, which is the point (`library_themed_fit.py` makes the same argument
about the fitness rule at length).

SCOPE IS DERIVED, NOT DECLARED:

    archetype  the stage's jobs carry `archetype_id` -- it bakes against ONE
               building. Getting this wrong is the defect this repo keeps
               finding: kit, dressing and fixtures were each planned once per
               mission and attached to five buildings.
    candidate  one job per candidate, and no archetype -- it runs before the
               lock, on every seed.
    mission    exactly one job for the whole run.

The synthetic brief uses 3 candidates and 2 buildings ON PURPOSE, so the two
counts cannot be confused with each other. Two of each would make a
candidate-scoped stage and an archetype-scoped stage indistinguishable by count
alone, and the `archetype_id` test would be carrying the whole answer untested.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "level_factory"))

DOC = ROOT / "PIPELINE_MAP.md"
BEGIN = "<!-- BEGIN GENERATED: factory_map.py -- do not edit by hand -->"
END = "<!-- END GENERATED -->"

#: Deliberately not 2 and 2 -- see the module docstring.
CANDIDATES = 3
BUILDINGS = 2
FAMILIES = ("alpha", "bravo", "charlie")


def _library(root: Path) -> Path:
    """A minimum themeable Deli Counter build dir: what `index` and
    `themed_fitness` actually read, and nothing else.

    The manifests carry CONTENT. Written as the literal `{}` they are a
    faithful stand-in for a library of holed, never-judged buildings, and
    `require_themed_shells` correctly refuses the lot -- which is how thirteen
    fan-out tests died on 2026-08-08 telling the exact truth about their
    fixture."""
    root.mkdir(parents=True, exist_ok=True)
    for fam in FAMILIES:
        aid = f"{fam}_a01"
        (root / f"{aid}.glb").write_text("{}", encoding="utf-8")
        (root / f"{aid}.gameplay.json").write_text("{}", encoding="utf-8")
        (root / f"{aid}.slots.json").write_text(
            json.dumps({"coverage": {"wall": 96, "doorway": 4}}), encoding="utf-8")
        (root / f"{aid}.lights.json").write_text("{}", encoding="utf-8")
        (root / f"{aid}.navgate.json").write_text(json.dumps(
            {"markers": {"interior_checked": 1, "interior_reachable": 1},
             "navigable": True,
             "navigable_reason": "synthetic: factory_map fixture"}),
            encoding="utf-8")
        (root / f"{aid}.validation.json").write_text(
            json.dumps({"facade": False}), encoding="utf-8")
    return root


def plan(library: Path, gameplay: bool = True):
    """The real graph, from the real planner."""
    from packages.core.ids import candidate_id
    from packages.core.models import MissionBrief
    from packages.pipeline import planner as P

    brief = MissionBrief(
        mission_id="factory_map", display_name="factory_map",
        archetype="depot", theme="rockay",
        candidate_count=CANDIDATES, building_count=BUILDINGS,
        lot_library=str(library))
    seeds = P.derive_seeds(5000, CANDIDATES)
    layers = {P.LAYER_ART} | ({P.LAYER_GAMEPLAY} if gameplay else set())
    return P.plan_mission(
        brief, seed_base=5000, layers=layers,
        selected_candidate=candidate_id(brief.mission_id, seeds[0]))


def stages(pl) -> list[dict]:
    """One row per stage, in the graph's own topological order."""
    order, by_stage = [], {}
    for job in pl.graph.topological_order():
        if job.stage_id not in by_stage:
            by_stage[job.stage_id] = []
            order.append(job.stage_id)
        by_stage[job.stage_id].append(job)
    stage_of = {j.job_id: j.stage_id for j in pl.graph.jobs()}

    rows = []
    for sid in order:
        jobs = by_stage[sid]
        j = jobs[0]
        if any(x.archetype_id for x in jobs):
            scope = "archetype"
        elif len({x.candidate_id for x in jobs}) == CANDIDATES:
            scope = "candidate"
        else:
            scope = "mission"
        deps, seen = [], set()
        for x in jobs:
            for d in x.depends_on:
                s = stage_of.get(d, d)
                if s not in seen:
                    seen.add(s)
                    deps.append(s)
        outs = [o.replace(str(j.archetype_id), "<archetype>")
                if j.archetype_id else o for o in (j.expected_outputs or [])]
        rows.append(dict(stage=sid, adapter=j.adapter_id,
                         resource=j.resource_class, scope=scope,
                         deps=deps, outputs=outs, count=len(jobs)))

    # DEPTH, not the graph's topological order. Topological order is not unique
    # and the one the graph happens to yield interleaves the scopes -- it put
    # `zoo_fixtures_build` above `walktest_navqa`, so the "candidate locked"
    # marker landed above two stages that run before the lock. Depth is the
    # longest path from a root, which is what a reader means by "a layer".
    depth, by_stage_row = {}, {r["stage"]: r for r in rows}

    def _d(sid, seen=()):
        if sid in depth:
            return depth[sid]
        if sid in seen:                      # cannot happen in a DAG; do not hang
            return 0
        r = by_stage_row.get(sid)
        v = 0 if not r or not r["deps"] else 1 + max(
            _d(x, seen + (sid,)) for x in r["deps"])
        depth[sid] = v
        return v

    topo = {r["stage"]: i for i, r in enumerate(rows)}
    rows.sort(key=lambda r: (0 if r["scope"] == "candidate" else 1,
                             _d(r["stage"]), topo[r["stage"]]))
    return rows


def render(rows: list[dict], gameplay_only=frozenset()) -> str:
    """The markdown block. Anything a reader needs that the graph does not
    carry -- why an edge exists, what a stage is FOR -- belongs in the prose
    around this block, not in it."""
    out = [BEGIN, "",
           "| Stage | Adapter | Resource | Scope | Depends on | Expected outputs |",
           "|---|---|---|---|---|---|"]
    gate_done = False
    for r in rows:
        if not gate_done and r["scope"] != "candidate":
            out.append("| *candidate selected + functional shell locked* | | | "
                       "| | |")
            gate_done = True
        deps = ", ".join(f"`{d}`" for d in r["deps"]) or "—"
        outs = ", ".join(f"`{o}`" for o in r["outputs"]) \
            or "*named at exec; the adapter validates*"
        out.append(f"| `{r['stage']}` | {r['adapter']} | {r['resource']} | "
                   f"{r['scope']} | {deps} | {outs} |")
    n_c = sum(1 for r in rows if r["scope"] == "candidate")
    n_a = sum(1 for r in rows if r["scope"] == "archetype")
    n_m = sum(1 for r in rows if r["scope"] == "mission"
              and r["stage"] not in gameplay_only)
    gm = ", ".join(f"`{s}`" for s in sorted(gameplay_only))
    out += ["",
            f"**{len(rows)} stages: {n_c} per candidate, {n_a} per archetype, "
            f"{n_m + len(gameplay_only)} once per mission.** An `--art` run "
            f"plans `{n_c}N + {n_a}M + {n_m}` jobs for N candidates and M "
            f"placed buildings"
            + (f"; `--gameplay` adds {gm}." if gm else "."),
            "",
            "SCOPE IS THE COLUMN TO READ. Every art defect found between "
            "2026-08-06 and 2026-08-09 was a stage computing at a coarser "
            "scope than the thing it described: dressing and fixtures planned "
            "per mission and attached to five buildings, then the kit doing "
            "the same with `exact`-fit modules cut to one building's slots.",
            "", END]
    return "\n".join(out)


def generated() -> str:
    tmp = Path(tempfile.mkdtemp(prefix="factory_map_"))
    try:
        lib = _library(tmp / "build")
        full = stages(plan(lib, gameplay=True))
        art = {r["stage"] for r in stages(plan(lib, gameplay=False))}
        return render(full, frozenset(r["stage"] for r in full
                                      if r["stage"] not in art))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------------------------ selftest
def _selftest() -> int:
    """Prove the derivation before printing a table built on it.

    Two things can be silently wrong here and both have precedent in this repo:
    a scope rule that cannot distinguish its cases, and a fixture that agrees
    with a broken reader. So the scopes are asserted against what the planner's
    own docstrings say they are, and the fan-out is asserted to actually fan --
    a stage claiming `archetype` scope with one job is the 2026-08-09 bug
    wearing the right label.
    """
    bad = 0
    tmp = Path(tempfile.mkdtemp(prefix="factory_map_st_"))
    try:
        rows = {r["stage"]: r for r in stages(plan(_library(tmp / "build")))}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    want = {
        "deli_generate": ("candidate", CANDIDATES),
        "lot_assemble": ("candidate", CANDIDATES),
        "walktest_navqa": ("candidate", CANDIDATES),
        "laser_tag_evaluate": ("candidate", CANDIDATES),
        "pixelcoat_build": ("mission", 1),
        "zoo_kit_build": ("archetype", BUILDINGS),
        "patina_apply": ("archetype", BUILDINGS),
        "patina_dressing": ("archetype", BUILDINGS),
        "zoo_dressing_build": ("archetype", BUILDINGS),
        "zoo_fixtures_build": ("archetype", BUILDINGS),
        "lux_fixture_gate": ("archetype", BUILDINGS),
        "presentation_compose": ("mission", 1),
        "themed_site_assemble": ("mission", 1),
        "lux_apply": ("mission", 1),
        "dispatch_handoff": ("mission", 1),
    }
    for sid, (scope, count) in sorted(want.items()):
        r = rows.get(sid)
        if r is None:
            print(f"[selftest] {sid:22} MISSING from the planned graph")
            bad += 1
            continue
        ok = r["scope"] == scope and r["count"] == count
        bad += not ok
        print(f"[selftest] {sid:22} {r['scope']:9} x{r['count']}  "
              f"{'ok' if ok else f'FAIL want {scope} x{count}'}")

    extra = sorted(set(rows) - set(want))
    if extra:
        # Not a failure: a new stage is exactly what this script exists to
        # surface. It IS a prompt to give it a line of prose in PIPELINE_MAP.
        print(f"[selftest] NEW STAGE(S) not yet in this selftest: "
              f"{', '.join(extra)} -- add them here and describe them in the "
              f"prose around the generated block")

    # The edge PIPELINE_MAP got wrong, pinned so it cannot go stale twice.
    lux = rows.get("lux_apply", {})
    ok = lux.get("deps") == ["themed_site_assemble"]
    bad += not ok
    print(f"[selftest] lux_apply deps    {lux.get('deps')}  "
          f"{'ok' if ok else 'FAIL want [themed_site_assemble]'}")

    if bad:
        print("[selftest] the derivation is wrong; the table below it would be "
              "a document, not a measurement")
        return 1
    print("[selftest] scopes, fan-out counts and the lux edge all derived "
          "correctly")
    return 0


def _doc_block(text: str):
    if BEGIN not in text or END not in text:
        return None
    return text[text.index(BEGIN): text.index(END) + len(END)]


def _audit(text: str, rows: list[dict]) -> int:
    """What the hand-written doc says that the planner does not. Only used
    when the generated markers are absent -- once they are in, the diff IS the
    audit."""
    missing = [r["stage"] for r in rows if f"`{r['stage']}`" not in text
               and r["stage"] not in text]
    print(f"  {len(rows)} stages planned; "
          f"{len(missing)} named nowhere in {DOC.name}")
    for s in missing:
        print(f"    ABSENT  {s}")
    return 1 if missing else 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return _selftest()
    if _selftest():
        return 1
    print()
    block = generated()

    if "--check" not in argv and "--write" not in argv:
        print(block)
        return 0

    if not DOC.is_file():
        print(f"not found: {DOC}")
        return 2
    text = DOC.read_text(encoding="utf-8")
    current = _doc_block(text)

    if "--write" in argv:
        if current is None:
            print(f"{DOC.name} has no generated block yet. Paste the section "
                  f"above in place of the hand-written DAG table, markers "
                  f"included, then --write and --check will maintain it.")
            return 2
        DOC.write_text(text.replace(current, block), encoding="utf-8")
        print(f"  rewrote the generated block in {DOC.name}")
        return 0

    if current is None:
        print(f"  {DOC.name} has no generated block; auditing by name instead")
        tmp = Path(tempfile.mkdtemp(prefix="factory_map_a_"))
        try:
            rows = stages(plan(_library(tmp / "build")))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        return _audit(text, rows)

    if current == block:
        print(f"  {DOC.name} matches the planner")
        return 0
    print(f"  {DOC.name} HAS DRIFTED from the planner. Diff:")
    import difflib
    for line in difflib.unified_diff(
            current.splitlines(), block.splitlines(),
            fromfile=f"{DOC.name} (committed)", tofile="planner.py (derived)",
            lineterm="", n=1):
        print("    " + line)
    print("  run --write to regenerate")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
