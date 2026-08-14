r"""The compose stage fingerprints the tool it actually runs: Deli Counter.

    python patch_lf_presentation_probe.py --check
    python patch_lf_presentation_probe.py
    python patch_lf_presentation_probe.py --revert

## The defect

`PresentationAdapter` has no repo of its own -- its module docstring says so,
and says what it drives:

    the composition is done by DC's OWN composer ...
    ``portable_building.build_package`` ... (``themed_tscn._fit_rotation``
    over ``tscn_export.godot_basis``)

Its probe reported:

    tool_version=self.adapter_version,
    repository_commit=None,

`adapter_version` is ALREADY a separate field of `BuildFingerprint` -- the
scheduler passes `adapter_version=adapter.adapter_version` beside
`tool_version=probe.tool_version` -- so reporting it again said nothing new,
and `repository_commit=None` said nothing at all. The result: **no edit to Deli
Counter's composer could change this stage's fingerprint.**

`BaseAdapter._read_git_commit` was written for exactly this, and its own
docstring names the same failure ("a shell whose ladder slab-hole had been
fixed ... kept shipping the old symmetric cut ... because the fix was staged on
disk but not yet committed"). It returns HEAD plus a `+dirty.<hash>` marker
over the CONTENT of modified tracked files -- which is the state a fix in
progress is always in. The compose stage simply never called it.

Measured 2026-08-09: `deli_counter/themed_tscn.py` was corrected so the
composer names the roof module Zoo actually builds. The next `run --art`
reported `presentation_compose  cache` and shipped the scene naming the old
module. A hand-run `cache forget` was the only way through, and a step that
must be done by hand is a step that gets skipped -- `ContentCache.forget`'s own
docstring, one repo over.

## The change

Two edits in `level_factory/adapters/presentation/__init__.py`:

  * `probe()` reports Deli Counter's tool version and revision, via the same
    `BaseAdapter` helpers every repo-backed adapter uses.
  * `adapter_version` 0.2.0 -> 0.3.0. The RULES for computing this stage's
    fingerprint changed, so entries computed under the old rules must not be
    served alongside the new ones. Bumping retires them once, which is the
    convention `LotAdapter` already states for the same reason -- and it means
    you do NOT need another manual `cache forget` for this to take effect.

## What it does NOT fix

`themed_site_assemble` runs under the `lot` adapter, whose probe reads the LOT
repo. Forgetting that job -- not this one -- is what landed the roof fix on
2026-08-09, so Lot is reading DC's composer too and has the same blindness by a
different route. That needs its own read before it gets its own patch; this
patch does not touch it and does not claim to.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TARGET = Path("level_factory") / "adapters" / "presentation" / "__init__.py"
SIDECAR_SUFFIX = ".pre_dcprobe"

OLD_VERSION = '''    # 0.1.2: compose gates (z-fight/ladder/lineage) + dressing/fixtures
    # layers -- version participates in the build fingerprint, so bumping it
    # guarantees every mission recomposes under the new gates.
    adapter_version = "0.2.0"'''

NEW_VERSION = '''    # 0.1.2: compose gates (z-fight/ladder/lineage) + dressing/fixtures
    # layers -- version participates in the build fingerprint, so bumping it
    # guarantees every mission recomposes under the new gates.
    # 0.3.0: the probe now reports DELI COUNTER's revision rather than this
    # adapter's version. The rules for computing this stage's fingerprint
    # changed, so entries computed under the old rules are not comparable and
    # must be retired rather than served alongside the new ones.
    adapter_version = "0.3.0"'''

OLD_PROBE = '''        return ToolProbe(
            available=ok, tool_version=self.adapter_version,
            repository_commit=None, executable_versions={},
            capabilities=self.capabilities, problems=problems)'''

NEW_PROBE = '''        # THE TOOL THIS STAGE RUNS IS DELI COUNTER, so DC's revision is what
        # has to reach the fingerprint.
        #
        # This reported `self.adapter_version` -- which `BuildFingerprint`
        # already carries in its own `adapter_version` field -- and `None` for
        # the commit. Net effect: no edit to DC's composer could change this
        # stage's fingerprint. Measured 2026-08-09, `themed_tscn.PLATE_ROLES`
        # was corrected so the composer names the roof module Zoo builds; the
        # next run reported `cache` and shipped the scene naming the old one.
        #
        # `_read_git_commit` carries a `+dirty.<hash>` marker over the CONTENT
        # of modified tracked files, which is the state a fix in progress is
        # always in -- see its docstring, written after the same failure.
        repo = Path(str(deli)) if ok else None
        return ToolProbe(
            available=ok,
            tool_version=(self._read_tool_version(repo) if repo else None),
            repository_commit=(self._read_git_commit(repo) if repo else None),
            executable_versions={},
            capabilities=self.capabilities, problems=problems)'''

EDITS = ((OLD_VERSION, NEW_VERSION), (OLD_PROBE, NEW_PROBE))


def _find(body: str, anchor: str) -> tuple[str, int]:
    for a in (anchor, anchor.replace("\n", "\r\n")):
        n = body.count(a)
        if n:
            return a, n
    return anchor, 0


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _resolve(root: Path) -> Path:
    p = root / TARGET
    if p.is_file():
        return p
    raise SystemExit(f"cannot find {TARGET} under {root} -- run from the "
                     f"factory root")


def main(argv: list[str]) -> int:
    path = _resolve(Path.cwd())
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR_SUFFIX)

    if "--revert" in argv:
        if not side.is_file():
            print(f"no sidecar at {side.name}; nothing to revert")
            return 2
        pre = side.read_bytes()
        pre_text = pre.decode("utf-8")
        bad = [i for i, (old, _new) in enumerate(EDITS)
               if _find(pre_text, old)[1] != 1]
        if bad:
            print(f"REFUSING: {side.name} is not the pre-image this patch "
                  f"recorded (edit(s) {bad} did not match exactly once)")
            return 1
        path.write_bytes(pre)
        print(f"  reverted   {path.name}  {len(raw):,} -> {len(pre):,} bytes")
        print(f"  sha256     {_sha(pre)}")
        return 0

    applied = sum(1 for _old, new in EDITS if _find(body, new)[1] == 1)
    if applied == len(EDITS):
        print("  already applied: the probe reports Deli Counter's revision")
        print(f"  sha256     {_sha(raw)}")
        return 0
    if applied:
        print(f"REFUSING: {applied} of {len(EDITS)} edits are already present. "
              f"A half-applied file is not a state this patch can reason "
              f"about; revert or fix it by hand.")
        return 1

    out = body
    for old, new in EDITS:
        anchor, n = _find(out, old)
        if n != 1:
            print(f"REFUSING: expected exactly 1 occurrence of an anchor, "
                  f"found {n}. The file has drifted from what this patch was "
                  f"written against.")
            print(f"  anchor starts: {old.splitlines()[0].strip()!r}")
            print(f"  sha256 now {_sha(raw)}")
            return 1
        repl = new.replace("\n", "\r\n") if "\r\n" in anchor else new
        out = out.replace(anchor, repl, 1)

    out_bytes = out.encode("utf-8")

    if "--check" in argv:
        print("  --check only, nothing written")
        print(f"  would be   {path.name}  {len(raw):,} -> {len(out_bytes):,} "
              f"bytes ({len(out_bytes) - len(raw):+,})")
        print(f"  sha256 now {_sha(raw)}")
        print(f"  sha256 new {_sha(out_bytes)}")
        return 0

    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(out_bytes)
    print(f"  applied    {path.name}  {len(raw):,} -> {len(out_bytes):,} bytes "
          f"({len(out_bytes) - len(raw):+,})")
    print(f"  sha256     {_sha(out_bytes)}")
    print(f"  sidecar    {side.name}")
    print()
    print("  adapter_version 0.2.0 -> 0.3.0 retires the old entries, so the "
          "next run recomposes")
    print("  without a manual `cache forget`. Verify by editing nothing and "
          "running twice:")
    print("    run --art   -> presentation_compose runs")
    print("    run --art   -> presentation_compose cache")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
