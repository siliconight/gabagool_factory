"""Check a GDScript file before it is sent to a machine that can run Godot.

Four round-trips on this probe were spent on things Godot rejects at load, each
costing a full turn to discover. Three distinct classes, and no single tool
catches all three:

  1. implicit adjacent-string concatenation   -- gdparse ACCEPTS it, measured
                                                 across four files, so nothing
                                                 else is going to catch this
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


def _code(ln: str) -> str:
    """`ln` with any trailing comment removed, respecting string literals.

    A `#` inside a string is not a comment. This file used to split on `#`
    first, which truncated

        return Color.html(cosmetic.get("color", "#ffffff"))

    to `return Color.html(cosmetic.get("` and then reported two unbalanced
    brackets on code that is perfectly balanced. Three of the four files this
    checker has ever flagged were that one line of it.

    Known gap: triple-quoted strings are not tracked. No file in the repo has
    one; if that changes, this is where it breaks.
    """
    out, i, quote = [], 0, None
    while i < len(ln):
        c = ln[i]
        if quote:
            if c == "\\":
                out.append(ln[i:i + 2])
                i += 2
                continue
            out.append(c)
            if c == quote:
                quote = None
            i += 1
        elif c == "#":
            break
        else:
            if c in "\"'":
                quote = c
            out.append(c)
            i += 1
    return "".join(out)


#: A function signature as Godot spells it: an optional `static` before
#: `func`. Anchored after indentation so a `func` inside a string cannot match
#: -- this scanner reads raw lines, unlike the checks below it, which read
#: `_code(ln)` with comments already stripped.
_FUNC = re.compile(r"^[ \t]*(?:static[ \t]+)?func[ \t]+\w+")


def lint(path: str) -> list:
    """The failures a grammar check cannot see."""
    lines = open(path, encoding="utf-8").read().splitlines()
    out = []

    # every function's untyped parameter names, keyed by the line its
    # signature ends on, so a `:=` below it can be attributed to the right one
    #
    # `static func` COUNTS, and missing it was not a cosmetic gap. Until
    # 2026-09-25 this tested `startswith("func ")`, so no static function ever
    # entered `funcs`, and `params_at` -- which returns the nearest preceding
    # entry -- attributed every line inside one to the last NON-static function
    # above it. That produced false positives on Lux's shipped addon
    # (`lux_validator.gd:373` and `skymint_profile.gd:138`, neither of which
    # shadows anything) and, worse because nobody sees them, false negatives:
    # a real shadow or a `:=` on an untyped parameter inside a static function
    # was uncatchable, and both are load-time parse errors.
    funcs = []
    i = 0
    while i < len(lines):
        if _FUNC.match(lines[i]):
            sig, j = lines[i], i
            while sig.count("(") > sig.count(")") and j + 1 < len(lines):
                j += 1
                sig += " " + lines[j].strip()
            if "(" in sig and ")" in sig:
                inner = sig[sig.index("(") + 1:sig.rindex(")")]
                parts = [q.strip() for q in inner.split(",") if q.strip()]
                untyped = {p.split("=")[0].strip()
                           for p in parts if ":" not in p}
                # EVERY parameter, typed or not, for the shadowing trap below.
                allp = {p.split("=")[0].split(":")[0].strip() for p in parts}
                funcs.append((j, untyped, allp))
            i = j
        i += 1

    def params_at(n, which=0):
        cur = set()
        for entry in funcs:
            if entry[0] < n:
                cur = entry[1 + which]
        return cur

    prev = None
    depth = 0
    for n, ln in enumerate(lines, 1):
        # Comments removed by scanner, not by split -- see _code. Every check
        # below reads code only, so a `#` in a string no longer truncates a
        # line and a comment mentioning `+ "x" %` no longer raises a finding.
        s = _code(ln).strip()
        if not s:
            continue
        # Bracket depth as this line STARTS. A string can only be continuing an
        # expression if the expression is still open, so this is the whole
        # difference between real implicit concatenation and a line that merely
        # begins with a quote -- a match arm, a dict key, a bare string
        # statement. All three are legal and all three used to be flagged.
        open_before = depth
        masked = re.sub(r'"(\\.|[^"\\])*"', '""', s)
        depth += (masked.count("(") + masked.count("[")
                  - masked.count(")") - masked.count("]"))
        if prev and prev.endswith('"') and s.startswith('"') and open_before > 0:
            out.append((n, "a string literal continues on the next line with "
                           "no `+` -- GDScript has no implicit concatenation"))
        if re.search(r'\+\s*"[^"]*"\s*%(?!\w)', s):
            out.append((n, "`%` binds tighter than `+`, so this formats only "
                           "the last fragment -- build the joined string first"))
        # THE SUFFIX USED TO BE REQUIRED -- `[.(\[]` -- so this caught
        # `var n := param.field` and missed a bare `var n := param`, which is
        # the same load-time error ("Cannot infer the type of 'n' variable
        # because the value doesn't have a set type"). Widening is safe
        # because the finding is gated on membership in the UNTYPED parameter
        # set below: a typed parameter never reaches it, and a call like
        # `var n := helper(x)` captures `helper`, which is not a parameter.
        m = re.match(r'var\s+\w+\s*:=\s*(\w+)\b', s)
        if m and m.group(1) in params_at(n):
            out.append((n, f"`:=` infers from `{m.group(1)}`, an untyped "
                           f"parameter -- Godot rejects this at load"))
        # A LOCAL MAY NOT REUSE A PARAMETER'S NAME. Godot raises "There is
        # already a parameter named X declared in this scope" as a PARSE
        # ERROR at load -- not a warning -- so the script never runs. Cost:
        # one round-trip on tools/navmesh_demo.gd, where `var climb` shadowed
        # the bake's `climb` parameter and the driver reported only "wrote no
        # report" because it swallowed the engine's output.
        m2 = re.match(r'var\s+(\w+)\b', s)
        if m2 and m2.group(1) in params_at(n, 1):
            out.append((n, f"`var {m2.group(1)}` shadows a parameter of the "
                           f"same name -- Godot rejects this at load as a "
                           f"parse error"))
        prev = s

    if depth:
        out.append((0, f"unbalanced brackets across the file, net {depth:+d}"))
    return out


def main(argv) -> int:
    if not argv:
        print(__doc__.strip().splitlines()[-1].strip())
        return 2
    # Is the parser usable AT ALL? Asked once, before any file, because
    # "the parser is missing" and "this file is bad" are different answers and
    # inferring the first from a failed parse of the second gets it wrong. The
    # earlier version keyed on "No module named" appearing in stderr, which a
    # parser broken any other way does not say -- and it then reported the
    # breakage as a defect in the file being checked.
    parser_ok = False
    parser_why = ""
    try:
        probe = subprocess.run(
            [sys.executable, "-c", "import gdtoolkit.parser"],
            capture_output=True, text=True)
        parser_ok = probe.returncode == 0
        if not parser_ok:
            tail = (probe.stderr or "").strip().splitlines()
            parser_why = tail[-1] if tail else "import failed"
    except OSError as e:
        parser_why = f"{type(e).__name__}: {e}"
    if not parser_ok:
        print("THE GDSCRIPT GRAMMAR CHECK IS NOT RUNNING.")
        print(f"  {parser_why}")
        print(f"  install it with: {sys.executable} -m pip install gdtoolkit")
        print("  The hand-written trap checks below still run, but a file that "
              "passes\n  only those has not been parsed. Do not read it as "
              "clean.\n")

    bad = 0
    for path in argv:
        problems = []
        # Invoke the MODULE, not the `gdparse` console script. pip installs that
        # shim into a Scripts directory it warns may not be on PATH, and on a
        # clean install it was not -- so this raised FileNotFoundError with
        # gdtoolkit correctly installed, and the traceback made whatever ran
        # gdcheck look like the thing that was broken. Going through
        # sys.executable also guarantees the parser comes from the same
        # interpreter as this script rather than whichever one PATH finds first.
        if parser_ok:
            r = subprocess.run(
                [sys.executable, "-m", "gdtoolkit.parser", path],
                capture_output=True, text=True)
            if r.returncode != 0:
                tail = (r.stderr or r.stdout or "").strip().splitlines()
                problems.append((0, "gdparse: "
                                 + (tail[-1] if tail else "rejected")))
        problems += lint(path)
        if problems:
            bad += 1
            print(f"{path}:")
            for n, why in sorted(problems):
                where = f"  line {n}: " if n else "  "
                print(where + why)
        elif parser_ok:
            print(f"{path}: parses, and none of the four known traps")
        else:
            print(f"{path}: none of the four known traps -- NOT PARSED")
    # 1 = checked and found problems. 2 = could not fully check. Distinct,
    # because a checker that could not run must not report what a clean file
    # reports.
    if bad:
        return 1
    return 0 if parser_ok else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
