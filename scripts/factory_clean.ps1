<#
  Audit / clean regenerable build, preview, and cache artifacts across the whole
  gabagool_factory. Dry-run by default.

  Scans a curated allow-list of artifact directories and junk file patterns
  (see $DirNames / $DirLike / $FileLike). Within those, it deletes a file ONLY
  if git does not track it (checked per-repo via git ls-files). Tracked
  traceability artifacts -- e.g. deli_counter build/*.manifest.json and the
  committed .gameplay/.slots/.lights JSON -- are therefore NEVER removed. It
  never deletes source and never touches local config such as tools.local.json
  or .env. Safer than "git clean -xfd", which also wipes ignored-but-precious
  local config, and safer than blanket directory removal, which was deleting
  tracked build artifacts.

  Requires git on PATH: the tracked-file guard depends on it, so the script
  refuses to run if git is unavailable.

  Usage:
    powershell -ExecutionPolicy Bypass -File factory_clean.ps1          # audit
    powershell -ExecutionPolicy Bypass -File factory_clean.ps1 -Apply   # delete
#>
param(
  [string]$Root = "C:\Projects\gabagool_studios\gabagool_factory",
  [switch]$Apply
)

$DirNames = @('__pycache__','.pytest_cache','.mypy_cache','.ruff_cache',
              '.ipynb_checkpoints','build','dist','exhibits',
              '_preview','_skins','_runs','_out','.godot')
$DirLike  = @('*.egg-info')
$FileLike = @('*.pyc','*.pyo','*.tmp','*.blend1')

if (-not (Test-Path $Root)) { Write-Error "Root not found: $Root"; exit 1 }

$null = & git --version 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Error "git not found on PATH; refusing to run (the tracked-file guard needs it)."
  exit 1
}

function ToolOf($path) {
  $rel = $path.Substring($Root.Length).TrimStart('\')
  $seg = $rel.Split('\')[0]
  if ($seg) { return $seg }
  return '(root)'
}

function RepoOf($path) {
  $rel = $path.Substring($Root.Length).TrimStart('\')
  $seg = $rel.Split('\')[0]
  $cand = Join-Path $Root $seg
  if ($seg -and (Test-Path -LiteralPath (Join-Path $cand '.git'))) { return $cand }
  return $Root
}

$trackedCache = @{}
function TrackedSet($repo) {
  if ($trackedCache.ContainsKey($repo)) { return $trackedCache[$repo] }
  $set = New-Object 'System.Collections.Generic.HashSet[string]'
  if (Test-Path -LiteralPath (Join-Path $repo '.git')) {
    $out = & git -C $repo ls-files 2>$null
    foreach ($line in $out) {
      if ($line) { [void]$set.Add($line.Replace('/','\').ToLowerInvariant()) }
    }
  }
  $trackedCache[$repo] = $set
  return $set
}

function IsTracked($file) {
  $repo = RepoOf $file
  $rel  = $file.Substring($repo.Length).TrimStart('\').Replace('/','\').ToLowerInvariant()
  return (TrackedSet $repo).Contains($rel)
}

function SizeMB($p) {
  $i = Get-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue
  if (-not $i) { return 0.0 }
  $b = $i.Length
  if (-not $b) { $b = 0 }
  return [math]::Round(($b / 1MB), 2)
}

$modeText = 'DRY RUN (no changes)'
if ($Apply) { $modeText = 'APPLY (delete)' }
Write-Host "Factory: $Root"
Write-Host "Mode:    $modeText"
Write-Host ('=' * 78)

# 1. Candidate artifact directories (skip anything under .git).
$artDirs = New-Object System.Collections.Generic.List[string]
Get-ChildItem -LiteralPath $Root -Recurse -Directory -Force -ErrorAction SilentlyContinue | ForEach-Object {
  if ($_.FullName -match '\\\.git(\\|$)') { return }
  $hit = $DirNames -contains $_.Name
  if (-not $hit) { foreach ($g in $DirLike) { if ($_.Name -like $g) { $hit = $true; break } } }
  if ($hit) { $artDirs.Add($_.FullName) }
}

# 2. Candidate files: everything under an artifact dir, plus loose junk patterns.
$cand = New-Object System.Collections.Generic.List[string]
foreach ($d in $artDirs) {
  Get-ChildItem -LiteralPath $d -Recurse -File -Force -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.FullName -notmatch '\\\.git(\\|$)') { $cand.Add($_.FullName) }
  }
}
foreach ($g in $FileLike) {
  Get-ChildItem -LiteralPath $Root -Recurse -File -Force -Filter $g -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.FullName -notmatch '\\\.git(\\|$)') { $cand.Add($_.FullName) }
  }
}

# 3. Split candidates: delete only what git does NOT track.
$del = New-Object System.Collections.Generic.List[string]
$keptTracked = 0
foreach ($f in $cand) {
  if (IsTracked $f) { $keptTracked++ } else { $del.Add($f) }
}

# 4. Report grouped by tool.
$rows = @()
foreach ($f in $del) { $rows += [pscustomobject]@{ Tool = (ToolOf $f); MB = (SizeMB $f); Path = $f } }

$total = 0.0
foreach ($grp in ($rows | Group-Object Tool | Sort-Object Name)) {
  $sub = ($grp.Group | Measure-Object -Property MB -Sum).Sum
  $total = $total + $sub
  Write-Host ''
  Write-Host ("[{0}]  {1:N1} MB reclaimable  ({2} files)" -f $grp.Name, $sub, $grp.Group.Count)
  $shown = $grp.Group | Sort-Object MB -Descending | Select-Object -First 10
  foreach ($r in $shown) {
    $rel = $r.Path.Substring($Root.Length).TrimStart('\')
    Write-Host ("  {0,9:N2} MB  {1}" -f $r.MB, $rel)
  }
  if ($grp.Group.Count -gt 10) { Write-Host ("  ... +{0} more" -f ($grp.Group.Count - 10)) }
}

Write-Host ''
Write-Host ('=' * 78)
Write-Host ("TOTAL reclaimable: {0:N1} MB across {1} files" -f $total, $del.Count)
Write-Host ("Protected (git-tracked, skipped): {0} files" -f $keptTracked)

if ($Apply) {
  foreach ($f in $del) {
    if (Test-Path -LiteralPath $f) { Remove-Item -LiteralPath $f -Force -ErrorAction SilentlyContinue }
  }
  # Prune now-empty artifact dirs (deepest first).
  $byDepth = $artDirs | Sort-Object { ($_ -split '\\').Count } -Descending
  foreach ($d in $byDepth) {
    if (Test-Path -LiteralPath $d) {
      $left = Get-ChildItem -LiteralPath $d -Recurse -Force -ErrorAction SilentlyContinue | Select-Object -First 1
      if (-not $left) { Remove-Item -LiteralPath $d -Force -ErrorAction SilentlyContinue }
    }
  }
  Write-Host ("Removed about {0:N1} MB. Tracked files were left untouched." -f $total)
} else {
  Write-Host "Dry run - nothing deleted. Re-run with -Apply to remove the above."
}
