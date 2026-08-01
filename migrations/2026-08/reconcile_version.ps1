# reconcile_version.ps1
# Fix the version line after two chats collided on it:
#   aba3358 set VERSION 0.81.0 (fit-to-greybox)  ->  phase-1 reset it to 0.80.0
#   -> this repo drifted backwards to 0.80.1.
# This moves VERSION FORWARD to 0.82.0 (a clean minor above everything), adds a
# CHANGELOG entry that records the reconciliation, commits, tags v0.82.0, pushes.
# Pushed history is NOT rewritten and the mis-placed v0.80.0 tag is left as-is.
#
# Run:  powershell -ExecutionPolicy Bypass -File .\reconcile_version.ps1
# Add  -NoPush  to commit+tag without pushing.

param([switch]$NoPush)

$ErrorActionPreference = "Stop"
$repo = "C:\Projects\gabagool_studios\gabagool_factory\deli_counter"
Set-Location $repo

$target = "0.82.0"

# --- 1. set VERSION to the target (preserve any label prefix) ----------------
$verPath = Join-Path $repo "VERSION"
$cur = (Get-Content $verPath -Raw).Trim()
if ($cur -notmatch '\d+\.\d+\.\d+') { throw "can't find a semver in VERSION: '$cur'" }
$newLine = ($cur -replace '\d+\.\d+\.\d+', $target)
Set-Content $verPath $newLine -NoNewline
Write-Host "VERSION: '$cur' -> '$newLine'"

# --- 2. prepend a reconciliation CHANGELOG entry -----------------------------
$clPath = Join-Path $repo "CHANGELOG.md"
$entry = @"
## [$target] - Version-line reconciliation (two-chat collision)

Bookkeeping only -- no code change. The version line had regressed because two
work streams collided on it:

- ``aba3358`` set VERSION to 0.81.0 (fit-to-greybox placement + ground-truth gate).
- The phase-1 slice (``4c234a0``, ``d65e825``, "10 pvp_heist configs gated on
  Godot 4.7") then reset VERSION back to 0.80.0 and tagged v0.80.0 -- landing
  AFTER 0.81.0, so the number went backwards (0.81.0 -> 0.80.0 -> 0.80.1).

All that work is intact on ``main``; only the label regressed. This unifies the
line FORWARD to 0.82.0 -- above the 0.81.0 baseline, absorbing the phase-1
feature slice and the 0.80.1 gate-hardening. Pushed history is not rewritten and
the earlier v0.80.0 tag is left in place; a fresh v0.82.0 tag marks the true HEAD.

"@
if (Test-Path $clPath) {
    $old = Get-Content $clPath -Raw
    Set-Content $clPath ($entry + $old) -NoNewline
    Write-Host "CHANGELOG.md: prepended [$target] reconciliation entry"
} else {
    Set-Content $clPath $entry -NoNewline
}

# --- 3. commit ---------------------------------------------------------------
git add VERSION CHANGELOG.md
Write-Host "`n--- staged ---"
git status --short
git commit -m "deli_counter $($target): reconcile version line (0.81.0 + phase-1 unified forward)"
Write-Host "`n--- committed ---"
git log --oneline -1

# --- 4. tag ------------------------------------------------------------------
git tag -a "v$target" -m "deli_counter v$target"
Write-Host "tagged v$target"

# --- 5. push (commit + tag) --------------------------------------------------
if ($NoPush) {
    Write-Host "`n-NoPush set: committed + tagged locally, NOT pushed. Run 'git push ; git push origin v$target' when ready."
} else {
    git push
    git push origin "v$target"
    Write-Host "`npushed commit + tag v$target."
}
Write-Host "`nDone. VERSION is now $target and monotonic again; v$target tags true HEAD."
