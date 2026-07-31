"""Make the waypoint radius derive from the body instead of sitting at 0.15.

The library went 20/20 with DC_QA_WP=0.07 in the shell. The committed default is
0.15, so without that variable the corner-clipping defect returns and the green
sweep is not reproducible. A result that depends on an environment variable
nobody wrote down is not a result.

WHERE 0.07 COMES FROM. The funnel offsets a corner waypoint by the radius the
map was BAKED for; the body only needs its own. The clearance is the difference:

    margin = (bake agent radius) - (walker radius)

The walker is AGENT_RADIUS * 0.7, so margin = 0.3 * AGENT_RADIUS -- 0.12 for the
0.4 agent. Take 60% of it and the consume radius is 0.18 * AGENT_RADIUS = 0.072,
which is the 0.07 that produced the clean sweep.

Both measured points agree with that formula:

    cell_size 0.15 -> radius ceiled to 0.45, margin 0.17, 0.15 worked
    cell_size 0.10 -> radius exactly 0.40, margin 0.12, 0.15 FAILED and 0.07 worked

The formula uses the un-ceiled radius, so it is the conservative reading of the
margin at any cell size -- ceiling only ever makes the real margin larger. That
matters because cell_size lives in agent_contract.json and the director has no
way to see it.

Also raises DC_NAV_RADIUS's role: change the body and this follows, instead of
becoming a second number to remember.

Asserts its target before writing, and is idempotent.
"""
import pathlib
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
DIR_GD = ROOT / "lot" / "godot" / "addons" / "heist_nav_qa" / "nav_qa_director.gd"

OLD = 'var WP_RADIUS := _envf("DC_QA_WP", 0.15)\n'

NEW = '''#: Derived, not chosen. The funnel offsets a corner waypoint by the radius the
#: map was BAKED for and the body only needs its own, so the clearance a corner
#: gives us is (bake radius) - (walker radius). This walker is AGENT_RADIUS *
#: 0.7, making the margin 0.3 * AGENT_RADIUS, and 60% of that leaves room for
#: the step the body takes between frames. Two measured points agree: at
#: cell_size 0.15 the bake radius ceiled to 0.45 (margin 0.17) and 0.15 worked;
#: at cell_size 0.10 it is 0.40 exactly (margin 0.12) and 0.15 CLIPPED while
#: 0.07 cleared. Uses the un-ceiled radius because the director cannot see
#: cell_size, and ceiling only ever widens the real margin -- so this is the
#: conservative reading at any grid size.
var WP_RADIUS := _envf("DC_QA_WP", AGENT_RADIUS * 0.18)
'''


def main() -> int:
    src = DIR_GD.read_text(encoding="utf-8")
    if "AGENT_RADIUS * 0.18" in src:
        print("nav_qa_director.gd: WP_RADIUS already derived")
        return 0
    if src.count(OLD) != 1:
        raise SystemExit(
            f"nav_qa_director.gd: the WP_RADIUS line appears {src.count(OLD)} "
            f"time(s), expected exactly 1. Run patch_walker_waypoint.py first, "
            f"or read the file. Nothing written.")

    backup = DIR_GD.with_suffix(".gd.pre_wpdefault")
    if not backup.exists():
        shutil.copy2(DIR_GD, backup)
    DIR_GD.write_text(src.replace(OLD, NEW), encoding="utf-8")

    print("nav_qa_director.gd: WP_RADIUS = AGENT_RADIUS * 0.18")
    print(f"  previous file kept at {backup.name}")
    print("\n  for the 0.4 agent that is 0.072, which is what the 20/20 sweep ran at.")
    print("  DC_QA_WP still overrides it.\n")
    for r in (0.28, 0.35, 0.4, 0.5):
        print(f"    AGENT_RADIUS {r:.2f}  ->  margin {0.3 * r:.3f}   "
              f"WP_RADIUS {0.18 * r:.3f}")
    print("\n  confirm nothing moved, WITHOUT the env var set:")
    print("    Remove-Item Env:\\DC_QA_WP -ErrorAction SilentlyContinue")
    print("    python library_walk.py --only warehouse_district --timeout 1800")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
