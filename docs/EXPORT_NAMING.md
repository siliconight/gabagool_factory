# Export naming

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
