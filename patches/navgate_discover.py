#!/usr/bin/env python3
"""navgate_discover.py -- locate the nav gate, spawn markers, and the shells.

READS ONLY. Prints how many files it scanned and refuses to conclude from an
empty read. Every hit is reported with its file so a wrong location is visible
rather than silently producing an empty answer.
"""
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SKIP = re.compile(
    r'(^|[\\/])(\.git|__pycache__|node_modules|\.venv|venv|site-packages'
    r'|\.mypy_cache|\.pytest_cache|_preview[^\\/]*|_probe|_runs|_scratch'
    r'|\.import|\.godot)([\\/]|$)'
)
EXTS = {".py", ".md", ".json", ".ps1", ".tscn", ".gd", ".toml", ".cfg", ".txt", ".yaml", ".yml"}

TERMS = {
    "nav gate":      re.compile(r'nav[_ -]?gate', re.I),
    "spawn marker":  re.compile(r'spawn[_ ]?(marker|point|node)', re.I),
    "markerless":    re.compile(r'markerless', re.I),
    "navmesh":       re.compile(r'nav[_ ]?mesh', re.I),
    "shell":         re.compile(r'\bshells?\b', re.I),
    "bank_job":      re.compile(r'bank_job', re.I),
    "baie_dore":     re.compile(r'baie_dore', re.I),
    "night_pawn":    re.compile(r'night_pawn', re.I),
}

def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")

scanned = 0
skipped_big = 0
hits = defaultdict(Counter)       # term -> Counter(file -> n)
defsites = defaultdict(list)      # term -> [(file, lineno, text)]

for dp, dns, fns in os.walk(ROOT):
    if SKIP.search(dp):
        dns[:] = []
        continue
    for fn in fns:
        if fn.endswith(".pre_") or re.search(r'\.pre_[a-z0-9]+$', fn):
            continue
        ext = os.path.splitext(fn)[1].lower()
        if ext not in EXTS:
            continue
        p = os.path.join(dp, fn)
        try:
            if os.path.getsize(p) > 2_000_000:
                skipped_big += 1
                continue
            with open(p, "r", encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except Exception:
            continue
        scanned += 1
        low = text
        for term, rx in TERMS.items():
            found = rx.findall(low)
            if not found:
                continue
            hits[term][rel(p)] += len(found)
            if term in ("nav gate", "spawn marker", "markerless"):
                for i, line in enumerate(text.splitlines(), 1):
                    if rx.search(line) and re.search(
                            r'^\s*(def |class |[A-Z_]{3,}\s*=|#|"""|\'\'\')', line):
                        defsites[term].append((rel(p), i, line.strip()[:110]))

print("files scanned: %d   (skipped %d over 2MB)" % (scanned, skipped_big))
if scanned == 0:
    print("REFUSING TO CONCLUDE -- scanned nothing under %s" % ROOT)
    sys.exit(2)
print("")

for term in TERMS:
    c = hits[term]
    total = sum(c.values())
    print("=" * 74)
    print("%-14s %d hit(s) in %d file(s)" % (term, total, len(c)))
    print("=" * 74)
    if not c:
        print("      none")
        continue
    for f, n in c.most_common(12):
        print("      %4d  %s" % (n, f))
    if len(c) > 12:
        print("      ... %d more file(s)" % (len(c) - 12))
    for f, i, line in defsites.get(term, [])[:8]:
        print("        def> %s:%d  %s" % (f, i, line))
print("")

# where do CLI subcommands live? the gate is probably one.
print("=" * 74)
print("CLI SUBCOMMANDS mentioning gate / nav / spawn")
print("=" * 74)
found_any = False
for dp, dns, fns in os.walk(ROOT):
    if SKIP.search(dp):
        dns[:] = []
        continue
    for fn in fns:
        if not fn.endswith(".py"):
            continue
        p = os.path.join(dp, fn)
        try:
            with open(p, "r", encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except Exception:
            continue
        for m in re.finditer(r'add_parser\(\s*["\']([a-z0-9_-]+)["\']', text):
            name = m.group(1)
            if re.search(r'gate|nav|spawn|shell', name):
                line = text[: m.start()].count("\n") + 1
                print("      %s:%d  add_parser(%r)" % (rel(p), line, name))
                found_any = True
if not found_any:
    print("      none found by add_parser")
