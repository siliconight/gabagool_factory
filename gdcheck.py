"""Check a GDScript file before it is sent to a machine that can run Godot.

Four round-trips on this probe were spent on things Godot rejects at load, each
costing a full turn to discover. Three distinct classes, and no single tool
catches all three:

  1. implicit adjacent-string concatenation   -- a syntax error; gdparse sees it
  2. `%` binding tighter than `+`             -- parses fine, formats the wrong
                                                 fragment at runtime
  3. `:=` inferring from an untyped parameter -- Godot rejects it at load as a
                                                 parse error, but it is a TYPE
                                                 question and gdparse, being a
                                                 grammar, has no opinion on it

So this runs gdtoolkit's parser for the grammar and a small set of heuristics
for the two the grammar cannot see. It is not a substitute for loading the file
in Godot; it is a substitute for finding out from Godot that a string literal
was split across two lines.

    python gdcheck.py <file.gd> [<file.gd> ...]
"""
import re
import subprocess
import sys


def lint(path: str) -> list:
    """The failures a grammar check cannot see."""
    lines = open(path, encoding="utf-8").read().splitlines()
    out = []

    # every function's untyped parameter names, keyed by the line its
    # signature ends on, so a `:=` below it can be attributed to the right one
    funcs = []
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("func "):
            sig, j = lines[i], i
            while sig.count("(") > sig.count(")") and j + 1 < len(lines):
                j += 1
                sig += " " + lines[j].strip()
            if "(" in sig and ")" in sig:
                inner = sig[sig.index("(") + 1:sig.rindex(")")]
                untyped = {p.split("=")[0].strip()
                           for p in [q.strip() for q in inner.split(",") if q.strip()]
                           if ":" not in p}
                funcs.append((j, untyped))
            i = j
        i += 1

    def params_at(n):
        cur = set()
        for start, untyped in funcs:
            if start < n:
                cur = untyped
        return cur

    prev = None
    for n, ln in enumerate(lines, 1):
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        if prev and prev.endswith('"') and s.startswith('"'):
            out.append((n, "a string literal continues on the next line with "
                           "no `+` -- GDScript has no implicit concatenation"))
        if re.search(r'\+\s*"[^"]*"\s*%(?!\w)', s):
            out.append((n, "`%` binds tighter than `+`, so this formats only "
                           "the last fragment -- build the joined string first"))
        m = re.match(r'var\s+\w+\s*:=\s*(\w+)\s*[.(\[]', s)
        if m and m.group(1) in params_at(n):
            out.append((n, f"`:=` infers from `{m.group(1)}`, an untyped "
                           f"parameter -- Godot rejects this at load"))
        prev = s

    depth = 0
    for ln in lines:
        if ln.strip().startswith("#"):
            continue
        code = re.sub(r'"(\\.|[^"\\])*"', '""', ln.split("#")[0])
        depth += code.count("(") + code.count("[") - code.count(")") - code.count("]")
    if depth:
        out.append((0, f"unbalanced brackets across the file, net {depth:+d}"))
    return out


def main(argv) -> int:
    if not argv:
        print(__doc__.strip().splitlines()[-1].strip())
        return 2
    bad = 0
    for path in argv:
        problems = []
        r = subprocess.run(["gdparse", path], capture_output=True, text=True)
        if r.returncode != 0:
            tail = (r.stderr or r.stdout or "").strip().splitlines()
            problems.append((0, "gdparse: " + (tail[-1] if tail else "rejected")))
        problems += lint(path)
        if problems:
            bad += 1
            print(f"{path}:")
            for n, why in sorted(problems):
                where = f"  line {n}: " if n else "  "
                print(where + why)
        else:
            print(f"{path}: parses, and none of the three known traps")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
