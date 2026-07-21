# commit_gate_hardening.ps1
# deli_counter 0.81.1 -- placement-gate measurement fixes + AUTHORING.md.
# Corrects the height advisory (was a false positive from local-space bbox
# union), fixes a hidden substring slot-match bug, and documents the
# fit-to-greybox rule + the gate. PATCH bump.
#
# Run:  powershell -ExecutionPolicy Bypass -File .\commit_gate_hardening.ps1
# Add  -NoPush  to commit without pushing.

param([switch]$NoPush)

$ErrorActionPreference = "Stop"
$repo = "C:\Projects\gabagool_studios\gabagool_factory\deli_counter"
Set-Location $repo

# --- 1. bump VERSION (parse current, bump PATCH) -----------------------------
$verPath = Join-Path $repo "VERSION"
$cur = (Get-Content $verPath -Raw).Trim()
if ($cur -notmatch '(\d+)\.(\d+)\.(\d+)') { throw "can't parse VERSION: '$cur'" }
$maj = [int]$Matches[1]; $min = [int]$Matches[2]; $pat = [int]$Matches[3]
$new = "$maj.$min.$($pat + 1)"
$newLine = ($cur -replace '\d+\.\d+\.\d+', $new)
Set-Content $verPath $newLine -NoNewline
Write-Host "VERSION: '$cur' -> '$newLine'"

# --- 2. prepend CHANGELOG entry ----------------------------------------------
$clPath = Join-Path $repo "CHANGELOG.md"
$entry = @"
## [$new] - Placement gate: measure the shell truthfully

Hardening of the 0.81.0 ground-truth gate after validating it against real
opening geometry. No change to the fit-to-greybox placement itself; these fix
how the gate MEASURES the greybox so it stops crying wolf and starts catching a
bug it was masking.

- **Height advisory was a false positive -- fixed.** The gate compared a
  module's height to the greybox's *drawn solid* extent, unioned in LOCAL space.
  The greybox positions an opening's parts (lintel/sill/pane) by node
  translation with locally-centered vertices, so the local union collapsed three
  stacked parts into one short box (a 4.2 m window read as 2.4 m). The gate now
  unions in WORLD space (applies node translation) and checks height against the
  slot's AUTHORED opening height -- what the kit is contracted to build -- not
  the greybox's partial solid (a doorway is greyboxed as just its header lintel,
  so its drawn height is not a height reference). gas_street: 7 advisories -> 0.
- **Hidden substring slot-match bug -- fixed.** Slot-to-greybox-node matching
  used a bare substring test, so 'ext_0_N_seg1' also matched 'seg10'..'seg19'.
  It was invisible only because the local-space union collapsed the siblings
  onto the origin; measuring in world space exposed it (a wall read 30 m wide).
  Matching is now precise: a node is the slot's iff its name is the slot_id or
  starts with '<slot_id>_' (a named sub-part).
- **Portable closure hardened** (carried from the same pass): greybox-fallback
  slots keep their geometry in the base shell instead of emitting an unbundled
  external ref, so a partial kit still yields a closed, fully-visible package.
- **docs/AUTHORING.md:** new section "The gate that keeps art honest -- fit to
  the shell's truth" -- the fit-to-greybox rule, the gate, and the two
  measurement rules (world-space extents; precise slot matching) so the bugs
  above can't be quietly re-introduced.

Validated end-to-end on gas_street: 73/73 footprint match, 0 advisories,
PORTABLE=True, walkable=True. Gate teeth confirmed: a wrong-width module fails
the footprint check and a wrong-height module fails the height check.

"@
if (Test-Path $clPath) {
    $old = Get-Content $clPath -Raw
    Set-Content $clPath ($entry + $old) -NoNewline
    Write-Host "CHANGELOG.md: prepended [$new] entry"
} else {
    Set-Content $clPath $entry -NoNewline
}

# --- 3. stage + commit -------------------------------------------------------
git add portable_building.py themed_tscn.py docs/AUTHORING.md VERSION CHANGELOG.md
Write-Host "`n--- staged ---"
git status --short

$msg = "deli_counter $($new): truthful placement-gate measurement + AUTHORING.md"
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
Write-Host "`nDone. deli_counter is now at $new -- gate measures the shell truthfully, 0 advisories on gas_street."
