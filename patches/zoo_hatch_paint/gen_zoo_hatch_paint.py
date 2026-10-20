"""Write patches/patch_zoo_hatch_paint.py (Zoo 1.114.1) from the proven zoo_hp clone.

Each edited file's hunks are taken from a line diff of the REAL repo's pinned file against the clone's, each widened by
context lines until its old text occurs exactly once; the generator applies them to the real file and refuses to write
the patch unless the result is the clone's file. New files are embedded verbatim.

LINE ENDINGS, as the Level Factory generator in `patches/lf_fire_escape_ramp/` handles them: the pins and the edits
are of the LF-normalised text; the patch refuses a file whose endings are mixed, and writes each file back with the
endings it found (both of Zoo's edited files are LF on disk today).

    python gen_zoo_hatch_paint.py            # dry: build the patch in memory, check it compiles
    python gen_zoo_hatch_paint.py --write    # write it (refuses if the name is taken)
    python gen_zoo_hatch_paint.py --to <p>   # write a copy elsewhere, for a dry run
"""
import difflib
import hashlib
import pathlib
import subprocess
import sys

FACTORY = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
LF = FACTORY / "zoo"
SCRATCH = pathlib.Path(r"C:\Users\Brannen\AppData\Local\Temp\claude\C--Projects-gabagool-studios-gabagool-factory"
                       r"\27f14f8b-7ce5-44c0-a704-178a824035d7\scratchpad")
CLONE = SCRATCH / "zoo_hp"
EDITED = ["zoo_keeper/recipes/roof_hatch.py", "tests/test_hole_forms.py"]
NEW_FILES = []
OLD_VERSION, NEW_VERSION = "1.114.0", "1.114.1"


def sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def lf_text(raw, what):
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    assert crlf in (0, lf), "%s has mixed line endings (%d CRLF of %d)" % (what, crlf, lf)
    return raw.decode("utf-8").replace("\r\n", "\n"), crlf > 0


def hunks(old, new):
    """[(what, old_text, new_text)] turning `old` into `new`, each old_text unique in `old`."""
    a, b = old.splitlines(keepends=True), new.splitlines(keepends=True)
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        ctx = 0
        while True:
            lo2, hi2 = max(0, i1 - ctx), min(len(a), i2 + ctx)
            o = "".join(a[lo2:hi2])
            if o and old.count(o) == 1:
                n = "".join(a[lo2:i1]) + "".join(b[j1:j2]) + "".join(a[i2:hi2])
                out.append(("lines %d-%d" % (i1 + 1, i2), o, n))
                break
            ctx += 1
            assert ctx < 40, "no unique anchor near line %d" % (i1 + 1)
    return out


pins, plans = {}, {}
for name in EDITED:
    text, crlf = lf_text((LF / name).read_bytes(), "zoo/" + name)
    pins[name] = sha(text.encode("utf-8"))
    # the real file is the clone's base, once both are LF
    base = subprocess.run(["git", "-C", str(CLONE), "show", "HEAD:" + name], capture_output=True, check=True).stdout
    assert lf_text(base, "the clone's base " + name)[0] == text, "zoo/%s is not the clone's base" % name
    want, ccrlf = lf_text((CLONE / name).read_bytes(), "the clone's " + name)
    assert not ccrlf, "the clone's %s has CRLF lines" % name
    edits = hunks(text, want)
    for what, o, n in edits:
        assert text.count(o) == 1, (name, what, text.count(o))
        text = text.replace(o, n)
    assert text == want, "%s: the edits do not reproduce the clone's file" % name
    plans[name] = edits
    print(name, "pinned", pins[name], "CRLF on disk" if crlf else "LF on disk", "hunks", len(edits))
for n in NEW_FILES:
    assert not (LF / n).exists(), n
    assert b"\r\n" not in (CLONE / n).read_bytes(), "the clone's %s has CRLF lines" % n
new_files = {n: (CLONE / n).read_bytes().decode("utf-8") for n in NEW_FILES}
assert (LF / "VERSION").read_bytes().decode("utf-8") == OLD_VERSION
assert (CLONE / "VERSION").read_bytes().decode("utf-8") == NEW_VERSION

CHANGELOG = (SCRATCH / "zoo_changelog_11141.md").read_text(encoding="utf-8")
assert CHANGELOG.startswith("## [1.114.1]") and CHANGELOG.endswith("\n\n")
real_cl = (LF / "CHANGELOG.md").read_bytes()
assert b"\r\n" not in real_cl and real_cl.startswith(b"## [1.114.0]")
assert CHANGELOG.encode("utf-8") + real_cl == (CLONE / "CHANGELOG.md").read_bytes(), "CHANGELOG is not the clone's"
DOC = (SCRATCH / "patch_doc_zoo_11141.txt").read_text(encoding="utf-8")

BODY = '''%s
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / "zoo"
PINS = %r
EDITS = %r
NEW_FILES = %r
CHANGELOG = %r
OLD_VERSION, NEW_VERSION = %r, %r


def _sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def _read(name):
    """The file's LF text and whether it is CRLF on disk; refuses mixed endings and a file that is not the pinned one."""
    raw = (REPO / name).read_bytes()
    crlf, lf = raw.count(b"\\r\\n"), raw.count(b"\\n")
    if crlf not in (0, lf):
        raise SystemExit("REFUSED: zoo/%%s has mixed line endings (%%d CRLF of %%d); nothing written"
                         %% (name, crlf, lf))
    text = raw.decode("utf-8").replace("\\r\\n", "\\n")
    if _sha(text.encode("utf-8")) != PINS[name]:
        raise SystemExit("REFUSED: zoo/%%s is %%s, not the %%s this patch was written against; nothing "
                         "written" %% (name, _sha(text.encode("utf-8")), PINS[name]))
    return text, crlf > 0


def main(argv):
    # every file worked out and checked before any is written
    out = {}
    for name, edits in EDITS.items():
        text, crlf = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: zoo/%%s: the anchor at %%s is there %%d times; nothing written"
                                 %% (name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text.replace("\\n", "\\r\\n") if crlf else text
    for name in NEW_FILES:
        if (REPO / name).exists():
            raise SystemExit("REFUSED: zoo/%%s exists already; nothing written" %% name)
    v = REPO / "VERSION"
    if v.read_bytes().decode("utf-8") != OLD_VERSION:
        raise SystemExit("REFUSED: VERSION reads %%r, not %%s; nothing written" %% (v.read_text(), OLD_VERSION))
    cl = REPO / "CHANGELOG.md"
    craw = cl.read_bytes()
    if b"\\r\\n" in craw or not craw.startswith(b"## [" + OLD_VERSION.encode() + b"]"):
        raise SystemExit("REFUSED: CHANGELOG.md is not LF opening on %%s; nothing written" %% OLD_VERSION)
    for name, text in out.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    v.write_bytes(NEW_VERSION.encode("utf-8"))
    cl.write_bytes(CHANGELOG.encode("utf-8") + craw)
    print("Zoo %%s applied: %%d files edited, %%d written, VERSION, CHANGELOG. Now, in zoo/: the "
          "suite" %% (NEW_VERSION, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
''' % (DOC.rstrip("\n"), pins, plans, new_files, CHANGELOG, OLD_VERSION, NEW_VERSION)

dest = FACTORY / "patches" / "patch_zoo_hatch_paint.py"
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
    compile(BODY, "patch_zoo_hatch_paint.py", "exec")
    print("dry: the patch would be", len(BODY), "chars and compiles; --write to write it")
