"""Write patches/patch_dc_facade_stack.py (Deli Counter 0.238.0, roadmap 79) from the proven dc_facade clone.

Each edited file's hunks are taken from a line diff of the REAL repo's pinned file against the clone's, each widened by
context lines until its old text occurs exactly once; the generator applies them to the real file and refuses to write
the patch unless the result is byte-identical to the clone's file. New files are embedded verbatim.

    python gen_dc_facade_stack.py         # dry: build the patch in memory, check it compiles
    python gen_dc_facade_stack.py --write # write it (refuses if the name is taken)
    --base <dir>                            # read the pinned files from a checkout of 0.237.0 instead of
                                            # deli_counter/ (once the patch is applied there)
"""
import difflib
import hashlib
import pathlib
import sys

FACTORY = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
DC = (pathlib.Path(sys.argv[sys.argv.index("--base") + 1]) if "--base" in sys.argv
      else FACTORY / "deli_counter")
SCRATCH = pathlib.Path(r"C:\Users\Brannen\AppData\Local\Temp\claude\C--Projects-gabagool-studios-gabagool-factory"
                       r"\27f14f8b-7ce5-44c0-a704-178a824035d7\scratchpad")
CLONE = SCRATCH / "dc_facade"
import subprocess as _sp
EDITED = ["presets.py", "build_freshness.py"] + sorted(
    l[3:] for l in _sp.run(["git", "-C", str(CLONE), "status", "--short"], capture_output=True, text=True,
                           check=True).stdout.splitlines() if l[3:].startswith("specs/"))
assert len(EDITED) == 2 + 32, len(EDITED)
NEW_FILES = ["facade_plan.py", "migrate_facade_stack.py", "test_facade_plan.py"]
OLD_VERSION, NEW_VERSION = "Deli Counter 0.237.0", "Deli Counter 0.238.0"


def sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def hunks(old, new):
    """[(what, old_text, new_text)] turning `old` into `new`, each old_text unique in `old` and no two overlapping.

    Each change is widened by context lines until its old text occurs once; windows that then overlap or touch are
    merged into one, so applying them in order never asks for text an earlier hunk has already rewritten (the
    first version of this generator, copied from 0.237.0's, applied overlapping hunks one after another and the
    32 refurnished specs' third hunk found its anchor gone)."""
    a, b = old.splitlines(keepends=True), new.splitlines(keepends=True)
    ops = difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()

    def bmap(i):
        for tag, i1, i2, j1, j2 in ops:
            if tag == "equal" and i1 <= i <= i2:
                return j1 + (i - i1)
            if i == i1:
                return j1
        return len(b)

    wins = []
    for tag, i1, i2, j1, j2 in ops:
        if tag == "equal":
            continue
        ctx = 0
        while True:
            lo, hi = max(0, i1 - ctx), min(len(a), i2 + ctx)
            o = "".join(a[lo:hi])
            if o and old.count(o) == 1:
                break
            ctx += 1
            assert ctx < 40, "no unique anchor near line %d" % (i1 + 1)
        wins.append([lo, hi])
    merged = []
    for w in wins:
        if merged and w[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], w[1])
        else:
            merged.append(w)
    out = []
    for lo, hi in merged:
        o, n = "".join(a[lo:hi]), "".join(b[bmap(lo):bmap(hi)])
        assert old.count(o) == 1
        out.append(("lines %d-%d" % (lo + 1, hi), o, n))
    return out


#: The refurnished specs are DATA, patched BY LINE: their JSON repeats the same lines so often that string anchors,
#: however widened, can be recreated by an earlier hunk's own replacement (casino_a03.json's was). The hash pin
#: fixes the base's exact bytes, so each hunk is placed at its line, checked there, and applied bottom-up. (Whole
#: files under the pin worked too, and made the patch 900 KB.)
WHOLE = [n for n in EDITED if n.startswith("specs/")]
pins, plans, whole = {}, {}, {}
for name in WHOLE:
    raw = (DC / name).read_bytes()
    assert b"\r\n" not in raw, name
    pins[name] = sha(raw)
    import subprocess
    base = subprocess.run(["git", "-C", str(CLONE), "show", "HEAD:" + name], capture_output=True,
                          check=True).stdout
    assert base == raw, "deli_counter/%s is not the clone's base" % name
    craw = (CLONE / name).read_bytes()
    assert b"\r\n" not in craw and craw != raw, name
    a = raw.decode("utf-8").splitlines(keepends=True)
    b = craw.decode("utf-8").splitlines(keepends=True)
    at = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag != "equal":
            at.append((i1, "".join(a[i1:i2]), "".join(b[j1:j2])))
    # the hunks, applied from the bottom up at their lines, reproduce the clone's file
    lines = list(a)
    for i1, o, n in reversed(at):
        k = len(o.splitlines(keepends=True))
        assert "".join(lines[i1:i1 + k]) == o, (name, i1)
        lines[i1:i1 + k] = n.splitlines(keepends=True)
    assert "".join(lines) == craw.decode("utf-8"), name
    whole[name] = at
print(len(whole), "specs patched by line, each pinned;", sum(len(v) for v in whole.values()), "hunks")
for name in [n for n in EDITED if n not in WHOLE]:
    raw = (DC / name).read_bytes()
    assert b"\r\n" not in raw, name
    pins[name] = sha(raw)
    # the real file is the clone's base, byte for byte
    import subprocess
    base = subprocess.run(["git", "-C", str(CLONE), "show", "HEAD:" + name], capture_output=True, check=True).stdout
    assert base == raw, "deli_counter/%s is not the clone's base" % name
    text = raw.decode("utf-8")
    craw = (CLONE / name).read_bytes()
    assert b"\r\n" not in craw, "the clone's %s has CRLF lines" % name
    want = craw.decode("utf-8")
    edits = hunks(text, want)
    for what, o, n in edits:
        assert text.count(o) == 1, (name, what, text.count(o))
        text = text.replace(o, n)
    assert text == want, "%s: the edits do not reproduce the clone's file" % name
    plans[name] = edits
    print(name, "pinned", pins[name], "hunks", len(edits))
for n in NEW_FILES:
    assert not (DC / n).exists(), n
    assert b"\r\n" not in (CLONE / n).read_bytes(), "the clone's %s has CRLF lines" % n
new_files = {n: (CLONE / n).read_bytes().decode("utf-8") for n in NEW_FILES}
assert (DC / "VERSION").read_bytes().decode("utf-8") == OLD_VERSION
assert (CLONE / "VERSION").read_bytes().decode("utf-8") == NEW_VERSION

CHANGELOG = (SCRATCH / "dc_changelog_0238.md").read_text(encoding="utf-8")
assert CHANGELOG.startswith("## [0.238.0]") and CHANGELOG.endswith("\n\n")
real_cl = (DC / "CHANGELOG.md").read_bytes().decode("utf-8")
assert real_cl.startswith("## [0.237.0]")
assert (CHANGELOG + real_cl).encode("utf-8") == (CLONE / "CHANGELOG.md").read_bytes(), "CHANGELOG is not the clone's"
DOC = (SCRATCH / "patch_doc_dc_0238.txt").read_text(encoding="utf-8")

BODY = '''%s
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DC = ROOT / "deli_counter"
PINS = %r
EDITS = %r
WHOLE = %r
NEW_FILES = %r
CHANGELOG = %r
OLD_VERSION, NEW_VERSION = %r, %r


def _sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def _read(name):
    raw = (DC / name).read_bytes()
    if _sha(raw) != PINS[name]:
        raise SystemExit("REFUSED: deli_counter/%%s is %%s, not the %%s this patch was written against; nothing written"
                         %% (name, _sha(raw), PINS[name]))
    if b"\\r\\n" in raw:
        raise SystemExit("REFUSED: deli_counter/%%s has CRLF endings; these edits are LF" %% name)
    return raw.decode("utf-8")


def main(argv):
    # every file worked out and checked before any is written
    out = {}
    for name, edits in EDITS.items():
        text = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: deli_counter/%%s: the anchor at %%s is there %%d times; nothing written"
                                 %% (name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text
    for name, hunks_at in WHOLE.items():
        # the pin fixes the bytes, so each hunk is checked at its own line and applied from the bottom up
        lines = _read(name).splitlines(keepends=True)
        for i1, old, new in reversed(hunks_at):
            k = len(old.splitlines(keepends=True))
            if "".join(lines[i1:i1 + k]) != old:
                raise SystemExit("REFUSED: deli_counter/%%s: line %%d is not what this patch expects; nothing "
                                 "written" %% (name, i1 + 1))
            lines[i1:i1 + k] = new.splitlines(keepends=True)
        out[name] = "".join(lines)
    for name in NEW_FILES:
        p = DC / name
        if p.exists():
            raise SystemExit("REFUSED: deli_counter/%%s exists already; nothing written" %% name)
    v = DC / "VERSION"
    if v.read_bytes().decode("utf-8") != OLD_VERSION:
        raise SystemExit("REFUSED: VERSION reads %%r, not %%s; nothing written" %% (v.read_text(), OLD_VERSION))
    cl = DC / "CHANGELOG.md"
    ctext = cl.read_bytes().decode("utf-8")
    if not ctext.startswith("## [0.237.0]"):
        raise SystemExit("REFUSED: CHANGELOG.md does not open on 0.237.0; nothing written")
    for name, text in out.items():
        (DC / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (DC / name).write_bytes(text.encode("utf-8"))
    v.write_bytes(NEW_VERSION.encode("utf-8"))
    cl.write_bytes((CHANGELOG + ctext).encode("utf-8"))
    print("%%s applied: %%d files edited, %%d written, VERSION, CHANGELOG. Now, in deli_counter/: the suite, "
          "build.py --all, check.py" %% (NEW_VERSION, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
''' % (DOC.rstrip("\n"), pins, plans, whole, new_files, CHANGELOG, OLD_VERSION, NEW_VERSION)

dest = FACTORY / "patches" / "patch_dc_facade_stack.py"
if "--to" in sys.argv:
    to = pathlib.Path(sys.argv[sys.argv.index("--to") + 1])
    to.write_text(BODY, encoding="utf-8", newline="\n")
    print("wrote the dry copy", to)
elif "--write" in sys.argv:
    assert not dest.exists(), "name taken"
    dest.write_text(BODY, encoding="utf-8", newline="\n")
    compile(BODY, str(dest), "exec")
    print("wrote", dest, len(BODY), "chars; it compiles")
else:
    compile(BODY, "patch_dc_facade_stack.py", "exec")
    print("dry: the patch would be", len(BODY), "chars and compiles; --write to write it")
