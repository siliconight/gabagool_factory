$PSNativeCommandUseErrorActionPreference = $false
$F = "C:\Projects\gabagool_studios\gabagool_factory"
$MARK = "The 0.45.0 entry states that with"
$halted = $false

# ---------- 1. amend zoo and move v0.47.0 ----------
Write-Host "===== zoo: amend and move v0.47.0 ====="
Push-Location "$F\zoo"

$old = (& git rev-parse HEAD).Trim()
Write-Host ("  current HEAD {0}" -f $old.Substring(0,7))

& git reset *> $null
& git add -- "CHANGELOG.md"
$staged = @(& git diff --cached --name-only)
if ($staged.Count -ne 1 -or $staged[0] -ne "CHANGELOG.md") {
    Write-Host "REFUSE: expected exactly CHANGELOG.md staged, got:"
    $staged | ForEach-Object { Write-Host ("    {0}" -f $_) }
    & git reset *> $null
    $halted = $true
}

if (-not $halted) {
    & git commit --amend --no-edit
    if ($LASTEXITCODE -ne 0) { Write-Host "REFUSE: amend failed"; $halted = $true }
}
if (-not $halted) {
    $new = (& git rev-parse HEAD).Trim()
    if ($new -eq $old) { Write-Host "REFUSE: HEAD did not change"; $halted = $true }
    else { Write-Host ("  amended  {0} -> {1}" -f $old.Substring(0,7), $new.Substring(0,7)) }
}
if (-not $halted) {
    & git tag -f -a "v0.47.0" -m "zoo 0.46.0 -> 0.47.0: a test that fails when a recipe ignores its genome"
    if ($LASTEXITCODE -ne 0) { Write-Host "REFUSE: retag failed"; $halted = $true }
}
if (-not $halted) {
    $tagged = (& git rev-parse "v0.47.0^{commit}").Trim()
    $head   = (& git rev-parse HEAD).Trim()
    if ($tagged -ne $head) {
        Write-Host ("REFUSE: v0.47.0 points at {0}, HEAD is {1}" -f $tagged.Substring(0,7), $head.Substring(0,7))
        $halted = $true
    } else {
        $hit = & git show "v0.47.0:CHANGELOG.md" | Select-String -SimpleMatch $MARK
        if ($hit) { Write-Host "  VERIFIED: the correction is now inside v0.47.0" }
        else { Write-Host "REFUSE: v0.47.0 still lacks the correction"; $halted = $true }
    }
}
& git log -1 --oneline
Pop-Location

# ---------- 2. re-verify the manifest ----------
if (-not $halted) {
    Write-Host ""
    Write-Host "===== manifest selftest (it resolves tags, which just moved) ====="
    Set-Location $F
    & python patches\patch_manifest_133.py --selftest
    if ($LASTEXITCODE -ne 0) { Write-Host "REFUSE: manifest selftest failed"; $halted = $true }
}

# ---------- 3. tag the factory ----------
if (-not $halted) {
    Write-Host ""
    Write-Host "===== factory-v1.33.0 ====="
    Set-Location $F
    & "$F\patches\tag_factory_133.ps1"
}

Write-Host ""
if ($halted) { Write-Host "HALTED -- see the REFUSE line above." }
else { Write-Host "DONE." }
