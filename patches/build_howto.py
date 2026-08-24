#!/usr/bin/env python3
"""build_howto.py -- how do I build ONE shell and run the gate on it?"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DC = os.path.join(ROOT, "deli_counter")

def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")

def cli_of(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        src = fh.read()
    out = []
    for m in re.finditer(r'add_argument\(\s*([^)]{0,140})', src):
        out.append(("arg", src[: m.start()].count("\n") + 1, m.group(1).strip()[:110]))
    for m in re.finditer(r'add_parser\(\s*["\']([a-z0-9_-]+)["\']', src):
        out.append(("cmd", src[: m.start()].count("\n") + 1, m.group(1)))
    return out

for fn in ("deli_counter.py", "nav_gate.py"):
    p = os.path.join(DC, fn)
    if not os.path.isfile(p):
        print("%s NOT FOUND" % fn); continue
    print("=" * 76)
    print("%s -- CLI surface" % rel(p))
    print("=" * 76)
    got = cli_of(p)
    if not got:
        print("  no argparse found")
    for kind, line, text in got[:40]:
        print("  %-4s %5d  %s" % (kind, line, text))
    print("")

print("=" * 76)
print("DOES THE BUILDER REGENERATE SPECS FROM presets.py?")
print("=" * 76)
hits = 0
for dp, dns, fns in os.walk(DC):
    if re.search(r'[\\/](build|__pycache__|_probe|specs)$', dp):
        dns[:] = []
        continue
    for fn in fns:
        if not fn.endswith(".py"):
            continue
        p = os.path.join(dp, fn)
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
        for i, l in enumerate(lines, 1):
            if re.search(r'import presets|from presets|presets\.\w+\(|'
                         r'json\.dump.*spec', l):
                print("  %s:%d  %s" % (rel(p), i, l.strip()[:110]))
                hits += 1
                if hits >= 26:
                    break
        if hits >= 26:
            break
    if hits >= 26:
        break
if hits == 0:
    print("  no reference found -- specs look like checked-in inputs, not outputs")

print("")
print("=" * 76)
print("BUILD SCRIPTS / HOOK")
print("=" * 76)
for cand in ("tools", ".githooks", "scripts"):
    d = os.path.join(DC, cand)
    if os.path.isdir(d):
        for fn in sorted(os.listdir(d))[:20]:
            print("  %s" % rel(os.path.join(d, fn)))
for h in (os.path.join(ROOT, ".git", "hooks", "pre-commit"),
          os.path.join(DC, ".git", "hooks", "pre-commit")):
    if os.path.isfile(h):
        print("")
        print("  hook %s:" % rel(h))
        with open(h, "r", encoding="utf-8", errors="replace") as fh:
            for i, l in enumerate(fh.read().splitlines()[:40], 1):
                print("    %3d  %s" % (i, l.rstrip()[:120]))
        break

print("")
print("night_pawn build artefacts currently on disk")
b = os.path.join(DC, "build")
for fn in sorted(os.listdir(b)):
    if fn.startswith("night_pawn"):
        print("  %-40s %9d bytes" % (fn, os.path.getsize(os.path.join(b, fn))))
