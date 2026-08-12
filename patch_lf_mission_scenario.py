r"""Laser Tag evaluates the mission's encounter instead of its own stock one.

    python patch_lf_mission_scenario.py --explain
    python patch_lf_mission_scenario.py --check
    python patch_lf_mission_scenario.py
    python patch_lf_mission_scenario.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

## The measurement this comes from

`lot_demo_001` seed 5118, 25 runs, 45/100 FAIL. Traversal 0 of 25, because
`route_completion_rate` is 0.0, because `team_wipe_count` is 25.

    player_count   1     player_health   5
    enemy_count    6     enemy_health    2

The crew must land **twelve** hits to clear the map. It fires 15-17 shots and
lands 6-9, and has never killed more than 2 of 6 across fifty recorded runs --
25 before the collider patch and 25 after. It absorbs five hits and dies.

**The scenario is unwinnable, and `route_completed` requires surviving the
route.** Traversal's 25 points cannot be earned by any arrangement of geometry.
Per `site_spawns.OPENING_RANGE`'s own note -- one visible enemy is 0% route
completion by construction -- and with six enemies at 35 m sight on any real
map, the crew will see one.

So the 45 is mostly a fact about `default_laser_tag_scenario.tres`, and Level
Factory has been running Laser Tag's stock resource on every mission it has ever
evaluated. A five-building night heist and a single-shell test box are graded
against the same 1-versus-6.

## The hook already exists and nothing reaches it

    scenario = str(job_spec.get(
        "scenario_res",
        "res://addons/laser_tag_tool/resources/default_laser_tag_scenario.tres"))

`scenario_res` has been readable from the job spec since the adapter was
written. Nothing has ever set it. Same shape as `PLATE_ROLES`, as
`site_lux.tscn`, as `solids` not reaching `place_enemies`: the seam is cut and
nothing is threaded through it.

## The change

Three files, and the derivation is deliberately dull.

  * **`MissionBrief`** gains `crew_size`, `crew_health`, `enemy_count` and
    `enemy_health`. Defaults are exactly today's numbers -- 1, 5, 6, 2 -- so
    every existing brief produces the identical scenario and no evaluated
    mission changes underneath its grade.

  * **The Laser Tag job spec** carries a `scenario` dict built from those four
    fields. It is a dict rather than a path because the adapter already
    fingerprints `job_spec["scenario"]`: making it the VALUES means changing the
    encounter re-runs the evaluation, and making it a path would have
    fingerprinted the string while the file underneath moved.

  * **The adapter** writes `mission_scenario.tres` into the staged project and
    points `--scenario` at it. Everything the brief does not name is copied from
    the stock resource verbatim, in one table, so drift between LF's copy and
    Laser Tag's is a diff rather than an archaeology problem.

Nothing is derived from `building_count`, `target_minutes` or `verticality`.
A crew size inferred from a plate area would be a number nobody chose, dressed
as a decision -- which is the thing this tree keeps finding. If a mission wants
four people, its brief says four people.

## What this does NOT do

**It does not change Lot's `place_enemies(enemy_count=6)`.** Lot writes six
enemy hooks and `LT_MapEvalHarness` spawns `scenario.enemy_count` of them over
whatever points it finds, so a scenario asking for fewer uses a subset and the
even spread along the route is no longer even. That is a real seam and it is
one wire, not this patch: the count would have to reach `_write_site_spec` and
`write_walk_scene` as well. Until it does, **change `crew_size` and leave
`enemy_count` at 6** -- which is also the honest heist framing, since the thing
the brief was missing was a crew, not fewer guards.

**It does not touch `functional_signature`.** `enemy_count` genuinely changes
the walk scene and so arguably belongs in the lock, but adding a key to that
signature invalidates every lock already on disk -- `rockay-ws` carries one.
That is a migration with its own decisions, not a line in this patch.

**It does not predict the grade.** Four crew against six may still wipe; the
crew may complete the route and the map may still lose points to 34 enemy-stuck
events and 37% overexposure, which have other causes entirely. What it does is
make the encounter a property of the mission, so the question can be asked at
all.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

MODELS = Path("level_factory") / "packages" / "core" / "models.py"
CMDS = Path("level_factory") / "apps" / "cli" / "commands" / "__init__.py"
ADAPTER = Path("level_factory") / "adapters" / "laser_tag" / "__init__.py"
SIDECAR = ".pre_missionscenario"


# --------------------------------------------------------------------------
# models.py
# --------------------------------------------------------------------------

BRIEF_OLD = '''    lot_library: str = ""
    notes: str = ""'''

BRIEF_NEW = '''    lot_library: str = ""
    #: THE ENCOUNTER, which the brief could not previously express at all.
    #:
    #: Every mission Level Factory has ever evaluated was graded against Laser
    #: Tag's stock `default_laser_tag_scenario.tres`: one crew member with 5
    #: health against six enemies with 2 each. Measured on `lot_demo_001` seed
    #: 5118 over 50 runs, the crew must land twelve hits to clear the map, lands
    #: six to nine, and wipes 25 times out of 25. `route_completed` requires
    #: surviving the route, so traversal's 25 of 100 points were unreachable by
    #: any arrangement of geometry.
    #:
    #: DEFAULTS ARE THE STOCK NUMBERS on purpose. An existing brief produces a
    #: scenario identical to the one it was graded under, so no evaluated
    #: mission changes underneath its grade.
    #:
    #: Nothing here is derived from `building_count` or `target_minutes`. A crew
    #: size inferred from plate area would be a number nobody chose wearing the
    #: clothes of a decision; if a mission wants four people it says four.
    crew_size: int = 1
    crew_health: int = 5
    #: Lot still places six enemy hooks regardless (`place_enemies`' own
    #: default), and the harness spawns this many over the points it finds. Set
    #: it below six and the even spread along the route stops being even --
    #: wiring the count through to `_write_site_spec` is the follow-up.
    enemy_count: int = 6
    enemy_health: int = 2
    notes: str = ""'''


# --------------------------------------------------------------------------
# commands/__init__.py
# --------------------------------------------------------------------------

SPEC_OLD = '''            specs[job.job_id] = {
                "seed": int(job.candidate_id.rsplit("_", 1)[-1]),
                "run_count": 25,
                # Laser Tag evaluates the walkable candidate scene.
                "evaluation_scene": str(_latest_output(lot_out, "site_walk.tscn")),'''

SPEC_NEW = '''            specs[job.job_id] = {
                "seed": int(job.candidate_id.rsplit("_", 1)[-1]),
                "run_count": 25,
                # THE MISSION'S ENCOUNTER, not Laser Tag's stock one. The
                # adapter has read `scenario_res` from this dict since it was
                # written and nothing ever set it, so every mission was graded
                # 1-versus-6 whatever its brief said.
                #
                # VALUES rather than a path, because `fingerprint_inputs`
                # already hashes `job_spec["scenario"]`: the numbers being here
                # means changing the encounter re-runs the evaluation. A path
                # would have fingerprinted the string while the file underneath
                # it moved.
                "scenario": {
                    "player_count": int(getattr(model, "crew_size", 1)),
                    "player_health": int(getattr(model, "crew_health", 5)),
                    "enemy_count": int(getattr(model, "enemy_count", 6)),
                    "enemy_health": int(getattr(model, "enemy_health", 2)),
                },
                # Already read by the staging hook injector and already in the
                # fingerprint; it just had no source but a default.
                "enemy_count": int(getattr(model, "enemy_count", 6)),
                # Laser Tag evaluates the walkable candidate scene.
                "evaluation_scene": str(_latest_output(lot_out, "site_walk.tscn")),'''


# --------------------------------------------------------------------------
# adapters/laser_tag/__init__.py
# --------------------------------------------------------------------------

WRITE_OLD = '''        scenario = str(job_spec.get(
            "scenario_res",
            "res://addons/laser_tag_tool/resources/default_laser_tag_scenario.tres"))'''

WRITE_NEW = '''        # THE MISSION'S ENCOUNTER, when the brief expressed one.
        #
        # `scenario_res` has been readable here since this adapter was written
        # and nothing ever set it, so every mission Level Factory has evaluated
        # was graded against Laser Tag's stock 1-versus-6 -- a five-building
        # night heist and a single-shell test box against the same resource.
        # Measured on `lot_demo_001`: the crew needs twelve hits, lands six to
        # nine, wipes 25 of 25, and `route_completed` never goes true, which is
        # 25 of the 100 points unreachable by geometry.
        #
        # Written into the STAGED project rather than the checkout: the addon
        # belongs to Laser Tag and Level Factory does not edit other tools'
        # repositories. The stock resource stays the fallback, so a job spec
        # carrying no scenario behaves exactly as it did.
        scenario = str(job_spec.get(
            "scenario_res",
            "res://addons/laser_tag_tool/resources/default_laser_tag_scenario.tres"))
        wanted = job_spec.get("scenario")
        if isinstance(wanted, Mapping) and wanted and project:
            written = _write_scenario(Path(str(project)), wanted)
            if written is not None:
                scenario = written'''


HELPER_OLD = '''class LaserTagAdapter(BaseAdapter):'''

HELPER_NEW = '''#: Everything `LT_TestScenario` carries, with the stock resource's values.
#: Copied verbatim and in one place so drift between this table and
#: `default_laser_tag_scenario.tres` is a diff rather than an excavation --
#: the same reason `site_spawns` carries `OPENING_RANGE` and names where it
#: came from. Only the keys a brief names are overridden; the rest are written
#: out unchanged so the generated resource is complete and readable.
_STOCK_SCENARIO: dict = {
    "run_count": 25,
    "max_run_time_seconds": 180.0,
    "player_health": 5,
    "enemy_health": 2,
    "player_count": 1,
    "enemy_count": 6,
    "enemies_enabled": True,
    "player_laser_range": 60.0,
    "enemy_laser_range": 35.0,
    "enemy_fire_cooldown": 1.25,
    "enemy_reaction_delay_min": 0.25,
    "enemy_reaction_delay_max": 0.5,
    "enemy_sight_range": 35.0,
    "enemy_preferred_distance": 14.0,
    "first_contact_min_seconds": 3.0,
    "first_contact_max_seconds": 30.0,
    "min_reasonable_survival_seconds": 10.0,
    "use_random_spawn_permutations": True,
    "use_bot_players": True,
    "enable_debug_lasers": True,
    "record_debug_events": True,
    "enable_map_sampling": True,
    "sample_spacing": 2.0,
    "overexposed_threshold": 3,
    "fail_on_missing_player_spawn": True,
    "fail_on_missing_enemy_spawns": True,
    "fail_on_unreachable_spawns": True,
    "require_navigation": False,
}

#: Where the generated resource lands inside the staged project, and the
#: res:// path `--scenario` is given.
_SCENARIO_NAME = "mission_scenario.tres"

#: The script the resource is an instance of. It lives in Laser Tag's addon,
#: which staging has already copied into the project, so the generated
#: resource resolves against the same checkout the runner does.
_SCENARIO_SCRIPT = "res://addons/laser_tag_tool/resources/LT_TestScenario.gd"


def _tres_value(value) -> str:
    """A Godot resource literal. `bool` before `int` -- bool IS an int."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return repr(float(value))
    if isinstance(value, int):
        return str(value)
    return f'"{value}"'


def _write_scenario(project: Path, overrides: Mapping) -> str | None:
    """Write the mission's scenario into the staged project; res:// path back.

    Returns ``None`` rather than raising when the addon is not staged: without
    `LT_TestScenario.gd` at the path the resource names, Godot would load a
    resource with no script and the runner would read defaults off a bare
    `Resource` -- which is a silently different evaluation, and the stock
    resource is a better answer than that.
    """
    script = project / "addons" / "laser_tag_tool" / "resources" / \\
        "LT_TestScenario.gd"
    if not script.is_file():
        return None
    values = dict(_STOCK_SCENARIO)
    for key, value in overrides.items():
        if key in values:
            values[key] = value
    lines = [
        '[gd_resource type="Resource" script_class="LT_TestScenario" '
        'load_steps=2 format=3]',
        "",
        f'[ext_resource type="Script" path="{_SCENARIO_SCRIPT}" '
        'id="1_scenario"]',
        "",
        "[resource]",
        'script = ExtResource("1_scenario")',
    ]
    lines += [f"{k} = {_tres_value(v)}" for k, v in values.items()]
    (project / _SCENARIO_NAME).write_text("\\n".join(lines) + "\\n",
                                          encoding="utf-8")
    return f"res://{_SCENARIO_NAME}"


class LaserTagAdapter(BaseAdapter):'''


EDITS = {
    MODELS: ((BRIEF_OLD, BRIEF_NEW),),
    CMDS: ((SPEC_OLD, SPEC_NEW),),
    ADAPTER: ((HELPER_OLD, HELPER_NEW), (WRITE_OLD, WRITE_NEW)),
}

_CRLF = "\r\n"


def _find(body: str, anchor: str):
    for candidate in (anchor, anchor.replace("\n", _CRLF)):
        count = body.count(candidate)
        if count:
            return candidate, count
    return anchor, 0


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(path: Path, edits, *, check: bool) -> int:
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR)

    done = sum(1 for _o, new in edits if _find(body, new)[1] == 1)
    if done == len(edits):
        print(f"  already applied  {path.name}")
        return 0
    if done:
        print(f"REFUSING: {path.name} has {done} of {len(edits)} edits already "
              f"present.")
        return 1

    out = body
    for old, new in edits:
        anchor, count = _find(out, old)
        if count != 1:
            print(f"REFUSING: {path.name} -- expected 1 occurrence of an "
                  f"anchor, found {count}.")
            print(f"  anchor starts: {old.splitlines()[0].strip()!r}")
            return 1
        out = out.replace(
            anchor, new.replace("\n", _CRLF) if _CRLF in anchor else new, 1)

    data = out.encode("utf-8")
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        return 0
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def _explain() -> int:
    sys.path.insert(0, str(Path.cwd() / "level_factory"))
    try:
        from packages.core.models import MissionBrief
    except ImportError as exc:
        print(f"  cannot import MissionBrief: {exc}")
        return 1
    fields = ("crew_size", "crew_health", "enemy_count", "enemy_health")
    have = [f for f in fields if hasattr(MissionBrief, f)]
    if len(have) != len(fields):
        print("  unpatched: the brief cannot express an encounter. Every")
        print("  mission is graded against Laser Tag's stock resource:")
        print("    player_count 1, player_health 5, enemy_count 6, "
              "enemy_health 2")
        print("  The crew needs 12 hits, lands 6-9, and wipes 25 of 25.")
        return 0
    b = MissionBrief(mission_id="x", display_name="x")
    print("  brief defaults (identical to the stock resource):")
    for f in fields:
        print(f"    {f:<14} {getattr(b, f)}")
    print()
    from adapters.laser_tag import _STOCK_SCENARIO, _tres_value
    print(f"  {len(_STOCK_SCENARIO)} scenario fields carried; a brief names 4")
    print("  literals:", ", ".join(
        f"{_tres_value(v)}" for v in (True, False, 4, 2.0)))
    return 0


def main(argv: list[str]) -> int:
    if "--explain" in argv:
        return _explain()

    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root (the directory holding "
                             f"level_factory/)")

    if "--revert" in argv:
        bad = 0
        for rel in EDITS:
            path = root / rel
            side = path.with_suffix(path.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {path.name}")
                bad = 1
                continue
            path.write_bytes(side.read_bytes())
            print(f"  reverted     {path.name}")
        return bad

    check = "--check" in argv
    for rel, edits in EDITS.items():
        code = _apply(root / rel, edits, check=check)
        if code:
            return code
    if not check:
        print()
        print("  Nothing changes until a brief says so -- the defaults ARE the")
        print("  stock numbers. To give lot_demo_001 a crew, add to its")
        print("  brief.json:")
        print('      "crew_size": 4,')
        print("  and leave enemy_count alone (see the docstring). Then:")
        print("      python $LF -C lot-demo-ws run lot_demo_001 --art")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
