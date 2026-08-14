r"""Roadmap item 42: the export does not say what it is.

    python patch_roadmap_item42.py --check
    python patch_roadmap_item42.py
    python patch_roadmap_item42.py --selftest
    python patch_roadmap_item42.py --revert

Run from the FACTORY ROOT (the directory holding `factory.manifest.json`).

RAISED 2026-08-14, from the workspace as it stands. Item 27 closed the
question of whether the export WORKS -- 36 resources, closure ok, portability
PASS in a clean Godot project. This is the different question of whether the
artifact identifies itself once it leaves the workspace.

What `.level_factory/exports/` holds today:

    lot_demo_001.portable-godot/                 the drop-in folder
    lot_demo_001.portable-godot.portability.json
    lot_demo_001.pure-shell/                     a different profile, same
                                                 naming shape
    lot_demo_001.zip                             18.6 MB, and the name does
                                                 not say which profile it is

Nothing in any of those names says which factory version built it, which tool
versions went into it, or when. The information EXISTS -- `build.lock.json`
carries `created_at`, `spec_sha256` and per-file hashes, and
`export_profile.json` names the profile -- it is simply not in the name, so it
is only available to someone who has already unpacked the thing and knows
which file to open.

Which is the same shape as the rest of 2026-08-14: the record exists, in a
place nobody reads.

AND `lot` IS ONE TOOL OF TEN. The drop-in folder is named for it, the
per-building subtree is `lot/<building>/`, and `assets/` holds `lot.glb` and
`shell.glb` at 242,168 bytes each with an identical mtime -- the same asset
under two names, one of which is a tool's name. The export is the whole
factory's output, not Lot's.

WHAT THE ITEM DOES NOT DECIDE. The exact scheme is a decision, not a
deduction, so the item states the properties the name has to carry and leaves
the format to whoever picks it up. Writing a scheme into the roadmap as though
it were a finding is how a preference becomes a requirement nobody agreed to.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

TARGET = "PIPELINE_ROADMAP.md"
SIDECAR = ".pre_item42"

ANCHOR = "### Not to be worked on"

ITEM = """*STATUS: OPEN 2026-08-14 -- raised. `.level_factory/exports/` holds `lot_demo_001.portable-godot/`, `lot_demo_001.pure-shell/` and `lot_demo_001.zip`; no name carries a factory version, a tool set or a date, and `assets/` ships `lot.glb` and `shell.glb` at 242,168 bytes with the same mtime*

**42. A level leaves the factory with a name that does not say what it is.**
Item 27 closed whether the export WORKS: 36 resources, closure ok, portability
PASS in a clean Godot project. This is the other question — whether the thing
can still be identified once it is on somebody else's disk.

Today, `.level_factory/exports/`:

```
lot_demo_001.portable-godot/                  the drop-in folder
lot_demo_001.portable-godot.portability.json
lot_demo_001.pure-shell/                      a different profile, same shape
lot_demo_001.zip                              18.6 MB, profile unstated
```

**Nothing in those names carries a version or a date.** Not the factory
version that built it, not the tool versions that went into it, not when it
ran. Two exports from two different weeks are indistinguishable on disk. Send
someone `lot_demo_001.zip` twice and they cannot tell which is newer without
unpacking it and knowing that `build.lock.json` is the file to open.

The information is not missing — it is unplaced. `build.lock.json` carries
`created_at`, `spec_sha256` and per-file hashes; `export_profile.json` names
the profile; `factory.manifest.json` pins the certified set. None of it
reaches the name, which is the only part a recipient sees first. That is the
same defect this file spent 2026-08-14 finding everywhere else: a record that
exists somewhere nobody reads.

**And it is named after one tool of ten.** The folder is `lot_*`, the
per-building subtree is `lot/<building>/`, and `assets/` holds `lot.glb`
alongside `shell.glb` — 242,168 bytes each, identical mtime, the same asset
under two names, one of them a tool's. A level is the output of the whole
DAG: Deli Counter shells, Zoo kits, Pixelcoat materials, Patina wear, Lux
light, Dispatch packaging, Lot assembly. Naming the result for the assembler
tells a recipient the wrong thing about what they have, and tells the next
maintainer the wrong thing about who owns it.

**What the name has to carry**, stated as properties rather than a format,
because the format is a decision:

* **Identity** — the mission, so it is obvious what level this is.
* **Provenance** — the factory version, so the pinned tool set is recoverable
  from `factory.manifest.json` at that tag.
* **Time** — when the run happened, sortable, so two exports order themselves
  in a directory listing without being opened.
* **Profile** — `portable-godot` vs `pure-shell`, on the zip as well as the
  folder, because the zip is what gets sent.
* **Origin** — that this came out of a Level Factory at all, rather than out
  of `lot`.

**What is already right and should not be broken.** The contents are
correct and portability is proven; this is a naming and manifest change, not
a repackaging. `HANDOFF.md` (437 bytes today) is the natural place for the
same facts in prose, since it is the first file a recipient opens. Whatever
scheme is chosen wants to be written once in Dispatch or Level Factory and
read everywhere else, rather than composed by each caller — otherwise the
next `make_package.ps1` will name it a fourth way.

"""

_CRLF = "\r\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply(root: Path, *, check: bool) -> int:
    p = root / TARGET
    if not p.is_file():
        print(f"REFUSING: {TARGET} is not here")
        return 1
    raw = p.read_bytes()
    body = raw.decode("utf-8")

    if "**42. A level leaves the factory" in body:
        print("  already applied")
        return 0
    if "**42." in body:
        print("REFUSING: an item 42 already exists and is not this one")
        return 1
    if body.count(ANCHOR) != 1:
        print(f"REFUSING: '{ANCHOR}' occurs {body.count(ANCHOR)} time(s), "
              f"expected 1")
        return 1
    if "**41." not in body:
        print("REFUSING: item 41 is not here -- this appends after it")
        return 1

    idx = body.index(ANCHOR)
    eol = _CRLF if body[:idx].endswith(_CRLF) else "\n"
    item = ITEM.replace("\n", eol) if eol == _CRLF else ITEM
    out = body[:idx] + item + body[idx:]

    data = out.encode("utf-8")
    got = data.count(_CRLF.encode())
    want = raw.count(_CRLF.encode()) + item.count(_CRLF)
    if got != want:
        print(f"REFUSING: CRLF count is {got:,}, expected {want:,}")
        return 1

    if check:
        print(f"  would patch  {TARGET}  {len(raw):,} -> {len(data):,} bytes "
              f"({len(data) - len(raw):+,})")
        return 0
    side = p.with_suffix(p.suffix + SIDECAR)
    if not side.is_file():
        side.write_bytes(raw)
    p.write_bytes(data)
    print(f"  patched      {TARGET}  {len(raw):,} -> {len(data):,} bytes "
          f"({len(data) - len(raw):+,})  sha256 {_sha(data)[:16]}")
    return 0


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    t = (root / TARGET).read_text(encoding="utf-8")
    flat = " ".join(t.split())

    check("item 42 exists, once",
          t.count("**42. A level leaves the factory") == 1)
    check("it has a status line", "*STATUS: OPEN 2026-08-14 -- raised." in t)
    check("it sits after item 41",
          t.index("**41.") < t.index("**42."))
    check("it sits before 'Not to be worked on'",
          t.index("**42.") < t.index(ANCHOR))
    check("it names the three real export paths",
          all(s in t for s in ("lot_demo_001.portable-godot/",
                               "lot_demo_001.pure-shell/",
                               "lot_demo_001.zip")))
    check("it records the duplicated asset",
          "242,168 bytes" in flat and "lot.glb" in t and "shell.glb" in t)
    check("it says the information exists but is unplaced",
          "not missing — it is unplaced" in flat)
    check("it credits item 27 rather than re-opening it",
          "Item 27 closed whether the export WORKS" in flat)
    check("it states properties, not a format",
          "stated as properties rather than a format" in flat)
    check("it names all five properties",
          all(s in t for s in ("**Identity**", "**Provenance**", "**Time**",
                               "**Profile**", "**Origin**")))
    check("it says what not to break",
          "this is a naming and manifest change, not a repackaging" in flat)

    # Nothing else moved.
    check("item 41 is untouched",
          "The dressing layer is STRUCTURAL ART routed through the decoration"
          in flat)
    check("item 8 stays closed",
          "STATUS: CLOSED 2026-08-14 -- shipped as Lot 0.28.0" in t)
    check("item 16 stays closed",
          "STATUS: CLOSED 2026-08-14 -- not a bake defect" in t)

    if "| 42 |" not in t:
        print("  note  the generated table has no row 42 yet -- run "
              "`python tools\\roadmap_status.py --write`")

    print()
    print("  item 42 raised, with the export's real filenames in it"
          if not bad else f"  {bad} FAILURE(S)")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    root = Path.cwd()
    if not (root / "factory.manifest.json").is_file():
        raise SystemExit("run this from the factory root")

    if "--selftest" in argv:
        return selftest(root)

    if "--revert" in argv:
        p = root / TARGET
        side = p.with_suffix(p.suffix + SIDECAR)
        if not side.is_file():
            print(f"  no sidecar for {TARGET}")
            return 1
        p.write_bytes(side.read_bytes())
        print(f"  reverted     {TARGET}")
        return 0

    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("  python patches\\patch_roadmap_item42.py --selftest")
        print("  python tools\\roadmap_status.py --write")
        print("  python tools\\roadmap_status.py --check")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
