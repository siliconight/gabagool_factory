"""Repair the site_shape announcement in commands/__init__.py.

The heredoc that wrote it collapsed `\\n` inside an f-string into a literal
newline and split the string across lines -- SyntaxError at import, which
took every test that imports the CLI down with it. Same trap the repo's
CLAUDE.md lists for GDScript; it is not GDScript-specific.

Rewritten as separate print calls with no escapes at all. Spliced by index
between two markers that survived the collapse intact.
"""
import io
import sys

P = "level_factory/apps/cli/commands/__init__.py"
START = '    if not site_variation.shape_known(model.site_shape):\n'
END = '            file=sys.stderr)\n'

GOOD = '''    if not site_variation.shape_known(model.site_shape):
        # The capability-gap voice USING_THE_FACTORY.md asks every tool for:
        # what was asked, what exists, who is short. Non-blocking, because a
        # row is a real site and the brief still builds.
        err = sys.stderr
        print("  site_shape: %r is not a spelling site_variation knows -- "
              "laid out as a ROW" % (model.site_shape,), file=err)
        print("    known: " + ", ".join(site_variation.known_spellings()),
              file=err)
        print("    add the spelling to _SHAPE_ALIASES, or change the brief; "
              "the fallback is recorded in the site spec as "
              "site_shape_resolved", file=err)
'''


def main() -> int:
    t = io.open(P, encoding="utf-8", newline="").read()
    if t.count(START) != 1:
        print("start marker matched %d times" % t.count(START), file=sys.stderr)
        return 1
    a = t.index(START)
    b = t.index(END, a)
    if b - a > 1200:
        print("span too long (%d) -- refusing" % (b - a), file=sys.stderr)
        return 1
    b += len(END)
    print("replacing %d bytes:\n%s" % (b - a, t[a:b]))
    t = t[:a] + GOOD + t[b:]
    io.open(P, "w", encoding="utf-8", newline="").write(t)
    compile(t, P, "exec")          # refuse to leave it unimportable again
    print("repaired and compiles")
    return 0


if __name__ == "__main__":
    sys.exit(main())
