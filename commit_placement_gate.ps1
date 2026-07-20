# commit_placement_gate.ps1
# Locks in the fit-to-greybox placement + ground-truth gate as deli_counter 0.81.0.
# Reads the REAL files on disk (not any staged snapshot), bumps VERSION by minor,
# prepends a CHANGELOG entry, stages the changed files, commits, and pushes.
#
# Run from anywhere:  powershell -ExecutionPolicy Bypass -File .\commit_placement_gate.ps1
# Add  -NoPush  to commit without pushing.

param([switch]$NoPush)

$ErrorActionPreference = "Stop"
$repo = "C:\Projects\gabagool_studios\gabagool_factory\deli_counter"
Set-Location $repo

# --- 1. bump VERSION (parse current, bump MINOR, reset patch) ----------------
$verPath = Join-Path $repo "VERSION"
$cur = (Get-Content $verPath -Raw).Trim()
if ($cur -notmatch '(\d+)\.(\d+)\.(\d+)') { throw "can't parse VERSION: '$cur'" }
$maj = [int]$Matches[1]; $min = [int]$Matches[2]
$new = "$maj.$($min + 1).0"
$newLine = ($cur -replace '\d+\.\d+\.\d+', $new)
Set-Content $verPath $newLine -NoNewline
Write-Host "VERSION: '$cur' -> '$newLine'"

# --- 2. prepend CHANGELOG entry ----------------------------------------------
$clPath = Join-Path $repo "CHANGELOG.md"
$entry = @"
## [$new] - Placement rides the shell's truth (fit-to-greybox gate)

Themed art now ORIENTS to the greybox collision instead of trusting a dims
convention -- and a build-time gate proves it, so a mis-placed module fails the
build instead of shipping.

- **Fit-to-greybox placement (tscn_export.godot_basis + themed_tscn).** Each
  themed module is oriented by fitting its footprint to the greybox slot's
  extent (the shell is ground truth). Walls -- already world-oriented by the
  greyboxer -- fall out to 0 deg; canonical openings to 90/270. Nothing is
  hard-coded, so it stays correct on future buildings by construction. Fixes
  the E/W openings that double-rotated under the old rot_y convention.
- **Ground-truth placement gate (portable_building.verify_placement).** Every
  build compares each themed module's placed footprint to its greybox slot's
  and fails on mismatch -- the durable guard against visuals that don't sit on
  the collision. Horizontal footprint is the hard invariant; module height is
  reported as an advisory (some zoo opening modules are authored taller than
  the greybox frame -- an authoring gap, not a placement error).
- **Portable closure hardened.** Greybox-fallback slots (no themed module for
  that width in the kit) keep their geometry in the base shell instead of
  emitting an unbundled external ref -- the package stays self-contained
  (PORTABLE=True) and fully visible even with a partial kit.

Validated end-to-end on gas_street: 73/73 footprint match, PORTABLE=True,
walkable=True, 7 opening-height items flagged advisory.

"@
if (Test-Path $clPath) {
    $old = Get-Content $clPath -Raw
    Set-Content $clPath ($entry + $old) -NoNewline
    Write-Host "CHANGELOG.md: prepended [$new] entry"
} else {
    Set-Content $clPath $entry -NoNewline
    Write-Host "CHANGELOG.md: created with [$new] entry"
}

# --- 3. stage + commit -------------------------------------------------------
git add tscn_export.py themed_tscn.py portable_building.py VERSION CHANGELOG.md
Write-Host "`n--- staged ---"
git status --short

$msg = "deli_counter $($new): fit-to-greybox placement + ground-truth gate"
git commit -m $msg
Write-Host "`n--- committed ---"
git log --oneline -1

# --- 4. push -----------------------------------------------------------------
if ($NoPush) {
    Write-Host "`n-NoPush set: committed but NOT pushed. Run 'git push' when ready."
} else {
    git push
    Write-Host "`npushed."
}
Write-Host "`nDone. deli_counter is now at $new with the placement gate locked in."
