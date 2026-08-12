r"""The closure scan stops resolving `res://` by path suffix.

    python patch_lf_closure_misrooted.py --explain
    python patch_lf_closure_misrooted.py --check
    python patch_lf_closure_misrooted.py
    python patch_lf_closure_misrooted.py --verify <export_dir>
    python patch_lf_closure_misrooted.py --revert

Run from the FACTORY ROOT (the directory holding `level_factory/`).

## The defect, in one line

    if not any(pr.endswith(rel) for pr in present):
        result.missing_resource_count += 1

`rel` is what a scene asked for after `res://`. `present` is every file in the
package, relative to its root. **The suffix match says a reference resolves when
some file anywhere in the package merely ENDS WITH the requested path.**

Godot does not resolve `res://` that way and never has. `res://x` is exactly
`<project root>/x`. There is no search path, no fallback, no walking up.

## What it certified

`lot_demo_001`, portable-godot, after the two fixes in
`patch_lf_export_closure.py`:

    export_closure_scan.json:  ok true, 38 resources, 0 missing

Meanwhile each of the five buildings the mission instances is a scene that was
composed as its own project root and staged under `lot/<archetype>/` **with none
of its references rewritten**. Measured on `lot/bank_branch_a04/site.tscn`:

    31 x  res://art/zoo/...        the modules live at lot/bank_branch_a04/art/zoo/
     1 x  res://art/fixtures/...
     1 x  res://art/dressing/...
     1 x  res://site_base.glb      all five resolve to the same root greybox base

`res://art/zoo/wall_rockay_01_w200.glb` is absent from the root. But
`lot/bank_branch_a04/art/zoo/wall_rockay_01_w200.glb` ends with it, so the suffix
match called it resolved. **165 dangling references across five scenes, reported
as zero.**

And the package looks exactly like that when you open it: floors, ceilings and
one amber staircase floating in a lit night sky, every wall and doorway and roof
absent, and the debug overlay naming `res://site_base.glb` under the player --
compose's single greybox building, standing in for all five.

## The change

`res://x` resolves if and only if `<root>/x` exists. The directory check stays
(a preset-library scan names a folder, and folders are not in the file set) and
the `.godot/` skip stays with its own long-standing reason.

The suffix match is **not deleted, it is renamed to what it actually finds.** A
reference that fails at its stated path while a file with that tail exists
elsewhere is not a resolved reference and it is not an ordinary missing one
either -- it is a scene that was moved without having its references rewritten,
which is a specific and very fixable defect. So it gets its own count,
`misrooted_resource_count`, and an issue line naming both what was asked for and
where the file actually sits:

    site.tscn: MISROOTED res://art/zoo/wall_rockay_01_w200.glb
               -> present at lot/bank_branch_a04/art/zoo/wall_rockay_01_w200.glb

`ok` is False when that count is non-zero, because the package does not load.

## Expect the number to jump

This will surface references that have been suppressed since the suffix match
was written. That is the point, and it is worth saying plainly rather than
having it arrive as a shock: an export that reported 0 missing may now report
dozens, and none of them are new -- they were always there, and the judge was
looking at them and calling them fine.

The first fix that follows is not in this file: the building scenes staged under
`lot/<id>/` need their `res://` references rewritten to their new root. This
patch only stops the scanner from lying about them.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

CLOSURE = Path("level_factory") / "packages" / "exporting" / "closure.py"
SIDECAR = ".pre_misrooted"


FIELD_OLD = '''    missing_resource_count: int = 0
    required_plugin_count: int = 0
    required_autoload_count: int = 0
    issues: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return (self.absolute_path_count == 0
                and self.missing_resource_count == 0
                and self.external_reference_count == 0
                and self.required_plugin_count == 0
                and self.required_autoload_count == 0)'''

FIELD_NEW = '''    missing_resource_count: int = 0
    #: References that fail at the path they name while a file with that TAIL
    #: exists elsewhere in the package. Counted apart from `missing` because the
    #: two want different fixes: a missing resource was not copied, a misrooted
    #: one was copied and the scene that names it was moved without having its
    #: references rewritten.
    #:
    #: This category exists because the scan used to treat exactly this case as
    #: RESOLVED -- `any(pr.endswith(rel) for pr in present)` -- and Godot does
    #: not resolve `res://` by suffix. Measured on lot_demo_001: five building
    #: scenes staged under `lot/<archetype>/` with 33 unrewritten references
    #: each, and a report of `ok: true, 0 missing`.
    misrooted_resource_count: int = 0
    required_plugin_count: int = 0
    required_autoload_count: int = 0
    issues: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return (self.absolute_path_count == 0
                and self.missing_resource_count == 0
                and self.misrooted_resource_count == 0
                and self.external_reference_count == 0
                and self.required_plugin_count == 0
                and self.required_autoload_count == 0)'''


DICT_OLD = '''            "missing_resource_count": self.missing_resource_count,
            "required_plugin_count": self.required_plugin_count,'''

DICT_NEW = '''            "missing_resource_count": self.missing_resource_count,
            "misrooted_resource_count": self.misrooted_resource_count,
            "required_plugin_count": self.required_plugin_count,'''


SCAN_OLD = '''                if not any(pr.endswith(rel) for pr in present):
                    result.missing_resource_count += 1
                    result.issues.append(f"{f.name}: unresolved res://{rel}")'''

SCAN_NEW = '''                # `res://x` IS `<root>/x`. No search path, no fallback,
                # no walking up -- Godot has never resolved a res:// path by
                # suffix and this scan used to, with
                # `any(pr.endswith(rel) for pr in present)`. That single line
                # certified lot_demo_001's portable export at `ok: true,
                # 0 missing` while five building scenes, staged under
                # `lot/<archetype>/` without their references rewritten, each
                # dangled 33 of them. The package opened as floors and a
                # staircase in an empty sky.
                #
                # The suffix search is kept and RENAMED to what it finds. A
                # reference that fails where it points while the file exists
                # elsewhere is not resolved and is not ordinarily missing
                # either: it is a scene that moved without being rewritten,
                # which is a specific defect with a specific fix, and saying
                # so beats a bare "unresolved".
                found_at = next((pr for pr in sorted(present)
                                 if pr.endswith("/" + rel) or pr == rel), None)
                if found_at is None:
                    result.missing_resource_count += 1
                    result.issues.append(f"{f.name}: unresolved res://{rel}")
                else:
                    result.misrooted_resource_count += 1
                    result.issues.append(
                        f"{f.name}: MISROOTED res://{rel} -> present at "
                        f"{found_at}")'''


EDITS = {CLOSURE: ((FIELD_OLD, FIELD_NEW), (DICT_OLD, DICT_NEW),
                   (SCAN_OLD, SCAN_NEW))}

_CRLF = "\r\n"


def _find(body: str, anchor: str):
    for candidate in (anchor, anchor.replace("\n", _CRLF)):
        count = body.count(candidate)
        if count:
            return candidate, count
    return anchor, 0


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(path: Path, edits, *, check: bool) -> int:
    raw = path.read_bytes()
    body = raw.decode("utf-8")
    side = path.with_suffix(path.suffix + SIDECAR)

    done = sum(1 for _o, new in edits if _find(body, new)[1] == 1)
    if done == len(edits):
        print(f"  already applied  {path.name}")
        return 0
    if done:
        print(f"REFUSING: {path.name} has {done} of {len(edits)} edits already "
              f"present.")
        return 1

    out = body
    for old, new in edits:
        anchor, count = _find(out, old)
        if count != 1:
            print(f"REFUSING: {path.name} -- expected 1 occurrence of an "
                  f"anchor, found {count}.")
            print(f"  anchor starts: {old.splitlines()[0].strip()!r}")
            return 1
        out = out.replace(
            anchor, new.replace("\n", _CRLF) if _CRLF in anchor else new, 1)

    data = out.encode("utf-8")
    if check:
        print(f"  would patch  {path.name}  {len(raw):,} -> {len(data):,} "
              f"bytes ({len(data) - len(raw):+,})")
        return 0
    if not side.is_file():
        side.write_bytes(raw)
    path.write_bytes(data)
    print(f"  patched      {path.name}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def _explain() -> int:
    import tempfile
    sys.path.insert(0, str(Path.cwd() / "level_factory"))
    from packages.exporting.closure import scan_closure
    root = Path(tempfile.mkdtemp())
    (root / "lot" / "bank" / "art" / "zoo").mkdir(parents=True)
    (root / "lot" / "bank" / "art" / "zoo" / "wall.glb").write_bytes(b"g")
    (root / "lot" / "bank" / "site.tscn").write_text(
        '[gd_scene]\n[ext_resource path="res://art/zoo/wall.glb" id="1"]\n')
    (root / "mission.tscn").write_text(
        '[gd_scene]\n[ext_resource path="res://gone.glb" id="1"]\n')
    r = scan_closure(root)
    d = r.as_dict()
    print("  a scene under lot/bank/ asking for res://art/zoo/wall.glb,")
    print("  whose file is at lot/bank/art/zoo/wall.glb, plus one truly")
    print("  absent res://gone.glb:")
    print()
    print(f"    ok                        {d['ok']}")
    print(f"    missing_resource_count    {d['missing_resource_count']}")
    if "misrooted_resource_count" in d:
        print(f"    misrooted_resource_count  {d['misrooted_resource_count']}")
    else:
        print("    misrooted_resource_count  (unpatched -- the misrooted one")
        print("                               is counted as RESOLVED)")
    for issue in d["issues"]:
        print(f"      {issue}")
    return 0


def _verify(export_dir: Path) -> int:
    sys.path.insert(0, str(Path.cwd() / "level_factory"))
    from packages.exporting.closure import scan_closure
    d = scan_closure(export_dir).as_dict()
    print(f"  {export_dir}")
    for key in ("resource_count", "missing_resource_count",
                "misrooted_resource_count", "absolute_path_count",
                "external_reference_count", "required_plugin_count",
                "required_autoload_count", "ok"):
        if key in d:
            print(f"    {key:<26} {d[key]}")
    mis = [i for i in d["issues"] if "MISROOTED" in i]
    if mis:
        print(f"\n    {len(mis)} misrooted -- scenes moved without their "
              f"references rewritten:")
        for i in mis[:5]:
            print(f"      {i}")
        if len(mis) > 5:
            print(f"      ... and {len(mis) - 5} more")
    other = [i for i in d["issues"] if "MISROOTED" not in i]
    if other:
        print(f"\n    {len(other)} other:")
        for i in other[:5]:
            print(f"      {i}")
        if len(other) > 5:
            print(f"      ... and {len(other) - 5} more")
    on_disk = export_dir / "export_closure_scan.json"
    if on_disk.is_file():
        try:
            was = json.loads(on_disk.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            was = {}
        print(f"\n    the scan ON DISK says ok={was.get('ok')}, "
              f"{was.get('missing_resource_count')} missing -- re-export to "
              f"refresh it")
    return 0 if d["ok"] else 1


def main(argv: list[str]) -> int:
    if "--explain" in argv:
        return _explain()
    if "--verify" in argv:
        i = argv.index("--verify")
        if i + 1 >= len(argv):
            raise SystemExit("--verify needs a path to an export dir")
        return _verify(Path(argv[i + 1]))

    root = Path.cwd()
    for rel in EDITS:
        if not (root / rel).is_file():
            raise SystemExit(f"cannot find {rel} under {root} -- run from the "
                             f"factory root")

    if "--revert" in argv:
        bad = 0
        for rel in EDITS:
            path = root / rel
            side = path.with_suffix(path.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {path.name}")
                bad = 1
                continue
            path.write_bytes(side.read_bytes())
            print(f"  reverted     {path.name}")
        return bad

    check = "--check" in argv
    for rel, edits in EDITS.items():
        code = _apply(root / rel, edits, check=check)
        if code:
            return code
    if not check:
        print()
        print("  EXPECT THE NUMBER TO JUMP. These references were always there;")
        print("  the judge was looking at them and calling them fine.")
        print()
        print("  python patch_lf_closure_misrooted.py --verify \\")
        print("    lot-demo-ws\\.level_factory\\exports\\"
              "lot_demo_001.portable-godot")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
