"""Level Factory 0.179.0: roof props reach a level, a job of their own per enterable building
(roadmap 181).

See `lf_roof_props/CHANGELOG_0.179.0.md`. Anchored edits, each asserted once, nothing written
until all of them matched:
  packages/pipeline/planner.py             `_STAGE_ZOO_ROOF`; a roof job per enterable building
                                           whose slots carry a roof slot, the brief's `roof_props`
                                           read; the compose waits on them
  packages/pipeline/building_library.py    `has_roof_slot`
  packages/core/models.py                  `MissionBrief.roof_props`, True
  apps/cli/commands/__init__.py            the job spec (mode roof_props) and the compose's
                                           `roofprops_glb`
  adapters/zoo/__init__.py                 the `roof_props` mode (validate, fingerprint, command);
                                           the kit branch's dead `roof_props_slots` read gone
  adapters/presentation/__init__.py        the third layer, validated, hashed, passed as
                                           --roofprops; `_circulation_arms` reads `roofprops`
  assets/scripts/run_presentation_compose.py  --roofprops -> `roofprops_glb`; the gate's third arm
  tests/unit/test_fanout.py                the fake library's shells carry a roof slot; the stage
                                           in the fan-out, compose and golden lists
  tests/fixtures/repos/zoo/tools/zoo_cli.py       the fake Zoo answers --roof-props
  tests/fixtures/repos/deli_counter/portable_building.py  the stub composer's third layer
  tests/integration/test_presentation_export.py   the stage asserted succeeded
  tests/unit/test_roof_props_stage.py      NEW, from `lf_roof_props/test_roof_props_stage.py.txt`
CHANGELOG and VERSION from `lf_roof_props/CHANGELOG_0.179.0.md`.

    python patches/patch_lf_roof_props.py --results-pending && cd level_factory && python -m pytest -q
    python patches/patch_lf_roof_props.py --fill
    LF_ROOT=<copy> python patches/patch_lf_roof_props.py --draft
"""
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LF = pathlib.Path(os.environ.get("LF_ROOT") or HERE.parent / "level_factory")
SRC = HERE / "lf_roof_props"
DRAFT = "--draft" in sys.argv
PENDING = "--results-pending" in sys.argv
FILL = "--fill" in sys.argv
RESULTS = {"RESULT_SUITE": "result_suite.txt"}
VERSION_WAS, VERSION = b"0.178.6", b"0.179.0"
CHANGELOG_HEAD = "## [0.178.6] - A light bake that fails is tried once more on a fresh copy\n"

PLANNER = "packages/pipeline/planner.py"
LIBRARY = "packages/pipeline/building_library.py"
MODELS = "packages/core/models.py"
COMMANDS = "apps/cli/commands/__init__.py"
ZOO = "adapters/zoo/__init__.py"
PRES = "adapters/presentation/__init__.py"
DRIVER = "assets/scripts/run_presentation_compose.py"
FANOUT = "tests/unit/test_fanout.py"
FAKE_ZOO = "tests/fixtures/repos/zoo/tools/zoo_cli.py"
STUB_DC = "tests/fixtures/repos/deli_counter/portable_building.py"
INTEG = "tests/integration/test_presentation_export.py"
NEW_TEST = "tests/unit/test_roof_props_stage.py"
SHA = {PLANNER: "5bc94d210ff47a0b", LIBRARY: "4c74d5459ce74de4", MODELS: "4af56a652009d0b9",
       COMMANDS: "63f4e6823a5d8cde", ZOO: "4f8796284a5c9ac9", PRES: "e54d0ff422a9fa61",
       DRIVER: "137d3106e305da45", FANOUT: "ce2eb59f05983197", FAKE_ZOO: "97ddfa0fc26c31eb",
       STUB_DC: "428b679369da54a0", INTEG: "ecf5cbd9a9653f46"}

# --- planner.py -----------------------------------------------------------------------------
P_STAGE_OLD = ("_STAGE_ZOO_FIXTURES = \"zoo_fixtures_build\"\n"
               "_STAGE_LUX_FIXTURE_GATE = \"lux_fixture_gate\"\n")
P_STAGE_NEW = ("_STAGE_ZOO_FIXTURES = \"zoo_fixtures_build\"\n"
               "# Roof props (0.179.0, roadmap 181): Zoo's rooftop scatter, a job of its\n"
               "# own per enterable building. In LAYER_ART with the kit it stands on.\n"
               "_STAGE_ZOO_ROOF = \"zoo_roof_props_build\"\n"
               "_STAGE_LUX_FIXTURE_GATE = \"lux_fixture_gate\"\n")
P_INIT_OLD = ("        zoo_dress_jids: list[str] = []\n"
              "        zoo_kit_jids: list[str] = []\n"
              "        for _entry in art_buildings:\n"
              "            aid = _entry[\"id\"] if _entry else None\n")
P_INIT_NEW = ("        zoo_dress_jids: list[str] = []\n"
              "        zoo_kit_jids: list[str] = []\n"
              "        # ROOF PROPS (0.179.0, roadmap 181): Zoo 0.25's rooftop scatter, a job\n"
              "        # of its own per enterable building whose slots carry a roof slot. The\n"
              "        # Zoo adapter's kit branch read `roof_props_slots` for this from 0.25\n"
              "        # to 0.178.6, and nothing wrote it -- nor could the one command it\n"
              "        # built have run both, since `zoo_cli` answers --roof-props before\n"
              "        # --build-kit and returns. An Empty is planned below, in its own loop,\n"
              "        # and gets none: its roof is never reached and carries its antenna\n"
              "        # already (Deli Counter 0.185.0). The brief's `roof_props: false`\n"
              "        # plans none at all. The mission's own shell (no library) is planned\n"
              "        # one unseen: its slots are written by its Deli Counter job, and every\n"
              "        # generated shell carries a roof slot but a `roof: none` demo.\n"
              "        zoo_roof_jids: list[str] = []\n"
              "        roof_props = bool(getattr(brief, \"roof_props\", True))\n"
              "        for _entry in art_buildings:\n"
              "            aid = _entry[\"id\"] if _entry else None\n")
P_JOB_OLD = ("            zoo_kit_jids.append(zoo_kit_jid)\n"
             "            # Patina names its outputs from the INPUT STEM\n")
P_JOB_NEW = ("            zoo_kit_jids.append(zoo_kit_jid)\n"
             "            if roof_props and (_entry is None\n"
             "                               or building_library.has_roof_slot(_entry)):\n"
             "                zoo_roof_jid = job_id(brief.mission_id, _STAGE_ZOO_ROOF,\n"
             "                                      archetype=aid)\n"
             "                plan.graph.add(Job(\n"
             "                    job_id=zoo_roof_jid, mission_id=brief.mission_id,\n"
             "                    stage_id=_STAGE_ZOO_ROOF, adapter_id=\"zoo\",\n"
             "                    candidate_id=selected_candidate, archetype_id=aid,\n"
             "                    resource_class=\"blender\",\n"
             "                    depends_on=[lot_jid, pixelcoat_jid],\n"
             "                    expected_outputs=[],  # zoo names by building_id at exec; adapter checks\n"
             "                ))\n"
             "                zoo_roof_jids.append(zoo_roof_jid)\n"
             "            # Patina names its outputs from the INPUT STEM\n")
P_COMPOSE_OLD = ("            depends_on=[deli_sel_jid, *zoo_kit_jids,\n"
                 "                        *zoo_dress_jids, *zoo_fixtures_jids],\n"
                 "            expected_outputs=[\"presentation/site.tscn\"],\n")
P_COMPOSE_NEW = ("            depends_on=[deli_sel_jid, *zoo_kit_jids,\n"
                 "                        *zoo_dress_jids, *zoo_fixtures_jids, *zoo_roof_jids],\n"
                 "            expected_outputs=[\"presentation/site.tscn\"],\n")

# --- building_library.py --------------------------------------------------------------------
L_OLD = "\n\n#: EMPTIES (0.137.0): Deli Counter's non-enterable shells with real fronts\n"
L_NEW = ("\n\n"
         "def has_roof_slot(entry) -> bool:\n"
         "    \"\"\"Does this library building's slot manifest carry a roof slot -- the\n"
         "    hook Zoo's roof props are planned on (0.179.0, roadmap 181)? False for\n"
         "    a manifest that cannot be read: a building whose slots are unreadable\n"
         "    gets no roof job rather than one that fails in Blender, and\n"
         "    `require_art_inputs` has already judged what the mission needs.\"\"\"\n"
         "    data = _manifest(entry.get(\"slots\") if isinstance(entry, dict) else entry)\n"
         "    return any(isinstance(s, dict) and s.get(\"role\") == \"roof\"\n"
         "               for s in ((data or {}).get(\"slots\") or []))\n"
         "\n\n"
         "#: EMPTIES (0.137.0): Deli Counter's non-enterable shells with real fronts\n")

# --- models.py ------------------------------------------------------------------------------
M_OLD = ("    cluster: str = \"\"\n"
         "    seed_policy: str = \"derived\"\n")
M_NEW = ("    cluster: str = \"\"\n"
         "    #: ROOF PROPS (0.179.0, roadmap 181): Zoo's rooftop scatter -- units, vent\n"
         "    #: stacks, fans, skylights, a dish -- on every enterable building's roof,\n"
         "    #: planned off its hatches and landings. `false` plans none. Not in the\n"
         "    #: functional signature: a roof prop is art and changes nothing a lock\n"
         "    #: protects, like the weather.\n"
         "    roof_props: bool = True\n"
         "    seed_policy: str = \"derived\"\n")

# --- apps/cli/commands/__init__.py ----------------------------------------------------------
C_SPEC_OLD = ("            elif job.stage_id == \"zoo_dressing_build\":\n"
              "                dress_job = _dep(job, \"patina_dressing\",\n")
C_SPEC_NEW = ("            elif job.stage_id == \"zoo_roof_props_build\":\n"
              "                # ROOF PROPS (0.179.0, roadmap 181): ITS OWN SLOTS, as the kit\n"
              "                # branch below reads them -- the library row's for an\n"
              "                # archetype, the Deli Counter job's `shell.slots.json` for the\n"
              "                # mission's own shell -- and the kit's skin library, found by\n"
              "                # candidate as the dressing branch finds it.\n"
              "                entry = _art_entry(job)\n"
              "                pix_job = next(\n"
              "                    (j.job_id for j in plan.graph.topological_order()\n"
              "                     if j.adapter_id == \"pixelcoat\"\n"
              "                     and j.candidate_id == job.candidate_id), None)\n"
              "                specs[job.job_id] = {\n"
              "                    \"mode\": \"roof_props\",\n"
              "                    \"seed\": int(str(job.candidate_id).rsplit(\"_\", 1)[-1]),\n"
              "                    \"theme\": model.theme or batch.get(\"theme_family\", \"\"),\n"
              "                    \"slots_path\": (str(entry[\"slots\"]) if entry\n"
              "                                   else str(_lot_slots(ws, jobs_dir, job))),\n"
              "                    \"wet\": _is_raining(model),\n"
              "                    \"skins_dir\": (str(_latest_output(jobs_dir / pix_job, \".\"))\n"
              "                                  if pix_job else \"\"),\n"
              "                }\n"
              "            elif job.stage_id == \"zoo_dressing_build\":\n"
              "                dress_job = _dep(job, \"patina_dressing\",\n")
C_LAYERS_OLD = ("            dressing_glb = _layer_paths(\"zoo_dressing_build\", \"_dressing.glb\")\n"
                "            fixtures_glb = _layer_paths(\"zoo_fixtures_build\", \"_fixtures.glb\")\n")
C_LAYERS_NEW = ("            dressing_glb = _layer_paths(\"zoo_dressing_build\", \"_dressing.glb\")\n"
                "            fixtures_glb = _layer_paths(\"zoo_fixtures_build\", \"_fixtures.glb\")\n"
                "            # the third layer (0.179.0): a building's roof props, its own\n"
                "            roofprops_glb = _layer_paths(\"zoo_roof_props_build\", \"_roofprops.glb\")\n")
C_DICT_OLD = ("                \"dressing_glb\": dressing_glb,\n"
              "                \"fixtures_glb\": fixtures_glb,\n")
C_DICT_NEW = ("                \"dressing_glb\": dressing_glb,\n"
              "                \"fixtures_glb\": fixtures_glb,\n"
              "                \"roofprops_glb\": roofprops_glb,\n")

# --- adapters/zoo/__init__.py ---------------------------------------------------------------
Z_VAL_OLD = ("        elif mode == \"habitat\":\n"
             "            # A SET of standalone species -- the Layer 3 clutter (roadmap\n")
Z_VAL_NEW = ("        elif mode == \"roof_props\":\n"
             "            # ROOF PROPS (0.179.0, roadmap 181): a job of its own over the\n"
             "            # building's slots, as the kit is.\n"
             "            slots = job_spec.get(\"slots_path\")\n"
             "            if not slots:\n"
             "                problems.append(\"zoo roof props build requires a slots.json\")\n"
             "            elif not Path(str(slots)).exists():\n"
             "                problems.append(f\"slots.json missing: {slots}\")\n"
             "        elif mode == \"habitat\":\n"
             "            # A SET of standalone species -- the Layer 3 clutter (roadmap\n")
Z_FP_OLD = ("        if job_spec.get(\"mode\") == \"habitat\":\n"
            "            fp[\"habitat\"] = str(job_spec.get(\"habitat\") or \"\")\n")
Z_FP_NEW = ("        if job_spec.get(\"mode\") == \"habitat\":\n"
            "            fp[\"habitat\"] = str(job_spec.get(\"habitat\") or \"\")\n"
            "        # The density IS a roof props job's input, folded in on the same rule.\n"
            "        if job_spec.get(\"mode\") == \"roof_props\" and job_spec.get(\"density\") is not None:\n"
            "            fp[\"density\"] = str(job_spec.get(\"density\"))\n")
Z_CMD_OLD = ("        if mode == \"dress\":\n"
             "            zoo_args = [\"--dress\", str(job_spec.get(\"manifest_path\", \"\")),\n")
Z_CMD_NEW = ("        if mode == \"roof_props\":\n"
             "            # ROOF PROPS (0.179.0, roadmap 181): a job of its own. The kit branch\n"
             "            # below carried `--roof-props` on the kit's command from 0.25 to\n"
             "            # 0.178.6 for a job spec key nothing wrote, and the command could not\n"
             "            # have built both: zoo_cli answers --roof-props before --build-kit\n"
             "            # and returns. --skins with --theme, the pair the dress branch\n"
             "            # explains; --wet gated on the library as everywhere.\n"
             "            zoo_args = [\"--roof-props\", str(job_spec.get(\"slots_path\", \"\")),\n"
             "                        \"--out\", str(work), \"--no-blend\"]\n"
             "            if job_spec.get(\"skins_dir\"):\n"
             "                zoo_args += [\"--skins\", str(job_spec[\"skins_dir\"])]\n"
             "            if job_spec.get(\"theme\"):\n"
             "                zoo_args += [\"--theme\", str(job_spec[\"theme\"])]\n"
             "            if job_spec.get(\"wet\") and job_spec.get(\"skins_dir\"):\n"
             "                zoo_args += [\"--wet\"]\n"
             "            if job_spec.get(\"seed\") is not None:\n"
             "                zoo_args += [\"--seed\", str(job_spec[\"seed\"])]\n"
             "            if job_spec.get(\"density\") is not None:\n"
             "                zoo_args += [\"--density\", str(job_spec[\"density\"])]\n"
             "            bid = _bid(job_spec.get(\"slots_path\")) or \"building\"\n"
             "            # both DECLARED: the compose needs the GLB, as it does the dressing's\n"
             "            expected = (f\"{bid}_roofprops.built.json\", f\"{bid}_roofprops.glb\")\n"
             "            args = [\"--background\", \"--python\", cli, \"--\", *zoo_args]\n"
             "            return [PlannedCommand(\n"
             "                executable=Path(blender), arguments=tuple(args),\n"
             "                working_directory=repo, expected_outputs=expected,\n"
             "                resource_class=\"blender\", timeout_seconds=1200,\n"
             "            )]\n"
             "        if mode == \"dress\":\n"
             "            zoo_args = [\"--dress\", str(job_spec.get(\"manifest_path\", \"\")),\n")
Z_DEAD_OLD = ("            if job_spec.get(\"roof_props_slots\"):\n"
              "                zoo_args += [\"--roof-props\", str(job_spec[\"roof_props_slots\"])]\n"
              "                if job_spec.get(\"density\"):\n"
              "                    zoo_args += [\"--density\", str(job_spec[\"density\"])]\n"
              "            bid = _bid(job_spec.get(\"slots_path\")) or \"building\"\n"
              "            expected = (f\"{bid}_kit.built.json\",)\n")
Z_DEAD_NEW = ("            # `roof_props_slots` used to add --roof-props to THIS command (0.25 to\n"
              "            # 0.178.6): nothing ever wrote the key, and zoo_cli would have\n"
              "            # answered --roof-props before --build-kit and returned, so the kit\n"
              "            # could never have been built by it. Roof props are the `roof_props`\n"
              "            # mode above (0.179.0, roadmap 181).\n"
              "            bid = _bid(job_spec.get(\"slots_path\")) or \"building\"\n"
              "            expected = (f\"{bid}_kit.built.json\",)\n")

# --- adapters/presentation/__init__.py ------------------------------------------------------
PR_VAL_OLD = ("        for key, suffix in ((\"dressing_glb\", \"_dressing.glb\"),\n"
              "                            (\"fixtures_glb\", \"_fixtures.glb\")):\n"
              "            for aid, directory in sorted(_layer_map(job_spec.get(key)).items()):\n"
              "                _, problem = resolve_layer(directory, suffix)\n")
PR_VAL_NEW = ("        for key, suffix in ((\"dressing_glb\", \"_dressing.glb\"),\n"
              "                            (\"fixtures_glb\", \"_fixtures.glb\"),\n"
              "                            (\"roofprops_glb\", \"_roofprops.glb\")):\n"
              "            for aid, directory in sorted(_layer_map(job_spec.get(key)).items()):\n"
              "                _, problem = resolve_layer(directory, suffix)\n")
PR_FP_OLD = ("        for key, suffix in ((\"dressing_glb\", \"_dressing.glb\"),\n"
             "                            (\"fixtures_glb\", \"_fixtures.glb\")):\n"
             "            for aid, directory in sorted(_layer_map(job_spec.get(key)).items()):\n"
             "                # The spec names a DIRECTORY -- the job that fills it has not\n")
PR_FP_NEW = ("        for key, suffix in ((\"dressing_glb\", \"_dressing.glb\"),\n"
             "                            (\"fixtures_glb\", \"_fixtures.glb\"),\n"
             "                            (\"roofprops_glb\", \"_roofprops.glb\")):\n"
             "            for aid, directory in sorted(_layer_map(job_spec.get(key)).items()):\n"
             "                # The spec names a DIRECTORY -- the job that fills it has not\n")
PR_SIG_OLD = ("        def compose(*, slots, gameplay, greybox, out, bid, scene_rel,\n"
              "                    dressing, fixtures, modules):\n")
PR_SIG_NEW = ("        def compose(*, slots, gameplay, greybox, out, bid, scene_rel,\n"
              "                    dressing, fixtures, roofprops, modules):\n")
PR_ARGS_OLD = ("            if fixtures:\n"
               "                args += [\"--fixtures\", str(fixtures)]\n"
               "            return PlannedCommand(\n")
PR_ARGS_NEW = ("            if fixtures:\n"
               "                args += [\"--fixtures\", str(fixtures)]\n"
               "            if roofprops:\n"
               "                args += [\"--roofprops\", str(roofprops)]\n"
               "            return PlannedCommand(\n")
PR_RES_OLD = ("        fixtures = {aid: resolve_layer(d, \"_fixtures.glb\")[0]\n"
              "                    for aid, d in _layer_map(\n"
              "                        job_spec.get(\"fixtures_glb\")).items()}\n")
PR_RES_NEW = ("        fixtures = {aid: resolve_layer(d, \"_fixtures.glb\")[0]\n"
              "                    for aid, d in _layer_map(\n"
              "                        job_spec.get(\"fixtures_glb\")).items()}\n"
              "        # the third layer (0.179.0, roadmap 181), keyed like the two above\n"
              "        roofprops = {aid: resolve_layer(d, \"_roofprops.glb\")[0]\n"
              "                     for aid, d in _layer_map(\n"
              "                         job_spec.get(\"roofprops_glb\")).items()}\n")
PR_ONE_OLD = ("            dressing=dressing.get(\"\"), fixtures=fixtures.get(\"\"),\n"
              "            modules=modules.get(\"\"),\n")
PR_ONE_NEW = ("            dressing=dressing.get(\"\"), fixtures=fixtures.get(\"\"),\n"
              "            roofprops=roofprops.get(\"\"),\n"
              "            modules=modules.get(\"\"),\n")
PR_LOT_OLD = ("                dressing=dressing.get(str(a[\"id\"])),\n"
              "                fixtures=fixtures.get(str(a[\"id\"])),\n"
              "                modules=modules.get(str(a[\"id\"])),\n")
PR_LOT_NEW = ("                dressing=dressing.get(str(a[\"id\"])),\n"
              "                fixtures=fixtures.get(str(a[\"id\"])),\n"
              "                roofprops=roofprops.get(str(a[\"id\"])),\n"
              "                modules=modules.get(str(a[\"id\"])),\n")
PR_ARMS_OLD = ("    arms = [(k, circ[k]) for k in (\"shell\", \"dressing\")\n"
               "            if isinstance(circ.get(k), Mapping)]\n")
PR_ARMS_NEW = ("    # `roofprops` since Deli Counter 0.209.0 (the third layer's arm)\n"
               "    arms = [(k, circ[k]) for k in (\"shell\", \"dressing\", \"roofprops\")\n"
               "            if isinstance(circ.get(k), Mapping)]\n")

# --- assets/scripts/run_presentation_compose.py ---------------------------------------------
D_ARG_OLD = ("    ap.add_argument(\"--fixtures\", default=\"\",\n"
             "                    help=\"zoo fixtures GLB (light fixtures + LuxEmit markers)\")\n")
D_ARG_NEW = ("    ap.add_argument(\"--fixtures\", default=\"\",\n"
             "                    help=\"zoo fixtures GLB (light fixtures + LuxEmit markers)\")\n"
             "    ap.add_argument(\"--roofprops\", default=\"\",\n"
             "                    help=\"zoo roof props GLB (rooftop units) to bundle + instance\")\n")
D_LIN_OLD = ("    for layer in (a.dressing, a.fixtures):\n"
             "        if not layer:\n")
D_LIN_NEW = ("    for layer in (a.dressing, a.fixtures, a.roofprops):\n"
             "        if not layer:\n")
D_KW_OLD = ("    if a.fixtures:\n"
            "        layer_kwargs[\"fixtures_glb\"] = a.fixtures\n")
D_KW_NEW = ("    if a.fixtures:\n"
            "        layer_kwargs[\"fixtures_glb\"] = a.fixtures\n"
            "    if a.roofprops:\n"
            "        layer_kwargs[\"roofprops_glb\"] = a.roofprops\n")
D_ARMS_OLD = ("    arms = [(k, circ[k]) for k in (\"shell\", \"dressing\")\n"
              "            if isinstance(circ.get(k), dict)]\n")
D_ARMS_NEW = ("    arms = [(k, circ[k]) for k in (\"shell\", \"dressing\", \"roofprops\")\n"
              "            if isinstance(circ.get(k), dict)]\n")

# --- tests/unit/test_fanout.py --------------------------------------------------------------
T_LIB_OLD = ("        (root / f\"{aid}.slots.json\").write_text(\n"
             "            json.dumps({\"coverage\": {\"wall\": 96, \"doorway\": 4}}\n"
             "                       if themeable else {}), encoding=\"utf-8\")\n")
T_LIB_NEW = ("        # A ROOF SLOT on every themeable shell (0.179.0): 133 of the real\n"
             "        # library's 145 carry one, and it is what a roof props job is\n"
             "        # planned on.\n"
             "        (root / f\"{aid}.slots.json\").write_text(\n"
             "            json.dumps({\"coverage\": {\"wall\": 96, \"doorway\": 4},\n"
             "                        \"slots\": [{\"slot_id\": \"roof_footprint\", \"role\": \"roof\",\n"
             "                                   \"fit\": {\"dims\": [20.0, 12.0, 0.3]}}]}\n"
             "                       if themeable else {}), encoding=\"utf-8\")\n")
T_PUB_OLD = ("            if job.stage_id not in (\"zoo_dressing_build\", \"zoo_fixtures_build\"):\n"
             "                continue\n"
             "            out = ws.jobs_dir / job.job_id / \"out\"\n"
             "            out.mkdir(parents=True, exist_ok=True)\n"
             "            bid = job.archetype_id or \"shell\"\n"
             "            kind = (\"dressing\" if job.stage_id == \"zoo_dressing_build\"\n"
             "                    else \"fixtures\")\n")
T_PUB_NEW = ("            kinds = {\"zoo_dressing_build\": \"dressing\",\n"
             "                     \"zoo_fixtures_build\": \"fixtures\",\n"
             "                     \"zoo_roof_props_build\": \"roofprops\"}\n"
             "            if job.stage_id not in kinds:\n"
             "                continue\n"
             "            out = ws.jobs_dir / job.job_id / \"out\"\n"
             "            out.mkdir(parents=True, exist_ok=True)\n"
             "            bid = job.archetype_id or \"shell\"\n"
             "            kind = kinds[job.stage_id]\n")
T_FAN_OLD = ("    for stage in (\"patina_apply\", \"patina_dressing\", \"zoo_dressing_build\",\n"
             "                  \"zoo_fixtures_build\", \"zoo_kit_build\"):\n")
T_FAN_NEW = ("    for stage in (\"patina_apply\", \"patina_dressing\", \"zoo_dressing_build\",\n"
             "                  \"zoo_fixtures_build\", \"zoo_kit_build\", \"zoo_roof_props_build\"):\n")
T_WAIT_OLD = ("    for stage in (\"zoo_dressing_build\", \"zoo_fixtures_build\"):\n"
              "        deps = {j.job_id for j in _stages(plan, stage)}\n")
T_WAIT_NEW = ("    for stage in (\"zoo_dressing_build\", \"zoo_fixtures_build\",\n"
              "                  \"zoo_roof_props_build\"):\n"
              "        deps = {j.job_id for j in _stages(plan, stage)}\n")
T_GOLD_OLD = ("    assert f\"{MISSION}.zoo_fixtures_build\" in jobs\n"
              "    assert f\"{MISSION}.lux_fixture_gate\" in jobs\n")
T_GOLD_NEW = ("    assert f\"{MISSION}.zoo_fixtures_build\" in jobs\n"
              "    # 0.179.0 grew the plan by the roof props job (roadmap 181): art on the\n"
              "    # roof, nothing the lock protects, so the golden moved on purpose.\n"
              "    assert f\"{MISSION}.zoo_roof_props_build\" in jobs\n"
              "    assert f\"{MISSION}.lux_fixture_gate\" in jobs\n")
T_DEPS_OLD = ("        f\"{MISSION}.zoo_dressing_build\",\n"
              "        f\"{MISSION}.zoo_fixtures_build\"]\n")
T_DEPS_NEW = ("        f\"{MISSION}.zoo_dressing_build\",\n"
              "        f\"{MISSION}.zoo_fixtures_build\",\n"
              "        f\"{MISSION}.zoo_roof_props_build\"]\n")

# --- the fake Zoo and the stub composer -----------------------------------------------------
F_OLD = "\n    if a.fixtures:\n"
F_NEW = ("\n"
         "    if a.roof_props:\n"
         "        # the roof props build (Level Factory 0.179.0): its own index and GLB\n"
         "        bid = _bid(a.roof_props)\n"
         "        idx = out / f\"{bid}_roofprops.built.json\"\n"
         "        idx.write_text(json.dumps(\n"
         "            {\"mode\": \"roof_props\", \"building_id\": bid, \"props_built\": 2,\n"
         "             \"counts\": {\"hvac_unit\": 1, \"vent_stack\": 1}}, sort_keys=True))\n"
         "        (out / f\"{bid}_roofprops.glb\").write_bytes(_stub_glb(\"zoo-roofprops\"))\n"
         "        print(f\"[zoo] index: {idx}\")\n"
         "        return 0\n"
         "    if a.fixtures:\n")
S_SIG_OLD = ("                  theme, style=1, building_id=None, greybox_glb=None,\n"
             "                  dressing_glb=None, fixtures_glb=None):\n")
S_SIG_NEW = ("                  theme, style=1, building_id=None, greybox_glb=None,\n"
             "                  dressing_glb=None, fixtures_glb=None, roofprops_glb=None):\n")
S_LOOP_OLD = ("    for layer_name, layer_glb in ((\"dressing\", dressing_glb),\n"
              "                                  (\"fixtures\", fixtures_glb)):\n")
S_LOOP_NEW = ("    for layer_name, layer_glb in ((\"dressing\", dressing_glb),\n"
              "                                  (\"fixtures\", fixtures_glb),\n"
              "                                  (\"roofprops\", roofprops_glb)):\n")
I_OLD = ("    for stage in (\"pixelcoat_build\", \"zoo_kit_build\", \"patina_apply\",\n"
         "                  \"patina_dressing\", \"zoo_dressing_build\", \"presentation_compose\",\n"
         "                  \"lux_apply\", \"dispatch_handoff\"):\n")
I_NEW = ("    for stage in (\"pixelcoat_build\", \"zoo_kit_build\", \"patina_apply\",\n"
         "                  \"patina_dressing\", \"zoo_dressing_build\", \"zoo_roof_props_build\",\n"
         "                  \"presentation_compose\", \"lux_apply\", \"dispatch_handoff\"):\n")


def _eol(raw, rel):
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    assert crlf in (0, lf), (rel, "mixed line endings", crlf, lf)
    return b"\r\n" if crlf else b"\n"


def _src(name):
    return (SRC / name).read_bytes().decode("utf-8").replace("\r\n", "\n")


def _once(text, old, new, what):
    assert text.count(old) == 1, (what, text.count(old))
    return text.replace(old, new)


def _read(rel):
    p = LF / rel
    raw = p.read_bytes()
    got = hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()[:16]
    assert got == SHA[rel], (rel, "is not the file this patch read", got)
    return p, _eol(raw, rel), raw.decode("utf-8").replace("\r\n", "\n")


def _write(p, eol, text):
    p.write_bytes(text.replace("\n", eol.decode()).encode("utf-8"))


def fill():
    assert (LF / "VERSION").read_bytes().strip() == VERSION, (LF / "VERSION").read_bytes()
    results = {}
    for key, name in RESULTS.items():
        value = (SRC / name).read_text(encoding="utf-8").strip()
        assert value and "RESULT_" not in value and not value.endswith("."), (name, value[-40:])
        results[key] = value
    writes = {}
    for path, rel in [(LF / "CHANGELOG.md", "CHANGELOG.md"), (SRC / "CHANGELOG_0.179.0.md", "the entry")]:
        raw = path.read_bytes()
        eol = _eol(raw, rel)
        text = raw.decode("utf-8").replace("\r\n", "\n")
        for key, value in results.items():
            assert text.count(key) == 1, (rel, key, text.count(key))
            text = text.replace(key, value)
        writes[path] = text.encode("utf-8").replace(b"\n", eol)
    for path, data in writes.items():
        path.write_bytes(data)
    print("Level Factory 0.179.0: results filled")


def main():
    if FILL:
        return fill()
    if DRAFT and not os.environ.get("LF_ROOT"):
        sys.exit("refusing: --draft is for an LF_ROOT copy, never the repo")
    assert (LF / "VERSION").read_bytes().strip() == VERSION_WAS, (LF / "VERSION").read_bytes()
    entry = _src("CHANGELOG_0.179.0.md")
    assert entry.startswith("## [0.179.0] - "), entry[:40]
    if not DRAFT:
        left = entry
        if PENDING:
            for key in RESULTS:
                left = left.replace(key, "")
        assert "RESULT_" not in left, "the changelog still carries an unfilled result"
    new_test = _src("test_roof_props_stage.py.txt")
    assert not (LF / NEW_TEST).exists(), "already applied"

    edits = []

    p, eol, t = _read(PLANNER)
    assert "_STAGE_ZOO_ROOF" not in t, "already applied"
    t = _once(t, P_STAGE_OLD, P_STAGE_NEW, "the stage constants")
    t = _once(t, P_INIT_OLD, P_INIT_NEW, "the art loop's head")
    t = _once(t, P_JOB_OLD, P_JOB_NEW, "the roof job after the kit")
    t = _once(t, P_COMPOSE_OLD, P_COMPOSE_NEW, "the compose's dependencies")
    edits.append((p, eol, t))

    p, eol, t = _read(LIBRARY)
    t = _once(t, L_OLD, L_NEW, "has_roof_slot before the Empties")
    edits.append((p, eol, t))

    p, eol, t = _read(MODELS)
    t = _once(t, M_OLD, M_NEW, "the brief's roof_props")
    edits.append((p, eol, t))

    p, eol, t = _read(COMMANDS)
    t = _once(t, C_SPEC_OLD, C_SPEC_NEW, "the roof job's spec")
    t = _once(t, C_LAYERS_OLD, C_LAYERS_NEW, "the compose's layer paths")
    t = _once(t, C_DICT_OLD, C_DICT_NEW, "the compose spec's layers")
    edits.append((p, eol, t))

    p, eol, t = _read(ZOO)
    t = _once(t, Z_VAL_OLD, Z_VAL_NEW, "the adapter's validation")
    t = _once(t, Z_FP_OLD, Z_FP_NEW, "the adapter's fingerprint")
    t = _once(t, Z_CMD_OLD, Z_CMD_NEW, "the adapter's command")
    t = _once(t, Z_DEAD_OLD, Z_DEAD_NEW, "the kit branch's dead read")
    assert "roof_props_slots" in t and t.count("roof_props_slots") == 1, "the note stands alone"
    edits.append((p, eol, t))

    p, eol, t = _read(PRES)
    t = _once(t, PR_VAL_OLD, PR_VAL_NEW, "the presentation adapter's validation")
    t = _once(t, PR_FP_OLD, PR_FP_NEW, "the presentation adapter's fingerprint")
    t = _once(t, PR_SIG_OLD, PR_SIG_NEW, "compose()'s signature")
    t = _once(t, PR_ARGS_OLD, PR_ARGS_NEW, "compose()'s arguments")
    t = _once(t, PR_RES_OLD, PR_RES_NEW, "the layer resolution")
    t = _once(t, PR_ONE_OLD, PR_ONE_NEW, "the mission shell's compose")
    t = _once(t, PR_LOT_OLD, PR_LOT_NEW, "each archetype's compose")
    t = _once(t, PR_ARMS_OLD, PR_ARMS_NEW, "_circulation_arms")
    edits.append((p, eol, t))

    p, eol, t = _read(DRIVER)
    t = _once(t, D_ARG_OLD, D_ARG_NEW, "the driver's --roofprops")
    t = _once(t, D_LIN_OLD, D_LIN_NEW, "the lineage guard")
    t = _once(t, D_KW_OLD, D_KW_NEW, "the layer kwargs")
    t = _once(t, D_ARMS_OLD, D_ARMS_NEW, "circulation_gate's arms")
    edits.append((p, eol, t))

    p, eol, t = _read(FANOUT)
    t = _once(t, T_LIB_OLD, T_LIB_NEW, "the fake library's slots")
    t = _once(t, T_PUB_OLD, T_PUB_NEW, "the published layers")
    t = _once(t, T_FAN_OLD, T_FAN_NEW, "the fan-out list")
    t = _once(t, T_WAIT_OLD, T_WAIT_NEW, "the compose-waits list")
    t = _once(t, T_GOLD_OLD, T_GOLD_NEW, "the golden plan's jobs")
    t = _once(t, T_DEPS_OLD, T_DEPS_NEW, "the golden compose dependencies")
    edits.append((p, eol, t))

    p, eol, t = _read(FAKE_ZOO)
    t = _once(t, F_OLD, F_NEW, "the fake Zoo's roof props")
    edits.append((p, eol, t))

    p, eol, t = _read(STUB_DC)
    t = _once(t, S_SIG_OLD, S_SIG_NEW, "the stub composer's signature")
    t = _once(t, S_LOOP_OLD, S_LOOP_NEW, "the stub composer's layers")
    edits.append((p, eol, t))

    p, eol, t = _read(INTEG)
    t = _once(t, I_OLD, I_NEW, "the integration run's stages")
    edits.append((p, eol, t))

    cl = LF / "CHANGELOG.md"
    cl_raw = cl.read_bytes()
    cl_eol = _eol(cl_raw, "CHANGELOG.md")
    cl_text = cl_raw.decode("utf-8").replace("\r\n", "\n")
    assert cl_text.startswith(CHANGELOG_HEAD) and cl_text.count(CHANGELOG_HEAD) == 1, cl_text[:90]
    # every anchor matched: now write
    for p, eol, t in edits:
        _write(p, eol, t)
    _write(LF / NEW_TEST, b"\n", new_test)
    _write(cl, cl_eol, entry.rstrip("\n") + "\n\n" + cl_text)
    (LF / "VERSION").write_bytes(VERSION)
    print("Level Factory 0.178.6 -> 0.179.0" + (" (DRAFT)" if DRAFT else ""))


if __name__ == "__main__":
    main()
