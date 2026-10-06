"""One generated index per folder nobody can read by listing it.

    python tools/factory_index.py                # print drift for every registered folder
    python tools/factory_index.py --check        # exit 1 on drift (what the hygiene check runs)
    python tools/factory_index.py --write        # rewrite every registered index in place
    python tools/factory_index.py --dir patches  # one folder, any of the above
    python tools/factory_index.py --selftest     # prove it on a throwaway folder

WHY GENERATED. `patches/` holds 978 files and `docs/findings/` 68 entries,
and until 2026-10-06 neither had an index; `migrations/MIGRATIONS.md` had a
typed table that stopped at 2026-08. A typed index is a document, and a
document drifts silently. This one is a measurement: each line is the
entry's own first sentence, read from the file, and `--check` fails the
moment the folder and the index disagree -- the same shape as
`roadmap_status.py` and `factory_map.py`.

WHAT A LINE IS. The entry's own description, never a guess:
    .py            the first line of the module docstring
    .md            the first heading
    .gd / .ps1 / .sh   the first comment line
    .json / .txt / other   the file name alone
    a directory    its README.md's first heading, else its file count
An entry without a description is listed as "(undescribed)", which is a
to-do, not a shrug: the fix is to give the file a docstring.

WHERE THE INDEX LIVES. `README.md` in the folder, between the markers
below. Prose above the markers is yours and survives every rewrite; the
block is not. A folder with no README gets one holding the block alone.
"""
import ast
import os
import re
import sys

BEGIN = "<!-- BEGIN GENERATED: factory_index.py -- do not edit by hand -->"
END = "<!-- END GENERATED -->"

#: folder -> (title, kinds of entry to list). Relative to the factory root.
REGISTRY = {
    "docs/findings": "Findings: investigations, each with its instruments beside it",
    "patches": "Patches: every anchored edit a tool repo received, by topic",
    "tools": "Tools: what you run against the factory",
    "scripts": "Scripts: standing PowerShell runbooks",
    "migrations": "Migrations: one-shots that already ran at the factory root",
    "deli_counter/migrations": "Deli Counter's one-shots and retired instruments",
    "docs/proposals": "Proposals: designs waiting for or past their decision",
    "docs/sessions": "Session notes and handoffs",
    "docs/history": "Reports from phases that are over",
}
SKIP = {"__pycache__", ".pytest_cache", "README.md", "MIGRATIONS.md", ".gitkeep"}


def factory_root():
    here = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        if os.path.exists(os.path.join(here, "factory.manifest.json")):
            return here
        here = os.path.dirname(here)
    raise SystemExit("factory.manifest.json not found above " + __file__)


def _first_line(text):
    for ln in text.splitlines():
        ln = ln.strip()
        if ln:
            return ln
    return ""


def describe(path):
    """The entry's own first sentence, by its kind. Never a guess."""
    name = os.path.basename(path)
    if os.path.isdir(path):
        readme = os.path.join(path, "README.md")
        if os.path.exists(readme):
            for ln in open(readme, encoding="utf-8", errors="replace"):
                if ln.startswith("#"):
                    return ln.lstrip("# ").strip()
        n = sum(len(f) for _d, _s, f in os.walk(path))
        # no README: the folder's first described file says what the folder
        # is, as a reader opening it would find out. 87 patch topic folders
        # read "2 file(s), no README" until this fallback (2026-10-06).
        for f in sorted(os.listdir(path)):
            if f in SKIP or os.path.isdir(os.path.join(path, f)):
                continue
            d = describe(os.path.join(path, f))
            if d and d not in ("(undescribed)", "(unreadable)"):
                return "%d file(s); %s" % (n, d)
        return "%d file(s), no README" % n
    ext = os.path.splitext(name)[1].lower()
    try:
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return "(unreadable)"
    if ext == ".py":
        # a file's own bad escape is its business, not this index's noise
        import warnings
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                doc = ast.get_docstring(ast.parse(text))
        except SyntaxError:
            doc = None
        return _first_line(doc) if doc else "(undescribed)"
    if ext == ".md":
        for ln in text.splitlines():
            if ln.startswith("#"):
                return ln.lstrip("# ").strip()
        return _first_line(text) or "(undescribed)"
    if ext in (".gd", ".ps1", ".sh"):
        for ln in text.splitlines():
            s = ln.strip()
            if s.startswith("#") or s.startswith("<#"):
                s = s.lstrip("<#").strip()
                if s:
                    return s
            elif s and not s.startswith("extends") and not s.startswith("param"):
                break
        return "(undescribed)"
    return ""


def render(folder, title):
    entries = sorted(e for e in os.listdir(folder) if e not in SKIP)
    dirs = [e for e in entries if os.path.isdir(os.path.join(folder, e))]
    files = [e for e in entries if not os.path.isdir(os.path.join(folder, e))]
    lines = [BEGIN, "", "## %s" % title, "",
             "%d entries: %d folders, %d files. Generated by `tools/factory_index.py`;" % (len(entries), len(dirs), len(files)),
             "`--check` fails when this block and the folder disagree.", ""]
    if dirs:
        lines += ["### Folders", ""]
        for d in dirs:
            lines.append("- `%s/` -- %s" % (d, describe(os.path.join(folder, d))))
        lines.append("")
    if files:
        lines += ["### Files", ""]
        for f in files:
            desc = describe(os.path.join(folder, f))
            lines.append("- `%s`%s" % (f, (" -- " + desc) if desc else ""))
        lines.append("")
    lines.append(END)
    return "\n".join(lines) + "\n"


def splice(existing, block):
    """The README with its generated block replaced, or appended."""
    if BEGIN in existing and END in existing:
        a = existing.index(BEGIN)
        b = existing.index(END) + len(END)
        tail = existing[b:]
        if tail.startswith("\n"):
            tail = tail[1:]
        return existing[:a] + block + tail
    if existing and not existing.endswith("\n"):
        existing += "\n"
    return existing + ("\n" if existing else "") + block


def current_block(existing):
    if BEGIN in existing and END in existing:
        return existing[existing.index(BEGIN):existing.index(END) + len(END)] + "\n"
    return None


def run(root, folders, write):
    drift = 0
    for rel in folders:
        folder = os.path.join(root, rel)
        if not os.path.isdir(folder):
            print("  %-26s (no such folder)" % rel)
            continue
        readme = os.path.join(folder, "README.md")
        existing = open(readme, encoding="utf-8").read() if os.path.exists(readme) else ""
        block = render(folder, REGISTRY.get(rel, rel))
        same = current_block(existing) == block
        if write and not same:
            with open(readme, "w", encoding="utf-8", newline="\n") as f:
                f.write(splice(existing, block))
        n = block.count("\n- ")
        print("  %-26s %4d entries  %s" % (rel, n, "matches" if same else ("WRITTEN" if write else "DRIFT")))
        drift += 0 if same else 1
    return drift


def selftest():
    import tempfile
    d = tempfile.mkdtemp(prefix="factory_index_")
    os.makedirs(os.path.join(d, "sub"))
    open(os.path.join(d, "a.py"), "w").write('"""A probe.\n\nMore."""\n')
    open(os.path.join(d, "b.md"), "w").write("intro\n# A finding\n")
    open(os.path.join(d, "c.gd"), "w").write("# Bakes a thing\nextends SceneTree\n")
    open(os.path.join(d, "d.json"), "w").write("{}")
    open(os.path.join(d, "e.py"), "w").write("x = 1\n")
    open(os.path.join(d, "sub", "README.md"), "w").write("# Sub things\n")
    block = render(d, "T")
    want = ["- `sub/` -- Sub things", "- `a.py` -- A probe.", "- `b.md` -- A finding",
            "- `c.gd` -- Bakes a thing", "- `d.json`", "- `e.py` -- (undescribed)"]
    for w in want:
        assert w in block, (w, block)
    prose = "# Mine\n\nkeep this\n"
    once = splice(prose, block)
    assert once.startswith(prose) and once.count(BEGIN) == 1
    twice = splice(once, block)
    assert twice == once, "a second splice must be a no-op"
    assert current_block(once) == block
    print("selftest ok")


def main():
    argv = sys.argv[1:]
    if "--selftest" in argv:
        return selftest()
    root = factory_root()
    folders = [argv[argv.index("--dir") + 1]] if "--dir" in argv else list(REGISTRY)
    drift = run(root, folders, "--write" in argv)
    if "--check" in argv and drift:
        print("  %d index(es) drift; run with --write" % drift)
        sys.exit(1)


if __name__ == "__main__":
    main()
