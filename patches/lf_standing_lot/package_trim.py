"""What Level Factory 0.207.0 left out of a package, measured against a package exported before it.

    python patches/lf_standing_lot/package_trim.py <control package> <subject package>

For each package: its `lot/` packages and the ones its assembly scene (`site.tscn`) names; its files and bytes; the
light bake's model imports (`light_bake.json` `imports.baked`), lightmap users (`result.users`) and its two timings
(`editor_s`, the editor's import; `result.bake_ms`), one run each and so no price; and the closure verdict
(`export_closure_scan.json`). Then, across the two:
- the files only one package carries, grouped by `lot/<id>` or top directory;
- of the files both carry by path, how many are byte-identical, and every one that is not.

Prints what it measured and stops. An unreadable artefact, or a key it cannot find, stops it with an error rather
than reading as an empty list.
"""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

LOT_REF = re.compile(r'path="(res://)?lot/([^"/]+)/site\.tscn"')


def need(d, *keys):
    for k in keys:
        if not isinstance(d, dict) or k not in d:
            raise SystemExit("missing key %s in %r" % (".".join(keys), list(d)[:12] if isinstance(d, dict) else d))
        d = d[k]
    return d


def group(rel):
    parts = rel.split("/")
    return "/".join(parts[:2]) if parts[0] == "lot" and len(parts) > 2 else parts[0]


def read(pkg):
    pkg = Path(pkg)
    site = (pkg / "site.tscn").read_text(encoding="utf-8", errors="replace")
    refs = LOT_REF.findall(site)
    files = {}
    for p in pkg.rglob("*"):
        if p.is_file():
            data = p.read_bytes()
            files[p.relative_to(pkg).as_posix()] = (len(data), hashlib.sha256(data).hexdigest())
    bake = json.loads((pkg / "light_bake.json").read_text(encoding="utf-8"))
    scan = json.loads((pkg / "export_closure_scan.json").read_text(encoding="utf-8"))
    return {
        "lot": sorted(d.name for d in (pkg / "lot").iterdir() if d.is_dir()),
        "named": sorted({r[1] for r in refs}),
        "named_res": sum(1 for r in refs if r[0]),
        "files": files,
        "baked": list(need(bake, "imports", "baked")),
        "bake_ok": need(bake, "ok"),
        "users": need(bake, "result", "users"),
        "editor_s": need(bake, "editor_s"),
        "bake_ms": need(bake, "result", "bake_ms"),
        "closure": {k: need(scan, k) for k in ("ok", "missing_resource_count", "unresolved_relative_count",
                                               "package_file_count")},
    }


def main(control, subject):
    a, b = read(control), read(subject)
    for name, r in (("control", a), ("subject", b)):
        print("%s  %s" % (name, control if r is a else subject))
        print("  lot/ packages %d, named by site.tscn %d (res:// %d); unnamed: %s; named and absent: %s" % (
            len(r["lot"]), len(r["named"]), r["named_res"],
            ", ".join(sorted(set(r["lot"]) - set(r["named"]))) or "none",
            ", ".join(sorted(set(r["named"]) - set(r["lot"]))) or "none"))
        print("  files %d, bytes %d (%.1f MB)" % (len(r["files"]), sum(s for s, _ in r["files"].values()),
                                                 sum(s for s, _ in r["files"].values()) / 1e6))
        print("  light bake ok %s, imports.baked %d, result.users %d; editor_s %.1f, result.bake_ms %d (one run each)" % (
            r["bake_ok"], len(r["baked"]), r["users"], r["editor_s"], r["bake_ms"]))
        print("  closure %s" % r["closure"])
    print("lot/ packages only in control: %s" % (", ".join(sorted(set(a["lot"]) - set(b["lot"]))) or "none"))
    print("lot/ packages only in subject: %s" % (", ".join(sorted(set(b["lot"]) - set(a["lot"]))) or "none"))
    gone = Counter(group(p) for p in set(a["baked"]) - set(b["baked"]))
    new = Counter(group(p) for p in set(b["baked"]) - set(a["baked"]))
    print("baked imports only in control: %d %s" % (sum(gone.values()), dict(sorted(gone.items()))))
    print("baked imports only in subject: %d %s" % (sum(new.values()), dict(sorted(new.items()))))
    fa, fb = a["files"], b["files"]
    for label, only in (("control", set(fa) - set(fb)), ("subject", set(fb) - set(fa))):
        by = Counter(group(p) for p in only)
        size = Counter()
        for p in only:
            size[group(p)] += (fa if label == "control" else fb)[p][0]
        print("files only in %s: %d, %d bytes" % (label, len(only), sum(size.values())))
        for g in sorted(by):
            print("  %-40s %5d files %11d bytes" % (g, by[g], size[g]))
    shared = sorted(set(fa) & set(fb))
    differ = [p for p in shared if fa[p][1] != fb[p][1]]
    print("files in both: %d, byte-identical %d, differing %d" % (len(shared), len(shared) - len(differ), len(differ)))
    for p in differ:
        print("  differs  %s  %d -> %d bytes" % (p, fa[p][0], fb[p][0]))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
