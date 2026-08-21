# ============================================================
#  tag_factory_131.ps1 -- the factory commit + factory-v1.31.0
#
#  Runs LAST. Everything it certifies is already committed and tagged in
#  its own repository, and verify-manifest reports OK for all ten.
#
#  Explicitly excludes the .pre_manifest131 sidecar -- that is the patch's
#  revert copy, not content.
#
#  Run:
#    pwsh -ExecutionPolicy Bypass -File ...\tag_factory_131.ps1 -Check
#    pwsh -ExecutionPolicy Bypass -File ...\tag_factory_131.ps1
# ============================================================
param([switch]$Check)

$ErrorActionPreference = "Stop"
$F = "C:\Projects\gabagool_studios\gabagool_factory"
$TAG = "factory-v1.31.0"
$FORBIDDEN = '(^|/)(_preview[^/]*|_probe|_runs|_scratch|build|out)/|\.pre_[a-z0-9]+$'

$PATHS = @(
  "factory.manifest.json",
  "patches/commit_stale_tools.ps1",
  "patches/commit_stale_tools2.ps1",
  "patches/patch_manifest_131.py",
  "patches/patch_m.json",
  "patches/tag_factory_131.ps1"
)

Push-Location $F

if (& git tag --list $TAG) { Pop-Location; throw "$TAG already exists -- refusing" }

# the manifest must actually say 1.31.0 before a tag claims it does
$fv = (Get-Content "factory.manifest.json" -Raw | ConvertFrom-Json).factory_version
Write-Host ("factory_version in the manifest: " + $fv)
if ($fv -ne "1.31.0") { Pop-Location; throw "manifest says $fv, not 1.31.0 -- run patch_manifest_131.py first" }

if ($Check) {
  Write-Host "would commit:"
  & git status --short -- $PATHS | ForEach-Object { Write-Host ("  " + $_) }
  Write-Host ("would tag: " + $TAG)
  Write-Host ""
  Write-Host "deliberately NOT committed:"
  & git status --short | Where-Object { $_ -match $FORBIDDEN } |
      ForEach-Object { Write-Host ("  " + $_) }
  Pop-Location
  Write-Host ""
  Write-Host "-Check: nothing staged, nothing written."
  exit 0
}

foreach ($rel in $PATHS) { if (Test-Path $rel) { & git add -- $rel } }
$staged = & git diff --cached --name-only
$bad = $staged | Where-Object { $_ -match $FORBIDDEN }
if ($bad) {
  $bad | ForEach-Object { Write-Host ("  FORBIDDEN " + $_) -ForegroundColor Red }
  & git reset --quiet; Pop-Location
  throw "forbidden paths staged"
}
Write-Host ("staged " + ($staged | Measure-Object).Count + " file(s)")
$staged | ForEach-Object { Write-Host ("  " + $_) }

$msg = @'
factory 1.31.0: the tintable-pack set

Re-pins four tools, each already committed and tagged in its own
repository before this pin was written:

    deli_counter  0.89.0 -> 0.90.0   v0.90.0  7121245
    level_factory 0.46.0 -> 0.47.0   v0.47.0  3076689
    pixelcoat     0.12.0 -> 0.15.0   v0.15.0  bd48df5
    zoo           0.38.0 -> 0.44.0   v0.44.0  5e6237c

verify-manifest reports OK for all ten.

WHAT THIS SET DOES NOT CERTIFY, and the description says it first: no
end-to-end chain ran. Every previous entry is backed by a mission run;
this one is backed by four suites green in isolation plus one measured
zoo/pixelcoat interop -- a delco theme library built through Pixelcoat and
resolved back through zoo.skins.find_pack. That proves the two tools agree
about packs. It does not prove the pipeline still produces a level. The
prop modules have also not been rebuilt since the 0.90.0 stem change
renamed 84 role=prop files, which is the first thing the next chain run
has to do.

AND ONE PIN THIS SET DOES NOT RECONCILE: laser_tag is pinned tag v0.8.0
and that tag does not exist -- the repository holds only v0.7.0 through
v0.7.3. Recorded rather than resolved, because creating the tag is a claim
about when 0.8.0 shipped and correcting the pin down contradicts
lasertag's own VERSION file.

The manifest patch now resolves EVERY pinned tag, not only the four it
writes, inside each tool's own repository. That audit is how the laser_tag
finding was produced rather than inherited; verify_manifest itself compares
the pin, the installed VERSION and the newest CHANGELOG heading, and never
reads the tag field at all.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01EcV9Es5RCxEZyW87879Coj
'@

$tmp = Join-Path $env:TEMP "factory131_msg.txt"
Set-Content -Path $tmp -Value $msg -Encoding utf8
& git commit -F $tmp | Out-Null
if ($LASTEXITCODE -ne 0) { Pop-Location; throw "commit failed -- NOT tagging" }
& git tag -a $TAG -m "factory 1.31.0 -- the tintable-pack set"
if ($LASTEXITCODE -ne 0) { Pop-Location; throw "commit OK but tag failed" }
Write-Host ("committed " + (& git rev-parse --short HEAD) + "   tagged " + $TAG)
Pop-Location
