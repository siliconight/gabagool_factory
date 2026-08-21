# close_t3.ps1 -- runs as a child process. No `exit` anywhere, so a failing
# step reports and stops the sequence without touching the parent session.
$ErrorActionPreference = "Continue"
$PSNativeCommandUseErrorActionPreference = $false
$Factory = "C:\Projects\gabagool_studios\gabagool_factory"
Set-Location $Factory

$steps = @()
$halted = $false

function Step($label, $block) {
    if ($script:halted) {
        Write-Host ""
        Write-Host ("SKIPPED  {0}  (an earlier step failed)" -f $label)
        return
    }
    Write-Host ""
    Write-Host ("===== {0} =====" -f $label)
    & $block
    $rc = $LASTEXITCODE
    if ($null -eq $rc) { $rc = 0 }
    $script:steps += [pscustomobject]@{ Step = $label; Exit = $rc }
    if ($rc -ne 0) {
        Write-Host ""
        Write-Host ("FAILED   {0}  exit {1}  -- stopping here, nothing after this ran" -f $label, $rc)
        $script:halted = $true
    }
}

Step "apply"          { python patches\patch_thread3_close.py }
Step "selftest"       { python patches\patch_thread3_close.py --selftest }
Step "rebuild"        { & "$Factory\pixelcoat\tools\rebuild_theme_libraries.ps1" }
Step "stamp check"    { python patches\stamp_check.py }
Step "zoo suite"      { Push-Location "$Factory\zoo";       python -m pytest -q; Pop-Location }
Step "pixelcoat suite"{ Push-Location "$Factory\pixelcoat"; python -m pytest -q; Pop-Location }

Write-Host ""
Write-Host "===== SUMMARY ====="
$steps | Format-Table -AutoSize
if ($halted) {
    Write-Host "SEQUENCE HALTED -- see the FAILED line above."
} else {
    Write-Host "ALL STEPS GREEN."
}
