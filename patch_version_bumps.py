r"""Bump the two tools whose code moved after their VERSION was written.

    python patch_version_bumps.py --check
    python patch_version_bumps.py
    python patch_version_bumps.py --selftest   (run it AFTER applying)
    python patch_version_bumps.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

WHY THIS EXISTS, AND WHY IT IS NOT A FORMALITY.
`verify-manifest` reported both of these OK on 2026-08-14:

    OK  deli_counter    0.88.0 matches certified 0.88.0
    OK  level_factory   0.22.0 matches certified 0.22.0

    deli_counter/VERSION     written 2026-07-25    check.py changed 2026-08-13
    level_factory/VERSION    written 2026-07-28    model.py changed 2026-08-13

The pin matches the file and the file is stale, so the lockstep check is
comparing two numbers that agree with each other and with nothing else. This
is the same failure `build_freshness.py` was written for -- an artefact older
than the code it describes, reported with full confidence -- and the same one
that made every recorded Laser Tag grade describe a draw that never shipped.

README.md states the rule this breaks: "Code changes ALWAYS land in a tool
repo" with its own semver, VERSION file, CHANGELOG and tags. The code landed.
The version did not follow it.

MINOR, NOT PATCH, FOR BOTH. Each adds behaviour and each changes what a gate
does. `deli_counter` gains a lint rule that can fail a spec that passed
before; `level_factory` changes which runs report as blocked. Neither is
backward-incompatible, so neither is a major.

RE-CERTIFY AFTER THIS, NOT BEFORE. `factory.manifest.json` still pins the set
from 2026-07-28 and also carries DRIFT on `lot` (0.33.0 installed vs 0.32.0
certified) and `lux` (0.16.0 vs 0.15.4). Those two want their real-tool smoke
re-run; this patch does not touch the manifest, because bumping the set while
two of its members are unverified would be certifying a set nobody has tested
together -- which is the one thing `factory_version` is supposed to mean.

COMMIT IN THE TOOL REPOS. This patch edits files inside `deli_counter/` and
`level_factory/`, which are their own git repos. The commits and tags belong
there:

    git -C deli_counter  add VERSION CHANGELOG.md
    git -C deli_counter  commit -m "0.89.0 -- freshness gate, L17 stair lint, four shells repaired"
    git -C deli_counter  tag v0.89.0 && git -C deli_counter push --follow-tags

    git -C level_factory add VERSION CHANGELOG.md
    git -C level_factory commit -m "0.23.0 -- eliminated candidates stop blocking; grade what ships"
    git -C level_factory tag v0.23.0 && git -C level_factory push --follow-tags
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

SIDECAR = ".pre_vbump"

DC_VERSION = Path("deli_counter/VERSION")
DC_CHANGELOG = Path("deli_counter/CHANGELOG.md")
LF_VERSION = Path("level_factory/VERSION")
LF_CHANGELOG = Path("level_factory/CHANGELOG.md")

DC_OLD_V = "Deli Counter 0.88.0"
DC_NEW_V = "Deli Counter 0.89.0"

LF_OLD_V = "0.22.0"
LF_NEW_V = "0.23.0"

DC_ENTRY = """## [0.89.0] - Stairs a nav agent can actually walk

Seven of 135 shells failed `nav_gate --all` on stair traversal. Four are
fixed and engine-confirmed; the mechanism turned out to be the same number
in every case -- a Godot nav agent bakes at radius 0.40 and needs 0.80 m of
clear width, and each of these left less.

- **check.py:** `build_freshness.py` now runs BEFORE the nav gate. That gate
  grades the shells in `build/`, and a stale shell does not make it answer
  weakly, it makes it answer wrongly with full confidence. On 2026-08-12
  every shell in `build/` was 4.2 days behind the code; a ladder that
  `patch_dc_roof_voids.py` had already fixed still climbed into a solid roof.
- **layout_lint.py L17 (NEW, FAIL):** a volume must not narrow a stair flight
  below `AGENT_DIAMETER` (0.80 m). Footprint comes from
  `stair_core._core_of`, the same reservation the stair placer uses, so the
  lint and the placer cannot disagree about where a stair is. Deliberately
  narrow: measured across the specs to hand it fires on 1 of 8 failing stairs
  and 0 of 8 passing ones. Three wider rules were tested and rejected --
  "volume overlaps the stair well" flags a vault and a power cabinet that
  both bake fine. A lint that fails working buildings gets switched off, and
  then it protects nothing.
- **specs/office.json:** `elevator_block`, a 2.0 x 2.0 x 3.0 m solid, was
  authored at (0.0, 0.0) -- the exact coordinates of `office_stair_0`. It
  left 0.60 m of a 3.20 m flight. Moved to x 3.6. `nav_gate`: no_path -> ok,
  markers 0/1 -> 1/1 reachable.
- **specs/cr_deli.json, corner_deli_heist_01.json, night_deli.json:** three
  clones of one authored deli. A switchback's two runs meet at the stair's
  own x and `office_stair_door` was centred on that seam, so each run got
  half a 1.20 m door -- 0.60 m, against 0.80 m needed. Widened to 2.40 m.
  `cr_deli` now bakes as ONE island, y -3.00..6.90, 483 polys, which is the
  signature every passing shell has.
- **specs/night_deli.json:** the door fix moved its break up a floor rather
  than closing it. `planter_box_upper_hall_1` (z 3.30..4.20) left 0.76 m on
  the ascending run -- four centimetres short. Moved clear, along with its
  derived `AUTO_PLANTER_BOX_UPPER_HALL_1` cover marker, which would otherwise
  have sent bots to take cover behind nothing in a stairwell.

Still failing and NOT fixed here: `night_pawn` (1.00 m runs, and a story-1
wall with no opening over the flight), `primos_pizza` (undiagnosed), and
`cbp_town_finale_midbalanced_schemafixed`, whose first floor bakes as ten-plus
fragments plus 32 slivers across 63 islands -- a floor that failed to be a
surface, which no amount of moving furniture fixes.
"""

LF_ENTRY = """## [0.23.0] - A blocked candidate is not a blocked mission

- **validation/model.py:** `aggregate()` takes `eliminated_candidates` and
  partitions blockers into `blocking_open` and `blocking_eliminated`;
  `has_blockers` follows `blocking_open` as it always did. The scheduler has
  scoped candidate failures for a while -- a candidate-scoped failure
  eliminates that candidate and the run carries on -- but the reporting never
  followed. Measured 2026-08-12 on lot_demo_001: one candidate's
  `dispatch_handoff` exited 1, all three candidates built, `blocked_job` was
  never set, and the summary still read "Blocked: unresolved blocking
  issues". The run that continued reported as the run that halted.
  Opt-in: the default is an empty set and every issue lands in
  `blocking_open` exactly as before, so `cmd_validate` and both suites are
  byte-identical.
- **cli/commands:** `cmd_run` passes the eliminated set and prints the
  eliminations. `cmd_batch_run` had printed them for a while; on a
  single-mission run the reason the mission survived was invisible.
- Findings are partitioned, never dropped: `total` still counts a blocker on
  a discarded candidate, because it is still a real finding about a real
  defect -- it is just not the mission's to answer for.

Downstream of this: `lot_demo_001` was re-run on the art layer and its three
candidates graded 40 / 55 / 60. SESSION_0811 concluded Laser Tag's score was a
step function stuck on a plateau, from five evaluations that all returned 45 --
but those were grading the greybox draw while the themed draw shipped. Grading
what ships, the score separates the candidates. The plateau was an artifact of
grading the wrong geometry.
"""

EDITS = {
    DC_VERSION: ((DC_OLD_V, DC_NEW_V),),
    LF_VERSION: ((LF_OLD_V, LF_NEW_V),),
}

_CRLF = "\r\n"


def _eol(body: str) -> str:
    """The file's dominant line ending -- keyed off the FILE, never an anchor."""
    crlf = body.count(_CRLF)
    lf = body.count("\n") - crlf
    return _CRLF if crlf > lf else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _bump(path: Path, old: str, new: str, *, check: bool) -> int:
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    if new in body:
        print(f"  already applied  {path}")
        return 0
    if body.count(old) != 1:
        print(f"REFUSING: {path} -- expected 1 occurrence of {old!r}, "
              f"found {body.count(old)}")
        return 1
    out = body.replace(old, new, 1)
    data = out.encode("utf-8")
    if check:
        print(f"  would bump   {path}  {old} -> {new}")
        return 0
    side = path.with_suffix(path.suffix + SIDECAR)
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  bumped       {path}  {old} -> {new}  sha256 {_sha(data)[:16]}")
    return 0


def _prepend(path: Path, entry: str, marker: str, *, check: bool) -> int:
    """CHANGELOGs here are newest-first, so a new entry goes on top."""
    if not path.is_file():
        print(f"  NOTE no {path} -- writing a new one")
        raw, body = b"", ""
    else:
        raw = path.read_bytes()
        body = raw.decode("utf-8")
    if marker in body:
        print(f"  already applied  {path}")
        return 0
    eol = _eol(body) if body else "\n"
    out = _as(entry, eol) + eol + body
    data = out.encode("utf-8")
    if check:
        print(f"  would prepend {path}  +{len(data) - len(raw):,} bytes")
        return 0
    side = path.with_suffix(path.suffix + SIDECAR)
    if not side.is_file() and raw:
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  prepended    {path}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})")
    return 0


def selftest(root: Path) -> int:
    bad = 0
    checks = [
        (DC_VERSION, "Deli Counter 0.89.0"),
        (LF_VERSION, "0.23.0"),
        (DC_CHANGELOG, "## [0.89.0]"),
        (LF_CHANGELOG, "## [0.23.0]"),
    ]
    for rel, want in checks:
        p = root / rel
        got = p.read_text(encoding="utf-8") if p.is_file() else ""
        ok = want in got
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {str(rel):<28} contains {want!r}")

    # The whole point: the VERSION must now be newer than the code it describes.
    import os
    for vrel, srel in ((DC_VERSION, Path("deli_counter/check.py")),
                       (LF_VERSION, Path("level_factory/packages/validation/model.py"))):
        v, s = root / vrel, root / srel
        if not (v.is_file() and s.is_file()):
            continue
        ok = os.path.getmtime(v) >= os.path.getmtime(s)
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {str(vrel):<28} is newer than "
              f"{srel.name}")

    print()
    print("  both tools now declare the code they contain" if not bad
          else f"  {bad} problem(s)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    for rel in (DC_VERSION, LF_VERSION):
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root")

    if "--selftest" in argv:
        return selftest(root)

    if "--revert" in argv:
        bad = 0
        for rel in (DC_VERSION, LF_VERSION, DC_CHANGELOG, LF_CHANGELOG):
            path = root / rel
            side = path.with_suffix(path.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {rel}")
                bad = 1
                continue
            path.write_bytes(side.read_bytes())
            print(f"  reverted     {rel}")
        return bad

    check = "--check" in argv
    rc = 0
    rc |= _bump(root / DC_VERSION, DC_OLD_V, DC_NEW_V, check=check)
    rc |= _bump(root / LF_VERSION, LF_OLD_V, LF_NEW_V, check=check)
    if rc:
        return rc
    rc |= _prepend(root / DC_CHANGELOG, DC_ENTRY, "## [0.89.0]", check=check)
    rc |= _prepend(root / LF_CHANGELOG, LF_ENTRY, "## [0.23.0]", check=check)
    if not check and not rc:
        print()
        print("  commit these IN THE TOOL REPOS -- see this file's docstring.")
        print("  then re-run: python -m level_factory verify-manifest --factory .")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
