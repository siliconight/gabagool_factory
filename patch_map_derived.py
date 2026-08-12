"""PIPELINE_MAP.md's DAG table, derived from the planner instead of typed.

    python patch_map_derived.py --check     # verify targets, write nothing
    python patch_map_derived.py             # apply
    python patch_map_derived.py --revert    # restore from the .pre_derived sidecar

Adds `factory_map.py` at the factory root and replaces the hand-typed DAG table
in PIPELINE_MAP.md with a generated block between markers, plus the prose the
old table got wrong.

MEASURED BEFORE THIS EXISTED. `factory_map.py --check` on the unpatched tree:

    15 stages planned; 2 named nowhere in PIPELINE_MAP.md
      ABSENT  walktest_navqa
      ABSENT  themed_site_assemble

and beyond the names: `lux_apply` was documented as depending on
`presentation_compose` when planner.py line 415 says `themed_site_assemble`;
`patina_apply` was documented as emitting `shell.patina.*` when the planner has
used `stem = aid or "shell"` since the kit fan-out; and "everything below the
gate runs once, on the selected candidate only" had been false for six stages
since the same change. None of it was visible to a reader.

WHAT THE SCRIPT DOES. It imports `plan_mission`, plans a real mission against a
synthetic themeable library, and reads the graph back. It knows no stage names,
no edges and no scopes -- they are measurements. A stage added to planner.py
appears on the next run with this file unchanged.

SCOPE IS DERIVED. `archetype` when the stage's jobs carry `archetype_id`,
`candidate` when there is one job per candidate, `mission` when there is one.
The synthetic brief uses 3 candidates and 2 buildings on purpose so the two
counts cannot be confused. `--selftest` asserts every stage's scope and fan-out
count and pins the `lux_apply` edge; both were put wrong on purpose and both
fail it.

THE POINT IS THE GATE, NOT THE TABLE. `--check` exits non-zero when the doc and
the planner disagree, so the map can be wired into the same habit
`build_freshness.py` already established for shells: an artefact older than the
thing that produces it reports with full confidence, and nothing was checking
this one.

REFUSES on any target whose bytes are not what this patch was written against --
a whole-file SHA-256, so a drifted file cannot be half-patched.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

SIDECAR = ".pre_derived"
ROOT = Path(__file__).resolve().parent

TARGETS = [
    {
        "rel": 'PIPELINE_MAP.md',
        "pre_sha": '7ac6bd2e72733009dbb62c75d05f403065e488a2872840794d632e53447f82fb',
        "post_sha": 'f20d8bfc140223b2635bf34d0003655d76f5ebc146e67084bf5ba443ffb22606',
        "pre_bytes": 25708, "post_bytes": 28247,
        "hunks": [
            ('5219, 5320, 5421.\n\n## The DAG\n\nDefined in `packages/pipeline/planner.py::plan_mission`. Graybox runs per\ncandidate; everything below the gate runs once, on the selected candidate only.\n\n| Stage | Adapter | Resource | Depends on | Expected outputs |\n|---|---|---|---|---|\n| `deli_generate` | deli_counter | blender | — | `shell.glb`, `shell.gameplay.json`, `shell.slots.json`, `shell.manifest.json`, `shell.lights.json` |\n| `lot_assemble` | lot | python_cpu | deli | `site.tscn`, `site_walk.tscn`, `site.site.gameplay.json`, `site.site.lights.json` |\n| `laser_tag_evaluate` | laser_tag | godot_headless | lot | `lasertag.report.json`, `lasertag.report.csv` |\n| *candidate selected + functional shell locked* | | | | |\n| `pixelcoat_build` | pixelcoat | python_cpu | lot | `<kind>_<theme>/` skin library (dynamic; adapter validates) |\n| `zoo_kit_build` | zoo | blender | lot, pixelcoat | named by `building_id` at exec; adapter validates |\n| `patina_apply` | patina | python_cpu | lot | `shell.patina.glb`, `shell.patina.json`, `shell.patina.gameplay.json` |\n| `patina_dressing` | patina | python_cpu | patina_apply | the above plus `shell.patina.dressing.json` |\n| `zoo_dressing_build` | zoo | blender | patina_dressing, zoo_kit | named by `building_id` at exec |\n| `zoo_fixtures_build` | zoo | blender | deli (selected) | named by `scope_id` at exec |\n| `presentation_compose` | presentation | python_cpu | deli, zoo_kit, zoo_dressing, zoo_fixtures | `presentation/site.tscn` |\n| `lux_apply` | lux | godot_headless | presentation_compose | `lux.applied.tscn`, `lux.quality.json`, `lux.validation.json` |\n| `lux_fixture_gate` | lux | godot_headless | zoo_fixtures | `fixture_gate.report.json` |\n| `dispatch_handoff` | dispatch | python_cpu | lux (with Art) or lot (without) | `mission.tscn`, `mission_manifest.json`, `gameplay_anchors.json`, `runtime_ownership_requirements.json`, `proposed_beat_graph.json`, `navigation_hints.json`, `build.lock.json`, `HANDOFF.md` |\n\nTwo edges are easy to miss. `presentation_compose` is what makes `--art` mean\n"themed level" rather than "grey level with a lighting pass" — it fits themed\nZoo modules onto the greybox slot footprints while keeping greybox floors and\ncollision as the walkable base. And `lux_apply` runs over that *composed* scene,\nnot over the raw Lot site.\n\n## The repos\n\n**level_factory** — orchestrator. `packages/` holds the engine (pipeline,\n',
             '5219, 5320, 5421.\n\n## The DAG\n\nDefined in `packages/pipeline/planner.py::plan_mission`. **The table below is\ngenerated — do not edit it by hand.** `python factory_map.py --write` derives it\nby planning a real mission against a synthetic library and reading the graph\nback; `--check` exits non-zero when the table and the planner disagree, and\n`--selftest` proves the derivation before either. The hand-typed version this\nreplaced had drifted by two missing stages, one wrong edge and one wrong output\nname, and none of it was visible to a reader — the same failure `build_freshness.py`\nexists to stop one layer down.\n\n<!-- BEGIN GENERATED: factory_map.py -- do not edit by hand -->\n\n| Stage | Adapter | Resource | Scope | Depends on | Expected outputs |\n|---|---|---|---|---|---|\n| `deli_generate` | deli_counter | blender | candidate | — | `shell.glb`, `shell.gameplay.json`, `shell.slots.json`, `shell.manifest.json`, `shell.lights.json` |\n| `lot_assemble` | lot | python_cpu | candidate | `deli_generate` | `site.tscn`, `site_walk.tscn`, `site.site.gameplay.json`, `site.site.lights.json` |\n| `laser_tag_evaluate` | laser_tag | godot_headless | candidate | `lot_assemble` | `lasertag.report.json`, `lasertag.report.csv` |\n| `walktest_navqa` | walktest | godot_headless | candidate | `lot_assemble` | `site_navqa.walktest.json` |\n| *candidate selected + functional shell locked* | | | | | |\n| `zoo_fixtures_build` | zoo | blender | archetype | `deli_generate` | *named at exec; the adapter validates* |\n| `patina_apply` | patina | python_cpu | archetype | `lot_assemble` | `<archetype>.patina.glb`, `<archetype>.patina.json`, `<archetype>.patina.gameplay.json` |\n| `pixelcoat_build` | pixelcoat | python_cpu | mission | `lot_assemble` | *named at exec; the adapter validates* |\n| `lux_fixture_gate` | lux | godot_headless | archetype | `zoo_fixtures_build` | `fixture_gate.report.json` |\n| `patina_dressing` | patina | python_cpu | archetype | `patina_apply` | `<archetype>.patina.glb`, `<archetype>.patina.json`, `<archetype>.patina.gameplay.json`, `<archetype>.patina.dressing.json` |\n| `zoo_kit_build` | zoo | blender | archetype | `lot_assemble`, `pixelcoat_build` | *named at exec; the adapter validates* |\n| `zoo_dressing_build` | zoo | blender | archetype | `patina_dressing`, `zoo_kit_build` | *named at exec; the adapter validates* |\n| `presentation_compose` | presentation | python_cpu | mission | `deli_generate`, `zoo_kit_build`, `zoo_dressing_build`, `zoo_fixtures_build` | `presentation/site.tscn` |\n| `themed_site_assemble` | lot | python_cpu | mission | `presentation_compose` | `site.tscn` |\n| `lux_apply` | lux | godot_headless | mission | `themed_site_assemble` | `lux.applied.tscn`, `lux.quality.json`, `lux.validation.json` |\n| `dispatch_handoff` | dispatch | python_cpu | mission | `lux_apply` | `mission.tscn`, `mission_manifest.json`, `gameplay_anchors.json`, `runtime_ownership_requirements.json`, `proposed_beat_graph.json`, `navigation_hints.json`, `build.lock.json`, `HANDOFF.md` |\n\n**15 stages: 4 per candidate, 6 per archetype, 5 once per mission.** An `--art` run plans `4N + 6M + 4` jobs for N candidates and M placed buildings; `--gameplay` adds `dispatch_handoff`.\n\nSCOPE IS THE COLUMN TO READ. Every art defect found between 2026-08-06 and 2026-08-09 was a stage computing at a coarser scope than the thing it described: dressing and fixtures planned per mission and attached to five buildings, then the kit doing the same with `exact`-fit modules cut to one building\'s slots.\n\n<!-- END GENERATED -->\n\nGraybox runs per candidate. Below the lock, **scope is the column to read**:\n`mission` runs once for the whole run, `archetype` runs once per placed\nbuilding, and confusing the two is the defect this stack keeps finding — Zoo\ndressing, Zoo fixtures and then the Zoo kit were each planned once per mission\nand attached to every building in a varied lot.\n\nTwo edges are easy to miss. `presentation_compose` is what makes `--art` mean\n"themed level" rather than "grey level with a lighting pass" — it fits themed\nZoo modules onto the greybox slot footprints while keeping greybox floors and\ncollision as the walkable base. And `lux_apply` runs over `themed_site_assemble`\'s\noutput — the composed buildings placed back onto the site — not over\n`presentation_compose` directly and not over the raw Lot site. This paragraph\nsaid `presentation_compose` until 2026-08-09: `themed_site_assemble` was added\nbetween the two and nothing updated the sentence, which is exactly why the table\nabove is now derived rather than typed.\n\n`_STAGE_REGRESSION` is declared in `planner.py` and no job is ever planned with\nit. A stage constant with nothing behind it is an unfinished thought (`CLAUDE.md`\nmakes the same point about unused parameters); `factory_map.py` reports what is\nplanned, so it does not appear above.\n\n## The repos\n\n**level_factory** — orchestrator. `packages/` holds the engine (pipeline,\n'),
        ],
    },
]

NEW_FILES = {
    'factory_map.py': '"""The DAG section of PIPELINE_MAP.md, derived from the planner instead of typed.\n\n    python factory_map.py                 # print the generated section\n    python factory_map.py --check         # compare it to PIPELINE_MAP.md, exit 1 on drift\n    python factory_map.py --write         # rewrite the section in place\n    python factory_map.py --selftest      # prove the derivation before trusting it\n\nRun from the factory root (the file must SIT there -- it locates\n`level_factory/packages` relative to itself, so cwd does not matter).\n\n## Why this exists\n\n`PIPELINE_MAP.md` is the architecture document and its DAG table is hand-typed,\nso it drifts silently. Measured 2026-08-09, before this script existed:\n\n    walktest_navqa          named nowhere in PIPELINE_MAP.md\n    themed_site_assemble    named nowhere in PIPELINE_MAP.md\n    regression              named nowhere in PIPELINE_MAP.md\n    lux_apply               documented as depending on presentation_compose;\n                            planner.py line 415 says themed_site_assemble\n    patina_apply            documented as emitting shell.patina.*; the planner\n                            has used `stem = aid or "shell"` since the kit\n                            fan-out, so it is <archetype>.patina.*\n    "everything below the gate runs once, on the selected candidate only"\n                            false for six stages since the fan-out landed\n\nNone of that is visible to a reader, which is the whole problem. `build_freshness.py`\nexists because a shell older than the code that produced it reported with full\nconfidence; a doc older than the planner does the same thing, and nothing checked.\n\n## How it derives, rather than restates\n\nIt IMPORTS `plan_mission` and plans a real mission against a synthetic library,\nthen reads the graph back. Nothing here knows the stage list, the edges or the\nscopes -- they are measurements of the object the pipeline actually builds. A\nstage added to `planner.py` appears here on the next run without this file\nchanging, which is the point (`library_themed_fit.py` makes the same argument\nabout the fitness rule at length).\n\nSCOPE IS DERIVED, NOT DECLARED:\n\n    archetype  the stage\'s jobs carry `archetype_id` -- it bakes against ONE\n               building. Getting this wrong is the defect this repo keeps\n               finding: kit, dressing and fixtures were each planned once per\n               mission and attached to five buildings.\n    candidate  one job per candidate, and no archetype -- it runs before the\n               lock, on every seed.\n    mission    exactly one job for the whole run.\n\nThe synthetic brief uses 3 candidates and 2 buildings ON PURPOSE, so the two\ncounts cannot be confused with each other. Two of each would make a\ncandidate-scoped stage and an archetype-scoped stage indistinguishable by count\nalone, and the `archetype_id` test would be carrying the whole answer untested.\n"""\nfrom __future__ import annotations\n\nimport json\nimport shutil\nimport sys\nimport tempfile\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parent\nsys.path.insert(0, str(ROOT / "level_factory"))\n\nDOC = ROOT / "PIPELINE_MAP.md"\nBEGIN = "<!-- BEGIN GENERATED: factory_map.py -- do not edit by hand -->"\nEND = "<!-- END GENERATED -->"\n\n#: Deliberately not 2 and 2 -- see the module docstring.\nCANDIDATES = 3\nBUILDINGS = 2\nFAMILIES = ("alpha", "bravo", "charlie")\n\n\ndef _library(root: Path) -> Path:\n    """A minimum themeable Deli Counter build dir: what `index` and\n    `themed_fitness` actually read, and nothing else.\n\n    The manifests carry CONTENT. Written as the literal `{}` they are a\n    faithful stand-in for a library of holed, never-judged buildings, and\n    `require_themed_shells` correctly refuses the lot -- which is how thirteen\n    fan-out tests died on 2026-08-08 telling the exact truth about their\n    fixture."""\n    root.mkdir(parents=True, exist_ok=True)\n    for fam in FAMILIES:\n        aid = f"{fam}_a01"\n        (root / f"{aid}.glb").write_text("{}", encoding="utf-8")\n        (root / f"{aid}.gameplay.json").write_text("{}", encoding="utf-8")\n        (root / f"{aid}.slots.json").write_text(\n            json.dumps({"coverage": {"wall": 96, "doorway": 4}}), encoding="utf-8")\n        (root / f"{aid}.lights.json").write_text("{}", encoding="utf-8")\n        (root / f"{aid}.navgate.json").write_text(json.dumps(\n            {"markers": {"interior_checked": 1, "interior_reachable": 1},\n             "navigable": True,\n             "navigable_reason": "synthetic: factory_map fixture"}),\n            encoding="utf-8")\n        (root / f"{aid}.validation.json").write_text(\n            json.dumps({"facade": False}), encoding="utf-8")\n    return root\n\n\ndef plan(library: Path, gameplay: bool = True):\n    """The real graph, from the real planner."""\n    from packages.core.ids import candidate_id\n    from packages.core.models import MissionBrief\n    from packages.pipeline import planner as P\n\n    brief = MissionBrief(\n        mission_id="factory_map", display_name="factory_map",\n        archetype="depot", theme="rockay",\n        candidate_count=CANDIDATES, building_count=BUILDINGS,\n        lot_library=str(library))\n    seeds = P.derive_seeds(5000, CANDIDATES)\n    layers = {P.LAYER_ART} | ({P.LAYER_GAMEPLAY} if gameplay else set())\n    return P.plan_mission(\n        brief, seed_base=5000, layers=layers,\n        selected_candidate=candidate_id(brief.mission_id, seeds[0]))\n\n\ndef stages(pl) -> list[dict]:\n    """One row per stage, in the graph\'s own topological order."""\n    order, by_stage = [], {}\n    for job in pl.graph.topological_order():\n        if job.stage_id not in by_stage:\n            by_stage[job.stage_id] = []\n            order.append(job.stage_id)\n        by_stage[job.stage_id].append(job)\n    stage_of = {j.job_id: j.stage_id for j in pl.graph.jobs()}\n\n    rows = []\n    for sid in order:\n        jobs = by_stage[sid]\n        j = jobs[0]\n        if any(x.archetype_id for x in jobs):\n            scope = "archetype"\n        elif len({x.candidate_id for x in jobs}) == CANDIDATES:\n            scope = "candidate"\n        else:\n            scope = "mission"\n        deps, seen = [], set()\n        for x in jobs:\n            for d in x.depends_on:\n                s = stage_of.get(d, d)\n                if s not in seen:\n                    seen.add(s)\n                    deps.append(s)\n        outs = [o.replace(str(j.archetype_id), "<archetype>")\n                if j.archetype_id else o for o in (j.expected_outputs or [])]\n        rows.append(dict(stage=sid, adapter=j.adapter_id,\n                         resource=j.resource_class, scope=scope,\n                         deps=deps, outputs=outs, count=len(jobs)))\n\n    # DEPTH, not the graph\'s topological order. Topological order is not unique\n    # and the one the graph happens to yield interleaves the scopes -- it put\n    # `zoo_fixtures_build` above `walktest_navqa`, so the "candidate locked"\n    # marker landed above two stages that run before the lock. Depth is the\n    # longest path from a root, which is what a reader means by "a layer".\n    depth, by_stage_row = {}, {r["stage"]: r for r in rows}\n\n    def _d(sid, seen=()):\n        if sid in depth:\n            return depth[sid]\n        if sid in seen:                      # cannot happen in a DAG; do not hang\n            return 0\n        r = by_stage_row.get(sid)\n        v = 0 if not r or not r["deps"] else 1 + max(\n            _d(x, seen + (sid,)) for x in r["deps"])\n        depth[sid] = v\n        return v\n\n    topo = {r["stage"]: i for i, r in enumerate(rows)}\n    rows.sort(key=lambda r: (0 if r["scope"] == "candidate" else 1,\n                             _d(r["stage"]), topo[r["stage"]]))\n    return rows\n\n\ndef render(rows: list[dict], gameplay_only=frozenset()) -> str:\n    """The markdown block. Anything a reader needs that the graph does not\n    carry -- why an edge exists, what a stage is FOR -- belongs in the prose\n    around this block, not in it."""\n    out = [BEGIN, "",\n           "| Stage | Adapter | Resource | Scope | Depends on | Expected outputs |",\n           "|---|---|---|---|---|---|"]\n    gate_done = False\n    for r in rows:\n        if not gate_done and r["scope"] != "candidate":\n            out.append("| *candidate selected + functional shell locked* | | | "\n                       "| | |")\n            gate_done = True\n        deps = ", ".join(f"`{d}`" for d in r["deps"]) or "—"\n        outs = ", ".join(f"`{o}`" for o in r["outputs"]) \\\n            or "*named at exec; the adapter validates*"\n        out.append(f"| `{r[\'stage\']}` | {r[\'adapter\']} | {r[\'resource\']} | "\n                   f"{r[\'scope\']} | {deps} | {outs} |")\n    n_c = sum(1 for r in rows if r["scope"] == "candidate")\n    n_a = sum(1 for r in rows if r["scope"] == "archetype")\n    n_m = sum(1 for r in rows if r["scope"] == "mission"\n              and r["stage"] not in gameplay_only)\n    gm = ", ".join(f"`{s}`" for s in sorted(gameplay_only))\n    out += ["",\n            f"**{len(rows)} stages: {n_c} per candidate, {n_a} per archetype, "\n            f"{n_m + len(gameplay_only)} once per mission.** An `--art` run "\n            f"plans `{n_c}N + {n_a}M + {n_m}` jobs for N candidates and M "\n            f"placed buildings"\n            + (f"; `--gameplay` adds {gm}." if gm else "."),\n            "",\n            "SCOPE IS THE COLUMN TO READ. Every art defect found between "\n            "2026-08-06 and 2026-08-09 was a stage computing at a coarser "\n            "scope than the thing it described: dressing and fixtures planned "\n            "per mission and attached to five buildings, then the kit doing "\n            "the same with `exact`-fit modules cut to one building\'s slots.",\n            "", END]\n    return "\\n".join(out)\n\n\ndef generated() -> str:\n    tmp = Path(tempfile.mkdtemp(prefix="factory_map_"))\n    try:\n        lib = _library(tmp / "build")\n        full = stages(plan(lib, gameplay=True))\n        art = {r["stage"] for r in stages(plan(lib, gameplay=False))}\n        return render(full, frozenset(r["stage"] for r in full\n                                      if r["stage"] not in art))\n    finally:\n        shutil.rmtree(tmp, ignore_errors=True)\n\n\n# ------------------------------------------------------------------ selftest\ndef _selftest() -> int:\n    """Prove the derivation before printing a table built on it.\n\n    Two things can be silently wrong here and both have precedent in this repo:\n    a scope rule that cannot distinguish its cases, and a fixture that agrees\n    with a broken reader. So the scopes are asserted against what the planner\'s\n    own docstrings say they are, and the fan-out is asserted to actually fan --\n    a stage claiming `archetype` scope with one job is the 2026-08-09 bug\n    wearing the right label.\n    """\n    bad = 0\n    tmp = Path(tempfile.mkdtemp(prefix="factory_map_st_"))\n    try:\n        rows = {r["stage"]: r for r in stages(plan(_library(tmp / "build")))}\n    finally:\n        shutil.rmtree(tmp, ignore_errors=True)\n\n    want = {\n        "deli_generate": ("candidate", CANDIDATES),\n        "lot_assemble": ("candidate", CANDIDATES),\n        "walktest_navqa": ("candidate", CANDIDATES),\n        "laser_tag_evaluate": ("candidate", CANDIDATES),\n        "pixelcoat_build": ("mission", 1),\n        "zoo_kit_build": ("archetype", BUILDINGS),\n        "patina_apply": ("archetype", BUILDINGS),\n        "patina_dressing": ("archetype", BUILDINGS),\n        "zoo_dressing_build": ("archetype", BUILDINGS),\n        "zoo_fixtures_build": ("archetype", BUILDINGS),\n        "lux_fixture_gate": ("archetype", BUILDINGS),\n        "presentation_compose": ("mission", 1),\n        "themed_site_assemble": ("mission", 1),\n        "lux_apply": ("mission", 1),\n        "dispatch_handoff": ("mission", 1),\n    }\n    for sid, (scope, count) in sorted(want.items()):\n        r = rows.get(sid)\n        if r is None:\n            print(f"[selftest] {sid:22} MISSING from the planned graph")\n            bad += 1\n            continue\n        ok = r["scope"] == scope and r["count"] == count\n        bad += not ok\n        print(f"[selftest] {sid:22} {r[\'scope\']:9} x{r[\'count\']}  "\n              f"{\'ok\' if ok else f\'FAIL want {scope} x{count}\'}")\n\n    extra = sorted(set(rows) - set(want))\n    if extra:\n        # Not a failure: a new stage is exactly what this script exists to\n        # surface. It IS a prompt to give it a line of prose in PIPELINE_MAP.\n        print(f"[selftest] NEW STAGE(S) not yet in this selftest: "\n              f"{\', \'.join(extra)} -- add them here and describe them in the "\n              f"prose around the generated block")\n\n    # The edge PIPELINE_MAP got wrong, pinned so it cannot go stale twice.\n    lux = rows.get("lux_apply", {})\n    ok = lux.get("deps") == ["themed_site_assemble"]\n    bad += not ok\n    print(f"[selftest] lux_apply deps    {lux.get(\'deps\')}  "\n          f"{\'ok\' if ok else \'FAIL want [themed_site_assemble]\'}")\n\n    if bad:\n        print("[selftest] the derivation is wrong; the table below it would be "\n              "a document, not a measurement")\n        return 1\n    print("[selftest] scopes, fan-out counts and the lux edge all derived "\n          "correctly")\n    return 0\n\n\ndef _doc_block(text: str):\n    if BEGIN not in text or END not in text:\n        return None\n    return text[text.index(BEGIN): text.index(END) + len(END)]\n\n\ndef _audit(text: str, rows: list[dict]) -> int:\n    """What the hand-written doc says that the planner does not. Only used\n    when the generated markers are absent -- once they are in, the diff IS the\n    audit."""\n    missing = [r["stage"] for r in rows if f"`{r[\'stage\']}`" not in text\n               and r["stage"] not in text]\n    print(f"  {len(rows)} stages planned; "\n          f"{len(missing)} named nowhere in {DOC.name}")\n    for s in missing:\n        print(f"    ABSENT  {s}")\n    return 1 if missing else 0\n\n\ndef main(argv: list[str]) -> int:\n    if "--selftest" in argv:\n        return _selftest()\n    if _selftest():\n        return 1\n    print()\n    block = generated()\n\n    if "--check" not in argv and "--write" not in argv:\n        print(block)\n        return 0\n\n    if not DOC.is_file():\n        print(f"not found: {DOC}")\n        return 2\n    text = DOC.read_text(encoding="utf-8")\n    current = _doc_block(text)\n\n    if "--write" in argv:\n        if current is None:\n            print(f"{DOC.name} has no generated block yet. Paste the section "\n                  f"above in place of the hand-written DAG table, markers "\n                  f"included, then --write and --check will maintain it.")\n            return 2\n        DOC.write_text(text.replace(current, block), encoding="utf-8")\n        print(f"  rewrote the generated block in {DOC.name}")\n        return 0\n\n    if current is None:\n        print(f"  {DOC.name} has no generated block; auditing by name instead")\n        tmp = Path(tempfile.mkdtemp(prefix="factory_map_a_"))\n        try:\n            rows = stages(plan(_library(tmp / "build")))\n        finally:\n            shutil.rmtree(tmp, ignore_errors=True)\n        return _audit(text, rows)\n\n    if current == block:\n        print(f"  {DOC.name} matches the planner")\n        return 0\n    print(f"  {DOC.name} HAS DRIFTED from the planner. Diff:")\n    import difflib\n    for line in difflib.unified_diff(\n            current.splitlines(), block.splitlines(),\n            fromfile=f"{DOC.name} (committed)", tofile="planner.py (derived)",\n            lineterm="", n=1):\n        print("    " + line)\n    print("  run --write to regenerate")\n    return 1\n\n\nif __name__ == "__main__":\n    raise SystemExit(main(sys.argv[1:]))\n',
}


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _write(p: Path, text: str) -> None:
    p.write_text(text, encoding="utf-8", newline="")


def check(verbose: bool = True):
    """(ok, todo) -- every target read and hashed, nothing written."""
    ok, todo = True, []
    for t in TARGETS:
        p = ROOT / t["rel"]
        if not p.is_file():
            print(f"  MISSING   {t['rel']}")
            ok = False
            continue
        cur = _read(p)
        got = _sha(cur)
        if got == t["post_sha"]:
            print(f"  already   {t['rel']}")
            continue
        if got != t["pre_sha"]:
            print(f"  DRIFTED   {t['rel']}")
            print(f"            expected {t['pre_bytes']} bytes "
                  f"sha {t['pre_sha'][:16]}")
            print(f"            found    {len(cur.encode('utf-8'))} bytes "
                  f"sha {got[:16]}")
            ok = False
            continue
        todo.append((p, t, cur))
        if verbose:
            print(f"  ready     {t['rel']}  ({len(t['hunks'])} hunk(s), "
                  f"{t['pre_bytes']} -> {t['post_bytes']} bytes)")
    for rel in NEW_FILES:
        p = ROOT / rel
        state = "exists (will not overwrite)" if p.is_file() else "will create"
        print(f"  new file  {rel}  -- {state}")
    return ok, todo


def apply() -> int:
    print("checking every target before writing anything")
    ok, todo = check()
    if not ok:
        print("\nREFUSED. At least one target is not the file this patch was "
              "written against; nothing has been written.")
        return 1
    for p, t, cur in todo:
        side = p.with_name(p.name + SIDECAR)
        if not side.exists():
            _write(side, cur)
        out = cur
        for old, new in t["hunks"]:
            if out.count(old) != 1:
                print(f"REFUSED mid-file on {t['rel']} -- anchor not unique. "
                      f"Restore from {side.name} and re-read.")
                return 1
            out = out.replace(old, new, 1)
        if _sha(out) != t["post_sha"]:
            print(f"REFUSED on {t['rel']} -- result does not match the "
                  f"expected post-image. Nothing further written.")
            return 1
        _write(p, out)
        print(f"  patched   {t['rel']}  ({side.name} written)")
    for rel, body in NEW_FILES.items():
        p = ROOT / rel
        if p.is_file():
            print(f"  kept      {rel} (already present, not overwritten)")
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        _write(p, body)
        print(f"  created   {rel}")
    print("\nNow run, from the factory root:  python factory_map.py --check")
    print("Expected: `python factory_map.py --check` prints 'PIPELINE_MAP.md matches the planner'.")
    return 0


def revert() -> int:
    n = 0
    for t in TARGETS:
        p = ROOT / t["rel"]
        side = p.with_name(p.name + SIDECAR)
        if not side.is_file():
            continue
        body = _read(side)
        if _sha(body) != t["pre_sha"]:
            print(f"  REFUSED   {t['rel']} -- {side.name} is not the "
                  f"pre-image this patch recorded")
            continue
        _write(p, body)
        side.unlink()
        n += 1
        print(f"  reverted  {t['rel']}")
    for rel in NEW_FILES:
        p = ROOT / rel
        if p.is_file() and _sha(_read(p)) == _sha(NEW_FILES[rel]):
            p.unlink()
            print(f"  removed   {rel}")
    print(f"\n{n} file(s) restored.")
    return 0


def main(argv):
    if "--check" in argv:
        ok, _ = check()
        print("\nOK to apply." if ok else "\nNOT ok to apply.")
        return 0 if ok else 1
    if "--revert" in argv:
        return revert()
    return apply()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
