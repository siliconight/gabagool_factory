# ============================================================
#  commit_session.ps1 -- commit the tintable / metal-split run
#
#  zoo       0.38.0 (last tag) -> 0.44.0   one commit, tag v0.44.0
#  pixelcoat 0.12.0 (last tag) -> 0.15.0   one commit, tag v0.15.0
#  factory   patches/ committed as the audit trail
#
#  WHY EXPLICIT PATHS. `git add -A` would sweep zoo\_preview_plastic\,
#  zoo\_preview_street\ and pixelcoat\_probe\ into history -- none of them
#  are gitignored (checked), and they are hundreds of MB of render output
#  and probe GLBs. Every path below is named. After staging, the script
#  ASSERTS that nothing matching those patterns got staged anyway, and
#  unstages + aborts if it did.
#
#  Run:
#    pwsh -ExecutionPolicy Bypass -File ...\commit_session.ps1 -Check
#    pwsh -ExecutionPolicy Bypass -File ...\commit_session.ps1
# ============================================================
param([switch]$Check)

$ErrorActionPreference = "Stop"
$F = "C:\Projects\gabagool_studios\gabagool_factory"

# Path-COMPONENT match, not a substring. The first version of this was
# '_preview|_probe|...' and it blocked tools/tint_probe.py -- a file we very
# much want committed -- because 'tint_probe' contains '_probe'. It also let a
# root-level build/ through, since it required a LEADING slash. Anchored to a
# segment boundary and a trailing slash, so only real directories match.
$FORBIDDEN = '(^|/)(_preview[^/]*|_probe|_runs|_scratch|build)/'

# ---- what each repo commits ------------------------------------------------
$ZOO = @(
  "CHANGELOG.md", "VERSION",
  "tools/preview_specimen.py", "tools/preview_street_solids.ps1",
  "tools/tint_probe.py",
  "zoo_keeper/bpylayer/geometry.py", "zoo_keeper/bpylayer/materials.py",
  "zoo_keeper/core/kit.py", "zoo_keeper/core/skins.py",
  "zoo_keeper/genome/species/helmet.json",
  "zoo_keeper/genome/species/queue_stanchion.json",
  "zoo_keeper/genome/species/simple_car.json",
  "zoo_keeper/genome/species/vending_machine.json",
  "zoo_keeper/recipes/simple_car.py",
  "tests/test_material_options_closed.py", "tests/test_tintable.py",
  "tests/test_volume_stem.py",
  ".gitignore"
)
$PX = @(
  "CHANGELOG.md", "VERSION",
  "pixelcoat/core/material_grammar.py", "pixelcoat/version.py",
  "profiles/materials/metal_bare_neutral.json",
  "profiles/materials/metal_painted_neutral.json",
  "profiles/materials/plastic_neutral.json",
  "profiles/themes/bank.json", "profiles/themes/casino.json",
  "profiles/themes/delco.json", "profiles/themes/rockay.json",
  "profiles/themes/rockay_civic.json", "profiles/themes/rockay_retail.json",
  "profiles/themes/rockay_service.json", "profiles/themes/stadium.json",
  "profiles/themes/street.json",
  "tools/rebuild_theme_libraries.ps1",
  ".gitignore"
)

# ---- gitignore lines to guarantee, per repo --------------------------------
$IGNORE = @{
  "zoo"       = @("_preview_*/", "_probe/")
  "pixelcoat" = @("_probe/")
}

function Ensure-Ignore($repo) {
  $p = Join-Path $F "$repo\.gitignore"
  $have = if (Test-Path $p) { Get-Content $p } else { @() }
  $add = @()
  foreach ($line in $IGNORE[$repo]) {
    if ($have -notcontains $line) { $add += $line }
  }
  if ($add.Count -eq 0) { Write-Host "  .gitignore already covers it"; return $false }
  if ($Check) {
    Write-Host ("  .gitignore WOULD gain: " + ($add -join ", "))
    return $false
  }
  # LF, not Add-Content's CRLF: the rest of these files are LF and git
  # warned about the mixed endings on the first run.
  $text = ($add -join "`n") + "`n"
  [System.IO.File]::AppendAllText($p, $text)
  Write-Host ("  .gitignore += " + ($add -join ", "))
  return $true
}

function Show-Missing($repo, $paths) {
  $miss = @()
  foreach ($rel in $paths) {
    if ($rel -eq ".gitignore") { continue }
    if (-not (Test-Path (Join-Path $F "$repo\$rel"))) { $miss += $rel }
  }
  if ($miss.Count) {
    Write-Host "  MISSING ON DISK (will not be committed):"
    $miss | ForEach-Object { Write-Host ("    " + $_) }
  }
  return $miss
}

function Stage-And-Guard($repo, $paths) {
  Push-Location (Join-Path $F $repo)
  foreach ($rel in $paths) {
    if (Test-Path $rel) { & git add -- $rel }
  }
  $staged = & git diff --cached --name-only
  $bad = $staged | Where-Object { $_ -match $FORBIDDEN }
  if ($bad) {
    Write-Host "  ABORT -- these would have entered history:" -ForegroundColor Red
    $bad | ForEach-Object { Write-Host ("    " + $_) }
    & git reset --quiet
    Pop-Location
    throw "$repo : forbidden paths staged"
  }
  Write-Host ("  staged " + ($staged | Measure-Object).Count + " file(s)")
  $staged | ForEach-Object { Write-Host ("    " + $_) }
  Pop-Location
  return $staged
}

$ZooMsg = @'
zoo 0.39.0 - 0.44.0: tintable packs, the metal split, batch 1

Six releases developed in one working tree and committed together; the
CHANGELOG carries the per-version detail. Tagged v0.44.0 only, because all
of it is one tree and eight tags on one commit would read as eight trees.

0.39.0/0.39.1  prop stem carries height; --species on preview_specimen
0.40.0/0.41.0  shade-by-angle and taper_z; simple_car rebuilt parametrically
0.42.0         packs can declare `tintable`; make_material multiplies the
               mesh colour into an achromatic pack and keys the material
               cache on (kind, theme, colour)
0.42.1         tint_probe measured the export boundary on Blender 5.1.1 --
               baseColorFactor carries the genome colour, texture intact
0.43.0         metal_painted / metal_bare registered. Two kinds and not one
               because METALLIC is per-kind: paint is a dielectric (0.0),
               bare metal a conductor (0.90). Scoped by measurement: of 42
               species that can wear `metal`, only 12 declare a style colour
               with chroma >= 0.10; the other 30 -- ten of them architecture
               -- correctly keep the theme-owned kind.
0.44.0         batch 1 onto metal_painted: vending_machine, simple_car,
               helmet, queue_stanchion. Genome data only.

test_material_options_closed.py asserts, across all 53 genomes, that every
styles[*].material and the default are present in materials.options --
dna.resolve_plan discards a kind that is not, silently, and the failure mode
is a render that looks untouched.

479 passed, 2 skipped.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01EcV9Es5RCxEZyW87879Coj
'@

$PxMsg = @'
pixelcoat 0.13.0 - 0.15.0: tintable grammars and prop metal

0.13.0  `tintable` on the material grammar, written into every pack
        manifest. A grammar sets it when its albedo is deliberately
        achromatic and the consumer supplies the hue. Adds
        plastic_neutral. Also reconciles version.py, which the 0.12.0
        release left at 0.11.0 -- every pack built since was stamped with
        the wrong tool_version.
0.14.0  all nine themes map plastic -> plastic_neutral. 17 of 53 Zoo
        species can wear plastic; they now take grain and roughness while
        keeping their own colour.
0.15.0  metal_painted_neutral and metal_bare_neutral, both tintable,
        mapped in all nine themes. `metal` is untouched and stays
        theme-owned -- a rusted facade belongs to the building.

Theme libraries under build/ are gitignored and rebuilt with
tools/rebuild_theme_libraries.ps1, which deletes before it builds:
build_material_pack does makedirs(exist_ok=True) without clearing, and
zoo's load_pack takes sorted(*.pack.json)[0], so a rebuild in place layers
a second manifest and the alphabetically-first one keeps winning.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01EcV9Es5RCxEZyW87879Coj
'@

$FacMsg = @'
patches: the verification record for the tintable / metal-split run

Ten patch scripts, each carrying pre/post sha256 per target, an
all-or-nothing pre-flight sweep, --check / --selftest / --revert, and a
falsification that must FAIL when the change is backed out. Committed as
the record of how each change was made and proven, so a later session can
re-run --selftest against the tree.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01EcV9Es5RCxEZyW87879Coj
'@

$PLAN = @(
  @{ repo = "zoo";       paths = $ZOO; msg = $ZooMsg; tag = "v0.44.0" },
  @{ repo = "pixelcoat"; paths = $PX;  msg = $PxMsg;  tag = "v0.15.0" }
)

foreach ($step in $PLAN) {
  $existing = & git -C (Join-Path $F $step.repo) tag --list $step.tag
  if ($existing) {
    throw ($step.repo + ": tag " + $step.tag + " ALREADY EXISTS. Refusing -- " +
           "re-running this script would commit on top of a tagged release.")
  }
}

foreach ($step in $PLAN) {
  Write-Host ""
  Write-Host ("=== " + $step.repo)
  Ensure-Ignore $step.repo | Out-Null
  Show-Missing $step.repo $step.paths | Out-Null
  if ($Check) {
    Push-Location (Join-Path $F $step.repo)
    Write-Host "  would commit (working-tree state):"
    & git status --short -- $step.paths | ForEach-Object { Write-Host ("    " + $_) }
    Write-Host ("  would tag: " + $step.tag)
    Pop-Location
    continue
  }
  Stage-And-Guard $step.repo $step.paths | Out-Null
  $tmp = Join-Path $env:TEMP ($step.repo + "_msg.txt")
  Set-Content -Path $tmp -Value $step.msg -Encoding utf8
  Push-Location (Join-Path $F $step.repo)
  & git commit -F $tmp | Out-Null
  if ($LASTEXITCODE -ne 0) { Pop-Location; throw ($step.repo + ": git commit failed (exit " + $LASTEXITCODE + ") -- NOT tagging") }
  & git tag -a $step.tag -m ($step.repo + " " + $step.tag)
  if ($LASTEXITCODE -ne 0) { Pop-Location; throw ($step.repo + ": commit OK but `git tag " + $step.tag + "` failed -- does the tag already exist?") }
  Write-Host ("  committed " + (& git rev-parse --short HEAD) + "   tagged " + $step.tag)
  Pop-Location
}

# ---- factory: the patches folder -------------------------------------------
Write-Host ""
Write-Host "=== factory (patches/)"
Push-Location $F
if ($Check) {
  & git status --short -- patches | ForEach-Object { Write-Host ("    " + $_) }
  Write-Host "  (no factory tag here -- that waits for the manifest bump)"
} else {
  & git add -- patches
  $staged = & git diff --cached --name-only
  $bad = $staged | Where-Object { $_ -match $FORBIDDEN }
  if ($bad) {
    $bad | ForEach-Object { Write-Host ("    FORBIDDEN " + $_) -ForegroundColor Red }
    & git reset --quiet
    Pop-Location
    throw "factory: forbidden paths staged"
  }
  Write-Host ("  staged " + ($staged | Measure-Object).Count + " file(s)")
  $tmp = Join-Path $env:TEMP "factory_msg.txt"
  Set-Content -Path $tmp -Value $FacMsg -Encoding utf8
  & git commit -F $tmp | Out-Null
  if ($LASTEXITCODE -ne 0) { Pop-Location; throw ("factory: git commit failed (exit " + $LASTEXITCODE + ")") }
  Write-Host ("  committed " + (& git rev-parse --short HEAD))
  Write-Host "  NO factory tag yet -- factory.manifest.json still pins the old"
  Write-Host "  versions. Bump + verify-manifest first, then factory-v1.31.0."
}
Pop-Location

Write-Host ""
if ($Check) { Write-Host "-Check: nothing staged, nothing written." }
