"""Plan one art job per building, and hand each building its own.

Run from the factory root:

    python patch_lf_fanout.py --check
    python patch_lf_fanout.py

Steps 3b, 3c and 3d of `level_factory/docs/PER_BUILDING_ART.md`. They land
together on purpose. 3b alone is worse than neither: the planner would emit five
dressing jobs, five Blender builds would run, and the spec builder's `next(...)`
would hand the first one's output to all five buildings -- today's defect
exactly, with five times the build cost and a green suite over it.

WHAT WAS MEASURED. 2026-08-06, off the loaded scene of the first walkable
multi-building site: five shells with footprints from 26.1 x 20.3 to 46.3 x 26.3
and roofs from 3.4 m to 12.7 m, all wearing a dressing bounding box of exactly
30.4 x 8.4 x 22.4 and a fixtures box of exactly 30.5 x 3.7 x 17.9. Three of the
five carried their props 1.8 m, 3.8 m and 4.9 m above their own roof; in one the
dressing footprint was LARGER than the shell it sat in.

THE MECHANISM, in three parts, all of which this patch touches:

1. `planner.py`'s LAYER_ART block added `patina_apply`, `patina_dressing`,
   `zoo_dressing_build` and `zoo_fixtures_build` as ONE job each, keyed to the
   selected candidate. Singular by construction.
2. `commands/__init__.py` resolved each of those by substring against
   `depends_on` with `next(...)`, which returns the first and drops the rest
   without a word, and `_layer_glb` took `hits[-1]` -- whichever filename sorted
   last -- and gave it to everybody.
3. `adapters/presentation/__init__.py`'s `compose()` took six keyword arguments
   and the per-archetype loop overrode all six, but dressing and fixtures were
   not among them: they were read from the closed-over `job_spec`. The comment
   directly above that loop promises each building is "dressed AS ITSELF" and
   names the failure it was performing.

WHAT FANS OUT AND WHAT DOES NOT. Only BAKED PLACEMENTS. `zoo_kit_build` and
`pixelcoat_build` stay one job per mission: a kit is a LIBRARY of modules
resolved per slot at compose time, and the five packages demonstrably drew
different module sets from the one kit (`final_stand` took none,
`lf_lot_demo_001_5017` took 25). A library shared across buildings is fine; a
placement shared across buildings is the defect. Fanning the kit out would cost
a Blender build per building and fix nothing.

`lux_fixture_gate` DOES fan out, which the doc's stage list does not name.
Not a preference: it is a GATE over one fixtures bake, and with fixtures fanned
the only two alternatives were to depend on all five and gate `depends_on[0]`,
or to depend on one and gate one while reporting the whole mission passed. Both
are "a check that cannot fail is indistinguishable from one that passed", in a
gate, which is the failure this repo has now written down three times. It also
writes `fixture_gate.report.json`, and one job directory holds one report. Cost:
one headless Godot run per building instead of one per mission.

BYTE-IDENTICAL WHERE NOTHING CHANGED. `lot_for` returns an empty lot for every
mission that does not set `lot_library`, and an empty lot plans as ONE unnamed
building: `job_id` gets no archetype segment, Patina's stem stays `shell`, and
`compose`'s dependency list keeps its old order and length. `Plan.as_dict`
emits `archetype_id` only when a job has one, so an existing plan's json does
not grow a null on every line. A level that has already been evaluated must not
quietly become a different one.

EXPECTED OUTPUTS FOLLOW THE INPUT. Patina derives its output names from the
input stem (`adapters/patina/__init__.py:42-48`), so a job pointed at
`final_stand.glb` writes `final_stand.patina.*`. `planner.py` hardcoded
`shell.patina.glb` and `commands/__init__.py` hardcoded
`shell.patina.dressing.json` as the consumer path; both were only ever right
because every art job was pointed at the mission's own shell.

THE ART SCREEN HAD TO FOLLOW. `service/facade.py`'s `_ART_SECTIONS` maps each
art stage to ONE job directory, `f"{mission_id}.{stage}"`, and a fanned stage
does not have one -- its directories are `<mission>.<stage>.<archetype>`. Left
alone the screen reported "not_started" for a stage that had completed five
times. It now aggregates: DONE when every building's job has published. Rows per
building were the alternative and were rejected, because the lot size would then
decide how many sections the screen has.

REFUSAL, NOT FALLBACK, in the three places where the two sides could disagree:
a stage with several dependency jobs and no archetype to choose between them,
a fanned job whose archetype is not in its candidate's lot, and a job that
published more than one layer of a kind. Each of those is the planner and the
spec builder disagreeing about which buildings this mission places, and quietly
substituting one building's props for another's is the thing being removed.
"""
from __future__ import annotations

import sys
from pathlib import Path

PLANNER = Path("level_factory/packages/pipeline/planner.py")
CLI = Path("level_factory/apps/cli/commands/__init__.py")
PRES = Path("level_factory/adapters/presentation/__init__.py")
FACADE = Path("level_factory/packages/service/facade.py")

TARGETS = (PLANNER, CLI, PRES, FACADE)

EDITS: list[tuple[Path, str, str, str]] = [

    # ---- 3b: the planner fans out ------------------------------------

    (PLANNER, "planner: report the archetype axis in the plan json", '''\
                    "stage": j.stage_id,
                    "candidate_id": j.candidate_id,
                    "depends_on": list(j.depends_on),
''', '''\
                    "stage": j.stage_id,
                    "candidate_id": j.candidate_id,
                    # Only when the job HAS one. A mission-wide job carries no
                    # archetype, and adding a null to every line of every plan
                    # that has ever been written buys nothing; an absent key
                    # reads as "this stage runs once for the mission".
                    **({"archetype_id": j.archetype_id} if j.archetype_id else {}),
                    "depends_on": list(j.depends_on),
'''),

    (PLANNER, "planner: one placement bake per building", '''\
        # Patina base cohesion pass.
        patina_base_jid = job_id(brief.mission_id, _STAGE_PATINA_BASE)
        plan.graph.add(Job(
            job_id=patina_base_jid, mission_id=brief.mission_id,
            stage_id=_STAGE_PATINA_BASE, adapter_id="patina",
            candidate_id=selected_candidate, resource_class="python_cpu",
            depends_on=[lot_jid],
            expected_outputs=["shell.patina.glb", "shell.patina.json",
                              "shell.patina.gameplay.json"],
        ))
        # Patina dressing manifest.
        patina_dress_jid = job_id(brief.mission_id, _STAGE_PATINA_DRESS)
        plan.graph.add(Job(
            job_id=patina_dress_jid, mission_id=brief.mission_id,
            stage_id=_STAGE_PATINA_DRESS, adapter_id="patina",
            candidate_id=selected_candidate, resource_class="python_cpu",
            depends_on=[patina_base_jid],
            expected_outputs=["shell.patina.glb", "shell.patina.json",
                              "shell.patina.gameplay.json",
                              "shell.patina.dressing.json"],
        ))
        # Zoo dressing build from the Patina manifest (collision-free).
        zoo_dress_jid = job_id(brief.mission_id, _STAGE_ZOO_DRESS)
        plan.graph.add(Job(
            job_id=zoo_dress_jid, mission_id=brief.mission_id,
            stage_id=_STAGE_ZOO_DRESS, adapter_id="zoo",
            candidate_id=selected_candidate, resource_class="blender",
            depends_on=[patina_dress_jid, zoo_kit_jid],
            expected_outputs=[],  # zoo names by building_id at exec; adapter checks
        ))
''', '''\
        # WHICH BUILDINGS THIS MISSION PLACES, and therefore how many times a
        # placement stage runs. `lot_for` is the one selection rule -- the
        # compose spec and the site spec call the same function -- so the jobs
        # planned here are for the buildings that actually get placed by
        # construction, not by two derivations that happen to agree.
        #
        # AN EMPTY LOT IS THE SINGLE-SHELL PATH: one unnamed building, job ids
        # with no archetype segment, `shell.patina.*` outputs, and a compose
        # dependency list of the same length and order as before. Every mission
        # that does not set `lot_library` plans byte-for-byte what it planned
        # before this existed.
        from packages.pipeline import building_library
        art_lot, _art_excluded = building_library.lot_for(
            getattr(brief, "lot_library", None),
            getattr(brief, "building_count", 1),
            selected_candidate)
        # RAISES rather than filtering. A building whose light manifest is
        # missing dropping quietly out here would turn a five building brief
        # into a four building site with every stage reporting success -- the
        # failure already recorded in docs/WALKABLE_SITE.md.
        if art_lot:
            building_library.require_art_inputs(art_lot)
        art_buildings = art_lot or [None]

        zoo_dress_jids: list[str] = []
        for _entry in art_buildings:
            aid = _entry["id"] if _entry else None
            # Patina names its outputs from the INPUT STEM
            # (adapters/patina/__init__.py:42-48), so a job pointed at
            # `final_stand.glb` writes `final_stand.patina.*`. The contract has
            # to follow the input. `shell.patina.glb` was hardcoded here and was
            # only ever right because every art job was pointed at the mission's
            # own shell; an archetype id IS its file stem, by construction in
            # `building_library.index`.
            stem = aid or "shell"
            # Patina base cohesion pass.
            patina_base_jid = job_id(brief.mission_id, _STAGE_PATINA_BASE,
                                     archetype=aid)
            plan.graph.add(Job(
                job_id=patina_base_jid, mission_id=brief.mission_id,
                stage_id=_STAGE_PATINA_BASE, adapter_id="patina",
                candidate_id=selected_candidate, archetype_id=aid,
                resource_class="python_cpu",
                depends_on=[lot_jid],
                expected_outputs=[f"{stem}.patina.glb", f"{stem}.patina.json",
                                  f"{stem}.patina.gameplay.json"],
            ))
            # Patina dressing manifest.
            patina_dress_jid = job_id(brief.mission_id, _STAGE_PATINA_DRESS,
                                      archetype=aid)
            plan.graph.add(Job(
                job_id=patina_dress_jid, mission_id=brief.mission_id,
                stage_id=_STAGE_PATINA_DRESS, adapter_id="patina",
                candidate_id=selected_candidate, archetype_id=aid,
                resource_class="python_cpu",
                depends_on=[patina_base_jid],
                expected_outputs=[f"{stem}.patina.glb", f"{stem}.patina.json",
                                  f"{stem}.patina.gameplay.json",
                                  f"{stem}.patina.dressing.json"],
            ))
            # Zoo dressing build from the Patina manifest (collision-free).
            # Depends on ITS OWN patina_dressing and the SHARED kit: the kit is
            # a module library resolved per slot, the dressing is a placement
            # baked against this building's walls and roof.
            zoo_dress_jid = job_id(brief.mission_id, _STAGE_ZOO_DRESS,
                                   archetype=aid)
            plan.graph.add(Job(
                job_id=zoo_dress_jid, mission_id=brief.mission_id,
                stage_id=_STAGE_ZOO_DRESS, adapter_id="zoo",
                candidate_id=selected_candidate, archetype_id=aid,
                resource_class="blender",
                depends_on=[patina_dress_jid, zoo_kit_jid],
                expected_outputs=[],  # zoo names by building_id at exec; adapter checks
            ))
            zoo_dress_jids.append(zoo_dress_jid)
        # Named before the fixtures jobs are added, because compose depends on
        # them and is added first -- as it was when there was one.
        zoo_fixtures_jids = [
            job_id(brief.mission_id, _STAGE_ZOO_FIXTURES,
                   archetype=(_e["id"] if _e else None))
            for _e in art_buildings]
'''),

    (PLANNER, "planner: compose waits on every building's layers", '''\
            depends_on=[deli_sel_jid, zoo_kit_jid, zoo_dress_jid,
                        job_id(brief.mission_id, _STAGE_ZOO_FIXTURES)],
            expected_outputs=["presentation/site.tscn"],
''', '''\
            depends_on=[deli_sel_jid, zoo_kit_jid,
                        *zoo_dress_jids, *zoo_fixtures_jids],
            expected_outputs=["presentation/site.tscn"],
'''),

    (PLANNER, "planner: one fixture bake and one gate per building", '''\
        deli_sel_jid = job_id(brief.mission_id, _STAGE_DELI,
                              candidate=selected_candidate)
        zoo_fixtures_jid = job_id(brief.mission_id, _STAGE_ZOO_FIXTURES)
        plan.graph.add(Job(
            job_id=zoo_fixtures_jid, mission_id=brief.mission_id,
            stage_id=_STAGE_ZOO_FIXTURES, adapter_id="zoo",
            candidate_id=selected_candidate, resource_class="blender",
            depends_on=[deli_sel_jid],
            expected_outputs=[],  # zoo names by scope_id at exec; adapter checks
        ))
        fixture_gate_jid = job_id(brief.mission_id, _STAGE_LUX_FIXTURE_GATE)
        plan.graph.add(Job(
            job_id=fixture_gate_jid, mission_id=brief.mission_id,
            stage_id=_STAGE_LUX_FIXTURE_GATE, adapter_id="lux",
            candidate_id=selected_candidate, resource_class="godot_headless",
            depends_on=[zoo_fixtures_jid],
            expected_outputs=["fixture_gate.report.json"],
        ))
''', '''\
        deli_sel_jid = job_id(brief.mission_id, _STAGE_DELI,
                              candidate=selected_candidate)
        for _entry, zoo_fixtures_jid in zip(art_buildings, zoo_fixtures_jids):
            aid = _entry["id"] if _entry else None
            # The lights manifest an archetype bake reads is a LIBRARY file that
            # exists before the run, so this edge is the locked-candidate gate
            # rather than a data dependency. It is kept because the single-shell
            # path genuinely reads that job's `shell.lights.json`, and because a
            # placement bake for a mission that has not locked a shell is a bake
            # for a level nobody has chosen.
            plan.graph.add(Job(
                job_id=zoo_fixtures_jid, mission_id=brief.mission_id,
                stage_id=_STAGE_ZOO_FIXTURES, adapter_id="zoo",
                candidate_id=selected_candidate, archetype_id=aid,
                resource_class="blender",
                depends_on=[deli_sel_jid],
                expected_outputs=[],  # zoo names by scope_id at exec; adapter checks
            ))
            # The gate follows the bake. One gate over five bakes would either
            # take `depends_on[0]` and report the mission passed on the strength
            # of one building, or hold five reports in one job directory. A gate
            # that examines one of five and says nothing about the other four is
            # the failure mode this whole document is about.
            fixture_gate_jid = job_id(brief.mission_id, _STAGE_LUX_FIXTURE_GATE,
                                      archetype=aid)
            plan.graph.add(Job(
                job_id=fixture_gate_jid, mission_id=brief.mission_id,
                stage_id=_STAGE_LUX_FIXTURE_GATE, adapter_id="lux",
                candidate_id=selected_candidate, archetype_id=aid,
                resource_class="godot_headless",
                depends_on=[zoo_fixtures_jid],
                expected_outputs=["fixture_gate.report.json"],
            ))
'''),

    # ---- 3c: the spec builder stops taking the first match ------------

    (CLI, "cli: a resolver that refuses instead of choosing", '''\
def _lot_slots(ws: Workspace, jobs_dir: Path, job) -> Path:
''', '''\
def _dep(job, stage: str, archetype: str | None = None) -> str | None:
    """The ONE dependency of ``job`` in ``stage``, or None.

    `next((d for d in job.depends_on if "<stage>" in d), None)` returns the
    FIRST match and drops the rest without a word. That was correct while every
    art stage was planned once per mission. The stages that bake a PLACEMENT now
    run once per building, and a resolver that takes whichever id happens to
    come first hands one building's props to all of them -- which is the defect,
    reintroduced one layer down.

    So: narrow by archetype when the caller has one, and REFUSE when more than
    one survives. A caller with several candidates and no way to choose between
    them does not have a default; it has a bug.
    """
    hits = [d for d in job.depends_on if f".{stage}" in d]
    if archetype:
        hits = [d for d in hits if d.endswith(f".{archetype}")]
    if len(hits) > 1:
        raise RuntimeError(
            f"{job.job_id} has {len(hits)} '{stage}' dependencies "
            f"({', '.join(hits)})"
            + (f" for archetype {archetype!r}" if archetype else
               " and no archetype to choose between them"))
    return hits[0] if hits else None


def _lot_slots(ws: Workspace, jobs_dir: Path, job) -> Path:
'''),

    (CLI, "cli: derive the lot once, and bind a fanned job to its building", '''\
    specs: dict[str, dict] = {}
    jobs_dir = ws.jobs_dir
    for job in plan.graph.topological_order():
''', '''\
    specs: dict[str, dict] = {}
    jobs_dir = ws.jobs_dir

    # ONE derivation per candidate. `_lot_for_compose` lists a directory and
    # prints what it excluded; with the placement stages fanned out there are
    # now twenty-odd jobs that need the same answer, and doing it per job would
    # list the library twenty times and say the same sentence twenty times.
    _lot_memo: dict[str, list] = {}

    def _lot_rows(candidate_id) -> list:
        cid = str(candidate_id)
        if cid not in _lot_memo:
            _lot_memo[cid] = _lot_for_compose(model, cid)
        return _lot_memo[cid]

    def _art_entry(job):
        """The library row for the building THIS job bakes, None if mission-wide.

        `job.archetype_id` was set by the planner from the same `lot_for` rule
        this reads, so a fanned job whose archetype is not in the candidate's lot
        means the planner and the spec builder disagree about which buildings the
        mission places. Refused rather than fallen back from: quietly using the
        mission's own shell instead is exactly the substitution being removed.
        """
        aid = getattr(job, "archetype_id", None)
        if not aid:
            return None
        row = next((a for a in _lot_rows(job.candidate_id)
                    if a.get("id") == aid), None)
        if row is None:
            raise RuntimeError(
                f"{job.job_id} is planned for archetype {aid!r}, which is not "
                f"in this candidate's lot -- the planner and the spec builder "
                f"disagree about which buildings this mission places")
        return row

    for job in plan.graph.topological_order():
'''),

    (CLI, "cli: themed site resolves its one compose", '''\
                compose_job = next((d for d in job.depends_on
                                    if "presentation_compose" in d), None)
''', '''\
                compose_job = _dep(job, "presentation_compose")
'''),

    (CLI, "cli: themed site reads the memoised lot", '''\
                lot = _lot_for_compose(model, job.candidate_id)
''', '''\
                lot = _lot_rows(job.candidate_id)
'''),

    (CLI, "cli: a fixture bake reads ITS building's lights manifest", '''\
            if job.stage_id == "zoo_fixtures_build":
                deli_job = job.depends_on[0]
                specs[job.job_id] = {
                    "mode": "fixtures",
                    "seed": int(str(job.candidate_id).rsplit("_", 1)[-1]),
                    "theme": model.theme or batch.get("theme_family", ""),
                    "lights_path": str(_latest_output(jobs_dir / deli_job,
                                                      "shell.lights.json")),
''', '''\
            if job.stage_id == "zoo_fixtures_build":
                # An archetype's lights manifest comes from the LIBRARY, where
                # it already exists; the mission's own shell reads the one its
                # Deli Counter job wrote. `building_library.index` carries the
                # path, and `require_art_inputs` has already refused the mission
                # if any picked building lacks one -- so this is a lookup, not a
                # probe with a fallback.
                entry = _art_entry(job)
                deli_job = _dep(job, "deli_generate") or job.depends_on[0]
                lights_path = (str(entry["lights"]) if entry
                               else str(_latest_output(jobs_dir / deli_job,
                                                       "shell.lights.json")))
                specs[job.job_id] = {
                    "mode": "fixtures",
                    "seed": int(str(job.candidate_id).rsplit("_", 1)[-1]),
                    "theme": model.theme or batch.get("theme_family", ""),
                    "lights_path": lights_path,
'''),

    (CLI, "cli: a dressing build reads ITS building's manifest", '''\
                dress_job = next(d for d in job.depends_on if "patina_dressing" in d)
''', '''\
                dress_job = _dep(job, "patina_dressing",
                                 getattr(job, "archetype_id", None))
'''),

    (CLI, "cli: un-hardcode the dressing manifest name", '''\
                    # Zoo --dress consumes Patina's <stem>.patina.dressing.json.
                    "manifest_path": str(_latest_output(jobs_dir / dress_job,
                                                        "shell.patina.dressing.json")),
''', '''\
                    # Zoo --dress consumes Patina's <stem>.patina.dressing.json,
                    # and Patina takes that stem from its INPUT
                    # (adapters/patina/__init__.py:42-48). A dressing job for
                    # `final_stand.glb` therefore writes
                    # `final_stand.patina.dressing.json`; `shell` is the stem
                    # only for the mission's own shell.
                    "manifest_path": str(_latest_output(
                        jobs_dir / dress_job,
                        f"{getattr(job, 'archetype_id', None) or 'shell'}"
                        f".patina.dressing.json")),
'''),

    (CLI, "cli: the kit build resolves its one pixelcoat", '''\
                pix_job = next((d for d in job.depends_on if "pixelcoat" in d), None)
''', '''\
                pix_job = _dep(job, "pixelcoat_build")
'''),

    (CLI, "cli: a patina pass treats ITS building", '''\
        elif job.adapter_id == "patina":
            deli_glb = str(_latest_output(jobs_dir / _deli_for(plan, job), "shell.glb"))
''', '''\
        elif job.adapter_id == "patina":
            # The shell this pass treats. An archetype's greybox is the library
            # file the lot picked; the mission's own shell is what its Deli
            # Counter job built. Patina names every output from this path's
            # stem, so it also decides what the planner's expected_outputs say.
            entry = _art_entry(job)
            deli_glb = (str(entry["glb"]) if entry else
                        str(_latest_output(jobs_dir / _deli_for(plan, job),
                                           "shell.glb")))
'''),

    (CLI, "cli: content layers become one per building", '''\
            kit_job = next((d for d in job.depends_on if "zoo_kit_build" in d), None)
            modules_dir = (str(_latest_output(jobs_dir / kit_job, "."))
                           if kit_job else "")

            def _layer_glb(dep_key: str, suffix: str) -> str:
                """The dressing/fixtures GLB a dependency job published --
                the CONTENT LAYERS the composed scene instances (props +
                light-fixture hardware). Resolved by suffix because the
                filename carries the building id."""
                dep = next((d for d in job.depends_on if dep_key in d), None)
                if not dep:
                    return ""
                hits = sorted((jobs_dir / dep / "out").glob(f"*{suffix}"))
                return str(hits[-1]) if hits else ""

            dressing_glb = _layer_glb("zoo_dressing_build", "_dressing.glb")
            fixtures_glb = _layer_glb("zoo_fixtures_build", "_fixtures.glb")
''', '''\
            kit_job = _dep(job, "zoo_kit_build")
            modules_dir = (str(_latest_output(jobs_dir / kit_job, "."))
                           if kit_job else "")

            def _layer_paths(stage: str, suffix: str) -> dict:
                """``{archetype_id or "": glb}`` -- one CONTENT LAYER per building.

                The dressing and fixtures GLBs the composed scene instances
                (props + light-fixture hardware). A bake is a PLACEMENT against
                one specific shell's walls and roof, so the building it was
                built for is the key. This used to take `hits[-1]` -- whichever
                filename sorted last -- from whichever dependency matched first,
                and hand it to every building: measured 2026-08-06, one
                30.4 x 8.4 x 22.4 dressing box inside five shells whose
                footprints ran from 26.1 x 20.3 to 46.3 x 26.3.

                Keyed off the JOB's archetype rather than parsed back out of the
                filename, because reconstructing ids from strings is already the
                fragile part of this codebase.

                Several layers of one kind in one job dir is refused rather than
                resolved: one bake is one placement against one shell, so there
                is no basis for preferring one of them.
                """
                deps = set(job.depends_on)
                found: dict[str, str] = {}
                for dep in plan.graph.jobs():
                    if dep.job_id not in deps or dep.stage_id != stage:
                        continue
                    hits = sorted((jobs_dir / dep.job_id / "out")
                                  .glob(f"*{suffix}"))
                    if len(hits) > 1:
                        raise RuntimeError(
                            f"{dep.job_id} published {len(hits)} '{suffix}' "
                            f"layers ({', '.join(h.name for h in hits)}); one "
                            f"bake is one placement against one shell and there "
                            f"is no basis for choosing between them")
                    found[getattr(dep, "archetype_id", None) or ""] = (
                        str(hits[0]) if hits else "")
                return found

            dressing_glb = _layer_paths("zoo_dressing_build", "_dressing.glb")
            fixtures_glb = _layer_paths("zoo_fixtures_build", "_fixtures.glb")
'''),

    (CLI, "cli: compose reads the memoised lot", '''\
                "lot_archetypes": _lot_for_compose(model, job.candidate_id),
''', '''\
                "lot_archetypes": _lot_rows(job.candidate_id),
'''),

    (CLI, "cli: lux resolves its one site and compose", '''\
            themed_job = next((d for d in job.depends_on
                               if "themed_site_assemble" in d), None)
            compose_job = next((d for d in job.depends_on
                                if "presentation_compose" in d), None)
''', '''\
            themed_job = _dep(job, "themed_site_assemble")
            compose_job = _dep(job, "presentation_compose")
'''),

    # ---- 3d: compose takes the layers as arguments --------------------

    (PRES, "presentation: a layer is looked up per building", '''\
def _driver_path() -> Path:
''', '''\
def _layer_map(value) -> dict:
    """``{archetype_id: path}`` for a content layer, keyed ``""`` for the shell.

    The mission's own shell has no archetype id and is keyed on the empty
    string, which is what the spec builder writes for a job with no
    `archetype_id`. A bare string is the PRE FAN-OUT shape and can only mean the
    mission shell -- back then there was exactly one layer to mean.
    """
    if isinstance(value, str):
        return {"": value} if value else {}
    return {str(k): str(v) for k, v in (value or {}).items() if v}


def _driver_path() -> Path:
'''),

    (PRES, "presentation: fingerprint every building's layers", '''\
        for key in ("dressing_glb", "fixtures_glb"):
            lp = job_spec.get(key)
            if lp and Path(str(lp)).exists():
                fp[key + "_hash"] = hash_file(Path(str(lp)))
''', '''\
        for key in ("dressing_glb", "fixtures_glb"):
            for aid, lp in sorted(_layer_map(job_spec.get(key)).items()):
                if not Path(str(lp)).exists():
                    continue
                # The mission shell keeps the historical key, so a single-shell
                # mission that has already composed does not recompose for a
                # rename. Per-building layers are new keys, so a varied lot
                # recomposes exactly once -- which it must, because until now
                # every building was fingerprinted against one building's props.
                fp[f"{key}_hash" if not aid else f"{key}_hash.{aid}"] = (
                    hash_file(Path(str(lp))))
'''),

    (PRES, "presentation: compose takes the layers as arguments", '''\
        def compose(*, slots, gameplay, greybox, out, bid, scene_rel):
''', '''\
        # `dressing` and `fixtures` are ARGUMENTS, and deliberately have no
        # defaults. They used to be read from the closed-over `job_spec` while
        # the six geometry arguments were overridden per archetype, so the loop
        # below dressed five different buildings out of one building's bake --
        # the failure the comment above that loop names. A layer that is not
        # visible at the call site is a layer nobody notices is shared.
        def compose(*, slots, gameplay, greybox, out, bid, scene_rel,
                    dressing, fixtures):
'''),

    (PRES, "presentation: pass the layers through", '''\
            if job_spec.get("dressing_glb"):
                args += ["--dressing", str(job_spec["dressing_glb"])]
            if job_spec.get("fixtures_glb"):
                args += ["--fixtures", str(job_spec["fixtures_glb"])]
''', '''\
            if dressing:
                args += ["--dressing", str(dressing)]
            if fixtures:
                args += ["--fixtures", str(fixtures)]
'''),

    (PRES, "presentation: the shell composes with the shell's layers", '''\
        cmds = [compose(
            slots=job_spec.get("slots_path"),
            gameplay=job_spec.get("gameplay_path"),
            greybox=job_spec.get("greybox_glb"),
            out=work / _OUT_SUBDIR, bid=_STABLE_BID, scene_rel=_SCENE_REL,
        )]
''', '''\
        dressing = _layer_map(job_spec.get("dressing_glb"))
        fixtures = _layer_map(job_spec.get("fixtures_glb"))
        cmds = [compose(
            slots=job_spec.get("slots_path"),
            gameplay=job_spec.get("gameplay_path"),
            greybox=job_spec.get("greybox_glb"),
            out=work / _OUT_SUBDIR, bid=_STABLE_BID, scene_rel=_SCENE_REL,
            dressing=dressing.get(""), fixtures=fixtures.get(""),
        )]
'''),

    (PRES, "presentation: each archetype composes with its own layers", '''\
            cmds.append(compose(
                slots=a.get("slots"), gameplay=a.get("gameplay"),
                greybox=a.get("glb"),
                out=work / _LOT_SUBDIR / str(a["id"]),
                bid=_STABLE_BID, scene_rel=rel,
            ))
''', '''\
            cmds.append(compose(
                slots=a.get("slots"), gameplay=a.get("gameplay"),
                greybox=a.get("glb"),
                out=work / _LOT_SUBDIR / str(a["id"]),
                bid=_STABLE_BID, scene_rel=rel,
                # ITS OWN props and ITS OWN light hardware. The three geometry
                # arguments above were already per building; these two were not,
                # and that is the entire difference between a building dressed
                # as itself and five buildings wearing one building's clothes.
                dressing=dressing.get(str(a["id"])),
                fixtures=fixtures.get(str(a["id"])),
            ))
'''),

    (PRES, "presentation: dressing is now per building", '''\
        # own slots, its own gameplay markers, its own greybox. Pointing five
        # different buildings at one composed scene would place five
        # greyboxes and dress them identically, which is the lie this exists
        # to remove.
''', '''\
        # own slots, its own gameplay markers, its own greybox, its own
        # dressing and its own light fixtures. Pointing five different
        # buildings at one composed scene would place five greyboxes and
        # dress them identically, which is the lie this exists to remove --
        # and which it performed until 2026-08-06, because dressing and
        # fixtures were the two things this list did not name.
'''),

    # ---- the art screen, which the fan-out breaks outright ------------

    (FACADE, "facade: the art screen aggregates a fanned stage", '''\
        for name, stage in _ART_SECTIONS:
            out = self._job_out(f"{mission_id}.{stage}")
            status = "done" if out.exists() and any(out.iterdir()) else "not_started"
            sections.append(ArtPassSection(name=name, status=status))
''', '''\
        for name, stage in _ART_SECTIONS:
            # AGGREGATE, not one row per building, and it is not a preference.
            # The placement stages run once per building now, so their job
            # directories are `<mission>.<stage>.<archetype>` and the single
            # `<mission>.<stage>` this looked for does not exist at all. Left
            # alone the screen reported "not_started" for a stage that had
            # completed five times -- an empty answer that looks exactly like a
            # quiet one.
            #
            # Per building ROWS were the alternative. Rejected: the lot size
            # would decide how many sections the screen has, and a row per
            # building says nothing the stage row does not until there is
            # something per building to say. DONE means EVERY building's job
            # published, so four of five finished still reads as unfinished.
            roots = (sorted(self.ws.jobs_dir.glob(f"{mission_id}.{stage}"))
                     + sorted(self.ws.jobs_dir.glob(f"{mission_id}.{stage}.*")))
            outs = [r / "out" for r in roots]
            status = ("done" if outs and all(
                o.exists() and any(o.iterdir()) for o in outs)
                else "not_started")
            sections.append(ArtPassSection(name=name, status=status))
'''),
]


def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    for path in TARGETS:
        if not path.is_file():
            print(f"[patch] {path} not found -- run from the factory root")
            return 1
    files: dict[Path, tuple[bytes, bool, str]] = {}
    for path in TARGETS:
        raw = path.read_bytes()
        crlf = b"\r\n" in raw
        files[path] = (raw, crlf, raw.decode("utf-8").replace("\r\n", "\n"))
        print(f"[patch] {path}: {len(raw)} bytes, "
              f"endings={'CRLF' if crlf else 'LF'}")

    problems = []
    applied = 0
    for path, name, before, after in EDITS:
        text = files[path][2]
        if after in text:
            print(f"[patch]   ALREADY APPLIED: {name}")
            applied += 1
        elif before not in text:
            print(f"[patch]   ANCHOR NOT FOUND: {name}")
            problems.append(name)
        elif text.count(before) != 1:
            print(f"[patch]   ANCHOR NOT UNIQUE ({text.count(before)}x): {name}")
            problems.append(name)
    if problems:
        print(f"[patch] REFUSING to write: {len(problems)} anchor(s) did not "
              f"match cleanly.")
        return 1
    if applied == len(EDITS):
        print("[patch] all edits already applied -- nothing to do")
        return 0

    for path, name, before, after in EDITS:
        raw, crlf, text = files[path]
        if after in text:
            continue
        files[path] = (raw, crlf, text.replace(before, after))
        print(f"[patch]   applied: {name}")

    if check_only:
        print("[patch] --check: no write")
        return 0
    for path, (raw, crlf, text) in files.items():
        payload = (text.replace("\n", "\r\n") if crlf else text).encode("utf-8")
        path.write_bytes(payload)
        print(f"[patch] wrote {path}: {len(raw)} -> {len(payload)} bytes "
              f"({len(payload) - len(raw):+d})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
