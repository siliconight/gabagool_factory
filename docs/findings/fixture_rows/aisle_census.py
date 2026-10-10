"""Census of the AISLES a selling or storage room's ceiling rows could follow, from the furnished specs.

    python docs/findings/fixture_rows/aisle_census.py [<deli_counter root>]

Loads every library spec (`build._spec_paths()`), furnishes it in plain Python the way the build
does (`level_design.furnish`), and for every interior room on every storey reads the VISIBLE
volumes whose name carries a shelf word (`ISLAND_WORDS`: shelf runs, gondolas, racks, pack walls),
projects them on the room's across-axis, merges the spans that overlap, and counts the GAPS at
least an aisle wide (`level_design.island_aisle_width()`, 1.25 m) between them and the room's
bounds: the lanes a row could run over. It prints what it counted and stops: rooms with shelf
volumes, lanes per room, lane widths, the shelf vocabulary it matched, and what `_rows_for_room`
lays in those rooms today. It does not decide where a row goes.
"""
import collections
import json
import os
import sys

ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "deli_counter")
ROOT = os.path.abspath(ROOT)
sys.path.insert(0, ROOT)
import build            # noqa: E402
import level_design     # noqa: E402
import lights           # noqa: E402

ISLAND_WORDS = ("shelf", "gondola", "rack", "pack_wall")


def _spans(vols, along_x):
    out = []
    for v in vols:
        if along_x:
            out.append((float(v["y"]) - float(v.get("size_y", 0.0)) / 2.0,
                        float(v["y"]) + float(v.get("size_y", 0.0)) / 2.0))
        else:
            out.append((float(v["x"]) - float(v.get("size_x", 0.0)) / 2.0,
                        float(v["x"]) + float(v.get("size_x", 0.0)) / 2.0))
    out.sort()
    merged = []
    for a, b in out:
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    return merged


def lanes_of(room, vols, aisle):
    x0, y0, x1, y1 = room["bounds"]
    along_x = (x1 - x0) >= (y1 - y0)
    lo, hi = (y0, y1) if along_x else (x0, x1)
    spans = _spans(vols, along_x)
    edges = [lo] + [e for a, b in spans for e in (a, b)] + [hi]
    gaps = [(edges[k], edges[k + 1]) for k in range(0, len(edges), 2)]
    return [(a, b) for a, b in gaps if b - a >= aisle - 1e-6], along_x


def main():
    aisle = level_design.island_aisle_width()
    rooms_total = rooms_with = 0
    lanes_hist = collections.Counter()
    widths = collections.Counter()
    vocab = collections.Counter()
    rows_today = collections.Counter()
    failed = []
    examples = []
    for p in build._spec_paths():
        if not p.endswith(".json"):
            continue
        try:
            spec = json.load(open(p, encoding="utf-8"))
            level_design.furnish(spec)
        except Exception as exc:                      # noqa: BLE001
            failed.append((os.path.basename(p), str(exc)[:80]))
            continue
        sh = float(spec.get("story_height", 3.0))
        for r in spec.get("rooms", []):
            if not r.get("bounds"):
                continue
            rooms_total += 1
            in_room = lights._volumes_in(spec.get("volumes", []), r, sh)
            isl = [v for v in in_room if any(w in str(v.get("name", "")).lower() for w in ISLAND_WORDS)]
            if not isl:
                continue
            rooms_with += 1
            for v in isl:
                vocab[str(v.get("name", "")).rstrip("0123456789_")] += 1
            lanes, along_x = lanes_of(r, isl, aisle)
            lanes_hist[len(lanes)] += 1
            for a, b in lanes:
                widths[round(b - a * 1.0, 0)] += 1
            x0, y0, x1, y1 = r["bounds"]
            today = lights._rows_for_room(r["bounds"], float(r.get("story", 0)) * sh + sh - 0.3,
                                          float(r.get("story", 0)) * sh, 1.0, False)
            rows_today[(len(today), len(lanes))] += 1
            if len(examples) < 8 and len(lanes) >= 2:
                examples.append((os.path.basename(p), r["id"], [round(x1 - x0, 1), round(y1 - y0, 1)],
                                 len(isl), [(round(a, 1), round(b, 1)) for a, b in lanes]))
    print("specs furnished: %d (failed %d)" % (len(build._spec_paths()) - len(failed), len(failed)))
    for f in failed[:6]:
        print("  failed:", f)
    print("rooms: %d; with shelf volumes: %d" % (rooms_total, rooms_with))
    print("shelf vocabulary:", dict(vocab.most_common()))
    print("lanes per room (lanes: rooms):", dict(sorted(lanes_hist.items())))
    print("lane widths, m rounded (width: lanes):", dict(sorted(widths.items())))
    print("(rows today, lanes): rooms", dict(sorted(rows_today.items())))
    print("examples (spec, room, dims, shelves, lanes):")
    for e in examples:
        print("  ", e)


if __name__ == "__main__":
    main()
