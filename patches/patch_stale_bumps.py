r"""dispatch 0.3.1, pixelcoat 0.12.0, zoo 0.33.0 -- the STALE tools catch up.

    python patch_stale_bumps.py --check
    python patch_stale_bumps.py
    python patch_stale_bumps.py --selftest
    python patch_stale_bumps.py --revert

Run from the FACTORY ROOT (the directory holding `factory.manifest.json`).

WHY. `verify-manifest` reported four tools STALE -- code committed after the
VERSION naming it -- and named the file for each:

    dispatch    README.md
    pipeline    registries/building_configuration_registry.json +1 more
    pixelcoat   profiles/materials/brick_buff_civic.json +3 more
    zoo         tests/test_plate.py +3 more

Three of those are handled here. `pipeline` is not: its one commit is
`7ed8e00`, subject "checkpoint: uncommitted working tree", touching
`.gitignore`, `building_configuration_registry.json` (6 lines) and
`mission_registry.json` (60 lines). Something real changed in the registrar's
own data and the commit message does not say what. Writing an entry from the
version number alone would be inventing the one thing a CHANGELOG is for.

BUMP LEVELS COME FROM WHAT THE COMMITS TOUCHED, NOT FROM HOW BIG THEY FEEL.
`draft_version_bumps.py`'s rule: docs-only is a PATCH, anything touching code,
data or tests is a MINOR. dispatch's single commit is a README edit -- 0.3.1.
pixelcoat's eleven and zoo's seventeen touch materials, geometry and tests --
0.12.0 and 0.33.0.

EVERY BULLET NAMES ITS COMMIT. These entries are assembled from commit
subjects, not from watching the work happen, and each says so at the bottom.
The subjects here are unusually good -- "a structural slab is never
see-through", "conduit span still scaled a hint that had become a
measurement" -- so the entries are close to transcription. Where a subject
states a number (`warp 0.35 -> 0.12`, `panel_field proud 0.03 -> 0.012`) the
number is carried through rather than paraphrased, because that is the part a
reader will want to check against the code.

ONE COMMIT IN ZOO'S RANGE SAYS NOTHING ABOUT ITSELF: `5bbe380`, "checkpoint:
uncommitted working tree". It is in the range and it is not in the entry,
which the entry states. The same pattern that is holding `pipeline` back.

THREE HEADING STYLES, PRESERVED. `dispatch` writes `## v0.3.0 — 2026-07-11`
with an em dash and a date; `pixelcoat` and `zoo` write `## [0.11.0] - Title`
with a bracketed number and a title instead. Each entry matches the file it
joins. A patch that normalises house style while doing something else is two
changes wearing one commit message.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

SIDECAR = ".pre_stalebump"

#: tool -> (VERSION old, VERSION new)
VERSIONS: dict[str, tuple[str, str]] = {
    "dispatch": ("0.3.0", "0.3.1"),
    "pixelcoat": ("Pixelcoat 0.11.0", "Pixelcoat 0.12.0"),
    "zoo": ("Zoo 0.32.0", "Zoo 0.33.0"),
}

ANCHOR = "# Changelog\n\n"

ENTRIES: dict[str, str] = {

    "dispatch": """# Changelog

## v0.3.1 — 2026-08-14

Documentation only. No behaviour change, no contract change; the contract
stays `dispatch.mission.v0.2`.

- **README** points at `PIPELINE_MAP.md` and states what this repo owns
  (`bf356954`).

Cut because `verify-manifest` reported dispatch STALE: one commit newer than
the VERSION naming it. A docs-only change is a PATCH by this factory's own
rule, and a version that refuses to move for a real difference leaves the
check permanently unhappy about something true.

""",

    "pixelcoat": """# Changelog

## [0.12.0] - The art standard gets a gate, and the library is calibrated against it

### Added
- **Baseline regression gate over the material library** (`a14fa62`). The
  Controlled Contrast Environment Art Standard was a document; this makes it
  a check the library is measured against, so the standard is enforced rather
  than remembered.
- **Neighbour-pair check** (`dd707fd`): a value step between adjacent
  materials needs a visible reason. A step nobody can see is a step nobody
  chose.
- **The `rockay` profile** (`72a9056`), with retail / service / civic
  variants and profile validation (`2e282af`).
- **`metal_rusted_street`** joins the delco theme (`c3db6c2`).

### Changed
- **Pack size derives from `meters_per_tile` at a target texel density**
  (`8cadc44`) instead of being chosen. Texel density is the thing that has to
  be right; pack size is what falls out of it.
- **Four palettes pulled off the luminance ceiling; baseline re-snapshotted**
  (`19a65e6`). `value_range` widens as the clipping is removed -- the range
  was being compressed by the ceiling, not by the palettes.
- **The bulk metal and the civic floor quieted; civic gets its own brick; the
  chroma budget recalibrated from the contact sheet** (`f01e3fb`).
- **Mortar joints that read**, and polished concrete separated from drywall
  by hue (`0f9772c`).
- **`glass_wavy` ripple calmed**: warp 0.35 -> 0.12, height 0.9 -> 0.45
  (`ca614bb`).

### Docs
- README points at `PIPELINE_MAP.md` and states what this repo owns
  (`531aa2e`).

Assembled on 2026-08-14 from this repo's own commits, eleven of them since
VERSION last moved, after `verify-manifest` reported pixelcoat STALE. Each
bullet names its commit; the numbers are carried through from the subjects
rather than paraphrased, because they are the part worth checking against the
code.

""",

    "zoo": """# Changelog

## [0.33.0] - Architecture becomes plates and modules, and the covers stop lying about their UVs

### Changed
- **Floor and ceiling skins build as plates**, carrying the slab's holes in
  them (`a03617a`).
- **Openings cut the slot's authored aperture** instead of genome fractions,
  and tag it in the stem (`b919677`). The authored number is the one someone
  decided; a fraction of a genome is one nobody did.
- **Facade relief carves into the wall module** instead of standing boxes
  proud of it (`56a1fc6`).
- **A prop species is a solid themed box at a DC volume's exact dims**
  (`13b8b2a`), and `test_genome` treats prop as an ARCH species -- DC
  slot-driven, not a modelled prop (`0b61689`).
- **A structural slab is never see-through**, and the planned glazing kind is
  delivered to the pane rather than assumed (`d2a8ff3`).
- **Theme styles resolve by family prefix**, and the rockay wall relief is
  quieted (`cf8c3e8`).
- **`panel_field` proud 0.03 -> 0.012** (`5f7b898`).

### Fixed
- Covers orient by the anchor tangent, not the normal alone (`e2c6160`).
- Dressing carries ambient from the style block into the cover build
  (`f7ee3e2`).
- Skinned covers exported `COLOR_0` as flat white (`26728c7`).
- The wear layer was computed and never exported (`c26670a`).
- Every cover projected its UVs from the same local box (`3f18b6a`).
- Conduit span still scaled a hint that had become a measurement (`ad9b111`).

### Docs
- `dress_cover` claimed its UVs came from `uv_region`; they come from a cube
  projection (`ebdb924`).
- README points at `PIPELINE_MAP.md` and states what this repo owns
  (`abbe1db`).

Assembled on 2026-08-14 from this repo's own commits, seventeen of them since
VERSION last moved, after `verify-manifest` reported zoo STALE. One commit in
that range is not represented above: `5bbe380`, "checkpoint: uncommitted
working tree", which says nothing about itself. It is the same shape that is
currently holding `pipeline` at STALE.

""",
}

_CRLF = "\r\n"


def _eol(body: str) -> str:
    crlf = body.count(_CRLF)
    lf = body.count("\n") - crlf
    return _CRLF if crlf > lf else "\n"


def _as(text: str, eol: str) -> str:
    return text.replace(_CRLF, "\n").replace("\n", eol)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def newest_entry(path: Path) -> str | None:
    if not path.is_file():
        return None
    m = re.search(r"^##\s*\[?v?([0-9]+\.[0-9]+\.[0-9]+)\]?",
                  path.read_text(encoding="utf-8", errors="replace"), re.M)
    return m.group(1) if m else None


def _apply(root: Path, *, check: bool) -> int:
    rc = 0
    for tool, (old_v, new_v) in VERSIONS.items():
        vp = root / tool / "VERSION"
        cp = root / tool / "CHANGELOG.md"
        if not vp.is_file() or not cp.is_file():
            print(f"REFUSING: {tool} is missing VERSION or CHANGELOG.md")
            rc = 1
            continue

        vraw, craw = vp.read_bytes(), cp.read_bytes()
        vbody, cbody = vraw.decode("utf-8"), craw.decode("utf-8")
        want = new_v.split()[-1]

        if new_v in vbody and f"[{want}]" in cbody or (
                new_v in vbody and f"v{want} " in cbody):
            print(f"  already applied  {tool}")
            continue
        if old_v not in vbody:
            print(f"REFUSING: {tool}/VERSION does not say {old_v!r} "
                  f"(found {vbody.strip()!r})")
            rc = 1
            continue
        ceol = _eol(cbody)
        a, n = _as(ANCHOR, ceol), _as(ENTRIES[tool], ceol)
        if cbody.count(a) != 1:
            print(f"REFUSING: {tool}/CHANGELOG.md -- the title block occurs "
                  f"{cbody.count(a)} time(s), expected 1")
            rc = 1
            continue

        vout = vbody.replace(old_v, new_v, 1)
        cout = cbody.replace(a, n, 1)
        vdata, cdata = vout.encode("utf-8"), cout.encode("utf-8")
        if check:
            print(f"  would bump   {tool}/VERSION  {old_v} -> {new_v}")
            print(f"  would prepend {tool}/CHANGELOG.md  "
                  f"+{len(cdata) - len(craw):,} bytes")
            continue
        for p, raw in ((vp, vraw), (cp, craw)):
            side = p.with_suffix(p.suffix + SIDECAR)
            if not side.is_file():
                side.write_bytes(raw)
        vp.write_bytes(vdata)
        cp.write_bytes(cdata)
        print(f"  bumped       {tool}/VERSION  {old_v} -> {new_v}")
        print(f"  prepended    {tool}/CHANGELOG.md  +{len(cdata) - len(craw):,}"
              f" bytes  sha256 {_sha(cdata)[:16]}")
    return rc


def selftest(root: Path) -> int:
    bad = 0

    def check(label: str, ok: bool) -> None:
        nonlocal bad
        bad += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'} {label}")

    want = {"dispatch": "0.3.1", "pixelcoat": "0.12.0", "zoo": "0.33.0"}
    for tool, v in want.items():
        vf = (root / tool / "VERSION").read_text(encoding="utf-8")
        c = newest_entry(root / tool / "CHANGELOG.md")
        check(f"{tool:<10} VERSION {v}", v in vf)
        check(f"{tool:<10} newest entry {c} matches VERSION", c == v)

    # Heading style is preserved per file -- see the module docstring.
    d = (root / "dispatch/CHANGELOG.md").read_text(encoding="utf-8")
    check("dispatch keeps its `## vX — date` shape",
          "## v0.3.1 — 2026-08-14" in d and "## v0.3.0 — 2026-07-11" in d)
    for tool, head in (("pixelcoat", "## [0.12.0] - "),
                       ("zoo", "## [0.33.0] - ")):
        t = (root / tool / "CHANGELOG.md").read_text(encoding="utf-8")
        check(f"{tool} keeps its `## [X] - Title` shape", head in t)

    # Nothing was lost, and no entry was duplicated.
    for tool, older in (("dispatch", "## v0.3.0"), ("pixelcoat", "## [0.11.0]"),
                        ("zoo", "## [0.32.0]")):
        t = (root / tool / "CHANGELOG.md").read_text(encoding="utf-8")
        check(f"{tool}'s previous entry survives, once", t.count(older) == 1)
        check(f"{tool} has one title", t.count("# Changelog") == 1)

    # Every bullet's commit is real, per the report we read them from.
    shas = {
        "dispatch": ["bf356954"],
        "pixelcoat": ["a14fa62", "dd707fd", "72a9056", "2e282af", "c3db6c2",
                      "8cadc44", "19a65e6", "f01e3fb", "0f9772c", "ca614bb",
                      "531aa2e"],
        "zoo": ["a03617a", "b919677", "56a1fc6", "13b8b2a", "0b61689",
                "d2a8ff3", "cf8c3e8", "5f7b898", "e2c6160", "f7ee3e2",
                "26728c7", "c26670a", "3f18b6a", "ad9b111", "ebdb924",
                "abbe1db"],
    }
    for tool, want_shas in shas.items():
        t = (root / tool / "CHANGELOG.md").read_text(encoding="utf-8")
        missing = [s for s in want_shas if s not in t]
        check(f"{tool:<10} all {len(want_shas)} commit(s) named", not missing)

    z = (root / "zoo/CHANGELOG.md").read_text(encoding="utf-8")
    check("zoo declares the commit it could not describe", "5bbe380" in z)

    # And the instrument agrees, if 0.25.0 is in.
    lf = str((root / "level_factory").resolve())
    if lf not in sys.path:
        sys.path.insert(0, lf)
    try:
        import importlib
        contracts = importlib.import_module("packages.tools.contracts")
        importlib.reload(contracts)
        for tool in want:
            v = (root / tool / "VERSION").read_text(encoding="utf-8")
            c = contracts.newest_changelog_entry(root / tool)
            check(f"{tool:<10} reads as agreeing with itself",
                  contracts.self_disagreement(v, c) is None)
    except Exception as exc:
        print(f"  skip  contracts check ({type(exc).__name__}: {exc})")

    print()
    print("  three tools agree with themselves at their new versions"
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
        for tool in VERSIONS:
            for name in ("VERSION", "CHANGELOG.md"):
                p = root / tool / name
                side = p.with_suffix(p.suffix + SIDECAR)
                if not side.is_file():
                    print(f"  no sidecar for {tool}/{name}")
                    bad = 1
                    continue
                p.write_bytes(side.read_bytes())
                print(f"  reverted     {tool}/{name}")
        return bad

    check = "--check" in argv
    rc = _apply(root, check=check)
    if not rc and not check:
        print()
        print("  python patches\\patch_stale_bumps.py --selftest")
        print()
        print("  then, INSIDE each repo:")
        for tool, v, msg in (
                ("dispatch", "0.3.1", "README points at PIPELINE_MAP.md"),
                ("pixelcoat", "0.12.0",
                 "art standard gate + material calibration"),
                ("zoo", "0.33.0", "plates, modules, and honest cover UVs")):
            print(f"    git -C {tool} add -A && git -C {tool} commit "
                  f'-m "{v} -- {msg}"')
            print(f'    git -C {tool} tag -a v{v} -m "{v} -- {msg}" && '
                  f"git -C {tool} push --follow-tags")
        print()
        print("  pipeline stays STALE until `7ed8e00`'s registry diff is read.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
