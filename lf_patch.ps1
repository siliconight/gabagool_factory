# ============================================================================
#  lf_patch.ps1  --  level_factory 0.11.0 -> 0.11.1 (fast-suite stub fix)
#  The fixed pixelcoat stub is already written to tests/fixtures/... by the
#  bridge; this bumps VERSION, prepends the CHANGELOG, and commits + tags.
#  Run:  powershell -ExecutionPolicy Bypass -File .\lf_patch.ps1
# ============================================================================
$ErrorActionPreference = "Stop"
$lf = "C:\Projects\gabagool_studios\gabagool_factory\level_factory"
$enc = New-Object System.Text.UTF8Encoding($false)

# 1. VERSION 0.11.0 -> 0.11.1
[System.IO.File]::WriteAllText((Join-Path $lf "VERSION"), "0.11.1`n", $enc)

# 2. Prepend CHANGELOG entry (fresh read on this machine).
$entry = @'
## [0.11.1] - Fast-suite pixelcoat stub learns theme-library

- `tests/fixtures/repos/pixelcoat/pixelcoat/cli/main.py`: the stub CLI now
  implements `theme-library --theme <t> --out <dir>` (the command 0.11.0's
  adapter change started issuing), emitting one resolvable `<kind>_<theme>/`
  pack per curated kind with its maps written alongside. Without it the
  fast-suite presentation pipeline blocked at `pixelcoat_build` (exit 3),
  cascading into 8 service/integration failures. Production code is unchanged
  -- this realigns the test double with the 0.11.0 pixelcoat-stage contract.
'@
$clog = Join-Path $lf "CHANGELOG.md"
$raw = [System.IO.File]::ReadAllText($clog)
$idx = $raw.IndexOf("## [")
if ($idx -lt 0) { throw "no '## [' marker in $clog" }
$updated = $raw.Substring(0, $idx) + $entry.TrimEnd() + "`n`n" + $raw.Substring($idx)
[System.IO.File]::WriteAllText($clog, ($updated -replace "`r`n", "`n"), $enc)
Write-Host "VERSION=0.11.1, CHANGELOG prepended" -ForegroundColor Green

# 3. Commit + tag (no push).
git -C $lf add -A
git -C $lf commit -m "0.11.1: fast-suite pixelcoat stub learns theme-library (realigns test double with the 0.11.0 stage contract; fixes 8 presentation/service tests)" | Out-Host
git -C $lf tag -a v0.11.1 -m "v0.11.1" | Out-Host
Write-Host "tagged v0.11.1 @ $(git -C $lf log -1 --oneline)" -ForegroundColor Green
Write-Host "Push later with: git -C `"$lf`" push origin main --follow-tags" -ForegroundColor Yellow
