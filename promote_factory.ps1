# ============================================================================
#  promote_factory.ps1  --  factory manifest 1.2.0 -> 1.3.0 promotion (CERTIFY.md Step 5)
#  RUN ONLY AFTER the re-cert gates are green (walkabout, LF fast + real-tool smoke).
#  Prepends the factory CHANGELOG entry, strips the candidate's "status" field,
#  swaps it in as the live manifest, runs verify-manifest, then STOPS before
#  commit so you can review. Prints the commit/tag/push commands at the end.
# ============================================================================
$ErrorActionPreference = "Stop"
$root = "C:\Projects\gabagool_studios\gabagool_factory"
$cand = Join-Path $root "factory.manifest.v1.3.0-candidate.json"
$live = Join-Path $root "factory.manifest.json"
$clog = Join-Path $root "CHANGELOG.md"
$enc  = New-Object System.Text.UTF8Encoding($false)   # UTF-8, no BOM

if (-not (Test-Path $cand)) { throw "candidate manifest not found: $cand" }

# --- 1. Prepend the factory CHANGELOG entry (fresh read on THIS machine) -----
$entry = @'
## [factory-v1.3.0] - 2026-07-19

The art/material pass, certified. pixelcoat 0.10.0 -> 0.11.0 (procedural
material library: voronoi_cells + wave primitives, aggregate/emissive/
transparency grammars, ~23 tiling grammars + 6 textured glass + 3 opaque
glass_facade, theme-library CLI + street/delco/casino/stadium/bank profiles);
zoo 0.34.0 -> 0.35.0 (glass_facade kind, pack transparency import -> BSDF
alpha/blend, themed glazing routing kit->build->arch); deli_counter 0.79.0 ->
0.80.0 (facade windows tag glazing=facade -- resolves the 1.2.0 drift
known-issue); level_factory 0.10.5 -> 0.11.1 (pixelcoat stage builds the themed
skins library the Zoo kit resolves from; 0.11.1 realigns the fast-suite stub).
Verified on hardware: theme-library resolution (street/casino library_report),
real Blender kit build (glass<-glass_circles, 13 modules / 0 failed),
transparent window GLB in Blender 5.1, orchestrator out/ subdir preservation,
LF fast suite green. Pins: deli_counter 0.80.0, dispatch 0.3.0, lot 0.19.0,
lux 0.15.4, patina 0.18.0, pipeline 0.1.1, pixelcoat 0.11.0, zoo 0.35.0,
level_factory 0.11.1, laser_tag unpinned.
'@
$raw = [System.IO.File]::ReadAllText($clog)
$idx = $raw.IndexOf("## [")
if ($idx -lt 0) { throw "no '## [' marker found in $clog" }
$updated = $raw.Substring(0, $idx) + $entry.TrimEnd() + "`n`n" + $raw.Substring($idx)
[System.IO.File]::WriteAllText($clog, ($updated -replace "`r`n", "`n"), $enc)
Write-Host "CHANGELOG.md  <- factory-v1.3.0 entry prepended" -ForegroundColor Green

# --- 2. Strip the "status" line from candidate -> live manifest --------------
$lines = [System.IO.File]::ReadAllLines($cand)
$kept  = $lines | Where-Object { $_ -notmatch '^\s*"status"\s*:' }
[System.IO.File]::WriteAllText($live, (($kept -join "`n").TrimEnd() + "`n"), $enc)
Remove-Item $cand
Write-Host "factory.manifest.json  <- promoted (status field removed, candidate deleted)" -ForegroundColor Green

# quick sanity: the promoted manifest must still be valid JSON at 1.3.0
$check = Get-Content $live -Raw | ConvertFrom-Json
if ($check.factory_version -ne "1.3.0") { throw "promoted manifest factory_version != 1.3.0" }
if ($check.PSObject.Properties.Name -contains "status") { throw "status field survived the strip" }
Write-Host "sanity: valid JSON, factory_version=1.3.0, no status field" -ForegroundColor Green

# --- 3. verify-manifest (best-effort; needs level-factory installed) ---------
Write-Host "`n--- verify-manifest ---" -ForegroundColor Cyan
try {
    level-factory verify-manifest --factory $root
} catch {
    Write-Host "verify-manifest not runnable: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "install it with:  pip install -e level_factory   (then re-run verify-manifest)" -ForegroundColor Yellow
}

Write-Host "`nIf verify-manifest reports all OK, commit + tag + push:" -ForegroundColor Yellow
Write-Host '  git -C "C:\Projects\gabagool_studios\gabagool_factory" add factory.manifest.json CHANGELOG.md'
Write-Host '  git -C "C:\Projects\gabagool_studios\gabagool_factory" commit -m "factory 1.3.0: re-cert set (pixelcoat 0.11.0, zoo 0.35.0, deli_counter 0.80.0, level_factory 0.11.1)"'
Write-Host '  git -C "C:\Projects\gabagool_studios\gabagool_factory" tag factory-v1.3.0'
Write-Host '  git -C "C:\Projects\gabagool_studios\gabagool_factory" push origin main --follow-tags'
