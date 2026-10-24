"""Write patches/patch_lot_one_sign.py (Lot 0.129.0, walk of cold run 9386 finding 1) from the proven lot_sign clone.
Copied from `patches/lot_far_signals/gen_lot_far_signals.py`; its names, files and versions changed, nothing else.

Each edited file's hunks are taken from a line diff of the REAL repo's pinned file against the clone's, each widened by
context lines until its old text occurs exactly once; the generator applies them to the real file and refuses to write
the patch unless the result is the clone's file. New files are embedded verbatim.

LINE ENDINGS, as the Level Factory generator in `patches/lf_fire_escape_ramp/` handles them: the pins and the edits
are of the LF-normalised text; the patch refuses a file whose endings are mixed, and writes each file back with the
endings it found (every file this one edits is LF on disk today).

    python gen_lot_one_sign.py               # dry: build the patch in memory, check it compiles
    python gen_lot_one_sign.py--write        # write it (refuses if the name is taken)
    python gen_lot_one_sign.py--to <p>       # write a copy elsewhere, for a dry run
"""
import difflib
import hashlib
import pathlib
import subprocess
import sys

FACTORY = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
LF = FACTORY / "lot"
SCRATCH = pathlib.Path(r"C:\Users\Brannen\AppData\Local\Temp\claude\C--Projects-gabagool-studios-gabagool-factory"
                       r"\27f14f8b-7ce5-44c0-a704-178a824035d7\scratchpad")
CLONE = FACTORY / "_scratch" / "lot_sign"
EDITED = ["lot.py"]
NEW_FILES = ["tests/test_one_sign.py"]
OLD_VERSION, NEW_VERSION = "Lot 0.128.0", "Lot 0.129.0"


def sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def lf_text(raw, what):
    crlf, lf = raw.count(b"\r\n"), raw.count(b"\n")
    assert crlf in (0, lf), "%s has mixed line endings (%d CRLF of %d)" % (what, crlf, lf)
    return raw.decode("utf-8").replace("\r\n", "\n"), crlf > 0


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

    def bmap_end(i):
        """Where a window ending at ``i`` ends in ``new``: past every op that starts at ``i`` -- an insertion there
        (text appended at a file's end) belongs to the window that ends there. `bmap` alone dropped it."""
        pos = 0
        for tag, i1, i2, j1, j2 in ops:
            if i1 > i:
                break
            pos = j1 + (i - i1) if (tag == "equal" and i <= i2) else j2
        return pos

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
        o, n = "".join(a[lo:hi]), "".join(b[bmap(lo):bmap_end(hi)])
        assert old.count(o) == 1
        out.append(("lines %d-%d" % (lo + 1, hi), o, n))
    return out


pins, plans = {}, {}
for name in EDITED:
    text, crlf = lf_text((LF / name).read_bytes(), "lot/" + name)
    pins[name] = sha(text.encode("utf-8"))
    # the real file is the clone's base, once both are LF
    base = subprocess.run(["git", "-C", str(CLONE), "show", "HEAD:" + name], capture_output=True, check=True).stdout
    assert lf_text(base, "the clone's base " + name)[0] == text, "lot/%s is not the clone's base" % name
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

CHANGELOG = (SCRATCH / "lot_changelog_01290.md").read_text(encoding="utf-8")
assert CHANGELOG.startswith("## 0.129.0") and CHANGELOG.endswith("\n\n")
real_cl = (LF / "CHANGELOG.md").read_bytes()
assert b"\r\n" not in real_cl and real_cl.startswith(b"## 0.128.0")
assert CHANGELOG.encode("utf-8") + real_cl == (CLONE / "CHANGELOG.md").read_bytes(), "CHANGELOG is not the clone's"
DOC = (SCRATCH / "patch_doc_lot_01290.txt").read_text(encoding="utf-8")

BODY = '''%s
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT / "lot"
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
        raise SystemExit("REFUSED: lot/%%s has mixed line endings (%%d CRLF of %%d); nothing written"
                         %% (name, crlf, lf))
    text = raw.decode("utf-8").replace("\\r\\n", "\\n")
    if _sha(text.encode("utf-8")) != PINS[name]:
        raise SystemExit("REFUSED: lot/%%s is %%s, not the %%s this patch was written against; nothing "
                         "written" %% (name, _sha(text.encode("utf-8")), PINS[name]))
    return text, crlf > 0


def main(argv):
    # every file worked out and checked before any is written
    out = {}
    for name, edits in EDITS.items():
        text, crlf = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: lot/%%s: the anchor at %%s is there %%d times; nothing written"
                                 %% (name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text.replace("\\n", "\\r\\n") if crlf else text
    for name in NEW_FILES:
        if (REPO / name).exists():
            raise SystemExit("REFUSED: lot/%%s exists already; nothing written" %% name)
    v = REPO / "VERSION"
    if v.read_bytes().decode("utf-8") != OLD_VERSION:
        raise SystemExit("REFUSED: VERSION reads %%r, not %%s; nothing written" %% (v.read_text(), OLD_VERSION))
    cl = REPO / "CHANGELOG.md"
    craw = cl.read_bytes()
    if b"\\r\\n" in craw or not craw.startswith(b"## " + OLD_VERSION.split()[-1].encode() + b" "):
        raise SystemExit("REFUSED: CHANGELOG.md is not LF opening on %%s; nothing written" %% OLD_VERSION)
    for name, text in out.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (REPO / name).write_bytes(text.encode("utf-8"))
    v.write_bytes(NEW_VERSION.encode("utf-8"))
    cl.write_bytes(CHANGELOG.encode("utf-8") + craw)
    print("%%s applied: %%d files edited, %%d written, VERSION, CHANGELOG. Now, in lot/: the "
          "suite" %% (NEW_VERSION, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
''' % (DOC.rstrip("\n"), pins, plans, new_files, CHANGELOG, OLD_VERSION, NEW_VERSION)

dest = FACTORY / "patches" / "patch_lot_one_sign.py"
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
    compile(BODY, "patch_lot_one_sign.py", "exec")
    print("dry: the patch would be", len(BODY), "chars and compiles; --write to write it")
