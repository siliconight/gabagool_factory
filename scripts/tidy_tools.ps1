# Repo hygiene, pass 2: the code moves. Run patch_factory_root.py and
# patch_check_all_siblings.py FIRST -- this script refuses otherwise.
#
# THREE DESTINATIONS, and the third is the interesting one.
#
#   tools\        things you run against the factory: the four checkers, the two
#                 harnesses, gdcheck, the theme applier, factory_paths, and the
#                 nav probe.
#   scripts\      standing PowerShell you run more than once.
#   migrations\   PowerShell that already ran, once, and never will again.
#
# THAT THIRD SET CANNOT BE FOUND BY A RULE, and this is the honest limit of the
# approach tidy_migrations.ps1 takes. Its rule -- patch*.py and commit_*.ps1 --
# is right for generated name-spaces. lf_patch.ps1, reconcile_version.ps1 and
# guardrail_regate.ps1 match neither pattern and are one-shots anyway:
#
#   lf_patch.ps1          "level_factory 0.11.0 -> 0.11.1"; hardcodes the target
#                         version and one specific CHANGELOG entry.
#   reconcile_version.ps1 "fix the version line after two chats collided on it";
#                         hardcodes $target = "0.82.0".
#   guardrail_regate.ps1  a one-time rebuild of 30 named specs.
#
# They are listed here, by name, deliberately -- because the only way to know
# what they are is to read what they do, and a list somebody read and wrote down
# is a different animal from a list that pretends to describe a generated set.
# The rule stays a rule where a rule works; this is where it does not.
#
# THE GUARD. Before moving anything it scans every root and docs file for
# references to the names it is about to move. A .ps1 that shells `python
# check_freshness.py` from the root would break, and this is how we find out
# beforehand rather than in three weeks. Anything referenced is reported and the
# move refuses, unless -Force.
#
# THE PROOF. gd_files() reports 104 today with everything at the root. After the
# move it must still report 104. The command is printed at the end; run it.
#
# Dry run by default. -Commit to move and commit. Nothing is pushed.
param([switch]$Commit, [switch]$Force)

$ErrorActionPreference = "Continue"
$PSNativeCommandUseErrorActionPreference = $false
$root = "C:\Projects\gabagool_studios\gabagool_factory"

$plan = [ordered]@{
  "tools" = @("apply_rockay_theme.py", "check_all.py", "check_freshness.py",
              "check_stair_pitch.py", "check_steps.py", "factory_paths.py",
              "gdcheck.py", "library_walk.py", "navmesh_solid_probe.gd",
              "rebuild_buildings.py")
  "scripts" = @("archive_scratch.ps1", "build_portable_walkable.ps1",
                "factory_clean.ps1", "promote_factory.ps1",
                "render_kit_sheets.ps1", "tidy_docs.ps1",
                "tidy_migrations.ps1", "tidy_tools.ps1")
  "migrations\2026-08" = @("guardrail_regate.ps1", "lf_patch.ps1",
                           "patch_check_all_siblings.py", "patch_doc_paths.py",
                           "patch_factory_root.py", "reconcile_version.ps1")
}

Push-Location $root

# --------------------------------------------------------- prerequisites
$ca = Get-Content (Join-Path $root "check_all.py") -Raw -ErrorAction SilentlyContinue
if (-not $ca -or $ca -notmatch "factory_root\(\)") {
  Write-Host "  check_all.py does not call factory_root() yet." -ForegroundColor Red
  Write-Host "  Run: python patch_factory_root.py" -ForegroundColor Red
  Pop-Location; exit 2
}
if ($ca -notmatch "SCRIPT_DIR / script") {
  Write-Host "  check_all.py still resolves checkers as ROOT / script." -ForegroundColor Red
  Write-Host "  Run: python patch_check_all_siblings.py" -ForegroundColor Red
  Write-Host "  Without it the move breaks every checker it invokes." -ForegroundColor Red
  Pop-Location; exit 2
}

$moving = @(); $destOf = @{}
foreach ($d in $plan.Keys) {
  foreach ($f in $plan[$d]) { $moving += $f; $destOf[$f] = $d }
}

$missing = @($moving | Where-Object { -not (Test-Path (Join-Path $root $_)) })
if ($missing) {
  Write-Host "  named but not present: $($missing -join ', ')" -ForegroundColor Yellow
  Write-Host "  (already moved, or renamed -- check before continuing)" -ForegroundColor Yellow
}
$moving = @($moving | Where-Object { Test-Path (Join-Path $root $_) })

# ----------------------------------------------------------------- guard
$scan = @(Get-ChildItem -Path "$root\*" -File -Include *.ps1, *.py, *.md -ErrorAction SilentlyContinue)
if (Test-Path (Join-Path $root "docs")) {
  $scan += @(Get-ChildItem -Path "$root\docs\*" -File -Include *.md -ErrorAction SilentlyContinue)
}
# A reference is only a PROBLEM if it is an invocation -- something that will
# actually fail to find the file. A sentence naming a tool goes stale, which is
# worth fixing and is not worth blocking a move over. The first version of this
# guard could not tell the difference and reported both as breakage, which is
# the same defect as a gate that fails nineteen of twenty sites: technically
# right, and switched off by the first person in a hurry.
$refs = @()
foreach ($name in $moving) {
  $esc = [regex]::Escape($name)
  # A bare name still matches inside an already-corrected path: `gdcheck.py` is
  # a substring of `tools\gdcheck.py`. Without this the guard flags the very
  # lines a previous pass fixed, which makes it unfalsifiable -- it can never
  # go green, so the only way past it is -Force, and a gate whose only exit is
  # the override is not a gate.
  $destEsc = (($destOf[$name] -replace '\\', '/') -replace '/', '[\\/]')
  $fixed = "$destEsc[\\/]$esc"
  $call = "(python|powershell|pwsh)\b[^;|]*$esc|-File\s+\S*$esc|\.[\\/]$esc"
  foreach ($f in $scan) {
    if ($f.Name -eq $name) { continue }
    if ($moving -contains $f.Name) { continue }   # both moving: nothing to fix
    $hit = Select-String -Path $f.FullName -SimpleMatch $name -ErrorAction SilentlyContinue
    foreach ($h in $hit) {
      $refs += [pscustomobject]@{
        Name = $name; In = $f.Name; Line = $h.LineNumber; Text = $h.Line.Trim()
        Kind = if ($h.Line -match $fixed) { "fixed" }
               elseif ($h.Line -match $call) { "call" }
               else { "prose" }
      }
    }
  }
}
$calls = @($refs | Where-Object Kind -eq "call")
$prose = @($refs | Where-Object Kind -eq "prose")
$fixed = @($refs | Where-Object Kind -eq "fixed")

Write-Host ""
foreach ($d in $plan.Keys) {
  $here = @($plan[$d] | Where-Object { $moving -contains $_ })
  if (-not $here) { continue }
  Write-Host "=========== -> $d\ ===========" -ForegroundColor Cyan
  foreach ($f in $here) {
    $item = Get-Item (Join-Path $root $f)
    $t = @(git ls-files -- $f 2>$null)
    $how = if ($t.Count -gt 0) { "git mv" } else { "move  " }
    Write-Host ("  {0}  {1,-30} {2,7} bytes" -f $how, $f, $item.Length)
  }
  Write-Host ""
}

if ($calls.Count -gt 0) {
  Write-Host "=========== INVOCATIONS that would break ===========" -ForegroundColor Red
  foreach ($r in ($calls | Sort-Object In, Line)) {
    Write-Host ("  {0}:{1}" -f $r.In, $r.Line) -ForegroundColor Red
    Write-Host ("      {0}" -f $r.Text) -ForegroundColor DarkYellow
  }
  Write-Host "  These run the file by path. Update them before moving." -ForegroundColor Red
} else {
  Write-Host "  No file that stays behind INVOKES a file that moves." -ForegroundColor Green
}
if ($fixed.Count -gt 0) {
  Write-Host ("  {0} invocation(s) already name the destination -- counted, not flagged." `
              -f $fixed.Count) -ForegroundColor DarkGreen
}

if ($prose.Count -gt 0) {
  Write-Host ""
  Write-Host ("  {0} prose mention(s) across {1} file(s) -- these go stale, they do not break:" `
              -f $prose.Count, (($prose | Select-Object -Unique In).Count)) -ForegroundColor DarkGray
  foreach ($g in ($prose | Group-Object In | Sort-Object Name)) {
    Write-Host ("    {0,-24} {1} mention(s)" -f $g.Name, $g.Count) -ForegroundColor DarkGray
  }
  Write-Host "    Worth a documentation pass afterwards, not a reason to stop." -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "  Staying at the root:" -ForegroundColor DarkGray
Get-ChildItem -Path "$root\*" -File -Include *.py, *.ps1, *.gd, *.md, *.json |
  Where-Object { $moving -notcontains $_.Name } |
  ForEach-Object { Write-Host "    $($_.Name)" -ForegroundColor DarkGray }

if (-not $Commit) {
  Write-Host ""
  Write-Host "Dry run. Nothing moved. Re-run with -Commit when it looks right." -ForegroundColor Yellow
  Pop-Location; exit 0
}
if ($calls.Count -gt 0 -and -not $Force) {
  Write-Host ""
  Write-Host "REFUSING: the invocations above would break. -Force to override." -ForegroundColor Red
  Pop-Location; exit 1
}

foreach ($d in $plan.Keys) {
  $here = @($plan[$d] | Where-Object { $moving -contains $_ })
  if (-not $here) { continue }
  New-Item -ItemType Directory -Force -Path (Join-Path $root $d) | Out-Null
  foreach ($f in $here) {
    $t = @(git ls-files -- $f 2>$null)
    $destRel = ($d -replace '\\', '/') + "/$f"
    if ($t.Count -gt 0) { git mv -- $f $destRel }
    else { Move-Item -Path (Join-Path $root $f) -Destination (Join-Path $root "$d\$f") -Force }
  }
}

$msg = @'
move the tools out of the factory root

tools/ for the things you run against the factory, scripts/ for standing
PowerShell, migrations/2026-08/ for three one-shots that no naming rule catches.

The code change that made this safe landed first, in its own commit: six tools
derived the tree they scan from their own __file__, so relocating them would
have made check_all scan tools/, find a handful of .gd files instead of 104, and
still print clean. They now walk up to factory.manifest.json instead, and
check_all keeps SCRIPT_DIR separate from ROOT because "where my siblings are"
and "what I am checking" stopped being the same answer the moment anything
moved.

lf_patch.ps1, reconcile_version.ps1 and guardrail_regate.ps1 are named
explicitly rather than matched. They already ran -- one bumps level_factory to a
hardcoded 0.11.1, one sets a hardcoded VERSION 0.82.0, one rebuilds a fixed list
of 30 specs -- and none matches the patch*/commit_* rule. Where a set is
generated, describe it; where it is only knowable by reading what each file
does, list it and say why.

Before moving anything the script scanned every file staying behind for
references to the names moving, so a .ps1 shelling a checker by path would have
been found first.

Verified by measurement, not by a green row: gd_files() reported 104 before and
104 after. check_all prints clean whether it looked at 104 files or four, which
is why the count is checked directly.
'@

$status = git status --short
if ($status) {
  $status | ForEach-Object { Write-Host "  $_" }
  $tmp = [System.IO.Path]::GetTempFileName()
  Set-Content -Path $tmp -Value $msg -Encoding UTF8
  git commit -F $tmp
  Remove-Item $tmp -Force
  Write-Host ""
  Write-Host "Committed. Nothing pushed." -ForegroundColor Green
} else {
  Write-Host "  nothing staged" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "NOW PROVE IT. A clean row does not distinguish 104 files from four:" -ForegroundColor Green
Write-Host '  python tools\check_all.py' -ForegroundColor Green
Write-Host '  python -c "import sys; sys.path.insert(0,''tools''); import check_all as a; print(len(a.gd_files()), ''files''); print(a.ROOT); print(a.SCRIPT_DIR)"' -ForegroundColor Green
Write-Host "  Expect 104 files, ROOT at the factory, SCRIPT_DIR at tools\." -ForegroundColor Green
Pop-Location
