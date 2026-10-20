"""Write patches/patch_dc_hole_causes.py (Deli Counter 0.236.0, roadmap 265) from the proven dc_hole2 clone.

Each edited file's hunks are taken from a line diff of the REAL repo's pinned file against the clone's, each widened by
context lines until its old text occurs exactly once; the generator applies them to the real file and refuses to write
the patch unless the result is byte-identical to the clone's file. New files are embedded verbatim.

    python gen_dc_hole_causes.py            # dry: build the patch in memory, check it compiles
    python gen_dc_hole_causes.py --write    # write it (refuses if the name is taken)
    --base <dir>                            # read the pinned files from a checkout of 0.235.0 instead of
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
CLONE = SCRATCH / "dc_hole2"
EDITED = ["spec_types.py", "schema/level.schema.json", "deli_counter.py", "layout_lint.py", "prop_species.py",
          "build_freshness.py"]
NEW_FILES = ["hole_causes.py", "test_hole_causes.py"]
OLD_VERSION, NEW_VERSION = "Deli Counter 0.235.0", "Deli Counter 0.236.0"


def sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


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

CHANGELOG = (SCRATCH / "dc_changelog_0236.md").read_text(encoding="utf-8") + "\n"
assert CHANGELOG.startswith("## [0.236.0]") and CHANGELOG.endswith("\n\n")
real_cl = (DC / "CHANGELOG.md").read_bytes().decode("utf-8")
assert real_cl.startswith("## [0.235.0]")
assert (CHANGELOG + real_cl).encode("utf-8") == (CLONE / "CHANGELOG.md").read_bytes(), "CHANGELOG is not the clone's"
DOC = (SCRATCH / "patch_doc_0236.txt").read_text(encoding="utf-8")

BODY = '''%s
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DC = ROOT / "deli_counter"
PINS = %r
EDITS = %r
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
    for name in NEW_FILES:
        p = DC / name
        if p.exists():
            raise SystemExit("REFUSED: deli_counter/%%s exists already; nothing written" %% name)
    v = DC / "VERSION"
    if v.read_bytes().decode("utf-8") != OLD_VERSION:
        raise SystemExit("REFUSED: VERSION reads %%r, not %%s; nothing written" %% (v.read_text(), OLD_VERSION))
    cl = DC / "CHANGELOG.md"
    ctext = cl.read_bytes().decode("utf-8")
    if not ctext.startswith("## [0.235.0]"):
        raise SystemExit("REFUSED: CHANGELOG.md does not open on 0.235.0; nothing written")
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
''' % (DOC.rstrip("\n"), pins, plans, new_files, CHANGELOG, OLD_VERSION, NEW_VERSION)

dest = FACTORY / "patches" / "patch_dc_hole_causes.py"
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
    compile(BODY, "patch_dc_hole_causes.py", "exec")
    print("dry: the patch would be", len(BODY), "chars and compiles; --write to write it")
