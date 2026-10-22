"""Extract every NARROWED roadmap item, as the index's own parser classes it, into balanced batch files.

Each record: n, title, line (1-based line of the item heading in PIPELINE_ROADMAP.md), newest (the status up to
the first "Earlier status kept:"), earlier_chars (how much history follows it), body (heading to the next item's
status block).
"""
import json
import pathlib
import sys

F = pathlib.Path(r"C:\Projects\gabagool_studios\gabagool_factory")
S = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(F / "tools"))
import roadmap_status as rs  # noqa: E402

text = (F / "PIPELINE_ROADMAP.md").read_bytes().decode("utf-8")
rows = rs.parse(text)
narrowed = {r["num"]: r for r in rows if r["status"] == "NARROWED"}
print("parse(): items", len(rows), "NARROWED", len(narrowed))

lines = text.splitlines()
upto = text[:text.index("## What to do next")].count("\n")
heads = {}
for i, ln in enumerate(lines):
    if i < upto:
        continue
    m = rs._ITEM.match(ln)
    if m:
        heads[int(m.group(1))] = i
order = sorted(heads.values())


def block_start(i):
    """First line of the non-blank block directly above line i (the status block's paragraph)."""
    k = i - 1
    while k >= 0 and not lines[k].strip():
        k -= 1
    j = k
    while j >= 0 and lines[j].strip():
        j -= 1
    return j + 1


items = []
for n in sorted(narrowed):
    i = heads[n]
    status = rs._block_above(lines, i)
    assert status.startswith("*STATUS: NARROWED"), (n, status[:80])
    cut = status.find("Earlier status kept:")
    newest = status if cut < 0 else status[:cut].rstrip()
    nxt = next((h for h in order if h > i), len(lines))
    end = block_start(nxt) if nxt < len(lines) else len(lines)
    body = "\n".join(lines[i:end]).strip()
    items.append(dict(n=n, title=narrowed[n]["title"], line=i + 1, newest=newest,
                      earlier_chars=0 if cut < 0 else len(status) - cut, body=body))

size = lambda it: len(it["newest"]) + len(it["body"])  # noqa: E731
print("chars to read:", sum(size(it) for it in items), "largest:",
      sorted(((size(it), it["n"]) for it in items), reverse=True)[:5])
NB = int(sys.argv[1]) if len(sys.argv) > 1 else 10
batches, sizes = [[] for _ in range(NB)], [0] * NB
for it in sorted(items, key=lambda x: -size(x)):
    j = sizes.index(min(sizes))
    batches[j].append(it)
    sizes[j] += size(it)
for old in S.glob("batch_*.json"):
    old.unlink()
for j, b in enumerate(batches):
    b.sort(key=lambda x: x["n"])
    (S / ("batch_%02d.json" % (j + 1))).write_text(json.dumps(b, indent=1, ensure_ascii=False), encoding="utf-8")
    print("batch %02d: %2d items %6d chars %s" % (j + 1, len(b), sizes[j], [x["n"] for x in b]))
(S / "narrowed_all.json").write_text(json.dumps(items, indent=1, ensure_ascii=False), encoding="utf-8")
