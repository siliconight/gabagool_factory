$PSNativeCommandUseErrorActionPreference = $false
$F = "C:\Projects\gabagool_studios\gabagool_factory"
$FORBIDDEN = '(^|/)(_preview[^/]*|_probe|_runs|_scratch|build|out)/|\.pre_[a-z0-9]+'
$halted = $false

function Commit-Repo($repo, $files, $msg, $tag) {
    if ($script:halted) { Write-Host "SKIPPED $repo"; return }
    $dir = Join-Path $F $repo
    Write-Host ""
    Write-Host ("===== {0} =====" -f $repo)
    Push-Location $dir

    if ($tag) {
        & git rev-parse -q --verify ("refs/tags/" + $tag) *> $null
        if ($LASTEXITCODE -eq 0) {
            Write-Host ("REFUSE: tag {0} already exists" -f $tag)
            $script:halted = $true; Pop-Location; return
        }
    }
    foreach ($f in $files) {
        if ($f -match $FORBIDDEN) {
            Write-Host ("REFUSE: forbidden path {0}" -f $f)
            $script:halted = $true; Pop-Location; return
        }
        if (-not (Test-Path -LiteralPath (Join-Path $dir $f))) {
            Write-Host ("REFUSE: missing {0}" -f $f)
            $script:halted = $true; Pop-Location; return
        }
    }
    & git reset *> $null
    & git add -- $files
    if ($LASTEXITCODE -ne 0) { Write-Host "REFUSE: git add failed"; $script:halted = $true; Pop-Location; return }

    $staged = @(& git diff --cached --name-only)
    $bad = @($staged | Where-Object { $_ -match $FORBIDDEN })
    if ($bad.Count -gt 0) {
        Write-Host "REFUSE: forbidden paths reached the index:"
        $bad | ForEach-Object { Write-Host ("    {0}" -f $_) }
        & git reset *> $null
        $script:halted = $true; Pop-Location; return
    }
    if ($staged.Count -eq 0) { Write-Host "nothing staged, skipping"; Pop-Location; return }
    Write-Host ("staging {0} file(s)" -f $staged.Count)
    $staged | ForEach-Object { Write-Host ("    {0}" -f $_) }

    & git commit -m $msg
    if ($LASTEXITCODE -ne 0) { Write-Host "REFUSE: commit failed"; $script:halted = $true; Pop-Location; return }
    if ($tag) {
        & git tag -a $tag -m $msg
        if ($LASTEXITCODE -ne 0) { Write-Host "REFUSE: tag failed"; $script:halted = $true; Pop-Location; return }
        Write-Host ("TAGGED {0}" -f $tag)
    }
    & git log -1 --oneline
    Pop-Location
}

$pcFiles = @(
    "CHANGELOG.md", "VERSION", "pixelcoat/version.py",
    "profiles/materials/pebble_gravel.json",
    "profiles/materials/carbon_neutral.json",
    "profiles/materials/laminate_neutral.json",
    "profiles/materials/paper_neutral.json",
    "profiles/materials/tar_neutral.json",
    "profiles/materials/vegetation_neutral.json",
    "profiles/themes/bank.json", "profiles/themes/casino.json",
    "profiles/themes/delco.json", "profiles/themes/rockay.json",
    "profiles/themes/rockay_civic.json", "profiles/themes/rockay_retail.json",
    "profiles/themes/rockay_service.json", "profiles/themes/stadium.json",
    "profiles/themes/street.json"
)
Commit-Repo "pixelcoat" $pcFiles `
    "pixelcoat 0.15.0 -> 0.16.0: five grammars for unmapped kinds, gravel retag, ten kinds wired into all nine themes" `
    "v0.16.0"

$zooFiles = @("CHANGELOG.md", "VERSION", "tests/test_recipe_reads_its_genome.py")
Commit-Repo "zoo" $zooFiles `
    "zoo 0.46.0 -> 0.47.0: a test that fails when a recipe ignores its genome" `
    "v0.47.0"

# factory: patch scripts only, non-recursive so patches/_probe is never seen
Push-Location $F
$patchFiles = @(Get-ChildItem -Path (Join-Path $F "patches") -File |
    Where-Object { $_.Extension -in ".py", ".ps1" } |
    ForEach-Object { "patches/" + $_.Name })
Pop-Location
Commit-Repo "." $patchFiles `
    "thread 3: probes and patches for the ten unmapped material kinds" `
    $null

Write-Host ""
if ($halted) { Write-Host "HALTED -- see the REFUSE line above." }
else { Write-Host "COMMITS DONE." }
