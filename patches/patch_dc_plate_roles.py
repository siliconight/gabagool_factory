r"""`roof` joins Deli Counter's PLATE_ROLES, so it names the file Zoo builds.

    python patch_dc_plate_roles.py --check
    python patch_dc_plate_roles.py
    python patch_dc_plate_roles.py --revert

## What this is

`zoo_keeper/core/kit.py` gained `"roof"` in `PLATE_ROLES` (patch_zoo_roof_plate).
`deli_counter/themed_tscn.py` carries a HAND COPY of that tuple -- its own comment
says `#: Mirror of ``zoo_keeper.core.kit.PLATE_ROLES``` -- and it did not.

That one word decides two things inside `resolve_themed_stem`:

    depth_cm = (int(round(dims[1] * 100))
                if exact and typ in PLATE_ROLES else None)
    vtag = void_tag(fit.get("voids")) if typ in PLATE_ROLES else None

so with `roof` absent, DC wrote `roof_rockay_01_w4000` into `site.tscn` while Zoo
built `roof_rockay_01_w4000_d3000_v72fc6e.glb`. The scene referenced a module
that does not exist, an ORPHAN of that name from an older run was sitting in
`art/zoo/` and satisfied the load, and the orphan is a solid plate. That is the
ladder.

## What it does NOT do

No geometry changes. The roof module is already built and cached under the
correct stem -- only the `.tscn` writer is wrong, and it is a python_cpu stage.
Do not rebuild in Blender to test this.

Verify after applying by re-running the assemble/compose stage and re-reading
the scene:

    Select-String -Path <site>\site.tscn -Pattern "art/zoo/roof"

EXPECT `roof_rockay_01_w4000_d3000_v72fc6e.glb`, and that file present in
`art/zoo/`. If the stem comes out with a DIFFERENT `_v` tag, DC's `void_tag`
has drifted from Zoo's too -- test_mirror_agreement.py is what tells you.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TARGET = Path("deli_counter") / "themed_tscn.py"
SIDECAR_SUFFIX = ".pre_plateroles"

OLD = '''#: Roles built as a horizontal PLATE, whose footprint varies on BOTH axes.
#: Mirror of ``zoo_keeper.core.kit.PLATE_ROLES``.
PLATE_ROLES = ("floor", "ceiling")'''

NEW = '''#: Roles built as a horizontal PLATE, whose footprint varies on BOTH axes.
#: Mirror of ``zoo_keeper.core.kit.PLATE_ROLES``.
PLATE_ROLES = ("floor", "ceiling", "roof")'''


def _resolve(root: Path) -> Path:
    p = root / TARGET
    if p.is_file():
        return p
    p2 = root / TARGET.name
    if p2.is_file():
        return p2
    raise SystemExit(f"cannot find {TARGET} from {root} -- run this from the "
                     f"factory root, or from deli_counter/")


def _find(body: str, anchor: str) -> tuple[str, int]:
    """Return (anchor-as-written, count). Handles CRLF without rewriting the
    file's endings, which would change every byte and defeat the byte report."""
    for a in (anchor, anchor.replace("\n", "\r\n")):
        n = body.count(a)
        if n:
            return a, n
    return anchor, 0


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _report(label: str, path: Path, before: int, after: int) -> None:
    print(f"  {label:<10} {path.name}  {before:,} -> {after:,} bytes "
          f"({after - before:+,})")


def main(argv: list[str]) -> int:
    root = Path.cwd()
    path = _resolve(root)
    body = path.read_text(encoding="utf-8")
    raw = path.read_bytes()
    side = path.with_suffix(path.suffix + SIDECAR_SUFFIX)

    if "--revert" in argv:
        if not side.is_file():
            print(f"no sidecar at {side.name}; nothing to revert")
            return 2
        pre = side.read_bytes()
        old_anchor, n_old = _find(pre.decode("utf-8"), OLD)
        if n_old != 1:
            print(f"REFUSING: {side.name} is not the pre-image this patch "
                  f"recorded (found {n_old} occurrences of the original "
                  f"tuple, expected 1)")
            return 1
        path.write_bytes(pre)
        _report("reverted", path, len(raw), len(pre))
        print(f"  sha256     {_sha(pre)}")
        print(f"  sidecar    {side.name} left in place (delete when committed)")
        return 0

    new_anchor, n_new = _find(body, NEW)
    old_anchor, n_old = _find(body, OLD)

    if n_new == 1 and n_old == 0:
        print("  already applied: PLATE_ROLES already carries \"roof\"")
        print(f"  sha256     {_sha(raw)}")
        return 0
    if n_old != 1:
        print(f"REFUSING: expected exactly 1 occurrence of the original "
              f"PLATE_ROLES block, found {n_old}. The file has drifted from "
              f"what this patch was written against; re-read it before "
              f"editing.")
        print(f"  sha256     {_sha(raw)}")
        return 1

    replacement = (NEW.replace("\n", "\r\n")
                   if "\r\n" in old_anchor else NEW)
    out = body.replace(old_anchor, replacement, 1)
    out_bytes = out.encode("utf-8")

    if "--check" in argv:
        print("  --check only, nothing written")
        _report("would be", path, len(raw), len(out_bytes))
        print(f"  sha256 now {_sha(raw)}")
        print(f"  sha256 new {_sha(out_bytes)}")
        return 0

    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(out_bytes)
    _report("applied", path, len(raw), len(out_bytes))
    print(f"  sha256     {_sha(out_bytes)}")
    print(f"  sidecar    {side.name}")
    print()
    print("  No rebuild needed. Re-run the stage that writes site.tscn, then:")
    print("    Select-String -Path <site>\\site.tscn -Pattern \"art/zoo/roof\"")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
