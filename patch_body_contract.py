"""One body, chosen on purpose, and every clearance re-derived from it.

Written against the real agent_contract.json rather than a remembered one, and
that changed the patch. The contract does not merely list numbers -- it carries
its own derivation formulas, and they bind:

    min_door_width  >= 2*ceil(agent_radius/cell_size)*cell_size + 2*cell_size
    min_corridor     = 2*agent_radius + 0.3

At radius 0.4 those give 1.2 (ratified 1.25) and 1.1. At radius 0.5 they give
1.5 and 1.3. So adopting the standard capsule is not a one-field change: every
door in the library has to be 1.5 m, up from 1.25. Sites will fail. They were
always going to fail -- they were drawn for a body nobody had chosen.

WHY A NEW BODY AT ALL. Three player-shaped capsules were in use and no two
agreed. The contract says the QA walker is 0.35; nav_qa_director.gd computes
AGENT_RADIUS * 0.7 = 0.28 and uses that; lot.py emits the walk-scene player at
0.4. The walktest is the gate that certifies a level walkable, and it has been
proving routes with the narrowest of the three. That is this codebase's
recurring defect -- a cheap observable standing in for the expensive truth, with
nothing recording the substitution -- sitting inside the instrument built to
catch it. The contract's own description says it is "THE single source of truth"
and the walker does not read it.

THE OTHER GAP, measured today on walkup_siege. nav_bake.agent_max_climb_m is
0.5: the navmesh will happily route a body up a half-metre riser. What a capsule
actually walks up unassisted is R * (1 - cos(floor_max_angle)) = 0.146. The
floor at the stuck point rises 0.492 m in 0.018 m of travel -- inside what the
navmesh allows, 3.4x outside what the body can do. Every riser between those two
numbers is nav-passable and body-impassable, and nothing in the toolchain knew
that band existed. It is the same defect as the kerb (0.16 against 0.117), three
times the size. Both numbers now sit in the contract next to each other so the
band is visible rather than discovered in play.

Asserts every target before writing, and is idempotent. Run from the factory
root.
"""
import json
import math
import pathlib

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
CONTRACT = ROOT / "deli_counter" / "agent_contract.json"

#: Godot's stock CapsuleShape3D and CharacterBody3D defaults, unmodified.
#: `height` is the FULL height including both hemispheres, per the class
#: reference -- not the cylindrical mid-section. Minimum legal height is 2*R.
RADIUS_M = 0.5
HEIGHT_M = 2.0
FLOOR_MAX_ANGLE_DEG = 45.0


def unassisted_step_max_m(radius_m, floor_max_angle_deg):
    """The tallest step this body WALKS up with no step-up code at all.

    A capsule meets a low step on its bottom hemisphere, so the contact normal
    is sloped rather than horizontal: normal.y = (R - h) / R. The engine calls
    that contact a floor only while its angle stays inside floor_max_angle."""
    return radius_m * (1.0 - math.cos(math.radians(floor_max_angle_deg)))


def door_width_m(radius_m, cell_m):
    """The contract's own formula, applied to the new body rather than quoted."""
    return 2.0 * math.ceil(radius_m / cell_m) * cell_m + 2.0 * cell_m


def main() -> int:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if "superseded_2026_07" in c:
        print("contract: already patched")
        return 0

    for key in ("characters", "nav_bake", "clearances", "qa"):
        if key not in c:
            raise SystemExit(f"agent_contract.json has no `{key}`. Nothing "
                             f"written -- this patch is aimed at the wrong file.")
    player = c["characters"]["player"]
    nav = c["nav_bake"]
    clear = c["clearances"]
    qa = c["qa"]
    cell = float(nav["cell_size_m"])

    if HEIGHT_M < 2.0 * RADIUS_M:
        raise SystemExit(f"a capsule of radius {RADIUS_M} cannot be {HEIGHT_M} "
                         f"tall -- height is the FULL height including both "
                         f"hemispheres, so the floor is {2.0 * RADIUS_M}.")

    step = unassisted_step_max_m(RADIUS_M, FLOOR_MAX_ANGLE_DEG)
    door = door_width_m(RADIUS_M, cell)
    corridor = 2.0 * RADIUS_M + 0.3
    headroom = HEIGHT_M + 0.2          # the old contract's own 1.8 -> 2.0 margin
    scale = HEIGHT_M / float(player["height_m"])

    old = {
        "characters.player.radius_m": player["radius_m"],
        "characters.player.height_m": player["height_m"],
        "characters.player.eye_height_m": player["eye_height_m"],
        "characters.player.crouch_height_m": player["crouch_height_m"],
        "characters.npc_standard.radius_m":
            c["characters"]["npc_standard"]["radius_m"],
        "nav_bake.agent_radius_m": nav["agent_radius_m"],
        "nav_bake.agent_height_m": nav["agent_height_m"],
        "clearances.min_door_width_m": clear["min_door_width_m"],
        "clearances.min_corridor_width_m": clear["min_corridor_width_m"],
        "clearances.min_headroom_m": clear["min_headroom_m"],
        "clearances.derivation": clear["derivation"],
        "qa.walker_capsule_radius_m": qa["walker_capsule_radius_m"],
        "qa.walker_capsule_height_m": qa["walker_capsule_height_m"],
        "nav_qa_director.gd AGENT_RADIUS * 0.7 (code, never in the contract)":
            0.28,
        "lot.py walk-scene PlayerCol radius (code, never in the contract)": 0.4,
    }

    # --- the body ---------------------------------------------------------
    player["radius_m"] = RADIUS_M
    player["height_m"] = HEIGHT_M
    player["eye_height_m"] = round(float(old["characters.player.eye_height_m"])
                                   * scale, 3)
    player["crouch_height_m"] = round(
        float(old["characters.player.crouch_height_m"]) * scale, 3)
    player["capsule_radius_m"] = RADIUS_M
    player["capsule_height_m"] = HEIGHT_M
    player["capsule_height_is_full_height"] = True
    player["centre_to_feet_m"] = round(HEIGHT_M / 2.0, 4)
    player["floor_max_angle_deg"] = FLOOR_MAX_ANGLE_DEG
    player["provisional"] = True
    player["body_provenance"] = (
        "Godot's stock CapsuleShape3D (radius 0.5, height 2.0) and "
        "CharacterBody3D floor_max_angle (45 deg), adopted unmodified so the "
        "body is a decision rather than a residue. PROVISIONAL: when the "
        "gameplay team picks the real player size, change these three numbers "
        "and every clearance below re-derives from them. capsule_height_m is "
        "Godot's `height`, which the class reference defines as the FULL height "
        "INCLUDING both hemispheres -- so this is a 1.0 m cylinder capped by "
        "two 0.5 m hemispheres, the centre sits 1.0 above the feet, and the "
        "minimum legal height at this radius is 1.0. Read it as the "
        "mid-section instead and every feet-to-centre offset in the toolchain "
        "is wrong by half a radius."
    )
    npc = c["characters"]["npc_standard"]
    npc["radius_m"] = RADIUS_M
    npc["height_m"] = HEIGHT_M

    # --- what follows from it --------------------------------------------
    nav["agent_radius_m"] = RADIUS_M
    nav["agent_height_m"] = HEIGHT_M
    clear["min_door_width_m"] = round(door, 3)
    clear["min_corridor_width_m"] = round(corridor, 3)
    clear["min_headroom_m"] = round(headroom, 3)
    clear["unassisted_step_max_m"] = round(step, 4)
    clear["derivation"] = (
        f"min_door_width >= 2*ceil(agent_radius/cell_size)*cell_size + "
        f"2*cell_size -> 2*ceil({RADIUS_M}/{cell})*{cell} + {2 * cell:.1f} = "
        f"{door:.2f}. min_corridor = 2*agent_radius + 0.3 body margin = "
        f"{corridor:.2f}. min_headroom = agent_height + 0.2. These are the "
        f"contract's own formulas applied to the new body, not new numbers: "
        f"widening the agent widens every opening it must fit through."
    )
    clear["unassisted_step_derivation"] = (
        "A capsule meets a low step on its bottom HEMISPHERE, so the contact "
        "normal is sloped rather than horizontal: normal.y = (R - h) / R. The "
        "engine calls that contact a floor only while its angle stays inside "
        "floor_max_angle, so the tallest step a body WALKS up with no step-up "
        "code is R * (1 - cos(floor_max_angle)). characters.player."
        "max_step_up_m is what a controller can LIFT itself over; this is what "
        "it can walk over with none. The deliverable ships into projects with "
        "none of this toolchain present, so any transition above this line "
        "requires the consumer to have implemented step-up themselves."
    )
    clear["nav_climb_vs_body_step"] = (
        f"nav_bake.agent_max_climb_m is {nav['agent_max_climb_m']} and "
        f"clearances.unassisted_step_max_m is {step:.4f}. Anything between "
        f"them is a riser the NAVMESH routes a body over and the BODY cannot "
        f"walk up -- passable on paper, a wall in play. Measured on "
        f"walkup_siege 2026-07-28: the floor rises 0.492 m in 0.018 m of "
        f"travel at the foot of a staircase, inside what the bake allows and "
        f"{0.492 / step:.1f}x outside what the body can do, and the walktest "
        f"walker parks against it with a horizontal contact normal. Lot's kerb "
        f"is the same defect at 0.16. Closing this band means either emitting "
        f"no riser above unassisted_step_max_m, or lowering agent_max_climb so "
        f"the navmesh stops promising routes the body cannot take -- which "
        f"would disconnect any staircase whose leading edge is a riser. That "
        f"is a decision, not a cleanup, and it is not made here."
    )

    qa["walker_capsule_radius_m"] = RADIUS_M
    qa["walker_capsule_height_m"] = HEIGHT_M
    qa["walker_capsule_note"] = (
        "The QA walker IS the player, not a slimmed-down stand-in. This field "
        "said 0.35 while nav_qa_director.gd computed AGENT_RADIUS * 0.7 = 0.28 "
        "and used that, against a walk-scene player lot.py emits at 0.4 -- so "
        "the gate certifying levels walkable was driving the narrowest of three "
        "bodies and reading the contract for none of them. Wire the director to "
        "this field; a contract nothing reads is a comment."
    )

    c["superseded_2026_07"] = {
        "values": old,
        "why": (
            "Three player capsules were in use and none had been chosen. "
            "Replaced by Godot's stock capsule, with the nav bake agent, the QA "
            "walker, and every clearance derived from it rather than set beside "
            "it. Kept because the re-bake at the wider radius will fail sites "
            "that previously passed, and these are the only way to tell a "
            "regression from a defect the new numbers finally exposed."
        ),
    }

    CONTRACT.write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")

    print(f"contract: player {old['characters.player.radius_m']} x "
          f"{old['characters.player.height_m']}  ->  {RADIUS_M} x {HEIGHT_M}")
    print(f"contract: nav_bake agent {old['nav_bake.agent_radius_m']} x "
          f"{old['nav_bake.agent_height_m']}  ->  {RADIUS_M} x {HEIGHT_M}")
    print(f"contract: QA walker {old['qa.walker_capsule_radius_m']} -> "
          f"{RADIUS_M} (the code used 0.28 and read neither)")
    print(f"contract: {len(old)} superseded value(s) recorded")

    print("\n=========== clearances, re-derived not re-guessed ===========")
    for label, was, now in (
            ("min_door_width_m", old["clearances.min_door_width_m"], door),
            ("min_corridor_width_m", old["clearances.min_corridor_width_m"],
             corridor),
            ("min_headroom_m", old["clearances.min_headroom_m"], headroom)):
        print(f"  {label:<22} {was}  ->  {now:.2f}"
              + ("   WIDER: expect sites to fail" if now > float(was) else ""))

    print("\n=========== the band nothing knew about ===========")
    print(f"  a body walks up                       {step:.3f} m")
    print(f"  the navmesh routes it up to           "
          f"{nav['agent_max_climb_m']:.3f} m")
    print(f"  everything between is nav-passable and body-impassable")
    print()
    for name, h in (("road", 0.08), ("path", 0.10), ("courtyard", 0.12),
                    ("sidewalk / kerb", 0.16),
                    ("walkup_siege stair foot", 0.492)):
        if h <= step:
            verdict = "walks"
        elif h <= float(nav["agent_max_climb_m"]):
            verdict = "IN THE BAND -- navmesh says yes, body says no"
        else:
            verdict = "neither: not even the navmesh should route this"
        print(f"  {name:<26} {h:.3f}   {verdict}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
