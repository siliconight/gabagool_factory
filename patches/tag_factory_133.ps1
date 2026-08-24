$PSNativeCommandUseErrorActionPreference = $false
$F = "C:\Projects\gabagool_studios\gabagool_factory"
Set-Location $F

$EXPECT    = "1.33.0"
$TAG       = "factory-v1.33.0"
$FORBIDDEN = '(^|/)(_preview[^/]*|_probe|_runs|_scratch|build|out)/|\.pre_[a-z0-9]+'
$FILES     = @(
    "factory.manifest.json",
    "patches/patch_manifest_133.py",
    "patches/manifest_shape.py",
    "patches/fix_changelog_53.py"
)

# the manifest asserts the version; this script only agrees or refuses
$m = Get-Content "factory.manifest.json" -Raw | ConvertFrom-Json
if ($m.factory_version -ne $EXPECT) {
    Write-Host ("REFUSE: manifest says {0}, expected {1}" -f $m.factory_version, $EXPECT)
    return
}
& git rev-parse -q --verify ("refs/tags/" + $TAG) *> $null
if ($LASTEXITCODE -eq 0) { Write-Host ("REFUSE: {0} already exists" -f $TAG); return }

foreach ($f in $FILES) {
    if ($f -match $FORBIDDEN) { Write-Host ("REFUSE: forbidden path {0}" -f $f); return }
    if (-not (Test-Path -LiteralPath $f)) { Write-Host ("REFUSE: missing {0}" -f $f); return }
}

& git reset *> $null
& git add -- $FILES
if ($LASTEXITCODE -ne 0) { Write-Host "REFUSE: git add failed"; return }

$staged = @(& git diff --cached --name-only)
$bad = @($staged | Where-Object { $_ -match $FORBIDDEN })
if ($bad.Count -gt 0) {
    Write-Host "REFUSE: forbidden paths in the index:"
    $bad | ForEach-Object { Write-Host ("    {0}" -f $_) }
    & git reset *> $null
    return
}
if ($staged.Count -eq 0) { Write-Host "REFUSE: nothing staged"; return }
Write-Host "staging:"
$staged | ForEach-Object { Write-Host ("    {0}" -f $_) }

& git commit -m "factory 1.33.0 -- pin pixelcoat 0.16.0 and zoo 0.47.0" `
             -m "Ten material kinds that no theme mapped are now built and resolvable. Records two corrections rather than burying them: six of seven suspected shadow literals were false positives (the body already read plan[material] and the literal was a sub-part), and the zoo 0.45.0 claim that all 53 genomes round-trip is 49 of 53. Still no end-to-end chain, export still blocked on collision_fingerprint, laser_tag still pins a v0.8.0 that does not exist."
if ($LASTEXITCODE -ne 0) { Write-Host "REFUSE: commit failed"; return }

& git tag -a $TAG -m "factory 1.33.0 -- pixelcoat 0.16.0, zoo 0.47.0, deli_counter 0.91.0, level_factory 0.47.0"
if ($LASTEXITCODE -ne 0) { Write-Host "REFUSE: tag failed"; return }
& git rev-parse -q --verify ("refs/tags/" + $TAG) *> $null
if ($LASTEXITCODE -ne 0) { Write-Host "REFUSE: tag did not land"; return }

Write-Host ""
Write-Host ("TAGGED {0}" -f $TAG)
& git show -s --oneline --stat HEAD
