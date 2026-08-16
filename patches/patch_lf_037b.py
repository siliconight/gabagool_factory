r"""level_factory 0.37.0 (amendment) -- the graybox is a base, not an alternative.

    python patches\patch_lf_037b.py --check
    python patches\patch_lf_037b.py
    python patches\patch_lf_037b.py --selftest
    python patches\patch_lf_037b.py --revert

Run from the FACTORY ROOT. Apply AFTER patch_lf_037.py.

WHAT THE GUARD FOUND

0.37.0's `ExportContentError` fired on PURE-SHELL -- two unit tests and the
integration export test. The guard is right and pure-shell is broken.

    base_dir = handoff_dir if (handoff_dir and handoff_dir.exists()) else graybox_dir

An either/or. The comment three lines above already describes the intent
correctly -- "With the Gameplay layer this is the Dispatch handoff ...;
without it, the graybox Lot site IS the deliverable base" -- but a layer is
something you put ON a base, not something you swap for it. The moment a
mission gained a `dispatch_handoff`, Lot's `site.tscn` stopped shipping.

MEASURED ON lot_demo_001, TWO EXPORTS OF THE SAME MISSION

    lot_demo_001.pure-shell   2026-08-10   site.tscn 25,378 B   entry 688 B
    LF_lot_demo_001.art-unlit 2026-08-15   no site.tscn         entry 571 B

The older one predates this mission having a handoff, so `base_dir` fell
through to the graybox and carried the site. Dispatch's handoff `out/` holds
`mission.tscn` at 65,493 bytes and no `site.tscn` at all -- and
`write_entry_scene` overwrites that 65 KB scene with its own ~600 byte stub,
so what Dispatch built is not what ships either way.

For every mode carrying art this went unnoticed, because the themed assembly
replaces the graybox one. Pure-shell has no replacement, so it shipped an
entry that instanced nothing -- and closure passed it, because closure walks
FROM the entry.

THE FIX, AND WHY IT IS NARROW

The graybox tree is copied UNDER the handoff for pure-shell only. Art modes
take their assembly from `themed_site_assemble` in section 2.5, and laying
the graybox underneath them would ship greybox geometry a themed package has
no use for -- the same reasoning that keeps `art-unlit` out of the
composed-root branch.

`skip` still applies to it, so a pure-shell export drops Lux's outputs from
the graybox copy exactly as it does from the handoff.

WHAT THIS DOES NOT FIX, AND IS WORTH ITS OWN ITEM

Dispatch writes a 65,493-byte `mission.tscn` -- the composed mission scene --
and every export throws it away and writes a stub in its place. That may be
right (an export carries one entry, and export.py's comment says so
deliberately) or it may be a second thing nobody has opened. It is recorded
here rather than changed, because nothing measured says which.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

EXPORT = "level_factory/packages/exporting/export.py"
NEW_TEST = "level_factory/tests/unit/test_pure_shell_base.py"
CHANGELOG = "level_factory/CHANGELOG.md"
SIDECAR = ".pre_037b"

EDITS: list[tuple[str, str, str]] = [
    (EXPORT,
     "    base_dir = handoff_dir if (handoff_dir and handoff_dir.exists()) else graybox_dir\n"
     "    if base_dir and base_dir.exists():\n"
     "        _copy_tree(base_dir, export_dir, skip=skip)\n",

     "    base_dir = handoff_dir if (handoff_dir and handoff_dir.exists()) else graybox_dir\n"
     "    # THE GRAYBOX IS A BASE, NOT AN ALTERNATIVE. The line above is an\n"
     "    # either/or, and the comment three lines above it already describes\n"
     "    # the intent correctly: the Dispatch handoff is a LAYER, and a layer\n"
     "    # goes on a base rather than replacing it. The moment a mission gained\n"
     "    # a dispatch_handoff, Lot's site.tscn stopped shipping.\n"
     "    #\n"
     "    # Measured 2026-08-15, two exports of lot_demo_001: the one from\n"
     "    # 2026-08-10 -- before this mission had a handoff -- carries a 25,378\n"
     "    # byte site.tscn and a 688 byte entry; today's carries neither, and\n"
     "    # its entry instances nothing. Closure passed it, because closure\n"
     "    # walks FROM the entry.\n"
     "    #\n"
     "    # PURE-SHELL ONLY. Art modes take their assembly from\n"
     "    # themed_site_assemble in 2.5 below, and laying the graybox under a\n"
     "    # themed package would ship greybox geometry it has no use for -- the\n"
     "    # same reasoning that keeps art-unlit out of the composed-root branch.\n"
     "    if (profile.mode == MODE_PURE_SHELL and graybox_dir\n"
     "            and graybox_dir.exists() and base_dir is not graybox_dir):\n"
     "        _copy_tree(graybox_dir, export_dir, skip=skip)\n"
     "    if base_dir and base_dir.exists():\n"
     "        _copy_tree(base_dir, export_dir, skip=skip)\n"),

    (CHANGELOG,
     "new tests build one without it.\n",

     "new tests build one without it.\n"
     "\n"
     "AMENDED, SAME VERSION -- THE GRAYBOX IS A BASE, NOT AN ALTERNATIVE\n"
     "\n"
     "The new guard fired on PURE-SHELL, in two unit tests and the integration\n"
     "export test. It was right, and pure-shell was broken:\n"
     "\n"
     "    base_dir = handoff_dir if (handoff_dir and handoff_dir.exists())\n"
     "               else graybox_dir\n"
     "\n"
     "An either/or, where the comment three lines above already says the\n"
     "Dispatch handoff is a LAYER -- and a layer goes on a base rather than\n"
     "replacing it. The moment a mission gained a dispatch_handoff, Lot's\n"
     "site.tscn stopped shipping with it.\n"
     "\n"
     "Two exports of lot_demo_001 measure it: the one from 2026-08-10, before\n"
     "this mission had a handoff, carries a 25,378 byte site.tscn and a 688\n"
     "byte entry; today's carries neither and its entry instances nothing. For\n"
     "every mode carrying art this was invisible, because the themed assembly\n"
     "replaces the graybox one. Pure-shell has no replacement.\n"
     "\n"
     "The graybox tree is now copied UNDER the handoff for pure-shell only,\n"
     "with the same `skip` applied. Art modes are untouched.\n"
     "\n"
     "RECORDED, NOT CHANGED: Dispatch writes a 65,493 byte `mission.tscn` --\n"
     "the composed mission scene -- and every export discards it and writes a\n"
     "~600 byte stub instead. export.py says that is deliberate, an export\n"
     "carrying one entry. Whether it is still right is unmeasured.\n"),
]

NEW_FILES: dict[str, str] = {
    NEW_TEST: '''"""pure-shell keeps the graybox site once a mission gains a handoff.

Written after 0.37.0's entry guard fired on pure-shell. `base_dir` chose the
Dispatch handoff OR the graybox, and Dispatch's handoff carries no
`site.tscn` -- so a mission that grew a `dispatch_handoff` silently stopped
shipping the only scene a pure-shell package had to instance.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from packages.exporting.export import (  # noqa: E402
    MODE_PURE_SHELL, ExportProfile, export_mission,
)
from packages.exporting.localize import ExportContentError  # noqa: E402


def _mission(root, *, with_handoff=True):
    """A graybox with a site, and a Dispatch handoff that has none.

    Shaped from the real lot_demo_001: `dispatch_handoff/out` holds
    mission.tscn and the gameplay JSON, and no site.tscn at all.
    """
    graybox = root / "graybox"
    graybox.mkdir(parents=True)
    (graybox / "site.tscn").write_text("[gd_scene]\\n")
    (graybox / "site_base.glb").write_bytes(b"glTF")

    handoff = None
    if with_handoff:
        handoff = root / "handoff"
        handoff.mkdir(parents=True)
        (handoff / "mission_manifest.json").write_text("{}")
        (handoff / "gameplay_anchors.json").write_text("{}")
        # Dispatch's own entry, which the export replaces with its stub.
        (handoff / "mission.tscn").write_text("[gd_scene] dispatch\\n")
    return graybox, handoff


def _export(root, *, with_handoff=True):
    graybox, handoff = _mission(root, with_handoff=with_handoff)
    return export_mission(
        mission_id="m1", out_root=root / "exports",
        profile=ExportProfile(mode=MODE_PURE_SHELL),
        handoff_dir=handoff, presentation_dir=None, composed_root=None,
        themed_site_dir=None, graybox_dir=graybox,
        source_dir=None, tool_versions={}, layers=frozenset(),
    )


def test_pure_shell_without_a_handoff_still_works(tmp_path):
    """The path that never broke: graybox IS the base."""
    result = _export(tmp_path, with_handoff=False)
    assert (result.export_dir / "site.tscn").is_file()


def test_pure_shell_with_a_handoff_keeps_the_graybox_site(tmp_path):
    """THE REGRESSION. The handoff used to REPLACE the graybox."""
    result = _export(tmp_path)
    assert (result.export_dir / "site.tscn").is_file()


def test_the_handoff_content_still_lands(tmp_path):
    """A base, not a substitution -- both are in the package."""
    result = _export(tmp_path)
    names = {p.name for p in result.export_dir.rglob("*") if p.is_file()}
    assert "gameplay_anchors.json" in names
    assert "site_base.glb" in names


def test_the_entry_instances_the_graybox_site(tmp_path):
    result = _export(tmp_path)
    body = (result.export_dir / "mission.tscn").read_text()
    assert "res://site.tscn" in body
    assert "add_child" in body


def test_a_pure_shell_export_with_no_graybox_at_all_refuses(tmp_path):
    """The guard still guards. Nothing to instance is still an error."""
    handoff = tmp_path / "h"
    handoff.mkdir()
    (handoff / "mission_manifest.json").write_text("{}")
    with pytest.raises(ExportContentError):
        export_mission(
            mission_id="m1", out_root=tmp_path / "exports",
            profile=ExportProfile(mode=MODE_PURE_SHELL),
            handoff_dir=handoff, presentation_dir=None, composed_root=None,
            themed_site_dir=None, graybox_dir=None,
            source_dir=None, tool_versions={}, layers=frozenset(),
        )
''',
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _eol(raw: bytes) -> str:
    return "\r\n" if b"\r\n" in raw else "\n"


def _as(text: str, eol: str) -> str:
    return text if eol == "\n" else text.replace("\n", eol)


def _apply(root: Path, *, check: bool) -> int:
    by_file: dict[str, list[tuple[str, str]]] = {}
    for rel, old, new in EDITS:
        by_file.setdefault(rel, []).append((old, new))

    for rel, edits in by_file.items():
        p = root / rel
        if not p.is_file():
            print(f"REFUSING: {rel} is not here")
            return 1
        raw = p.read_bytes()
        eol = _eol(raw)
        out, done = raw.decode("utf-8"), 0
        for old, new in edits:
            old_f, new_f = _as(old, eol), _as(new, eol)
            if new_f in out:
                done += 1
                continue
            if out.count(old_f) != 1:
                print(f"REFUSING: {rel} -- an anchor occurs {out.count(old_f)} "
                      f"time(s), expected 1:\n    "
                      f"{old.strip().splitlines()[0][:72]}")
                return 1
            out = out.replace(old_f, new_f, 1)
        if done == len(edits):
            print(f"  already applied  {rel}")
            continue
        if p.suffix == ".py":
            try:
                compile(out, str(p), "exec")
            except SyntaxError as exc:
                print(f"REFUSING: {rel} -- does not parse after the edit: {exc}")
                return 1
        data = out.encode("utf-8")
        if data == raw:
            print(f"  already applied  {rel}")
            continue
        if check:
            print(f"  would patch  {rel}  {len(raw):,} -> {len(data):,} bytes "
                  f"({len(data) - len(raw):+,})")
            continue
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(raw)
        p.write_bytes(data)
        print(f"  patched      {rel}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")

    for rel, content in NEW_FILES.items():
        p = root / rel
        data = content.encode("utf-8")
        if p.is_file():
            if p.read_bytes() == data:
                print(f"  already applied  {rel}")
                continue
            print(f"REFUSING: {rel} exists and is not what this patch writes")
            return 1
        try:
            compile(content, str(p), "exec")
        except SyntaxError as exc:
            print(f"REFUSING: {rel} -- does not parse: {exc}")
            return 1
        if check:
            print(f"  would create {rel}  {len(data):,} bytes")
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        print(f"  created      {rel}  {len(data):,} bytes  "
              f"sha256 {_sha(data)[:16]}")
    return 0


def selftest(root: Path) -> int:
    import subprocess
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    lf = (root / "level_factory").resolve()

    def run(*paths):
        return subprocess.run([sys.executable, "-m", "pytest", *paths],
                              cwd=str(lf), capture_output=True, text=True)

    print("  the pure-shell base tests --")
    r = run("tests/unit/test_pure_shell_base.py")
    for line in (r.stdout + r.stderr).strip().splitlines()[-5:]:
        print(f"       {line}")
    check("PURE-SHELL KEEPS ITS SITE", r.returncode == 0)

    print()
    print("  the two closure tests the guard broke --")
    r2 = run("tests/unit/test_closure_export.py")
    for line in (r2.stdout + r2.stderr).strip().splitlines()[-5:]:
        print(f"       {line}")
    check("THEY PASS AGAIN", r2.returncode == 0)

    print()
    print("  the whole unit suite --")
    r3 = run("tests/unit")
    for line in (r3.stdout + r3.stderr).strip().splitlines()[-5:]:
        print(f"       {line}")
    check("UNIT IS GREEN", r3.returncode == 0)

    print()
    print("  service + integration -- ~2.5 min --")
    r4 = run("tests/service", "tests/integration")
    for line in (r4.stdout + r4.stderr).strip().splitlines()[-5:]:
        print(f"       {line}")
    check("THE INTEGRATION EXPORT TEST PASSES AGAIN", r4.returncode == 0)

    src = (root / EXPORT).read_text(encoding="utf-8")
    code = "\n".join(ln for ln in src.splitlines()
                     if not ln.strip().startswith("#"))
    check("only pure-shell lays the graybox underneath",
          "if (profile.mode == MODE_PURE_SHELL and graybox_dir" in code)
    check("and the skip set applies to it too",
          code.count("_copy_tree(graybox_dir, export_dir, skip=skip)") == 1)

    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    flat = " ".join(cl.split())
    check("the entry measures the regression rather than asserting it",
          "25,378 byte site.tscn" in flat)
    check("and records the discarded Dispatch scene as unmeasured",
          "Whether it is still right is unmeasured" in flat)

    print()
    print("  NOT VERIFIED HERE: the real exports. Re-run all three modes --")
    print("    export <mission> --mode portable-godot --format folder")
    print("    export <mission> --mode art-unlit     --format folder")
    print("    export <mission> --mode pure-shell    --format folder")
    print("    python tools\\probe_unlit_ab.py <ws> <mission>")

    print()
    print("  a layer goes on a base"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")
    if "--selftest" in argv:
        return selftest(root)
    if "--revert" in argv:
        bad = 0
        for rel in (EXPORT, CHANGELOG):
            p = root / rel
            side = p.with_suffix(p.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {rel}")
                bad = 1
                continue
            p.write_bytes(side.read_bytes())
            print(f"  reverted     {rel}")
        for rel, content in NEW_FILES.items():
            p = root / rel
            if not p.is_file():
                print(f"  already gone {rel}")
                continue
            if p.read_bytes() != content.encode("utf-8"):
                print(f"  KEPT (edited since) {rel}")
                bad = 1
                continue
            p.unlink()
            print(f"  removed      {rel}")
        return bad
    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("    python patches\\patch_lf_037b.py --selftest")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
