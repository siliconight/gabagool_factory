r"""docs/EXPORT_NAMING.md, and item 42 narrowed to an accepted proposal.

    python patch_export_naming_doc.py --check
    python patch_export_naming_doc.py
    python patch_export_naming_doc.py --selftest
    python patch_export_naming_doc.py --revert

Run from the FACTORY ROOT. Requires item 42 to be in the roadmap already --
run `patch_roadmap_item42.py` first.

WHAT THIS LANDS. Item 42 states the properties an export name must carry and
deliberately does not pick a format. This lands the format, accepted
2026-08-14, as `docs/EXPORT_NAMING.md`, and moves item 42 to NARROWED: the
question is no longer what the name should carry, it is that nothing produces
it yet.

    LF_lot_demo_001_s5219_20260814T183045Z_f1.17.0_portable-godot.zip
    LF_lot_demo_001/                             <- the folder, stable

THE ONE STRUCTURAL DECISION. A timestamped name and a droppable folder pull
opposite ways: the folder becomes part of every `res://` path inside it, so
timestamping it changes every path on every export and anyone who integrated
the last one re-points their whole project to take an update. So the ARCHIVE
is fully qualified and the FOLDER is stable, with `LF_MANIFEST.json` carrying
what the folder name gave up.

WHY THE DOC AND NOT THE CODE, YET. `packages/core/ids.py` is the right home
for the function -- it already owns `candidate_id` and `job_id`, refuses
unsafe input rather than sanitising it, and is the only place that would keep
one definition of this grammar. But adding a public function nothing calls is
precisely what `tools/never_wired.py` exists to find, and it would be right.
The function lands in the same change that wires it into the exporter, which
needs the packaging path read first.

THE FOUR OPEN DECISIONS ARE TAKEN AT THEIR DEFAULTS and recorded as such, so a
later reader can tell a decision from an omission: `LF_` over
`levelfactory_`, dots kept in `f1.17.0`, no seed in the folder name, and the
profile on the archive including `pure-shell`.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROADMAP = "PIPELINE_ROADMAP.md"
DOC = "docs/EXPORT_NAMING.md"
SIDECAR = ".pre_exportnaming"

OLD_42 = ("*STATUS: OPEN 2026-08-14 -- raised. `.level_factory/exports/` holds "
          "`lot_demo_001.portable-godot/`, `lot_demo_001.pure-shell/` and "
          "`lot_demo_001.zip`; no name carries a factory version, a tool set "
          "or a date, and `assets/` ships `lot.glb` and `shell.glb` at 242,168 "
          "bytes with the same mtime*")

NEW_42 = ("*STATUS: NARROWED 2026-08-14 -- scheme accepted, nothing produces "
          "it yet. `docs/EXPORT_NAMING.md`: archive "
          "`LF_<mission>_s<seed>_<utc>_f<factory>_<profile>.zip`, folder "
          "`LF_<mission>/` stable so `res://` paths survive an update, "
          "provenance in `LF_MANIFEST.json`. Remaining work is one naming "
          "function in `packages/core/ids.py` and the callers that stop "
          "composing their own*")

DOC_TEXT = '''# Export naming

Accepted 2026-08-14. Written against roadmap item 42, which states the
*properties* a name must carry and deliberately does not pick a format. This
picks one.

Nothing produces these names yet. The remaining work is one function in
`level_factory/packages/core/ids.py` and the callers that stop composing their
own.

## The tension that shapes everything below

A timestamped name and a droppable folder pull in opposite directions.

Timestamps are what make an artifact identifiable in a downloads folder: two
exports of the same mission from different weeks must not look alike. But the
folder someone drops into their Godot project becomes part of every `res://`
path inside it. Put a timestamp there and the paths change on every export --
so anyone who integrated the last one has to re-point their references to take
an update, and `git diff` on their project is a rename of every file.

So: **the archive is fully qualified, the folder inside is stable.** The
archive is what gets sent and stored; the folder is what gets integrated. What
the folder loses from its name, it carries in a manifest as its first file.

## The archive name

```
LF_<mission>_s<seed>_<utc>_f<factory>_<profile>.zip
```

```
LF_lot_demo_001_s5219_20260814T183045Z_f1.17.0_portable-godot.zip
LF_lot_demo_001_s5219_20260814T183045Z_f1.17.0_pure-shell.zip
```

| part | example | why |
|---|---|---|
| `LF_` | `LF_` | **Origin.** This came out of a Level Factory, not out of `lot`. One tool of ten should not name the whole DAG's output. |
| `<mission>` | `lot_demo_001` | **Identity.** Unchanged; it is already the mission id. |
| `s<seed>` | `s5219` | **Which level.** `lot_demo_001` at seed 5219 and at seed 5017 are different levels that graded 60 and 40. The old name could not tell them apart. |
| `<utc>` | `20260814T183045Z` | **Time**, ISO-8601 basic. No colons -- illegal in Windows filenames. Fixed width, so it sorts. |
| `f<factory>` | `f1.17.0` | **Provenance.** One number recovers all ten tool versions via `factory.manifest.json` at tag `factory-v1.17.0`. `f` marks it as the factory version, not a tool's. |
| `<profile>` | `portable-godot` | **Profile.** On the archive, not just the folder -- the archive is what gets sent, and `lot_demo_001.zip` did not say which of the two it contained. |

**Time before factory version, on purpose.** Within one mission and seed the
name then sorts chronologically. The other order does not: `f1.9.0` sorts
after `f1.17.0` lexically, so a version-first name lists a nine-month-old
export as the newest.

## The folder inside

```
LF_lot_demo_001/
```

Stable across exports of the same mission. Dropping in a newer export
overwrites in place, which is what an update should do, and `res://` paths
survive it. Two different missions coexist without collision.

The seed is deliberately *not* here: swapping which candidate you ship is an
update to the same mission, not a second thing to keep side by side.

## `LF_MANIFEST.json`, the first file inside

Everything the folder name gave up, in the place a reader looks next. Nothing
here is new information -- it is `build.lock.json`, `export_profile.json` and
`factory.manifest.json` gathered into one file whose name says to open it.

```json
{
  "schema": "level_factory.export_manifest.v1",
  "mission": "lot_demo_001",
  "candidate": "lot_demo_001.candidate.seed_5219",
  "seed": 5219,
  "profile": "portable-godot",
  "built_utc": "2026-08-14T18:30:45Z",
  "factory_version": "1.17.0",
  "factory_tag": "factory-v1.17.0",
  "tools": { "deli_counter": "0.89.0", "lot": "0.41.0", "zoo": "0.36.0" },
  "spec_sha256": "...",
  "archive_name": "LF_lot_demo_001_s5219_20260814T183045Z_f1.17.0_portable-godot.zip",
  "godot_version": "4.7",
  "verified": {
    "portability": "PASS",
    "export_closure": "ok",
    "walktest": "19/20 sites, 0 stuck",
    "not_run": ["unit suites", "pack load check"]
  }
}
```

`archive_name` matters more than it looks: it is how an unpacked folder tells
you what it came from after someone has deleted the zip. `verified` carries
`not_run` for the same reason `factory-v1.17.0`'s entry does -- a record that
lists only what passed invites the reader to assume the rest.

`HANDOFF.md` (437 bytes today) should open with the same facts in prose, since
it is the first file a *human* opens.

## Interior names

Riskier than the two above, because these change `res://` paths inside the
package. Worth doing once, in the same change, rather than twice.

| today | proposed | why |
|---|---|---|
| `lot/<building>/` | `sites/<building>/` | Each holds `site.tscn` + `site_base.glb` + `art/`. They are sites. `lot/` names the assembler, not the content. |
| `assets/lot.glb` | *delete* | 242,168 bytes, identical mtime to `shell.glb`. The same asset twice, one copy named for a tool. |
| `assets/shell.glb` | unchanged | It is the Deli Counter shell and the name says so. |
| `runtime/lux/` | unchanged | Correctly named -- it *is* Lux's runtime, and the recipient needs to know that to update it. |

The rule that separates those last two rows: **name a directory for a tool
only when the recipient needs to know which tool owns it.** They need that for
`runtime/lux/`, because it is a dependency they may update independently. They
do not need it for a folder of assembled sites.

## Where the scheme lives

One function, in `level_factory/packages/core/ids.py` -- which already owns
`candidate_id` and `job_id`, and already refuses unsafe input rather than
sanitising it. Imported everywhere, composed nowhere. `make_package.ps1`
currently builds a name of its own; left alone it will build a fourth one. A
naming convention enforced by convention is a naming convention until the next
Tuesday.

Worth a `--check` mode that asserts an existing export's name matches what the
function would produce, so drift is detectable rather than discovered.

## What this costs

* Every `res://` path under `lot/` moves to `sites/`. One-time, mechanical,
  and it invalidates any integration that hardcoded the old paths -- including
  the portability test, which will need re-running rather than assumed.
* `assets/lot.glb` disappearing breaks anything referencing it by that name.
  `portable_resource_manifest.json` should say whether anything does before
  the file is removed.
* Longer archive names eat Windows' 260-character path budget. The deepest
  path inside the package is around 95 characters; 63 at the root leaves
  headroom, but a recipient who unpacks into a deep directory has less than
  they did.

## Decisions taken, and their defaults

Recorded so a later reader can tell a decision from an omission.

1. **`LF_`, not `levelfactory_`.** Shorter helps the path budget, and the
   prefix only has to be unambiguous among things this factory ships.
2. **Dots kept in `f1.17.0`.** Some tooling splits filenames on the first dot,
   and `f1-17-0` would be immune. The package already ships
   `lot_demo_001.portable-godot.portability.json`, so dots are established --
   but established is not the same as safe, and this is the decision most
   likely to be revisited.
3. **No seed in the folder name.** Shipping two candidates side by side was
   judged hypothetical rather than a workflow. If that changes, this flips.
4. **The profile appears on every archive, including `pure-shell`.** Even if
   `pure-shell` never leaves the building, a name that only sometimes carries
   its profile is a name you have to think about.
'''

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
    rp, dp = root / ROADMAP, root / DOC
    if not rp.is_file():
        print(f"REFUSING: {ROADMAP} is not here")
        return 1
    raw = rp.read_bytes()
    body = raw.decode("utf-8")

    if "**42. A level leaves the factory" not in body:
        print("REFUSING: item 42 is not in the roadmap -- run "
              "patch_roadmap_item42.py first")
        return 1

    done_doc = dp.is_file() and "Accepted 2026-08-14" in dp.read_text(
        encoding="utf-8", errors="replace")
    done_status = NEW_42 in body
    if done_doc and done_status:
        print("  already applied")
        return 0

    if not done_status:
        if body.count(OLD_42) != 1:
            print(f"REFUSING: item 42's status line occurs "
                  f"{body.count(OLD_42)} time(s), expected 1")
            return 1
        out = body.replace(OLD_42, NEW_42, 1)
        data = out.encode("utf-8")
        if data.count(_CRLF.encode()) != raw.count(_CRLF.encode()):
            print("REFUSING: the CRLF count changed on a single-line swap")
            return 1
    else:
        out, data = body, raw

    if dp.is_file() and not done_doc:
        print(f"REFUSING: {DOC} exists and is not this document")
        return 1

    if check:
        if not done_status:
            print(f"  would patch  {ROADMAP}  {len(raw):,} -> {len(data):,} "
                  f"bytes ({len(data) - len(raw):+,})")
        if not done_doc:
            print(f"  would create {DOC}  "
                  f"{len(DOC_TEXT.encode('utf-8')):,} bytes")
        return 0

    if not done_status:
        side = rp.with_suffix(rp.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(raw)
        rp.write_bytes(data)
        print(f"  patched      {ROADMAP}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    if not done_doc:
        dp.parent.mkdir(parents=True, exist_ok=True)
        blob = DOC_TEXT.encode("utf-8")
        dp.write_bytes(blob)
        print(f"  created      {DOC}  {len(blob):,} bytes  "
              f"sha256 {_sha(blob)[:16]}")
    return 0


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    r = (root / ROADMAP).read_text(encoding="utf-8")
    d = (root / DOC).read_text(encoding="utf-8")
    dflat = " ".join(d.split())
    #: Prose assertions run against a copy with markdown emphasis and code
    #: ticks stripped as well as whitespace collapsed. Three of these failed
    #: on their first run purely because the phrase wrapped across a line and
    #: carried backticks -- an assertion about content should not be an
    #: assertion about typography.
    plain = dflat.replace("`", "").replace("**", "").replace("*", "")

    check("item 42 reads NARROWED", NEW_42 in r)
    check("its OPEN stamp is gone", OLD_42 not in r)
    check("the status points at the doc", "docs/EXPORT_NAMING.md" in r)
    check("the status says nothing produces it yet",
          "nothing produces it yet" in r)

    check("the doc gives the archive grammar",
          "LF_<mission>_s<seed>_<utc>_f<factory>_<profile>.zip" in d)
    check("and a worked example",
          "LF_lot_demo_001_s5219_20260814T183045Z_f1.17.0_portable-godot.zip"
          in d)
    check("the folder is stable, and says why",
          "LF_lot_demo_001/" in d and "res:// paths survive it" in plain)
    check("it explains the timestamp/droppable tension",
          "pull in opposite directions" in plain)
    check("time sorts before the factory version, with the reason",
          "f1.9.0 sorts after f1.17.0" in plain)
    check("LF_MANIFEST.json is specified with not_run",
          "LF_MANIFEST.json" in d and '"not_run"' in d)
    check("the interior rule is stated",
          "name a directory for a tool only when the recipient needs to know"
          in plain)
    check("it says where the function lives",
          "level_factory/packages/core/ids.py" in d)
    check("it lists what the change costs",
          "What this costs" in d and "260-character path budget" in plain)
    check("all four defaults are recorded as decisions",
          "Decisions taken, and their defaults" in d
          and all(s in plain for s in ("LF_, not levelfactory_",
                                       "Dots kept in f1.17.0",
                                       "No seed in the folder name",
                                       "The profile appears on every archive")))
    check("it flags which decision is likeliest to be revisited",
          "most likely to be revisited" in plain)

    check("item 41 is untouched",
          "The dressing layer is STRUCTURAL ART" in r)
    check("items 8 and 16 stay closed",
          "STATUS: CLOSED 2026-08-14 -- shipped as Lot 0.28.0" in r
          and "STATUS: CLOSED 2026-08-14 -- not a bake defect" in r)

    if "| 42 | **OPEN**" in r:
        print("  note  the generated table is stale -- run "
              "`python tools\\roadmap_status.py --write`")

    print()
    print("  the scheme is written down and item 42 knows it"
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
        p = root / ROADMAP
        side = p.with_suffix(p.suffix + SIDECAR)
        if side.is_file():
            p.write_bytes(side.read_bytes())
            print(f"  reverted     {ROADMAP}")
        else:
            print(f"  no sidecar for {ROADMAP}")
            bad = 1
        d = root / DOC
        if d.is_file():
            d.unlink()
            print(f"  removed      {DOC}")
        return bad

    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("  python patches\\patch_export_naming_doc.py --selftest")
        print("  python tools\\roadmap_status.py --write")
        print("  python tools\\roadmap_status.py --check")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
