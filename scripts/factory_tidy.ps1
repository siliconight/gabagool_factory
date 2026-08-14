<#
.SYNOPSIS
    File the factory root's loose SOURCE into the folders that already exist.

.DESCRIPTION
    Companion to factory_clean.ps1. That one clears regenerable ARTIFACTS;
    this one files loose SOURCE. Same doctrine, from docs\CLEANUP.md:

        allow-list, never guess.  Dry-run by default.  -Apply to execute.

    Anything this script does not have an explicit rule for STAYS WHERE IT IS.
    Silence means "not classified", never "safe to move".

    Destinations are the folders the repo already uses -- nothing invented:

        tools\            probes, censuses, checks   (34 already live here)
        scripts\          .ps1 runbooks              (9 already live here)
        docs\sessions\    SESSION_*.md
        docs\findings\    investigation write-ups
        docs\diagrams\    exported svg/png
        patches\          patch_*.py / unpatch_*.py     <- the only new folder
        _runs\            measurement scratch        (already gitignored AND
                                                      already on factory_clean's
                                                      allow-list, so it gets
                                                      swept for free)

.PARAMETER Apply
    Actually move. Without it you get a report and nothing changes.

.NOTES
    TRACKED FILES MOVE WITH `git mv` so history follows them. Untracked files
    move with Move-Item. The script asks git which is which rather than
    assuming.

    IT REFUSES TO MOVE A SCRIPT THAT LOCATES THINGS VIA `__file__`. Every
    patch here is documented "run from the FACTORY ROOT" and resolves targets
    from Path.cwd(), so running it as `python patches\patch_x.py` from the
    root still works. A script that instead derives paths from its own
    location would break the moment it moved, so those are listed and left
    alone for you to look at.

    RUN THE AUDIT, READ IT, THEN APPLY. It is idempotent.
#>
[CmdletBinding()]
param([switch]$Apply)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\level_factory") -or -not (Test-Path ".\.git")) {
    Write-Host "run this from the factory root" -ForegroundColor Red
    exit 1
}

# --------------------------------------------------------------- rules ----
# Ordered. First match wins. Anything unmatched stays put.
$Rules = @(
    @{ Dest = "patches";       Match = { $_ -like "patch_*.py" -or $_ -like "unpatch_*.py" } }
    @{ Dest = "tools";         Match = { $_ -like "probe_*.py" -or $_ -like "library_*.py" `
                                        -or $_ -like "*_census.py" -or $_ -eq "module_extents.py" `
                                        -or $_ -eq "compare_candidates.py" -or $_ -eq "roadmap_status.py" `
                                        -or $_ -eq "factory_map.py" -or $_ -eq "verify_staging_identity.py" `
                                        -or $_ -eq "test_mirror_agreement.py" } }
    @{ Dest = "scripts";       Match = { $_ -like "*.ps1" -and $_ -ne "factory_tidy.ps1" } }
    @{ Dest = "docs\sessions"; Match = { $_ -like "SESSION_*.md" } }
    @{ Dest = "docs\findings"; Match = { $_ -in @("LADDER_INTO_SOLID_ROOF.md",
                                                  "LASERTAG_STAGES_A_STALE_SCENE.md",
                                                  "ITEM7_SOURCE_LIBRARY.md",
                                                  "ROADMAP_0809_ADDENDUM.md",
                                                  "GUARDRAILS_PLAN.md",
                                                  "NARRATIVE_SLATE.md") } }
    @{ Dest = "docs\diagrams"; Match = { $_ -like "*.svg" -or $_ -like "dag_*.png" `
                                        -or $_ -like "factory_for_*.png" -or $_ -like "levelfactory_*.png" } }
    @{ Dest = "_runs\measurements"; Match = { $_ -like "lt_*.json" -or $_ -like "lt_*.csv" `
                                        -or $_ -like "gp_*.json" -or $_ -like "shots_*.json" `
                                        -or $_ -eq "lux_applied.tscn" -or $_ -eq "probe_roof.glb" `
                                        -or $_ -eq "themed_fit.txt" -or $_ -eq "walkbot.before.json" } }
    @{ Dest = "_runs\attic";   Match = { $_ -like "*.pre_*" -or $_ -like "*.pending" } }
)

# Files that belong at the root and must never be filed away.
$Keep = @("README.md", "CLAUDE.md", "AGENT_CONTRACT.md", "CERTIFY.md",
          "CHANGELOG.md", "ENGINE_GATES.md", "NEXT.md", "PIPELINE_MAP.md",
          "PIPELINE_ROADMAP.md", "PACKAGE_README.md", "factory.manifest.json",
          ".gitignore", "factory_tidy.ps1")

# ------------------------------------------------------------- classify ----
$tracked = @{}
git ls-files | ForEach-Object { $tracked[$_] = $true }

$plan, $skipped, $unmatched = @(), @(), @()

foreach ($f in Get-ChildItem -File -Name) {
    if ($Keep -contains $f) { continue }
    $rule = $Rules | Where-Object { & $_.Match $f } | Select-Object -First 1
    if (-not $rule) { $unmatched += $f; continue }

    # A python script that resolves paths from its own location breaks when
    # moved. Ask the file, do not assume.
    if ($f -like "*.py" -and (Select-String -Path $f -Pattern '__file__' -Quiet)) {
        $skipped += [pscustomobject]@{ File = $f; Why = "uses __file__ -- would break if moved" }
        continue
    }
    $plan += [pscustomobject]@{
        File = $f; Dest = $rule.Dest; Tracked = [bool]$tracked[$f]
        Size = (Get-Item $f).Length
    }
}

# ---------------------------------------------------------------- report ----
Write-Host ""
Write-Host "loose files at the root: $((Get-ChildItem -File).Count)" -ForegroundColor Cyan
Write-Host ""
foreach ($g in $plan | Group-Object Dest | Sort-Object Name) {
    $mb = ($g.Group | Measure-Object Size -Sum).Sum / 1MB
    Write-Host ("  {0,-20} {1,3} file(s)  {2,6:N1} MB" -f $g.Name, $g.Count, $mb)
}
Write-Host ""
Write-Host ("  staying at the root:  {0}" -f ($Keep | Where-Object { Test-Path $_ }).Count)
if ($unmatched) {
    Write-Host ("  UNCLASSIFIED (left alone): {0}" -f $unmatched.Count) -ForegroundColor Yellow
    $unmatched | ForEach-Object { Write-Host "      $_" -ForegroundColor Yellow }
}
if ($skipped) {
    Write-Host ""
    Write-Host "  NOT MOVED -- would break:" -ForegroundColor Yellow
    $skipped | ForEach-Object { Write-Host ("      {0}  ({1})" -f $_.File, $_.Why) -ForegroundColor Yellow }
}

if (-not $Apply) {
    Write-Host ""
    Write-Host "dry run. Nothing moved. Re-run with -Apply to file them." -ForegroundColor Green
    exit 0
}

# ----------------------------------------------------------------- apply ----
Write-Host ""
foreach ($d in ($plan.Dest | Sort-Object -Unique)) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
}
$moved = 0
foreach ($p in $plan) {
    $target = Join-Path $p.Dest $p.File
    if (Test-Path $target) {
        Write-Host "  SKIP $($p.File) -- already at $target" -ForegroundColor Yellow
        continue
    }
    if ($p.Tracked) { git mv -- $p.File $target } else { Move-Item -- $p.File $target }
    if ($LASTEXITCODE -and $p.Tracked) {
        Write-Host "  git mv failed for $($p.File)" -ForegroundColor Red
    } else { $moved++ }
}
Write-Host ""
Write-Host "moved $moved file(s). Tracked ones went via git mv, so history follows." -ForegroundColor Green
Write-Host "Review with: git status --short" -ForegroundColor Green
Write-Host ""
Write-Host "_runs\ is already gitignored and already on factory_clean.ps1's" -ForegroundColor Green
Write-Host "allow-list, so the measurement scratch now gets swept for free." -ForegroundColor Green
