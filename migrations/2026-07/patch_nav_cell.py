"""Let the bake tell a steep ramp from a tall step.

MEASURED. After agent_max_climb_m dropped 0.5 -> 0.15, eight path proofs across
two sites failed, and every one of them is a STOREY CHANGE:

    central_vault        0.3 -> 4.5     4.5 -> -3.9    -3.9 -> 0.3
    warehouse_district   0.4 -> -4.0    0.3 -> 5.2     0.3 -> -4.7
                        -4.0 -> 0.3     0.3 -> 5.2

All eight report "off the main network ... disjoint islands", with
anchors_without_standing_room and anchors_behind_a_barrier both empty and zero
stuck walkers. The navmesh split into one island per storey: the stairs stopped
connecting.

WHY, and it is arithmetic that should have been done before choosing 0.15.
Recast joins two adjacent voxel columns only if their height difference is
within walkableClimb. On a ramp that difference is

    cell_size * tan(pitch)

so the steepest ramp that stays connected is atan(max_climb / cell_size). At
cell_size 0.15 and max_climb 0.15 that is exactly 45 degrees.

    storey 3.2 over a 4.0 run  ->  38.7 deg,  per-column 0.120  connects
    storey 4.2 over a 4.0 run  ->  46.4 deg,  per-column 0.158  SEVERED
    storey 5.0 over a 4.0 run  ->  51.3 deg,  per-column 0.188  SEVERED

walkup_siege has 3.2 m storeys, which is why it passed the same sweep these
failed. And nav_bake.agent_max_slope_deg is 55, so these stairs are legal by the
contract's own slope limit and were severed by its climb limit.

THE POINT. agent_max_climb is doing two unrelated jobs. It permits genuine STEPS
-- which is what we wanted to restrict, because a body walks up 0.117 and the
bake was routing over 0.5 -- and it also permits the voxel staircase that any
continuous SLOPE becomes once it is discretised. Lowering it to stop fictional
steps also severs legitimate ramps, and no single value of it can do both jobs
while cell_size is this coarse.

So separate them: keep the step ceiling at 0.15 and make the discretisation fine
enough that a legal slope's per-column rise fits under it.

    cell_size 0.150  ->  45.0 deg   severs stairs above this
    cell_size 0.125  ->  50.2 deg   still severs
    cell_size 0.100  ->  56.3 deg   covers the 55 deg contract limit
    cell_size 0.075  ->  63.4 deg   more headroom, 4x the bake

0.10 is the smallest value that clears 55 degrees. It costs 2.25x the horizontal
voxel columns, so bakes get slower -- that is the price of the bake being able to
tell a ramp from a step.

TWO SIDE EFFECTS, both good, both from the contract's own formulas:

  * agent_radius 0.4 stops being ceiled. At cell_size 0.15 it becomes 0.45, which
    is where the corner-clearance margin in nav_qa_director.gd came from. At 0.10
    it is 0.40 exactly.
  * min_door_width by the contract formula drops from 1.20 to 1.00, so the
    ratified 1.25 keeps more margin than before rather than less.

Asserts every target before writing, and is idempotent.
"""
import json
import math
import pathlib

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
CONTRACT = ROOT / "deli_counter" / "agent_contract.json"

NEW_CELL_SIZE_M = 0.10


def main() -> int:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    nav = c.get("nav_bake")
    if nav is None:
        raise SystemExit("agent_contract.json has no `nav_bake`. Nothing written.")
    for key in ("cell_size_m", "cell_height_m", "agent_max_climb_m",
                "agent_max_slope_deg", "agent_radius_m"):
        if key not in nav:
            raise SystemExit(f"nav_bake has no `{key}`. Nothing written.")

    old_cs = float(nav["cell_size_m"])
    climb = float(nav["agent_max_climb_m"])
    slope = float(nav["agent_max_slope_deg"])
    radius = float(nav["agent_radius_m"])

    if climb > 0.3:
        raise SystemExit(
            f"agent_max_climb_m is {climb}, so the bake is not climb-limited yet "
            f"and this change would only make it slower. Run patch_nav_climb.py "
            f"first. Nothing written.")
    if abs(old_cs - NEW_CELL_SIZE_M) < 1e-9:
        print(f"contract: cell_size_m already {NEW_CELL_SIZE_M}")
        return 0

    need = math.degrees(math.atan(climb / NEW_CELL_SIZE_M))
    if need < slope:
        raise SystemExit(
            f"cell_size {NEW_CELL_SIZE_M} only carries slopes to {need:.1f} deg, "
            f"below agent_max_slope_deg {slope}. Pick a smaller cell_size or "
            f"lower the declared slope. Nothing written.")

    nav["cell_size_m"] = NEW_CELL_SIZE_M
    nav["cell_size_derivation"] = (
        f"Was {old_cs}. Recast joins adjacent voxel columns only within "
        f"walkableClimb, and on a ramp that gap is cell_size * tan(pitch). So "
        f"the steepest ramp that stays CONNECTED is "
        f"atan(agent_max_climb_m / cell_size_m) -- {old_cs} with a climb of "
        f"{climb} capped that at "
        f"{math.degrees(math.atan(climb / old_cs)):.1f} deg while "
        f"agent_max_slope_deg says {slope}. Measured 2026-07-29: eight path "
        f"proofs across central_vault and warehouse_district failed as "
        f"'disjoint islands', every one of them a storey change, because those "
        f"buildings have 4.2-5.0 m storeys over a 4.0 m run (46-51 deg) while "
        f"walkup_siege's 3.2 m storeys (38.7 deg) stayed connected and passed "
        f"the same sweep. agent_max_climb serves two jobs -- permitting real "
        f"steps, and permitting the voxel staircase a continuous slope becomes "
        f"-- and no value of it does both while cell_size is coarse. "
        f"{NEW_CELL_SIZE_M} is the largest cell that carries {slope} deg "
        f"({need:.1f} deg), at {(old_cs / NEW_CELL_SIZE_M) ** 2:.2f}x the "
        f"horizontal columns and so a slower bake. Raising climb instead would "
        f"re-permit the 0.16 kerb, which is the defect this is protecting."
    )

    ceil_old = math.ceil(radius / old_cs) * old_cs
    ceil_new = math.ceil(radius / NEW_CELL_SIZE_M) * NEW_CELL_SIZE_M
    door_old = 2 * math.ceil(radius / old_cs) * old_cs + 2 * old_cs
    door_new = (2 * math.ceil(radius / NEW_CELL_SIZE_M) * NEW_CELL_SIZE_M
                + 2 * NEW_CELL_SIZE_M)

    CONTRACT.write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")

    print(f"contract: nav_bake.cell_size_m {old_cs} -> {NEW_CELL_SIZE_M}")
    print(f"contract: connected slope limit "
          f"{math.degrees(math.atan(climb / old_cs)):.1f} -> {need:.1f} deg "
          f"(agent_max_slope_deg is {slope})")

    print("\n=========== what this changes ===========")
    for h, run in ((3.2, 4.0), (4.2, 4.0), (5.0, 4.0)):
        pitch = math.degrees(math.atan(h / run))
        was = "connects" if old_cs * math.tan(math.radians(pitch)) <= climb else "SEVERED"
        now = ("connects" if NEW_CELL_SIZE_M * math.tan(math.radians(pitch)) <= climb
               else "SEVERED")
        mark = "   <- fixed" if was != now else ""
        print(f"  storey {h:.1f} over run {run:.1f}  {pitch:5.1f} deg   "
              f"was {was:<9} now {now}{mark}")
    print(f"\n  agent_radius {radius} ceiled by the voxel grid: "
          f"{ceil_old:.2f} -> {ceil_new:.2f}")
    print(f"  min_door_width by the contract formula: {door_old:.2f} -> "
          f"{door_new:.2f} (ratified value keeps more margin)")
    print(f"  bake cost: about {(old_cs / NEW_CELL_SIZE_M) ** 2:.2f}x the "
          f"horizontal columns -- expect the sweep to take longer")
    m_old, m_new = ceil_old - 0.28, ceil_new - 0.28
    wp = 0.15
    print(f"\n  CAUTION -- this moves the walker's corner margin. It is "
          f"(ceiled bake radius) - (walker radius):")
    print(f"    was {ceil_old:.2f} - 0.28 = {m_old:.2f}   now "
          f"{ceil_new:.2f} - 0.28 = {m_new:.2f}")
    if m_new <= wp:
        print(f"    nav_qa_director.gd's WP_RADIUS is {wp:.2f}, which is NO "
              f"LONGER under that margin.")
        print(f"    Set DC_QA_WP to about {max(0.05, m_new * 0.6):.2f} for the "
              f"re-walk, or the corner-clipping")
        print(f"    defect patch_walker_waypoint.py fixed will come straight "
              f"back. A finer bake")
        print(f"    grid makes the navmesh honest and the funnel's clearance "
              f"tighter at the same time.")
    else:
        print(f"    WP_RADIUS {wp:.2f} still sits under it.")
    print("\n  re-walk the two that failed on this, then the library:")
    print("    python library_walk.py --only central_vault warehouse_district")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
