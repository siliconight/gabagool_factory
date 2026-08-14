# Factory Re-Certification Runbook

How to promote the certified lockstep set after a tool bump. Written for the
`1.1.0 -> 1.2.0` re-cert (zoo `0.34.0`, pixelcoat `0.10.0`), but the shape is
reusable for any bump. All paths assume the factory root
`C:\Projects\gabagool_studios\gabagool_factory`.

## What changed this cycle -> what must be re-proven

- **zoo 0.30.2 -> 0.34.0** — floor/ceiling surface species + 6 tiling material
  kinds. Re-proven by the **walkabout** (real Blender build of zoo species).
- **pixelcoat 0.9.0 -> 0.10.0** — DELCO signage packs. Re-proven by building
  the packs and having the **LF real-tool smoke** drive them through zoo's
  resolver.
- deli_counter / lot / lux / dispatch / pipeline: **unchanged** this cycle.
  The engine leg (steps 4) is therefore belt-and-suspenders for a clean
  "verified together" stamp, not strictly gated by the two bumps.

## Prerequisites (once per shell)

```powershell
# Blender: walkabout.ps1 uses C:\blender\blender.exe directly; DC build.py
# resolves Blender via $BLENDER / PATH.
$env:BLENDER = "C:\blender\blender.exe"

# Godot (only for the engine leg, step 4). Prefer the _console.exe variant.
$env:DC_GODOT = "C:\path\to\Godot_v4.7-stable_win64_console.exe"

# level-factory CLI (for verify-manifest). From the factory root:
pip install -e level_factory
```

## Step 0 — see the drift (confirms why we're here)

```powershell
level-factory verify-manifest --factory C:\Projects\gabagool_studios\gabagool_factory
```

Reads the LIVE manifest (still 1.1.0), so it should report **DRIFT** on `zoo`
and `pixelcoat` and **OK** on everything else. That drift is the trigger for
this whole runbook. (`DRIFT` = same major, re-certify + bump; `INCOMPATIBLE` =
major bump; `UNKNOWN` = no VERSION source.)

## Step 1 — Zoo walkabout (covers the 0.34.0 bump)

```powershell
powershell -ExecutionPolicy Bypass -File C:\Projects\gabagool_studios\gabagool_factory\zoo\tools\walkabout.ps1
```

Runs: env audit -> tool versions -> manifest discovery -> anchor counts ->
zoo plan (pure) -> zoo Blender build (building) -> zoo Blender build (site
streetlights) -> built-index gates -> zips everything under
`_runs\walkabout_<stamp>\`. Green across all sections = the zoo art-pass leg
holds with the new species/kinds. Paste any failure back here.

## Step 2 — Pixelcoat signage packs (covers the 0.10.0 bump)

```powershell
cd C:\Projects\gabagool_studios\gabagool_factory\pixelcoat
powershell -ExecutionPolicy Bypass -File tools\make_delco_signage.ps1
```

Builds the six DELCO packs into
`_runs\skins\delco_signage\signs_delco\<asset_id>\` — the exact layout zoo's
sign-pack resolver consumes via `--skins`.

## Step 3 — Level Factory suites (the "verified together" proof)

```powershell
cd C:\Projects\gabagool_studios\gabagool_factory\level_factory

# fast suite (real-tool tests auto-skip without LF_TOOLS_DIR)
python -m pytest tests -q

# real-tool smoke: drives the ACTUAL tool repos, i.e. the new zoo + pixelcoat
$env:LF_TOOLS_DIR = "C:\Projects\gabagool_studios\gabagool_factory"
python -m pytest tests/real_tools -q
```

The real-tool smoke is the one that exercises zoo 0.34.0 and pixelcoat 0.10.0
through the orchestrator end-to-end — this is what makes "certified together"
true rather than asserted.

## Step 4 — Engine leg (full 1.1.0 parity; optional this cycle)

deli_counter/lot geometry did not change, so this reproduces the 1.1.0 stamp
rather than testing the bumps. From ENGINE_GATES.md, needs `$env:DC_GODOT`:

```powershell
cd C:\Projects\gabagool_studios\gabagool_factory\deli_counter
python build.py specs\pvp_station_ref.json
python build.py specs\bank_job.json
python nav_gate.py build\pvp_station_ref.glb
python godot_gate.py build\pvp_station_ref.glb
python roundtrip.py build\pvp_station_ref.glb

# stage the built buildings into the reference site
copy build\pvp_station_ref.glb            ..\lot\specs\ref_pvp\buildings\
copy build\pvp_station_ref.gameplay.json  ..\lot\specs\ref_pvp\buildings\
copy build\bank_job.glb                   ..\lot\specs\ref_pvp\buildings\
copy build\bank_job.gameplay.json         ..\lot\specs\ref_pvp\buildings\

cd ..\lot
python lot.py specs\ref_pvp\ref_pvp_site.json --out-dir ..\_runs\ref_pvp_proj --walkable --navqa
xcopy /E /I /Y specs\ref_pvp\buildings ..\_runs\ref_pvp_proj\buildings
python walktest.py ..\_runs\ref_pvp_proj --all
python mp_smoke.py ..\_runs\ref_pvp_proj specs\ref_pvp\ref_pvp_site.json --players 4
cd ..
```

Green across all five gate commands = engine leg intact. (Optional lux visual
leg: `lux\tools\headless_walk.ps1` — lux is unchanged this cycle.)

## Step 5 — promote the manifest + tag the factory

Only after the steps above are green:

```powershell
cd C:\Projects\gabagool_studios\gabagool_factory

# 1. edit factory.manifest.v1.2.0-candidate.json: delete the "status" field
# 2. replace the live manifest with the candidate
move /Y factory.manifest.v1.2.0-candidate.json factory.manifest.json

# 3. confirm the lockstep check is now clean (all OK)
level-factory verify-manifest --factory .

# 4. add a one-line entry to CHANGELOG.md (factory root), then commit + tag.
#    This repo tracks ONLY the manifest + docs; tool dirs are gitignored.
git add factory.manifest.json CHANGELOG.md
git commit -m "factory 1.2.0: re-cert set (zoo 0.34.0, pixelcoat 0.10.0)"
git tag factory-v1.2.0
git push origin main --tags
```

`verify-manifest` reading all-OK against the promoted manifest is the
done-signal: the certified set now honestly describes what is installed.
