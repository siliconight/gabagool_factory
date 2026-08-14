r"""level_factory 0.27.0 -- stage 1b: the archive says which level it is.

    python patch_lf_027.py --check
    python patch_lf_027.py
    python patch_lf_027.py --selftest
    python patch_lf_027.py --revert

Run from the FACTORY ROOT.

WHAT THIS LANDS

`docs/EXPORT_NAMING.md` specifies three names. 0.26.0 landed the first (the
build directory). This lands the other two:

    LF_lot_demo_001_s5219_20260814T203226Z_f1.18.0_portable-godot.zip
    LF_lot_demo_001/                       the folder inside that archive
    LF_MANIFEST.json                       inside that folder

THE SIGNATURE CHANGES, AND IT CHANGES ADDITIVELY ON PURPOSE

`export_mission` gains five keyword-only parameters -- seed, candidate_id,
factory_version, factory_tag, built_utc -- and every one of them defaults to
None. `tests/unit/test_closure_export.py` calls `export_mission` with the old
argument set twice; making any of these required would break the unit suite
on a patch whose subject is a filename. Defaulting also decides the behaviour
for a caller that genuinely has nothing to pass, which is the real reason:

NOTHING IS OMITTED FROM A NAME. AN UNKNOWN PART IS WRITTEN `NA`.

    LF_m1_sNA_20260814T203226Z_fNA_portable-godot.zip

Dropping the part instead would give one artifact two grammars, and the doc's
argument for the timestamp -- "fixed width, so it sorts" -- dies the moment
the field before it can vanish. `fNA` also tells a recipient something true
and useful: the provenance was not recoverable at build time, so there is no
`factory.manifest.json` tag that pins what they are holding.

WHERE THE SEED COMES FROM

The functional lock first -- it is the approved, drift-checked record of which
candidate ships -- then the selection marker. `cmd_export` resolves it and
passes it in; `export_mission` never goes looking. Same split for the factory
version: the CLI walks up for `factory.manifest.json`, the tool is handed a
string or None. A tool that reaches up into the factory checkout to find out
what it is would be code at the factory level wearing a disguise.

THE ARCHIVE NAME IS COMPUTED ONCE, AT BUILD TIME

`export_mission` computes it and hangs it on `ExportResult`; `zip_export`
uses it. This is the same rule 0.26.0 established for the directory name, and
it is what lets `LF_MANIFEST.json` state `archive_name` and be right -- the
manifest is written before the archive exists, so any second composition of
that string is a chance for the file inside to disagree with the file
containing it.

THE ARCHIVE'S CONTENT IS STILL DETERMINISTIC; ITS NAME IS NOT

`test_export_zip_is_deterministic` stays green: entries are still sorted and
timestamps still fixed at 1980-01-01, so the same inputs still produce the
same bytes. The PATH now carries a build time, by design -- two exports of
one mission from different weeks must not look alike. The test asserts
existence and suffix, not the name, so it is unaffected. Naming this because
"deterministic" in that test's title now means something narrower than it did.

WHAT LF_MANIFEST.json CLAIMS, AND WHAT IT REFUSES TO

The doc's example shows `verified: {portability: PASS, ...}`. A build-time
manifest cannot say that. `portability-test` is a separate command that runs
AFTER the export, against the build directory -- at the moment this file is
written the answer does not exist. So `verified` carries the one check that
DID run inside the build (`export_closure`, the scan 0.25.0-era work put on
the export path), names portability under `not_run`, and carries a note
saying that pipeline-stage results are not visible from here and their
absence is not a claim they did not run. A manifest that lists only passes
invites the reader to assume the rest, which is the argument
`factory-v1.17.0`'s entry made about itself.

`spec_sha256` FROM THE DOC IS DELIBERATELY NOT IMPLEMENTED

The doc names one field. `FunctionalLock` carries two hashes -- deli_spec_hash
and lot_spec_hash -- and they answer different questions (what the shell
generator was told, what the assembler was told). Collapsing them into one
field named for neither is the kind of decision that looks like an
implementation detail and reads as a fact later. Left out, recorded here, and
the doc should be corrected or the field named before anything writes it.

NOT DONE, AND NAMED SO IT IS NOT MISTAKEN FOR DONE

Stage 2: the interior renames -- `lot/<building>/` -> `sites/<building>/`,
dropping `assets/lot.glb`. Those move `res://` paths INSIDE the package and
want their own portability run. Nothing here touches them.

`portability-test` does not update `LF_MANIFEST.json` after it passes. It
could, and then the build directory's manifest would carry a verdict the
archive's copy does not, which is worse than both being honest about when
they were written.

`HANDOFF.md` still opens with the same 437 bytes of prose it always has. The
doc says it should lead with these same facts for the human who opens it
first. It does not yet.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

IDS = "level_factory/packages/core/ids.py"
EXPORT = "level_factory/packages/exporting/export.py"
COMMANDS = "level_factory/apps/cli/commands/__init__.py"
VERSION_F = "level_factory/VERSION"
CHANGELOG = "level_factory/CHANGELOG.md"
SIDECAR = ".pre_027"

OLD_V, NEW_V = "0.26.0", "0.27.0"

IDS_NEW = '''

#: What a name part says when its value could not be established.
#:
#: WRITTEN, NEVER OMITTED. Dropping the part would give one artifact two
#: grammars, and the reason docs/EXPORT_NAMING.md gives for the timestamp --
#: "fixed width, so it sorts" -- stops holding the moment a field before it
#: can vanish. It also says something true: `fNA` tells a recipient the
#: provenance was not recoverable, so no factory tag pins what they hold.
UNKNOWN_PART = "NA"

#: An ISO-8601 instant, loose about the input so `_now()`'s output and a
#: hand-written stamp both land in the same place.
_ISO_UTC = re.compile(
    r"(\\d{4})-?(\\d{2})-?(\\d{2})[T ]?(\\d{2}):?(\\d{2}):?(\\d{2})")


def compact_utc(raw: str) -> str:
    """`2026-08-14T20:32:26.869174+00:00` -> `20260814T203226Z`.

    ISO-8601 basic, because a colon is illegal in a Windows filename and
    this string goes into one. Fixed width, so a directory listing sorts
    chronologically without anybody parsing anything.
    """
    m = _ISO_UTC.search(str(raw or ""))
    if not m:
        raise ValueError(f"not an ISO-8601 instant: {raw!r}")
    return "{}{}{}T{}{}{}Z".format(*m.groups())


def export_package_dir_name(mission_id: str) -> str:
    """The folder INSIDE the archive -- the one a recipient drops in.

    STABLE ACROSS EXPORTS, and that is the whole specification. This
    folder becomes part of every `res://` path in the recipient's
    project, so a build time or a seed in it would move every reference
    they wrote the last time they took an update. Dropping a newer export
    over an older one has to overwrite in place.

    Which is also why the seed is NOT here: shipping a different
    candidate is an update to the same mission, not a second thing to
    keep side by side.
    """
    mid = str(mission_id).strip()
    if not mid:
        raise ValueError("mission id is empty")
    bad = sorted(set(mid) & _UNSAFE_IN_A_PATH)
    if bad or mid in (".", ".."):
        raise ValueError(
            f"mission id {mid!r} is not usable as a directory name "
            f"(it becomes the package root): {bad or mid}")
    return f"{EXPORT_PREFIX}_{mid}"


def export_archive_name(mission_id: str, *, profile_mode: str,
                        seed=None, built_utc: str | None = None,
                        factory_version: str | None = None) -> str:
    """`LF_<mission>_s<seed>_<utc>_f<factory>_<profile>.zip`

    The archive is what gets sent and stored, so it is fully qualified --
    the opposite requirement from the folder inside it. See
    docs/EXPORT_NAMING.md for why these are two names and not one.

    TIME BEFORE FACTORY VERSION, on purpose: within one mission and seed
    the name then sorts chronologically. The other order does not, because
    `f1.9.0` sorts after `f1.17.0` lexically, which would list a
    nine-month-old export as the newest.

    `seed` and `factory_version` may be None; each renders as `NA` rather
    than disappearing. `built_utc` defaults to now, but a caller that
    wants the name and a manifest to agree should pass the same instant
    to both.
    """
    mid = str(mission_id).strip()
    mode = str(profile_mode).strip()
    for label, value in (("mission id", mid), ("profile mode", mode)):
        if not value:
            raise ValueError(f"{label} is empty")
        bad = sorted(set(value) & _UNSAFE_IN_A_PATH)
        if bad or value in (".", ".."):
            raise ValueError(
                f"{label} {value!r} is not usable in a filename: "
                f"{bad or value}")

    def _part(label: str, value) -> str:
        if value is None or str(value).strip() == "":
            return UNKNOWN_PART
        s = str(value).strip()
        bad = sorted(set(s) & _UNSAFE_IN_A_PATH)
        if bad:
            raise ValueError(
                f"{label} {s!r} is not usable in a filename: {bad}")
        return s

    stamp = compact_utc(built_utc) if built_utc else compact_utc(
        _dt.datetime.now(_dt.timezone.utc).isoformat())
    return (f"{EXPORT_PREFIX}_{mid}"
            f"_s{_part('seed', seed)}"
            f"_{stamp}"
            f"_f{_part('factory version', factory_version)}"
            f"_{mode}.zip")

'''

EDITS: list[tuple[str, str, str]] = [
    # -------------------------------------------------------------- ids.py --
    (IDS,
     "import re\n",
     "import datetime as _dt\nimport re\n"),

    (IDS,
     "\n\ndef namespaced_anchor(mission_id: str, anchor_id: str) -> str:\n",
     IDS_NEW + "\ndef namespaced_anchor(mission_id: str, anchor_id: str) -> str:\n"),

    # ----------------------------------------------------------- export.py --
    (EXPORT,
     "from packages.core.ids import export_build_dir_name\n",
     "from packages.core.ids import (export_archive_name,\n"
     "                               export_build_dir_name,\n"
     "                               export_package_dir_name)\n"),

    (EXPORT,
     "    zip_path: Path | None = None\n",
     "    zip_path: Path | None = None\n"
     "    #: Composed ONCE, at build time, and used by zip_export. The\n"
     "    #: manifest inside the package states this string before the\n"
     "    #: archive exists, so a second composition of it is a chance for\n"
     "    #: the file inside to disagree with the file containing it.\n"
     "    archive_name: str | None = None\n"
     "    package_dir_name: str | None = None\n"),

    (EXPORT,
     '            "zip_path": str(self.zip_path) if self.zip_path else None,\n'
     "        }\n",
     '            "zip_path": str(self.zip_path) if self.zip_path else None,\n'
     '            "archive_name": self.archive_name,\n'
     '            "package_dir_name": self.package_dir_name,\n'
     "        }\n"),

    (EXPORT,
     "    composed_root: Path | None = None,\n) -> ExportResult:\n",
     "    composed_root: Path | None = None,\n"
     "    # EVERY ONE OF THESE DEFAULTS TO None, and that is not laziness.\n"
     "    # tests/unit/test_closure_export.py calls this with the old\n"
     "    # argument set; a required parameter would fail the unit suite on a\n"
     "    # patch about filenames. It also decides the behaviour for a caller\n"
     "    # that has nothing to pass -- the part is written NA, not dropped.\n"
     "    seed=None,\n"
     "    candidate_id: str | None = None,\n"
     "    factory_version: str | None = None,\n"
     "    factory_tag: str | None = None,\n"
     "    built_utc: str | None = None,\n"
     ") -> ExportResult:\n"
     "    # ONE INSTANT, used by the archive name and the manifest both. Two\n"
     "    # calls to the clock would put two different times on one build.\n"
     "    built_utc = built_utc or _now()\n"
     "    archive_name = export_archive_name(\n"
     "        mission_id, profile_mode=profile.mode, seed=seed,\n"
     "        built_utc=built_utc, factory_version=factory_version)\n"
     "    package_dir_name = export_package_dir_name(mission_id)\n"),

    (EXPORT,
     "    return ExportResult(\n"
     "        mission_id=mission_id, mode=profile.mode, export_dir=export_dir,\n",

     "    # 5. LF_MANIFEST.json -- everything the folder name gave up.\n"
     "    #\n"
     "    # WRITTEN LAST, after build_resource_manifest has already walked the\n"
     "    # tree, so the package's resource manifest does not list a file that\n"
     "    # describes it.\n"
     "    #\n"
     "    # `verified` carries the one check that ran INSIDE this build.\n"
     "    # portability-test is a separate command that runs afterwards\n"
     "    # against the build directory, so at this moment its answer does not\n"
     "    # exist and claiming it would be inventing one. The note is there\n"
     "    # because a block listing only passes invites a reader to assume the\n"
     "    # rest -- and because the absence of walktest or nav-gate results\n"
     "    # here is a limit of what export can see, not a claim they were\n"
     "    # skipped.\n"
     "    (export_dir / EXPORT_MANIFEST_NAME).write_text(pretty_dumps({\n"
     '        "schema": EXPORT_MANIFEST_SCHEMA,\n'
     '        "mission": mission_id,\n'
     '        "candidate": candidate_id,\n'
     '        "seed": seed,\n'
     '        "profile": profile.mode,\n'
     '        "built_utc": built_utc,\n'
     '        "factory_version": factory_version,\n'
     '        "factory_tag": factory_tag or (\n'
     '            f"factory-v{factory_version}" if factory_version else None),\n'
     '        "tools": {k: v for k, v in sorted(tool_versions.items())},\n'
     '        "godot_version": profile.godot_version,\n'
     '        "package_dir": package_dir_name,\n'
     '        "archive_name": archive_name,\n'
     '        "layers": sorted(layers),\n'
     '        "verified": {\n'
     '            "export_closure": "ok" if scan.ok else "BROKEN",\n'
     '            "not_run": ["portability -- runs after the build, as a '
     'separate command"],\n'
     '            "note": "This block records what THIS BUILD checked. '
     "Pipeline-stage results (walktest, nav gate, grades) are not visible "
     'from here; their absence is not a claim they did not run.",\n'
     "        },\n"
     "    }), encoding=\"utf-8\")\n"
     "\n"
     "    return ExportResult(\n"
     "        mission_id=mission_id, mode=profile.mode, export_dir=export_dir,\n"
     "        archive_name=archive_name, package_dir_name=package_dir_name,\n"),

    (EXPORT,
     '    zip_path = result.export_dir.parent / (result.export_dir.name + ".zip")\n'
     '    files = sorted(p for p in result.export_dir.rglob("*") if p.is_file())\n',

     "    # The build-time name if there is one. The fallback is 0.26.0's\n"
     "    # behaviour, kept so a caller that built an ExportResult by hand --\n"
     "    # the unit suite does -- still gets an archive rather than a crash.\n"
     "    zip_path = result.export_dir.parent / (\n"
     '        result.archive_name or (result.export_dir.name + ".zip"))\n'
     "    # THE FOLDER INSIDE THE ARCHIVE IS NOT THE BUILD DIRECTORY. The\n"
     "    # build dir carries the profile so two profiles can coexist in one\n"
     "    # workspace; the folder a recipient drops in must NOT change between\n"
     "    # exports, or every res:// path they integrated moves. Same bytes,\n"
     "    # different name, and the archive is the only place that is true.\n"
     "    top = result.package_dir_name or result.export_dir.name\n"
     '    files = sorted(p for p in result.export_dir.rglob("*") if p.is_file())\n'),

    (EXPORT,
     "            arc = f.relative_to(result.export_dir.parent).as_posix()\n",
     "            arc = (Path(top) / f.relative_to(result.export_dir)).as_posix()\n"),

    # ----------------------------------------------------------- commands --
    (COMMANDS,
     "def _lock_path(ws: Workspace, mission_id: str) -> Path:\n",

     "def _factory_pin() -> tuple[str | None, str | None]:\n"
     '    """The factory version an export was built by, or (None, None).\n'
     "\n"
     "    Walks up from this file for factory.manifest.json. level_factory is\n"
     "    a tool repo that lives INSIDE the factory checkout and nothing hands\n"
     "    it the root -- `verify-manifest --factory` defaults to the working\n"
     "    directory, which is right only when someone is standing in the right\n"
     "    place, and an export should not depend on where it was launched.\n"
     "\n"
     "    RESOLVED HERE, IN THE CLI, AND PASSED DOWN. A tool that reached up\n"
     "    into the factory checkout to discover what it is would be code at\n"
     "    the factory level wearing a tool's directory name.\n"
     "\n"
     "    Not found returns None, which the archive name renders as `fNA`. A\n"
     "    guessed number is worse than an absent one: it points a reader at a\n"
     "    factory.manifest.json tag that never pinned this build.\n"
     '    """\n'
     "    for d in Path(__file__).resolve().parents:\n"
     '        p = d / "factory.manifest.json"\n'
     "        if not p.is_file():\n"
     "            continue\n"
     "        try:\n"
     '            v = json.loads(p.read_text(encoding="utf-8")).get(\n'
     '                "factory_version")\n'
     "        except (OSError, ValueError):\n"
     "            return None, None\n"
     '        return (str(v), f"factory-v{v}") if v else (None, None)\n'
     "    return None, None\n"
     "\n"
     "\n"
     "def _lock_path(ws: Workspace, mission_id: str) -> Path:\n"),

    (COMMANDS,
     '    out_root = ws.internal_dir / "exports"\n'
     '    repos = ws.load_tools_local().get("repositories", {})\n',

     "    # WHICH LEVEL THIS IS. `lot_demo_001` at seed 5219 and at seed 5017\n"
     "    # are different levels that graded 60 and 40, and the archive name\n"
     "    # could not tell them apart. The functional lock first -- it is the\n"
     "    # approved, drift-checked record of which candidate ships -- then\n"
     "    # the selection marker. Neither existing is recorded as unknown\n"
     "    # rather than guessed.\n"
     "    selected_candidate = _resolve_selected_candidate(ws, mission_id)\n"
     "    export_seed = None\n"
     "    if lock_file.exists():\n"
     "        try:\n"
     "            export_seed = json.loads(\n"
     '                lock_file.read_text(encoding="utf-8")).get("seed")\n'
     "        except (OSError, ValueError):\n"
     "            export_seed = None\n"
     "    if export_seed is None and selected_candidate:\n"
     '        tail = selected_candidate.rsplit("_", 1)[-1]\n'
     "        export_seed = tail if tail.isdigit() else None\n"
     "    factory_version, factory_tag = _factory_pin()\n"
     "\n"
     '    out_root = ws.internal_dir / "exports"\n'
     '    repos = ws.load_tools_local().get("repositories", {})\n'),

    (COMMANDS,
     "        composed_root=compose_root if compose_root.exists() else None,\n"
     "    )\n",
     "        composed_root=compose_root if compose_root.exists() else None,\n"
     "        seed=export_seed, candidate_id=selected_candidate,\n"
     "        factory_version=factory_version, factory_tag=factory_tag,\n"
     "    )\n"),
]

#: Written into export.py beside the other module constants.
CONST_ANCHOR = '_PRESENTATION_FILES = {"lux.applied.tscn", "lux.quality.json"}\n'
CONST_NEW = (
    '_PRESENTATION_FILES = {"lux.applied.tscn", "lux.quality.json"}\n'
    "\n"
    "#: The first file inside the package, and named so a reader opens it.\n"
    "#: Everything the folder name gave up lives here -- see\n"
    "#: docs/EXPORT_NAMING.md.\n"
    'EXPORT_MANIFEST_NAME = "LF_MANIFEST.json"\n'
    'EXPORT_MANIFEST_SCHEMA = "level_factory.export_manifest.v1"\n')

ENTRY = """## [0.27.0] - the archive says which level it is

Stage 1b of `docs/EXPORT_NAMING.md`. 0.26.0 landed the build directory; this
lands the archive name, the stable folder inside it, and `LF_MANIFEST.json`.

    LF_lot_demo_001_s5219_20260814T203226Z_f1.18.0_portable-godot.zip
    LF_lot_demo_001/            the folder inside, stable across exports
    LF_MANIFEST.json            the first file inside that folder

- **`export_mission` gains five keyword-only parameters, all defaulting to
  `None`** -- seed, candidate_id, factory_version, factory_tag, built_utc.
  Defaulting is not laziness: `tests/unit/test_closure_export.py` calls this
  with the old argument set, and a required parameter would fail the unit
  suite on a patch about filenames. It also decides what a caller with
  nothing to pass gets, which is the part that matters.
- **An unknown part is written `NA`, never omitted.** `LF_m1_sNA_<utc>_fNA_
  portable-godot.zip`. Dropping it would give one artifact two grammars, and
  the doc's argument for the timestamp -- "fixed width, so it sorts" -- stops
  holding the moment a field before it can vanish. `fNA` is also a true
  statement: no factory tag pins that build.
- **The seed comes from the functional lock first**, the selection marker
  second. The lock is the approved, drift-checked record of which candidate
  ships. `cmd_export` resolves it; `export_mission` never goes looking.
- **The factory version is resolved in the CLI by walking up for
  `factory.manifest.json`**, and passed down. A tool that reached up into the
  factory checkout to discover what it is would be code at the factory level
  wearing a tool's directory name.
- **The archive name is composed once, at build time**, hung on
  `ExportResult`, and used by `zip_export`. That is what lets
  `LF_MANIFEST.json` state `archive_name` and be right: the manifest is
  written before the archive exists, so a second composition of that string
  is a chance for the file inside to disagree with the file containing it.
- **The folder inside the archive is not the build directory.** The build dir
  carries the profile so two profiles coexist in one workspace; the dropped
  folder must not change between exports or every `res://` path a recipient
  integrated moves. `zip_export` rewrites the arcname prefix; the bytes are
  identical.

THE CONTENT IS STILL DETERMINISTIC; THE NAME IS NOT

Entries are still sorted and timestamps still fixed at 1980-01-01, so the
same inputs still produce the same archive bytes.
`test_export_zip_is_deterministic` asserts existence and suffix, not the
name, and stays green. But the PATH now carries a build time by design --
two exports of one mission from different weeks must not look alike -- so
"deterministic" in that test's title now means something narrower than it
did, and this says so rather than letting a reader find out.

WHAT LF_MANIFEST.json REFUSES TO CLAIM

The doc's example shows `verified: {portability: PASS}`. A build-time
manifest cannot say that: `portability-test` runs afterwards, as a separate
command, and at the moment the file is written the answer does not exist. So
`verified` carries `export_closure` -- the one check that ran inside this
build -- names portability under `not_run`, and carries a note that
pipeline-stage results are not visible from here and their absence is not a
claim they were skipped. A block listing only passes invites the reader to
assume the rest.

`spec_sha256` IS DELIBERATELY NOT IMPLEMENTED

The doc names one field. `FunctionalLock` carries two hashes -- deli and lot
-- answering different questions: what the shell generator was told, and what
the assembler was told. Collapsing them into one field named for neither is
the kind of decision that looks like an implementation detail and reads as a
fact later. Left out, and the doc should name the field before anything
writes it.

NOT DONE HERE

Stage 2, the interior renames (`lot/<building>/` -> `sites/<building>/`,
dropping `assets/lot.glb`), which move `res://` paths inside the package and
want their own portability run. `portability-test` does not update
`LF_MANIFEST.json` afterwards -- it could, and then the build directory's
copy would carry a verdict the archive's copy does not. `HANDOFF.md` still
opens with its original 437 bytes; the doc says it should lead with these
same facts for the human who opens it first.
"""

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
    by_file: dict[str, list[tuple[str, str]]] = {}
    for rel, old, new in EDITS:
        by_file.setdefault(rel, []).append((old, new))
    by_file.setdefault(EXPORT, []).insert(0, (CONST_ANCHOR, CONST_NEW))

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

        # Post-conditions, not rewrites: if the anchors above ever stop
        # producing these, say so instead of shipping a NameError.
        if rel == EXPORT:
            for name in ("export_archive_name", "export_package_dir_name",
                         "EXPORT_MANIFEST_NAME"):
                if name not in out:
                    print(f"REFUSING: {rel} does not define or import {name} "
                          f"after the edit")
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
        return 0
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
        return 0
    for p, txt in ((vp, vbody), (cp, cbody)):
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(txt.encode("utf-8"))
    vp.write_bytes(vout.encode("utf-8"))
    cp.write_bytes(cout.encode("utf-8"))
    print(f"  bumped       VERSION  {OLD_V} -> {NEW_V}")
    print("  prepended    CHANGELOG.md")
    return 0


def selftest(root: Path) -> int:
    import importlib
    import json
    import zipfile
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

    STAMP = "2026-08-14T20:32:26.869174+00:00"
    check("the clock is normalised to ISO-8601 basic",
          ids.compact_utc(STAMP) == "20260814T203226Z")
    check("and an already-compact stamp survives it unchanged",
          ids.compact_utc("20260814T203226Z") == "20260814T203226Z")

    name = ids.export_archive_name(
        "lot_demo_001", profile_mode="portable-godot", seed=5219,
        built_utc=STAMP, factory_version="1.18.0")
    check("the archive name is the doc's grammar",
          name == "LF_lot_demo_001_s5219_20260814T203226Z_f1.18.0"
                  "_portable-godot.zip")
    check("and Path still reads .zip off it",
          Path(name).suffix == ".zip")

    na = ids.export_archive_name("m1", profile_mode="portable-godot",
                                 built_utc=STAMP)
    check("an unknown part is written NA, not dropped",
          na == "LF_m1_sNA_20260814T203226Z_fNA_portable-godot.zip")
    check("so both names have the same number of fields",
          len(na.split("_")) == len(name.replace("lot_demo_001", "x")
                                    .split("_")))

    check("time sorts before factory version",
          name.index("20260814T203226Z") < name.index("f1.18.0"))
    a = ids.export_archive_name("m", profile_mode="p", seed=1,
                                built_utc="2026-01-02T03:04:05Z",
                                factory_version="1.17.0")
    b = ids.export_archive_name("m", profile_mode="p", seed=1,
                                built_utc="2026-02-02T03:04:05Z",
                                factory_version="1.9.0")
    check("so a newer export sorts after an older one with a lower factory",
          a < b)

    check("the package dir drops the profile and the seed",
          ids.export_package_dir_name("lot_demo_001") == "LF_lot_demo_001")
    check("and is not the build dir name",
          ids.export_package_dir_name("lot_demo_001")
          != ids.export_build_dir_name("lot_demo_001", "portable-godot"))

    for label, kw in (
            ("a separator in the mission id",
             dict(mission_id="a/b", profile_mode="p")),
            ("a separator in the seed",
             dict(mission_id="m", profile_mode="p", seed="a/b")),
            ("a drive colon in the factory version",
             dict(mission_id="m", profile_mode="p", factory_version="c:1")),
            ("an empty mission id", dict(mission_id="", profile_mode="p"))):
        try:
            ids.export_archive_name(kw.pop("mission_id"), **kw)
            check(f"{label} is refused", False)
        except ValueError:
            check(f"{label} is refused", True)

    # A real export, end to end, in a temp workspace.
    import tempfile
    exp = importlib.import_module("packages.exporting.export")
    importlib.reload(exp)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        handoff = tmp / "handoff"
        handoff.mkdir()
        (handoff / "mission.tscn").write_text("[gd_scene]\n", encoding="utf-8")
        result = exp.export_mission(
            mission_id="m1", handoff_dir=handoff, presentation_dir=None,
            source_dir=None, profile=exp.ExportProfile(),
            tool_versions={"lot": "0.41.0"}, out_root=tmp / "exports",
            seed=5219, candidate_id="m1.candidate.seed_5219",
            factory_version="1.18.0", built_utc=STAMP)

        check("the build dir still keeps the profile",
              result.export_dir.name == "LF_m1.portable-godot")
        check("the archive name is carried on the result",
              result.archive_name ==
              "LF_m1_s5219_20260814T203226Z_f1.18.0_portable-godot.zip")

        mf = result.export_dir / exp.EXPORT_MANIFEST_NAME
        check("LF_MANIFEST.json is in the package", mf.is_file())
        man = json.loads(mf.read_text(encoding="utf-8"))
        check("it carries the seed the caller passed", man.get("seed") == 5219)
        check("and the candidate", man.get("candidate")
              == "m1.candidate.seed_5219")
        check("and the factory tag it implies",
              man.get("factory_tag") == "factory-v1.18.0")
        check("and the archive name, before the archive exists",
              man.get("archive_name") == result.archive_name)
        check("and the same instant as the name",
              man.get("built_utc") == STAMP)
        check("it does NOT claim portability",
              "portability" not in man["verified"])
        check("it names portability under not_run",
              any("portability" in s
                  for s in man["verified"].get("not_run", [])))
        check("and says pipeline results are not visible from here",
              "not a claim they did not run" in man["verified"].get("note", ""))

        # The manifest must not describe itself into the resource manifest.
        rm = json.loads((result.export_dir / "portable_resource_manifest.json")
                        .read_text(encoding="utf-8"))
        check("the resource manifest does not list LF_MANIFEST.json",
              exp.EXPORT_MANIFEST_NAME not in json.dumps(rm))

        z = exp.zip_export(result)
        check("the archive is written under the build-time name",
              z.name == result.archive_name)
        with zipfile.ZipFile(z) as zf:
            tops = {n.split("/", 1)[0] for n in zf.namelist()}
            names = set(zf.namelist())
        check("everything inside sits under one stable folder",
              tops == {"LF_m1"})
        check("which is NOT the build dir name",
              "LF_m1.portable-godot" not in tops)
        check("and the manifest is in there",
              f"LF_m1/{exp.EXPORT_MANIFEST_NAME}" in names)

        # 0.26.0's fallback must survive for a hand-built result.
        hand = exp.ExportResult(mission_id="m1", mode="portable-godot",
                                export_dir=result.export_dir)
        z2 = exp.zip_export(hand)
        check("a result with no build-time name still gets an archive",
              z2.name == "LF_m1.portable-godot.zip")

    src = (root / EXPORT).read_text(encoding="utf-8")
    check("export.py composes the archive name in exactly one place",
          src.count("export_archive_name(") == 1)
    check("and zip_export keeps 0.26.0's fallback for a hand-built result",
          '.name + ".zip"' in src)
    cmds = (root / COMMANDS).read_text(encoding="utf-8")
    check("the CLI resolves the factory pin and passes it down",
          "_factory_pin()" in cmds and "factory_version=factory_version" in cmds)
    check("and prefers the lock over the marker for the seed",
          cmds.index("export_seed = json.loads(")
          < cmds.index("if export_seed is None and selected_candidate:"))

    v = (root / VERSION_F).read_text(encoding="utf-8")
    cl = (root / CHANGELOG).read_text(encoding="utf-8")
    check(f"VERSION is {NEW_V}", NEW_V in v)
    check(f"one {NEW_V} entry", cl.count(f"## [{NEW_V}]") == 1)
    check("the entry says what is NOT done",
          "NOT DONE HERE" in cl and "sites/<building>/" in cl)
    check("and that spec_sha256 was left out on purpose",
          "spec_sha256" in cl and "DELIBERATELY NOT IMPLEMENTED" in cl)
    check("and that the archive name is no longer deterministic",
          "THE NAME IS NOT" in cl)

    print()
    print("  the archive names the level, and the folder inside does not move"
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
        print("    python patches\\patch_lf_027.py --selftest")
        print()
        print("  THEN A REAL RUN -- the archive name and its contents changed:")
        print("    python -m level_factory -C workspaces\\lot-demo-ws \\")
        print("        export lot_demo_001 --mode portable-godot --format zip")
        print("    python -m level_factory -C workspaces\\lot-demo-ws \\")
        print("        portability-test lot_demo_001 --mode portable-godot")
        print()
        print("  then, INSIDE level_factory:")
        print('    git -C level_factory commit -am "0.27.0 -- the archive says '
              'which level it is"')
        print(f'    git -C level_factory tag -a v{NEW_V} -m "{NEW_V}"')
        print("    git -C level_factory push --follow-tags")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
