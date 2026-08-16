r"""level_factory 0.35.0 -- Lux becomes a layer you can decline.

    python patches\patch_lf_035.py --check
    python patches\patch_lf_035.py
    python patches\patch_lf_035.py --selftest
    python patches\patch_lf_035.py --revert

Run from the FACTORY ROOT. Roadmap item 47, stage 1.

WHAT THIS IS FOR

A team bringing its own renderer wants everything the art pass produces and
none of Lux's result. Today that is impossible: `LAYER_ART` means
"Zoo + Pixelcoat + Patina + Lux", one indivisible thing, and `--art` is the
only way to ask for any of it.

ONLY THE APPLY PASS MOVES

`lux_apply` is the render solution and it is the only stage behind the new
layer. `zoo_fixtures_build` bakes the physical light hardware from the locked
shell's manifest, and `lux_fixture_gate` machine-checks it -- spawn count,
lamp-to-hardware co-location, powered kill/restore, findings BLOCKING. A
floating light or a dark fixture is broken GEOMETRY whoever ends up lighting
it, so both stay in `LAYER_ART`.

That is the useful part of the split: an unlit art package still ships
validated fixtures and their `LuxEmit` markers, which is a contract somebody
else's lighting system can actually read, rather than a vague promise that
"the lights were meant to go about here".

`--art` STILL MEANS WHAT IT MEANT

`--art` continues to produce a lit level, and `--target presentation`
continues to plan the full stack. If `--art` silently stopped producing
lighting, every existing script that says `--art` would change what it ships
without anyone typing anything. `--unlit` subtracts the light layer; nothing
subtracts it by default.

THE ONE LINE THAT CARRIES THE RISK

    dispatch_dep = lux_jid

lives at the end of the art branch. With the split it becomes

    dispatch_dep = lux_jid if LAYER_LIGHT in layers else themed_jid

and getting it wrong hands Dispatch a scene nobody would notice was wrong:
falling through to the graybox default would build the handoff on a site with
no art pass on it and report success. `themed_jid` is bound unconditionally
at the same indentation inside the same branch -- checked, not assumed -- so
the `else` cannot raise. Six of this patch's tests are about this line.

LIGHT IS NOT INDEPENDENT, AND THE OTHER TWO ARE

`lux_apply` runs over `themed_site_assemble`'s output, so light-without-art
is asking to light a place that was never themed. The DAG's answer to that
today would be to plan nothing at all, silently, because a plan with no jobs
is a legal plan. `normalize_layers` refuses instead, and every path into
`plan_mission` goes through it.

THE EXPORT SIDE MOVES WITH IT

0.34.0 made `_layers_produced` read the art layer from what the art layer
produces. It now reads the light layer from `lux_apply`'s output, which is
what that directory always meant. Two tests in
`tests/unit/test_export_layers.py` change with it: a workspace with Lux
output now reports `{art, light}` rather than `{art}`, which is more true
than what it said before and is exactly what an art-unlit package needs
`LF_MANIFEST.json` to distinguish.

WHAT STAGE 1 DOES NOT DO

There is no `art-unlit` export MODE yet. A mission RUN without the light
layer already exports correctly -- no `lux_apply` output means no
`presentation/` directory, `_root_site_wanted(None)` keeps the themed
`site.tscn`, and `write_entry_scene`'s `elif` makes that the entry. What is
still missing is export-time subtraction: taking a mission that DID run Lux
and shipping an unlit package from it, so a recipient can A/B two archives
from one build. That is stage 2.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

PLANNER = "level_factory/packages/pipeline/planner.py"
MAIN = "level_factory/apps/cli/main.py"
CMDS = "level_factory/apps/cli/commands/__init__.py"
EXPORT_TEST = "level_factory/tests/unit/test_export_layers.py"
PLANNER_TEST = "level_factory/tests/unit/test_planner_graph.py"
NEW_TEST = "level_factory/tests/unit/test_light_layer.py"
VERSION_F = "level_factory/VERSION"
CHANGELOG = "level_factory/CHANGELOG.md"
SIDECAR = ".pre_035"

OLD_V, NEW_V = "0.34.0", "0.35.0"

EDITS: list[tuple[str, str, str]] = [
    # ------------------------------------------------------------- constants
    (PLANNER,
     "# Composable output layers. Graybox (DC greybox+collision, assembled by Lot) is\n"
     "# the always-on base; Art and Gameplay are independent optional layers.\n"
     'LAYER_ART = "art"          # Zoo swaps + props/dressing, Pixelcoat, Patina, Lux\n'
     'LAYER_GAMEPLAY = "gameplay"  # Dispatch objective/nav/spawn suggestions (advisory)\n'
     "ALL_LAYERS = frozenset({LAYER_ART, LAYER_GAMEPLAY})\n",

     "# Composable output layers. Graybox (DC greybox+collision, assembled by Lot) is\n"
     "# the always-on base; Art, Light and Gameplay are the optional layers on top.\n"
     'LAYER_ART = "art"          # Zoo swaps + props/dressing, Pixelcoat, Patina\n'
     'LAYER_LIGHT = "light"      # Lux\'s APPLY pass -- the render solution, only that\n'
     'LAYER_GAMEPLAY = "gameplay"  # Dispatch objective/nav/spawn suggestions (advisory)\n'
     "ALL_LAYERS = frozenset({LAYER_ART, LAYER_LIGHT, LAYER_GAMEPLAY})\n"
     "\n"
     "#: ONLY THE APPLY PASS IS IN LAYER_LIGHT. `zoo_fixtures_build` bakes the\n"
     "#: physical light hardware from the locked shell's manifest and\n"
     "#: `lux_fixture_gate` machine-checks it -- spawn count, lamp-to-hardware\n"
     "#: co-location, powered kill/restore, findings BLOCKING. A floating light\n"
     "#: or a dark fixture is broken GEOMETRY whoever lights it, so both stay in\n"
     "#: LAYER_ART. An unlit art package therefore still ships validated\n"
     "#: fixtures and their `LuxEmit` markers, which is a contract another\n"
     "#: lighting system can read.\n"
     "#:\n"
     "#: LIGHT IS NOT INDEPENDENT, and the other two layers are. `lux_apply`\n"
     "#: runs over `themed_site_assemble`'s output, so light-without-art asks to\n"
     "#: light a place that was never themed. The DAG's answer would be to plan\n"
     "#: nothing at all -- silently, because a plan with no jobs is a legal\n"
     "#: plan. `normalize_layers` refuses instead.\n"
     "_LAYER_REQUIRES = {LAYER_LIGHT: LAYER_ART}\n"),

    # ------------------------------------------------------- target mapping
    (PLANNER,
     "    TARGET_PRESENTATION: frozenset({LAYER_ART, LAYER_GAMEPLAY}),  # full stack\n",

     "    # UNCHANGED IN MEANING. `--target presentation` has always produced a\n"
     "    # LIT level; splitting the light layer out must not quietly stop it.\n"
     "    TARGET_PRESENTATION: frozenset({LAYER_ART, LAYER_LIGHT,\n"
     "                                    LAYER_GAMEPLAY}),  # full stack\n"),

    # ------------------------------------------------------ normalize_layers
    (PLANNER,
     "def label_for_layers(layers) -> str:\n",

     "def normalize_layers(layers) -> frozenset:\n"
     '    """Validate a layer set, or REFUSE it. Never silently repair it.\n'
     "\n"
     "    Two ways to be wrong, and both used to produce a plan rather than an\n"
     "    error:\n"
     "\n"
     "    A typo'd layer name was simply not in any `in layers` test, so\n"
     "    `--art` misspelt planned the graybox base and reported success.\n"
     "\n"
     "    `light` without `art` reaches the `lux_apply` block only from inside\n"
     "    `if LAYER_ART in layers:`, so it plans nothing -- and a plan with no\n"
     "    optional jobs is a legal plan that runs, succeeds, and produces the\n"
     "    graybox somebody did not ask for.\n"
     "\n"
     "    Adding the missing layer would be worse than refusing. A caller who\n"
     "    asked for light and gets a full art pass has been billed for four\n"
     "    tools it did not request.\n"
     '    """\n'
     "    lset = frozenset(layers or ())\n"
     "    unknown = sorted(lset - ALL_LAYERS)\n"
     "    if unknown:\n"
     "        raise ValueError(\n"
     '            f"unknown layer(s): {\', \'.join(unknown)}; "\n'
     '            f"known layers are {\', \'.join(sorted(ALL_LAYERS))}")\n'
     "    for layer, needs in sorted(_LAYER_REQUIRES.items()):\n"
     "        if layer in lset and needs not in lset:\n"
     "            raise ValueError(\n"
     '                f"the {layer!r} layer requires the {needs!r} layer: "\n'
     '                f"lux_apply runs over themed_site_assemble\'s output, so "\n'
     '                f"there is nothing to light without it")\n'
     "    return lset\n"
     "\n"
     "\n"
     "def label_for_layers(layers) -> str:\n"),

    # ----------------------------------------------------------- the label
    (PLANNER,
     '    parts = ["graybox"]\n'
     "    if LAYER_ART in lset:\n"
     '        parts.append("art")\n'
     "    if LAYER_GAMEPLAY in lset:\n"
     '        parts.append("gameplay")\n'
     '    return "+".join(parts)\n',

     '    parts = ["graybox"]\n'
     "    if LAYER_ART in lset:\n"
     '        parts.append("art")\n'
     "    if LAYER_LIGHT in lset:\n"
     '        parts.append("light")\n'
     "    if LAYER_GAMEPLAY in lset:\n"
     '        parts.append("gameplay")\n'
     '    return "+".join(parts)\n'),

    # --------------------------------------------------- plan_mission docstring
    (PLANNER,
     "      * LAYER_ART      -> Pixelcoat + Zoo (kit swaps + props/dressing) + Patina + Lux\n"
     "      * LAYER_GAMEPLAY -> Dispatch objective/nav/spawn suggestions (advisory)\n"
     "    Layers are independent and apply only once a candidate is selected + locked.\n",

     "      * LAYER_ART      -> Pixelcoat + Zoo (kit swaps + props/dressing + light\n"
     "                          fixtures and their gate) + Patina + the themed site\n"
     "      * LAYER_LIGHT    -> Lux's apply pass over the themed site. Requires ART.\n"
     "      * LAYER_GAMEPLAY -> Dispatch objective/nav/spawn suggestions (advisory)\n"
     "    ART and GAMEPLAY are independent; LIGHT requires ART, because there is\n"
     "    nothing to light before `themed_site_assemble` has made a place. All of\n"
     "    them apply only once a candidate is selected + locked.\n"),

    # ---------------------------------------------------- plan_mission guard
    (PLANNER,
     "    layers = frozenset(layers) if layers is not None else layers_for_target(target)\n",

     "    # Through the validator on EVERY path, not just the explicit one. A\n"
     "    # bad layer set that reaches the DAG produces a plan, and a plan runs.\n"
     "    layers = normalize_layers(\n"
     "        layers if layers is not None else layers_for_target(target))\n"),

    # -------------------------------------------------------- the lux job
    (PLANNER,
     "        # Lux apply (final PS2 look) over the themed SITE \u2014 not the greybox\n"
     "        # site, and not the single composed building it used to light.\n"
     "        lux_jid = job_id(brief.mission_id, _STAGE_LUX)\n",

     "        # Lux apply (final PS2 look) over the themed SITE \u2014 not the greybox\n"
     "        # site, and not the single composed building it used to light.\n"
     "        #\n"
     "        # BEHIND LAYER_LIGHT since 0.35.0, and it is the ONLY stage that\n"
     "        # moved. The fixture bake and its gate below stay in LAYER_ART:\n"
     "        # they are about where the hardware physically is, which is a\n"
     "        # question about the level rather than about the render.\n"
     "        lux_jid = \"\"\n"
     "        if LAYER_LIGHT in layers:\n"
     "            lux_jid = job_id(brief.mission_id, _STAGE_LUX)\n"),

    (PLANNER,
     "        plan.graph.add(Job(\n"
     "            job_id=lux_jid, mission_id=brief.mission_id,\n"
     "            stage_id=_STAGE_LUX, adapter_id=\"lux\",\n"
     "            candidate_id=selected_candidate, resource_class=\"godot_headless\",\n"
     "            depends_on=[themed_jid],\n"
     "            expected_outputs=[\"lux.applied.tscn\", \"lux.quality.json\",\n"
     "                              \"lux.validation.json\"],\n"
     "        ))\n",

     "            plan.graph.add(Job(\n"
     "                job_id=lux_jid, mission_id=brief.mission_id,\n"
     "                stage_id=_STAGE_LUX, adapter_id=\"lux\",\n"
     "                candidate_id=selected_candidate,\n"
     "                resource_class=\"godot_headless\",\n"
     "                depends_on=[themed_jid],\n"
     "                expected_outputs=[\"lux.applied.tscn\", \"lux.quality.json\",\n"
     "                                  \"lux.validation.json\"],\n"
     "            ))\n"),

    # ----------------------------------------------------- the dispatch dep
    (PLANNER,
     "        # Dispatch depends on the Lux-applied presentation, not just the Lot site.\n"
     "        dispatch_dep = lux_jid\n",

     "        # Dispatch depends on the LIT presentation when there is one, and on\n"
     "        # the THEMED SITE when the light layer is off. Never back to the\n"
     "        # graybox default: `themed_site_assemble` is the last stage that\n"
     "        # makes a place, and an unlit art package is still that place.\n"
     "        # Falling through would hand Dispatch a site with no art pass on it\n"
     "        # and report success, which is the whole reason this is a\n"
     "        # conditional rather than a deletion.\n"
     "        #\n"
     "        # `themed_jid` is bound unconditionally at this indentation inside\n"
     "        # this branch -- verified, not assumed -- so the else cannot raise.\n"
     "        dispatch_dep = lux_jid if LAYER_LIGHT in layers else themed_jid\n"),

    # --------------------------------------------------------------- the CLI
    (MAIN,
     '    br.add_argument("--art", action="store_true", help="add the Art layer (Zoo/Pixelcoat/Patina/Lux)")\n',

     '    br.add_argument("--art", action="store_true",\n'
     '                    help="add the Art layer AND the Light layer "\n'
     '                         "(Zoo/Pixelcoat/Patina + Lux)")\n'
     '    br.add_argument("--unlit", action="store_true",\n'
     '                    help="with --art: drop the Light layer (Lux). Fixtures "\n'
     '                         "and their gate still ship.")\n'),

    (MAIN,
     '    sp.add_argument("--art", action="store_true", help="add the Art layer")\n',

     '    sp.add_argument("--art", action="store_true",\n'
     '                    help="add the Art layer AND the Light layer")\n'
     '    sp.add_argument("--unlit", action="store_true",\n'
     '                    help="with --art: drop the Light layer (Lux)")\n'),

    (MAIN,
     '    sp.add_argument("--art", action="store_true",\n'
     '                    help="add the Art layer (Zoo swaps + props/dressing, Pixelcoat, Patina, Lux)")\n',

     '    sp.add_argument("--art", action="store_true",\n'
     '                    help="add the Art layer (Zoo swaps + props/dressing + light "\n'
     '                         "fixtures, Pixelcoat, Patina) AND the Light layer (Lux)")\n'
     '    sp.add_argument("--unlit", action="store_true",\n'
     '                    help="with --art: drop the Light layer. The level is themed "\n'
     '                         "and dressed, its light fixtures are baked and gated, and "\n'
     '                         "no Lux render is applied -- for a team bringing its own.")\n'),

    (CMDS,
     '    """Resolve the composable layer set from CLI args. Explicit --art/--gameplay\n'
     '    win; otherwise fall back to the legacy --target mapping; otherwise graybox."""\n'
     "    from packages.pipeline.planner import LAYER_ART, LAYER_GAMEPLAY, layers_for_target\n"
     '    art = bool(getattr(args, "art", False))\n'
     '    gameplay = bool(getattr(args, "gameplay", False))\n'
     "    if art or gameplay:\n"
     "        layers = set()\n"
     "        if art:\n"
     "            layers.add(LAYER_ART)\n"
     "        if gameplay:\n"
     "            layers.add(LAYER_GAMEPLAY)\n"
     "        return frozenset(layers)\n",

     '    """Resolve the composable layer set from CLI args. Explicit --art/--gameplay\n'
     "    win; otherwise fall back to the legacy --target mapping; otherwise graybox.\n"
     "\n"
     "    `--art` MEANS WHAT IT ALWAYS MEANT: art AND light. 0.35.0 split Lux's\n"
     "    apply pass into its own layer, and if `--art` had quietly stopped\n"
     "    producing lighting, every existing script saying `--art` would ship\n"
     "    something different without anyone typing anything. `--unlit`\n"
     '    subtracts the light layer; nothing subtracts it by default."""\n'
     "    from packages.pipeline.planner import (\n"
     "        LAYER_ART, LAYER_GAMEPLAY, LAYER_LIGHT, layers_for_target,\n"
     "    )\n"
     '    art = bool(getattr(args, "art", False))\n'
     '    gameplay = bool(getattr(args, "gameplay", False))\n'
     '    unlit = bool(getattr(args, "unlit", False))\n'
     "    if art or gameplay:\n"
     "        layers = set()\n"
     "        if art:\n"
     "            layers.add(LAYER_ART)\n"
     "            if not unlit:\n"
     "                layers.add(LAYER_LIGHT)\n"
     "        if gameplay:\n"
     "            layers.add(LAYER_GAMEPLAY)\n"
     "        return frozenset(layers)\n"),

    # ------------------------------------------------- the export inference
    (CMDS,
     "    from packages.pipeline.planner import LAYER_ART, LAYER_GAMEPLAY\n"
     "    layers = set()\n"
     "    if compose_root.exists() or lux_dir.exists():\n"
     "        layers.add(LAYER_ART)\n"
     "    if handoff_dir.exists():\n"
     "        layers.add(LAYER_GAMEPLAY)\n"
     "    return layers\n",

     "    from packages.pipeline.planner import (\n"
     "        LAYER_ART, LAYER_GAMEPLAY, LAYER_LIGHT,\n"
     "    )\n"
     "    layers = set()\n"
     "    if compose_root.exists() or lux_dir.exists():\n"
     "        layers.add(LAYER_ART)\n"
     "    # `lux_apply`'s output is what this directory always meant. Since\n"
     "    # 0.35.0 it answers its own question instead of standing in for the\n"
     "    # art layer, which is what an art-unlit package needs LF_MANIFEST.json\n"
     "    # to be able to say.\n"
     "    if lux_dir.exists():\n"
     "        layers.add(LAYER_LIGHT)\n"
     "    if handoff_dir.exists():\n"
     "        layers.add(LAYER_GAMEPLAY)\n"
     "    return layers\n"),

    # ---------------------- the planner suite, which asserted the old meaning
    #
    # FOUR TESTS FAIL WITHOUT THIS, and every one of them is right to. They
    # were written when LAYER_ART meant "and Lux", so they ask for
    # {LAYER_ART} and then assert lux_apply is planned. The layer set they
    # request is what changed; not one assertion is weakened.
    (PLANNER_TEST,
     "def test_art_layer_has_full_art_pass_but_no_dispatch():\n"
     "    st = _stages(frozenset({LAYER_ART}))\n"
     '    assert {"pixelcoat_build", "zoo_kit_build", "patina_apply", "patina_dressing",\n'
     '            "zoo_dressing_build", "presentation_compose", "lux_apply"} <= st\n'
     '    assert "dispatch_handoff" not in st  # art alone never runs the gameplay layer\n',

     "def test_art_layer_has_full_art_pass_but_no_dispatch():\n"
     "    # ART + LIGHT since 0.35.0: `lux_apply` moved behind its own layer, so\n"
     "    # this asks for both to keep asserting the same stage list.\n"
     "    st = _stages(frozenset({LAYER_ART, LAYER_LIGHT}))\n"
     '    assert {"pixelcoat_build", "zoo_kit_build", "patina_apply", "patina_dressing",\n'
     '            "zoo_dressing_build", "presentation_compose", "lux_apply"} <= st\n'
     '    assert "dispatch_handoff" not in st  # art alone never runs the gameplay layer\n'
     "\n"
     "\n"
     "def test_the_art_layer_alone_stops_at_the_themed_site():\n"
     '    """The other half of the split, asserted here too.\n'
     "\n"
     "    Everything above stays; only the render leaves. See\n"
     '    tests/unit/test_light_layer.py for the rest."""\n'
     "    st = _stages(frozenset({LAYER_ART}))\n"
     '    assert {"pixelcoat_build", "zoo_kit_build", "patina_apply",\n'
     '            "patina_dressing", "zoo_dressing_build", "presentation_compose",\n'
     '            "themed_site_assemble", "zoo_fixtures_build",\n'
     '            "lux_fixture_gate"} <= st\n'
     '    assert "lux_apply" not in st\n'),

    (PLANNER_TEST,
     "    plan = plan_mission(_brief(), seed_base=1997, layers=frozenset({LAYER_ART}),\n"
     "                        selected_candidate=_SEL)\n"
     "    jobs = {j.stage_id: j for j in plan.graph.jobs()}\n"
     '    assert "presentation_compose" in jobs\n',

     "    plan = plan_mission(_brief(), seed_base=1997,\n"
     "                        layers=frozenset({LAYER_ART, LAYER_LIGHT}),\n"
     "                        selected_candidate=_SEL)\n"
     "    jobs = {j.stage_id: j for j in plan.graph.jobs()}\n"
     '    assert "presentation_compose" in jobs\n'),

    (PLANNER_TEST,
     "def test_both_layers_dispatch_builds_on_art_scene():\n"
     "    plan = plan_mission(_brief(), seed_base=1997,\n"
     "                        layers=frozenset({LAYER_ART, LAYER_GAMEPLAY}), selected_candidate=_SEL)\n"
     "    disp = next(j for j in plan.graph.jobs() if j.stage_id == \"dispatch_handoff\")\n"
     '    assert disp.depends_on[0].endswith("lux_apply")\n',

     "def test_both_layers_dispatch_builds_on_art_scene():\n"
     "    # The LIT stack, spelled out. What happens when the light layer is off\n"
     "    # is the whole point of 0.35.0 and is asserted in test_light_layer.py:\n"
     "    # dispatch falls back to themed_site_assemble, never to the graybox.\n"
     "    plan = plan_mission(_brief(), seed_base=1997,\n"
     "                        layers=frozenset({LAYER_ART, LAYER_LIGHT,\n"
     "                                          LAYER_GAMEPLAY}),\n"
     "                        selected_candidate=_SEL)\n"
     "    disp = next(j for j in plan.graph.jobs() if j.stage_id == \"dispatch_handoff\")\n"
     '    assert disp.depends_on[0].endswith("lux_apply")\n'),

    (PLANNER_TEST,
     "    assert layers_for_target(TARGET_PRESENTATION) == frozenset({LAYER_ART, LAYER_GAMEPLAY})\n",

     "    # presentation has always meant a LIT level; 0.35.0 names the light\n"
     "    # layer explicitly rather than changing what the target produces.\n"
     "    assert layers_for_target(TARGET_PRESENTATION) == frozenset(\n"
     "        {LAYER_ART, LAYER_LIGHT, LAYER_GAMEPLAY})\n"),

    (PLANNER_TEST,
     "from packages.pipeline.planner import (  # noqa: E402\n"
     "    LAYER_ART, LAYER_GAMEPLAY, layers_for_target, label_for_layers,\n"
     "    TARGET_PRESENTATION,\n"
     ")\n",

     "from packages.pipeline.planner import (  # noqa: E402\n"
     "    LAYER_ART, LAYER_GAMEPLAY, LAYER_LIGHT, layers_for_target,\n"
     "    label_for_layers, TARGET_PRESENTATION,\n"
     ")\n"),

    # ------------------------------- the two export tests the split changes
    (EXPORT_TEST,
     "def test_lux_alone_still_reports_the_art_layer(tmp_path):\n"
     '    """The union, not a replacement. An existing workspace must not start\n'
     '    describing itself differently after the upgrade."""\n'
     "    assert _layers_produced(**_dirs(tmp_path, lux=True)) == {LAYER_ART}\n"
     "\n"
     "\n"
     "def test_both_report_it_once(tmp_path):\n"
     "    assert _layers_produced(**_dirs(tmp_path, compose=True, lux=True)) == {LAYER_ART}\n",

     "def test_lux_alone_still_reports_the_art_layer(tmp_path):\n"
     '    """The union, not a replacement. An existing workspace must not start\n'
     "    describing itself with FEWER layers after the upgrade.\n"
     "\n"
     "    It reports one MORE since 0.35.0: Lux output is the light layer, and\n"
     '    saying so is what lets an art-unlit package be told apart."""\n'
     "    assert _layers_produced(\n"
     "        **_dirs(tmp_path, lux=True)) == {LAYER_ART, LAYER_LIGHT}\n"
     "\n"
     "\n"
     "def test_both_report_art_once_and_light_too(tmp_path):\n"
     "    assert _layers_produced(\n"
     "        **_dirs(tmp_path, compose=True, lux=True)\n"
     "    ) == {LAYER_ART, LAYER_LIGHT}\n"
     "\n"
     "\n"
     "def test_an_art_pass_without_lux_is_art_without_light(tmp_path):\n"
     '    """THE POINT OF ROADMAP 47. Themed, dressed, unlit -- and the manifest\n'
     '    says exactly that rather than calling it a graybox or calling it lit."""\n'
     "    got = _layers_produced(**_dirs(tmp_path, compose=True))\n"
     "    assert got == {LAYER_ART}\n"
     "    assert LAYER_LIGHT not in got\n"),

    (EXPORT_TEST,
     "from packages.pipeline.planner import LAYER_ART, LAYER_GAMEPLAY  # noqa: E402\n",

     "from packages.pipeline.planner import (  # noqa: E402\n"
     "    LAYER_ART, LAYER_GAMEPLAY, LAYER_LIGHT,\n"
     ")\n"),
]

NEW_FILES: dict[str, str] = {
    NEW_TEST: '''"""LAYER_LIGHT: Lux's apply pass, and only that, is declinable.

Roadmap item 47 stage 1. Six of these are about one line --

    dispatch_dep = lux_jid if LAYER_LIGHT in layers else themed_jid

-- because getting it wrong builds the Dispatch handoff on the wrong scene
and reports success, which is a failure nobody would see.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from packages.core.models import MissionBrief  # noqa: E402
from packages.pipeline.planner import (  # noqa: E402
    ALL_LAYERS, LAYER_ART, LAYER_GAMEPLAY, LAYER_LIGHT, TARGET_PRESENTATION,
    label_for_layers, layers_for_target, normalize_layers, plan_mission,
)

CAND = "m1.candidate.seed_1997"


def _brief():
    return MissionBrief(mission_id="m1", display_name="M1",
                        archetype="urban_bank", candidate_count=1)


def _plan(layers):
    return plan_mission(_brief(), seed_base=1997, layers=layers,
                        selected_candidate=CAND)


def _stages(plan):
    return {j.stage_id for j in plan.graph.jobs()}


def _job(plan, stage_id):
    matches = [j for j in plan.graph.jobs() if j.stage_id == stage_id]
    assert len(matches) == 1, f"{stage_id}: {[j.job_id for j in matches]}"
    return matches[0]


# --------------------------------------------------------------- the vocabulary

def test_light_is_a_layer():
    assert LAYER_LIGHT in ALL_LAYERS


def test_presentation_still_means_the_full_lit_stack():
    """--target presentation has always produced a LIT level."""
    assert layers_for_target(TARGET_PRESENTATION) == frozenset(
        {LAYER_ART, LAYER_LIGHT, LAYER_GAMEPLAY})


def test_the_label_names_the_light_layer():
    assert label_for_layers({LAYER_ART}) == "graybox+art"
    assert label_for_layers({LAYER_ART, LAYER_LIGHT}) == "graybox+art+light"
    assert label_for_layers(
        {LAYER_ART, LAYER_LIGHT, LAYER_GAMEPLAY}) == "graybox+art+light+gameplay"


def test_light_without_art_is_refused_not_repaired():
    """It would otherwise plan NOTHING and succeed.

    `lux_apply` is reached only from inside `if LAYER_ART in layers`, so a
    light-only request produces a graybox plan that runs and reports success.
    Adding art silently would be worse: a caller who asked for light would be
    billed for four tools it never requested.
    """
    with pytest.raises(ValueError) as exc:
        normalize_layers({LAYER_LIGHT})
    assert "requires" in str(exc.value)


def test_an_unknown_layer_is_refused():
    with pytest.raises(ValueError):
        normalize_layers({"lighting"})


def test_plan_mission_validates_too():
    """Not just the helper -- the door everything comes through."""
    with pytest.raises(ValueError):
        plan_mission(_brief(), seed_base=1997, layers={LAYER_LIGHT},
                     selected_candidate=CAND)


# ------------------------------------------------------------- what is planned

def test_light_on_plans_lux_apply():
    assert "lux_apply" in _stages(_plan({LAYER_ART, LAYER_LIGHT}))


def test_light_off_does_not():
    assert "lux_apply" not in _stages(_plan({LAYER_ART}))


def test_the_fixture_pass_stays_in_the_art_layer():
    """THE PART THAT MUST NOT MOVE.

    Where the light hardware physically is, and whether it is co-located with
    its lamp, is a question about the LEVEL. An unlit package still ships
    validated fixtures and their LuxEmit markers for another lighting system.
    """
    unlit = _stages(_plan({LAYER_ART}))
    assert "zoo_fixtures_build" in unlit
    assert "lux_fixture_gate" in unlit


def test_the_themed_site_stays_in_the_art_layer():
    assert "themed_site_assemble" in _stages(_plan({LAYER_ART}))


# ------------------------------------------------- the one line that carries it

def test_dispatch_depends_on_lux_when_lit():
    plan = _plan({LAYER_ART, LAYER_LIGHT, LAYER_GAMEPLAY})
    assert _job(plan, "dispatch_handoff").depends_on == [
        _job(plan, "lux_apply").job_id]


def test_dispatch_depends_on_the_themed_site_when_unlit():
    """NOT the greybox, which is where a fallthrough would land it.

    `themed_site_assemble` is the last stage that makes a place. Handing
    Dispatch the graybox instead would build the handoff on a site with no art
    pass on it and report success.
    """
    plan = _plan({LAYER_ART, LAYER_GAMEPLAY})
    assert _job(plan, "dispatch_handoff").depends_on == [
        _job(plan, "themed_site_assemble").job_id]


def test_the_unlit_handoff_does_not_depend_on_the_graybox():
    plan = _plan({LAYER_ART, LAYER_GAMEPLAY})
    dep = _job(plan, "dispatch_handoff").depends_on[0]
    assert "lot_assemble" not in dep


def test_a_graybox_gameplay_plan_is_unchanged():
    """No art at all still means Dispatch rides the Lot site."""
    plan = _plan({LAYER_GAMEPLAY})
    dep = _job(plan, "dispatch_handoff").depends_on[0]
    assert "lot_assemble" in dep


def test_no_dangling_dependencies_either_way():
    """A dependency on a job that was never planned is exactly what the
    conditional could produce, and a DAG will happily hold one."""
    for layers in ({LAYER_ART, LAYER_GAMEPLAY},
                   {LAYER_ART, LAYER_LIGHT, LAYER_GAMEPLAY}):
        plan = _plan(layers)
        planned = {j.job_id for j in plan.graph.jobs()}
        for j in plan.graph.jobs():
            missing = [d for d in j.depends_on if d not in planned]
            assert not missing, f"{layers} -> {j.job_id} needs {missing}"


def test_the_unlit_plan_is_the_lit_plan_minus_exactly_one_stage():
    lit = _stages(_plan({LAYER_ART, LAYER_LIGHT, LAYER_GAMEPLAY}))
    unlit = _stages(_plan({LAYER_ART, LAYER_GAMEPLAY}))
    assert lit - unlit == {"lux_apply"}
    assert not unlit - lit
''',
}

ENTRY = """## [0.35.0] - Lux becomes a layer you can decline

`LAYER_ART` meant "Zoo + Pixelcoat + Patina + Lux", one indivisible thing, so
a team bringing its own renderer had no way to ask for the art pass without
the render. `LAYER_LIGHT` splits Lux's apply pass out. Roadmap item 47,
stage 1.

ONLY THE APPLY PASS MOVED

`lux_apply` is the render solution and it is the only stage behind the new
layer. `zoo_fixtures_build` bakes the physical light hardware from the locked
shell's manifest and `lux_fixture_gate` machine-checks it -- spawn count,
lamp-to-hardware co-location, powered kill/restore, findings BLOCKING. A
floating light or a dark fixture is broken GEOMETRY whoever lights it, so
both stay in `LAYER_ART`.

That is the useful part: an unlit art package still ships validated fixtures
and their `LuxEmit` markers, which another lighting system can read as a
contract rather than a guess.

`--art` STILL MEANS WHAT IT MEANT

`--art` produces a lit level and `--target presentation` plans the full
stack, both unchanged. If `--art` had quietly stopped producing lighting,
every existing script saying `--art` would ship something different without
anyone typing anything. `--unlit` subtracts the light layer; nothing
subtracts it by default.

THE ONE LINE THAT CARRIES THE RISK

    dispatch_dep = lux_jid if LAYER_LIGHT in layers else themed_jid

Falling through to the graybox default would build the Dispatch handoff on a
site with no art pass on it and report success. `themed_site_assemble` is the
last stage that makes a place, and an unlit art package is still that place.
`themed_jid` is bound unconditionally at the same indentation in the same
branch, so the else cannot raise -- checked rather than assumed. Six tests in
`tests/unit/test_light_layer.py` cover this line, including one that asserts
no job in either plan depends on a job that was never planned.

LIGHT REQUIRES ART, AND IS REFUSED WITHOUT IT

`lux_apply` runs over `themed_site_assemble`'s output, so light-without-art
asks to light a place that was never themed. The DAG's answer would be a plan
with no optional jobs -- which is legal, runs, and succeeds, producing a
graybox nobody asked for. `normalize_layers` raises instead, and
`plan_mission` routes every path through it, including the legacy `--target`
mapping. Adding the missing layer silently would be worse: a caller who asked
for light would be billed for four tools it never requested. An unknown layer
name is refused the same way, which it never was -- `--art` misspelt used to
plan the graybox and report success.

THE EXPORT SIDE

`_layers_produced` reads the light layer from `lux_apply`'s output, which is
what that directory always meant; 0.34.0 had just finished stopping it from
standing in for the art layer as well. A workspace with Lux output now
reports `{art, light}` rather than `{art}` -- one more layer than before,
never fewer, and the distinction is what `LF_MANIFEST.json` needs to describe
an art-unlit package honestly.

NOT IN THIS RELEASE

There is no `art-unlit` export MODE. A mission RUN without the light layer
already exports correctly: no `lux_apply` output means no `presentation/`
directory, `_root_site_wanted(None)` keeps the themed `site.tscn`, and
`write_entry_scene`'s `elif` makes that the entry. What is missing is
export-time subtraction -- taking a mission that DID run Lux and shipping an
unlit package from it, so two archives from one build can be compared. Stage
2.
"""


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _eol(raw: bytes) -> str:
    return "\r\n" if b"\r\n" in raw else "\n"


def _as(text: str, eol: str) -> str:
    return text if eol == "\n" else text.replace("\n", eol)


def _apply(root: Path, *, check: bool) -> int:
    by_file: dict[str, list[tuple[str, str]]] = {}
    for rel, old, new in EDITS:
        by_file.setdefault(rel, []).append((old, new))

    for rel, edits in by_file.items():
        p = root / rel
        if not p.is_file():
            print(f"REFUSING: {rel} is not here")
            return 1
        raw = p.read_bytes()
        eol = _eol(raw)
        out, done = raw.decode("utf-8"), 0
        for old, new in edits:
            old_f, new_f = _as(old, eol), _as(new, eol)
            if new_f in out:
                done += 1
                continue
            if out.count(old_f) != 1:
                print(f"REFUSING: {rel} -- an anchor occurs {out.count(old_f)} "
                      f"time(s), expected 1:\n    "
                      f"{old.strip().splitlines()[0][:72]}")
                return 1
            out = out.replace(old_f, new_f, 1)
        if done == len(edits):
            print(f"  already applied  {rel}")
            continue
        if p.suffix == ".py":
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

    for rel, content in NEW_FILES.items():
        p = root / rel
        data = content.encode("utf-8")
        if p.is_file():
            if p.read_bytes() == data:
                print(f"  already applied  {rel}")
                continue
            print(f"REFUSING: {rel} exists and is not what this patch writes")
            return 1
        try:
            compile(content, str(p), "exec")
        except SyntaxError as exc:
            print(f"REFUSING: {rel} -- does not parse: {exc}")
            return 1
        if check:
            print(f"  would create {rel}  {len(data):,} bytes")
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        print(f"  created      {rel}  {len(data):,} bytes  "
              f"sha256 {_sha(data)[:16]}")

    vp, cp = root / VERSION_F, root / CHANGELOG
    vraw, craw = vp.read_bytes(), cp.read_bytes()
    vbody, cbody = vraw.decode("utf-8"), craw.decode("utf-8")
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
    for q, rawb in ((vp, vraw), (cp, craw)):
        side = q.with_suffix(q.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(rawb)
    vp.write_bytes(vbody.replace(OLD_V, NEW_V, 1).encode("utf-8"))
    ceol = _eol(craw)
    cp.write_bytes((_as(ENTRY, ceol) + _as("\n", ceol) + cbody).encode("utf-8"))
    print(f"  bumped       VERSION  {OLD_V} -> {NEW_V}")
    print("  prepended    CHANGELOG.md")
    return 0


def selftest(root: Path) -> int:
    import subprocess
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    lf = (root / "level_factory").resolve()

    def run(*paths):
        return subprocess.run([sys.executable, "-m", "pytest", *paths],
                              cwd=str(lf), capture_output=True, text=True)

    print("  the light-layer unit tests --")
    r = run("tests/unit/test_light_layer.py")
    for line in (r.stdout + r.stderr).strip().splitlines()[-4:]:
        print(f"       {line}")
    check("THE LIGHT LAYER TESTS PASS", r.returncode == 0)

    print()
    print("  the export-layer tests the split changed --")
    r2 = run("tests/unit/test_export_layers.py")
    for line in (r2.stdout + r2.stderr).strip().splitlines()[-4:]:
        print(f"       {line}")
    check("THE EXPORT LAYER TESTS PASS", r2.returncode == 0)

    print()
    print("  the planner's own suite, which asserted the OLD meaning --")
    r3 = run("tests/unit/test_planner_graph.py")
    for line in (r3.stdout + r3.stderr).strip().splitlines()[-4:]:
        print(f"       {line}")
    check("THE PLANNER SUITE PASSES", r3.returncode == 0)

    print()
    print("  service + integration, green at 0.34.0 -- this takes ~2.5 min --")
    r4 = run("tests/service", "tests/integration")
    for line in (r4.stdout + r4.stderr).strip().splitlines()[-4:]:
        print(f"       {line}")
    check("STILL GREEN -- --target presentation is unchanged", r4.returncode == 0)

    v = (root / VERSION_F).read_text(encoding="utf-8").strip()
    py = (root / "level_factory/pyproject.toml").read_text(encoding="utf-8")
    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    flat = " ".join(cl.split())
    check(f"VERSION is {NEW_V}", v == NEW_V)
    # 0.34.0 asked whether pyproject carried the same STRING, and this patch
    # bumped VERSION without it, so the drift 0.34.0 had just corrected
    # restarted in the very next release. patch_lf_035b.py removes the second
    # copy: pyproject declares the version dynamic and points at VERSION.
    # There is no string to compare any more, so ask about the mechanism.
    check("pyproject takes its version FROM VERSION (no second copy)",
          'dynamic = ["version"]' in py
          and 'version = {file = "VERSION"}' in py)
    check(f"one {NEW_V} entry", cl.count(f"## [{NEW_V}]") == 1)
    check("the entry says --art is unchanged",
          "still means what it meant" in flat.lower())
    check("and names the one risky line",
          "dispatch_dep = lux_jid if LAYER_LIGHT in layers else themed_jid"
          in flat)
    check("and says the fixture pass did not move",
          "both stay in `LAYER_ART`" in flat)

    print()
    print("  NOT VERIFIED HERE: an actual unlit RUN through real tools, and")
    print("  the art-unlit export MODE, which is stage 2. These are plans and")
    print("  layer sets -- correct DAGs, not executed ones.")

    print()
    print("  Lux is a layer you can decline"
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
        for rel in (PLANNER, MAIN, CMDS, EXPORT_TEST, PLANNER_TEST,
                    VERSION_F, CHANGELOG):
            p = root / rel
            side = p.with_suffix(p.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {rel}")
                bad = 1
                continue
            p.write_bytes(side.read_bytes())
            print(f"  reverted     {rel}")
        for rel, content in NEW_FILES.items():
            p = root / rel
            if not p.is_file():
                print(f"  already gone {rel}")
                continue
            if p.read_bytes() != content.encode("utf-8"):
                print(f"  KEPT (edited since) {rel}")
                bad = 1
                continue
            p.unlink()
            print(f"  removed      {rel}")
        return bad
    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_lf_035.py --selftest")
        print()
        print("  Stage 2 is the art-unlit export MODE: dropping Lux at EXPORT")
        print("  time, from a mission that ran it, so two archives compare.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
