"""Wire the step gate for real, and stop hardcoding the player.

THREE FIXES, all verified against the current files rather than remembered.

1. THE GATE WAS NEVER WIRED. patch_step_contract.py guarded itself with

       if "site_steps" in src: return "lot.py: already wired"

   and patch_kerb_cuts.py had already put the words "site_steps.py" into a
   COMMENT in lot.py. So the guard matched, the wiring was skipped, and the
   script reported success. The `[LOT_STEP_NEEDS_ASSIST]` output that looked
   like proof came from patch_step_contract.py's own verification step, which
   runs site_steps.py standalone against the built .tscn -- a one-off report,
   not the build. A substring test standing in for "is this code connected",
   which is the same defect shape as everything else in this pass, written into
   the guard meant to prevent a bad patch. This one keys on the actual call.

2. THE CONTRACT RECORDED THE WRONG RADIUS. clearances.unassisted_step_max_m was
   written as 0.117, derived from nav_bake.agent_radius_m (0.4). But the bake
   radius is not a body -- the contract's own note says it is "fattest
   navigating character + 0.05 safety", so it is deliberately larger than
   anything that walks. The step a body can walk up is a property OF THE BODY:
   characters.player.radius_m, 0.35, giving 0.1025. site_steps.py already reads
   the player radius, which is why the build gate said 0.103 while the contract
   said 0.117 -- two numbers for one quantity, live at the same time.

3. lot.py HARDCODES THE WALK-SCENE PLAYER. Three lines under agent_radius and
   agent_height, both read properly from _agent():

       '[sub_resource type="CapsuleShape3D" id="PlayerCol"]',
       'radius = 0.4',
       'height = 1.8', '',

   String literals. This is the capsule that ships in the preview scene, and it
   is 0.4 against a contract player of 0.35 -- so the thing a human walks is
   wider than the thing every clearance was derived for. Of the three
   player-shaped capsules in this toolchain, this is the one genuinely
   disconnected from the contract, and it is the one a person feels.

WHAT IS NOT CHANGED, and why -- correcting an earlier claim. The QA walker is
AGENT_RADIUS * 0.7, and I called that a substitution defect for proving routes
with a narrower body than ships. That was wrong in the way that matters: the
navmesh is ERODED by agent_radius, so every path on it already guarantees that
much clearance -- a narrower walker cannot hide a corridor that is too tight,
because the navmesh never went there. What the 0.7 buys is room for the walker
not to clip corners while it tests what erosion cannot model: steps, slopes,
props, steering. Widening it to the bake radius would drive the corner margin to
zero and bring back the defect patch_walker_waypoint.py just fixed. It stays,
and it gets a derivation instead of a removal.

The stock 0.5 capsule is also NOT adopted here. It wants doors at 1.40 and
corridors at 1.30 by the contract's own formulas, against 1.25 and 1.10 today,
so it is a change that will fail sites on openings drawn for a 0.35 body. That
is a measurement to run deliberately, not a rider on this patch.

Asserts every target before writing, and is idempotent on the real call.
"""
import json
import math
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
LOT_PY = ROOT / "lot" / "lot.py"
CONTRACT = ROOT / "deli_counter" / "agent_contract.json"

# --- 1. the gate ------------------------------------------------------------

GATE_ANCHOR = '''    tscn_out = os.path.join(out_dir, f"{site_spec['name']}.tscn")
    write_godot_scene(site_spec, merged, tscn_out, preview=preview,
                      self_flooring=self_flooring)
'''

GATE_INSERT = '''
    # Site-level step gate, read back off the scene just WRITTEN rather than
    # re-derived from the constants that produced it. A capsule walks up a step
    # only while the contact normal stays inside floor_max_angle, which for the
    # contract player is clearances.unassisted_step_max_m -- and SIDEWALK_H is
    # 0.16, so a kerb away from a crossing is a wall to anything without
    # step-up code. Two codes: BLOCKS_A_ROUTE is major and fires when a designed
    # route crosses the rise; NEEDS_ASSIST is minor and fires off-route, which
    # is what a kerb correctly is. Never allowed to break a build -- but note
    # that a check which cannot fail is also a check that can go silent, so the
    # unavailable branch says so loudly.
    result_steps = []
    try:
        import site_steps as _steps
        _a = _agent()
        result_steps = _steps.findings(
            tscn_out,
            radius_m=float(_a["characters"]["player"]["radius_m"]),
            floor_max_angle_deg=45.0,
            assist_m=float(_a["characters"]["player"]["max_step_up_m"]),
            site_spec=site_spec)
        for _i in result_steps:
            print(f"  [lot] {_i['code']}: {_i['message']}")
    except Exception as _e:
        print(f"  [lot] STEP GATE DID NOT RUN ({type(_e).__name__}: {_e}) -- "
              f"a silent check is not a passing one")
'''

RESULT_ANCHOR = '''        "tactical": tactical_report,'''
RESULT_NEW = '''        "tactical": tactical_report,
        "steps": result_steps,'''

# --- 3. the player ----------------------------------------------------------

PLAYER_OLD = """        '[sub_resource type="CapsuleShape3D" id="PlayerCol"]',
        'radius = 0.4',
        'height = 1.8', '',
"""

PLAYER_NEW = """        # The body a human walks in the preview scene. These two were fixed
        # string literals -- 0.4 radius and 1.8 height -- sitting three lines
        # under an agent_radius and agent_height that both read the contract.
        # So the shipped capsule was wider than the contract player every
        # clearance had been derived for. Deliberately not quoting the old
        # values in a way a search could match: a comment mentioning
        # `site_steps.py` is what made this patch's own idempotency guard
        # report success while skipping the wiring. Godot's `height` is the
        # FULL height including both hemispheres.
        '[sub_resource type="CapsuleShape3D" id="PlayerCol"]',
        f'radius = {_agent()["characters"]["player"]["radius_m"]}',
        f'height = {_agent()["characters"]["player"]["height_m"]}', '',
"""


def patch_contract() -> str:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    player = c["characters"]["player"]
    clear = c["clearances"]
    r = float(player["radius_m"])
    want = round(r * (1.0 - math.cos(math.radians(45.0))), 4)
    have = clear.get("unassisted_step_max_m")
    if have is not None and abs(float(have) - want) < 1e-9:
        return f"contract: unassisted_step_max_m already {want} (player {r})"
    clear["unassisted_step_max_m"] = want
    clear["unassisted_step_derivation"] = (
        f"A capsule meets a low step on its bottom HEMISPHERE, so the contact "
        f"normal is sloped rather than horizontal: normal.y = (R - h) / R. The "
        f"engine calls that contact a floor only while its angle stays inside "
        f"floor_max_angle, so the tallest step a body WALKS up with no step-up "
        f"code is R * (1 - cos(floor_max_angle)) = {r} * (1 - cos 45 deg) = "
        f"{want}. R is characters.player.radius_m -- the BODY. It is not "
        f"nav_bake.agent_radius_m, which this field previously used: that one "
        f"is deliberately larger than any body ('fattest navigating character "
        f"+ 0.05 safety', see nav_bake.note) and using it recorded 0.117 while "
        f"the gate enforcing it reported 0.103, two numbers for one quantity. "
        f"characters.player.max_step_up_m ({player['max_step_up_m']}) is what "
        f"a controller can LIFT itself over; this is what it can walk over "
        f"with none. The deliverable ships into projects with none of this "
        f"toolchain present, so a transition above this line requires the "
        f"consumer to have implemented step-up themselves."
    )
    CONTRACT.write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    return (f"contract: unassisted_step_max_m {have} -> {want} "
            f"(from the PLAYER radius {r}, not the bake radius)")


def patch_lot() -> list:
    src = LOT_PY.read_text(encoding="utf-8")
    out = []
    backup = LOT_PY.with_suffix(".py.pre_gate")
    if not backup.exists():
        shutil.copy2(LOT_PY, backup)

    # the gate -- keyed on the CALL, not on the words appearing anywhere
    if "_steps.findings(" in src:
        out.append("lot.py: step gate already wired")
    else:
        if src.count(GATE_ANCHOR) != 1:
            raise SystemExit(f"lot.py: the write_godot_scene anchor appears "
                             f"{src.count(GATE_ANCHOR)} time(s), expected 1. "
                             f"Nothing written.")
        if src.count(RESULT_ANCHOR) != 1:
            raise SystemExit(f"lot.py: the result dict anchor appears "
                             f"{src.count(RESULT_ANCHOR)} time(s), expected 1. "
                             f"Nothing written.")
        src = src.replace(GATE_ANCHOR, GATE_ANCHOR + GATE_INSERT)
        src = src.replace(RESULT_ANCHOR, RESULT_NEW)
        out.append("lot.py: step gate wired into assemble(), reported in result")

    # the player capsule
    if "id=\"PlayerCol\"" in src and "'radius = 0.4'" not in src:
        out.append("lot.py: PlayerCol already reads the contract")
    else:
        if src.count(PLAYER_OLD) != 1:
            raise SystemExit(f"lot.py: the hardcoded PlayerCol block appears "
                             f"{src.count(PLAYER_OLD)} time(s), expected 1. "
                             f"Nothing written.")
        src = src.replace(PLAYER_OLD, PLAYER_NEW)
        out.append("lot.py: PlayerCol reads characters.player radius + height")

    LOT_PY.write_text(src, encoding="utf-8")
    py_compile.compile(str(LOT_PY), doraise=True)
    out.append(f"lot.py: compiles; previous file kept at {backup.name}")
    return out


if __name__ == "__main__":
    print(patch_contract())
    for line in patch_lot():
        print(line)
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    r = float(c["characters"]["player"]["radius_m"])
    lim = float(c["clearances"]["unassisted_step_max_m"])
    print(f"\n  the player is now one number: {r} radius, "
          f"{c['characters']['player']['height_m']} height, everywhere.")
    print(f"  it walks up {lim:.4f} m.\n")
    for name, h in (("road", 0.08), ("path", 0.10), ("kerbcut", 0.08),
                    ("courtyard", 0.12), ("sidewalk / kerb", 0.16)):
        print(f"    {name:<18} {h:.2f}   "
              + ("walks" if h <= lim else "WALL without step-up"))
    print("\n  rebuild one site and confirm the gate actually speaks now:")
    print("    python library_walk.py --only ballpark_block --timeout 1800")
    print("  a build with no [lot] LOT_STEP_ line AND no 'STEP GATE DID NOT "
          "RUN' line\n  means it ran and found nothing.")
