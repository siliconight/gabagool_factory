r"""probe_unlit_ab.py -- read two packages off disk and say how they differ.

    python probe_unlit_ab.py <workspace> [mission_id]

READ-ONLY. It opens no tool and runs no stage; it lists what is in two export
directories and what their manifests claim, so the art-unlit mode is judged
on an artifact rather than on a test that built one.

Run the two exports first:

    python level_factory\apps\cli\main.py -C <ws> export <mission> \
        --mode portable-godot --format folder
    python level_factory\apps\cli\main.py -C <ws> export <mission> \
        --mode art-unlit --format folder

WHAT TO LOOK FOR, and what would mean the seam is wrong:

  * ONLY IN LIT should be Lux and only Lux -- its two scene outputs AND its
    whole runtime under runtime/lux/. A NON-Lux file in that column is
    content art-unlit dropped and should not have.
  * ONLY IN UNLIT should be empty. A file that exists only in the unlit
    package means the mode is adding something rather than subtracting.
  * The shared file count should be nearly everything. If it is small, the
    composed-root branch is being skipped and the package has no art in it.
  * layers: the unlit manifest must not list `light`, and must list `art`.
  * entry: both name mission.tscn; the unlit one must instance site.tscn and
    must not mention lux.applied.tscn.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

MANIFEST = "LF_MANIFEST.json"


def _pkg(exports: Path, mission: str, mode: str) -> Path:
    # Same spelling as packages.core.ids.export_build_dir_name, written out
    # rather than imported: this is a probe, and a probe that asks the code
    # what to look for cannot notice the code looking in the wrong place.
    return exports / f"LF_{mission}.{mode}"


def _files(root: Path) -> dict[str, int]:
    if not root.is_dir():
        return {}
    return {str(p.relative_to(root)).replace("\\", "/"): p.stat().st_size
            for p in root.rglob("*") if p.is_file()}


def _manifest(root: Path) -> dict:
    p = root / MANIFEST
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except ValueError as exc:
        return {"__unreadable__": str(exc)}


def main(argv: list[str]) -> int:
    if not argv:
        raise SystemExit(__doc__.strip().splitlines()[2].strip())
    ws = Path(argv[0]).resolve()
    mission = argv[1] if len(argv) > 1 else "lot_demo_001"
    exports = ws / ".level_factory" / "exports"
    if not exports.is_dir():
        print(f"no exports directory: {exports}")
        return 2

    lit_dir = _pkg(exports, mission, "portable-godot")
    unlit_dir = _pkg(exports, mission, "art-unlit")

    print(f"workspace : {ws}")
    print(f"mission   : {mission}")
    print(f"exports/  : {sorted(p.name for p in exports.iterdir())}")
    print()

    missing = [d for d in (lit_dir, unlit_dir) if not d.is_dir()]
    if missing:
        for d in missing:
            print(f"MISSING: {d.name} -- run that export first")
        return 2

    lit, unlit = _files(lit_dir), _files(unlit_dir)
    only_lit = sorted(set(lit) - set(unlit))
    only_unlit = sorted(set(unlit) - set(lit))
    shared = sorted(set(lit) & set(unlit))

    print(f"  lit    : {len(lit):>5} files, {sum(lit.values()):>12,} bytes")
    print(f"  unlit  : {len(unlit):>5} files, {sum(unlit.values()):>12,} bytes")
    print(f"  shared : {len(shared):>5} files")
    print()

    print(f"ONLY IN LIT ({len(only_lit)}) -- should be Lux and only Lux: its "
          f"scene outputs AND its runtime")
    for rel in only_lit[:40]:
        print(f"    {rel}  ({lit[rel]:,} B)")
    if len(only_lit) > 40:
        print(f"    ... and {len(only_lit) - 40} more")
    print()

    print(f"ONLY IN UNLIT ({len(only_unlit)}) -- should be EMPTY")
    for rel in only_unlit[:40]:
        print(f"    {rel}  ({unlit[rel]:,} B)")
    print()

    # Files present in both but differing in size: the mode is meant to
    # SUBTRACT, so anything it also rewrites is worth seeing.
    changed = [r for r in shared if lit[r] != unlit[r]]
    print(f"IN BOTH BUT DIFFERENT SIZE ({len(changed)}) -- expect only "
          f"{MANIFEST} and project.godot")
    for rel in changed[:20]:
        print(f"    {rel}  lit {lit[rel]:,} B  unlit {unlit[rel]:,} B")
    print()

    ml, mu = _manifest(lit_dir), _manifest(unlit_dir)
    print("MANIFESTS")
    for label, m in (("lit  ", ml), ("unlit", mu)):
        print(f"  {label}  profile={m.get('profile')!r}  "
              f"layers={m.get('layers')}  "
              f"package_dir={m.get('package_dir')!r}")
        print(f"         archive={m.get('archive_name')!r}")
    print()

    entry_lit = (lit_dir / "mission.tscn")
    entry_unlit = (unlit_dir / "mission.tscn")
    print("ENTRY SCENES")
    for label, p in (("lit  ", entry_lit), ("unlit", entry_unlit)):
        if not p.is_file():
            print(f"  {label}  MISSING mission.tscn")
            continue
        body = p.read_text(encoding="utf-8", errors="replace")
        instanced = [tok for tok in ("presentation/lux.applied.tscn",
                                     "site.tscn") if tok in body]
        print(f"  {label}  instances {instanced}")
    print()

    # The verdict, stated as the questions rather than as a score. Each line
    # is something that would be wrong, not something that would be nice.
    bad = 0

    def verdict(label: str, ok: bool, detail: str = "") -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'LOOK'} {label}{detail}")

    # EVERYTHING LUX, not just the two scene files. An unlit package correctly
    # drops the whole Lux runtime as well -- presets, rigs, shaders, the
    # emissive binder -- roughly 250 KB of GDScript that a team bringing its
    # own renderer has no use for. The first version of this listed only
    # `_PRESENTATION_FILES` and reported 31 correctly-dropped files as
    # something to look at.
    def _is_lux(rel: str) -> bool:
        return (rel.startswith("presentation/")
                or rel.startswith("runtime/lux/")
                or "lux." in rel.rsplit("/", 1)[-1])

    lux_names = {r for r in only_lit if _is_lux(r)}
    stray = [r for r in only_lit if not _is_lux(r)]
    verdict("the unlit package drops Lux's outputs and runtime",
            bool(lux_names), f" -- {len(lux_names)} file(s)")
    verdict("and drops nothing else", not stray,
            f" -- {len(stray)} NON-Lux file(s) missing from unlit: "
            f"{stray[:5]}" if stray else "")
    verdict("it adds nothing", not only_unlit)
    verdict("it still carries the art",
            len(shared) > 0 and len(unlit) > 2,
            f" -- {len(unlit)} files")
    verdict("the unlit manifest does not claim the light layer",
            "light" not in (mu.get("layers") or []))
    verdict("and does claim the art layer",
            "art" in (mu.get("layers") or []))
    verdict("the lit manifest still claims light",
            "light" in (ml.get("layers") or []))
    verdict("both packages share an interior folder name",
            ml.get("package_dir") == mu.get("package_dir"))
    verdict("the two archives are named apart",
            ml.get("archive_name") != mu.get("archive_name"))

    print()
    print("  the two packages differ only in the render"
          if not bad else f"  {bad} thing(s) to look at")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
