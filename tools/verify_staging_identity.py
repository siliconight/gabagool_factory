"""Did staging change anything except ext_resource path prefixes?

    python verify_staging_identity.py <source_package_dir> <staged_package_dir>

This answers one question and refuses to answer any other: whether the staging
step is capable of having caused a geometry defect. It compares the composed
package `presentation_compose` wrote against the copy `themed_site_assemble`
staged, and it does it on BYTES rather than on reasoning about what the code
does.

The claim under test is mine, so it should not be taken on my word: "a path
rewrite cannot displace geometry, because a wrong path raises a load error
rather than moving a mesh." That is a plausible mechanism, and a plausible
mechanism believed without a test is the exact failure this repo has a document
about. So:

  - every non-.tscn file (all the .glb geometry) must be byte-identical
  - every .tscn must be identical AFTER undoing the rewrite, i.e. the ONLY
    difference permitted is `path="res://X"` -> `path="X"` on ext_resource
    lines

If both hold, staging moved no geometry and the defects visible in the walk
were baked before it ran. If either fails, the difference is printed and the
defect is mine.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

# Must match packages/staging/site_packages.py exactly.
SKIP_NAMES = {"project.godot", "compose.summary.json", "HANDOFF.md",
              "portable_resource_manifest.json"}
EXT_RESOURCE = re.compile(r'(\[ext_resource\b[^\]]*?\bpath=")res://([^"]*)(")')


def sha(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def rewritten(text: str) -> str:
    return EXT_RESOURCE.sub(lambda m: f"{m.group(1)}{m.group(2)}{m.group(3)}",
                            text)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.splitlines()[2].strip())
        return 2
    src, staged = Path(argv[0]), Path(argv[1])
    for d in (src, staged):
        if not d.is_dir():
            print(f"not a directory: {d}")
            return 2

    expected = sorted(
        p for p in src.rglob("*")
        if p.is_file() and p.name not in SKIP_NAMES
        and not p.name.endswith("_main.tscn"))

    identical, rewrites, problems = [], [], []
    for s in expected:
        rel = s.relative_to(src)
        d = staged / rel
        if not d.is_file():
            problems.append(f"MISSING in staged: {rel}")
            continue
        if s.suffix == ".tscn":
            a = rewritten(s.read_text(encoding="utf-8"))
            b = d.read_text(encoding="utf-8")
            if a == b:
                n = len(EXT_RESOURCE.findall(s.read_text(encoding="utf-8")))
                rewrites.append((rel, n))
            else:
                problems.append(
                    f"DIFFERS beyond the rewrite: {rel}")
        elif sha(s) == sha(d):
            identical.append((rel, s.stat().st_size))
        else:
            problems.append(f"BYTES DIFFER: {rel}")

    extra = sorted(
        p.relative_to(staged) for p in staged.rglob("*")
        if p.is_file() and not (src / p.relative_to(staged)).exists())
    for rel in extra:
        problems.append(f"EXTRA in staged, not in source: {rel}")

    print(f"source: {src}")
    print(f"staged: {staged}")
    print()
    total = sum(size for _, size in identical)
    print(f"byte-identical files: {len(identical)}  ({total:,} bytes)")
    for rel, size in identical[:6]:
        print(f"    {str(rel):58} {size:>10,}")
    if len(identical) > 6:
        print(f"    ... and {len(identical) - 6} more")
    print()
    print(f"scenes differing ONLY by the res:// rewrite: {len(rewrites)}")
    for rel, n in rewrites:
        print(f"    {str(rel):58} {n:>3} ext_resource path(s)")
    print()

    if problems:
        print(f"PROBLEMS: {len(problems)}")
        for p in problems:
            print(f"    {p}")
        print()
        print("VERDICT: staging changed something other than an ext_resource "
              "path prefix. It is a candidate cause and must be investigated.")
        return 1

    print("VERDICT: every .glb is byte-identical and every scene differs only "
          "by the res:// prefix on ext_resource lines.")
    print("Staging moved no geometry, changed no transform, and altered no "
          "mesh. Any misplaced geometry in the walk was baked before it ran.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
