# ============================================================================
#  commit_pass.ps1  --  version bumps + CHANGELOG + commit + tag (4 tool repos)
#  Writes version files with LF endings (no BOM), prepends CHANGELOG entries,
#  then git add -A / commit / annotated tag. DOES NOT PUSH -- review first.
#  Run from anywhere:  powershell -ExecutionPolicy Bypass -File .\commit_pass.ps1
# ============================================================================
$ErrorActionPreference = "Stop"
$root = "C:\Projects\gabagool_studios\gabagool_factory"

function Write-Lf([string]$path, [string]$text) {
    # LF line endings, UTF-8 no BOM -- keeps git diffs clean on Windows.
    $enc = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($path, ($text -replace "`r`n", "`n"), $enc)
}

function Prepend-Changelog([string]$path, [string]$entry) {
    $raw = [System.IO.File]::ReadAllText($path)
    $idx = $raw.IndexOf("## [")
    if ($idx -lt 0) { throw "no '## [' entry marker found in $path" }
    $updated = $raw.Substring(0, $idx) + $entry.TrimEnd() + "`n`n" + $raw.Substring($idx)
    $enc = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($path, $updated, $enc)
}

function Replace-In([string]$path, [string]$find, [string]$repl) {
    $raw = [System.IO.File]::ReadAllText($path)
    if (-not $raw.Contains($find)) { throw "expected '$find' not found in $path" }
    $enc = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($path, $raw.Replace($find, $repl), $enc)
}

function Commit-Repo([string]$name, [string]$msg, [string]$tag) {
    $p = Join-Path $root $name
    Write-Host "==================== $name ====================" -ForegroundColor Cyan
    git -C $p add -A
    git -C $p commit -m $msg | Out-Host
    git -C $p tag -a $tag -m $tag | Out-Host
    Write-Host "tagged $tag @ $(git -C $p log -1 --oneline)" -ForegroundColor Green
}

# ---------------------------------------------------------------------------
# 1. PIXELCOAT  0.10.0 -> 0.11.0
# ---------------------------------------------------------------------------
$px = Join-Path $root "pixelcoat"
Write-Lf   (Join-Path $px "VERSION") "Pixelcoat 0.11.0`n"
Replace-In (Join-Path $px "pixelcoat\version.py") '__version__ = "0.10.0"' '__version__ = "0.11.0"'
Prepend-Changelog (Join-Path $px "CHANGELOG.md") @'
## [0.11.0] - Procedural material library + themed curation + stylized glass

### Added
- Two surface primitives: `voronoi_cells` (filled Voronoi cells with a
  per-cell id, for cobblestone/terrazzo/flagstone aggregates) and `wave`
  (undulating flutes; warp=0 gives straight reeded glass).
- `MaterialGrammar` gains `aggregate` (per-cell palette + mortar), `emissive`,
  `transparency` (an import hint, not lighting -- see below), multi-scale
  `veins` (list of passes), and `albedo_pattern` (albedo-only value mod).
- ~23 new tiling grammars: cinderblock, cobblestone, flagstone, granite,
  travertine, marble, subway/terrazzo/vct tile, hardwood/plywood,
  rusted/brass/galvanized/spandrel metal, stucco, pebble.
- Six textured glasses (circles, cracked_cells, wavy, blobby, frosted,
  reeded) + three opaque `glass_facade` variants (bronze, mirror_blue,
  spandrel_green) for hollow-shell building fronts.
- Themed curation: `build_theme_library()` + `pixelcoat theme-library
  --theme <t> --out <dir>` build one `<kind>_<theme>/` pack per curated
  material from `profiles/themes/<theme>.json`. Profiles shipped:
  street, delco, casino, stadium, bank.

### Changed
- Retuned `ceiling_tile_delco` (coarser acoustic grid) and
  `marble_bank_floor` (sharper veins).

### Notes
- Transparency is authored as a pack hint
  (`import_hints.transparency = {opacity, ior, alpha_mode}`); Pixelcoat never
  sets shader/lighting state itself -- Zoo honors the hint on the material.
'@

# ---------------------------------------------------------------------------
# 2. ZOO  0.34.0 -> 0.35.0
# ---------------------------------------------------------------------------
$zo = Join-Path $root "zoo"
Write-Lf (Join-Path $zo "VERSION") "0.35.0`n"
Prepend-Changelog (Join-Path $zo "CHANGELOG.md") @'
## [0.35.0] - Glass-facade kind + transparency import + themed glazing routing

### Added
- `glass_facade` material kind (opaque building-front glazing) registered in
  `core.skins.KNOWN_KINDS`; roughness anchor .08 in `bpylayer.materials`.
- Transparency import: `skins.load_pack` surfaces
  `import_hints.transparency`; `bpylayer.materials` sets BSDF Alpha + IOR and
  the mesh blend method when opacity < 1, so a Pixelcoat see-through pack
  renders transparent (glTF alphaMode=BLEND -> Godot transparent).
- Glazing routing (4 hops): `kit.plan_kit` threads a slot's `glazing` onto
  the module key/bucket; `bpylayer.build.build_module` maps
  `glazing=="facade"` -> `glazing_kind="glass_facade"`; `recipes/_arch`
  window pane resolves `plan.glazing_kind` -- facade windows wear opaque
  glass, interior windows stay see-through.

### Verified
- Hardware (Blender 5.1): street kit build skinned `glass <- glass_circles`
  on real window geometry; imported window GLB pane reads see-through in
  Material Preview. 13 modules built, 0 failed.
'@

# ---------------------------------------------------------------------------
# 3. DELI_COUNTER  0.79.0 -> 0.80.0
# ---------------------------------------------------------------------------
$dc = Join-Path $root "deli_counter"
Write-Lf   (Join-Path $dc "VERSION") "Deli Counter 0.80.0`n"
Replace-In (Join-Path $dc "version.py") 'KIT_VERSION = "0.79.0"' 'KIT_VERSION = "0.80.0"'
Prepend-Changelog (Join-Path $dc "CHANGELOG.md") @'
## [0.80.0] - Facade windows tag opaque glazing

- `_record_opening_slot`: a `window` opening on a `facade` shell (a hollow
  building front with no interior) now tags `glazing:"facade"` on the slot,
  so Zoo skins those panes with opaque `glass_facade` instead of see-through
  glass -- you no longer look "through" a building that has nothing inside.
  Non-facade (interior) windows are unchanged and remain transparent.
'@

# ---------------------------------------------------------------------------
# 4. LEVEL_FACTORY  0.10.5 -> 0.11.0
# ---------------------------------------------------------------------------
$lf = Join-Path $root "level_factory"
Write-Lf (Join-Path $lf "VERSION") "0.11.0`n"
Prepend-Changelog (Join-Path $lf "CHANGELOG.md") @'
## [0.11.0] - Pixelcoat stage builds the themed skins library

- `adapters/pixelcoat`: theme mode -- when a job spec carries `theme`, the
  stage plans `pixelcoat theme-library --theme <t> --out <work>` (one
  `<kind>_<theme>/` pack per curated material) instead of a single legacy
  recipe. `validate_configuration`/`fingerprint_inputs` accept a theme and
  invalidate on the theme profile's hash.
- `_job_specs_for_plan`: the pixelcoat job now derives
  `{theme: model.theme or batch.theme_family or "delco"}`. The Zoo kit stage
  already points `--skins` at that job's `out/` and `--theme` at the same
  theme, so a building wears its theme profile's curated vocabulary end to end.
- `packages/pipeline/planner`: pixelcoat stage `expected_outputs` relaxed to
  `[]` -- the library is a dynamic set of `<kind>_<theme>/` dirs, validated
  by the adapter in `normalize_validation`.

### Verified
- Seam confirmed against the real scheduler: `_publish_stable` reconstructs
  each output's path relative to work_dir, so the `<kind>_<theme>/`
  subdirectories survive into the stable `out/` the Zoo stage resolves from.
'@

# ---------------------------------------------------------------------------
#  Commit + tag (NO push)
# ---------------------------------------------------------------------------
Commit-Repo "pixelcoat"    "0.11.0: procedural material library + themed glass/curation -- voronoi_cells+wave primitives, aggregate/emissive/transparency grammars, ~23 new grammars, 6 glass + 3 facade, theme-library CLI + 5 profiles" "v0.11.0"
Commit-Repo "zoo"          "0.35.0: glass_facade kind + transparency import (BSDF alpha/blend) + themed glazing routing (kit->build->arch); facade windows opaque, glass see-through (validated Blender 5.1)" "v0.35.0"
Commit-Repo "deli_counter" "0.80.0: facade windows tag glazing=facade so Zoo skins hollow-shell panes opaque; interior windows stay transparent" "v0.80.0"
Commit-Repo "level_factory" "0.11.0: pixelcoat stage builds the themed skins library (theme-library) the Zoo kit resolves from; job specs derive theme; planner expected_outputs relaxed" "v0.11.0"

Write-Host ""
Write-Host "All four repos committed + tagged. Nothing pushed yet." -ForegroundColor Yellow
Write-Host "Review, then push each with:" -ForegroundColor Yellow
Write-Host '  git -C "C:\Projects\gabagool_studios\gabagool_factory\pixelcoat"    push origin main --follow-tags'
Write-Host '  git -C "C:\Projects\gabagool_studios\gabagool_factory\zoo"          push origin main --follow-tags'
Write-Host '  git -C "C:\Projects\gabagool_studios\gabagool_factory\deli_counter" push origin main --follow-tags'
Write-Host '  git -C "C:\Projects\gabagool_studios\gabagool_factory\level_factory" push origin main --follow-tags'
