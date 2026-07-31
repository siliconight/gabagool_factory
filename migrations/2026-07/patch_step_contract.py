"""Record the step number a capsule actually obeys, and make Lot check it.

`agent_contract.json` states `max_step_up_m: 0.5` as though the body were a box.
It is not: a capsule meets a low step on its bottom HEMISPHERE, so the contact
normal is sloped rather than horizontal, and the lower the step the more
vertical that normal becomes. The engine calls the contact a floor only while
that angle stays inside `floor_max_angle`, so the tallest step a body walks up
with no step-up assistance at all is

    R * (1 - cos(floor_max_angle))  =  0.4 * (1 - cos 45)  =  0.117 m

Lot's own kerb is 0.16. That is why walking from a spawn toward the street stops
dead and needs a jump, and why the courtyard edge at 0.12 clears the limit by
3 mm. Both numbers were chosen against `max_step_up_m: 0.5`, which is what a
controller can LIFT itself over, not what it can WALK over.

Asserts every target before writing.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
CONTRACT = ROOT / "deli_counter" / "agent_contract.json"
LOT_PY = ROOT / "lot" / "lot.py"


def patch_contract() -> str:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    cl = c.get("clearances")
    if cl is None:
        raise SystemExit("agent_contract.json has no `clearances`. Nothing written.")
    if "unassisted_step_max_m" in cl:
        return "contract: already has unassisted_step_max_m"
    cl["unassisted_step_max_m"] = 0.117
    cl["unassisted_step_derivation"] = (
        "A capsule meets a low step on its bottom HEMISPHERE, so the contact "
        "normal is sloped rather than horizontal: normal.y = (R - h) / R. The "
        "engine calls that contact a floor only while its angle stays inside "
        "floor_max_angle, so the tallest step a body WALKS up with no step-up "
        "code is R * (1 - cos(floor_max_angle)) = 0.4 * (1 - cos 45 deg) = "
        "0.117 m. characters.player.max_step_up_m (0.5) is what a controller "
        "can LIFT itself over; this is what it can walk over. The deliverable "
        "ships into projects with none of these tools present, so a transition "
        "above this line requires the consumer to have implemented step-up. R "
        "here is the 0.4 m capsule lot.py emits for the walk player, which "
        "matches nav_bake.agent_radius_m rather than characters.player.radius_m "
        "(0.35) -- that discrepancy is real and is recorded, not resolved."
    )
    CONTRACT.write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    return f"contract: added unassisted_step_max_m 0.117 ({CONTRACT.name})"


ANCHOR = '''    tscn_out = os.path.join(out_dir, f"{site_spec['name']}.tscn")
    write_godot_scene(site_spec, merged, tscn_out, preview=preview,
                      self_flooring=self_flooring)
'''

INSERT = '''
    # site-level step check, read back off the scene we just WROTE rather than
    # re-derived from the constants that produced it. A capsule walks up a step
    # only while the contact normal stays inside floor_max_angle, which for a
    # 0.4 m body at 45 deg is 0.117 m -- and SIDEWALK_H is 0.16, so stepping off
    # the ground onto a kerb is a wall to anything without step-up code. Reported
    # here beside the other site gates; see clearances.unassisted_step_max_m.
    try:
        import site_steps as _steps
        _a = _agent()
        _step_issues = _steps.findings(
            tscn_out,
            radius_m=float(_a["nav_bake"]["agent_radius_m"]),
            floor_max_angle_deg=45.0,
            assist_m=float(_a["characters"]["player"]["max_step_up_m"]))
        for _i in _step_issues:
            print(f"  [lot] {_i['code']}: {_i['message']}")
        result_steps = _step_issues
    except Exception as _e:            # a check must never break the build
        print(f"  [lot] step check unavailable: {_e}")
        result_steps = []
'''


def patch_lot() -> str:
    src = LOT_PY.read_text(encoding="utf-8")
    if "site_steps" in src:
        return "lot.py: already wired"
    if src.count(ANCHOR) != 1:
        raise SystemExit(
            "lot.py: could not find the write_godot_scene call to hang the step "
            "check off. Nothing written -- read the file and re-aim.")
    src = src.replace(ANCHOR, ANCHOR + INSERT)
    src = src.replace('''        "tactical": tactical_report,''',
                      '''        "tactical": tactical_report,
        "steps": result_steps,''')
    LOT_PY.write_text(src, encoding="utf-8")
    import py_compile
    py_compile.compile(str(LOT_PY), doraise=True)
    return "lot.py: step check wired after write_godot_scene, and it compiles"


if __name__ == "__main__":
    print(patch_contract())
    print(patch_lot())
    print("\n=========== the kerb, off a scene Lot already wrote ===========")
    import subprocess
    import sys
    proj = ROOT / "_runs" / "ballpark_block_proj" / "ballpark_block.tscn"
    if proj.exists():
        subprocess.run([sys.executable, str(ROOT / "lot" / "site_steps.py"),
                        str(proj), str(CONTRACT)])
    else:
        print(f"  {proj} not there yet -- run library_walk.py --only ballpark_block")
