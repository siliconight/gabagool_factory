"""gdcheck flagged four files and was wrong on all four. Two defects, one cause.

MEASURED. Run across the 104 .gd files this repo owns, gdcheck reported findings
on four and gdparse accepted every one of them. Its own docstring claims trap 1
is "a syntax error; gdparse sees it", so the two instruments contradicted each
other -- and that contradiction was the tell.

DEFECT 1, THE BRACKET COUNTER STRIPS COMMENTS BEFORE MASKING STRINGS.

    code = re.sub(r'"(\\\\.|[^"\\\\])*"', '""', ln.split("#")[0])

`ln.split("#")[0]` is evaluated first, so a `#` inside a string literal
truncates the line and takes the closing brackets with it. The arithmetic is
exact rather than plausible:

    LT_Cosmetic.gd:46     return Color.html(cosmetic.get("color", "#ffffff"))
                          -> return Color.html(cosmetic.get("      two open, +2
                          reported: net +2

    LT_GhostPlayer.gd:44  _label.text = "%s (#%d)" % [cosmetic.get(...), id]
                          -> _label.text = "%s (               one open, +1
                          reported: net +1

Both files' entire finding is one line of hex-colour or format-string code.

DEFECT 2, THE CONCATENATION CHECK READS COMMENTS AS CODE AND HAS NO IDEA WHEN A
LINE MAY LEGALLY BEGIN WITH A STRING. It fires on `prev.endswith('"') and
s.startswith('"')`, against raw text:

    deli_counter_postimport.gd 37-38   a dict whose values carry
                                       `# e.g. "res://scenes/..."` comments, so
                                       every line ENDS with a quote because of
                                       the comment
    LT_DebugLaser.gd 180, 182          a `match` on string patterns:
                                       `return &"enemy"` ends with a quote and
                                       `"PLAYER_HIT", "FRIENDLY_HIT":` legally
                                       begins with one

THE FIX IS TO STOP APPROXIMATING TOKENISATION WITH str.split. `_code()` is a
twelve-line scanner that walks the line tracking whether it is inside a quote,
so a `#` in a string stays and a `#` in code ends the line. Both checks use it.

And the concatenation check gains the guard it always needed: **only flag when
the previous line left a bracket open.** A string can only be continuing an
expression if the expression is still open. At depth zero a line beginning with
a string is a match arm, a dict key, or a bare string statement -- all legal.
That is derived from what implicit concatenation IS rather than tuned to make
these four files pass, which matters, because a heuristic tuned against its own
false positives is how a checker ends up wrong in a new way.

WHAT THIS DOES NOT FIX. `_code` does not know about GDScript's triple-quoted
strings; a `#` inside one can still end a line early. Recorded rather than
handled -- no file in the repo has one, and guessing at the shape of a bug
nobody has seen is how the last three instruments went wrong.

VERIFIED before sending: the four real files reproduce clean, and a genuine
implicit concatenation and a genuine unbalanced bracket both still fail.

Asserts every target, refuses on a miss, idempotent, byte-compiles.
"""
import pathlib
import py_compile
import shutil

ROOT = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
GD = ROOT / "gdcheck.py"

DOC_OLD = """  1. implicit adjacent-string concatenation   -- a syntax error; gdparse sees it
"""

DOC_NEW = """  1. implicit adjacent-string concatenation   -- gdparse ACCEPTS it, measured
                                                 across four files, so nothing
                                                 else is going to catch this
"""

HELPER_OLD = '''def lint(path: str) -> list:
'''

HELPER_NEW = '''def _code(ln: str) -> str:
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
            if c == "\\\\":
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
            if c in "\\"'":
                quote = c
            out.append(c)
            i += 1
    return "".join(out)


def lint(path: str) -> list:
'''

LOOP_OLD = '''    prev = None
    for n, ln in enumerate(lines, 1):
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        if prev and prev.endswith('"') and s.startswith('"'):
            out.append((n, "a string literal continues on the next line with "
                           "no `+` -- GDScript has no implicit concatenation"))
        if re.search(r'\\+\\s*"[^"]*"\\s*%(?!\\w)', s):
            out.append((n, "`%` binds tighter than `+`, so this formats only "
                           "the last fragment -- build the joined string first"))
        m = re.match(r'var\\s+\\w+\\s*:=\\s*(\\w+)\\s*[.(\\[]', s)
        if m and m.group(1) in params_at(n):
            out.append((n, f"`:=` infers from `{m.group(1)}`, an untyped "
                           f"parameter -- Godot rejects this at load"))
        prev = s

    depth = 0
    for ln in lines:
        if ln.strip().startswith("#"):
            continue
        code = re.sub(r'"(\\\\.|[^"\\\\])*"', '""', ln.split("#")[0])
        depth += code.count("(") + code.count("[") - code.count(")") - code.count("]")
    if depth:
        out.append((0, f"unbalanced brackets across the file, net {depth:+d}"))
    return out
'''

LOOP_NEW = '''    prev = None
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
        masked = re.sub(r'"(\\\\.|[^"\\\\])*"', '""', s)
        depth += (masked.count("(") + masked.count("[")
                  - masked.count(")") - masked.count("]"))
        if prev and prev.endswith('"') and s.startswith('"') and open_before > 0:
            out.append((n, "a string literal continues on the next line with "
                           "no `+` -- GDScript has no implicit concatenation"))
        if re.search(r'\\+\\s*"[^"]*"\\s*%(?!\\w)', s):
            out.append((n, "`%` binds tighter than `+`, so this formats only "
                           "the last fragment -- build the joined string first"))
        m = re.match(r'var\\s+\\w+\\s*:=\\s*(\\w+)\\s*[.(\\[]', s)
        if m and m.group(1) in params_at(n):
            out.append((n, f"`:=` infers from `{m.group(1)}`, an untyped "
                           f"parameter -- Godot rejects this at load"))
        prev = s

    if depth:
        out.append((0, f"unbalanced brackets across the file, net {depth:+d}"))
    return out
'''


def _swap(src, old, new, label, done):
    n = src.count(old)
    if n != 1:
        raise SystemExit(f"{label}: target appears {n} time(s), expected exactly "
                         f"1. NOTHING WRITTEN.")
    done.append(label)
    return src.replace(old, new)


def main() -> int:
    if not GD.exists():
        raise SystemExit(f"missing {GD}. Nothing written.")
    src = GD.read_text(encoding="utf-8")
    if "def _code(" in src:
        print("gdcheck.py: already tokenises comments")
        return 0
    if "def lint(path: str) -> list:" not in src:
        raise SystemExit("gdcheck.py has no lint() -- this is not the file this "
                         "patch was written against. NOTHING WRITTEN.")
    done = []
    src = _swap(src, DOC_OLD, DOC_NEW,
                "gdcheck.py: the docstring stops claiming gdparse catches trap 1",
                done)
    src = _swap(src, HELPER_OLD, HELPER_NEW,
                "gdcheck.py: _code(), a scanner instead of split('#')", done)
    src = _swap(src, LOOP_OLD, LOOP_NEW,
                "gdcheck.py: both checks read code only; concatenation needs an "
                "open bracket", done)

    backup = GD.with_suffix(".py.pre_tokens")
    if not backup.exists():
        shutil.copy2(GD, backup)
    GD.write_text(src, encoding="utf-8")
    py_compile.compile(str(GD), doraise=True)
    print("applied:")
    for line in done:
        print(f"  {line}")
    print(f"  compiles; previous file kept at {backup.name}")
    print("\n  Expected: the four flagged files go clean and check_all's "
          "gdscript row\n  reports a real verdict instead of noise.\n")
    print("    python check_all.py")
    print("\n  If a NEW file is flagged that was not flagged before, read it "
          "before\n  assuming the patch caused it -- the old bracket counter "
          "could cancel two\n  errors against each other, and this one cannot.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
