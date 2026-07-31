"""Make site_steps.py's own command line able to report its own worst finding.

`python site_steps.py <scene>` has three defects, and together they make it a
check that cannot fail:

1. IT NEVER PASSES site_spec. `findings()` builds `on_route` only when it has the
   spec, so without one the set is empty and LOT_STEP_BLOCKS_A_ROUTE -- the only
   MAJOR code, the one that means a body following the site's own circulation is
   stopped -- is unreachable. Every standalone run reported at most the minor
   off-route code and read as reassuring.

2. IT MEASURES THE WRONG BODY.

       r = float(((contract.get("qa") or {}).get("walker_capsule_radius_m")) or 0.4)

   The QA walker is deliberately narrower than the player, and the 0.4 fallback is
   the BAKE radius -- larger than any body, per the contract's own note. What a
   capsule walks up is a property of the player: characters.player.radius_m. The
   CLI reported a 0.117 m limit for a body that walks 0.1025, while the build gate
   two files away reported 0.103 from the same contract.

3. IT ONLY READS A CONTRACT IF YOU HAND IT ONE. With no second argument the
   contract dict is empty and every number falls back, so the output looks
   authoritative and is derived from nothing. lot.py already knows how to find the
   contract ($DC_AGENT_CONTRACT, then the deli_counter sibling); this uses the same
   order rather than inventing a third.

The three compound: the numbers it printed came from the wrong body, via
fallbacks, through a path where the major branch was switched off. It happened to
be directionally right, which is worse than being wrong, because it was quoted as
evidence the gate worked.

Also finds the site spec by matching spec["name"] against the scene's stem rather
than guessing from the directory -- Lot names a scene from the name FIELD, so
specs/ref_pvp/ref_pvp_site.json builds ref_pvp_site.tscn, and a directory guess
misses it. If no spec can be found the CLI says the major finding cannot fire,
because a check that cannot fail must not be able to look like one that passed.

Asserts its target before writing, refuses on a miss, idempotent, byte-compiles,
and runs the fixed CLI against a built scene so the change is visible.
"""
import glob
import os
import pathlib
import py_compile
import shutil
import subprocess
import sys

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
STEPS_PY = ROOT / "lot" / "site_steps.py"

OLD = '''if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: python site_steps.py <site.tscn> [agent_contract.json]")
        raise SystemExit(2)
    contract = {}
    if len(sys.argv) > 2 and os.path.exists(sys.argv[2]):
        contract = json.load(open(sys.argv[2], encoding="utf-8"))
    r = float(((contract.get("qa") or {}).get("walker_capsule_radius_m")) or 0.4)
    assist = float(((contract.get("characters") or {}).get("player") or {})
                   .get("max_step_up_m") or 0.5)
    angle = 45.0
    print(f"capsule radius {r} m, floor angle {angle} deg -> unassisted step "
          f"max {unassisted_step_max_m(r, angle):.3f} m; assist {assist} m\\n")
    rows = steps(sys.argv[1], radius_m=r, floor_max_angle_deg=angle,
                 assist_m=assist)
    for s in rows:
        flag = ("ok" if s["walkable_unassisted"]
                else ("needs step-up" if s["climbable_with_assist"] else "JUMP"))
        print(f"  {s['from']:<16} {s['from_top']:+.3f}  ->  {s['to']:<16} "
              f"{s['to_top']:+.3f}   rise {s['rise_m']:.3f} m   {flag}")
    print(f"\\n{len(rows)} transition(s)")
    for f in findings(sys.argv[1], radius_m=r, floor_max_angle_deg=angle,
                      assist_m=assist):
        print(f"\\n[{f['code']}] {f['message']}")
'''

NEW = '''def _find_contract(explicit=None):
    """The agent contract, in the search order lot.py already uses.

    An empty contract is not a neutral default. Every number below then falls
    back, and the output looks authoritative while being derived from nothing.
    """
    cands = []
    if explicit:
        cands.append(explicit)
    if os.environ.get("DC_AGENT_CONTRACT"):
        cands.append(os.environ["DC_AGENT_CONTRACT"])
    here = os.path.dirname(os.path.abspath(__file__))
    cands.append(os.path.join(os.path.dirname(here), "deli_counter",
                              "agent_contract.json"))
    for c in cands:
        try:
            with open(c, "r", encoding="utf-8") as f:
                return json.load(f), c
        except (OSError, ValueError):
            continue
    return {}, None


def _all_specs():
    """[(directory name, path, parsed spec)] for every site spec beside this."""
    here = os.path.dirname(os.path.abspath(__file__))
    base = os.path.join(here, "specs")
    out = []
    if not os.path.isdir(base):
        return out
    for entry in sorted(os.listdir(base)):
        d = os.path.join(base, entry)
        if not os.path.isdir(d):
            continue
        for fname in sorted(os.listdir(d)):
            if not fname.endswith("_site.json"):
                continue
            try:
                with open(os.path.join(d, fname), "r", encoding="utf-8") as f:
                    out.append((entry, os.path.join(d, fname), json.load(f)))
            except (OSError, ValueError):
                continue
    return out


def _find_spec(tscn_path, explicit=None):
    """The site spec that produced this scene.

    Matched on spec["name"] against the scene's stem FIRST, and only then on the
    directory the spec lives in: Lot names a scene from the name FIELD, so
    specs/ref_pvp/ref_pvp_site.json builds ref_pvp_site.tscn -- and a directory
    named ref_pvp_site also exists, so a single pass that accepted either would
    resolve by directory-listing order rather than by intent. Two passes, name
    first, is deterministic.
    """
    if explicit:
        with open(explicit, "r", encoding="utf-8") as f:
            return json.load(f), explicit
    stem = os.path.splitext(os.path.basename(tscn_path))[0]
    specs = _all_specs()
    for _dir, path, spec in specs:
        if spec.get("name") == stem:
            return spec, path
    for _dir, path, spec in specs:
        if _dir == stem:
            return spec, path
    return None, None


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(
        description="Every place a site asks a body to step up, off the "
                    "emitted scene.")
    ap.add_argument("scene", help="a built <site>.tscn")
    ap.add_argument("contract_positional", nargs="?", default=None,
                    help="agent_contract.json (legacy positional form)")
    ap.add_argument("--contract", default=None,
                    help="agent_contract.json; otherwise "
                         "$DC_AGENT_CONTRACT then the deli_counter sibling")
    ap.add_argument("--spec", default=None,
                    help="the site spec; otherwise matched on its name field")
    args = ap.parse_args()

    contract, cpath = _find_contract(args.contract or args.contract_positional)
    if cpath is None:
        print("NO AGENT CONTRACT FOUND. Every metric below would be a fallback, "
              "so nothing is reported. Pass --contract or set "
              "$DC_AGENT_CONTRACT.")
        raise SystemExit(2)

    player = (contract.get("characters") or {}).get("player") or {}
    # The BODY, not the QA walker and not the bake radius. What a capsule walks
    # up is a property of the thing that walks; the walker is deliberately
    # narrower and the bake radius deliberately wider than any body.
    r = float(player.get("radius_m") or 0)
    assist = float(player.get("max_step_up_m") or 0)
    if not r or not assist:
        print(f"{cpath} has no characters.player radius_m / max_step_up_m. "
              f"Nothing is reported rather than guessing a body.")
        raise SystemExit(2)
    angle = 45.0

    spec, spath = _find_spec(args.scene, args.spec)
    print(f"contract {cpath}")
    print(f"player radius {r} m, floor angle {angle:.0f} deg -> walks up "
          f"{unassisted_step_max_m(r, angle):.4f} m unassisted; a controller "
          f"lifts itself {assist} m")
    if spec is None:
        print("NO SITE SPEC FOUND for this scene, so nothing knows which "
              "transitions are ON a route.\\n  "
              f"{CODE_ROUTE_BLOCKED} CANNOT FIRE -- pass --spec. A quiet run "
              "here is not a clean one.")
    else:
        print(f"spec     {spath}")
    print()

    rows = steps(args.scene, radius_m=r, floor_max_angle_deg=angle,
                 assist_m=assist)
    for s in rows:
        flag = ("ok" if s["walkable_unassisted"]
                else ("needs step-up" if s["climbable_with_assist"] else "JUMP"))
        print(f"  {s['from']:<16} {s['from_top']:+.3f}  ->  {s['to']:<16} "
              f"{s['to_top']:+.3f}   rise {s['rise_m']:.3f} m   {flag}")
    print(f"\\n{len(rows)} transition(s)")

    issues = findings(args.scene, radius_m=r, floor_max_angle_deg=angle,
                      assist_m=assist, site_spec=spec)
    for f in issues:
        print(f"\\n[{f['code']}] {f['message']}")
    if not issues:
        print("\\nno findings"
              + ("" if spec is not None else " -- but see the missing-spec note "
                                            "above"))
    # 1 = checked, found a major finding. 2 = COULD NOT check. 0 = checked,
    # clean. A run whose major branch was unreachable must not exit 0, or every
    # wrapper reads "could not check" as "passed" -- which is the whole reason
    # this entry point needed fixing.
    if any(f.get("severity") == "major" for f in issues):
        raise SystemExit(1)
    raise SystemExit(0 if spec is not None else 2)
'''


def main() -> int:
    if not STEPS_PY.exists():
        raise SystemExit(f"missing {STEPS_PY}. Nothing written.")
    src = STEPS_PY.read_text(encoding="utf-8")
    if "def _find_spec(" in src:
        print("site_steps.py: CLI already reads the contract and finds the spec")
        return 0
    if src.count(OLD) != 1:
        raise SystemExit(
            f"site_steps.py: the __main__ block appears {src.count(OLD)} "
            f"time(s), expected exactly 1. Read the file rather than forcing "
            f"this. NOTHING WRITTEN.")
    backup = STEPS_PY.with_suffix(".py.pre_cli")
    if not backup.exists():
        shutil.copy2(STEPS_PY, backup)
    STEPS_PY.write_text(src.replace(OLD, NEW), encoding="utf-8")
    py_compile.compile(str(STEPS_PY), doraise=True)
    print("site_steps.py: CLI reads the contract, uses the PLAYER radius, and "
          "passes the site spec")
    print(f"site_steps.py: compiles; previous file kept at {backup.name}")

    # prove it against a real scene, and against the site we know the answer for
    scenes = sorted(glob.glob(str(ROOT / "_runs" / "*_proj" / "*.tscn")))
    scenes = [s for s in scenes if not s.endswith("_navqa.tscn")]
    pick = ([s for s in scenes if "ballpark_block" in s] or scenes)[:1]
    if not pick:
        print("\n  no built scene under _runs to demonstrate against. Build one, "
              "then:\n    python lot\\site_steps.py <scene>")
        return 0
    print(f"\n=========== the CLI, run on {os.path.basename(pick[0])} ===========")
    r = subprocess.run([sys.executable, str(STEPS_PY), pick[0]],
                       capture_output=True, text=True, cwd=str(ROOT / "lot"))
    out = (r.stdout or "").rstrip().splitlines()
    head = out[:6]
    tail = [l for l in out if l.startswith("[LOT_")] or out[-3:]
    for line in head:
        print(f"  {line}")
    print("  ...")
    for line in tail:
        print(f"  {line[:200]}")
    print(f"\n  exit {r.returncode} (1 means a major finding, 0 means none)")
    if r.returncode not in (0, 1):
        print("  UNEXPECTED exit -- stderr tail:")
        for line in (r.stderr or "").rstrip().splitlines()[-8:]:
            print(f"    {line[:200]}")
    print("\n  It should now agree with check_steps.py on the same scene. Two "
          "instruments\n  reading the same number is the point; they disagreed "
          "by 14 mm before this.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
