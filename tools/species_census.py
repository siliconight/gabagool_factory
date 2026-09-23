"""Which of Zoo's species does the pipeline actually PLACE?

WHY THIS EXISTS. Three capabilities were found built-and-never-placed in one
afternoon, 2026-09-23, each by accident while looking for something else:

    zoo ladder species    built to fill a Deli Counter ladder slot -- its own
                          docstring says so -- and `_ladders` never records a
                          slot, so it cannot be placed at all
    roof mechanical       hvac_unit, vent_stack, exhaust_fan, satellite_dish:
                          full part structure, absent from every shipped GLB
    fire escapes          `Builder._fire_escapes` builds the whole assembly;
                          2 of 370 specs use it

Art that exists and is never placed is the cheapest quality in the repo and
the easiest to not notice, because nothing fails: the level builds, every gate
passes, and the roof is simply empty. That is the "works vs good" gap CLAUDE.md
names, and it stayed invisible because nobody was counting.

So this counts. It is an INSTRUMENT, not a gate -- it prints what it measured
and stops. Whether an absent species SHOULD be placed is a judgement about the
brief, and it belongs in the reply rather than in the tool.

HOW A SPECIES IS FINGERPRINTED, and the honest third answer. Zoo recipes name
their parts through one idiom -- `part(bm, "Hvac_Curb")`, sometimes an
f-string like `f"Ladder_Rung_{i + 1}"` -- and Zoo writes those names through to
the GLB's nodes and materials. The literal prefix is therefore a fingerprint.
A recipe this cannot extract a usable fingerprint from is reported
UNDETECTABLE, never "absent": a checker that cannot find the field it wants has
learned nothing and must say so. The first version of this measurement matched
recipe filenames against GLB filenames and called `fluorescent_fixture` absent
while the package carried `M_FluorescentFixture_metal` -- a false negative
that would have sent somebody to rebuild a species that was already there.

CONTROLS. `--control` names a species expected to be PRESENT. If it reads
absent, the fingerprinting is broken rather than the package, and the run says
so and exits 2 instead of printing a table nobody should trust.

Usage:
    python tools/species_census.py <package_dir> [--control fluorescent_fixture]
    python tools/species_census.py <package_dir> --json out.json
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECIPES = ROOT / "zoo" / "zoo_keeper" / "recipes"

#: `part(bm, "Name")` / `part(bm, f"Name_{i}")` -- capture the literal prefix,
#: stopping at a brace so an f-string contributes what is stable about it.
_PART = re.compile(r'part\(\s*\w+\s*,\s*f?"([^"{]*)')
#: the longhand some recipes use instead
_DIRECT = re.compile(r'bm_to_object\(\s*\w+\s*,\s*f?"([^"{]*)')
#: shorter than this is not a fingerprint, it is a coincidence waiting to
#: happen ("Cap" would match half the library).
MIN_FINGERPRINT = 5


def fingerprints(src: str) -> list[str]:
    out: set[str] = set()
    for rx in (_PART, _DIRECT):
        for m in rx.findall(src):
            tok = m.strip()
            if len(tok) >= MIN_FINGERPRINT:
                out.add(tok)
    return sorted(out)


def species() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for p in sorted(RECIPES.glob("*.py")):
        if p.stem.startswith("_"):
            continue
        out[p.stem] = fingerprints(p.read_text(encoding="utf-8", errors="ignore"))
    return out


def gltf_names(glb: Path) -> str:
    """Every node, mesh and material name in one GLB, as one blob."""
    data = glb.read_bytes()
    if len(data) < 20 or data[:4] != b"glTF":
        return ""
    ln = struct.unpack("<I", data[12:16])[0]
    try:
        js = json.loads(data[20:20 + ln].decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return ""
    parts: list[str] = []
    for key in ("nodes", "meshes", "materials"):
        parts.extend(str(x.get("name", "")) for x in js.get(key, []))
    return " ".join(parts)


def scan(pkg: Path) -> tuple[dict[str, int], int]:
    """{fingerprint-bearing blob} -> how many GLBs carry each species."""
    blobs: list[str] = []
    n = 0
    for g in pkg.rglob("*.glb"):
        if ".godot" in g.parts:
            continue
        b = gltf_names(g)
        if b:
            blobs.append(b)
            n += 1
    return blobs, n


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("package", type=Path)
    ap.add_argument("--control", action="append", default=[],
                    help="a species that MUST read present; proves the "
                         "fingerprinting works before the table is believed")
    ap.add_argument("--json", type=Path)
    args = ap.parse_args(argv)

    if not args.package.is_dir():
        print(f"species_census: {args.package} is not a directory")
        return 2

    cat = species()
    blobs, n_glb = scan(args.package)
    if n_glb == 0:
        print(f"species_census: no readable .glb under {args.package} -- "
              f"refusing to report every species as absent")
        return 2

    # TWO INDEPENDENT SIGNALS, because one was not enough and the gap was not
    # small. Part-name fingerprints classified 57 of 105 species; the other 48
    # name their parts from a VARIABLE (`bm_to_object(bm, name, ...)` in
    # vending_machine) or through some other idiom entirely (doorway, poster),
    # and `doorway` being called "absent" would have been absurd -- the
    # package is full of `doorway_delco_1997_*.glb`.
    #
    # Signal 2 is the module FILENAME: Zoo writes a module as
    # `<species>_<theme>_<variant>_...glb`, so the species name in a filename
    # is strong evidence of placement. It is weaker in the other direction --
    # a species placed under some other filename would be missed -- which is
    # why a miss on BOTH signals, with no part fingerprint to fall back on,
    # is reported UNCERTAIN rather than absent.
    names = [g.name.lower() for g in args.package.rglob("*.glb")
             if ".godot" not in g.parts]
    filenames = " ".join(names)

    placed: dict[str, int] = {}
    absent: list[str] = []
    uncertain: list[str] = []
    how: dict[str, str] = {}
    for name, fps in sorted(cat.items()):
        hits = sum(1 for b in blobs if any(f in b for f in fps)) if fps else 0
        by_file = name in filenames
        if hits:
            placed[name] = hits
            how[name] = "part name" + (" + filename" if by_file else "")
        elif by_file:
            placed[name] = sum(1 for n in names if name in n)
            how[name] = "filename"
        elif fps:
            # A usable fingerprint existed and matched nothing. That is a real
            # absence, not a blind spot.
            absent.append(name)
        else:
            uncertain.append(name)
    undetectable = uncertain

    bad = [c for c in args.control if c not in placed]
    print(f"species_census: {args.package}")
    print(f"  {n_glb} GLB(s) read; Zoo offers {len(cat)} species")
    print(f"  PLACED       {len(placed):3d}")
    print(f"  ABSENT       {len(absent):3d}")
    print(f"  UNCERTAIN    {len(undetectable):3d}  "
          f"(no part fingerprint AND name not in any module filename -- "
          f"NOT a claim about the package)")
    if args.control:
        state = "ok" if not bad else "FAILED: " + ", ".join(bad)
        print(f"  control      {state}")
    print()
    print("  absent, by name:")
    for i in range(0, len(absent), 3):
        print("   ", "  ".join("%-26s" % a for a in absent[i:i + 3]))
    if undetectable:
        print()
        print("  uncertain, by name:")
        for i in range(0, len(undetectable), 3):
            print("   ", "  ".join("%-26s" % u for u in undetectable[i:i + 3]))

    if args.json:
        args.json.write_text(json.dumps({
            "package": str(args.package), "glbs_read": n_glb,
            "species_total": len(cat), "placed": placed,
            "absent": absent, "uncertain": undetectable, "evidence": how,
            "controls": args.control, "controls_failed": bad,
        }, indent=1), encoding="utf-8")
        print(f"\n  wrote {args.json}")

    if bad:
        print("\n  A CONTROL READ ABSENT. The fingerprinting is wrong, not the "
              "package; the table above is not evidence.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
