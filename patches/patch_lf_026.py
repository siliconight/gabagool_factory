r"""level_factory 0.26.0 -- the export name has one home.

    python patch_lf_026.py --check
    python patch_lf_026.py
    python patch_lf_026.py --selftest
    python patch_lf_026.py --revert

Run from the FACTORY ROOT (the directory holding `factory.manifest.json`).

STAGE 1 OF THREE, AND SMALLER THAN I SAID IT WOULD BE. `docs/EXPORT_NAMING.md`
specifies three names. This lands the one that needs no new information
plumbed through the exporter, and it says what the other two still need.

    stage 1  (here)  the build dir gets one definition, and the archive
                     stops losing its profile
    stage 1b         seed, build time and factory version plumbed to
                     `export_mission`, so the full archive name and
                     `LF_MANIFEST.json` can be written, and the archive
                     repacks under `LF_<mission>/`
    stage 2          interior renames: `lot/<building>/` -> `sites/<building>/`
                     and `assets/lot.glb` deleted

Splitting further than promised because stage 1 is verifiable by inspection
and stage 1b is not: it changes what `export_mission` is called with, and the
only proof it works is a real export run.

WHAT CHANGES

`packages/core/ids.py` gains ONE function, and only one, because the file that
would flag an unused sibling is `tools/never_wired.py` and it would be right:

    export_build_dir_name(mission_id, profile_mode) -> "LF_<mission>.<mode>"

It lives there because `ids.py` already owns `candidate_id` and `job_id`,
already documents that ids become directory names, and already refuses unsafe
input instead of sanitising it. This does the same: a mission id or a mode
carrying a path separator is refused, not rewritten.

Five call sites stop composing the name themselves:

    export.py       out_root / f"{mission_id}.{profile.mode}"
    export.py       zip_path = result.export_dir.with_suffix(".zip")
    commands        f"{mission_id}.portable-godot"        hardcoded, cmd_walk
    commands        export_root / f"{mission_id}.{mode}"
    commands        f"{mission_id}.{mode}.portability.json"

THE ZIP STOPS LOSING ITS PROFILE, AND THAT NEEDED NO PLUMBING AT ALL.
`with_suffix(".zip")` treats `.portable-godot` as a file extension and
replaces it, which is the entire reason the archive was `lot_demo_001.zip`.
Appending rather than substituting gives `LF_lot_demo_001.portable-godot.zip`
today, and the full name once stage 1b has the seed and the timestamp. Nobody
ever decided to drop the profile; a path helper ate it, and one line puts it
back.

WHAT THIS RENAMES ON DISK. `lot_demo_001.portable-godot/` becomes
`LF_lot_demo_001.portable-godot/`, and the same for `pure-shell` and the
`.portability.json` beside it. Old export directories are not migrated --
they are regenerable output under `.level_factory/`, and a migration that
renames build artifacts is a migration that can be wrong about which ones.

CHECKED BEFORE WRITING: no `.ps1` under `scripts/` names either profile, so
the runbooks do not compose this name and are unaffected. `cmd_walk` derives
the path to find what `cmd_export` just wrote, and derived it with the profile
HARDCODED four lines after setting it -- right today, and it would go on
looking in the same place if that default ever changed. It now asks for the
mode it set.

THE PORTABILITY TEST DERIVES A PATH THAT MOVES. `cmd_portability_test` builds
the export dir name itself; it is one of the five call sites and is updated
here, but its pass has to be RE-EARNED by a real run rather than assumed. That
is the one thing this patch cannot verify from where it was written.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

SIDECAR = ".pre_026"

IDS = "level_factory/packages/core/ids.py"
EXPORT = "level_factory/packages/exporting/export.py"
COMMANDS = "level_factory/apps/cli/commands/__init__.py"
VERSION_F = "level_factory/VERSION"
CHANGELOG = "level_factory/CHANGELOG.md"

OLD_V, NEW_V = "0.25.0", "0.26.0"

EDITS: list[tuple[str, str, str]] = [

    # ------------------------------------------------------------- ids.py --
    (IDS,
     'def namespaced_anchor(mission_id: str, anchor_id: str) -> str:\n',

     '#: The prefix every exported artifact carries. A level is the output of\n'
     '#: the whole DAG -- Deli Counter shells, Zoo kits, Pixelcoat materials,\n'
     '#: Patina wear, Lux light, Dispatch packaging, Lot assembly -- and naming\n'
     '#: the result for the assembler tells a recipient the wrong thing about\n'
     '#: what they have. See docs/EXPORT_NAMING.md.\n'
     'EXPORT_PREFIX = "LF"\n'
     '\n'
     '\n'
     'def export_build_dir_name(mission_id: str, profile_mode: str) -> str:\n'
     '    """The workspace directory one export builds into.\n'
     '\n'
     '    KEEPS THE PROFILE, unlike the folder that ends up inside the archive.\n'
     '    The workspace holds `portable-godot` and `pure-shell` at the same\n'
     '    time; give them one stable name and the second export silently\n'
     '    overwrites the first. The folder a RECIPIENT drops in has the\n'
     '    opposite requirement -- it must not change between exports, or every\n'
     '    `res://` path in their project moves. One name cannot do both, which\n'
     '    is why docs/EXPORT_NAMING.md specifies three.\n'
     '\n'
     '    Refused rather than sanitised, for the reason `job_id` gives: this\n'
     '    becomes a directory, and a silently rewritten name is output written\n'
     '    somewhere nobody looks.\n'
     '    """\n'
     '    mid, mode = str(mission_id).strip(), str(profile_mode).strip()\n'
     '    for label, value in (("mission id", mid), ("profile mode", mode)):\n'
     '        if not value:\n'
     '            raise ValueError(f"{label} is empty")\n'
     '        bad = sorted(set(value) & _UNSAFE_IN_A_PATH)\n'
     '        if bad or value in (".", ".."):\n'
     '            raise ValueError(\n'
     '                f"{label} {value!r} is not usable as a directory name "\n'
     '                f"(the export becomes a directory): {bad or value}")\n'
     '    return f"{EXPORT_PREFIX}_{mid}.{mode}"\n'
     '\n'
     '\n'
     'def namespaced_anchor(mission_id: str, anchor_id: str) -> str:\n'),

    # ---------------------------------------------------------- export.py --
    (EXPORT,
     'from packages.core.canonical import pretty_dumps\n'
     'from packages.core.hashing import hash_file\n',

     'from packages.core.canonical import pretty_dumps\n'
     'from packages.core.hashing import hash_file\n'
     'from packages.core.ids import export_build_dir_name\n'),

    (EXPORT,
     '    export_dir = out_root / f"{mission_id}.{profile.mode}"\n',
     '    export_dir = out_root / export_build_dir_name(mission_id, profile.mode)\n'),

    (EXPORT,
     '    zip_path = result.export_dir.with_suffix(".zip")\n',
     '    # APPEND, do not substitute. `with_suffix(".zip")` reads\n'
     '    # `.portable-godot` as a file extension and replaces it, which is the\n'
     '    # whole reason the archive was `lot_demo_001.zip` with no profile in\n'
     '    # it. Nobody decided to drop it; a path helper ate it.\n'
     '    zip_path = result.export_dir.parent / (result.export_dir.name + ".zip")\n'),

    # ---------------------------------------------------------- commands --
    # MERGE INTO THE EXISTING IMPORT, do not add a second one. The first draft
    # of this patch assumed `commands/__init__.py` did not import from
    # packages.core.ids and inserted its own line; the file has imported
    # `slugify` from there since before this work started. The guard caught it
    # and refused, which is the behaviour I want -- but the fix is to anchor on
    # the line that is actually there, not to special-case it in _apply.
    (COMMANDS,
     'from packages.core.ids import slugify\n',
     'from packages.core.ids import export_build_dir_name, slugify\n'),

    (COMMANDS,
     '    export_dir = ws.internal_dir / "exports" / f"{mission_id}.portable-godot"\n',
     '    # ASK FOR THE MODE THIS BLOCK SET, four lines up, rather than naming\n'
     '    # it again. Hardcoding it was right only for as long as the default\n'
     '    # above never changed, and nothing would have said so if it had.\n'
     '    export_dir = (ws.internal_dir / "exports"\n'
     '                  / export_build_dir_name(mission_id, export_args.mode))\n'),

    (COMMANDS,
     '    export_dir = export_root / f"{mission_id}.{mode}"\n',
     '    export_dir = export_root / export_build_dir_name(mission_id, mode)\n'),

    (COMMANDS,
     '    (export_root / f"{mission_id}.{mode}.portability.json").write_text(\n',
     '    (export_root / (export_build_dir_name(mission_id, mode)\n'
     '                    + ".portability.json")).write_text(\n'),
]

#: `commands/__init__.py` imports lazily inside functions in places; the three
#: call sites are in different functions, so the name is imported once at
#: module level -- on the `packages.core.ids` line that is already there.
COMMANDS_IMPORT_LINE = "from packages.core.ids import export_build_dir_name, slugify\n"
EXPORT_IMPORT_LINE = "from packages.core.ids import export_build_dir_name\n"

ENTRY = """## [0.26.0] - the export name has one home

`docs/EXPORT_NAMING.md`, accepted 2026-08-14, specifies three names for an
export. Before writing any of them, the grammar was measured: it is composed
in five places.

    export.py       out_root / f"{mission_id}.{profile.mode}"
    export.py       zip_path = result.export_dir.with_suffix(".zip")
    commands        f"{mission_id}.portable-godot"      hardcoded, in cmd_walk
    commands        export_root / f"{mission_id}.{mode}"
    commands        f"{mission_id}.{mode}.portability.json"

- **`ids.export_build_dir_name`** is now the only definition. It lives beside
  `candidate_id` and `job_id` because those already own the rule that an id
  becoming a directory is refused rather than sanitised, and this is the same
  rule for the same reason.
- **The build dir keeps the profile**, and the docstring says why: the
  workspace holds `portable-godot` and `pure-shell` at once, so one stable
  name would have the second export overwrite the first. The folder a
  recipient drops in has the opposite requirement — it must not change between
  exports or their `res://` paths move — which is why the doc specifies three
  names and not two. That correction came from reading `export.py:232`; the
  first draft of the doc had two and was wrong.
- **The archive stops losing its profile, and that needed no plumbing.**
  `with_suffix(".zip")` treats `.portable-godot` as a file extension and
  replaces it. That is the entire reason the archive was `lot_demo_001.zip`.
  Appending instead of substituting gives
  `LF_lot_demo_001.portable-godot.zip`.
- **`cmd_walk` stops hardcoding the profile** four lines after setting it. It
  was right, and it would have gone on looking in the same place if the
  default above it had ever changed.

- **The import merged into the line that was already there.**
  `commands/__init__.py` has imported `slugify` from `packages.core.ids`
  since before this work started. The patch's first draft assumed it imported
  nothing from there and was going to insert a second import line. It refused
  and named the file instead of writing one, which is the guard doing its
  job -- recorded because the near-miss is the useful part, not the fix.

Renames on disk: `lot_demo_001.portable-godot/` becomes
`LF_lot_demo_001.portable-godot/`, and the `.portability.json` beside it
follows. Existing export directories are not migrated — they are regenerable
output under `.level_factory/`.

NOT DONE HERE, AND NAMED SO IT IS NOT MISTAKEN FOR DONE: the full archive
name (`LF_<mission>_s<seed>_<utc>_f<factory>_<profile>.zip`) needs the seed,
the build time and the factory version plumbed to `export_mission`, which
changes its signature; `LF_MANIFEST.json` and repacking the archive under a
stable `LF_<mission>/` come with them. The interior renames
(`lot/<building>/` -> `sites/<building>/`, dropping `assets/lot.glb`) change
`res://` paths inside the package and want their own portability run.

`cmd_portability_test` composes one of the five names and is updated here, so
its pass has to be re-earned by a real run rather than assumed.
"""

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
    rc = 0
    by_file: dict[str, list[tuple[str, str]]] = {}
    for rel, old, new in EDITS:
        by_file.setdefault(rel, []).append((old, new))

    for rel, edits in by_file.items():
        p = root / rel
        if not p.is_file():
            print(f"REFUSING: {rel} is not here")
            return 1
        raw = p.read_bytes()
        body = raw.decode("utf-8")
        if body.count(_CRLF):
            print(f"REFUSING: {rel} has CRLF line endings; these anchors are LF")
            return 1
        out, done = body, 0

        for old, new in edits:
            if new in out:
                done += 1
                continue
            if out.count(old) != 1:
                print(f"REFUSING: {rel} -- an anchor occurs {out.count(old)} "
                      f"time(s), expected 1:\n    "
                      f"{old.strip().splitlines()[0][:72]}")
                return 1
            out = out.replace(old, new, 1)

        # Both files that call the helper must import it exactly once. This is
        # a post-condition on the result, not a rewrite: if the anchors above
        # ever stop producing it, this says so instead of shipping a NameError.
        if rel in (COMMANDS, EXPORT):
            want = (COMMANDS_IMPORT_LINE if rel == COMMANDS
                    else EXPORT_IMPORT_LINE)
            if out.count(want) != 1:
                print(f"REFUSING: {rel} -- the import of export_build_dir_name "
                      f"occurs {out.count(want)} time(s) after the edit, "
                      f"expected 1")
                return 1

        if done == len(edits):
            print(f"  already applied  {rel}")
            continue
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

    vp, cp = root / VERSION_F, root / CHANGELOG
    vbody = vp.read_text(encoding="utf-8")
    cbody = cp.read_text(encoding="utf-8")
    if NEW_V in vbody and f"## [{NEW_V}]" in cbody:
        print("  already applied  VERSION + CHANGELOG")
        return rc
    if OLD_V not in vbody:
        print(f"REFUSING: {VERSION_F} does not say {OLD_V} "
              f"(found {vbody.strip()!r})")
        return 1
    vout = vbody.replace(OLD_V, NEW_V, 1)
    cout = ENTRY + "\n" + cbody
    if check:
        print(f"  would bump   VERSION  {OLD_V} -> {NEW_V}")
        print(f"  would prepend CHANGELOG.md  "
              f"+{len(cout.encode('utf-8')) - len(cbody.encode('utf-8')):,} bytes")
        return rc
    for p, txt in ((vp, vbody), (cp, cbody)):
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(txt.encode("utf-8"))
    vp.write_bytes(vout.encode("utf-8"))
    cp.write_bytes(cout.encode("utf-8"))
    print(f"  bumped       VERSION  {OLD_V} -> {NEW_V}")
    print(f"  prepended    CHANGELOG.md")
    return rc


def selftest(root: Path) -> int:
    import importlib
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    lf = str((root / "level_factory").resolve())
    if lf not in sys.path:
        sys.path.insert(0, lf)
    ids = importlib.import_module("packages.core.ids")
    importlib.reload(ids)

    check("the name is prefixed and keeps the profile",
          ids.export_build_dir_name("lot_demo_001", "portable-godot")
          == "LF_lot_demo_001.portable-godot")
    check("pure-shell gets its own directory",
          ids.export_build_dir_name("lot_demo_001", "pure-shell")
          == "LF_lot_demo_001.pure-shell")
    check("the two profiles never collide",
          ids.export_build_dir_name("m", "portable-godot")
          != ids.export_build_dir_name("m", "pure-shell"))

    for label, args in (("a separator in the mission id", ("a/b", "x")),
                        ("a separator in the mode", ("m", "a\\b")),
                        ("a drive colon", ("m", "c:x")),
                        ("an empty mission id", ("", "x")),
                        ("a bare dotdot", ("..", "x"))):
        try:
            ids.export_build_dir_name(*args)
            check(f"{label} is refused", False)
        except ValueError:
            check(f"{label} is refused", True)

    src = (root / EXPORT).read_text(encoding="utf-8")
    check("export.py composes nothing itself",
          'f"{mission_id}.{profile.mode}"' not in src
          and "export_build_dir_name(mission_id, profile.mode)" in src)
    # The comment left behind QUOTES the call it replaced, so a whole-file
    # search finds it and calls the fix a failure. Read the code, not the
    # prose about the code -- the prose is the point of the comment.
    code = "\n".join(l for l in src.splitlines()
                     if not l.lstrip().startswith("#"))
    check("the zip appends instead of substituting",
          'with_suffix(".zip")' not in code
          and 'result.export_dir.name + ".zip"' in code)
    check("and says why, where the next reader will be",
          "reads\n    # `.portable-godot` as a file extension" in src)

    cmds = (root / COMMANDS).read_text(encoding="utf-8")
    check("commands composes nothing itself",
          'f"{mission_id}.portable-godot"' not in cmds
          and 'f"{mission_id}.{mode}"' not in cmds
          and 'f"{mission_id}.{mode}.portability.json"' not in cmds)
    check("cmd_walk asks for the mode it set",
          "export_build_dir_name(mission_id, export_args.mode)" in cmds)
    check("commands imports the one definition, once",
          cmds.count("from packages.core.ids import") == 1
          and cmds.count(COMMANDS_IMPORT_LINE) == 1)
    check("and slugify still comes in on that line",
          "slugify(" in cmds)
    check("three call sites use it",
          cmds.count("export_build_dir_name(") == 3)

    v = (root / VERSION_F).read_text(encoding="utf-8")
    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    check("VERSION is 0.26.0", NEW_V in v)
    check("one 0.26.0 entry", cl.count("## [0.26.0]") == 1)
    check("the entry says what is NOT done",
          "NOT DONE HERE" in cl and "LF_MANIFEST.json" in cl)
    check("and that portability must be re-earned",
          "re-earned by a real run" in cl)

    print()
    print("  one definition, five callers, and the zip keeps its profile"
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
        for rel in (IDS, EXPORT, COMMANDS, VERSION_F, CHANGELOG):
            p = root / rel
            side = p.with_suffix(p.suffix + SIDECAR)
            if not side.is_file():
                print(f"  no sidecar for {rel}")
                bad = 1
                continue
            p.write_bytes(side.read_bytes())
            print(f"  reverted     {rel}")
        return bad

    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("  python patches\\patch_lf_026.py --selftest")
        print()
        print("  THEN RE-EARN THE PORTABILITY PASS -- the export dir moved:")
        print("    level-factory -C <ws> export <mission> --mode portable-godot")
        print("    level-factory -C <ws> portability-test <mission> "
              "--mode portable-godot")
        print()
        print("  then, INSIDE level_factory:")
        print("    git -C level_factory add -A")
        print('    git -C level_factory commit -m "0.26.0 -- the export name '
              'has one home"')
        print('    git -C level_factory tag -a v0.26.0 -m "0.26.0"')
        print("    git -C level_factory push --follow-tags")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
