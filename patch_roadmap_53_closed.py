#!/usr/bin/env python3
"""Item 53: correct the mechanism in place, and record the fix that shipped.

The item ranked FIRST a comparison of `_preset_for(model)` against
`lux.quality.json["preset"]`, on the stated ground that the file "already
echoes the applied preset back". It echoes the REQUEST -- `run_lux_apply.gd`
line 128 writes `{"preset": preset_name, ...}`, the `--preset` argument
straight back out. The proposed check compared a string with itself, inside
an item whose subject is checks that cannot fail.

That is the fourth mechanism published from a grep this session. It is
corrected in place, named as wrong, rather than quietly rewritten -- the same
treatment items 49 and 53's first two drafts got.

Two anchored edits, both in PIPELINE_ROADMAP.md. After applying, the derived
table needs regenerating:

    pwsh> python tools\\roadmap_status.py --write

Usage:
    pwsh> python patch_roadmap_53_closed.py --check
    pwsh> python patch_roadmap_53_closed.py
    pwsh> python patch_roadmap_53_closed.py --selftest
    pwsh> python patch_roadmap_53_closed.py --revert
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROADMAP = ROOT / "PIPELINE_ROADMAP.md"
TAG = "pre_53closed"

STATUS_OLD = (
    '*STATUS: OPEN 2026-08-17 -- CORRECTED, second re-scope. The previous one '
    'ranked `walk_preview`\'s `has_lux` first as a check that finds nothing and '
    'carries on. IT IS NOT ONE: it has a documented two-way detection, it does '
    'not render unlit but substitutes a preview RIG, and it reports which it '
    'used -- `lighting: "lux (content-owned)" | "preview rig"` in its return '
    'value. Withdrawn, with what it actually does, at '
    '`walk_preview.py:308-314,376` (18,781 B, sha256 3400109C...). That leaves '
    'ONE ranked defect: `_preset_for` is a silent no-op on a wrong Lux preset '
    'display name, PROVEN ON HARDWARE per its own comment, and '
    '`lux.quality.json` already echoes the applied preset back while nothing '
    'compares them. The 27 filename literals across 8 modules stay third and '
    'stay tidiness. `--unlit` interface: DECIDED, leave it*'
)

STATUS_NEW = (
    '*STATUS: NARROWED 2026-08-18 -- FIRST RANKED FIX SHIPPED, and the '
    'mechanism this item gave for it was WRONG. It said `lux.quality.json` '
    '"already echoes the applied preset back" and ranked first a comparison '
    'against `_preset_for(model)`. It echoes the REQUEST: `run_lux_apply.gd` '
    'writes `{"preset": preset_name, ...}`, the `--preset` argument straight '
    'back out, so the proposed check compared a string with itself -- inside '
    'an item whose subject is checks that cannot fail. Fourth mechanism '
    'published from a grep this session; corrected in place below rather than '
    'rewritten. level_factory 0.41.0 reads `LuxRoot.get_current_preset()` '
    'instead (`lux_root.gd:641`, `_current`, assigned only by '
    '`_apply_immediate` from the library resource), reports it as '
    '`preset_applied`, and raises LUX_PRESET_NOT_APPLIED when the two '
    'disagree -- no Python touched, the finding rides the existing '
    '`lux.validation.json` channel. NOT YET RUN ON HARDWARE. What remains '
    'open is the third-ranked item only: 27 filename literals across 8 '
    'modules, tidiness*'
)

BLOCK_OLD = (
    'It is also nearly closed, because the artifact answers it. Level Factory asks\n'
    'for a preset; Lux reports the one it applied:\n'
    '\n'
    '```\n'
    'requested   _preset_for(model)          ->  "Blue Hour"\n'
    'applied     lux.quality.json["preset"]  ->  "Blue Hour"     (lot_demo_001, 2026-08-17)\n'
    '```\n'
    '\n'
    'Nothing compares those two strings. A comparison needs no new data, turns a\n'
    'silent no-op into a finding, and would have been exercised by every lit\n'
    'export this pipeline has produced.\n'
)

BLOCK_NEW = '''IT WAS NOT NEARLY CLOSED BY THE ARTIFACT, AND THIS ITEM SAID IT WAS.

The claim was read off a filename and a field name rather than off the
driver. `assets/godot/run_lux_apply.gd` (6,902 B, sha256 0CC60D6D..., line
128):

```
var quality := {"preset": preset_name, "applied": applied_ok, ...}
```

`preset_name` IS the `--preset` argument. That field is the request written
straight back out. Comparing it against `_preset_for(model)` compares a
string with itself -- a check that cannot fail, proposed inside an item whose
subject is checks that cannot fail. Both sides of the table this item
published were the same string, and its agreement meant nothing:

```
requested   _preset_for(model)          ->  "Blue Hour"
"applied"   lux.quality.json["preset"]  ->  "Blue Hour"   <- the SAME string
```

**WHAT LUX ACTUALLY OFFERS, AND WHAT SHIPPED.**

`LuxRoot.get_current_preset()` returns `_current` -- `lux_root.gd:641`
(25,638 B, sha256 529f70e7...) -- and `_current` is assigned in exactly one
place, `_apply_immediate`, from the LIBRARY resource. It cannot be the
argument arriving back round.

Reading it also covers a failure the driver's existing library-dictionary
check cannot see. `apply_preset` returns early when `_initialized` is false,
assigning `active_preset` and applying nothing:

```
func apply_preset(preset: LuxPreset, blend_time: float = 0.0) -> void:
    if preset == null:
        return
    if not _initialized:
        active_preset = preset      # and applies NOTHING
        return
```

The name is in the library, so `preset_known` is true, so no issue is raised,
and the level ships with no look. The dictionary says the preset exists; only
LuxRoot says it arrived.

level_factory 0.41.0:

```
lux.quality.json     "preset"          the REQUEST, meaning unchanged
                     "preset_applied"  NEW -- get_current_preset()
lux.validation.json  LUX_PRESET_NOT_APPLIED (moderate) when they disagree
```

No Python changed. The driver already writes findings to
`lux.validation.json` and the Lux adapter's `normalize_validation` already
passes arbitrary codes through, so the new finding reaches the findings
channel without the adapter being touched. Same release, same file, same
shape of defect: `ResourceSaver.save(...)`'s return was discarded and
`applied_ok` tracked only `pack()`, so a save that failed reported
`applied: true` for a scene that was never written.

NOT YET RUN ON HARDWARE. No Godot process has produced a `preset_applied`
field yet. `tests/unit/test_lux_preset_readback.py` is a source-shape test
and says so in its own docstring -- it pins the one regression that would
restore the tautology without changing an output key, and it proves nothing
about the driver running. The next lit run is the evidence.
'''


def _sha(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:8].upper()


def _eol(path: Path) -> str:
    return "\r\n" if b"\r\n" in path.read_bytes() else "\n"


def _stamp(p: Path) -> str:
    t = p.read_text(encoding="utf-8")
    return f"{p.name}: {len(t.encode('utf-8'))} B  sha {_sha(t)}"


EDITS = [
    ("status line", STATUS_OLD, STATUS_NEW),
    ("the mechanism block", BLOCK_OLD, BLOCK_NEW),
]


def _plan(text: str) -> str:
    for label, old, new in EDITS:
        n = text.count(old)
        if n != 1:
            raise SystemExit(
                f"REFUSING: anchor for '{label}' occurs {n} times, expected 1.")
        text = text.replace(old, new, 1)
        print(f"  ok  {label}")
    return text


def _require() -> None:
    if not ROADMAP.is_file():
        sys.exit(f"REFUSING: not found: {ROADMAP}")


def cmd_check() -> int:
    _require()
    print("   ", _stamp(ROADMAP))
    t = ROADMAP.read_text(encoding="utf-8")
    if "preset_applied" in t:
        print("\nALREADY APPLIED.")
        return 0
    print()
    _plan(t)
    print("\nboth anchors resolve exactly once.")
    return 0


def cmd_apply() -> int:
    _require()
    src = ROADMAP.read_text(encoding="utf-8")
    if "preset_applied" in src:
        print("ALREADY APPLIED; nothing to do.")
        return 0
    eol = _eol(ROADMAP)
    if eol == "\r\n":
        # normalise for matching, restore on write
        src_n = src.replace("\r\n", "\n")
    else:
        src_n = src
    out = _plan(src_n)
    (ROADMAP.parent / f"{ROADMAP.name}.{TAG}").write_bytes(ROADMAP.read_bytes())
    ROADMAP.write_text(out if eol == "\n" else out.replace("\n", "\r\n"),
                       encoding="utf-8", newline="")
    print("\nafter:")
    print("   ", _stamp(ROADMAP))
    print(f"\nsidecar .{TAG} written. NEXT: python tools\\roadmap_status.py --write")
    return 0


def cmd_revert() -> int:
    side = ROADMAP.parent / f"{ROADMAP.name}.{TAG}"
    if not side.is_file():
        print("nothing to revert.")
        return 0
    ROADMAP.write_bytes(side.read_bytes())
    side.unlink()
    print(f"  restored {ROADMAP.name}")
    return 0


def cmd_selftest() -> int:
    _require()
    t = ROADMAP.read_text(encoding="utf-8")
    checks = [
        ("the wrong mechanism is named as wrong, not deleted",
         'the request written' in t and 'compares a\nstring with itself' in t),
        ("the old claim is gone",
         'lux.quality.json` already echoes the applied preset back' not in t),
        ("the real source is named with a line number",
         'lux_root.gd:641' in t),
        ("the new field is documented",
         '"preset_applied"  NEW' in t),
        ("the finding code is documented",
         'LUX_PRESET_NOT_APPLIED' in t),
        ("the hardware gap is stated, not glossed",
         'NOT YET RUN ON HARDWARE' in t),
        ("the status verb is one roadmap_status knows",
         '*STATUS: NARROWED 2026-08-18 --' in t),
    ]
    bad = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(("  ok  " if ok else "  FAIL ") + name)
    if bad:
        raise SystemExit("SELFTEST FAILED: " + "; ".join(bad))

    # Falsification: every check above must FAIL on the pre-image. A check
    # that passes on the un-patched file is not a check.
    side = ROADMAP.parent / f"{ROADMAP.name}.{TAG}"
    if side.is_file():
        pre = side.read_text(encoding="utf-8")
        still = [name for name, _ in checks
                 if name != "the status verb is one roadmap_status knows"
                 and _eval_on(pre, name)]
        # the two "absence" checks are expected to be TRUE-after/FALSE-before;
        # _eval_on returns the same predicate against the pre-image.
        if still:
            raise SystemExit(
                "SELFTEST FAILED: these passed on the PRE-IMAGE too, so they "
                "test nothing: " + "; ".join(still))
        print("  ok  every content check fails on the pre-image")
    else:
        print("  --  no sidecar; falsification against the pre-image skipped")

    # No phantom items: roadmap_status parses `^\\*\\*(\\d+)\\. ` as a heading.
    import re
    heads = re.findall(r"(?m)^\*\*(\d+)\. ", t)
    nums = [int(h) for h in heads]
    if nums != sorted(set(nums)) or len(nums) != len(set(nums)):
        raise SystemExit(f"SELFTEST FAILED: item numbering is not strictly "
                         f"increasing/unique: {nums}")
    print(f"  ok  {len(nums)} item headings, strictly increasing, max {nums[-1]}")
    print("\nSELFTEST PASSED")
    return 0


def _eval_on(text: str, name: str) -> bool:
    if name == "the wrong mechanism is named as wrong, not deleted":
        return 'the request written' in text and 'compares a\nstring with itself' in text
    if name == "the old claim is gone":
        return 'lux.quality.json` already echoes the applied preset back' not in text
    if name == "the real source is named with a line number":
        return 'lux_root.gd:641' in text
    if name == "the new field is documented":
        return '"preset_applied"  NEW' in text
    if name == "the finding code is documented":
        return 'LUX_PRESET_NOT_APPLIED' in text
    if name == "the hardware gap is stated, not glossed":
        return 'NOT YET RUN ON HARDWARE' in text
    raise SystemExit(f"selftest bug: no pre-image predicate for {name!r}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true")
    g.add_argument("--revert", action="store_true")
    g.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.check:
        return cmd_check()
    if a.revert:
        return cmd_revert()
    if a.selftest:
        return cmd_selftest()
    return cmd_apply()


if __name__ == "__main__":
    raise SystemExit(main())
