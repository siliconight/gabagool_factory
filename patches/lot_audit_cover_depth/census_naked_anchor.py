"""Roadmap 211's census: every site spec on disk audited twice, once with
`site_audit._cover_rects` as shipped (the middle number of `size` read as the
plan depth) and once reading the third, and every `S_NAKED_ANCHOR` that the
two disagree on listed with its site.

    python census_naked_anchor.py <factory root>

Reads every `workspaces/*/.level_factory/jobs/*lot_assemble*/out/site.site.drawn.json`
(the spec as Lot drew it, cover included) and every `lot/specs/**/*.json` that
is a site spec. Prints what it measured and stops.
"""
import glob
import json
import os
import sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
sys.path.insert(0, os.path.join(ROOT, "lot"))

import site_audit  # noqa: E402

SHIPPED = site_audit._cover_rects


def depth_third(site):
    out = []
    for c in site.get("cover", []):
        (x, y), s = c["at"][:2], c.get("size", [1, 1, 1])
        out.append((x - s[0] / 2, y - s[2] / 2, x + s[0] / 2, y + s[2] / 2))
    return out


def naked(site, reader):
    site_audit._cover_rects = reader
    try:
        found = site_audit.audit(site)["findings"]
    finally:
        site_audit._cover_rects = SHIPPED
    return sorted(f[2] for f in found if f[1] == "S_NAKED_ANCHOR")


def specs():
    for p in sorted(glob.glob(os.path.join(
            ROOT, "workspaces", "*", ".level_factory", "jobs", "*lot_assemble*", "out",
            "site.site.drawn.json"))):
        yield p
    for p in sorted(glob.glob(os.path.join(ROOT, "lot", "specs", "**", "*.json"), recursive=True)):
        yield p


read = skipped = with_cover = 0
moved = []
for path in specs():
    try:
        site = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        skipped += 1
        continue
    if not isinstance(site, dict) or not isinstance(site.get("buildings"), list):
        skipped += 1
        continue
    read += 1
    if site.get("cover"):
        with_cover += 1
    try:
        old, new = naked(site, SHIPPED), naked(site, depth_third)
    except Exception as exc:                      # a spec the audit cannot read
        print(f"  AUDIT FAILED {os.path.relpath(path, ROOT)}: {type(exc).__name__}: {exc}")
        continue
    if old != new:
        moved.append((os.path.relpath(path, ROOT), old, new))

print(f"{read} site specs audited ({with_cover} with cover), {skipped} files not site specs")
print(f"S_NAKED_ANCHOR differs on {len(moved)}")
for rel, old, new in moved:
    print(f"  {rel}")
    for m in old:
        if m not in new:
            print(f"    only as shipped: {m[:150]}")
    for m in new:
        if m not in old:
            print(f"    only reading depth: {m[:150]}")
