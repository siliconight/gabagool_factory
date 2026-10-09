"""Cold run 9209: did the responders' car make it from Zoo's site kit into the
package, named, unstood -- and imported dynamic (Level Factory 0.162.1)?

    python check_vehicle.py [workspace]     (default: workspaces/cold-9209-ws)

Reads, in pipeline order, and prints what each says:
1. the site kit's `site_kit.built.json`: the cruiser module and its status;
2. the themed site: `responders.json`, the car in `cover/`, and whether
   `site.tscn` names it (it must not);
3. the package: the car and every texture it names, `responder_arrivals.json`
   (schema, each arrival's `vehicle_scene`, `vehicle_findings`), and the
   export's own closure and GLB-reference verdicts.
A file it cannot find, or a shape it does not know, is printed as such and
counted. Prints what it measured and stops.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
WS = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "workspaces" / "cold-9209-ws"
LF = WS / ".level_factory"
PKG = LF / "exports" / "LF_club_block_014.portable-godot"
unknown = []


def load(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        unknown.append(f"{p}: {exc}")
        return None


# 1. the site kit
kits = sorted(LF.glob("jobs/club_block_014.zoo_kit_build.site*/*/out/**/site_kit.built.json"))
kits = kits or sorted(LF.glob("jobs/*zoo_kit_build*site*/**/site_kit.built.json"))
print("site kit index:", kits[-1] if kits else "NOT FOUND")
if kits:
    idx = load(kits[-1])
    rows = idx.get("modules") if isinstance(idx, dict) else idx
    if not isinstance(rows, list):
        unknown.append(f"site_kit.built.json: no module list ({type(idx).__name__})")
        rows = []
    cars = [r for r in rows if "cruiser" in str(r.get("stem", ""))]
    print("  cruiser rows:", [(r.get("stem"), r.get("status")) for r in cars])

# 2. the themed site
themed = sorted(LF.glob("jobs/club_block_014.themed_site_assemble*/*/out"))
themed = themed[-1] if themed else None
print("themed site:", themed or "NOT FOUND")
if themed:
    rv = load(themed / "responders.json")
    if rv:
        print("  responders.json:", [(v["arrival"], v["scene"], v["stop"]) for v in rv["vehicles"]],
              "missing", rv["missing"])
        for v in rv["vehicles"]:
            print("  in cover/:", v["scene"], (themed / v["scene"]).is_file())
        scene = (themed / "site.tscn").read_text(encoding="utf-8") if (themed / "site.tscn").is_file() else ""
        stems = {pathlib.Path(v["scene"]).stem for v in rv["vehicles"]}
        print("  site.tscn names the car:", any(s in scene for s in stems))

# 3. the package
arr = load(PKG / "responder_arrivals.json")
if arr:
    print("responder_arrivals.json:", arr.get("schema"), len(arr.get("arrivals", [])), "arrivals")
    for a in arr.get("arrivals", []):
        vs = a.get("vehicle_scene", "KEY ABSENT")
        rel = vs[len("res://"):] if isinstance(vs, str) and vs.startswith("res://") else None
        print("  ", a["anchor"], "vehicle_scene", vs, "in package:", bool(rel) and (PKG / rel).is_file())
    print("  vehicle_findings:", arr.get("vehicle_findings", "KEY ABSENT"))
    cars = {a.get("vehicle_scene") for a in arr.get("arrivals", []) if a.get("vehicle_scene")}
    for vs in sorted(cars):
        glb = PKG / vs[len("res://"):]
        print("  car file:", glb.name, glb.stat().st_size if glb.is_file() else "ABSENT", "bytes")
        imp = glb.with_name(glb.name + ".import")
        lines = [ln for ln in imp.read_text(encoding="utf-8").splitlines()
                 if ln.startswith("meshes/light_baking=")] if imp.is_file() else []
        # 2 is Static Lightmaps, 3 Dynamic: measured in cold run 9208's notes
        print("  car import:", lines or "NO light_baking LINE",
              "unwrap cache:", glb.with_name(glb.name + ".unwrap_cache").is_file())
        if not lines:
            unknown.append(f"{imp}: no meshes/light_baking line")
closure = load(PKG / "export_closure_scan.json")
if closure is not None:
    print("closure scan: ok", closure.get("ok"), "issues", len(closure.get("issues") or []),
          "missing", closure.get("missing_resource_count"))
glbs = load(PKG / "glb_reference_scan.json")
if glbs is not None:
    # read off cold run 9207's: ok, glbs_scanned, references, resolved, and
    # `missing` a list -- a scan without them is counted, not passed
    need = ("ok", "glbs_scanned", "references", "resolved", "missing")
    if not isinstance(glbs, dict) or any(k not in glbs for k in need):
        unknown.append("glb_reference_scan.json: not the shape cold run 9207 wrote")
    else:
        print("glb reference scan: ok", glbs["ok"], "glbs", glbs["glbs_scanned"], "references",
              glbs["references"], "resolved", glbs["resolved"], "missing", len(glbs["missing"]))
lb = load(PKG / "light_bake.json")
if lb is not None:
    imports = lb.get("imports") or {}
    print("light_bake.json: ok", lb.get("ok"), "spawned", imports.get("spawned", "KEY ABSENT"),
          "unmatched", imports.get("spawned_unmatched", "KEY ABSENT"))
print("unread or unknown:", unknown or "none")
