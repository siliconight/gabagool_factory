r"""docs/EXPORT_NAMING.md: three names, not two.

    python patch_export_naming_fix.py --check
    python patch_export_naming_fix.py
    python patch_export_naming_fix.py --selftest
    python patch_export_naming_fix.py --revert

Run from the FACTORY ROOT. Requires `docs/EXPORT_NAMING.md` -- run
`patch_export_naming_doc.py` first.

THE ERROR. The accepted doc says the folder is `LF_<mission>/`, stable. Then
reading `packages/exporting/export.py:232`:

    export_dir = out_root / f"{mission_id}.{profile.mode}"

The workspace holds `portable-godot` AND `pure-shell` side by side. Under one
stable name they collide and the second export overwrites the first. The doc
conflated two different directories -- the one the factory builds into, and
the one a recipient drops in -- and they have opposite requirements. The build
dir must distinguish profiles; the dropped folder must not change between
exports.

So there are THREE names, and the doc now says so:

    exports/LF_lot_demo_001.portable-godot/   build dir, profile kept
    LF_lot_demo_001/                          inside the archive, stable
    LF_lot_demo_001_s5219_20260814T183045Z_f1.17.0_portable-godot.zip

TWO MEASURED FACTS GO IN AT THE SAME TIME, because they are the evidence for
the section that says where the function belongs, and the doc asserted it
without them.

`export.py:441` is `result.export_dir.with_suffix(".zip")`. `with_suffix`
treats `.portable-godot` as a file extension and replaces it, which is why the
archive is `lot_demo_001.zip` with no profile in it. Nobody decided to drop
it; a path helper ate it.

And the grammar is composed in four places, which the doc predicted as a
future risk and is in fact already true:

    export.py:232    out_root / f"{mission_id}.{profile.mode}"
    commands:2057    f"{mission_id}.portable-godot"     hardcoded, cmd_walk
    commands:2248    export_root / f"{mission_id}.{mode}"
    commands:2260    f"{mission_id}.{mode}.portability.json"

Line 2057 hardcodes the profile rather than using the mode it set four lines
earlier, so `cmd_walk` looks in a fixed place regardless.

WHY A SEPARATE PATCH. The wrong version is committed and pushed. A correction
that leaves no trace is how the next reader learns nothing from it -- the same
argument as item 16's retraction earlier today.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

DOC = "docs/EXPORT_NAMING.md"
ROADMAP = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_namingfix"

OLD_FOLDER = """## The folder inside

```
LF_lot_demo_001/
```

Stable across exports of the same mission. Dropping in a newer export
overwrites in place, which is what an update should do, and `res://` paths
survive it. Two different missions coexist without collision.

The seed is deliberately *not* here: swapping which candidate you ship is an
update to the same mission, not a second thing to keep side by side.
"""

NEW_FOLDER = """## Three names, not two

*Corrected 2026-08-14, after reading `packages/exporting/export.py`. The first
version of this doc had two names and was wrong about one of them.*

```
exports/LF_lot_demo_001.portable-godot/    the build dir, in the workspace
LF_lot_demo_001/                           the folder inside the archive
LF_lot_demo_001_s5219_20260814T183045Z_f1.17.0_portable-godot.zip
```

**The build dir keeps the profile.** `export.py:232` writes
`out_root / f"{mission_id}.{profile.mode}"`, and the workspace holds
`portable-godot` and `pure-shell` at the same time. Give them one stable name
and the second export silently overwrites the first. This directory is never
sent anywhere, so its name only has to be unambiguous inside the workspace.

**The folder inside the archive drops it.** A recipient receives one profile.
That folder becomes part of every `res://` path in their project, so it must
be stable across exports: dropping in a newer one overwrites in place, which
is what an update should do, and their references survive it. Two different
missions coexist without collision.

**The seed is in neither folder**, only the archive. Swapping which candidate
you ship is an update to the same mission, not a second thing to keep side by
side.

The original doc conflated the first two. They have opposite requirements —
the build dir must distinguish profiles, the dropped folder must not change
between exports — and one name cannot do both.
"""

OLD_LIVES = """## Where the scheme lives

One function, in `level_factory/packages/core/ids.py` -- which already owns
`candidate_id` and `job_id`, and already refuses unsafe input rather than
sanitising it. Imported everywhere, composed nowhere. `make_package.ps1`
currently builds a name of its own; left alone it will build a fourth one. A
naming convention enforced by convention is a naming convention until the next
Tuesday.

Worth a `--check` mode that asserts an existing export's name matches what the
function would produce, so drift is detectable rather than discovered.
"""

NEW_LIVES = """## Where the scheme lives

One function, in `level_factory/packages/core/ids.py` -- which already owns
`candidate_id` and `job_id`, and already refuses unsafe input rather than
sanitising it. Imported everywhere, composed nowhere.

**It is already composed in four places.** Measured 2026-08-14, so this is a
present fact rather than a future risk:

```
export.py:232    out_root / f"{mission_id}.{profile.mode}"
commands:2057    f"{mission_id}.portable-godot"     hardcoded, in cmd_walk
commands:2248    export_root / f"{mission_id}.{mode}"
commands:2260    f"{mission_id}.{mode}.portability.json"
```

`commands:2057` hardcodes the profile rather than using the mode it set four
lines earlier. It happens to be right because that block forces
`portable-godot`, and it would go on looking in the same place if that ever
stopped being true.

**And the archive already lost its profile to a path helper.**
`export.py:441` is:

```python
zip_path = result.export_dir.with_suffix(".zip")
```

`with_suffix` treats `.portable-godot` as a file extension and replaces it, so
`lot_demo_001.portable-godot` becomes `lot_demo_001.zip`. Nobody decided to
drop the profile from the archive name. That is what composing a grammar out
of string operations costs, and it is the argument for the function.

`make_package.ps1` builds a name of its own as well; left alone it will build
a fifth. A naming convention enforced by convention is a naming convention
until the next Tuesday.

Worth a `--check` mode that asserts an existing export's name matches what the
function would produce, so drift is detectable rather than discovered.
"""

OLD_42 = ("*STATUS: NARROWED 2026-08-14 -- scheme accepted, nothing produces "
          "it yet. `docs/EXPORT_NAMING.md`: archive "
          "`LF_<mission>_s<seed>_<utc>_f<factory>_<profile>.zip`, folder "
          "`LF_<mission>/` stable so `res://` paths survive an update, "
          "provenance in `LF_MANIFEST.json`. Remaining work is one naming "
          "function in `packages/core/ids.py` and the callers that stop "
          "composing their own*")

NEW_42 = ("*STATUS: NARROWED 2026-08-14 -- scheme accepted and corrected; "
          "nothing produces it yet. `docs/EXPORT_NAMING.md`: THREE names -- "
          "build dir `LF_<mission>.<profile>/` (two profiles coexist in the "
          "workspace), folder inside the archive `LF_<mission>/` (stable, so "
          "`res://` paths survive an update), archive "
          "`LF_<mission>_s<seed>_<utc>_f<factory>_<profile>.zip`. The grammar "
          "is composed in four places today -- export.py:232, commands "
          "2057/2248/2260 -- and export.py:441's `with_suffix` is why the zip "
          "has no profile. Remaining work is `packages/core/ids.py` plus those "
          "four callers*")

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
    dp, rp = root / DOC, root / ROADMAP
    if not dp.is_file():
        print(f"REFUSING: {DOC} is not here -- run patch_export_naming_doc.py "
              f"first")
        return 1
    draw = dp.read_bytes()
    dbody = draw.decode("utf-8")

    if "## Three names, not two" in dbody:
        print("  already applied")
        return 0

    dout = dbody
    for label, old, new in (("the folder section", OLD_FOLDER, NEW_FOLDER),
                            ("the 'where it lives' section", OLD_LIVES,
                             NEW_LIVES)):
        if dout.count(old) != 1:
            print(f"REFUSING: {label} occurs {dout.count(old)} time(s), "
                  f"expected 1")
            return 1
        dout = dout.replace(old, new, 1)
    ddata = dout.encode("utf-8")

    rraw = rp.read_bytes()
    rbody = rraw.decode("utf-8")
    if rbody.count(OLD_42) != 1:
        print(f"REFUSING: item 42's status occurs {rbody.count(OLD_42)} "
              f"time(s), expected 1")
        return 1
    rout = rbody.replace(OLD_42, NEW_42, 1)
    rdata = rout.encode("utf-8")
    if rdata.count(_CRLF.encode()) != rraw.count(_CRLF.encode()):
        print("REFUSING: the CRLF count changed on a single-line swap")
        return 1

    if check:
        print(f"  would patch  {DOC}  {len(draw):,} -> {len(ddata):,} bytes "
              f"({len(ddata) - len(draw):+,})")
        print(f"  would patch  {ROADMAP}  {len(rraw):,} -> {len(rdata):,} "
              f"bytes ({len(rdata) - len(rraw):+,})")
        return 0

    for p, raw, data in ((dp, draw, ddata), (rp, rraw, rdata)):
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            side.write_bytes(raw)
        p.write_bytes(data)
        print(f"  patched      {p.name}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    d = (root / DOC).read_text(encoding="utf-8")
    r = (root / ROADMAP).read_text(encoding="utf-8")
    plain = " ".join(d.split()).replace("`", "").replace("*", "")

    check("the doc has three names", "## Three names, not two" in d)
    check("the build dir keeps the profile",
          "exports/LF_lot_demo_001.portable-godot/" in d)
    check("the archive folder drops it", "LF_lot_demo_001/" in d)
    check("it says why they cannot be one name",
          "opposite requirements" in plain)
    check("the correction is dated and visible",
          "Corrected 2026-08-14" in d)
    check("it names the line that forced the correction",
          "export.py:232" in d)

    check("the four composition sites are listed",
          all(s in d for s in ("export.py:232", "commands:2057",
                               "commands:2248", "commands:2260")))
    check("the with_suffix finding is recorded",
          "with_suffix" in d and 'with_suffix(".zip")' in d)
    check("it explains what with_suffix did",
          "treats .portable-godot as a file extension" in plain)
    check("it says nobody decided that",
          "Nobody decided to drop the profile" in plain)

    check("item 42 says three names", "THREE names" in r)
    check("item 42 names the four sites", "commands 2057/2248/2260" in r)
    check("item 42 records the with_suffix cause",
          "with_suffix" in r and "why the zip has no profile" in r)
    check("the old two-name status is gone", OLD_42 not in r)

    # Untouched.
    check("the archive grammar is unchanged",
          "LF_<mission>_s<seed>_<utc>_f<factory>_<profile>.zip" in d)
    check("the four defaults survive",
          "Decisions taken, and their defaults" in d)
    check("the interior rule survives",
          "name a directory for a tool only when the recipient needs to know"
          in plain)

    print()
    print("  the spec says three names, and why the third exists"
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
        for rel in (DOC, ROADMAP):
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
        print("  python patches\\patch_export_naming_fix.py --selftest")
        print("  python tools\\roadmap_status.py --write")
        print("  then stage 1: ids.py + the four callers")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
