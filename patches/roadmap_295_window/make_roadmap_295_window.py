"""Write patches/patch_roadmap_295_window.py (roadmap 295 NARROWED: scout models and the scout window ship) from `decisions.json` beside
this file. Copied from `roadmap_narrowed_audit/make_roadmap_narrowed_audit.py`: for each decided item, its
status block (the lines from the last `*STATUS:` line above its heading down to the blank line before it --
one line, hard-wrapped, or glued under a paragraph as item 42's is) replaced by one line, the new status first and
the old one kept after "Earlier status kept:", joined as `roadmap_status.py` joins it. Copied in shape from
`roadmap_296_298_drawings/make_roadmap_296_298.py`, widened for the wrapped and glued dialects. Refuses if the name
is taken.

    python patches/roadmap_295_window/make_roadmap_295_window.py

`decisions.json`: a list of {"n": int, "status": "CLOSED|SUPERSEDED|ANALYSIS|NARROWED|OPEN", "text": "..."}; the
written block is "*STATUS: <status> 2026-10-22 -- <text> Earlier status kept: <old, less its '*STATUS: '>".
"""
import json
import pathlib
import re

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
HERE = pathlib.Path(__file__).resolve().parent
dest = F / "patches" / "patch_roadmap_295_window.py"
assert not dest.exists(), "name taken"
t = (F / "PIPELINE_ROADMAP.md").read_bytes().decode("utf-8")
assert "\r\n" not in t
DATE = "2026-10-22"
VOCAB = ("OPEN", "CLOSED", "RETRACTED", "NARROWED", "SUPERSEDED", "ANALYSIS")


def block(n):
    """(heading line with its leading blank line, the exact status text above it)."""
    m = list(re.finditer(r"\n\n\*\*%d\. " % n, t))
    assert len(m) == 1, n
    h = m[0].start()
    heading = t[h:t.index("\n", h + 2)]
    assert t.count(heading) == 1, n
    s = max(t.rindex("\n\n", 0, h) + 2, t.rindex("\n*STATUS:", 0, h) + 1)
    old = t[s:h]
    assert old.startswith("*STATUS: ") and old.endswith("*"), (n, old[:60], old[-20:])
    return heading, old


rows = []
for d in json.loads((HERE / "decisions.json").read_text(encoding="utf-8")):
    assert d["status"] in VOCAB, d["n"]
    heading, old = block(d["n"])
    joined = " ".join(ln.strip() for ln in old.split("\n"))
    text = d["text"].strip()
    assert "\n" not in text and not text.endswith("*"), d["n"]
    by = " by " + d["by"] if d.get("by") else ""
    new = "*STATUS: %s %s%s -- %s Earlier status kept: %s" % (d["status"], DATE, by, text, joined[len("*STATUS: "):])
    assert new.endswith("*") and "\n" not in new
    rows.append((d["n"], heading, old, new))
assert len({r[0] for r in rows}) == len(rows), "an item decided twice"

PATCH = '''"""Roadmap 295 NARROWED (2026-10-22): the scout models and the scout window ship, called through one seam --
cold run 9381. Copied from `patch_roadmap_295_scout_model.py`. Every status block is the lines from
the last `*STATUS:` line above its heading to the blank line before it, asserted to be the one this was written
against, replaced by one line that keeps it after "Earlier status kept:". The index is NOT touched here: run
`python tools/roadmap_status.py --write` then `--check` after it.

    python patches/patch_roadmap_295_window.py && python tools/roadmap_status.py --write && python tools/roadmap_status.py --check
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
RM = ROOT / "PIPELINE_ROADMAP.md"

STATUSES = %r


def main():
    raw = RM.read_bytes()
    if b"\\r\\n" in raw:
        raise SystemExit("REFUSED: the roadmap is LF and CRLF was found; nothing written")
    text = raw.decode("utf-8")
    if STATUSES[0][3] in text:
        raise SystemExit("REFUSED: already applied; nothing written")
    for n, heading, old, new in STATUSES:
        if text.count(heading) != 1:
            raise SystemExit("REFUSED: %%d's heading is not there once; nothing written" %% n)
        h = text.find(heading)
        s = max(text.rindex("\\n\\n", 0, h) + 2, text.rindex("\\n*STATUS:", 0, h) + 1)
        if text[s:h] != old:
            raise SystemExit("REFUSED: %%d's status block is not the one this was written against; nothing written" %% n)
        text = text[:s] + new + text[h:]
        if text.count(new + heading) != 1:
            raise SystemExit("REFUSED: %%d's status no longer adjoins its heading; nothing written" %% n)
    RM.write_bytes(text.encode("utf-8"))
    print("roadmap: %%d statuses replaced; now roadmap_status.py --write / --check" %% len(STATUSES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % (rows,)
compile(PATCH, str(dest), "exec")
dest.write_text(PATCH, encoding="utf-8", newline="\n")
print("wrote", dest, len(PATCH), "chars;", len(rows), "statuses:", [r[0] for r in rows])
