"""Write patches/patch_roadmap_look_review_2026_10_20.py from the live roadmap: the walker's look-review answers of
2026-10-20 onto items 79, 148, 170, 210, 217 and 267, each in front of the status it had; item 210's status and a
dated paragraph for Zoo 1.117.0 and cold run 9355; item 261 CLOSED.

    python make_rm_review_1020.py [--write]

Texts come from rm_1020_texts.py beside this file. Each item's status block is read from the roadmap verbatim -- the
paragraph directly above its heading -- and must stand once, directly above it.
"""
import importlib.util
import pathlib
import re
import sys

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("texts", HERE / "rm_1020_texts.py")
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)

raw = (F / "PIPELINE_ROADMAP.md").read_bytes()
assert b"\r\n" not in raw
text = raw.decode("utf-8")


def status_of(n):
    """(the item's status block with its line's newline, the heading's start) -- the paragraph directly above
    '**<n>. ' at a line's start."""
    m = [x.start() for x in re.finditer(r"(?m)^\*\*%d\. " % n, text)]
    assert len(m) == 1, (n, len(m))
    h = m[0]
    assert text[h - 2:h] == "\n\n", (n, repr(text[h - 4:h]))
    start = text.rindex("\n\n", 0, h - 2) + 2
    block = text[start:h - 1]                       # "*STATUS: ...*\n"
    assert block.startswith("*STATUS: ") and block.endswith("*\n"), (n, block[:60], block[-60:])
    assert text.count(block + "\n**%d. " % n) == 1, n
    return block, h


entries = []
for n, head in T.HEADS:
    old, _h = status_of(n)
    inner = old[len("*STATUS: "):-2]
    new = "*STATUS: " + head + " Earlier status kept: " + inner + "*\n"
    assert "\n\n" not in new and not re.search(r"(?m)^\*\*\d+\.", new), n
    entries.append((str(n), old, new))

# item 210's dated paragraph: after its body, before the next item's status block
h210 = status_of(210)[1]
nxt = re.search(r"(?m)^\*\*(\d+)\. ", text[h210 + 10:])
nxt_n = int(nxt.group(1))
nxt_status, _ = status_of(nxt_n)
anchor_at = text.index(nxt_status, h210)
tail = text[anchor_at - 300:anchor_at] + nxt_status[:80]
assert text.count(tail) == 1
para = T.BODY_210.strip("\n") + "\n\n"
assert not re.search(r"(?m)^\*\*\d+\.", para)
body = (tail, text[anchor_at - 300:anchor_at] + para + nxt_status[:80])

doc = T.DOC
src = '''%s
import pathlib
import sys

ROADMAP = pathlib.Path(__file__).resolve().parents[1] / "PIPELINE_ROADMAP.md"
ENTRIES = %r
BODY_210 = %r


def main():
    data = ROADMAP.read_bytes()
    if b"\\r\\n" in data:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = data.decode("utf-8")
    if all(text.count(new + "\\n**%%s. " %% n) == 1 for n, _, new in ENTRIES) and text.count(BODY_210[1]) == 1:
        print("already applied")
        return 0
    for n, old, _ in ENTRIES:
        if text.count(old) != 1 or text.count(old + "\\n**%%s. " %% n) != 1:
            raise SystemExit("REFUSED: item %%s's status block is not there once, above its heading; nothing written" %% n)
    if text.count(BODY_210[0]) != 1:
        raise SystemExit("REFUSED: the end of item 210's body is not there once; nothing written")
    for n, old, new in ENTRIES:
        text = text.replace(old, new)
    text = text.replace(BODY_210[0], BODY_210[1])
    for n, _, new in ENTRIES:
        if text.count(new + "\\n**%%s. " %% n) != 1:
            raise SystemExit("REFUSED: item %%s's new status does not adjoin its heading; nothing written" %% n)
    ROADMAP.write_bytes(text.encode("utf-8"))
    print("roadmap: %%d statuses and item 210's paragraph; now tools/roadmap_status.py --write and --check"
          %% len(ENTRIES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % (doc.rstrip("\n"), entries, body)
compile(src, "patch", "exec")
dest = F / "patches" / "patch_roadmap_look_review_2026_10_20.py"
if "--write" in sys.argv:
    assert not dest.exists(), "name taken"
    dest.write_text(src, encoding="utf-8", newline="\n")
    print("wrote", dest, len(src), "chars;", len(entries), "statuses; next item after 210:", nxt_n)
elif "--to" in sys.argv:
    to = pathlib.Path(sys.argv[sys.argv.index("--to") + 1])
    to.write_text(src, encoding="utf-8", newline="\n")
    print("wrote the dry copy", to)
else:
    print("dry:", len(src), "chars,", len(entries), "statuses; next item after 210:", nxt_n)
