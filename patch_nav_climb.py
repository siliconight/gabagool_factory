"""Stop the navmesh promising climbs the body cannot make.

MEASURED, on walkup_siege, from the exported geometry rather than inferred:

The four stuck walkers are not at the foot of the staircase. They are walking
into its SIDE. Their route crosses the flight's lateral edge 45% of the way
along, and the ramp's top surface at that point sits 0.491 m above the slab --
against a probe reading of 0.492. The walker is being told to step sideways onto
a half-metre stringer.

It is told that because `agent_max_climb_m` is 0.5. What a capsule actually
walks up is `radius * (1 - cos(floor_max_angle))` = 0.146. Everything between
those numbers is a route the bake promises and the body cannot take, and this
is the third instance found in one investigation:

    stair lateral edge   0.49    walkup_siege, central_vault, ref_pvp
    stair ramp foot      0.26    fixed in geometry (patch_ramp_foot.py)
    Lot kerb             0.16    reported from play: "requiring me to jump"

THE OTHER OPTION, AND WHY NOT. `stairwell.py` already has the lateral-open check
and a `CONTAINMENT_ENFORCED` flag to make it blocking. Flipping it would force a
body-retaining barrier along every flight's sides in every building. Open-sided
stairs are ordinary architecture -- open stringers, feature stairs, half-landings
you can see past -- and walling them all in to satisfy a bake would let the tool
dictate the building. In a real building you cannot step onto a staircase's
stringer; you walk round to its foot. The architecture is right. The bake's claim
is wrong, so the claim is what changes.

WHY 0.15 AND NOT 0.146. Godot floors `agent_max_climb` to whole `cell_height`
voxels and warns that it does so, which is one of the two warnings every bake in
this project prints. At cell_height 0.15, asking for 0.146 quantises to ZERO and
disconnects everything. 0.15 is exactly one voxel: nothing is lost to rounding,
and it sits 4 mm above what the body can walk, which is the closest an honest
number can get without a finer bake.

ORDER MATTERS. This depends on patch_ramp_foot.py having been applied and the
buildings re-exported. With the old 0.26 m riser at the ramp's foot, dropping
max_climb to 0.15 disconnects the staircase entirely -- nav could not get on at
the bottom either. The ramp now lands flush, so the foot stays connected while
the side stops being.

EXPECT SITES TO FAIL. Any route that was only ever passable by a body able to
climb half a metre stops resolving. That is the point: those routes did not work
in play, they worked in the report.

Asserts its target before writing, and is idempotent.
"""
import json
import math
import pathlib

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
CONTRACT = ROOT / "deli_counter" / "agent_contract.json"

NEW_CLIMB_M = 0.15


def main() -> int:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    nav = c.get("nav_bake")
    if nav is None:
        raise SystemExit("agent_contract.json has no `nav_bake`. Nothing written.")
    for key in ("agent_max_climb_m", "cell_height_m", "agent_radius_m"):
        if key not in nav:
            raise SystemExit(f"nav_bake has no `{key}`. Nothing written.")

    old = float(nav["agent_max_climb_m"])
    cell = float(nav["cell_height_m"])
    radius = float(nav["agent_radius_m"])
    walks = radius * (1.0 - math.cos(math.radians(45.0)))

    if abs(old - NEW_CLIMB_M) < 1e-9:
        print(f"contract: agent_max_climb_m already {NEW_CLIMB_M}")
        return 0

    voxels = NEW_CLIMB_M / cell
    if abs(voxels - round(voxels)) > 1e-6:
        raise SystemExit(
            f"{NEW_CLIMB_M} is {voxels:.3f} voxels at cell_height {cell}; Godot "
            f"floors max_climb to whole voxels, so this would silently become "
            f"{math.floor(voxels) * cell:.3f}. Pick a multiple of {cell} or "
            f"lower cell_height. Nothing written.")

    nav["agent_max_climb_m"] = NEW_CLIMB_M
    nav["agent_max_climb_derivation"] = (
        f"Was {old}. The navmesh routes a body over any riser up to this "
        f"height; a capsule only WALKS up radius * (1 - cos(floor_max_angle)) "
        f"= {walks:.3f}. Everything between was a route the bake promised and "
        f"the body could not take. Measured on walkup_siege 2026-07-28: the "
        f"walkers' route crossed a staircase's open lateral edge, a 0.49 m "
        f"stringer, and four of them parked against it with a horizontal "
        f"contact normal. Set to exactly one cell_height voxel ({cell}) "
        f"because Godot FLOORS this to whole voxels and warns that it does -- "
        f"asking for {walks:.3f} at this cell height quantises to zero and "
        f"disconnects the map. Stairs are unaffected: Deli Counter gives them "
        f"a smooth ramp collider rather than per-step boxes, so they connect "
        f"by agent_max_slope, not by climb. The alternative -- enforcing "
        f"lateral containment on every flight -- was rejected because it would "
        f"put a barrier along the sides of every staircase in every building; "
        f"open-sided stairs are ordinary architecture and the bake, not the "
        f"building, is what was making the false claim."
    )
    CONTRACT.write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")

    print(f"contract: nav_bake.agent_max_climb_m {old} -> {NEW_CLIMB_M} "
          f"({round(voxels)} voxel of {cell})")
    print(f"contract: the body walks up {walks:.3f}, so the gap closes from "
          f"{old - walks:.3f} m to {NEW_CLIMB_M - walks:.3f} m")

    print("\n=========== what the navmesh will and will not route over ===========")
    for name, h in (("road", 0.08), ("path", 0.10), ("courtyard", 0.12),
                    ("Lot kerb", 0.16), ("stair ramp foot (was)", 0.26),
                    ("stair lateral edge", 0.49)):
        before = "routed" if h <= old else "not routed"
        after = "routed" if h <= NEW_CLIMB_M else "NOT routed"
        change = "" if before.strip("n ot ") == after.strip("N Ot ") else "   <- changed"
        print(f"  {name:<24}{h:.2f}   was {before:<10} now {after}{change}")
    print("\n  stairs still connect: their collision is a smooth ramp at the "
          "flight's\n  pitch, governed by agent_max_slope "
          f"({nav.get('agent_max_slope_deg')}), not by climb")
    print("\n  REQUIRES patch_ramp_foot.py applied AND buildings re-exported.")
    print("  Without it the ramp's foot is a 0.26 m riser and this "
          "disconnects\n  the staircase from below as well as from the side.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
