"""Let _agent() actually return the contract.

MEASURED. The step gate failed on every build with

    [lot] STEP GATE DID NOT RUN (KeyError: 'characters')

because _agent() does not return the agent contract. It returns the sections
that happen to be listed in _AGENT_DEFAULTS:

    merged = {k: dict(v) for k, v in _AGENT_DEFAULTS.items()}
    ...
    for sec in merged:                      # <- the DEFAULTS' keys, not the file's
        merged[sec].update(data.get(sec, {}))

_AGENT_DEFAULTS carries nav_bake and qa. So `characters` and `clearances` are
read off disk and thrown away, and its own docstring calls it "ONE source of
truth for character metrics and derived clearances" while carrying neither.

That also explains something I misjudged. lot.py hardcoded the walk-scene
player as string literals three lines under an agent_radius that reads the
contract properly, and I read that as an oversight. It was not: the accessor
could not reach characters.player at all, so a literal was the only thing
available. The defect was one layer down from where it showed.

TWO FIXES.

1. Merge what the FILE has, not what the defaults happen to list. The contract
   is authoritative and complete; defaults exist to survive a missing file, not
   to whitelist which sections count. A section added to the contract tomorrow
   then reaches callers without editing this function -- which is the whole
   point of having one source of truth.

2. Refresh the stale fallbacks. They say agent_max_climb_m 0.5 and cell_size_m
   0.15; today's ratified values are 0.15 and 0.10. The docstring promises the
   fallbacks equal the ratified values, so with the contract absent lot.py would
   silently bake with the numbers that produced the 0.49 m stair stringer and
   the severed staircases. A fallback that has drifted from the thing it stands
   in for is the recurring defect of this whole pass, one more time.

Asserts every target before writing, and is idempotent.
"""
import json
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
LOT_PY = ROOT / "lot" / "lot.py"
CONTRACT = ROOT / "deli_counter" / "agent_contract.json"

OLD_DEFAULTS = '''_AGENT_DEFAULTS = {"nav_bake": {"agent_radius_m": 0.4, "agent_height_m": 1.8,
                                "agent_max_climb_m": 0.5,
                                "agent_max_slope_deg": 55.0,
                                "cell_size_m": 0.15, "cell_height_m": 0.15},
                   "qa": {"arrive_dist_m": 1.5, "stuck_seconds": 4.0,
                          "snap_max_m": 2.0}}
'''

NEW_DEFAULTS = '''#: What a MISSING contract file falls back to. These must track the ratified
#: values in deli_counter/agent_contract.json -- they had drifted, still saying
#: agent_max_climb_m 0.5 and cell_size_m 0.15 after both were changed, so a
#: build with no contract present would have silently used the numbers that let
#: the bake promise a 0.49 m climb and then severed every stair over 45 deg.
_AGENT_DEFAULTS = {"nav_bake": {"agent_radius_m": 0.4, "agent_height_m": 1.8,
                                "agent_max_climb_m": 0.15,
                                "agent_max_slope_deg": 55.0,
                                "cell_size_m": 0.10, "cell_height_m": 0.15},
                   "characters": {"player": {"radius_m": 0.35,
                                             "height_m": 1.8,
                                             "eye_height_m": 1.6,
                                             "crouch_height_m": 1.2,
                                             "max_step_up_m": 0.5,
                                             "walk_speed_mps": 4.0},
                                  "npc_standard": {"radius_m": 0.35,
                                                   "height_m": 1.8}},
                   "clearances": {"min_door_width_m": 1.25,
                                  "min_corridor_width_m": 1.1,
                                  "min_headroom_m": 2.0,
                                  "unassisted_step_max_m": 0.1025},
                   "qa": {"arrive_dist_m": 1.5, "stuck_seconds": 4.0,
                          "snap_max_m": 2.0}}
'''

OLD_MERGE = '''            for sec in merged:
                merged[sec].update(data.get(sec, {}))
'''

NEW_MERGE = '''            # Merge what the FILE has, not what the defaults happen to
            # list. This iterated over `merged` -- the defaults' keys -- so any
            # contract section absent from _AGENT_DEFAULTS was read off disk and
            # discarded. `characters` and `clearances` were both dropped, which
            # is why the step gate died on KeyError: 'characters' and why the
            # walk-scene player had to be a literal. The contract is
            # authoritative; defaults only survive a missing file.
            for sec, val in data.items():
                if isinstance(val, dict) and isinstance(merged.get(sec), dict):
                    merged[sec].update(val)
                else:
                    merged[sec] = val
'''


def main() -> int:
    src = LOT_PY.read_text(encoding="utf-8")
    done = []

    if '"characters"' in src.split("def _agent")[0]:
        done.append("lot.py: _AGENT_DEFAULTS already carries characters")
    else:
        if src.count(OLD_DEFAULTS) != 1:
            raise SystemExit(f"lot.py: _AGENT_DEFAULTS appears "
                             f"{src.count(OLD_DEFAULTS)} time(s), expected 1. "
                             f"Nothing written.")
        src = src.replace(OLD_DEFAULTS, NEW_DEFAULTS)
        done.append("lot.py: _AGENT_DEFAULTS + characters, clearances; "
                    "stale nav_bake fallbacks refreshed")

    if "for sec, val in data.items():" in src:
        done.append("lot.py: _agent() already merges every contract section")
    else:
        if src.count(OLD_MERGE) != 1:
            raise SystemExit(f"lot.py: the merge loop appears "
                             f"{src.count(OLD_MERGE)} time(s), expected 1. "
                             f"Nothing written.")
        src = src.replace(OLD_MERGE, NEW_MERGE)
        done.append("lot.py: _agent() merges every section the contract has")

    backup = LOT_PY.with_suffix(".py.pre_accessor")
    if not backup.exists():
        shutil.copy2(LOT_PY, backup)
    LOT_PY.write_text(src, encoding="utf-8")
    py_compile.compile(str(LOT_PY), doraise=True)
    for line in done:
        print(line)
    print(f"lot.py: compiles; previous file kept at {backup.name}")

    # prove the accessor now reaches what the gate needs, without Godot
    import subprocess
    import sys
    probe = (
        "import sys, json; sys.path.insert(0, r'%s'); import lot; "
        "a = lot._agent(); "
        "print('  sections reachable:', ', '.join(sorted(a))); "
        "print('  player radius:', a['characters']['player']['radius_m']); "
        "print('  player height:', a['characters']['player']['height_m']); "
        "print('  step limit:', a['clearances']['unassisted_step_max_m']); "
        "print('  bake climb:', a['nav_bake']['agent_max_climb_m'], "
        "' cell:', a['nav_bake']['cell_size_m'])"
    ) % str(LOT_PY.parent)
    print("\n=========== what _agent() returns now ===========")
    r = subprocess.run([sys.executable, "-c", probe], capture_output=True,
                       text=True, cwd=str(LOT_PY.parent))
    print((r.stdout or "").rstrip() or (r.stderr or "").rstrip()[-500:])

    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    print(f"\n  contract on disk says player radius "
          f"{c['characters']['player']['radius_m']}, step limit "
          f"{c['clearances']['unassisted_step_max_m']}")
    print("\n  rebuild; the gate should now report instead of dying:")
    print("    python library_walk.py --only ballpark_block --timeout 1800")
    print("  expect LOT_STEP_NEEDS_ASSIST on two kerb sections and one "
          "courtyard edge.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
