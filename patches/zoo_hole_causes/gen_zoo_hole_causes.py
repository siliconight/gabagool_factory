"""Write patches/patch_zoo_hole_causes.py (Zoo 1.114.0, roadmap 265) from the proven zoo_hole clone.

As gen_dc_hole_causes.py: each edited file's hunks come from a line diff of the REAL repo's pinned file against the
clone's, widened until unique, applied and checked byte for byte against the clone before the patch is written; new
files are embedded verbatim; the CHANGELOG entry is prepended.

    python gen_zoo_hole_causes.py                 # dry
    python gen_zoo_hole_causes.py --to <path>     # a copy to dry-run elsewhere
    python gen_zoo_hole_causes.py --write         # patches/patch_zoo_hole_causes.py (refuses if the name is taken)
"""
import difflib
import hashlib
import pathlib
import subprocess
import sys

FACTORY = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
ZOO = FACTORY / "zoo"
SCRATCH = pathlib.Path(r"C:\Users\Brannen\AppData\Local\Temp\claude\C--Projects-gabagool-studios-gabagool-factory"
                       r"\27f14f8b-7ce5-44c0-a704-178a824035d7\scratchpad")
CLONE = SCRATCH / "zoo_hole"
EDITED = ["tests/test_coincident_faces.py", "zoo_keeper/genome/minted.json",
          "zoo_keeper/genome/species/roof_hatch.json", "zoo_keeper/recipes/roof_hatch.py"]
NEW_FILES = ["zoo_keeper/core/hole_forms.py", "zoo_keeper/recipes/hole_edge.py", "zoo_keeper/recipes/hole_spoil.py",
             "zoo_keeper/recipes/hole_kit.py", "zoo_keeper/genome/species/hole_edge.json",
             "zoo_keeper/genome/species/hole_spoil.json", "zoo_keeper/genome/species/hole_kit.json",
             "tests/test_hole_forms.py"]
OLD_VERSION, NEW_VERSION = "1.113.1", "1.114.0"


def sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def hunks(old, new):
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
    raw = (ZOO / name).read_bytes()
    assert b"\r\n" not in raw, name
    base = subprocess.run(["git", "-C", str(CLONE), "show", "HEAD:" + name], capture_output=True, check=True).stdout
    assert base == raw, "zoo/%s is not the clone's base" % name
    pins[name] = sha(raw)
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
    assert not (ZOO / n).exists(), n
    assert b"\r\n" not in (CLONE / n).read_bytes(), "the clone's %s has CRLF lines" % n
new_files = {n: (CLONE / n).read_bytes().decode("utf-8") for n in NEW_FILES}
assert (ZOO / "VERSION").read_bytes().decode("utf-8") == OLD_VERSION
assert (CLONE / "VERSION").read_bytes().decode("utf-8") == NEW_VERSION
real_cl = (ZOO / "CHANGELOG.md").read_bytes().decode("utf-8")
clone_cl = (CLONE / "CHANGELOG.md").read_bytes().decode("utf-8")
assert real_cl.startswith("## [1.113.1]") and clone_cl.endswith(real_cl)
CHANGELOG = clone_cl[:len(clone_cl) - len(real_cl)]
assert CHANGELOG.startswith("## [1.114.0]") and CHANGELOG.endswith("\n\n")
DOC = (SCRATCH / "patch_doc_zoo_1140.txt").read_text(encoding="utf-8")

BODY = '''%s
import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
ZOO = ROOT / "zoo"
PINS = %r
EDITS = %r
NEW_FILES = %r
CHANGELOG = %r
OLD_VERSION, NEW_VERSION = %r, %r


def _sha(b):
    return hashlib.sha256(b).hexdigest()[:16]


def _read(name):
    raw = (ZOO / name).read_bytes()
    if _sha(raw) != PINS[name]:
        raise SystemExit("REFUSED: zoo/%%s is %%s, not the %%s this patch was written against; nothing written"
                         %% (name, _sha(raw), PINS[name]))
    if b"\\r\\n" in raw:
        raise SystemExit("REFUSED: zoo/%%s has CRLF endings; these edits are LF" %% name)
    return raw.decode("utf-8")


def main(argv):
    # every file worked out and checked before any is written
    out = {}
    for name, edits in EDITS.items():
        text = _read(name)
        for what, old, new in edits:
            if text.count(old) != 1:
                raise SystemExit("REFUSED: zoo/%%s: the anchor at %%s is there %%d times; nothing written"
                                 %% (name, what, text.count(old)))
            text = text.replace(old, new)
        out[name] = text
    for name in NEW_FILES:
        if (ZOO / name).exists():
            raise SystemExit("REFUSED: zoo/%%s exists already; nothing written" %% name)
    v = ZOO / "VERSION"
    if v.read_bytes().decode("utf-8") != OLD_VERSION:
        raise SystemExit("REFUSED: VERSION reads %%r, not %%s; nothing written" %% (v.read_text(), OLD_VERSION))
    cl = ZOO / "CHANGELOG.md"
    ctext = cl.read_bytes().decode("utf-8")
    if not ctext.startswith("## [1.113.1]"):
        raise SystemExit("REFUSED: CHANGELOG.md does not open on 1.113.1; nothing written")
    for name, text in out.items():
        (ZOO / name).write_bytes(text.encode("utf-8"))
    for name, text in NEW_FILES.items():
        (ZOO / name).write_bytes(text.encode("utf-8"))
    v.write_bytes(NEW_VERSION.encode("utf-8"))
    cl.write_bytes((CHANGELOG + ctext).encode("utf-8"))
    print("Zoo %%s applied: %%d files edited, %%d written, VERSION, CHANGELOG. Now, in zoo/: the suite"
          %% (NEW_VERSION, len(out), len(NEW_FILES)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
''' % (DOC.rstrip("\n"), pins, plans, new_files, CHANGELOG, OLD_VERSION, NEW_VERSION)

dest = FACTORY / "patches" / "patch_zoo_hole_causes.py"
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
    compile(BODY, "patch_zoo_hole_causes.py", "exec")
    print("dry: the patch would be", len(BODY), "chars and compiles; --write to write it")
