$PSNativeCommandUseErrorActionPreference = $false
$F = "C:\Projects\gabagool_studios\gabagool_factory"
$FORBIDDEN = '(^|/)(_preview[^/]*|_probe|_runs|_scratch|build|out)/|\.pre_[a-z0-9]+'
$halted = $false
function Step($label, $block) {
    if ($script:halted) { Write-Host ("SKIPPED  {0}" -f $label); return }
    Write-Host ""; Write-Host ("===== {0} =====" -f $label)
    & $block
    $rc = $LASTEXITCODE; if ($null -eq $rc) { $rc = 0 }
    if ($rc -ne 0) { Write-Host ("FAILED {0} exit {1}" -f $label, $rc); $script:halted = $true }
}

Set-Location $F
Step "deli_counter version + changelog" { python patches\patch_dc_092.py }
Step "deli_counter suite" { Push-Location "$F\deli_counter"; python -m pytest -q; Pop-Location }

if (-not $halted) {
    Write-Host ""; Write-Host "===== commit + tag deli_counter v0.92.0 ====="
    Push-Location "$F\deli_counter"
    $files = @("VERSION","CHANGELOG.md","navgate_baseline.json","test_navgate_population.py")
    & git reset *> $null
    & git add -- $files
    $staged = @(& git diff --cached --name-only)
    $bad = @($staged | Where-Object { $_ -match $FORBIDDEN })
    if ($bad.Count -gt 0) {
        Write-Host "REFUSE: forbidden paths staged:"; $bad | ForEach-Object { Write-Host "    $_" }
        & git reset *> $null; $halted = $true
    } elseif ($staged.Count -eq 0) { Write-Host "REFUSE: nothing staged"; $halted = $true }
    else {
        $staged | ForEach-Object { Write-Host "    $_" }
        & git commit -m "deli_counter 0.91.0 -> 0.92.0: freeze the nav-gate unjudged set" -m "17 shells report markers: 0 checked because no marker's type ends in _spawn, and the exit code is deliberately unchanged, so the set could grow silently. Frozen with a derived baseline and a sweep that fails on a new entrant and on a stale entry. Corrects a prior note: 3 of 135 is the FAILURE count not the pass count, and the unjudged set is 17 not 18, with five members never previously named."
        if ($LASTEXITCODE -ne 0) { Write-Host "REFUSE: commit failed"; $halted = $true }
        else {
            & git tag -a "v0.92.0" -m "deli_counter 0.92.0 -- nav-gate unjudged set frozen"
            if ($LASTEXITCODE -ne 0) { Write-Host "REFUSE: tag failed"; $halted = $true }
            else { Write-Host "TAGGED v0.92.0"; & git log -1 --oneline }
        }
    }
    Pop-Location
}

Set-Location $F
Step "manifest 1.34.0 check"    { python patches\patch_manifest_134.py --check }
Step "manifest 1.34.0 apply"    { python patches\patch_manifest_134.py }
Step "manifest 1.34.0 selftest" { python patches\patch_manifest_134.py --selftest }

if (-not $halted) {
    Write-Host ""; Write-Host "===== factory-v1.34.0 ====="
    Set-Location $F
    & git rev-parse -q --verify "refs/tags/factory-v1.34.0" *> $null
    if ($LASTEXITCODE -eq 0) { Write-Host "REFUSE: tag exists"; $halted = $true }
    else {
        $pf = @(Get-ChildItem -Path (Join-Path $F "patches") -File |
                Where-Object { $_.Extension -in ".py",".ps1" } |
                ForEach-Object { "patches/" + $_.Name })
        $all = @("factory.manifest.json") + $pf
        & git reset *> $null
        & git add -- $all
        $staged = @(& git diff --cached --name-only)
        $bad = @($staged | Where-Object { $_ -match $FORBIDDEN })
        if ($bad.Count -gt 0) {
            Write-Host "REFUSE: forbidden paths staged:"; $bad | ForEach-Object { Write-Host "    $_" }
            & git reset *> $null; $halted = $true
        } else {
            Write-Host ("staging {0} file(s)" -f $staged.Count)
            & git commit -m "factory 1.34.0 -- pin deli_counter 0.92.0" -m "Freezes the nav-gate unjudged set. Corrects a figure carried forward as 'the nav-gate passing 3 of 135' -- 3 of 135 is the failure count; 132 shells pass. The three stair failures are recorded, not fixed."
            if ($LASTEXITCODE -ne 0) { Write-Host "REFUSE: commit failed"; $halted = $true }
            else {
                & git tag -a "factory-v1.34.0" -m "factory 1.34.0 -- deli_counter 0.92.0, zoo 0.47.0, pixelcoat 0.16.0"
                if ($LASTEXITCODE -ne 0) { Write-Host "REFUSE: tag failed"; $halted = $true }
                else { Write-Host "TAGGED factory-v1.34.0"; & git show -s --oneline --stat HEAD }
            }
        }
    }
}

Write-Host ""
if ($halted) { Write-Host "HALTED -- see the REFUSE/FAILED line above." } else { Write-Host "THREAD 4 CLOSED." }
