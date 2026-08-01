"""Read the step gate back off every scene the sweep just built.

WHY THIS EXISTS RATHER THAN SCROLLING THE SWEEP. library_walk forwards the
gate's `[lot]` lines as each site builds, so confirming a site is clean means
scrolling an hour of output and trusting that the ABSENCE of a line means the
check ran. It has not meant that four times in this pass. This asks each built
scene directly, in seconds, and distinguishes the three answers that matter:
clean, blocked, and NO SCENE TO CHECK.

WHY NOT `python site_steps.py <scene>`. That entry point cannot answer the
question. It never passes site_spec, and `on_route` is empty without one, so
LOT_STEP_BLOCKS_A_ROUTE -- the only major code -- can never fire from the CLI.
It also defaults the radius to qa.walker_capsule_radius_m or 0.4, while the
number that governs what a body walks up is characters.player.radius_m, 0.35.
A CLI that reports 0.117 for a body that walks 0.1025 and cannot emit the major
finding is a check that looks like it ran. Fixing that entry point is a separate
change; this reads the contract and passes the spec.

Exit code is 1 if any site blocks a route or has no scene, so it can gate a
build rather than just inform one.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from factory_paths import factory_root                        # noqa: E402

#: str, not Path -- everything below joins with os.path.join.
ROOT = str(factory_root())
LOT = os.path.join(ROOT, "lot")
RUNS = os.path.join(ROOT, "_runs")
SPECS = os.path.join(LOT, "specs")
CONTRACT = os.path.join(ROOT, "deli_counter", "agent_contract.json")

sys.path.insert(0, LOT)
import site_steps                                            # noqa: E402


def contract():
    with open(CONTRACT, encoding="utf-8") as f:
        return json.load(f)


def find_scene(spec_dir_name, spec):
    """The built scene for a site, or None.

    Lot names the scene from the spec's `name` FIELD, not from the directory the
    spec lives in, and those differ: specs/ref_pvp/ref_pvp_site.json declares
    name "ref_pvp_site" and builds to _runs/ref_pvp_proj/ref_pvp_site.tscn.
    Guessing <dir>.tscn reported that site as having no scene at all. So try the
    declared name, then the directory name, then take whatever single non-navqa
    scene is in the project directory -- the *_navqa.tscn beside it is the QA
    harness wrapper, not the site.
    """
    proj = os.path.join(RUNS, f"{spec_dir_name}_proj")
    if not os.path.isdir(proj):
        return None
    for cand in (spec.get("name"), spec_dir_name):
        if cand:
            p = os.path.join(proj, f"{cand}.tscn")
            if os.path.exists(p):
                return p
    loose = [f for f in sorted(os.listdir(proj))
             if f.endswith(".tscn") and not f.endswith("_navqa.tscn")]
    return os.path.join(proj, loose[0]) if len(loose) == 1 else None


def sites():
    """(name, spec_path, spec, tscn_path or None) for every site with a spec."""
    out = []
    for entry in sorted(os.listdir(SPECS)):
        d = os.path.join(SPECS, entry)
        spec_path = os.path.join(d, f"{entry}_site.json")
        if not os.path.isdir(d) or not os.path.exists(spec_path):
            continue
        with open(spec_path, encoding="utf-8") as f:
            spec = json.load(f)
        out.append((entry, spec_path, spec, find_scene(entry, spec)))
    return out


def main():
    only = sys.argv[1:] or None
    c = contract()
    r = float(c["characters"]["player"]["radius_m"])
    assist = float(c["characters"]["player"]["max_step_up_m"])
    limit = site_steps.unassisted_step_max_m(r, 45.0)
    print(f"player radius {r} m at a 45 deg floor angle -> walks up "
          f"{limit:.4f} m unassisted; a controller lifts itself {assist} m")
    print(f"contract clearances.unassisted_step_max_m = "
          f"{c['clearances'].get('unassisted_step_max_m')}"
          + ("   (agrees)" if abs(float(
              c["clearances"].get("unassisted_step_max_m", -1)) - limit) < 5e-4
             else "   <- DISAGREES with what site_steps enforces"))
    print()
    hdr = f"{'site':<22}{'scene':>7}{'blocks':>8}{'assist':>8}{'jump':>6}  detail"
    print(hdr)
    print("-" * len(hdr))

    bad, missing = [], []
    for name, spec_path, spec, tscn in sites():
        if only and name not in only:
            continue
        if tscn is None:
            print(f"{name:<22}{'NONE':>7}{'-':>8}{'-':>8}{'-':>6}  "
                  f"no built scene under _runs -- nothing was checked")
            missing.append(name)
            continue
        issues = site_steps.findings(tscn, radius_m=r, floor_max_angle_deg=45.0,
                                     assist_m=assist, site_spec=spec)
        by = {i["code"]: i for i in issues}
        blocked = by.get("LOT_STEP_BLOCKS_A_ROUTE")
        assisted = by.get("LOT_STEP_NEEDS_ASSIST")
        tootall = by.get("LOT_STEP_TOO_TALL_TO_WALK")

        def count(i):
            return int(i["message"].split()[0]) if i else 0

        nb, na, nj = count(blocked), count(assisted), count(tootall)
        detail = "clean" if not nb else blocked["message"].split(": ", 1)[1][:96]
        print(f"{name:<22}{'ok':>7}{nb:>8}{na:>8}{nj:>6}  {detail}")
        if nb or nj:
            bad.append((name, nb, nj, blocked or tootall))

    print()
    if missing:
        print(f"{len(missing)} site(s) had NO built scene: "
              f"{', '.join(missing)}")
        print("  A site with no scene is not a passing site. Build it, or drop "
              "the spec.")
    if bad:
        print(f"{len(bad)} site(s) block a route or need a jump:\n")
        for name, nb, nj, issue in bad:
            print(f"  {name}")
            print(f"    {issue['message']}")
            print(f"    fix: {issue['suggested_fix']}")
    elif not missing:
        print("Every built site: no rise on a designed route that a body cannot "
              "walk up.")
        print("The `assist` column is kerbs away from a crossing, which is what "
              "a kerb is for.")
    return 1 if (bad or missing) else 0


if __name__ == "__main__":
    raise SystemExit(main())
