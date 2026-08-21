# ============================================================
#  commit_stale_tools.ps1 -- deli_counter 0.90.0, level_factory 0.47.0
#
#  Both have been sitting uncommitted since earlier in this project, and
#  neither pin can move in factory.manifest.json until they are tagged --
#  pinning a version whose tag does not exist is exactly the defect
#  laser_tag currently carries (pinned tag v0.8.0; the repo has only
#  v0.7.0 - v0.7.3).
#
#  Both CHANGELOGs already carry their entry, and `verify_manifest` cross-
#  checks VERSION against the newest CHANGELOG heading, so they must match:
#     deli_counter   VERSION 0.90.0  <->  ## [0.90.0]
#     level_factory  VERSION 0.47.0  <->  ## [0.47.0]
#
#  TESTS RUN FIRST. A failing suite aborts before anything is staged.
#
#  Run:
#    pwsh -ExecutionPolicy Bypass -File ...\commit_stale_tools.ps1 -Check
#    pwsh -ExecutionPolicy Bypass -File ...\commit_stale_tools.ps1
# ============================================================
param([switch]$Check, [switch]$SkipTests)

$ErrorActionPreference = "Stop"
$F = "C:\Projects\gabagool_studios\gabagool_factory"
$FORBIDDEN = '(^|/)(_preview[^/]*|_probe|_runs|_scratch|build|out)/'

$DC = @("CHANGELOG.md", "VERSION", "specs/CATALOG.md", "themed_tscn.py")
$LF = @("CHANGELOG.md", "VERSION",
        "packages/validation/glb_collision.py",
        "packages/exporting/glb_collision_flag.py",
        "tests/unit/test_glb_collision_flag.py")

$DCMsg = @'
deli_counter 0.90.0: the prop stem mirror gains depth and height

themed_tscn.module_stem mirrors zoo 0.39.0. A `prop` slot's stem now
carries `_d<cm>` and `_h<cm>`, because a prop is free on all three axes and
width alone named two different solids the same file.

Measured over 52 of 136 shipped manifests before the change: 15 buildings
(28%) and 48 of 1,486 modules were colliding. After it, 9,185/9,185 slots
agree across both mirrors and exactly 84 filenames change, all role=prop.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01EcV9Es5RCxEZyW87879Coj
'@

$LFMsg = @'
level_factory 0.47.0: flipping collision on a .glb is a rename

packages/exporting/glb_collision_flag.py -- set or clear the collision a
.glb generates in Godot, one policy per file. Godot decides from NODE
NAMES, so the operation is a rename inside the glTF JSON chunk, not a flag
anywhere.

Refuses to clear when a sibling .glb.import has generate/physics=true,
because the importer would put the collision back and the file would lie.
Every write is re-read through glb_collision.collision_solids before it is
accepted.

glb_collision.py gains a public strip_duplicate(name) -> (stem, tail), and
name_generates_collision is rewritten on top of it; the two were checked
for equivalence over 525 generated names.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01EcV9Es5RCxEZyW87879Coj
'@

$PLAN = @(
  @{ repo="deli_counter";  paths=$DC; msg=$DCMsg; tag="v0.90.0"; ver="0.90.0" },
  @{ repo="level_factory"; paths=$LF; msg=$LFMsg; tag="v0.47.0"; ver="0.47.0" }
)

# ---- refuse up front if a tag already exists -------------------------------
foreach ($s in $PLAN) {
  if (& git -C (Join-Path $F $s.repo) tag --list $s.tag) {
    throw ($s.repo + ": tag " + $s.tag + " already exists -- refusing")
  }
}

foreach ($s in $PLAN) {
  $dir = Join-Path $F $s.repo
  Write-Host ""
  Write-Host ("=== " + $s.repo)

  # VERSION vs newest CHANGELOG heading -- verify_manifest compares these two
  # and reports self_disagreement if they differ. Check it BEFORE committing,
  # not after the factory tag is on.
  $v = ((Get-Content (Join-Path $dir "VERSION") -Raw).Trim() -split '\s+')[-1]
  $head = (Select-String -Path (Join-Path $dir "CHANGELOG.md") `
           -Pattern '^##\s*\[?v?([0-9]+\.[0-9]+\.[0-9]+)\]?' |
           Select-Object -First 1)
  $doc = if ($head) { $head.Matches[0].Groups[1].Value } else { "(none)" }
  Write-Host ("  VERSION=" + $v + "   newest CHANGELOG=" + $doc)
  if ($v -ne $s.ver) { throw ($s.repo + ": VERSION is " + $v + ", expected " + $s.ver) }
  if ($doc -ne $s.ver) {
    throw ($s.repo + ": CHANGELOG newest entry is " + $doc + " but VERSION is " +
           $v + " -- verify_manifest would report self_disagreement")
  }

  $missing = $s.paths | Where-Object { -not (Test-Path (Join-Path $dir $_)) }
  if ($missing) {
    Write-Host "  MISSING ON DISK:"; $missing | ForEach-Object { Write-Host ("    " + $_) }
    throw ($s.repo + ": named path missing")
  }

  if ($Check) {
    Write-Host "  would commit:"
    Push-Location $dir
    & git status --short -- $s.paths | ForEach-Object { Write-Host ("    " + $_) }
    Write-Host ("  would tag: " + $s.tag)
    Write-Host "  NOT shown here, deliberately left out of the commit:"
    & git status --short | Where-Object { $_ -match $FORBIDDEN } |
        ForEach-Object { Write-Host ("    " + $_) }
    Pop-Location
    continue
  }

  if (-not $SkipTests) {
    Write-Host "  running tests..."
    Push-Location $dir
    & python -m pytest -q 2>&1 | Select-Object -Last 3 |
        ForEach-Object { Write-Host ("    " + $_) }
    $rc = $LASTEXITCODE
    Pop-Location
    if ($rc -ne 0) { throw ($s.repo + ": test suite failed (exit " + $rc + ") -- nothing committed") }
  }

  Push-Location $dir
  foreach ($rel in $s.paths) { & git add -- $rel }
  $staged = & git diff --cached --name-only
  $bad = $staged | Where-Object { $_ -match $FORBIDDEN }
  if ($bad) {
    Write-Host "  ABORT -- would have entered history:" -ForegroundColor Red
    $bad | ForEach-Object { Write-Host ("    " + $_) }
    & git reset --quiet; Pop-Location
    throw ($s.repo + ": forbidden paths staged")
  }
  Write-Host ("  staged " + ($staged | Measure-Object).Count + " file(s)")
  $staged | ForEach-Object { Write-Host ("    " + $_) }

  $tmp = Join-Path $env:TEMP ($s.repo + "_msg.txt")
  Set-Content -Path $tmp -Value $s.msg -Encoding utf8
  & git commit -F $tmp | Out-Null
  if ($LASTEXITCODE -ne 0) { Pop-Location; throw ($s.repo + ": commit failed -- NOT tagging") }
  & git tag -a $s.tag -m ($s.repo + " " + $s.tag)
  if ($LASTEXITCODE -ne 0) { Pop-Location; throw ($s.repo + ": tag failed") }
  Write-Host ("  committed " + (& git rev-parse --short HEAD) + "   tagged " + $s.tag)
  Pop-Location
}

Write-Host ""
if ($Check) {
  Write-Host "-Check: nothing staged, nothing written."
} else {
  Write-Host "Both tagged. factory.manifest.json can now pin:"
  Write-Host "  deli_counter 0.89.0 -> 0.90.0     level_factory 0.46.0 -> 0.47.0"
  Write-Host "  pixelcoat    0.12.0 -> 0.15.0     zoo           0.38.0 -> 0.44.0"
  Write-Host "laser_tag stays at 0.8.0 -- its pinned tag v0.8.0 does not exist."
}
